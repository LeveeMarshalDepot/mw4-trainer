"""Build the ESP snapshot (boxes, names, health) from game state."""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

from src.core.attach import GameAttacher
from src.offsets.resolver import OffsetResolver

log = logging.getLogger("mw4.processor.esp")


@dataclass
class EspEntity:
    address: int
    world_x: float
    world_y: float
    world_z: float
    health: int
    team: int
    visible: bool


class EspProcessor:
    name = "esp"

    def __init__(self, attacher: GameAttacher, resolver: OffsetResolver):
        self.attacher = attacher
        self.resolver = resolver
        self.snapshot: list[EspEntity] = []
        self._lock = threading.Lock()

    def loop(self, stop: threading.Event) -> None:
        pm = self.attacher.pm
        base = pm.base_address
        entity_off = self.resolver.get("entity_list")
        stride = self.resolver.get("entity_stride", 0x1A0)
        while not stop.is_set():
            try:
                head = pm.read_uint(base + entity_off)
                count = min(pm.read_uint(base + entity_off + 0x8), 64)
                out: list[EspEntity] = []
                for i in range(count):
                    addr = head + i * stride
                    out.append(EspEntity(
                        address=addr,
                        world_x=pm.read_float(addr + 0x30),
                        world_y=pm.read_float(addr + 0x34),
                        world_z=pm.read_float(addr + 0x38),
                        health=pm.read_int(addr + 0x1C0),
                        team=pm.read_int(addr + 0x1F4),
                        visible=pm.read_int(addr + 0xE40) == 1,
                    ))
                with self._lock:
                    self.snapshot = out
            except Exception as exc:
                log.debug("esp read failed: %s", exc)
            stop.wait(0.033)

    def current(self) -> list[EspEntity]:
        with self._lock:
            return list(self.snapshot)