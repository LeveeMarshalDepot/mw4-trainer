"""Ingest -> processor -> driver job pipeline."""
from __future__ import annotations

import logging
import queue
import threading
from dataclasses import dataclass, field

from src.core.attach import GameAttacher
from src.offsets.resolver import OffsetResolver
from src.handlers.base import IngestHandler
from src.handlers.module_scan import ModuleScanHandler
from src.handlers.input_hook import InputHookHandler
from src.processors.esp_processor import EspProcessor
from src.processors.aimbot_processor import AimbotProcessor
from src.processors.recoil_processor import RecoilProcessor
from src.drivers.overlay_driver import OverlayDriver
from src.drivers.memory_driver import MemoryDriver
from src.jobs.queue import JobQueue

log = logging.getLogger("mw4.pipeline")


@dataclass
class TrainerPipeline:
    attacher: GameAttacher
    resolver: OffsetResolver
    profile: str = "default"
    overlay: bool = True
    dry_run: bool = False
    _stop: threading.Event = field(default_factory=threading.Event)
    _jobs: JobQueue = field(default_factory=JobQueue)

    def _build_handlers(self) -> list[IngestHandler]:
        return [
            ModuleScanHandler(self.attacher, self.resolver),
            InputHookHandler(self.attacher),
        ]

    def _build_processors(self):
        procs = [
            EspProcessor(self.attacher, self.resolver),
            AimbotProcessor(self.attacher, self.resolver),
            RecoilProcessor(self.attacher, self.resolver),
        ]
        return procs

    def run_forever(self) -> None:
        handlers = self._build_handlers()
        processors = self._build_processors()
        drivers = [MemoryDriver(self.attacher, self.dry_run)]
        if self.overlay:
            drivers.append(OverlayDriver(processors))

        for h in handlers:
            self._jobs.spawn(h.run, self._stop)
        for p in processors:
            self._jobs.spawn(p.loop, self._stop)
        for d in drivers:
            self._jobs.spawn(d.pump, self._stop)

        log.info("pipeline running: %d handlers, %d processors, %d drivers",
                 len(handlers), len(processors), len(drivers))
        self._stop.wait()

    def shutdown(self) -> None:
        self._stop.set()
        self._jobs.join(timeout=3.0)
        self.attacher.detach()