"""Background process lifecycle helpers for core-managed services."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import subprocess
import sys
import time

from core.services.loopback_host_utils import is_loopback_host, normalize_loopback_host
from core.services.logging_api import get_logger, get_repo_root
from core.services.stdlib_http import HTTPError, http_get
from core.services.time_utils import parse_utc_datetime, utc_now

_WIZARD_DEFAULT_BASE_URL = "http://127.0.0.1:8765"
_WIZARD_START_CMD = ("uv", "run", "wizard/server.py", "--no-interactive")

logger = get_logger("background-service-manager")


@dataclass(slots=True)
class WizardServiceStatus:
    base_url: str
    running: bool
    connected: bool
    pid: int | None
    message: str
    health: dict[str, object]
    scheduler: dict[str, object] | None = None
    repair_summary: dict[str, object] | None = None


def _extract_host(url: str) -> str:
    value = (url or "").strip()
    if "://" in value:
        value = value.split("://", 1)[1]
    authority = value.split("/", 1)[0].strip()
    if "@" in authority:
        authority = authority.rsplit("@", 1)[1]
    if authority.startswith("["):
        return authority[1:].split("]", 1)[0].strip().lower()
    return authority.split(":", 1)[0].strip().lower()


def _assert_loopback_base_url(base_url: str) -> None:
    if is_loopback_host(_extract_host(base_url)):
        return
    raise ValueError(f"non-loopback target blocked: {base_url}")


class WizardProcessManager:
    """Manage Wizard lifecycle for on-demand core command execution."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.pid_file = self.repo_root / ".wizard.pid"
        self.log_file = self.repo_root / "memory" / "logs" / "wizard-daemon.log"

    def _load_wizard_runtime_config(self) -> dict[str, object]:
        config_path = self.repo_root / "wizard" / "config" / "wizard.json"
        if not config_path.exists():
            return {}
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _base_url(self, value: str | None = None) -> str:
        from core.services.unified_config_loader import get_config

        configured = (value or get_config("WIZARD_BASE_URL", "")).strip()
        if configured:
            base_url = configured.rstrip("/")
        else:
            config = self._load_wizard_runtime_config()
            host = normalize_loopback_host(
                str(config.get("host") or "127.0.0.1"),
                fallback="127.0.0.1",
            )
            port = int(config.get("port") or 8765)
            base_url = f"http://{host}:{port}"
        _assert_loopback_base_url(base_url)
        return base_url

    @staticmethod
    def _pid_alive(pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    def _read_pid(self) -> int | None:
        if not self.pid_file.exists():
            return None
        raw_pid = self.pid_file.read_text(encoding="utf-8").strip()
        if not raw_pid.isdigit():
            self._clear_pid()
            return None
        pid = int(raw_pid)
        if self._pid_alive(pid):
            return pid
        self._clear_pid()
        return None

    def _write_pid(self, pid: int) -> None:
        self.pid_file.write_text(f"{pid}\n", encoding="utf-8")

    def _clear_pid(self) -> None:
        self.pid_file.unlink(missing_ok=True)

    @staticmethod
    def _health(base_url: str, timeout: int = 2) -> tuple[bool, dict[str, object]]:
        try:
            response = http_get(f"{base_url}/health", timeout=timeout)
        except (HTTPError, OSError, ValueError):
            return False, {}
        payload = response.get("json") if isinstance(response, dict) else None
        data = payload if isinstance(payload, dict) else {}
        return response.get("status_code") == 200, data

    def _scheduler_status(self) -> dict[str, object]:
        try:
            db_path = self.repo_root / "memory" / "wizard" / "ops.db"
            if not db_path.exists():
                return {"healthy": False, "error": "scheduler store missing", "jobs": {}}
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT key, value
                    FROM scheduler_settings
                    WHERE key LIKE 'automation_heartbeat:%'
                    """
                ).fetchall()
            payloads = {
                str(row["key"]).replace("automation_heartbeat:", "", 1): json.loads(row["value"])
                for row in rows
                if row["value"]
            }
            now = utc_now()
            windows = {"run_due_tasks": 5, "health_snapshot": 15, "maintenance": 90}
            statuses = {}
            for job_name, grace_minutes in windows.items():
                payload = payloads.get(job_name) or {}
                last_success_raw = payload.get("last_success_at")
                last_success = (
                    parse_utc_datetime(last_success_raw)
                    if isinstance(last_success_raw, str) and last_success_raw
                    else None
                )
                overdue = last_success is None or (
                    now - last_success
                ).total_seconds() > (grace_minutes * 60)
                statuses[job_name] = {
                    "job": job_name,
                    "last_run_at": payload.get("last_run_at"),
                    "last_success_at": payload.get("last_success_at"),
                    "last_failure_at": payload.get("last_failure_at"),
                    "last_status": payload.get("last_status", "unknown"),
                    "overdue": overdue,
                }
        except Exception as exc:
            return {"healthy": False, "error": str(exc), "jobs": {}}

        run_due = statuses.get("run_due_tasks") or {}
        maintenance = statuses.get("maintenance") or {}
        healthy = not bool(run_due.get("overdue")) and run_due.get("last_status") != "failed"
        return {
            "healthy": healthy,
            "jobs": statuses,
            "run_due_tasks": run_due,
            "maintenance": maintenance,
        }

    def _run_self_heal(self) -> dict[str, object]:
        try:
            from core.services.self_healer import collect_self_heal_summary

            return collect_self_heal_summary(component="wizard", auto_repair=True)
        except Exception as exc:
            return {
                "success": False,
                "component": "wizard",
                "error": str(exc),
            }

    def _scheduler_command(self) -> list[str]:
        uv_bin = shutil.which("uv")
        if uv_bin:
            return [uv_bin, "run", "-m", "wizard.jobs.run_due_tasks"]
        return [sys.executable, "-m", "wizard.jobs.run_due_tasks"]

    def _kick_scheduler(self) -> dict[str, object]:
        command = self._scheduler_command()
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

    @staticmethod
    def _scheduler_ready(payload: dict[str, object] | None) -> bool:
        if not isinstance(payload, dict):
            return False
        return bool(payload.get("healthy"))

    def status(self, *, base_url: str | None = None) -> WizardServiceStatus:
        url = self._base_url(base_url)
        connected, health = self._health(url, timeout=2)
        pid = self._read_pid()
        scheduler = self._scheduler_status() if connected else None
        running = connected or pid is not None
        if connected:
            if self._scheduler_ready(scheduler):
                message = "wizard reachable"
            else:
                message = "wizard reachable but scheduler degraded"
        elif running:
            message = "wizard process running but not healthy"
        else:
            message = "wizard not running"
        return WizardServiceStatus(
            base_url=url,
            running=running,
            connected=connected,
            pid=pid,
            message=message,
            health=health,
            scheduler=scheduler,
        )

    def ensure_running(
        self,
        *,
        base_url: str | None = None,
        wait_seconds: int = 25,
        auto_repair: bool = False,
        require_scheduler: bool = False,
    ) -> WizardServiceStatus:
        status = self.status(base_url=base_url)
        if status.connected and (not require_scheduler or self._scheduler_ready(status.scheduler)):
            return status

        repair_summary = None
        if auto_repair and (not status.connected or (require_scheduler and not self._scheduler_ready(status.scheduler))):
            repair_summary = self._run_self_heal()

        if not status.running:
            self._start_process()

        deadline = time.monotonic() + max(1, wait_seconds)
        url = self._base_url(base_url)
        scheduler_kicked = False
        while time.monotonic() < deadline:
            connected, health = self._health(url, timeout=1)
            if connected:
                scheduler = self._scheduler_status()
                if require_scheduler and not self._scheduler_ready(scheduler):
                    if auto_repair and not scheduler_kicked:
                        self._kick_scheduler()
                        scheduler_kicked = True
                        time.sleep(0.25)
                        continue
                pid = self._read_pid()
                return WizardServiceStatus(
                    base_url=url,
                    running=True,
                    connected=True,
                    pid=pid,
                    message="wizard started" if self._scheduler_ready(scheduler) or not require_scheduler else "wizard started but scheduler degraded",
                    health=health,
                    scheduler=scheduler,
                    repair_summary=repair_summary,
                )
            time.sleep(0.25)

        latest = self.status(base_url=url)
        if latest.running:
            latest.message = "wizard start timeout"
        latest.repair_summary = repair_summary
        return latest

    def _start_process(self) -> int:
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with self.log_file.open("ab") as handle:
            proc = subprocess.Popen(
                list(_WIZARD_START_CMD),
                cwd=self.repo_root,
                stdin=subprocess.DEVNULL,
                stdout=handle,
                stderr=handle,
                start_new_session=os.name != "nt",
            )
        self._write_pid(proc.pid)
        logger.info("started wizard process pid=%s", proc.pid)
        return proc.pid

    def stop(self, *, base_url: str | None = None, timeout_seconds: int = 8) -> WizardServiceStatus:
        _ = self._base_url(base_url)
        pid = self._read_pid()
        if pid is None:
            self._clear_pid()
            return self.status(base_url=base_url)

        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            self._clear_pid()
            return self.status(base_url=base_url)

        deadline = time.monotonic() + max(1, timeout_seconds)
        while time.monotonic() < deadline:
            if not self._pid_alive(pid):
                self._clear_pid()
                return self.status(base_url=base_url)
            time.sleep(0.2)

        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
        self._clear_pid()
        return self.status(base_url=base_url)


_WIZARD_MANAGER: WizardProcessManager | None = None


def get_wizard_process_manager() -> WizardProcessManager:
    global _WIZARD_MANAGER
    if _WIZARD_MANAGER is None:
        _WIZARD_MANAGER = WizardProcessManager()
    return _WIZARD_MANAGER
