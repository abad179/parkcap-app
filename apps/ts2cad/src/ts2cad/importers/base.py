from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ts2cad.core.models import ImportResult


class Importer(ABC):
    name: str

    @abstractmethod
    def can_handle(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def parse(self, path: Path) -> ImportResult:
        raise NotImplementedError
