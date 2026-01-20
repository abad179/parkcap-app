from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from ts2cad.core.models import ImportResult, PointRecord
from ts2cad.importers.base import Importer
from ts2cad.normalizer.normalize import parse_float, normalize_text


HEADER_ALIASES = {
    "n": {"id", "punto", "point", "pt"},
    "x": {"x", "este", "e", "easting"},
    "y": {"y", "norte", "n", "northing"},
    "z": {"z", "cota", "elev", "elevation"},
    "desc": {"desc", "descripcion", "código", "codigo", "code", "description"},
}


class GenericImporter(Importer):
    name = "Genérico TXT/CSV"

    def __init__(self, decimal_comma: bool = False, separator: str | None = None) -> None:
        self.decimal_comma = decimal_comma
        self.separator = separator

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in {".txt", ".csv"}

    def parse(self, path: Path) -> ImportResult:
        warnings: list[str] = []
        rejected: list[dict[str, str]] = []
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            sample = handle.read(2048)
            handle.seek(0)
            delimiter = self.separator or sniff_delimiter(sample)
            reader = csv.reader(handle, delimiter=delimiter)
            rows = list(reader)

        if not rows:
            return ImportResult(records=[], rejected=[], warnings=["Archivo vacío"])

        header = rows[0]
        if has_header(header):
            mapping = map_headers(header)
            data_rows = rows[1:]
        else:
            mapping = {"n": 0, "x": 1, "y": 2, "z": 3, "desc": 4}
            data_rows = rows
            warnings.append("Encabezados no detectados; se asume orden n,x,y,z,desc")

        records: list[PointRecord] = []
        for idx, row in enumerate(data_rows, start=1):
            if not row:
                continue
            record = parse_row(row, mapping, self.decimal_comma)
            if record is None:
                rejected.append({"line": str(idx), "row": str(row)})
                continue
            records.append(record)

        return ImportResult(records=records, rejected=rejected, warnings=warnings)


def sniff_delimiter(sample: str) -> str:
    for delimiter in [",", ";", "\t", "|"]:
        if delimiter in sample:
            return delimiter
    return ","


def has_header(header: list[str]) -> bool:
    lowered = {cell.strip().lower() for cell in header}
    return any(lowered & aliases for aliases in HEADER_ALIASES.values())


def map_headers(header: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, cell in enumerate(header):
        value = cell.strip().lower()
        for key, aliases in HEADER_ALIASES.items():
            if value in aliases:
                mapping[key] = idx
    return mapping


def parse_row(row: list[str], mapping: dict[str, int], decimal_comma: bool) -> PointRecord | None:
    try:
        n = normalize_text(row[mapping.get("n", 0)])
        x = parse_float(row[mapping.get("x", 1)], decimal_comma)
        y = parse_float(row[mapping.get("y", 2)], decimal_comma)
        z_idx = mapping.get("z")
        z = parse_float(row[z_idx], decimal_comma) if z_idx is not None and z_idx < len(row) else None
        desc_idx = mapping.get("desc")
        desc = normalize_text(row[desc_idx]) if desc_idx is not None and desc_idx < len(row) else ""
        return PointRecord(n=n, x=x, y=y, z=z, desc=desc)
    except (IndexError, ValueError):
        return None


def iter_rows(lines: Iterable[str], delimiter: str) -> Iterable[list[str]]:
    reader = csv.reader(lines, delimiter=delimiter)
    yield from reader
