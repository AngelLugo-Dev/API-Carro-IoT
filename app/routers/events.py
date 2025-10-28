from fastapi import APIRouter
from ..repositories import events_repository as repo

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/{device_id}")
def get_events(device_id: int, limit: int = 50):
    rows = repo.get_events(device_id, limit)
    return {"success": True, "events": rows}
