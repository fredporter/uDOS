"""File-backed state helpers for deterministic offline runtime flows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


@dataclass
class ULogicStateStore:
    root: Path

    @property
    def project_json(self) -> Path:
        return self.root / "project.json"

    @property
    def tasks_json(self) -> Path:
        return self.root / "tasks.json"

    @property
    def completed_json(self) -> Path:
        return self.root / "completed.json"

    def load_project(self) -> dict[str, Any]:
        return _read_json(self.project_json, {"name": "", "constraints": {}})

    def load_tasks(self) -> dict[str, Any]:
        return _read_json(self.tasks_json, {"tasks": []})

    def load_completed(self) -> dict[str, Any]:
        return _read_json(self.completed_json, {"completed": []})

    def save_completed(self, data: dict[str, Any]) -> None:
        _write_json(self.completed_json, data)

    def append_completed(self, entry: dict[str, Any]) -> None:
        data = self.load_completed()
        data.setdefault("completed", []).append(entry)
        self.save_completed(data)

    def now_iso(self) -> str:
        return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
