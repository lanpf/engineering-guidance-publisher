from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectLayout:
    root: Path

    @property
    def catalog(self) -> Path:
        return self.root / "catalog.json"

    @property
    def blueprints(self) -> Path:
        return self.root / "blueprints" / "skills"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or project_root() / "catalog.json"
    with catalog_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("catalog root must be an object")
    return data

