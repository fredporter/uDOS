from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import json, datetime

@dataclass
class DeferredQueue:
    project_root: Path

    @property
    def queue_path(self) -> Path:
        return self.project_root / "memory" / "ulogic" / "deferred.jsonl"

    def enqueue(self, item: Dict[str, Any]) -> None:
        p = self.queue_path
        p.parent.mkdir(parents=True, exist_ok=True)
        obj = dict(item)
        obj.setdefault("queued_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    def list_items(self, limit: int = 50) -> List[Dict[str, Any]]:
        p = self.queue_path
        if not p.exists():
            return []
        out: List[Dict[str, Any]] = []
        for line in p.read_text(encoding="utf-8").splitlines()[:limit]:
            if line.strip():
                out.append(json.loads(line))
        return out
