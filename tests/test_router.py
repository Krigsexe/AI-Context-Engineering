from odin.router import profile

def test_router_profiles_default():
    assert profile("low")["grounded_only"] is True
