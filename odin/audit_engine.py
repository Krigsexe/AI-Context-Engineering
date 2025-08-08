from pathlib import Path
from .integrity import project_sih
from .checkpoint import ensure_scaffold, AUDIT_REPORT
HEADER = "# ODIN Audit Report (v6.1)\n\n"
def run_audit(root: Path)->dict:
    ensure_scaffold()
    sih = project_sih(root)
    body=[HEADER, f"- Files hashed: {len(sih)}\n"]
    for i, (k,v) in enumerate(sih.items()):
        if i>=20: break
        body.append(f"  - {k}: {v}\n")
    AUDIT_REPORT.write_text("".join(body), encoding="utf-8")
    return {"file_count": len(sih), "sih_root": hash(tuple(sorted(sih.values())))}
