"""Canonical v1.5 launcher service for local uDOS operations."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from core.services.background_service_manager import get_wizard_process_manager
from core.services.self_healer import collect_self_heal_summary
from wizard.services.launch_session_service import get_launch_session_service
from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root
from wizard.services.port_manager import get_port_manager
from wizard.services.wizard_config import (
    load_wizard_config_data,
    save_wizard_config_data,
)

_log = get_logger("wizard", category="launcher")


@dataclass(slots=True)
class LauncherResult:
    success: bool
    action: str
    message: str
    details: dict[str, Any]
    exit_code: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "message": self.message,
            "details": self.details,
            "exit_code": self.exit_code,
        }


class UdosLauncherService:
    """Single local entrypoint for launcher, repair, and runtime ops."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.sessions = get_launch_session_service(repo_root=self.repo_root)
        self.process_manager = get_wizard_process_manager()
        self.port_manager = get_port_manager()

    def status(self) -> LauncherResult:
        wizard_status = self.process_manager.status()
        self.port_manager.check_all_services()
        conflicts = [
            {
                "service": name,
                "process": occupant.get("process"),
                "pid": occupant.get("pid"),
                "port": occupant.get("port"),
            }
            for name, occupant in self.port_manager.get_conflicts()
        ]
        details = {
            "repo_root": str(self.repo_root),
            "wizard": {
                "base_url": wizard_status.base_url,
                "running": wizard_status.running,
                "connected": wizard_status.connected,
                "pid": wizard_status.pid,
                "message": wizard_status.message,
            },
            "port_conflicts": conflicts,
        }
        return LauncherResult(
            success=wizard_status.connected or not conflicts,
            action="status",
            message="uDOS runtime status collected",
            details=details,
        )

    def start_runtime(
        self,
        *,
        auto_repair: bool = True,
        wait_seconds: int = 25,
    ) -> LauncherResult:
        session = self.sessions.create_session(
            target="udos-runtime",
            mode="start",
            launcher="udos",
            workspace="@dev" if self._dev_mode_active() else "core",
            state="planned",
        )
        self.sessions.transition(session["session_id"], "starting")
        repair_details: dict[str, Any] = {}
        if auto_repair:
            repair_details = self._repair_ports()
        wizard_status = self.process_manager.ensure_running(
            wait_seconds=wait_seconds,
            auto_repair=auto_repair,
            require_scheduler=True,
        )
        state = "ready" if wizard_status.connected else "error"
        self.sessions.transition(
            session["session_id"],
            state,
            error=None if wizard_status.connected else wizard_status.message,
            updates={"wizard_base_url": wizard_status.base_url},
        )
        success = wizard_status.connected
        message = (
            f"uDOS runtime ready at {wizard_status.base_url}"
            if success
            else f"uDOS runtime unavailable: {wizard_status.message}"
        )
        return LauncherResult(
            success=success,
            action="start",
            message=message,
            details={
                "session_id": session["session_id"],
                "wizard": {
                    "base_url": wizard_status.base_url,
                    "running": wizard_status.running,
                    "connected": wizard_status.connected,
                    "pid": wizard_status.pid,
                    "message": wizard_status.message,
                },
                "repair": repair_details,
            },
            exit_code=0 if success else 1,
        )

    def repair_runtime(self) -> LauncherResult:
        repair_details = self._repair_ports()
        wizard_summary = collect_self_heal_summary(component="wizard", auto_repair=True)
        wizard_status = self.process_manager.ensure_running(
            wait_seconds=25,
            auto_repair=True,
            require_scheduler=True,
        )
        success = wizard_status.connected and wizard_summary.get("success", False)
        return LauncherResult(
            success=success,
            action="repair",
            message="uDOS repair complete" if success else "uDOS repair needs attention",
            details={
                "repair": repair_details,
                "self_heal": wizard_summary,
                "wizard": {
                    "base_url": wizard_status.base_url,
                    "connected": wizard_status.connected,
                    "pid": wizard_status.pid,
                    "message": wizard_status.message,
                },
            },
            exit_code=0 if success else 1,
        )

    def rebuild_runtime(self) -> LauncherResult:
        commands: list[list[str]] = [
            ["uv", "sync", "--extra", "udos-wizard", "--dev"],
        ]
        build_script = self.repo_root / "scripts" / "build_udos_tui.sh"
        if build_script.exists():
            commands.append(["bash", str(build_script)])
        completed: list[dict[str, Any]] = []
        for command in commands:
            completed.append(self._run(command))
        success = all(item["returncode"] == 0 for item in completed)
        return LauncherResult(
            success=success,
            action="rebuild",
            message="uDOS rebuild complete" if success else "uDOS rebuild failed",
            details={"commands": completed},
            exit_code=0 if success else 1,
        )

    def update_from_remote(
        self,
        *,
        remote: str = "origin",
        branch: str = "main",
    ) -> LauncherResult:
        if not (self.repo_root / ".git").exists():
            return LauncherResult(
                success=False,
                action="update",
                message="git metadata not found in repo root",
                details={"repo_root": str(self.repo_root)},
                exit_code=1,
            )
        completed = [
            self._run(["git", "fetch", remote, "--prune"]),
            self._run(["git", "pull", "--ff-only", remote, branch]),
        ]
        success = all(item["returncode"] == 0 for item in completed)
        return LauncherResult(
            success=success,
            action="update",
            message="uDOS updated from remote" if success else "uDOS update failed",
            details={"commands": completed, "remote": remote, "branch": branch},
            exit_code=0 if success else 1,
        )

    def install_runtime(self, extra_args: list[str]) -> int:
        script = self.repo_root / "bin" / "install-udos.sh"
        os.execv("/bin/bash", ["/bin/bash", str(script), *extra_args])
        raise AssertionError("unreachable")

    def _bubbletea_binary(self) -> Path:
        return self.repo_root / "tui" / "bin" / "udos-tui"

    def _build_bubbletea_tui(self) -> bool:
        build_script = self.repo_root / "scripts" / "build_udos_tui.sh"
        if not build_script.exists():
            return False
        if not shutil.which("go"):
            return False
        result = subprocess.run(
            ["/bin/bash", str(build_script)],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            _log.warning(
                "Bubble Tea TUI build failed; falling back to core TUI",
                extra={
                    "returncode": result.returncode,
                    "stderr": (result.stderr or "").strip()[-500:],
                },
            )
            return False
        return True

    def launch_tui(self, extra_args: list[str]) -> int:
        bubbletea = self._bubbletea_binary()
        if not (bubbletea.exists() and os.access(bubbletea, os.X_OK)):
            self._build_bubbletea_tui()

        if bubbletea.exists() and os.access(bubbletea, os.X_OK):
            os.execv(str(bubbletea), [str(bubbletea), *extra_args])
            raise AssertionError("unreachable")

        raise RuntimeError(
            "uDOS v1.5 Bubble Tea TUI is unavailable. "
            "Run ./bin/udos install --update, or install Go 1.22+ and run ./scripts/build_udos_tui.sh."
        )

    def launch_ops(self, extra_args: list[str]) -> int:
        result = self.start_runtime(auto_repair=True, wait_seconds=25)
        if not result.success:
            return result.exit_code
        return self.launch_tui(extra_args)

    def wizard_command(self, command: str) -> LauncherResult:
        if command == "start":
            return self.start_runtime(auto_repair=True)
        if command == "status":
            return self.status()
        if command == "health":
            status = self.process_manager.status()
            return LauncherResult(
                success=status.connected,
                action="wizard-health",
                message="Wizard healthy" if status.connected else "Wizard unavailable",
                details={"wizard": status.__dict__},
                exit_code=0 if status.connected else 1,
            )
        if command == "stop":
            status = self.process_manager.stop()
            return LauncherResult(
                success=not status.running,
                action="wizard-stop",
                message="Wizard stopped" if not status.running else "Wizard stop incomplete",
                details={"wizard": status.__dict__},
                exit_code=0 if not status.running else 1,
            )
        if command == "restart":
            _ = self.process_manager.stop()
            return self.start_runtime(auto_repair=True)
        if command == "logs":
            path = self.process_manager.log_file
            text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
            return LauncherResult(
                success=True,
                action="wizard-logs",
                message="Wizard logs",
                details={"path": str(path), "tail": "\n".join(text.splitlines()[-120:])},
            )
        return LauncherResult(
            success=False,
            action="wizard",
            message=f"Unsupported wizard command: {command}",
            details={},
            exit_code=2,
        )

    def _dev_mode_active(self) -> bool:
        try:
            from wizard.services.dev_mode_service import get_dev_mode_service

            return bool(get_dev_mode_service().get_status().get("active"))
        except Exception:
            return False

    def _repair_ports(self) -> dict[str, Any]:
        self.port_manager.check_all_services()
        conflicts = self.port_manager.get_conflicts()
        healed = self.port_manager.heal_conflicts() if conflicts else {}
        remaining = self.port_manager.get_conflicts()
        reassigned = None
        if any(name == "wizard" for name, _occupant in remaining):
            reassigned = self._reassign_wizard_port()
            self.port_manager.check_all_services()
            remaining = self.port_manager.get_conflicts()
        return {
            "conflicts": [
                {"service": name, "process": occupant.get("process"), "pid": occupant.get("pid")}
                for name, occupant in conflicts
            ],
            "healed": healed,
            "remaining": [
                {"service": name, "process": occupant.get("process"), "pid": occupant.get("pid")}
                for name, occupant in remaining
            ],
            "wizard_reassigned": reassigned,
        }

    def _reassign_wizard_port(self) -> dict[str, Any] | None:
        service = self.port_manager.services.get("wizard")
        if service is None or service.port is None:
            return None
        old_port = service.port
        new_port = self.port_manager.get_available_port(old_port + 1)
        config = load_wizard_config_data()
        config["port"] = new_port
        save_wizard_config_data(config)
        self.port_manager.reassign_port("wizard", new_port)
        _log.info("reassigned wizard port", ctx={"old_port": old_port, "new_port": new_port})
        return {"old_port": old_port, "new_port": new_port}

    def _run(self, command: list[str]) -> dict[str, Any]:
        proc = subprocess.run(
            command,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        return {
            "command": command,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }


def get_udos_launcher_service(repo_root: Path | None = None) -> UdosLauncherService:
    return UdosLauncherService(repo_root=repo_root)
