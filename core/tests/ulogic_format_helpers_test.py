from __future__ import annotations

from core.ulogic import describe_json_format_profile, format_json_text


def test_format_helper_formats_contributor_tasks_ledger_by_path() -> None:
    result = format_json_text(
        '{"active_missions":[{"title":"Tracked editor","status":"done","id":"tracked-editor","artifacts":["wizard/routes/dev_routes.py"]}],"updated":"2026-03-04","version":"1.0"}',
        source_path="dev/ops/tasks.json",
    )

    assert result.ok is True
    assert result.profile == "tasks-ledger"
    assert result.format_label == "Contributor tasks JSON"
    assert '"version": "1.0"' in result.content
    assert result.content.index('"version"') < result.content.index('"updated"')
    assert result.content.index('"id"') < result.content.index('"title"')


def test_format_helper_formats_workflow_runtime_spec() -> None:
    result = format_json_text(
        '{"phases":[{"outputs":["01-outline.md"],"prompt_name":"creative-outline","name":"outline","adapter":"creative"}],"workflow_id":"wf-001","project":"demo"}',
        source_path="memory/vault/workflows/wf-001/workflow.json",
    )

    assert result.ok is True
    assert result.profile == "workflow-spec"
    assert result.content.index('"workflow_id"') < result.content.index('"project"')
    assert result.content.index('"name"') < result.content.index('"adapter"')


def test_format_helper_reports_workflow_shape_errors() -> None:
    result = format_json_text(
        '{"workflow_id":"wf-001","steps":[{"step_id":"outline"}]}',
        source_path="dev/ops/workflows/contributor-cycle.workflow.json",
    )

    assert result.ok is False
    assert result.profile == "workflow-plan"
    assert "missing required key `action`" in result.errors[0]


def test_format_helper_describes_completed_profile_by_path() -> None:
    helper = describe_json_format_profile(source_path="dev/ops/completed.json")

    assert helper["profile"] == "completed-ledger"
    assert helper["profile_label"] == "Completed Milestones"
