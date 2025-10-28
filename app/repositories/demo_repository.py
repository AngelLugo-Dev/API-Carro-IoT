from typing import Any, Dict, List, Optional
from ..db import call_procedure
import json


def add_demo(device_id: int, demo_name: str, moves: List[Dict[str, int]]):
    moves_json = json.dumps(moves)
    rows = call_procedure("sp_add_demo", (device_id, demo_name, moves_json))
    # Stored proc returns demo_id in a result set
    if rows and "demo_id" in rows[0]:
        return rows[0]["demo_id"]
    return None


def get_last20_demos(device_id: int):
    return call_procedure("sp_get_last20_demos", (device_id,))


def repeat_demo(demo_id: int, repeats: int, start_at: Optional[str] = None):
    return call_procedure("sp_repeat_demo", (demo_id, repeats, start_at))
