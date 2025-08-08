from pathlib import Path
import json, hashlib
ROOT = Path.cwd()
ODIN_DIR = ROOT/".odin"
BACKUPS = ODIN_DIR/"backups"
def read_json(p: Path, default):
    return default if not p.exists() else json.loads(p.read_text(encoding="utf-8"))
def write_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256(); h.update(data); return h.hexdigest()
def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())
