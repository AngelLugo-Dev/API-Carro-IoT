from fastapi import APIRouter
from ..schemas.status import ObstacleSimulateRequest
from ..repositories import events_repository as events
from ..services.websocket_manager import emit_to_device

router = APIRouter(prefix="/api/simulate", tags=["simulate"]) 


@router.post("/obstacle")
async def simulate_obstacle(payload: ObstacleSimulateRequest):
    # choose obstacle status by distance (simple heuristic)
    distance = payload.distance_cm
    if distance < 10:
        status_clave = 4  # multiple fronts
    elif distance < 20:
        status_clave = 1  # adelante
    else:
        status_clave = 2  # adelante-izquierda (arbitrary)

    meta = {"distance_cm": distance, "origin": "simulation"}
    if payload.timestamp:
        meta["timestamp"] = payload.timestamp

    events.add_obstacle_status(payload.device_id, status_clave, meta)

    await emit_to_device(
        payload.device_id,
        "obstacle_alert",
        {"device_id": payload.device_id, "status_clave": status_clave, "meta": meta},
    )

    return {"success": True}
