from pathlib import Path

from ts2cad.core.models import PointRecord
from ts2cad.exporters.scr import export_scr


def test_export_scr(tmp_path: Path) -> None:
    records = [PointRecord(n="1", x=10.0, y=20.0, z=0.0, desc="BM")]
    destination = tmp_path / "out.scr"

    export_scr(records, destination)

    content = destination.read_text(encoding="utf-8")
    assert "POINT 10.0,20.0,0.0" in content
    assert "TEXT 10.0,20.0,0.0" in content
