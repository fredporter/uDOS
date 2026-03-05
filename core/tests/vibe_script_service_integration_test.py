"""Integration-style tests for VibeScriptService execution and recovery."""

from __future__ import annotations

import subprocess
from pathlib import Path

from core.services.dev_mode_compat.script_service import VibeScriptService


def test_run_script_python_success(tmp_path: Path) -> None:
    service = VibeScriptService(script_root=tmp_path)
    script = tmp_path / "hello.py"
    script.write_text("print('hello from script')\n")

    result = service.run_script("hello")

    assert result["status"] == "success"
    assert result["exit_code"] == 0
    assert "hello from script" in result["output"]


def test_run_script_failure_then_recovery(monkeypatch, tmp_path: Path) -> None:
    service = VibeScriptService(script_root=tmp_path)
    script = tmp_path / "task.sh"
    script.write_text("#!/bin/sh\nexit 0\n")
    script.chmod(0o755)

    fail = subprocess.CompletedProcess(
        args=[str(script)],
        returncode=2,
        stdout="",
        stderr="boom",
    )
    ok = subprocess.CompletedProcess(
        args=[str(script)],
        returncode=0,
        stdout="ok",
        stderr="",
    )

    monkeypatch.setattr(
        "core.services.dev_mode_compat.script_service.subprocess.run",
        lambda *args, **kwargs: fail,
    )
    first = service.run_script("task")

    monkeypatch.setattr(
        "core.services.dev_mode_compat.script_service.subprocess.run",
        lambda *args, **kwargs: ok,
    )
    second = service.run_script("task")

    assert first["status"] == "error"
    assert first["exit_code"] == 2
    assert second["status"] == "success"
    assert second["exit_code"] == 0


def test_run_script_timeout_returns_error(monkeypatch, tmp_path: Path) -> None:
    service = VibeScriptService(script_root=tmp_path)
    script = tmp_path / "slow.sh"
    script.write_text("#!/bin/sh\nsleep 1\n")
    script.chmod(0o755)

    def _raise_timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd=["slow.sh"], timeout=120)

    monkeypatch.setattr(
        "core.services.dev_mode_compat.script_service.subprocess.run",
        _raise_timeout,
    )

    result = service.run_script("slow")
    assert result["status"] == "error"
    assert "timed out" in result["message"].lower()
