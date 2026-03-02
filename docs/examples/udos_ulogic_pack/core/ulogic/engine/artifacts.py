from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import json

@dataclass
class ArtifactStore:
    vault_root: Path

    def workflow_dir(self, workflow_id: str) -> Path:
        return self.vault_root / "workflows" / workflow_id

    def write_text(self, workflow_id: str, relpath: str, text: str) -> Path:
        p = self.workflow_dir(workflow_id) / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def write_json(self, workflow_id: str, relpath: str, obj: Dict[str, Any]) -> Path:
        p = self.workflow_dir(workflow_id) / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
        return p
