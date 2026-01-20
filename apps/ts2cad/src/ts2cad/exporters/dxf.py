from __future__ import annotations

from pathlib import Path

import ezdxf

from ts2cad.core.models import PointRecord


def export_dxf(
    records: list[PointRecord],
    destination: Path,
    layer_map: dict[str, str] | None = None,
) -> None:
    doc = ezdxf.new()
    msp = doc.modelspace()
    layer_map = layer_map or {}

    for record in records:
        layer_name = layer_map.get(record.desc, record.desc or "DEFAULT")
        if layer_name not in doc.layers:
            doc.layers.new(name=layer_name)
        z = record.z if record.z is not None else 0.0
        msp.add_point((record.x, record.y, z), dxfattribs={"layer": layer_name})

    doc.saveas(destination)
