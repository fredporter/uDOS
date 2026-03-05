from __future__ import annotations

from core.commands.dev_mode_handler import DevModeHandler


def test_dev_plan_renders_runtime_handoff_summary(monkeypatch) -> None:
    handler = DevModeHandler()

    monkeypatch.setattr(handler, "_admin_guard", lambda: None)
    monkeypatch.setattr(handler, "_dev_templates_guard", lambda: None)
    monkeypatch.setattr(
        "core.commands.dev_mode_handler.http_get",
        lambda *args, **kwargs: {
            "status_code": 200,
            "json": {
                "tasks_ledger": {"mission_count": 2},
                "workflow_plans": [
                    {"id": "contributor-cycle", "step_count": 3, "runtime_project": {"task_count": 3}}
                ],
                "scheduler_templates": [{"id": "weekly-dev-cycle"}],
                "runtime": {
                    "workflow_dashboard": {"summary": {"runs": 1}},
                    "scheduler": {"queue": [{"id": 1}]},
                },
                "ucode_handoff": ["DEV PLAN", "WORKFLOW LIST"],
            },
        },
    )

    result = handler.handle("DEV", ["plan"])

    assert result["status"] == "success"
    assert "DEV PLAN" in result["output"]
    assert "contributor-cycle" in result["output"]
    assert "WORKFLOW LIST" in result["output"]


def test_dev_sync_requires_workflow_path() -> None:
    handler = DevModeHandler()

    result = handler.handle("DEV", ["sync"])

    assert result["status"] == "error"
    assert "Usage: DEV SYNC" in result["output"]


def test_dev_schedule_renders_registered_scheduler_result(monkeypatch) -> None:
    handler = DevModeHandler()

    monkeypatch.setattr(handler, "_admin_guard", lambda: None)
    monkeypatch.setattr(handler, "_dev_templates_guard", lambda: None)
    monkeypatch.setattr(
        "core.commands.dev_mode_handler.http_post",
        lambda *args, **kwargs: {
            "status_code": 200,
            "json": {
                "scheduler_template": {"path": "scheduler/weekly-dev-cycle.template.json"},
                "task": {"id": "task_123"},
                "created": True,
            },
        },
    )

    result = handler.handle(
        "DEV",
        ["schedule", "weekly-dev-cycle.template.json", "contributor-cycle.workflow.json"],
    )

    assert result["status"] == "success"
    assert "DEV SCHEDULE" in result["output"]
    assert "task_123" in result["output"]


def test_dev_run_renders_runtime_task(monkeypatch) -> None:
    handler = DevModeHandler()

    monkeypatch.setattr(handler, "_admin_guard", lambda: None)
    monkeypatch.setattr(handler, "_dev_templates_guard", lambda: None)
    monkeypatch.setattr(
        "core.commands.dev_mode_handler.http_post",
        lambda *args, **kwargs: {
            "status_code": 200,
            "json": {
                "plan": {"path": "workflows/contributor-cycle.workflow.json"},
                "run": {
                    "task_id": "42",
                    "task_title": "implement",
                    "task_status": "in-progress",
                },
            },
        },
    )

    result = handler.handle("DEV", ["run", "contributor-cycle.workflow.json"])

    assert result["status"] == "success"
    assert "DEV RUN" in result["output"]
    assert "implement" in result["output"]


def test_dev_task_renders_updated_status(monkeypatch) -> None:
    handler = DevModeHandler()

    monkeypatch.setattr(handler, "_admin_guard", lambda: None)
    monkeypatch.setattr(handler, "_dev_templates_guard", lambda: None)
    monkeypatch.setattr(
        "core.commands.dev_mode_handler.http_post",
        lambda *args, **kwargs: {
            "status_code": 200,
            "json": {
                "plan": {"path": "workflows/contributor-cycle.workflow.json"},
                "task": {
                    "id": 42,
                    "title": "implement",
                    "status": "completed",
                },
            },
        },
    )

    result = handler.handle("DEV", ["task", "contributor-cycle.workflow.json", "42", "completed"])

    assert result["status"] == "success"
    assert "DEV TASK" in result["output"]
    assert "completed" in result["output"]
