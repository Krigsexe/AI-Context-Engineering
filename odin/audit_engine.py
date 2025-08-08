from __future__ import annotations
from pathlib import Path
from .integrity import project_sih
from .checkpoint import AUDIT_REPORT

HEADER = """# ODIN Audit Report (v6.1)\n\n"""

def run_audit(root: Path) -> dict:
    sih = project_sih(root)
    # très simple : on consigne juste la carte SIH
    changed = len(sih)
    body = [HEADER, f"- Files hashed: {changed}\n"]
    # on liste les 20 premiers pour inspection rapide
    for i, (k, v) in enumerate(sih.items()):
        if i >= 20: break
        body.append(f"  - {k}: {v}\n")
    AUDIT_REPORT.write_text("".join(body), encoding="utf-8")
    return {"file_count": changed, "sih_root": hash(tuple(sorted(sih.values())))}
