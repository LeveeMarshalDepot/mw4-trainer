"""Base contract for ingest handlers."""
from __future__ import annotations

import abc
import threading


class IngestHandler(abc.ABC):
    name: str = "handler"

    @abc.abstractmethod
    def run(self, stop: threading.Event) -> None:
        """Block until `stop` is set, pushing updates into the shared state."""