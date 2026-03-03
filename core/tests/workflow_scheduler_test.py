from __future__ import annotations

import shutil
from pathlib import Path

from core.workflows.parser import WorkflowTemplateParser
from core.workflows.scheduler import WorkflowScheduler
from core.services.path_service import get_repo_root


def _cleanup(workflow_id: str) -> None:
    path = Path(get_repo_root()) / "memory" / "vault" / "workflows" / workflow_id
    if path.exists():
        shutil.rmtree(path)


def test_workflow_template_parser_extracts_phases_and_outputs() -> None:
    markdown = """# WORKFLOW: writing-article-v1

## Project
release-ops

## Goal
Write a release note

## Constraints
- Audience: operators
- Tone: plain

## Phases
1. Outline (writing/outline -> 01-outline.md)
2. Draft (writing/draft -> 02-draft.md)

## Outputs
- 01-outline.md
- 02-draft.md
"""
    spec = WorkflowTemplateParser().parse("wf-test", markdown)

    assert spec.template_id == "writing-article-v1"
    assert spec.project == "release-ops"
    assert spec.goal == "Write a release note"
    assert spec.constraints["audience"] == "operators"
    assert [phase.name for phase in spec.phases] == ["outline", "draft"]
    assert spec.outputs == ["01-outline.md", "02-draft.md"]


def test_workflow_template_parser_understands_shared_sections() -> None:
    markdown = """# WORKFLOW: shared-shape-v1

## Purpose
Run a shared-shape workflow

## Inputs
- Project: release-ops
- Audience: operators

## Goal
Write a release note

## Constraints
- Tone: plain

## Steps
1. Draft the workflow outputs.

## Phases
1. Outline (writing/outline -> 01-outline.md)

## Outputs
- 01-outline.md

## Evidence
- Outline generated

## Notes
- Shared-shape test
"""
    spec = WorkflowTemplateParser().parse("wf-shared", markdown)

    assert spec.purpose == "Run a shared-shape workflow"
    assert spec.inputs["project"] == "release-ops"
    assert spec.inputs["audience"] == "operators"
    assert spec.project == "release-ops"
    assert spec.goal == "Write a release note"
    assert spec.constraints["tone"] == "plain"


def test_workflow_scheduler_create_run_approve_cycle() -> None:
    workflow_id = "wf-test-article"
    _cleanup(workflow_id)
    scheduler = WorkflowScheduler(Path(get_repo_root()))

    try:
        scheduler.create_workflow(
            "WRITING-article",
            workflow_id,
            {
                "goal": "Write a release note",
                "audience": "operators",
                "tone": "plain",
                "word_limit": "600",
            },
            project="release-ops",
        )
        spec = scheduler.load_spec(workflow_id)
        assert spec.project == "release-ops"
        assert spec.purpose
        assert spec.inputs["audience"] == "operators"
        state = scheduler.run_workflow(workflow_id)
        assert state.status == "awaiting_approval"
        assert state.phases[0].status == "pending_approval"
        assert (Path(get_repo_root()) / "memory" / "vault" / "workflows" / workflow_id / "01-outline.md").exists()

        approved = scheduler.approve_phase(workflow_id)
        assert approved.status == "ready"
        assert approved.current_phase_index == 1

        escalated = scheduler.escalate_phase(workflow_id)
        assert escalated.phases[1].tier == "tier2_cloud"
    finally:
        _cleanup(workflow_id)


def test_workflow_scheduler_create_from_markdown_persists_project() -> None:
    workflow_id = "wf-project-markdown"
    _cleanup(workflow_id)
    scheduler = WorkflowScheduler(Path(get_repo_root()))

    markdown = """# WORKFLOW: planning-note

## Goal
Plan a note

## Phases
1. Outline (writing/outline -> 01-outline.md)
"""

    try:
        scheduler.create_workflow_from_markdown(workflow_id, markdown, project="project-lane")
        spec = scheduler.load_spec(workflow_id)
        assert spec.project == "project-lane"
    finally:
        _cleanup(workflow_id)


def test_workflow_scheduler_rejects_invalid_deliverable_contract() -> None:
    workflow_id = "wf-invalid-contract"
    _cleanup(workflow_id)
    scheduler = WorkflowScheduler(Path(get_repo_root()))

    markdown = """# WORKFLOW: invalid-workflow

## Goal
Invalid workflow

## Phases
"""

    try:
        try:
            scheduler.create_workflow_from_markdown(workflow_id, markdown)
        except ValueError as exc:
            assert "Workflow deliverable contract failed" in str(exc)
        else:
            raise AssertionError("Expected deliverable validation failure")
    finally:
        _cleanup(workflow_id)
