from odin.checkpoint import ensure_scaffold, get_checkpoint
from odin.cli import cmd_init
class Args: pass


def test_scaffold_and_checkpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ensure_scaffold()
    data = get_checkpoint()
    assert data["risk_profile"] == "low"

    # run init to populate snapshot and context signature
    cmd_init(Args())
    data2 = get_checkpoint()
    assert isinstance(data2.get("sih_snapshot"), dict)
    assert data2.get("context_sig")
