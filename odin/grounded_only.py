from __future__ import annotations
from pathlib import Path

# Règle : toute assertion non triviale doit contenir un marqueur [[G:...]]
# On offre aussi une interface pour valider un mapping JSON {claim: [sources]}

def extract_proofs(text: str) -> list[str]:
    import re
    return re.findall(r"\[\[G:([^\]]+)\]\]", text)

def is_grounded(text: str, min_refs: int = 1) -> bool:
    return len(set(extract_proofs(text))) >= min_refs
