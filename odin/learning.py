from __future__ import annotations
from .checkpoint import LEARNING_LOG
from .utils import read_json, write_json

def log(event: str, data: dict|None=None):
    obj = read_json(LEARNING_LOG, {"entries": []})
    obj["entries"].append({"event": event, "data": data or {}})
    write_json(LEARNING_LOG, obj)
