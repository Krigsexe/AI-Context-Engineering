from __future__ import annotations
import ast, os, re, textwrap
from pathlib import Path
from .utils import sha256_file, sha256_bytes

IGNORES = {".git", ".odin", "backups", "__pycache__"}

def is_python(p: Path) -> bool:
    return p.suffix == ".py"

def normalize_python_ast(src: str) -> str:
    src = textwrap.dedent(src)
    src = re.sub(r'^\s+', '', src, flags=re.MULTILINE)
    tree = ast.parse(src)
    # on ne garde que la structure
    return ast.dump(tree, annotate_fields=True, include_attributes=False)

def semantic_hash_file(p: Path) -> str:
    if is_python(p):
        try:
            return sha256_bytes(normalize_python_ast(p.read_text(encoding="utf-8")).encode("utf-8"))
        except Exception:
            pass
    # fallback : contenu brut
    return sha256_file(p)

def walk_files(root: Path) -> list[Path]:
    out = []
    for base, dirs, files in os.walk(root):
        basep = Path(base)
        # filtres
        dirs[:] = [d for d in dirs if d not in IGNORES]
        for f in files:
            p = basep/f
            if any(part in IGNORES for part in p.parts):
                continue
            out.append(p)
    return sorted(out)

def project_sih(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): semantic_hash_file(p) for p in walk_files(root)}
