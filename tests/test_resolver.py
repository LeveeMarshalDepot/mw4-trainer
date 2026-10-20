from src.offsets.resolver import OffsetResolver


def test_default_build_loads():
    r = OffsetResolver.build_for_current_build("nonexistent-build")
    assert r.get("entity_list") > 0
    assert r.get("entity_stride") == 0x1A0


def test_missing_key_falls_back():
    r = OffsetResolver(build_id="x", table={"entity_list": 0x1000})
    assert r.get("entity_list") == 0x1000
    assert r.get("recoil_table", 0xDEAD) == 0xDEAD