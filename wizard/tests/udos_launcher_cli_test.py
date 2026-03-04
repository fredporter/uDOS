from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from wizard.services import udos_launcher_cli as cli_mod
from wizard.services.udos_launcher_service import LauncherResult


class _ExecvCalled(Exception):
    def __init__(self, program: str, argv: list[str]) -> None:
        self.program = program
        self.argv = argv


class _FakeService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def status(self):
        self.calls.append(("status", None))
        return LauncherResult(True, "status", "runtime ok", {"wizard": {"connected": True}}, 0)

    def start_runtime(self, *, auto_repair: bool = True):
        self.calls.append(("start_runtime", auto_repair))
        return LauncherResult(True, "start", "runtime ready", {"wizard": {"connected": True}}, 0)

    def repair_runtime(self):
        self.calls.append(("repair_runtime", None))
        return LauncherResult(True, "repair", "repair ok", {}, 0)

    def rebuild_runtime(self):
        self.calls.append(("rebuild_runtime", None))
        return LauncherResult(True, "rebuild", "rebuild ok", {}, 0)

    def update_from_remote(self, *, remote: str = "origin", branch: str = "main"):
        self.calls.append(("update_from_remote", (remote, branch)))
        return LauncherResult(True, "update", "update ok", {"remote": remote, "branch": branch}, 0)

    def wizard_command(self, command: str):
        self.calls.append(("wizard_command", command))
        return LauncherResult(True, "wizard-logs", "Wizard logs", {"tail": "log-a\nlog-b"}, 0)

    def launch_tui(self, args: list[str]):
        self.calls.append(("launch_tui", list(args)))
        return 91

    def launch_ops(self, args: list[str]):
        self.calls.append(("launch_ops", list(args)))
        return 37


def test_status_json_output(monkeypatch, capsys) -> None:
    service = _FakeService()
    monkeypatch.setattr(cli_mod, "get_udos_launcher_service", lambda: service)

    exit_code = cli_mod.main(["--json", "status"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["message"] == "runtime ok"
    assert service.calls == [("status", None)]


def test_start_no_tui_emits_result(monkeypatch, capsys) -> None:
    service = _FakeService()
    monkeypatch.setattr(cli_mod, "get_udos_launcher_service", lambda: service)

    exit_code = cli_mod.main(["start", "--no-tui"])

    assert exit_code == 0
    assert "runtime ready" in capsys.readouterr().out
    assert service.calls == [("start_runtime", True)]


def test_start_launches_tui_when_runtime_ready_and_tty(monkeypatch) -> None:
    service = _FakeService()
    monkeypatch.setattr(cli_mod, "get_udos_launcher_service", lambda: service)
    monkeypatch.setattr(cli_mod.sys, "stdin", SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(cli_mod.sys, "stdout", SimpleNamespace(isatty=lambda: True, write=lambda *_args: None, flush=lambda: None))

    exit_code = cli_mod.main(["start"])

    assert exit_code == 91
    assert service.calls == [("start_runtime", True), ("launch_tui", [])]


def test_wizard_logs_emits_tail(monkeypatch, capsys) -> None:
    service = _FakeService()
    monkeypatch.setattr(cli_mod, "get_udos_launcher_service", lambda: service)

    exit_code = cli_mod.main(["wizard", "logs"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Wizard logs" in output
    assert "log-a" in output
    assert service.calls == [("wizard_command", "logs")]


def test_ops_delegates_to_service(monkeypatch) -> None:
    service = _FakeService()
    monkeypatch.setattr(cli_mod, "get_udos_launcher_service", lambda: service)

    exit_code = cli_mod.main(["ops", "--", "STATUS"])

    assert exit_code == 37
    assert service.calls == [("launch_ops", ["--", "STATUS"])]


def test_tui_execv_uses_core_entry(monkeypatch) -> None:
    def _fake_execv(program: str, argv: list[str]) -> None:
        raise _ExecvCalled(program, argv)

    monkeypatch.setattr(cli_mod.os, "execv", _fake_execv)

    with pytest.raises(_ExecvCalled) as exc:
        cli_mod.main(["tui", "--", "STATUS"])

    assert exc.value.program == cli_mod.sys.executable
    assert exc.value.argv == [cli_mod.sys.executable, "-m", "core.tui.ucode_entry", "--", "STATUS"]


def test_install_execv_uses_repo_installer(monkeypatch) -> None:
    def _fake_execv(program: str, argv: list[str]) -> None:
        raise _ExecvCalled(program, argv)

    monkeypatch.setattr(cli_mod.os, "execv", _fake_execv)

    with pytest.raises(_ExecvCalled) as exc:
        cli_mod.main(["install", "--", "--wizard"])

    assert exc.value.program == "/bin/bash"
    assert exc.value.argv[0] == "/bin/bash"
    assert Path(exc.value.argv[1]).name == "install-udos-vibe.sh"
    assert exc.value.argv[-2:] == ["--", "--wizard"]
