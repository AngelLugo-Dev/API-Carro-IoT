from ..services.websocket_manager import sio, emit_to_device
from ..models.commands_map import COMMAND_TO_STATUS
from ..repositories import events_repository as events


@sio.event
async def movement_command(sid, data):
    try:
        device_id = int(data.get("device_id"))
        command = data.get("command")
        duration_ms = int(data.get("duration_ms", 1000))
        meta = data.get("meta") or {}

        status_clave = COMMAND_TO_STATUS.get(command)
        if not status_clave:
            await sio.emit("command_error", {"error": "Comando no válido"}, to=sid)
            return

        # Registrar en DB y emitir confirmación
        meta_with_duration = {**meta, "duration_ms": duration_ms}
        events.add_movement_status(device_id, status_clave, meta_with_duration)

        await emit_to_device(
            device_id,
            "command_sent",
            {
                "device_id": device_id,
                "command": command,
                "status_clave": status_clave,
                "duration_ms": duration_ms,
                "meta": meta_with_duration,
            },
        )

    except Exception as e:
        await sio.emit("command_error", {"error": str(e)}, to=sid)
