"""Integration tests for device/automation/user backend replacement paths."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from core.services.persistence_service import PersistenceService
from core.services.dev_mode_compat import (
    AutomationTask,
    DevModeToolAutomationService,
    DevModeToolDeviceService,
    DevModeToolUserService,
)


def test_user_auth_failure_then_recovery(tmp_path: Path) -> None:
    service = DevModeToolUserService()
    service.persistence_service = PersistenceService(str(tmp_path / "vibe"))
    service.users = {}

    create = service.add_user("alice", "alice@example.com", "user", password="secret123")
    assert create["status"] == "success"

    failed = service.authenticate("alice", "wrong")
    recovered = service.authenticate("alice", "secret123")

    assert failed["status"] == "error"
    assert recovered["status"] == "success"
    assert recovered["user"]["username"] == "alice"


def test_wizard_task_metrics_track_runs(tmp_path: Path) -> None:
    service = DevModeToolAutomationService()
    service.persistence_service = PersistenceService(str(tmp_path / "vibe"))
    service.tasks = {}
    service.task_stats = {}
    service._active_runs = {}

    task_id = "daily-report"
    now = datetime.now().isoformat()
    service.tasks[task_id] = AutomationTask(
        id=task_id,
        name="Daily Report",
        description="Generate report",
        status="idle",
        created=now,
    )

    started = service.start_task(task_id)
    assert started["status"] == "success"
    stopped = service.stop_task(task_id)
    assert stopped["status"] == "success"
    status = service.task_status(task_id)
    assert status["status"] == "success"
    assert status["metrics"]["total_runs"] == 1
    assert status["metrics"]["successful_runs"] == 1
    assert status["metrics"]["failed_runs"] == 0


def test_device_health_improves_after_recovery(tmp_path: Path) -> None:
    service = DevModeToolDeviceService()
    service.persistence_service = PersistenceService(str(tmp_path / "vibe"))
    service.devices = {}

    created = service.add_device("Edge-1", "server", "lab")
    device_id = created["device_id"]
    device = service.devices[device_id]
    device.status = "offline"
    device.last_seen = (datetime.now() - timedelta(minutes=20)).isoformat()
    service._save_devices()

    degraded = service.device_status(device_id)
    assert degraded["status"] == "success"
    degraded_score = degraded["health"]["health_score"]
    assert degraded_score < 60
    assert degraded["alerts"]

    service.update_device(device_id, status="online")
    recovered = service.device_status(device_id)
    assert recovered["status"] == "success"
    assert recovered["health"]["health_score"] > degraded_score
