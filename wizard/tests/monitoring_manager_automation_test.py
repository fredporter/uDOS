from datetime import datetime, timedelta

from wizard.services.monitoring_manager import MonitoringManager
from wizard.services.task_scheduler import TaskScheduler


def test_record_automation_run_exposed_in_recent_runs(tmp_path):
    manager = MonitoringManager(
        data_dir=tmp_path / "monitoring",
        db_path=tmp_path / "ops.db",
    )

    manager.record_automation_run(
        "run_due_tasks",
        success=True,
        duration_ms=123.4,
        metadata={"executed": 2, "deferred": 1},
    )

    runs = manager.get_recent_automation_runs(limit=5)
    assert len(runs) == 1
    assert runs[0]["operation"] == "automation:run_due_tasks"
    assert runs[0]["metadata"]["executed"] == 2

    status = manager.get_automation_status()
    assert status["run_due_tasks"]["last_status"] == "success"
    assert status["run_due_tasks"]["overdue"] is False


def test_overdue_automation_job_creates_alert(tmp_path):
    manager = MonitoringManager(
        data_dir=tmp_path / "monitoring",
        db_path=tmp_path / "ops.db",
    )
    manager.store.update_scheduler_settings(
        {
            "automation_heartbeat:run_due_tasks": {
                "last_run_at": "2000-01-01T00:00:00",
                "last_success_at": "2000-01-01T00:00:00",
                "last_status": "success",
            }
        }
    )

    health = manager.check_automation_jobs()

    assert health.status == "degraded"
    alerts = manager.get_alerts(service="wizard.jobs", limit=10)
    assert any("heartbeat overdue" in alert.message.lower() for alert in alerts)


def test_overdue_alert_resolves_after_recovery(tmp_path):
    manager = MonitoringManager(
        data_dir=tmp_path / "monitoring",
        db_path=tmp_path / "ops.db",
    )
    manager.store.update_scheduler_settings(
        {
            "automation_heartbeat:run_due_tasks": {
                "last_run_at": "2000-01-01T00:00:00",
                "last_success_at": "2000-01-01T00:00:00",
                "last_status": "success",
            }
        }
    )
    manager.check_automation_jobs()

    manager.record_automation_run("run_due_tasks", success=True, duration_ms=10.0, metadata={"executed": 1})
    manager.record_automation_run("health_snapshot", success=True, duration_ms=12.0, metadata={"status": "ok"})
    manager.record_automation_run("maintenance", success=True, duration_ms=8.0, metadata={"status": "ok"})
    health = manager.check_automation_jobs()

    assert health.status == "healthy"
    alerts = manager.get_alerts(service="wizard.jobs", limit=10)
    overdue_alerts = [alert for alert in alerts if "heartbeat overdue" in alert.message.lower()]
    assert overdue_alerts
    assert all(alert.resolved for alert in overdue_alerts)


def test_failure_alert_resolves_after_successful_run(tmp_path):
    manager = MonitoringManager(
        data_dir=tmp_path / "monitoring",
        db_path=tmp_path / "ops.db",
    )

    manager.record_automation_run("run_due_tasks", success=False, error="boom")
    failed_alerts = [
        alert for alert in manager.get_alerts(service="wizard.jobs", limit=10)
        if "automation job failed" in alert.message.lower()
    ]
    assert failed_alerts
    assert any(not alert.resolved for alert in failed_alerts)

    manager.record_automation_run("run_due_tasks", success=True, duration_ms=15.0, metadata={"executed": 2})

    refreshed = [
        alert for alert in manager.get_alerts(service="wizard.jobs", limit=10)
        if "automation job failed" in alert.message.lower()
    ]
    assert refreshed
    assert all(alert.resolved for alert in refreshed)


def test_deferred_queue_pressure_creates_and_resolves_alert(tmp_path):
    scheduler = TaskScheduler(db_path=tmp_path / "tasks.db")
    scheduler.update_settings(
        {
            "off_peak_start_hour": 0,
            "off_peak_end_hour": 23,
            "defer_alert_threshold": 2,
            "backoff_alert_minutes": 10,
        }
    )
    task = scheduler.create_task(name="Deferred task", schedule="daily")
    scheduler.schedule_task(task["id"], datetime.now() - timedelta(minutes=1))
    queue = scheduler.get_scheduled_queue(limit=5)
    scheduler._defer_queue_item(
        queue[0],
        reason="resource_pressure",
        now=datetime.now(),
        settings=scheduler.get_settings(),
    )
    queue = scheduler.get_scheduled_queue(limit=5)
    scheduler._defer_queue_item(
        queue[0],
        reason="resource_pressure",
        now=datetime.now(),
        settings=scheduler.get_settings(),
    )

    manager = MonitoringManager(
        data_dir=tmp_path / "monitoring",
        db_path=tmp_path / "tasks.db",
        scheduler_factory=lambda: scheduler,
    )
    health = manager.check_scheduler_queue()

    assert health.status == "degraded"
    alerts = manager.get_alerts(service="wizard.scheduler", limit=10)
    assert any("deferred queue pressure" in alert.message.lower() for alert in alerts)

    scheduler.retry_queue_item(int(scheduler.get_scheduled_queue(limit=5)[0]["id"]))
    recovered = manager.check_scheduler_queue()

    assert recovered.status == "healthy"
    refreshed = manager.get_alerts(service="wizard.scheduler", limit=10)
    pressure_alerts = [alert for alert in refreshed if "deferred queue pressure" in alert.message.lower()]
    assert pressure_alerts
    assert all(alert.resolved for alert in pressure_alerts)


def test_self_heal_notification_uses_configured_store(tmp_path, monkeypatch):
    manager = MonitoringManager(
        data_dir=tmp_path / "monitoring",
        db_path=tmp_path / "ops.db",
    )
    monkeypatch.setattr(
        "wizard.services.monitoring_manager.read_last_summary",
        lambda: {"self_heal": {"remaining": 1}},
    )
    monkeypatch.setattr(
        manager,
        "get_health_summary",
        lambda: {"status": "degraded"},
    )

    manager.log_training_summary()

    notifications, total = manager.store.get_notifications(limit=10, offset=0)
    assert total == 1
    assert "Self-Heal drift detected" in notifications[0]["message"]
