from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Any

from core.services.maintenance_utils import clean, get_compost_root, tidy
from core.services.time_utils import utc_compact_timestamp, utc_day_string


def _now_stamp() -> str:
    return utc_compact_timestamp()


@dataclass(frozen=True)
class KnowledgeArtifactRecord:
    action: str
    note_id: str
    path: Path
    title: str
    frontmatter: dict[str, Any]
    body: str


class KnowledgeArtifactService:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.knowledge_root = repo_root / "memory" / "bank" / "knowledge" / "user"
        self.workflow_root = repo_root / "memory" / "vault" / "workflows"
        self.binder_root = repo_root / "memory" / "vault" / "@binders"

    def save(self, *, action: str, note_id: str, content: str) -> Path:
        target = self._action_root(action) / f"{note_id}.md"
        if target.exists():
            self._archive_existing_version(target, scope=f"knowledge/{action}")
        target.write_text(content, encoding="utf-8")
        return target

    def list(self, action: str) -> list[str]:
        root = self._action_root(action)
        return sorted(path.name for path in root.glob("*.md"))

    def read(self, action: str, note_name: str) -> KnowledgeArtifactRecord:
        normalized = note_name[:-3] if note_name.lower().endswith(".md") else note_name
        path = self._action_root(action) / f"{normalized}.md"
        if not path.exists():
            raise FileNotFoundError(f"{action.title()} artifact not found: {normalized}")
        content = path.read_text(encoding="utf-8")
        frontmatter, body = self._split_frontmatter(content)
        title = self._extract_title(body, fallback=normalized)
        return KnowledgeArtifactRecord(
            action=action,
            note_id=normalized,
            path=path,
            title=title,
            frontmatter=frontmatter,
            body=body,
        )

    def import_into_workflow(
        self,
        *,
        workflow_id: str,
        action: str,
        note_name: str,
    ) -> dict[str, str]:
        record = self.read(action, note_name)
        workflow_dir = self.workflow_root / workflow_id
        if not workflow_dir.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_id}")

        destination = (
            workflow_dir
            / "inputs"
            / "knowledge"
            / action
            / f"{record.note_id}.md"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            self._archive_existing_version(
                destination,
                scope=f"workflow/{workflow_id}/knowledge/{action}",
            )
        shutil.copy2(record.path, destination)
        processed_path = self._archive_processed_snapshot(
            source_path=record.path,
            scope=f"workflow/{workflow_id}/{action}",
        )
        return {
            "workflow_id": workflow_id,
            "action": action,
            "note_id": record.note_id,
            "title": record.title,
            "source_path": str(record.path),
            "target_path": str(destination),
            "processed_snapshot": str(processed_path),
        }

    def import_into_binder(
        self,
        *,
        mission_id: str,
        action: str,
        note_name: str,
    ) -> dict[str, str]:
        record = self.read(action, note_name)
        mission_dir = self.binder_root / mission_id
        if not mission_dir.exists():
            raise FileNotFoundError(f"Mission not found: {mission_id}")

        destination = (
            mission_dir
            / "research"
            / action
            / f"{record.note_id}.md"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            self._archive_existing_version(
                destination,
                scope=f"binder/{mission_id}/research/{action}",
            )
        shutil.copy2(record.path, destination)
        processed_path = self._archive_processed_snapshot(
            source_path=record.path,
            scope=f"binder/{mission_id}/{action}",
        )
        return {
            "mission_id": mission_id,
            "action": action,
            "note_id": record.note_id,
            "title": record.title,
            "source_path": str(record.path),
            "target_path": str(destination),
            "processed_snapshot": str(processed_path),
        }

    def tidy_action(self, action: str | None = None) -> tuple[int, Path]:
        target = self._action_root(action) if action else self.knowledge_root
        return tidy(target, recursive=True)

    def clean_action(self, action: str | None = None) -> tuple[int, Path]:
        target = self._action_root(action) if action else self.knowledge_root
        return clean(target, allowed_entries=[], recursive=True)

    def _action_root(self, action: str | None) -> Path:
        if action:
            root = self.knowledge_root / action
        else:
            root = self.knowledge_root
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _archive_existing_version(self, path: Path, *, scope: str) -> Path:
        archive_dir = get_compost_root() / utc_day_string() / "backups" / scope
        archive_dir.mkdir(parents=True, exist_ok=True)
        archived = archive_dir / f"{_now_stamp()}-{path.name}"
        shutil.copy2(path, archived)
        return archived

    def _archive_processed_snapshot(self, *, source_path: Path, scope: str) -> Path:
        archive_dir = get_compost_root() / utc_day_string() / "archive" / "processed" / scope
        archive_dir.mkdir(parents=True, exist_ok=True)
        archived = archive_dir / f"{_now_stamp()}-{source_path.name}"
        shutil.copy2(source_path, archived)
        return archived

    def _split_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        lines = content.splitlines()
        if len(lines) < 3 or lines[0].strip() != "---":
            return {}, content
        frontmatter_lines: list[str] = []
        body_start = 0
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start = index + 1
                break
            frontmatter_lines.append(line)
        else:
            return {}, content
        frontmatter = self._parse_frontmatter(frontmatter_lines)
        body = "\n".join(lines[body_start:]).lstrip()
        return frontmatter, body

    def _parse_frontmatter(self, lines: list[str]) -> dict[str, Any]:
        frontmatter: dict[str, Any] = {}
        current_key = ""
        current_list: list[str] | None = None
        for raw in lines:
            line = raw.rstrip()
            if line.startswith("  - ") and current_key and current_list is not None:
                current_list.append(line[4:].strip().strip('"'))
                continue
            current_key = ""
            current_list = None
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not value:
                frontmatter[key] = []
                current_key = key
                current_list = frontmatter[key]
                continue
            if value.startswith('"') and value.endswith('"'):
                frontmatter[key] = value[1:-1]
            elif value in {"true", "false"}:
                frontmatter[key] = value == "true"
            else:
                frontmatter[key] = value
        return frontmatter

    def _extract_title(self, body: str, *, fallback: str) -> str:
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip() or fallback
        return fallback


def get_knowledge_artifact_service(repo_root: Path) -> KnowledgeArtifactService:
    return KnowledgeArtifactService(repo_root)
