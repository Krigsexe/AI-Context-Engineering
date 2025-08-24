from pathlib import Path
from odin.integrity import semantic_hash_file
from odin.audit_engine import run_audit
from odin.checkpoint import get_checkpoint


def test_semantic_hash_is_stable(tmp_path: Path):
    p = tmp_path/"a.py"
    p.write_text("x=1\n# comment\n x=1\n")
    h1 = semantic_hash_file(p)
    p.write_text("x=1\n# other comment\n x=1\n")
    h2 = semantic_hash_file(p)
    assert h1 == h2


def test_audit_diff_and_snapshot(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path/"a.txt").write_text("one\n")
    out1 = run_audit(tmp_path)
    assert out1["file_count"] >= 1
    # add a file; re-run
    (tmp_path/"b.txt").write_text("two\n")
    out2 = run_audit(tmp_path)
    assert "diff" in out2
    assert "added" in out2["diff"]
    # checkpoint should be updated by CLI but audit returns snapshot for caller
