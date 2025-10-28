from typing import Any, Dict, List, Optional, Tuple
from ..db import execute, call_procedure


def add_movement_status(device_id: int, status_clave: int, meta: Optional[Dict[str, Any]] = None):
    meta_json = None if meta is None else __import__("json").dumps(meta)
    return call_procedure("sp_add_movement_status", (device_id, status_clave, meta_json))


def get_last_movement_status(device_id: int):
    rows = call_procedure("sp_get_last_movement_status", (device_id,))
    return rows[0] if rows else None


def get_last10_movement_status(device_id: int):
    return call_procedure("sp_get_last10_movement_status", (device_id,))


def add_obstacle_status(device_id: int, status_clave: int, meta: Optional[Dict[str, Any]] = None):
    meta_json = None if meta is None else __import__("json").dumps(meta)
    return call_procedure("sp_add_obstacle_status", (device_id, status_clave, meta_json))


def get_last_obstacle_status(device_id: int):
    rows = call_procedure("sp_get_last_obstacle_status", (device_id,))
    return rows[0] if rows else None


def get_last10_obstacle_status(device_id: int):
    return call_procedure("sp_get_last10_obstacle_status", (device_id,))


def get_events(device_id: int, limit: int = 50):
    sql = (
        "SELECT de.id, de.device_id, de.event_type, de.status_clave, "
        "COALESCE(os.status_texto, obs.status_texto) AS status_description, "
        "de.demo_id, de.event_ts, de.meta "
        "FROM device_events de "
        "LEFT JOIN op_status os ON os.status_clave = de.status_clave AND de.event_type='movement' "
        "LEFT JOIN obstacle_status obs ON obs.status_clave = de.status_clave AND de.event_type='obstacle' "
        "WHERE de.device_id=%s "
        "ORDER BY de.event_ts DESC LIMIT %s"
    )
    return execute(sql, (device_id, limit))


def get_operational_status():
    return execute("SELECT status_clave, status_texto, description FROM op_status ORDER BY status_clave ASC")
