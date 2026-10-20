"""Small memory helpers shared across processors."""
from __future__ import annotations

import struct


def read_vec3(pm, address: int) -> tuple[float, float, float]:
    raw = pm.read_bytes(address, 12)
    return struct.unpack("<fff", raw)


def read_angle(pm, address: int) -> tuple[float, float]:
    raw = pm.read_bytes(address, 8)
    return struct.unpack("<ff", raw)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))