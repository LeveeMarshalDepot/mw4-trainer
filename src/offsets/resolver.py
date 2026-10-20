"""Resolve symbolic offsets against a known MW4 build table."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

BUILD_DIR = Path(__file__).parent / "builds"


@dataclass
class OffsetResolver:
    build_id: str
    table: dict[str, int] = field(default_factory=dict)

    @classmethod
    def build_for_current_build(cls, build_id: str) -> "OffsetResolver":
        path = BUILD_DIR / f"{build_id}.json"
        if not path.exists():
            path = BUILD_DIR / "default.json"
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls(build_id=build_id, table={k: int(v, 0) for k, v in data.items()})

    def get(self, key: str, default: int = 0) -> int:
        return self.table.get(key, default)