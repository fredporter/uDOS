from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from core.services.background_service_manager import WizardServiceStatus
from wizard.services import udos_launcher_service as launcher_mod


class _FakeSessions:
    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []
        self.transitions: list[tuple[str, str, str | None, dict[str, object] | None]] = []

    def create_session(self, **kwargs):
        session = {"session_id": "session-001", **kwargs}
        self.created.append(session)
        return session

    def transition(self, session_id, state, error=None, updates=None):
        self.transitions.append((session_id, state, error, updates))
        return {
            "session_id": session_id,
            "state": state,
            "error": error,
            "updates": updates,
        }


class _FakePortManager:
    def check_all_services(self):
        return None

    def get_conflicts(self):
        return []


def _wizard_status(*, connected: bool, running: bool = True, message: str = "ok", pid: int = 321):
    return WizardServiceStatus(
        base_url="http://127.0.0.1:58008",
        running=running,
        connected=connected,
        pid=pid if running else None,
        message=message,
        health={"status": "ok" if connected else "down"},
        scheduler={"healthy": connected},
    )


def test_start_runtime_uses_dev_workspace_when_dev_mode_active(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_ports = _FakePortManager()
    fake_process_manager = SimpleNamespace(
        ensure_running=lambda **kwargs: _wizard_status(connected=True),
    )

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)

    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)
    monkeypatch.setattr(service, "_dev_mode_active", lambda: True)
    monkeypatch.setattr(service, "_repair_ports", lambda: {"healed": {"wizard": True}})

    result = service.start_runtime(auto_repair=True, wait_seconds=3)

    assert result.success is True
    assert fake_sessions.created[0]["workspace"] == "@dev"
    assert fake_sessions.transitions == [
        ("session-001", "starting", None, None),
        ("session-001", "ready", None, {"wizard_base_url": "http://127.0.0.1:58008"}),
    ]
