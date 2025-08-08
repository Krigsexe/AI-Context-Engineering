from __future__ import annotations
from pathlib import Path
import shutil, time
from .utils import write_json

def create_backup(root: Path, manifest: dict[str, str], backups_dir: Path):
    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = backups_dir/f"{ts}"
    dest.mkdir(parents=True)
    # copie sélective (tous fichiers non .odin)
    for rel in manifest.keys():
        src = Path(rel)
        dst = dest/rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    write_json(dest/"manifest.json", {"created": ts, "files": manifest})
    return dest
