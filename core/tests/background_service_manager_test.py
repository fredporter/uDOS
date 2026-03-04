from __future__ import annotations

from core.services.background_service_manager import WizardProcessManager, WizardServiceStatus


def test_ensure_running_starts_process_when_wizard_is_down(monkeypatch, tmp_path) -> None:
    manager = WizardProcessManager(repo_root=tmp_path)
    state: dict[str, bool] = {"started": False}

    monkeypatch.setattr(
        manager,
        "status",
        lambda **_kwargs: WizardServiceStatus(
            base_url="http://127.0.0.1:8765",
            running=False,
            connected=False,
            pid=None,
            message="wizard not running",
            health={},
        ),
    )
    monkeypatch.setattr(
        manager,
        "_start_process",
        lambda: state.__setitem__("started", True) or 111,
    )
    probes = iter(((False, {}), (True, {"status": "ok"})))
    monkeypatch.setattr(manager, "_health", lambda *_args, **_kwargs: next(probes))
    monkeypatch.setattr(manager, "_read_pid", lambda: 111)

    status = manager.ensure_running(base_url="http://127.0.0.1:8765", wait_seconds=1)

    assert state["started"]
    assert status.connected
    assert status.running
    assert status.pid == 111


def test_status_marks_process_running_when_pid_exists_but_health_offline(monkeypatch, tmp_path) -> None:
    manager = WizardProcessManager(repo_root=tmp_path)
    manager.pid_file.write_text("123\n", encoding="utf-8")
    monkeypatch.setattr(manager, "_health", lambda *_args, **_kwargs: (False, {}))
    monkeypatch.setattr("core.services.background_service_manager.WizardProcessManager._pid_alive", staticmethod(lambda _pid: True))

    status = manager.status(base_url="http://127.0.0.1:8765")

    assert status.running
    assert not status.connected
    assert status.pid == 123


def test_read_pid_clears_stale_pid_file(monkeypatch, tmp_path) -> None:
    manager = WizardProcessManager(repo_root=tmp_path)
    manager.pid_file.write_text("999\n", encoding="utf-8")
    monkeypatch.setattr(
        "core.services.background_service_manager.WizardProcessManager._pid_alive",
        staticmethod(lambda _pid: False),
    )

    assert manager._read_pid() is None
    assert not manager.pid_file.exists()


def test_ensure_running_kicks_scheduler_when_required(monkeypatch, tmp_path) -> None:
    manager = WizardProcessManager(repo_root=tmp_path)
    started: dict[str, bool] = {"value": False}
    kicked: dict[str, bool] = {"value": False}

    monkeypatch.setattr(
        manager,
        "status",
        lambda **_kwargs: WizardServiceStatus(
            base_url="http://127.0.0.1:8765",
            running=False,
            connected=False,
            pid=None,
            message="wizard not running",
            health={},
            scheduler=None,
        ),
    )
    monkeypatch.setattr(
        manager,
        "_start_process",
        lambda: started.__setitem__("value", True) or 444,
    )
    monkeypatch.setattr(manager, "_health", lambda *_args, **_kwargs: (True, {"status": "ok"}))
    scheduler_states = iter(
        (
            {"healthy": False, "run_due_tasks": {"overdue": True}},
            {"healthy": True, "run_due_tasks": {"overdue": False}},
        )
    )
    monkeypatch.setattr(manager, "_scheduler_status", lambda: next(scheduler_states))
    monkeypatch.setattr(
        manager,
        "_kick_scheduler",
        lambda: kicked.__setitem__("value", True) or {"returncode": 0},
    )
    monkeypatch.setattr(manager, "_read_pid", lambda: 444)

    status = manager.ensure_running(wait_seconds=1, auto_repair=True, require_scheduler=True)

    assert started["value"] is True
    assert kicked["value"] is True
    assert status.connected is True
    assert status.scheduler["healthy"] is True


def test_ensure_running_records_self_heal_summary(monkeypatch, tmp_path) -> None:
    manager = WizardProcessManager(repo_root=tmp_path)
    monkeypatch.setattr(
        manager,
        "status",
        lambda **_kwargs: WizardServiceStatus(
            base_url="http://127.0.0.1:8765",
            running=False,
            connected=False,
            pid=None,
            message="wizard not running",
            health={},
            scheduler=None,
        ),
    )
    monkeypatch.setattr(manager, "_start_process", lambda: 222)
    monkeypatch.setattr(manager, "_health", lambda *_args, **_kwargs: (True, {"status": "ok"}))
    monkeypatch.setattr(manager, "_scheduler_status", lambda: {"healthy": True})
    monkeypatch.setattr(manager, "_read_pid", lambda: 222)
    monkeypatch.setattr(
        manager,
        "_run_self_heal",
        lambda: {"success": True, "component": "wizard", "repaired": 2},
    )

    status = manager.ensure_running(wait_seconds=1, auto_repair=True, require_scheduler=False)

    assert status.connected is True
    assert status.repair_summary == {"success": True, "component": "wizard", "repaired": 2}
