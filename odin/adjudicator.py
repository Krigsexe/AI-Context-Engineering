from __future__ import annotations

# Double-pass naïf : on compare deux sorties (déjà normalisées) et on retient
# l'intersection des phrases contenant des preuves [[G:...]].

def adjudicate(a: str, b: str) -> str:
    sa = set(_sentences_with_proofs(a))
    sb = set(_sentences_with_proofs(b))
    keep = sa.intersection(sb)
    return " ".join(sorted(keep))

def _sentences_with_proofs(text: str) -> list[str]:
    import re
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sents if "[[G:" in s]
