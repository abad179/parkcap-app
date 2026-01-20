from pathlib import Path

from ts2cad.core.config import ExportFormatConfig
from ts2cad.core.models import PointRecord
from ts2cad.exporters.txt import export_txt


def test_export_pnezd(tmp_path: Path) -> None:
    records = [PointRecord(n="101", x=100.0, y=200.0, z=5.5, desc="BM")]
    destination = tmp_path / "out.txt"
    config = ExportFormatConfig(template="PNEZD", separator=" ", decimals=1)

    export_txt(records, destination, config)

    assert destination.read_text(encoding="utf-8").strip() == "101 200.0 100.0 5.5 BM"
