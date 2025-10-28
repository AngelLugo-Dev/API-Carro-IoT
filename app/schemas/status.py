from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class MovementCommandRequest(BaseModel):
    device_id: int
    command: str = Field(..., description="Comando de movimiento (forward, left, ...)")
    duration_ms: int = Field(default=1000, ge=50, le=30000)
    meta: Optional[Dict[str, Any]] = None


class ObstacleSimulateRequest(BaseModel):
    device_id: int
    distance_cm: int = Field(default=10, ge=1, le=1000)
    timestamp: Optional[str] = None


class SequenceItem(BaseModel):
    command: str
    duration: int


class ExecuteSequenceRequest(BaseModel):
    device_id: int
    sequence: List[SequenceItem]
    name: Optional[str] = Field(default="demo-web")
