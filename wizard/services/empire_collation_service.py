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
    _DUE_PATTERN = re.compile(
        r"\b(?:by|before|due|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{4}-\d{2}-\d{2})\b",
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        self.empire = get_empire_extension_service()
        self.scope_service = get_empire_scope_service()
        self.vault_dir = get_vault_dir()

    def _storage(self):
        return self.empire._import_module("empire.services.storage")

    def _resolve_db_path(self, scope: str = "master", binder_id: str | None = None) -> Path:
        resolved = self.scope_service.resolve(scope=scope, binder_id=binder_id)
        return Path(resolved["db_path"])

    def _utc_now(self) -> str:
        ingestion = self.empire._import_module("empire.services.ingestion_service")
        return ingestion._utc_now()

    def _extract_tasks(self, text: str, title: str, classification: str | None = None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for line in text.splitlines():
            for pattern in self._TASK_PATTERNS:
                match = pattern.match(line)
                if match:
                    item = match.group("text").strip()
                    if item and all(existing["title"] != item for existing in results):
                        due_match = self._DUE_PATTERN.search(item)
                        task_type = "follow_up"
                        if classification == "meeting_note":
                            task_type = "meeting_follow_up"
                        elif classification == "finance_doc":
                            task_type = "finance_follow_up"
                        elif classification == "task_doc":
                            task_type = "action_item"
                        results.append(
                            {
                                "title": item,
                                "task_type": task_type,
                                "due_hint": due_match.group(0) if due_match else None,
                                "review_status": "ready" if due_match else "pending_review",
                                "confidence": 0.82 if due_match else 0.68,
                            }
                        )
        if not results:
            fallback = title.strip() or "Review imported document"
            results.append(
                {
                    "title": f"Review document: {fallback}",
                    "task_type": "document_review",
                    "due_hint": None,
                    "review_status": "pending_review",
                    "confidence": 0.45,
                }
            )
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
        tasks: list[dict[str, Any]],
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
        artifact_lines.extend(
            f"- [ ] {item['title']}" + (f" ({item['due_hint']})" if item.get("due_hint") else "")
            for item in tasks
        )
        artifact_lines.append("")
        artifact_path.write_text("\n".join(artifact_lines) + "\n", encoding="utf-8")
        return str(artifact_path)

    def _write_workflow_stub(
        self,
        *,
        document_id: str,
        title: str,
        source_path: str,
        tasks: list[dict[str, Any]],
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
                *[
                    f"- [ ] {task['title']}" + (f" ({task['due_hint']})" if task.get("due_hint") else "")
                    for task in tasks
                ],
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

    def collate_document(
        self,
        document_id: str,
        emit_mode: str = "task_note",
        *,
        scope: str = "master",
        binder_id: str | None = None,
    ) -> dict[str, Any]:
        storage = self._storage()
        db_path = self._resolve_db_path(scope=scope, binder_id=binder_id)
        document = storage.get_document(document_id, db_path=db_path)
        if not document:
            raise ValueError(f"Unknown document: {document_id}")
        if emit_mode not in {"task_only", "task_note", "workflow_stub"}:
            raise ValueError("emit_mode must be task_only, task_note, or workflow_stub")

        extracted_text = str(document.get("extracted_text") or "")
        title = str(document.get("title") or document.get("source_path") or document_id)
        tasks = self._extract_tasks(extracted_text, title, str(document.get("classification") or "document"))
        created_task_ids: list[str] = []
        for task in tasks:
            task_id = storage.record_task(
                title=task["title"],
                category="document",
                task_type=task.get("task_type"),
                source=f"document:{document_id}",
                source_ref=document_id,
                created_at=self._utc_now(),
                due_hint=task.get("due_hint"),
                status="open",
                review_status=task.get("review_status", "pending_review"),
                notes=f"Collated from {document.get('source_path')}",
                metadata={
                    "document_id": document_id,
                    "confidence": task.get("confidence"),
                    "classification": document.get("classification"),
                },
                dedupe_by_source=False,
                db_path=db_path,
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
            metadata=str({"artifact_path": artifact_path, "emit_mode": emit_mode, "tasks": tasks}),
            db_path=db_path,
        )
        return {
            "document_id": document_id,
            "task_count": len(tasks),
            "task_ids": created_task_ids,
            "tasks": tasks,
            "artifact_path": artifact_path,
            "emit_mode": emit_mode,
        }


_service: EmpireCollationService | None = None


def get_empire_collation_service() -> EmpireCollationService:
    global _service
    if _service is None:
        _service = EmpireCollationService()
    return _service
