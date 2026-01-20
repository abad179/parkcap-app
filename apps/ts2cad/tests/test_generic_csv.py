from pathlib import Path

from ts2cad.importers.generic import GenericImporter


def test_generic_csv(tmp_path: Path) -> None:
    data = "ID,E,N,Z,Desc\n1,500.0,1000.0,10.5,BM\n"
    file_path = tmp_path / "points.csv"
    file_path.write_text(data, encoding="utf-8")

    importer = GenericImporter()
    result = importer.parse(file_path)

    assert len(result.records) == 1
    record = result.records[0]
    assert record.n == "1"
    assert record.x == 500.0
    assert record.y == 1000.0
    assert record.z == 10.5
    assert record.desc == "BM"
