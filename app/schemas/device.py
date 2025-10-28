from pydantic import BaseModel, Field
from typing import Optional


class DeviceRegisterRequest(BaseModel):
    device_name: str = Field(..., min_length=1, max_length=100)
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DeviceResponse(BaseModel):
    success: bool
    device: dict
