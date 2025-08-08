from odin.checkpoint import ensure_scaffold, get_checkpoint

def test_scaffold_and_checkpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ensure_scaffold()
    data = get_checkpoint()
    assert data["risk_profile"] == "low"
