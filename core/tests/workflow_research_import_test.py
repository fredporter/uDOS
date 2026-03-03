from __future__ import annotations

from pathlib import Path

from core.commands.workflow_handler import WorkflowHandler
from core.workflows.scheduler import WorkflowScheduler


def test_workflow_import_research_copies_persisted_artifact(tmp_path: Path) -> None:
    scheduler = WorkflowScheduler(tmp_path)
    scheduler.knowledge_artifacts.knowledge_root = tmp_path / "memory" / "bank" / "knowledge" / "user"
    scheduler.knowledge_artifacts.workflow_root = tmp_path / "memory" / "vault" / "workflows"

    note_root = scheduler.knowledge_artifacts.knowledge_root / "research"
    note_root.mkdir(parents=True, exist_ok=True)
    note_path = note_root / "note-001.md"
    note_path.write_text(
        "---\nudos_id: \"note-001\"\n---\n\n# Research Note\n\nCaptured details.\n",
        encoding="utf-8",
    )

    scheduler.create_workflow_from_markdown(
        "wf-research-import",
        """# WORKFLOW: research-import

## Goal
Use imported research

## Phases
1. Outline (writing/outline -> 01-outline.md)
""",
        project="research-ops",
    )

    handler = WorkflowHandler()
    handler.scheduler = scheduler

    result = handler.handle(
        "WORKFLOW",
        ["IMPORT", "RESEARCH", "wf-research-import", "note-001"],
    )

    assert result["status"] == "success"
    imported_path = tmp_path / "memory" / "vault" / "workflows" / "wf-research-import" / "inputs" / "knowledge" / "research" / "note-001.md"
    assert imported_path.exists()
    meta_path = tmp_path / "memory" / "vault" / "workflows" / "wf-research-import" / "meta" / "research-imports.json"
    assert meta_path.exists()
    assert "Processed snapshot:" in result["output"]
