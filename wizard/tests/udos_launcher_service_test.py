from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

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
    def __init__(self, conflicts=None) -> None:
        self._conflicts = conflicts or []
        self.checked = 0

    def check_all_services(self):
        self.checked += 1

    def get_conflicts(self):
        return list(self._conflicts)


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


def test_status_reports_repo_root_and_port_conflicts(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_ports = _FakePortManager(
        conflicts=[
            (
                "wizard",
                {"process": "python", "pid": 999, "port": 58008},
            )
        ]
    )
    fake_process_manager = SimpleNamespace(status=lambda: _wizard_status(connected=False, message="degraded"))

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)

    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)
    result = service.status()

    assert result.success is False
    assert result.details["repo_root"] == str(tmp_path)
    assert result.details["wizard"]["message"] == "degraded"
    assert result.details["port_conflicts"] == [
        {"service": "wizard", "process": "python", "pid": 999, "port": 58008}
    ]
    assert fake_ports.checked == 1


def test_start_runtime_records_ready_launch_session(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_ports = _FakePortManager()
    fake_process_manager = SimpleNamespace(
        ensure_running=lambda **kwargs: _wizard_status(connected=True),
    )

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)

    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)
    monkeypatch.setattr(service, "_repair_ports", lambda: {"healed": {"wizard": True}})

    result = service.start_runtime(auto_repair=True, wait_seconds=3)

    assert result.success is True
    assert result.details["session_id"] == "session-001"
    assert result.details["repair"] == {"healed": {"wizard": True}}
    assert fake_sessions.created[0]["workspace"] == "core"
    assert fake_sessions.transitions == [
        ("session-001", "starting", None, None),
        ("session-001", "ready", None, {"wizard_base_url": "http://127.0.0.1:58008"}),
    ]


def test_repair_runtime_combines_self_heal_and_runtime_status(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_ports = _FakePortManager()
    fake_process_manager = SimpleNamespace(
        ensure_running=lambda **kwargs: _wizard_status(connected=True, message="healthy"),
    )

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)
    monkeypatch.setattr(
        launcher_mod,
        "collect_self_heal_summary",
        lambda component, auto_repair: {"success": True, "component": component, "auto_repair": auto_repair},
    )

    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)
    monkeypatch.setattr(service, "_repair_ports", lambda: {"remaining": []})

    result = service.repair_runtime()

    assert result.success is True
    assert result.details["repair"] == {"remaining": []}
    assert result.details["self_heal"] == {
        "success": True,
        "component": "wizard",
        "auto_repair": True,
    }
    assert result.details["wizard"]["message"] == "healthy"


def test_update_from_remote_runs_fetch_and_pull(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_ports = _FakePortManager()
    fake_process_manager = SimpleNamespace(status=lambda: _wizard_status(connected=True))

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)

    (tmp_path / ".git").mkdir()
    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)

    commands: list[list[str]] = []
    monkeypatch.setattr(
        service,
        "_run",
        lambda command: commands.append(command) or {"command": command, "returncode": 0, "stdout": "", "stderr": ""},
    )

    result = service.update_from_remote(remote="upstream", branch="stable")

    assert result.success is True
    assert commands == [
        ["git", "fetch", "upstream", "--prune"],
        ["git", "pull", "--ff-only", "upstream", "stable"],
    ]


def test_wizard_command_logs_returns_tail(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_ports = _FakePortManager()
    log_file = tmp_path / "memory" / "logs" / "wizard-daemon.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("line-1\nline-2\n", encoding="utf-8")
    fake_process_manager = SimpleNamespace(
        status=lambda: _wizard_status(connected=True),
        log_file=log_file,
    )

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)

    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)
    result = service.wizard_command("logs")

    assert result.success is True
    assert result.action == "wizard-logs"
    assert result.details["path"] == str(log_file)
    assert result.details["tail"] == "line-1\nline-2"


class _ExecvCalled(Exception):
    def __init__(self, program: str, argv: list[str]) -> None:
        self.program = program
        self.argv = argv


def test_launch_tui_prefers_bubbletea_binary(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_ports = _FakePortManager()
    fake_process_manager = SimpleNamespace(status=lambda: _wizard_status(connected=True))

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)

    bubbletea = tmp_path / "tui" / "bin" / "udos-tui"
    bubbletea.parent.mkdir(parents=True, exist_ok=True)
    bubbletea.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    bubbletea.chmod(0o755)

    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)

    monkeypatch.setattr(service, "_build_bubbletea_tui", lambda: False)

    def _fake_execv(program: str, argv: list[str]) -> None:
        raise _ExecvCalled(program, argv)

    monkeypatch.setattr(launcher_mod.os, "execv", _fake_execv)

    with pytest.raises(_ExecvCalled) as exc:
        service.launch_tui(["--", "STATUS"])

    assert exc.value.program == str(bubbletea)
    assert exc.value.argv == [str(bubbletea), "--", "STATUS"]


def test_launch_tui_errors_when_bubbletea_unavailable(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_ports = _FakePortManager()
    fake_process_manager = SimpleNamespace(status=lambda: _wizard_status(connected=True))

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)

    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)
    monkeypatch.setattr(service, "_build_bubbletea_tui", lambda: False)

    with pytest.raises(RuntimeError) as exc:
        service.launch_tui(["--", "STATUS"])

    assert "Bubble Tea TUI is unavailable" in str(exc.value)


def test_rebuild_runtime_runs_renderer_checks_when_npm_available(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_ports = _FakePortManager()
    fake_process_manager = SimpleNamespace(status=lambda: _wizard_status(connected=True))

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)
    monkeypatch.setattr(launcher_mod.shutil, "which", lambda name: "/usr/bin/npm" if name == "npm" else None)

    (tmp_path / "core").mkdir(parents=True, exist_ok=True)
    (tmp_path / "core" / "package.json").write_text("{}", encoding="utf-8")

    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)
    monkeypatch.setattr(service, "_repair_ports", lambda: {"remaining": []})

    captured: list[tuple[list[str], Path | None]] = []

    def _fake_run(command: list[str], cwd: Path | None = None):
        captured.append((command, cwd))
        return {"command": command, "cwd": str(cwd or tmp_path), "returncode": 0, "stdout": "", "stderr": ""}

    monkeypatch.setattr(service, "_run", _fake_run)

    result = service.rebuild_runtime()

    assert result.success is True
    assert any(cmd == ["npm", "run", "-s", "test:renderer"] for cmd, _cwd in captured)
    assert any(cmd == ["npm", "run", "-s", "test:renderer-cli"] for cmd, _cwd in captured)


def test_reassign_wizard_port_skips_reserved_ports(monkeypatch, tmp_path: Path) -> None:
    fake_sessions = _FakeSessions()
    fake_process_manager = SimpleNamespace(status=lambda: _wizard_status(connected=True))

    class _Service:
        def __init__(self, port):
            self.port = port

    class _FakePorts:
        def __init__(self):
            self.services = {"wizard": _Service(8765), "vite": _Service(5173)}
            self.calls = []
            self.reassigned = []

        def get_available_port(self, start_port, reserved_ports=None, include_registered=True):
            self.calls.append((start_port, reserved_ports, include_registered))
            return 8770

        def reassign_port(self, service_name, new_port):
            self.reassigned.append((service_name, new_port))
            return True

    fake_ports = _FakePorts()

    monkeypatch.setattr(launcher_mod, "get_launch_session_service", lambda repo_root=None: fake_sessions)
    monkeypatch.setattr(launcher_mod, "get_wizard_process_manager", lambda: fake_process_manager)
    monkeypatch.setattr(launcher_mod, "get_port_manager", lambda: fake_ports)
    monkeypatch.setattr(launcher_mod, "load_wizard_config_data", lambda: {"port": 8765})
    saved = {}
    monkeypatch.setattr(launcher_mod, "save_wizard_config_data", lambda cfg: saved.update(cfg))

    service = launcher_mod.UdosLauncherService(repo_root=tmp_path)
    outcome = service._reassign_wizard_port()

    assert outcome == {"old_port": 8765, "new_port": 8770}
    assert fake_ports.calls[0][0] == 8766
    assert fake_ports.calls[0][1] == {5173}
    assert fake_ports.calls[0][2] is False
    assert fake_ports.reassigned == [("wizard", 8770)]
    assert saved["port"] == 8770
