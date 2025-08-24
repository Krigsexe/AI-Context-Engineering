from __future__ import annotations
from pathlib import Path
import shutil, os


def latest_backup(backups: Path) -> Path|None:
    if not backups.exists():
        return None
    cands = sorted([p for p in backups.iterdir() if p.is_dir()])
    return cands[-1] if cands else None


def restore_from_backup(root: Path, backups: Path, *, mirror: bool=False) -> Path|None:
    b = latest_backup(backups)
    if not b:
        return None

    # Optionally remove files not present in backup (mirror mode)
    if mirror:
        # Build set of files in backup
        backup_files = set()
        for p in b.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(b)
            if rel.name == "manifest.json" and rel.parent == Path('.'):
                continue
            backup_files.add(rel)
        # Remove files not in backup
        for base, dirs, files in os.walk(root):
            basep = Path(base)
            for f in files:
                rel = (basep/ f).relative_to(root)
                # skip .odin
                if rel.parts and rel.parts[0] == ".odin":
                    continue
                if rel not in backup_files:
                    try:
                        (root/rel).unlink()
                    except FileNotFoundError:
                        pass

    for p in b.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(b)
        # do not restore the metadata file at project root
        if rel.name == "manifest.json" and rel.parent == Path('.'):
            continue
        dst = root/rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
    return b
