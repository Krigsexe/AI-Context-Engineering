from __future__ import annotations
from pathlib import Path
from .integrity import project_sih
from .checkpoint import AUDIT_REPORT, get_checkpoint

HEADER = """# ODIN Audit Report (v6.1)\n\n"""


def _diff_sih(prev: dict[str, str], curr: dict[str, str]) -> dict:
    prev_keys = set(prev.keys())
    curr_keys = set(curr.keys())
    added = sorted(curr_keys - prev_keys)
    removed = sorted(prev_keys - curr_keys)
    modified = sorted([k for k in (prev_keys & curr_keys) if prev.get(k) != curr.get(k)])
    return {"added": added, "removed": removed, "modified": modified}


def run_audit(root: Path) -> dict:
    sih = project_sih(root)
    ckpt = get_checkpoint()
    prev = ckpt.get("sih_snapshot", {}) if isinstance(ckpt, dict) else {}
    diff = _diff_sih(prev, sih)

    file_count = len(sih)
    added, removed, modified = diff["added"], diff["removed"], diff["modified"]

    body = [
        HEADER,
        f"- Files hashed: {file_count}\n",
        f"- Added: {len(added)}, Removed: {len(removed)}, Modified: {len(modified)}\n",
        "\n## Top changes (up to 20)\n",
    ]
    # list some changes for quick inspection
    showcase = added[:7] + removed[:7] + modified[:6]
    for k in showcase:
        tag = "A" if k in added else ("R" if k in removed else "M")
        body.append(f"  - [{tag}] {k}\n")

    AUDIT_REPORT.write_text("".join(body), encoding="utf-8")

    return {
        "file_count": file_count,
        "sih_root": hash(tuple(sorted(sih.values()))),
        "diff": diff,
        "sih_snapshot": sih,
    }
