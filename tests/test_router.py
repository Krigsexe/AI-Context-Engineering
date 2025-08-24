from odin.router import profile
from odin.cli import cmd_start
from odin.checkpoint import get_checkpoint
class Args:
    risk = "low"
    allow_drift = True


def test_router_profiles_default():
    assert profile("low")["grounded_only"] is True


def test_start_updates_risk_profile(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_start(Args())
    ckpt = get_checkpoint()
    assert ckpt["risk_profile"] == "low"
