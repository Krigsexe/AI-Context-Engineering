from __future__ import annotations
from pathlib import Path
import json, time

class TMS:
    def __init__(self, db: Path):
        self.db = db
        if not db.exists():
            db.write_text(json.dumps({"facts": []}, indent=2))

    def add(self, claim: str, sources: list[str]):
        obj = json.loads(self.db.read_text())
        obj["facts"].append({
            "claim": claim,
            "sources": sources,
            "ts": int(time.time())
        })
        self.db.write_text(json.dumps(obj, indent=2))

    def invalidate_by_source(self, source_id: str):
        obj = json.loads(self.db.read_text())
        for f in obj["facts"]:
            if source_id in f.get("sources", []):
                f["invalidated"] = True
        self.db.write_text(json.dumps(obj, indent=2))
