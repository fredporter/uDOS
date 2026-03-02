from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from wizard.services.path_utils import get_repo_root, get_vault_dir

_TASK_LINE_RE = re.compile(r"^\s*[-*]\s+\[(?P<done>[ xX])\]\s+(?P<title>.+)$")
_META_RE = re.compile(r"^\s*[-*]\s+(?P<key>schedule|priority|need|mission|objective|provider|window|kind|requires_network)\s*:\s*(?P<value>.+)$", re.IGNORECASE)
_WORKFLOW_PHASE_RE = re.compile(
    r"^\s*(?P<index>\d+)\.\s+(?P<title>.+?)\s+\((?P<adapter>[^/]+)/(?P<prompt>[^ ]+)\s+->\s+(?P<output>[^)]+)\)\s*$"
)


class MarkdownJobService:
    def __init__(self, repo_root: Path | None = None, vault_root: Path | None = None):
        self.repo_root = repo_root or get_repo_root()
        self.vault_root = vault_root or get_vault_dir()

    def resolve_source(self, source_path: str) -> Path:
        candidate = Path(source_path).expanduser()
        if candidate.is_absolute():
            return candidate
        vault_candidate = self.vault_root / candidate
        if vault_candidate.exists():
            return vault_candidate
        repo_candidate = self.repo_root / candidate
        if repo_candidate.exists():
            return repo_candidate
        raise FileNotFoundError(source_path)

    def import_source(self, source_path: str) -> list[dict[str, Any]]:
        path = self.resolve_source(source_path)
        text = path.read_text(encoding="utf-8")
        lowered = path.name.lower()
        if "workflow" in lowered or "# workflow:" in text.lower():
            return self._workflow_jobs(path, text)
        return self._task_jobs(path, text)

    def _task_jobs(self, path: Path, text: str) -> list[dict[str, Any]]:
        jobs: list[dict[str, Any]] = []
        metadata: dict[str, Any] = {
            "schedule": "daily",
            "priority": 5,
            "need": 5,
            "resource_cost": 1,
            "requires_network": False,
            "kind": "markdown_task",
        }
        for line in text.splitlines():
            meta = _META_RE.match(line)
            if meta:
                key = meta.group("key").strip().lower()
                value = meta.group("value").strip()
                if key in {"priority", "need"}:
                    metadata[key] = int(value)
                elif key == "requires_network":
                    metadata[key] = value.lower() in {"1", "true", "yes", "on"}
                elif key == "kind":
                    metadata["kind"] = value
                else:
                    metadata[key] = value
                continue
            match = _TASK_LINE_RE.match(line)
            if not match or match.group("done").lower() == "x":
                continue
            title = match.group("title").strip()
            jobs.append(
                {
                    "name": title,
                    "description": f"Imported from {path.relative_to(self.repo_root)}",
                    "schedule": metadata.get("schedule", "daily"),
                    "provider": metadata.get("provider"),
                    "priority": metadata.get("priority", 5),
                    "need": metadata.get("need", 5),
                    "mission": metadata.get("mission"),
                    "objective": metadata.get("objective"),
                    "resource_cost": metadata.get("resource_cost", 1),
                    "requires_network": metadata.get("requires_network", False),
                    "kind": metadata.get("kind", "markdown_task"),
                    "payload": {
                        "source_path": str(path.relative_to(self.repo_root)),
                        "source_type": "markdown_task",
                        "window": metadata.get("window"),
                    },
                }
            )
        return jobs

    def _workflow_jobs(self, path: Path, text: str) -> list[dict[str, Any]]:
        jobs: list[dict[str, Any]] = []
        workflow_id = path.stem
        for line in text.splitlines():
            match = _WORKFLOW_PHASE_RE.match(line)
            if not match:
                continue
            title = match.group("title").strip()
            jobs.append(
                {
                    "name": f"{workflow_id}: {title}",
                    "description": f"Workflow phase imported from {path.relative_to(self.repo_root)}",
                    "schedule": "off_peak",
                    "provider": None,
                    "priority": 8,
                    "need": 7,
                    "mission": workflow_id,
                    "objective": title,
                    "resource_cost": 2,
                    "requires_network": False,
                    "kind": "workflow_phase",
                    "payload": {
                        "source_path": str(path.relative_to(self.repo_root)),
                        "source_type": "workflow",
                        "phase_index": int(match.group("index")),
                        "adapter": match.group("adapter").strip(),
                        "prompt_name": match.group("prompt").strip(),
                        "output": match.group("output").strip(),
                    },
                }
            )
        return jobs
