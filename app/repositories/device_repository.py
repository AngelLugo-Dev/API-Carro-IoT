from typing import Optional, Any
from ..db import execute


def upsert_device(device_name: str, client_ip: str, country: Optional[str] = None,
                   city: Optional[str] = None, latitude: Optional[float] = None,
                   longitude: Optional[float] = None) -> Any:
    sql = (
        "INSERT INTO devices (device_name, client_ip, country, city, latitude, longitude) "
        "VALUES (%s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE country=VALUES(country), city=VALUES(city), latitude=VALUES(latitude), "
        "longitude=VALUES(longitude), updated_at=CURRENT_TIMESTAMP"
    )
    res = execute(sql, (device_name, client_ip, country, city, latitude, longitude))
    # Fetch the device record
    rows = execute(
        "SELECT * FROM devices WHERE device_name=%s AND client_ip=%s",
        (device_name, client_ip),
    )
    device = rows[0] if rows else None  # type: ignore[index]
    return {"success": True, "device": device}


def get_devices() -> Any:
    return execute("SELECT * FROM devices ORDER BY created_at DESC")


def get_device(device_id: int) -> Any:
    rows = execute("SELECT * FROM devices WHERE id=%s", (device_id,))
    return rows[0] if rows else None  # type: ignore[index]
