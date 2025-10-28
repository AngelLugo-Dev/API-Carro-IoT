from fastapi import APIRouter, Request
from ..repositories import device_repository as repo
from ..schemas.device import DeviceRegisterRequest

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("")
def list_devices():
    devices = repo.get_devices()
    return {"success": True, "devices": devices}


@router.get("/{device_id}")
def get_device(device_id: int):
    device = repo.get_device(device_id)
    if device:
        return {"success": True, "device": device}
    return {"success": False, "error": "Device not found"}


@router.post("/register")
def register_device(payload: DeviceRegisterRequest, request: Request):
    client_ip = request.client.host
    result = repo.upsert_device(
        device_name=payload.device_name,
        client_ip=client_ip,
        country=payload.country,
        city=payload.city,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    return result
