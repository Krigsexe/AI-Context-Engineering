from pathlib import Path
from odin.integrity import semantic_hash_file

def test_semantic_hash_is_stable(tmp_path: Path):
    p = tmp_path/"a.py"
    p.write_text("x=1\n# comment\n x=1\n")
    h1 = semantic_hash_file(p)
    p.write_text("x=1\n# other comment\n x=1\n")
    h2 = semantic_hash_file(p)
    assert h1 == h2
