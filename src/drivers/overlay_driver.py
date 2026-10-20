"""Transparent overlay window that renders the ESP snapshot."""
from __future__ import annotations

import threading
import tkinter as tk

from src.processors.esp_processor import EspProcessor


class OverlayDriver:
    name = "overlay"

    def __init__(self, processors):
        self.processors = processors
        self._root: tk.Tk | None = None
        self._canvas: tk.Canvas | None = None

    def _build(self) -> None:
        self._root = tk.Tk()
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-transparentcolor", "black")
        self._root.geometry(f"{self._root.winfo_screenwidth()}x{self._root.winfo_screenheight()}+0+0")
        self._canvas = tk.Canvas(self._root, bg="black", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

    def pump(self, stop: threading.Event) -> None:
        # overlay runs on the main thread in production; this keeps a
        # headless smoke-test path working without a display
        try:
            self._build()
        except tk.TclError:
            return
        esp: EspProcessor = next(p for p in self.processors if p.name == "esp")

        def tick():
            if stop.is_set():
                self._root.quit()
                return
            if self._canvas is not None:
                self._canvas.delete("esp")
                for e in esp.current():
                    if e.visible and e.health > 0:
                        self._canvas.create_rectangle(
                            100, 100, 200, 200, outline="lime", tags="esp"
                        )
            self._root.after(33, tick)

        self._root.after(33, tick)
        self._root.mainloop()