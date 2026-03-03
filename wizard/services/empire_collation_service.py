"""Collate imported Empire documents into tasks and scoped markdown artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.empire_scope_service import get_empire_scope_service
from wizard.services.path_utils import get_vault_dir


class EmpireCollationService:
    """Generate Empire tasks and markdown artifacts from imported documents."""

    _TASK_PATTERNS = (
        re.compile(r"^\s*[-*]\s+\[\s\]\s+(?P<text>.+?)\s*$"),
        re.compile(r"^\s*(?:TODO|Action|Next)\s*:\s*(?P<text>.+?)\s*$", re.IGNORECASE),
    )

    def __init__(self) -> None:
        self.empire = get_empire_extension_service()
        self.scope_service = get_empire_scope_service()
        self.vault_dir = get_vault_dir()

    def _storage(self):
        return self.empire._import_module("empire.services.storage")

    def _utc_now(self) -> str:
        ingestion = self.empire._import_module("empire.services.ingestion_service")
        return ingestion._utc_now()

    def _extract_tasks(self, text: str, title: str) -> list[str]:
        results: list[str] = []
        for line in text.splitlines():
            for pattern in self._TASK_PATTERNS:
                match = pattern.match(line)
                if match:
                    item = match.group("text").strip()
                    if item and item not in results:
                        results.append(item)
        if not results:
            fallback = title.strip() or "Review imported document"
            results.append(f"Review document: {fallback}")
        return results

    def _artifact_path(self, scope: str, binder_id: str | None, document_id: str) -> Path:
        resolved = self.scope_service.resolve(scope=scope, binder_id=binder_id)
        base = Path(resolved["vault_path"]) / "empire" / "tasks"
        base.mkdir(parents=True, exist_ok=True)
        return base / f"{document_id}.md"

    def _workflow_stub_path(self, document_id: str) -> Path:
        base = self.vault_dir / "workflows" / f"empire-{document_id}"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def _write_note_artifact(
        self,
        *,
        document_id: str,
        title: str,
        source_path: str,
        scope: str,
        binder_id: str | None,
        tasks: list[str],
    ) -> str:
        artifact_path = self._artifact_path(scope, binder_id, document_id)
        artifact_lines = [
            f"# Empire Tasks: {title}",
            "",
            f"Source: {source_path}",
            f"Document ID: {document_id}",
            "",
            "## Tasks",
        ]
        artifact_lines.extend(f"- [ ] {item}" for item in tasks)
        artifact_lines.append("")
        artifact_path.write_text("\n".join(artifact_lines) + "\n", encoding="utf-8")
        return str(artifact_path)

    def _write_workflow_stub(
        self,
        *,
        document_id: str,
        title: str,
        source_path: str,
        tasks: list[str],
    ) -> str:
        workflow_root = self._workflow_stub_path(document_id)
        workflow_md = "\n".join(
            [
                f"# WORKFLOW: empire-{document_id}",
                "",
                "## Goal",
                f"Review imported document and complete follow-up tasks for {title}.",
                "",
                "## Constraints",
                f"- Source: {source_path}",
                "- Origin: Empire collation",
                "",
                "## Phases",
                f"1. Review imported tasks (local/review -> 01-review.md)",
                f"2. Complete follow-up summary (local/summary -> 02-summary.md)",
                "",
                "## Outputs",
                "- 01-review.md",
                "- 02-summary.md",
                "",
                "## Derived Tasks",
                *[f"- [ ] {task}" for task in tasks],
                "",
            ]
        )
        (workflow_root / "workflow.md").write_text(workflow_md, encoding="utf-8")
        (workflow_root / "workflow.json").write_text(
            json.dumps(
                {
                    "workflow_id": f"empire-{document_id}",
                    "template_id": "empire-collation",
                    "goal": f"Review imported document {title}",
                    "source_path": source_path,
                    "tasks": tasks,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (workflow_root / "state.json").write_text(
            json.dumps(
                {
                    "workflow_id": f"empire-{document_id}",
                    "status": "ready",
                    "current_phase_index": 0,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return str(workflow_root / "workflow.md")

    def collate_document(self, document_id: str, emit_mode: str = "task_note") -> dict[str, Any]:
        storage = self._storage()
        document = storage.get_document(document_id, db_path=self.empire.db_path)
        if not document:
            raise ValueError(f"Unknown document: {document_id}")
        if emit_mode not in {"task_only", "task_note", "workflow_stub"}:
            raise ValueError("emit_mode must be task_only, task_note, or workflow_stub")

        extracted_text = str(document.get("extracted_text") or "")
        title = str(document.get("title") or document.get("source_path") or document_id)
        tasks = self._extract_tasks(extracted_text, title)
        created_task_ids: list[str] = []
        for task_title in tasks:
            task_id = storage.record_task(
                title=task_title,
                category="document",
                source=f"document:{document_id}",
                source_ref=document_id,
                created_at=self._utc_now(),
                status="open",
                notes=f"Collated from {document.get('source_path')}",
                dedupe_by_source=False,
                db_path=self.empire.db_path,
            )
            created_task_ids.append(task_id)

        artifact_path = None
        if emit_mode == "task_note":
            artifact_path = self._write_note_artifact(
                document_id=document_id,
                title=title,
                source_path=str(document.get("source_path")),
                scope=str(document.get("scope") or "master"),
                binder_id=document.get("binder_id"),
                tasks=tasks,
            )
        elif emit_mode == "workflow_stub":
            artifact_path = self._write_workflow_stub(
                document_id=document_id,
                title=title,
                source_path=str(document.get("source_path")),
                tasks=tasks,
            )

        storage.record_event(
            record_id=None,
            event_type="document.collate",
            occurred_at=self._utc_now(),
            subject=f"Collated {len(tasks)} tasks from document",
            notes=document_id,
            metadata=str({"artifact_path": artifact_path, "emit_mode": emit_mode}),
            db_path=self.empire.db_path,
        )
        return {
            "document_id": document_id,
            "task_count": len(tasks),
            "task_ids": created_task_ids,
            "artifact_path": artifact_path,
            "emit_mode": emit_mode,
        }


_service: EmpireCollationService | None = None


def get_empire_collation_service() -> EmpireCollationService:
    global _service
    if _service is None:
        _service = EmpireCollationService()
    return _service
