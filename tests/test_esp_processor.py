from src.processors.esp_processor import EspEntity, EspProcessor


def test_esp_snapshot_is_threaded():
    proc = EspProcessor(attacher=None, resolver=None)  # type: ignore[arg-type]
    assert proc.current() == []
    proc.snapshot = [EspEntity(0x1000, 1.0, 2.0, 3.0, 100, 1, True)]
    snap = proc.current()
    assert len(snap) == 1
    assert snap[0].health == 100
    assert snap[0].visible is True