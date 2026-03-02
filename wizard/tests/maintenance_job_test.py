from __future__ import annotations

from datetime import datetime, timedelta

from wizard.jobs import maintenance
from wizard.services.task_scheduler import TaskScheduler


def test_maintenance_retries_configured_deferred_reasons(tmp_path, monkeypatch):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings(
        {
            "auto_retry_deferred_reasons": ["network_unavailable"],
            "auto_retry_deferred_limit": 5,
        }
    )
    task = scheduler.create_task(name="Recoverable task", schedule="daily")
    scheduler.schedule_task(task["id"], datetime.now() - timedelta(minutes=1))
    queue = scheduler.get_scheduled_queue(limit=5)
    scheduler._defer_queue_item(
        queue[0],
        reason="network_unavailable",
        now=datetime.now(),
        settings=scheduler.get_settings(),
    )

    monkeypatch.setattr(maintenance, "TaskScheduler", lambda: scheduler)

    recorded = {}

    class StubMonitoring:
        def record_automation_run(self, name, *, success, duration_ms, metadata=None, error=None):
            recorded["name"] = name
            recorded["success"] = success
            recorded["metadata"] = metadata or {}
            recorded["error"] = error

    monkeypatch.setattr(maintenance, "MonitoringManager", lambda: StubMonitoring())

    result = maintenance.main()
    refreshed = scheduler.get_scheduled_queue(limit=5)

    assert result == 0
    assert refreshed[0]["defer_reason"] is None
    assert recorded["name"] == "maintenance"
    assert recorded["success"] is True
    assert recorded["metadata"]["retried_by_reason"]["network_unavailable"] == 1


def test_maintenance_uses_reason_policy_and_dry_run(tmp_path, monkeypatch):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings(
        {
            "maintenance_retry_dry_run": False,
            "auto_retry_deferred_reasons": ["network_unavailable", "api_budget_exhausted"],
            "auto_retry_deferred_limit": 10,
            "auto_retry_deferred_policy": {
                "network_unavailable": {"enabled": True, "limit": 1, "dry_run": False},
                "api_budget_exhausted": {"enabled": True, "limit": 2, "dry_run": True},
            },
        }
    )
    network_task = scheduler.create_task(name="Network task", schedule="daily")
    budget_task = scheduler.create_task(name="Budget task", schedule="daily")
    scheduler.schedule_task(network_task["id"], datetime.now() - timedelta(minutes=1))
    scheduler.schedule_task(budget_task["id"], datetime.now() - timedelta(minutes=1))
    queue = scheduler.get_scheduled_queue(limit=10)
    network_item = next(item for item in queue if item["task_id"] == network_task["id"])
    budget_item = next(item for item in queue if item["task_id"] == budget_task["id"])
    scheduler._defer_queue_item(
        network_item,
        reason="network_unavailable",
        now=datetime.now(),
        settings=scheduler.get_settings(),
    )
    scheduler._defer_queue_item(
        budget_item,
        reason="api_budget_exhausted",
        now=datetime.now(),
        settings=scheduler.get_settings(),
    )

    monkeypatch.setattr(maintenance, "TaskScheduler", lambda: scheduler)

    recorded = {}

    class StubMonitoring:
        def record_automation_run(self, name, *, success, duration_ms, metadata=None, error=None):
            recorded["name"] = name
            recorded["success"] = success
            recorded["metadata"] = metadata or {}
            recorded["error"] = error

    monkeypatch.setattr(maintenance, "MonitoringManager", lambda: StubMonitoring())

    result = maintenance.main()
    refreshed = scheduler.get_scheduled_queue(limit=10)
    refreshed_network = next(item for item in refreshed if item["task_id"] == network_task["id"])
    refreshed_budget = next(item for item in refreshed if item["task_id"] == budget_task["id"])

    assert result == 0
    assert refreshed_network["defer_reason"] is None
    assert refreshed_budget["defer_reason"] == "api_budget_exhausted"
    assert recorded["name"] == "maintenance"
    assert recorded["metadata"]["preview_by_reason"]["network_unavailable"] == 1
    assert recorded["metadata"]["preview_by_reason"]["api_budget_exhausted"] == 1
    assert recorded["metadata"]["retried_by_reason"]["network_unavailable"] == 1
    assert recorded["metadata"]["retried_by_reason"]["api_budget_exhausted"] == 0


def test_maintenance_dry_run_records_preview_operation(tmp_path, monkeypatch):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings(
        {
            "maintenance_retry_dry_run": True,
            "auto_retry_deferred_policy": {
                "network_unavailable": {"enabled": True, "limit": 5, "dry_run": False},
            },
        }
    )
    task = scheduler.create_task(name="Dry run task", schedule="daily")
    scheduler.schedule_task(task["id"], datetime.now() - timedelta(minutes=1))
    queue = scheduler.get_scheduled_queue(limit=5)
    scheduler._defer_queue_item(
        queue[0],
        reason="network_unavailable",
        now=datetime.now(),
        settings=scheduler.get_settings(),
    )

    monkeypatch.setattr(maintenance, "TaskScheduler", lambda: scheduler)

    recorded = {}

    class StubMonitoring:
        def record_automation_run(self, name, *, success, duration_ms, metadata=None, error=None):
            recorded["name"] = name
            recorded["success"] = success
            recorded["metadata"] = metadata or {}
            recorded["error"] = error

    monkeypatch.setattr(maintenance, "MonitoringManager", lambda: StubMonitoring())

    result = maintenance.main()
    refreshed = scheduler.get_scheduled_queue(limit=5)

    assert result == 0
    assert recorded["name"] == "maintenance_preview"
    assert recorded["metadata"]["preview_by_reason"]["network_unavailable"] == 1
    assert recorded["metadata"]["retried_by_reason"]["network_unavailable"] == 0
    assert refreshed[0]["defer_reason"] == "network_unavailable"


def test_maintenance_skips_reason_outside_window(tmp_path, monkeypatch):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings(
        {
            "maintenance_retry_dry_run": False,
            "auto_retry_deferred_policy": {
                "network_unavailable": {"enabled": True, "limit": 5, "dry_run": False, "window": "23:00-23:30"},
            },
        }
    )
    task = scheduler.create_task(name="Windowed task", schedule="daily")
    scheduler.schedule_task(task["id"], datetime.now() - timedelta(minutes=1))
    queue = scheduler.get_scheduled_queue(limit=5)
    scheduler._defer_queue_item(
        queue[0],
        reason="network_unavailable",
        now=datetime.now(),
        settings=scheduler.get_settings(),
    )

    monkeypatch.setattr(maintenance, "TaskScheduler", lambda: scheduler)

    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 3, 3, 12, 0, 0)

    monkeypatch.setattr(maintenance, "datetime", FakeDatetime)

    recorded = {}

    class StubMonitoring:
        def record_automation_run(self, name, *, success, duration_ms, metadata=None, error=None):
            recorded["name"] = name
            recorded["success"] = success
            recorded["metadata"] = metadata or {}
            recorded["error"] = error

    monkeypatch.setattr(maintenance, "MonitoringManager", lambda: StubMonitoring())

    result = maintenance.main()
    refreshed = scheduler.get_scheduled_queue(limit=5)

    assert result == 0
    assert recorded["name"] == "maintenance"
    assert recorded["metadata"]["preview_by_reason"]["network_unavailable"] == 1
    assert recorded["metadata"]["retried_by_reason"]["network_unavailable"] == 0
    assert recorded["metadata"]["skipped_by_window"]["network_unavailable"] == 1
    assert refreshed[0]["defer_reason"] == "network_unavailable"
