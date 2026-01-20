from __future__ import annotations

import csv
from pathlib import Path

from ts2cad.core.config import ExportFormatConfig
from ts2cad.core.models import PointRecord


TEMPLATE_MAP = {
    "NXY": ["n", "x", "y"],
    "NYX": ["n", "y", "x"],
    "PNEZD": ["n", "y", "x", "z", "desc"],
    "PENZD": ["n", "x", "y", "z", "desc"],
    "NXYZ": ["n", "x", "y", "z"],
}


def export_txt(records: list[PointRecord], destination: Path, config: ExportFormatConfig) -> None:
    template = config.template
    if template == "CUSTOM":
        export_custom(records, destination, config)
        return
    columns = TEMPLATE_MAP.get(template, TEMPLATE_MAP["NXY"])
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=config.separator or " ")
        if config.include_header:
            writer.writerow(columns)
        for record in records:
            writer.writerow([format_value(record, col, config) for col in columns])


def export_csv(records: list[PointRecord], destination: Path, config: ExportFormatConfig) -> None:
    columns = ["n", "x", "y", "z", "desc"]
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=config.separator or ",")
        if config.include_header:
            writer.writerow(columns)
        for record in records:
            writer.writerow([format_value(record, col, config) for col in columns])


def export_custom(records: list[PointRecord], destination: Path, config: ExportFormatConfig) -> None:
    with destination.open("w", encoding="utf-8") as handle:
        if config.include_header:
            handle.write(config.custom_pattern + "\n")
        for record in records:
            line = config.custom_pattern.format(
                n=record.n,
                x=format_value(record, "x", config),
                y=format_value(record, "y", config),
                z=format_value(record, "z", config),
                desc=record.desc,
            )
            handle.write(line + "\n")


def format_value(record: PointRecord, field: str, config: ExportFormatConfig) -> str:
    value = getattr(record, field)
    if value is None:
        return ""
    if isinstance(value, float):
        fmt = f"{{:.{config.decimals}f}}"
        formatted = fmt.format(value)
        if config.decimal_comma:
            return formatted.replace(".", ",")
        return formatted
    return str(value)
