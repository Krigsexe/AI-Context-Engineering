from pathlib import Path
from .utils import ODIN_DIR, write_json
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
      "low": {"reasoning_effort": "minimal","double_pass": False,"grounded_only": True},
      "med": {"reasoning_effort": "standard","double_pass": True,"grounded_only": True},
      "high":{"reasoning_effort": "max","double_pass": True,"grounded_only": True}
    },
    "allowed_tools": ["local_rag","unit_tests","integrity_check"],
    "schema_guard": {"enabled": True}
  },
  "learning_log.json": {"entries": []}
}
def ensure_scaffold():
    ODIN_DIR.mkdir(exist_ok=True)
    for name, default in DEFAULTS.items():
        p = ODIN_DIR/name
        if not p.exists(): write_json(p, default)
    (ODIN_DIR/"backups").mkdir(exist_ok=True)
    (ODIN_DIR/"docs_cache").mkdir(exist_ok=True)
    (ODIN_DIR/"audit_report.md").touch(exist_ok=True)
