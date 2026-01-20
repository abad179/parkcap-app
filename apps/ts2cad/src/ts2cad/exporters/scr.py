from __future__ import annotations

from pathlib import Path

from ts2cad.core.models import PointRecord


def export_scr(records: list[PointRecord], destination: Path, include_text: bool = True) -> None:
    lines: list[str] = []
    for record in records:
        z = record.z if record.z is not None else 0.0
        lines.append(f"POINT {record.x},{record.y},{z}")
        if include_text:
            label = f"{record.n} {record.desc}".strip()
            lines.append(f"TEXT {record.x},{record.y},{z} 2.5 0 {label}")
    destination.write_text("\n".join(lines), encoding="utf-8")
