from __future__ import annotations
from .checkpoint import get_config

PROFILES = ("low", "med", "high")

def profile(name: str) -> dict:
    cfg = get_config()
    return cfg.get("router", {}).get(name, cfg["router"]["low"])
