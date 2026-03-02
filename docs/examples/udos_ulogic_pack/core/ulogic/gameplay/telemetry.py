from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import json, datetime

@dataclass
class Telemetry:
    project_root: Path

    @property
    def log_path(self) -> Path:
        return self.project_root / "memory" / "ulogic" / "events.jsonl"

    def emit(self, event: str, data: Dict[str, Any] | None = None) -> None:
        p = self.log_path
        p.parent.mkdir(parents=True, exist_ok=True)
        obj = {"event": event, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "data": data or {}}
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
