from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
import json

from .contracts import WorkflowRuntimeState, WorkflowSpec


class WorkflowArtifactStore:
    def __init__(self, vault_root: Path):
        self.vault_root = vault_root

    def workflow_dir(self, workflow_id: str) -> Path:
        return self.vault_root / "workflows" / workflow_id

    def ensure_workflow_dir(self, workflow_id: str) -> Path:
        path = self.workflow_dir(workflow_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_text(self, workflow_id: str, relpath: str, text: str) -> Path:
        path = self.workflow_dir(workflow_id) / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def read_text(self, workflow_id: str, relpath: str) -> str:
        return (self.workflow_dir(workflow_id) / relpath).read_text(encoding="utf-8")

    def write_json(self, workflow_id: str, relpath: str, obj: dict[str, Any]) -> Path:
        path = self.workflow_dir(workflow_id) / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
        return path

    def read_json(self, workflow_id: str, relpath: str) -> dict[str, Any]:
        return json.loads((self.workflow_dir(workflow_id) / relpath).read_text(encoding="utf-8"))

    def write_spec(self, spec: WorkflowSpec, raw_markdown: str) -> None:
        self.write_text(spec.workflow_id, "workflow.md", raw_markdown)
        self.write_json(spec.workflow_id, "workflow.json", asdict(spec))

    def write_state(self, state: WorkflowRuntimeState) -> None:
        self.write_json(state.workflow_id, "state.json", asdict(state))

    def list_workflows(self) -> list[str]:
        if not self.vault_root.exists():
            return []
        root = self.vault_root / "workflows"
        if not root.exists():
            return []
        return sorted(path.name for path in root.iterdir() if path.is_dir())
