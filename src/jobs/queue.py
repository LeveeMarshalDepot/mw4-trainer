"""Thin worker pool used by the pipeline."""
from __future__ import annotations

import logging
import threading
from typing import Callable

log = logging.getLogger("mw4.jobs")


class JobQueue:
    def __init__(self) -> None:
        self._threads: list[threading.Thread] = []

    def spawn(self, target: Callable, *args, name: str | None = None) -> threading.Thread:
        t = threading.Thread(target=self._wrap, args=(target, *args), name=name or target.__name__, daemon=True)
        self._threads.append(t)
        t.start()
        return t

    @staticmethod
    def _wrap(target: Callable, *args) -> None:
        try:
            target(*args)
        except Exception as exc:
            log.exception("job %s crashed: %s", getattr(target, "__name__", "?"), exc)

    def join(self, timeout: float | None = None) -> None:
        for t in self._threads:
            t.join(timeout=timeout)