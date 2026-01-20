from pathlib import Path

from ts2cad.core.config import ExportFormatConfig
from ts2cad.core.models import PointRecord
from ts2cad.exporters.txt import export_txt


def test_export_nxy(tmp_path: Path) -> None:
    records = [PointRecord(n="1", x=10.0, y=20.0, z=None, desc="")]
    destination = tmp_path / "out.txt"
    config = ExportFormatConfig(template="NXY", separator=",", decimals=2)

    export_txt(records, destination, config)

    assert destination.read_text(encoding="utf-8").strip() == "1,10.00,20.00"
