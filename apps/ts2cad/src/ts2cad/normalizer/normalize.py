from __future__ import annotations

import re
from typing import Iterable

from ts2cad.core.models import PointRecord


SPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    return SPACE_RE.sub(" ", value.strip())


def parse_float(value: str, decimal_comma: bool) -> float:
    cleaned = value.strip()
    if decimal_comma:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        cleaned = cleaned.replace(",", ".")
    return float(cleaned)


def normalize_records(
    records: Iterable[PointRecord],
    decimal_comma: bool,
    renumber: bool,
    renumber_start: int,
    units_to_meters: bool,
) -> tuple[list[PointRecord], dict[str, int]]:
    normalized: list[PointRecord] = []
    duplicates: dict[str, int] = {"id": 0, "coords": 0}
    seen_ids: set[str] = set()
    seen_coords: set[tuple[float, float]] = set()
    current_id = renumber_start

    for record in records:
        record.desc = normalize_text(record.desc)
        if units_to_meters:
            # assume input already meters by default
            pass
        if renumber:
            record.n = str(current_id)
            current_id += 1
        if record.n in seen_ids:
            duplicates["id"] += 1
        else:
            seen_ids.add(record.n)
        coord_key = (record.x, record.y)
        if coord_key in seen_coords:
            duplicates["coords"] += 1
        else:
            seen_coords.add(coord_key)
        normalized.append(record)
    return normalized, duplicates
