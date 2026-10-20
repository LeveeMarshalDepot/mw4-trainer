"""Aim assist / aimbot: pick best target, compute delta to screen center."""
from __future__ import annotations

import logging
import math
import threading
from dataclasses import dataclass

from src.core.attach import GameAttacher
from src.offsets.resolver import OffsetResolver

log = logging.getLogger("mw4.processor.aimbot")


@dataclass
class AimTarget:
    address: int
    screen_x: float
    screen_y: float
    distance: float


class AimbotProcessor:
    name = "aimbot"

    def __init__(self, attacher: GameAttacher, resolver: OffsetResolver, fov: float = 120.0):
        self.attacher = attacher
        self.resolver = resolver
        self.fov = fov
        self.target: AimTarget | None = None
        self.enabled = False

    def _world_to_screen(self, wx: float, wy: float, wz: float) -> tuple[float, float] | None:
        pm = self.attacher.pm
        view = pm.base_address + self.resolver.get("view_matrix")
        m = [pm.read_float(view + i * 4) for i in range(16)]
        x = wx * m[0] + wy * m[4] + wz * m[8] + m[12]
        y = wx * m[1] + wy * m[5] + wz * m[9] + m[13]
        w = wx * m[3] + wy * m[7] + wz * m[11] + m[15]
        if w <= 0.001:
            return None
        return (x / w + 1.0) * 960.0, (1.0 - y / w) * 540.0

    def loop(self, stop: threading.Event) -> None:
        while not stop.is_set():
            if not self.enabled:
                self.target = None
                stop.wait(0.05)
                continue
            # target selection is driven by the ESP snapshot in the full build;
            # here we just refresh the delta against the current best candidate
            if self.target is not None:
                proj = self._world_to_screen(0.0, 0.0, 0.0)
                if proj is not None:
                    self.target.screen_x, self.target.screen_y = proj
            stop.wait(0.016)

    def set_target(self, t: AimTarget | None) -> None:
        if t is None:
            self.target = None
            return
        dist = math.hypot(t.screen_x - 960.0, t.screen_y - 540.0)
        if dist <= self.fov:
            self.target = t