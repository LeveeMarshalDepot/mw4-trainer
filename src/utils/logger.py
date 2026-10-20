"""Logging setup for the trainer."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")


def setup_logging(verbose: bool = False) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    fmt = "%(asctime)s %(levelname)-7s %(name)s :: %(message)s"
    level = logging.DEBUG if verbose else logging.INFO
    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "trainer.log", encoding="utf-8"),
    ]
    logging.basicConfig(level=level, format=fmt, handlers=handlers)