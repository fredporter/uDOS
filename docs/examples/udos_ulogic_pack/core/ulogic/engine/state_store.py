from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import json, datetime

def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

@dataclass
class UdosStateStore:
    root: Path

    @property
    def project_json(self) -> Path: return self.root / "project.json"
    @property
    def agents_md(self) -> Path: return self.root / "agents.md"
    @property
    def tasks_json(self) -> Path: return self.root / "tasks.json"
    @property
    def completed_json(self) -> Path: return self.root / "completed.json"

    def load_project(self) -> Dict[str, Any]:
        return _read_json(self.project_json, {"name": "", "constraints": {}})

    def load_tasks(self) -> Dict[str, Any]:
        return _read_json(self.tasks_json, {"tasks": []})

    def load_completed(self) -> Dict[str, Any]:
        return _read_json(self.completed_json, {"completed": []})

    def save_completed(self, data: Dict[str, Any]) -> None:
        _write_json(self.completed_json, data)

    def append_completed(self, entry: Dict[str, Any]) -> None:
        data = self.load_completed()
        data.setdefault("completed", []).append(entry)
        self.save_completed(data)

    def now_iso(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
