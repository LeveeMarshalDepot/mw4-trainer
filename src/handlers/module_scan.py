"""Periodically rescan MW4 modules for entity list changes."""
from __future__ import annotations

import logging
import threading
import time

from src.core.attach import GameAttacher
from src.handlers.base import IngestHandler
from src.offsets.resolver import OffsetResolver

log = logging.getLogger("mw4.handler.module_scan")


class ModuleScanHandler(IngestHandler):
    name = "module_scan"

    def __init__(self, attacher: GameAttacher, resolver: OffsetResolver, interval: float = 0.25):
        self.attacher = attacher
        self.resolver = resolver
        self.interval = interval
        self._entity_sig: int = 0

    def run(self, stop: threading.Event) -> None:
        pm = self.attacher.pm
        base = pm.base_address
        entity_off = self.resolver.get("entity_list")
        while not stop.is_set():
            try:
                count = pm.read_uint(base + entity_off + 0x8)
                if count != self._entity_sig:
                    log.debug("entity list changed: %d", count)
                    self._entity_sig = count
            except Exception as exc:  # game may be resizing lists
                log.debug("entity scan failed: %s", exc)
            stop.wait(self.interval)