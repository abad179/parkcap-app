from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path


CONFIG_PATH = Path.home() / ".ts2cad_config.json"


@dataclass
class ExportFormatConfig:
    template: str = "NXY"
    custom_pattern: str = "{n} {x} {y}"
    separator: str = " "
    include_header: bool = False
    decimals: int = 3
    decimal_comma: bool = False


@dataclass
class AppConfig:
    decimal_comma: bool = False
    input_separator: str | None = None
    renumber: bool = False
    renumber_start: int = 1
    units_to_meters: bool = True
    layer_by_code: bool = True
    export_format: ExportFormatConfig = field(default_factory=ExportFormatConfig)
    code_dictionary_path: str | None = None


DEFAULT_CONFIG = AppConfig()


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    export_cfg = ExportFormatConfig(**data.get("export_format", {}))
    return AppConfig(
        decimal_comma=data.get("decimal_comma", False),
        input_separator=data.get("input_separator"),
        renumber=data.get("renumber", False),
        renumber_start=data.get("renumber_start", 1),
        units_to_meters=data.get("units_to_meters", True),
        layer_by_code=data.get("layer_by_code", True),
        export_format=export_cfg,
        code_dictionary_path=data.get("code_dictionary_path"),
    )


def save_config(config: AppConfig) -> None:
    payload = asdict(config)
    with CONFIG_PATH.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
