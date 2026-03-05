"""Artifact helpers for deterministic offline runtime output."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ArtifactStore:
    vault_root: Path

    def workflow_dir(self, workflow_id: str) -> Path:
        return self.vault_root / "workflows" / workflow_id

    def write_text(self, workflow_id: str, relpath: str, text: str) -> Path:
        path = self.workflow_dir(workflow_id) / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_json(self, workflow_id: str, relpath: str, obj: dict[str, Any]) -> Path:
        path = self.workflow_dir(workflow_id) / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
        return path
