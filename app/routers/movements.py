from fastapi import APIRouter
from ..schemas.status import MovementCommandRequest, ExecuteSequenceRequest
from ..repositories import events_repository as events
from ..repositories import demo_repository as demos
from ..models.commands_map import COMMAND_TO_STATUS
from ..services.websocket_manager import emit_to_device

router = APIRouter(prefix="/api/movements", tags=["movements"])


@router.post("/send")
async def send_movement(payload: MovementCommandRequest):
    status_clave = COMMAND_TO_STATUS.get(payload.command)
    if not status_clave:
        return {"success": False, "error": "Comando no válido"}

    meta = payload.meta or {}
    meta.update({"duration_ms": payload.duration_ms, "origin": meta.get("origin", "web_rest")})

    # registrar en DB (SP)
    events.add_movement_status(payload.device_id, status_clave, meta)

    # notificar por WebSocket a los suscriptores del dispositivo
    await emit_to_device(
        payload.device_id,
        "execute_movement",
        {
            "device_id": payload.device_id,
            "command": payload.command,
            "status_clave": status_clave,
            "duration_ms": payload.duration_ms,
            "meta": meta,
        },
    )

    return {"success": True}


@router.post("/sequence")
async def execute_sequence(payload: ExecuteSequenceRequest):
    # Convertir la secuencia a formato de SP (status_clave/duration_ms)
    moves = []
    for item in payload.sequence:
        status = COMMAND_TO_STATUS.get(item.command)
        if not status:
            return {"success": False, "error": f"Comando inválido en secuencia: {item.command}"}
        moves.append({"status_clave": status, "duration_ms": int(item.duration)})

    demo_id = demos.add_demo(payload.device_id, payload.name or "demo-web", moves)

    # Opcionalmente, emitir una actualización de estado
    await emit_to_device(
        payload.device_id,
        "status_update",
        {"type": "demo_created", "demo_id": demo_id, "moves": len(moves)},
    )

    return {"success": True, "demo_id": demo_id}
