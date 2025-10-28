import socketio
from typing import Dict, Set
from .config import get_settings
from ..repositories import device_repository


settings = get_settings()

# Async Socket.IO server (ASGI)
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_allow_origins,
    logger=False,
    engineio_logger=False,
    ping_interval=25,
    ping_timeout=60,
)

# Track connections -> device rooms
connected_sids: Set[str] = set()
sid_device_map: Dict[str, int] = {}
sid_environ: Dict[str, dict] = {}


async def emit_to_device(device_id: int, event: str, data):
    room = f"device:{device_id}"
    await sio.emit(event, data, room=room)


@sio.event
async def connect(sid, environ, auth):
    connected_sids.add(sid)
    # Guardar environ/asgi scope para uso posterior
    try:
        sid_environ[sid] = environ or {}
    except Exception:
        sid_environ[sid] = {}
    await sio.emit("connection_response", {"status": "connected", "message": "Conectado al servidor"}, to=sid)


@sio.event
async def disconnect(sid):
    connected_sids.discard(sid)
    # If associated to a device, leave room
    if sid in sid_device_map:
        device_id = sid_device_map.pop(sid)
        await sio.leave_room(sid, f"device:{device_id}")
    sid_environ.pop(sid, None)


@sio.event
async def ping(sid):
    await sio.emit("pong", {"ok": True}, to=sid)


@sio.event
async def register_device(sid, data):
    try:
        device_id = int(data.get("device_id"))
        device_name = data.get("device_name", f"device-{device_id}")
        room = f"device:{device_id}"
        await sio.enter_room(sid, room)
        sid_device_map[sid] = device_id
        # Best-effort: registrar/actualizar dispositivo con IP del cliente
        client_ip = None
        try:
            env = sid_environ.get(sid) or {}
            scope = env.get("asgi.scope", {}) if isinstance(env, dict) else {}
            client = scope.get("client") if isinstance(scope, dict) else None
            if isinstance(client, (list, tuple)) and len(client) > 0:
                client_ip = client[0]
        except Exception:
            client_ip = None
        # Si no se pudo obtener IP desde ASGI, dejar como "0.0.0.0"
        device_repository.upsert_device(device_name, client_ip or "0.0.0.0")
        await sio.emit("registration_success", {"device_id": device_id, "device_name": device_name}, to=sid)
    except Exception as e:
        await sio.emit("registration_error", {"error": str(e)}, to=sid)


@sio.event
async def unregister_device(sid, data):
    device_id = data.get("device_id")
    if device_id is None:
        return
    room = f"device:{int(device_id)}"
    await sio.leave_room(sid, room)
    sid_device_map.pop(sid, None)

