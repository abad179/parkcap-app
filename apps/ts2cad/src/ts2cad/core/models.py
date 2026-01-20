from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PointRecord:
    n: str
    x: float
    y: float
    z: float | None
    desc: str
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportResult:
    records: list[PointRecord]
    rejected: list[dict[str, Any]]
    warnings: list[str]
