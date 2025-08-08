from __future__ import annotations
from pathlib import Path
from .integrity import project_sih
from .utils import sha256_bytes

# Contexte = hash du set (fichiers racine + quelques marqueurs)
MARKERS = ["requirements.txt", "pyproject.toml", "package.json"]

def context_signature(root: Path) -> str:
    sih = project_sih(root)
    markers = [(m, Path(m).read_text(encoding="utf-8") if Path(m).exists() else "") for m in MARKERS]
    payload = "|".join([f"{k}:{v}" for k, v in sorted(sih.items())] + [f"{m[0]}:{m[1]}" for m in markers])
    return sha256_bytes(payload.encode("utf-8"))
