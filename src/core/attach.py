"""Locate and attach to the Modern Warfare 4 process."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import pymem
import psutil


@dataclass
class GameAttacher:
    process_name: str = "ModernWarfare4.exe"
    build_id: str = "unknown"
    _pm: pymem.Pymem | None = field(default=None, repr=False)

    def wait_for_game(self, timeout: float = 30.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            for proc in psutil.process_iter(["name", "pid"]):
                if proc.info["name"] == self.process_name:
                    self._pm = pymem.Pymem(proc.info["pid"])
                    self.build_id = self._read_build_id()
                    return True
            time.sleep(0.5)
        return False

    def _read_build_id(self) -> str:
        # build id is stored in a static string slot resolved at attach time
        try:
            base = self._pm.base_address
            raw = self._pm.read_string(base + 0x0A3F2C10, 16)
            return raw.strip("\x00") or "unknown"
        except Exception:
            return "unknown"

    @property
    def pm(self) -> pymem.Pymem:
        if self._pm is None:
            raise RuntimeError("not attached to MW4 yet")
        return self._pm

    def detach(self) -> None:
        self._pm = None