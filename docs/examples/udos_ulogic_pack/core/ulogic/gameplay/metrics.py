from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
import json

@dataclass
class MetricsStore:
    project_root: Path
    _cache: Dict[str, Any] = field(default_factory=dict)

    @property
    def metrics_path(self) -> Path:
        return self.project_root / "memory" / "ulogic" / "metrics.json"

    def load(self) -> Dict[str, Any]:
        p = self.metrics_path
        if p.exists():
            self._cache = json.loads(p.read_text(encoding="utf-8"))
        else:
            self._cache = {"xp": 0, "trust": 0, "streak": 0, "entropy": 0, "unlocks": []}
        return self._cache

    def save(self) -> None:
        p = self.metrics_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self._cache, indent=2, ensure_ascii=False), encoding="utf-8")

    def snapshot(self) -> Dict[str, Any]:
        if not self._cache:
            self.load()
        return dict(self._cache)

    def add_xp(self, amount: int) -> None:
        self.load()
        self._cache["xp"] = int(self._cache.get("xp", 0)) + int(amount)
        self.save()

    def set_metric(self, key: str, value: Any) -> None:
        self.load()
        self._cache[key] = value
        self.save()
