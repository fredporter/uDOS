from __future__ import annotations

from core.ulogic.deliverables import (
    validate_project_file_payload,
    validate_project_record,
    validate_tasks_file_payload,
    validate_task_record,
    validate_wizard_budget_record,
    validate_workflow_record,
)
from core.ulogic.research_pipeline import (
    ResearchRequest,
    enrich_document,
    generate_artifact,
    normalize_research_input,
)


def test_validate_project_record_accepts_deliverable_shape() -> None:
    result = validate_project_record(
        {
            "project_id": "udos-v1-5",
            "name": "uDOS v1.5",
            "missions": ["logic", "tui"],
            "status": "active",
        }
    )

    assert result.ok is True
    assert result.errors == []


def test_validate_workflow_record_rejects_missing_step_action() -> None:
    result = validate_workflow_record(
        {
            "workflow_id": "wf-001",
            "steps": [{"step_id": "outline"}],
        }
    )

    assert result.ok is False
    assert "$.steps[0]: missing required key `action`" in result.errors


def test_validate_task_and_budget_records() -> None:
    task_result = validate_task_record(
        {"task_id": "task-001", "title": "Document flow", "status": "open"}
    )
    budget_result = validate_wizard_budget_record(
        {
            "daily_limit": 10.0,
            "tiers": {"tier0_free": True, "tier1_budget": 5.0, "tier2_budget": 5.0},
            "auto_defer_when_exceeded": True,
        }
    )

    assert task_result.ok is True
    assert budget_result.ok is True


def test_validate_project_and_tasks_file_payloads() -> None:
    project_result = validate_project_file_payload(
        {
            "id": "binder-alpha",
            "name": "Binder Alpha",
            "description": "Research lane",
        }
    )
    tasks_result = validate_tasks_file_payload(
        {
            "tasks": [
                {"id": "task-001", "title": "Collect notes", "status": "todo"},
                {"id": "task-002", "title": "Summarize notes", "status": "review"},
            ]
        }
    )

    assert project_result.ok is True
    assert tasks_result.ok is True


def test_research_pipeline_normalizes_enriches_and_generates_markdown() -> None:
    request = ResearchRequest(
        topic="local assist benchmarks",
        source_type="api",
        source_ref="benchmark://latest",
        project_id="udos-v1-5",
        binder_id="research-stack",
        tags=("benchmarks", "gpt4all"),
    )

    document = normalize_research_input(
        request,
        title="Local Assist Benchmarks",
        body=(
            "Compare GPT4All setup cost with offline workflow execution. "
            "Install and setup details matter for the upgrade path."
        ),
        metadata={"api_engine": "benchmarks-v1"},
    )
    enriched = enrich_document(
        document,
        active_projects=["udos-v1-5", "other-project"],
        active_binders=["research-stack"],
    )
    artifact = generate_artifact(enriched, artifact_kind="guide")

    markdown = document.to_markdown()

    assert 'source_type: "api"' in markdown
    assert 'topic: "local assist benchmarks"' in markdown
    assert "## Summary" in artifact.markdown
    assert "## Suggested Tasks" in artifact.markdown
    assert "Create comparison note from ingested source" in artifact.markdown
    assert enriched.related_projects == ("udos-v1-5",)
    assert enriched.related_binders == ("research-stack",)
