"""Applies queued memory patches to the MW4 process."""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass

from src.core.attach import GameAttacher

log = logging.getLogger("mw4.driver.memory")


@dataclass
class Patch:
    address: int
    data: bytes


class MemoryDriver:
    name = "memory"

    def __init__(self, attacher: GameAttacher, dry_run: bool = False):
        self.attacher = attacher
        self.dry_run = dry_run
        self._queue: list[Patch] = []
        self._lock = threading.Lock()

    def enqueue(self, patch: Patch) -> None:
        with self._lock:
            self._queue.append(patch)

    def pump(self, stop: threading.Event) -> None:
        while not stop.is_set():
            with self._lock:
                batch, self._queue = self._queue, []
            for p in batch:
                if self.dry_run:
                    log.info("[dry-run] patch %#x (%d bytes)", p.address, len(p.data))
                    continue
                try:
                    self.attacher.pm.write_bytes(p.address, p.data, len(p.data))
                except Exception as exc:
                    log.warning("patch failed at %#x: %s", p.address, exc)
            stop.wait(0.05)