from __future__ import annotations

from pathlib import Path

from ts2cad.core.report import ConversionReport


def export_report(report: ConversionReport, destination: Path) -> None:
    destination.write_text(report.to_text(), encoding="utf-8")
