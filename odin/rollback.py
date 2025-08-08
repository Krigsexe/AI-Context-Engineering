from __future__ import annotations
from pathlib import Path
import shutil

def latest_backup(backups: Path) -> Path|None:
    if not backups.exists():
        return None
    cands = sorted([p for p in backups.iterdir() if p.is_dir()])
    return cands[-1] if cands else None

def restore_from_backup(root: Path, backups: Path) -> Path|None:
    b = latest_backup(backups)
    if not b:
        return None
    for p in b.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(b)
        dst = root/rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
    return b
