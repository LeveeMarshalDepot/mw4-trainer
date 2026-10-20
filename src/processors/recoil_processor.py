"""Recoil control — smooths mouse delta while the trigger is held."""
from __future__ import annotations

import threading
from collections import deque

import pynput.mouse


class RecoilProcessor:
    name = "recoil"

    def __init__(self, attacher, resolver, strength: float = 0.6):
        self.attacher = attacher
        self.resolver = resolver
        self.strength = strength
        self.enabled = True
        self._history: deque[tuple[int, int]] = deque(maxlen=8)
        self._mouse = pynput.mouse.Controller()

    def loop(self, stop: threading.Event) -> None:
        while not stop.is_set():
            if self.enabled:
                dx, dy = self._estimate_pattern()
                if dx or dy:
                    self._mouse.move(int(dx * self.strength), int(dy * self.strength))
            stop.wait(0.016)

    def _estimate_pattern(self) -> tuple[float, float]:
        if len(self._history) < 2:
            return 0.0, 0.0
        recent = list(self._history)
        avg_x = sum(p[0] for p in recent) / len(recent)
        avg_y = sum(p[1] for p in recent) / len(recent)
        return -avg_x * 0.1, -avg_y * 0.15

    def push(self, dx: int, dy: int) -> None:
        self._history.append((dx, dy))