from fastapi import APIRouter
from ..repositories import events_repository as events

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get("/operational")
def get_operational_status():
    rows = events.get_operational_status()
    return {"success": True, "statuses": rows}
