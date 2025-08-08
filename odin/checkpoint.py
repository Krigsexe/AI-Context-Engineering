from __future__ import annotations
from pathlib import Path
from .utils import ODIN_DIR, write_json, read_json

AI_CHECKPOINT = ODIN_DIR/"AI_CHECKPOINT.json"
CONFIG = ODIN_DIR/"config.json"
LEARNING_LOG = ODIN_DIR/"learning_log.json"
AUDIT_REPORT = ODIN_DIR/"audit_report.md"
LOCK = ODIN_DIR/"odin.lock"

DEFAULTS = {
  "AI_CHECKPOINT.json": {
    "instance": {"locked": False, "pid": None},
    "last_audit": None, "last_backup": None,
    "sih_root": None, "risk_profile": "low", "commit": None
  },
  "config.json": {
    "version": "6.1.0",
    "slo": {"hallucination_max_rate": 0.005},
    "router": {
      "low": {"reasoning_effort": "minimal", "double_pass": False, "grounded_only": True},
      "med": {"reasoning_effort": "standard", "double_pass": True,  "grounded_only": True},
      "high": {"reasoning_effort": "max",     "double_pass": True,  "grounded_only": True}
    },
    "allowed_tools": ["local_rag", "unit_tests", "integrity_check"],
    "schema_guard": {"enabled": True}
  },
  "learning_log.json": {"entries": []}
}

def ensure_scaffold():
    ODIN_DIR.mkdir(exist_ok=True)
    for name, default in DEFAULTS.items():
        p = ODIN_DIR/name
        if not p.exists():
            write_json(p, default)
    (ODIN_DIR/"backups").mkdir(exist_ok=True)
    (ODIN_DIR/"docs_cache").mkdir(exist_ok=True)
    (ODIN_DIR/"audit_report.md").touch(exist_ok=True)

def lock_instance():
    ensure_scaffold()
    if LOCK.exists():
        raise RuntimeError("ODIN instance already running (lock present)")
    LOCK.write_text("locked\n", encoding="utf-8")

def unlock_instance():
    if LOCK.exists():
        LOCK.unlink()

def get_config():
    ensure_scaffold(); from .utils import read_json
    return read_json(CONFIG, DEFAULTS["config.json"])

def get_checkpoint():
    ensure_scaffold(); return read_json(AI_CHECKPOINT, DEFAULTS["AI_CHECKPOINT.json"])

def update_checkpoint(**kwargs):
    data = get_checkpoint(); data.update(kwargs); write_json(AI_CHECKPOINT, data)
