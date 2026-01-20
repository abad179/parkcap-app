from __future__ import annotations

import threading
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import Callable

from ts2cad.core.config import AppConfig
from ts2cad.core.models import ImportResult
from ts2cad.core.report import ConversionReport, summarize_records
from ts2cad.exporters.dxf import export_dxf
from ts2cad.exporters.report import export_report
from ts2cad.exporters.scr import export_scr
from ts2cad.exporters.txt import export_csv, export_txt
from ts2cad.importers.generic import GenericImporter
from ts2cad.normalizer.normalize import normalize_records


@dataclass
class ConversionRequest:
    files: list[Path]
    output_dir: Path
    base_name: str
    config: AppConfig
    export_flags: dict[str, bool]
    layer_map: dict[str, str]


def run_conversion(request: ConversionRequest, log: Callable[[str], None]) -> ConversionReport:
    started_at = datetime.now()
    log("Iniciando conversión...")
    importer = GenericImporter(
        decimal_comma=request.config.decimal_comma,
        separator=request.config.input_separator,
    )

    all_records = []
    rejected_total = []
    warnings = []
    for path in request.files:
        log(f"Importando {path.name}...")
        result: ImportResult = importer.parse(path)
        all_records.extend(result.records)
        rejected_total.extend(result.rejected)
        warnings.extend(result.warnings)

    if warnings:
        for warning in warnings:
            log(f"Advertencia: {warning}")

    normalized, duplicates = normalize_records(
        all_records,
        decimal_comma=request.config.decimal_comma,
        renumber=request.config.renumber,
        renumber_start=request.config.renumber_start,
        units_to_meters=request.config.units_to_meters,
    )

    codes = summarize_records(normalized)
    min_x = min((r.x for r in normalized), default=None)
    max_x = max((r.x for r in normalized), default=None)
    min_y = min((r.y for r in normalized), default=None)
    max_y = max((r.y for r in normalized), default=None)

    export_format = request.config.export_format

    if request.export_flags.get("txt"):
        log("Exportando TXT principal...")
        export_txt(normalized, request.output_dir / f"{request.base_name}.txt", export_format)
    if request.export_flags.get("pnezd"):
        log("Exportando TXT PNEZD...")
        pnezd_config = replace(export_format, template="PNEZD")
        export_txt(normalized, request.output_dir / f"{request.base_name}_PNEZD.txt", pnezd_config)
    if request.export_flags.get("penzd"):
        log("Exportando TXT PENZD...")
        penzd_config = replace(export_format, template="PENZD")
        export_txt(normalized, request.output_dir / f"{request.base_name}_PENZD.txt", penzd_config)
    if request.export_flags.get("csv"):
        log("Exportando CSV...")
        export_csv(normalized, request.output_dir / f"{request.base_name}.csv", export_format)
    if request.export_flags.get("scr"):
        log("Exportando SCR...")
        export_scr(normalized, request.output_dir / f"{request.base_name}.scr")
    if request.export_flags.get("dxf"):
        log("Exportando DXF...")
        export_dxf(normalized, request.output_dir / f"{request.base_name}.dxf", request.layer_map)

    finished_at = datetime.now()
    report = ConversionReport(
        total_records=len(all_records),
        valid_records=len(normalized),
        rejected_records=len(rejected_total),
        duplicate_ids=duplicates["id"],
        duplicate_coords=duplicates["coords"],
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
        codes=codes,
        created_layers=sorted(set(request.layer_map.values())) if request.layer_map else [],
        started_at=started_at,
        finished_at=finished_at,
    )

    if request.export_flags.get("report"):
        log("Exportando reporte...")
        export_report(report, request.output_dir / f"{request.base_name}_reporte.txt")

    log("Conversión finalizada.")
    return report


class ConversionWorker(threading.Thread):
    def __init__(self, request: ConversionRequest, log_queue: Queue[str], done_callback: Callable[[ConversionReport], None]):
        super().__init__(daemon=True)
        self.request = request
        self.log_queue = log_queue
        self.done_callback = done_callback

    def run(self) -> None:
        def logger(message: str) -> None:
            self.log_queue.put(message)

        report = run_conversion(self.request, logger)
        self.done_callback(report)
