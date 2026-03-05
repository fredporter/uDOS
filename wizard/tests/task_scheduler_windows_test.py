from __future__ import annotations

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from core.services.time_utils import utc_now
from wizard.services.task_scheduler import TaskScheduler


def test_schedule_due_task_defers_until_off_peak(tmp_path):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    now = utc_now()
    scheduler.update_settings(
        {
            "off_peak_start_hour": (now.hour + 2) % 24,
            "off_peak_end_hour": (now.hour + 3) % 24,
        }
    )
    task = scheduler.create_task(
        name="Night window task",
        schedule="off_peak",
        payload={"window": "off_peak"},
    )

    result = scheduler.schedule_due_tasks()
    queue = scheduler.get_scheduled_queue(limit=5)

    assert result == 1
    assert len(queue) == 1
    scheduled_for = datetime.fromisoformat(str(queue[0]["scheduled_for"]).replace("Z", "+00:00"))
    assert scheduled_for > now


def test_run_pending_defers_when_api_budget_is_exhausted(tmp_path):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings({"api_budget_daily": 2, "off_peak_start_hour": 0, "off_peak_end_hour": 23})
    task = scheduler.create_task(
        name="Budgeted network task",
        schedule="daily",
        provider="cloud",
        requires_network=True,
        resource_cost=3,
        payload={"budget_units": 3},
    )
    scheduler.schedule_task(task["id"], utc_now() - timedelta(minutes=1))
    scheduler._resources_ok = lambda _item: True  # type: ignore[method-assign]

    result = scheduler.run_pending(max_tasks=1)
    queue = scheduler.get_scheduled_queue(limit=5)

    assert result["executed"] == 0
    assert result["deferred"] == 1
    assert queue[0]["state"] == "pending"
    assert queue[0]["defer_reason"] == "api_budget_exhausted"
    assert queue[0]["defer_count"] == 1
    scheduled_for = datetime.fromisoformat(str(queue[0]["scheduled_for"]).replace("Z", "+00:00"))
    assert scheduled_for > utc_now()


def test_run_pending_defers_when_provider_quota_blocks_network_task(tmp_path, monkeypatch):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings({"api_budget_daily": 10, "off_peak_start_hour": 0, "off_peak_end_hour": 23})
    task = scheduler.create_task(
        name="Quota blocked provider task",
        schedule="daily",
        provider="openai",
        requires_network=True,
        resource_cost=1,
        payload={"budget_units": 1, "estimated_tokens": 500},
    )
    scheduler.update_settings({"off_peak_start_hour": 0, "off_peak_end_hour": 23})
    scheduler.schedule_task(task["id"], utc_now() - timedelta(minutes=1))

    class _Quota:
        def can_request(self, provider, estimated_tokens=0):
            return False

    monkeypatch.setattr("wizard.services.task_scheduler.get_quota_tracker", lambda: _Quota())

    result = scheduler.run_pending(max_tasks=1)
    queue = scheduler.get_scheduled_queue(limit=5)

    assert result["executed"] == 0
    assert result["deferred"] == 1
    assert queue[0]["defer_reason"] == "api_budget_exhausted"
    assert queue[0]["defer_count"] == 1


def test_workflow_phase_task_creates_and_defers_on_approval(tmp_path):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings({"off_peak_start_hour": 0, "off_peak_end_hour": 23})
    source = tmp_path / "writing-workflow.md"
    source.write_text(
        """
# WORKFLOW: writing-article-v1

## Goal
Write a release note

## Phases
1. Outline (writing/outline -> 01-outline.md)
2. Draft (writing/draft -> 02-draft.md)
""".strip(),
        encoding="utf-8",
    )
    task = scheduler.create_task(
        name="Workflow outline",
        schedule="daily",
        kind="workflow_phase",
        payload={
            "workflow_id": "writing-workflow",
            "project": "release-writes",
            "source_path": str(source),
            "phase_index": 1,
            "window": "off_peak",
        },
    )
    scheduler.schedule_task(task["id"], utc_now() - timedelta(minutes=1))

    workflow_root = Path("memory") / "vault" / "workflows" / "writing-workflow"
    if workflow_root.exists():
        shutil.rmtree(workflow_root)
    try:
        result = scheduler.run_pending(max_tasks=1)
        queue = scheduler.get_scheduled_queue(limit=5)
        spec = scheduler.workflow_scheduler.load_spec("writing-workflow")

        assert result["executed"] == 0
        assert result["deferred"] == 1
        assert queue[0]["defer_reason"] == "waiting_for_workflow_state"
        assert spec.project == "release-writes"
        assert (workflow_root / "workflow.json").exists()
        assert (workflow_root / "01-outline.md").exists()
    finally:
        if workflow_root.exists():
            shutil.rmtree(workflow_root)


def test_repeated_deferrals_increase_backoff_and_track_metadata(tmp_path, monkeypatch):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings(
        {
            "off_peak_start_hour": 0,
            "off_peak_end_hour": 23,
            "backoff_policy": {
                "resource_pressure": {"base_minutes": 1, "max_minutes": 10},
            },
        }
    )
    task = scheduler.create_task(
        name="Pressure-limited task",
        schedule="daily",
        resource_cost=5,
    )
    scheduler.schedule_task(task["id"], utc_now() - timedelta(minutes=1))

    monkeypatch.setattr(scheduler, "_resources_ok", lambda _item: False)

    first = scheduler.run_pending(max_tasks=1)
    first_queue = scheduler.get_scheduled_queue(limit=5)

    assert first["deferred"] == 1
    assert first_queue[0]["defer_reason"] == "resource_pressure"
    assert first_queue[0]["defer_count"] == 1
    assert first_queue[0]["backoff_seconds"] > 0
    assert first_queue[0]["last_deferred_at"]

    scheduler._defer_queue_item(
        first_queue[0],
        reason="resource_pressure",
        now=utc_now(),
        settings=scheduler.get_settings(),
    )
    second_queue = scheduler.get_scheduled_queue(limit=5)

    assert second_queue[0]["defer_count"] == 2
    assert second_queue[0]["backoff_seconds"] > first_queue[0]["backoff_seconds"]
    assert second_queue[0]["backoff_seconds"] <= 10 * 60


def test_retry_queue_item_clears_defer_metadata(tmp_path):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings({"off_peak_start_hour": 0, "off_peak_end_hour": 23})
    task = scheduler.create_task(name="Retryable task", schedule="daily")
    scheduled = scheduler.schedule_task(task["id"], utc_now() - timedelta(minutes=1))

    queue = scheduler.get_scheduled_queue(limit=5)
    scheduler._defer_queue_item(
        queue[0],
        reason="resource_pressure",
        now=utc_now(),
        settings=scheduler.get_settings(),
    )

    retried = scheduler.retry_queue_item(int(queue[0]["id"]))

    assert retried is not None
    assert retried["defer_reason"] is None
    assert retried["defer_count"] == 0
    assert retried["backoff_seconds"] == 0
    assert retried["last_deferred_at"] is None
    assert retried["run_id"] == scheduled["run_id"]


def test_retry_deferred_items_filters_by_reason(tmp_path):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    first = scheduler.create_task(name="Network task", schedule="daily")
    second = scheduler.create_task(name="Budget task", schedule="daily")
    scheduler.schedule_task(first["id"], utc_now() - timedelta(minutes=1))
    scheduler.schedule_task(second["id"], utc_now() - timedelta(minutes=1))
    queue = scheduler.get_scheduled_queue(limit=10)

    scheduler._defer_queue_item(
        queue[0],
        reason="network_unavailable",
        now=utc_now(),
        settings=scheduler.get_settings(),
    )
    scheduler._defer_queue_item(
        queue[1],
        reason="api_budget_exhausted",
        now=utc_now(),
        settings=scheduler.get_settings(),
    )

    retried = scheduler.retry_deferred_items(reason="network_unavailable", limit=10)
    refreshed = scheduler.get_scheduled_queue(limit=10)
    network_item = next(item for item in refreshed if item["task_id"] == first["id"])
    budget_item = next(item for item in refreshed if item["task_id"] == second["id"])

    assert len(retried) == 1
    assert retried[0]["task_id"] == first["id"]
    assert network_item["defer_reason"] is None
    assert budget_item["defer_reason"] == "api_budget_exhausted"
