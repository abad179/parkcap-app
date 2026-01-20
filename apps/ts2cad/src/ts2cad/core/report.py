from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ts2cad.core.models import PointRecord


@dataclass
class ConversionReport:
    total_records: int
    valid_records: int
    rejected_records: int
    duplicate_ids: int
    duplicate_coords: int
    min_x: float | None
    max_x: float | None
    min_y: float | None
    max_y: float | None
    codes: dict[str, int]
    created_layers: list[str]
    started_at: datetime
    finished_at: datetime

    def to_text(self) -> str:
        lines = [
            "Resumen de conversión",
            f"Inicio: {self.started_at.isoformat(sep=' ', timespec='seconds')}",
            f"Fin: {self.finished_at.isoformat(sep=' ', timespec='seconds')}",
            f"Total registros: {self.total_records}",
            f"Válidos: {self.valid_records}",
            f"Descartados: {self.rejected_records}",
            f"Duplicados por ID: {self.duplicate_ids}",
            f"Duplicados por coordenada: {self.duplicate_coords}",
        ]
        if self.min_x is not None:
            lines.append(f"Rango X: {self.min_x:.3f} - {self.max_x:.3f}")
        if self.min_y is not None:
            lines.append(f"Rango Y: {self.min_y:.3f} - {self.max_y:.3f}")
        lines.append("Códigos encontrados:")
        for code, count in sorted(self.codes.items()):
            lines.append(f"  {code}: {count}")
        if self.created_layers:
            lines.append("Capas creadas:")
            lines.extend([f"  {layer}" for layer in self.created_layers])
        return "\n".join(lines)


def summarize_records(records: list[PointRecord]) -> dict[str, int]:
    codes: dict[str, int] = {}
    for record in records:
        code = record.desc.strip() or "(sin código)"
        codes[code] = codes.get(code, 0) + 1
    return codes
