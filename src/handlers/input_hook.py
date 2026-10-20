"""Keyboard/mouse hook for toggling trainer features."""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field

from pynput import keyboard

from src.core.attach import GameAttacher
from src.handlers.base import IngestHandler

log = logging.getLogger("mw4.handler.input_hook")


@dataclass
class FeatureToggles:
    esp: bool = True
    aimbot: bool = False
    recoil: bool = True
    extras: dict[str, bool] = field(default_factory=dict)


class InputHookHandler(IngestHandler):
    name = "input_hook"

    def __init__(self, attacher: GameAttacher):
        self.attacher = attacher
        self.toggles = FeatureToggles()
        self._listener: keyboard.Listener | None = None

    def run(self, stop: threading.Event) -> None:
        def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
            try:
                k = key.char
            except AttributeError:
                return
            if k == "f1":
                self.toggles.esp = not self.toggles.esp
                log.info("esp toggled -> %s", self.toggles.esp)
            elif k == "f2":
                self.toggles.aimbot = not self.toggles.aimbot
                log.info("aimbot toggled -> %s", self.toggles.aimbot)
            elif k == "f3":
                self.toggles.recoil = not self.toggles.recoil
                log.info("recoil toggled -> %s", self.toggles.recoil)

        self._listener = keyboard.Listener(on_press=on_press)
        self._listener.start()
        stop.wait()
        if self._listener:
            self._listener.stop()