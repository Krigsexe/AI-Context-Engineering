from __future__ import annotations
import hashlib, os, json, time, shutil, contextlib
from pathlib import Path

ROOT = Path.cwd()
ODIN_DIR = ROOT/".odin"
BACKUPS = ODIN_DIR/"backups"

class OError(RuntimeError):
    pass

def read_json(p: Path, default):
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def write_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

@contextlib.contextmanager
def atomic_copy(src: Path, dst: Path):
    tmp = dst.with_suffix(".tmp")
    shutil.copy2(src, tmp)
    yield tmp
    tmp.replace(dst)

def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256(); h.update(data); return h.hexdigest()

def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())
