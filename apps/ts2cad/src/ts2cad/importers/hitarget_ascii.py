from __future__ import annotations

from pathlib import Path

from ts2cad.core.models import ImportResult
from ts2cad.importers.base import Importer


class HiTargetASCIIImporter(Importer):
    name = "Hi-Target ASCII (best-effort)"

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in {".txt", ".asc"}

    def parse(self, path: Path) -> ImportResult:
        warnings = ["Importador Hi-Target aún básico: use el importador genérico si faltan datos."]
        return ImportResult(records=[], rejected=[], warnings=warnings)
