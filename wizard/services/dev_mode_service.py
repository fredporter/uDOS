"""
Dev Mode Service for Wizard Server.

Dev Mode is a /dev workspace runner exposed via Wizard GUI APIs.
It does not launch a separate TUI or standalone Goblin server.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from wizard.services.logging_api import get_logger
from wizard.services.workflow_manager import WorkflowManager
from wizard.services.vibe_service import VibeService
from wizard.services.ai_context_store import write_context_bundle


class DevModeService:
    """Manages Wizard dev workspace mode (/dev scripts/tests)."""

    def __init__(self, wizard_root: Optional[Path] = None):
        self.wizard_root = wizard_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("dev-mode-service")

        self.active = False
        self.start_time: Optional[float] = None
        self.services_status = {
            "dev_workspace": False,
            "script_runner": False,
            "test_runner": False,
            "workflow_manager": False,
            "github_integration": False,
            "dashboard_watch": False,
        }

        self._dev_requirements_cache: Optional[Dict[str, Any]] = None
        self._dev_requirements_checked_at: Optional[float] = None
        self.dashboard_watch_process: Optional[subprocess.Popen] = None

    def _dev_root(self) -> Path:
        return self.wizard_root / "dev"

    def _scripts_root(self) -> Path:
        return self._dev_root() / "goblin" / "scripts"

    def _tests_root(self) -> Path:
        return self._dev_root() / "goblin" / "tests"

    def _sandbox_root(self) -> Path:
        return self._dev_root() / "goblin" / "wizard-sandbox"

    def _goblin_root(self) -> Path:
        return self._dev_root() / "goblin"

    def _dev_commands_manifest(self) -> Path:
        return self._goblin_root() / "dev_mode_commands.json"

    def get_dev_commands_manifest(self) -> Dict[str, Any]:
        path = self._dev_commands_manifest()
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def _dev_template_present(self) -> bool:
        dev_root = self._dev_root()
        if not dev_root.exists():
            return False
        markers = [
            self._scripts_root(),
            self._tests_root(),
            self._sandbox_root(),
            dev_root / "goblin" / "README.md",
            self._dev_commands_manifest(),
            dev_root / "README.md",
        ]
        return any(path.exists() for path in markers)

    def _ensure_goblin_scaffold(self) -> None:
        goblin_root = self._goblin_root()
        scripts = self._scripts_root()
        tests = self._tests_root()
        sandbox = self._sandbox_root()

        scripts.mkdir(parents=True, exist_ok=True)
        tests.mkdir(parents=True, exist_ok=True)
        sandbox.mkdir(parents=True, exist_ok=True)

        readme = goblin_root / "README.md"
        if not readme.exists():
            readme.write_text(
                "# Goblin Dev Scaffold\n\n"
                "Wizard dev mode uses this scaffold for development execution.\n"
                "- scripts/: runnable dev scripts\n"
                "- tests/: runnable dev tests\n"
                "- wizard-sandbox/: GUI-bound dev outputs\n",
                encoding="utf-8",
            )

    def _allowed_script(self, path: Path) -> bool:
        return path.suffix.lower() in {".sh", ".py"}

    def _allowed_test(self, path: Path) -> bool:
        suffix = path.suffix.lower()
        return suffix in {".py", ".sh"} and path.name.startswith("test_")

    def _safe_resolve(self, root: Path, rel_path: str) -> Optional[Path]:
        if not rel_path:
            return None
        candidate = (root / rel_path).resolve()
        if not str(candidate).startswith(str(root.resolve())):
            return None
        return candidate

    def _append_dev_log(self, message: str) -> None:
        try:
            log_dir = self.wizard_root / "memory" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "dev-mode.log"
            ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(f"[{ts}] {message}\n")
        except Exception:
            pass

    def check_requirements(self, force: bool = False) -> Dict[str, Any]:
        now = time.time()
        if (
            not force
            and self._dev_requirements_cache
            and self._dev_requirements_checked_at
            and now - self._dev_requirements_checked_at < 10
        ):
            return self._dev_requirements_cache

        dev_root = self._dev_root()
        scripts_root = self._scripts_root()
        tests_root = self._tests_root()
        sandbox_root = self._sandbox_root()

        present = self._dev_template_present()
        script_count = (
            sum(1 for path in scripts_root.rglob("*") if path.is_file() and self._allowed_script(path))
            if scripts_root.exists()
            else 0
        )
        test_count = (
            sum(1 for path in tests_root.rglob("*") if path.is_file() and self._allowed_test(path))
            if tests_root.exists()
            else 0
        )

        self._dev_requirements_cache = {
            "dev_root": str(dev_root),
            "dev_root_present": dev_root.exists(),
            "dev_template_present": present,
            "scripts_root": str(scripts_root),
            "tests_root": str(tests_root),
            "sandbox_root": str(sandbox_root),
            "goblin_root": str(self._goblin_root()),
            "dev_commands_manifest": str(self._dev_commands_manifest()),
            "dev_commands_manifest_present": self._dev_commands_manifest().exists(),
            "script_count": script_count,
            "test_count": test_count,
            "goblin_scaffold_ready": (
                scripts_root.exists() and tests_root.exists() and sandbox_root.exists()
            ),
        }
        self._dev_requirements_checked_at = now
        return self._dev_requirements_cache

    def ensure_requirements(self) -> Optional[str]:
        req = self.check_requirements(force=True)
        if not req.get("dev_root_present"):
            return "Dev submodule not present (/dev missing). Clone github.com/fredporter/uDOS-dev."
        if not req.get("dev_template_present"):
            return "Dev submodule is missing required templates. Re-clone or update /dev."
        if not req.get("dev_commands_manifest_present"):
            return "Dev command manifest missing (/dev/goblin/dev_mode_commands.json)."
        self._ensure_goblin_scaffold()
        refreshed = self.check_requirements(force=True)
        if not refreshed.get("goblin_scaffold_ready"):
            return "Dev submodule scaffold is incomplete (/dev/goblin/scripts, tests, wizard-sandbox required)."
        return None

    def ensure_active(self) -> Optional[str]:
        if not self.active:
            return "Dev mode is not active. Activate dev mode from Wizard GUI or run DEV ON in uCLI."
        return None

    def activate(self) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}

        if self.active:
            return {
                "status": "already_active",
                "message": "Dev mode is already active",
                "uptime_seconds": int(time.time() - self.start_time) if self.start_time else 0,
            }

        self.active = True
        self.start_time = time.time()
        self.services_status["dev_workspace"] = True
        self.services_status["script_runner"] = True
        self.services_status["test_runner"] = True

        self._start_dashboard_watch()

        workflow = WorkflowManager()
        round_name = f"Dev Milestone {datetime.now().strftime('%Y-%m-%d')}"
        workflow.get_or_create_project(
            round_name,
            description="Auto-created when DEV MODE is activated.",
        )
        self.services_status["workflow_manager"] = True

        self._append_dev_log("Dev mode activated")

        return {
            "status": "activated",
            "message": "Dev mode activated: /dev scripts/tests available in Wizard GUI",
            "dev_root": str(self._dev_root()),
            "timestamp": datetime.now().isoformat(),
        }

    def clear(self) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}
        active_error = self.ensure_active()
        if active_error:
            return {"status": "error", "message": active_error}

        self.logger.info("[WIZ-DEV] Clearing dev mode caches/rebuilds...")
        results: Dict[str, Any] = {"status": "cleared", "actions": []}

        try:
            write_context_bundle()
            results["actions"].append({"context": "refreshed"})
        except Exception as exc:
            results["actions"].append({"context": f"error: {exc}"})

        dashboard_dir = self.wizard_root / "wizard" / "dashboard"
        dist_path = dashboard_dir / "dist" / "index.html"
        rebuild = False
        if not dist_path.exists():
            rebuild = True
        else:
            try:
                for path in (dashboard_dir / "src").rglob("*"):
                    if path.is_file() and path.stat().st_mtime > dist_path.stat().st_mtime:
                        rebuild = True
                        break
            except Exception:
                rebuild = True

        if rebuild:
            try:
                subprocess.run(
                    ["npm", "install", "--no-fund", "--no-audit"],
                    cwd=str(dashboard_dir),
                    check=True,
                )
                subprocess.run(["npm", "run", "build"], cwd=str(dashboard_dir), check=True)
                results["actions"].append({"dashboard": "rebuilt"})
            except Exception as exc:
                results["actions"].append({"dashboard": f"error: {exc}"})

        self._append_dev_log("Dev mode clear completed")
        return results

    def _start_dashboard_watch(self) -> None:
        if self.dashboard_watch_process and self.dashboard_watch_process.poll() is None:
            return

        dashboard_dir = self.wizard_root / "wizard" / "dashboard"
        package_json = dashboard_dir / "package.json"
        if not package_json.exists():
            return

        try:
            self.dashboard_watch_process = subprocess.Popen(
                ["npm", "run", "build", "--", "--watch"],
                cwd=str(dashboard_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.services_status["dashboard_watch"] = True
            self.logger.info("[WIZ-DEV] Dashboard build watcher started")
        except Exception as exc:
            self.services_status["dashboard_watch"] = False
            self.logger.warning(f"[WIZ-DEV] Failed to start dashboard watch: {exc}")

    def suggest_next_steps(self) -> str:
        try:
            vibe = VibeService()
            context = vibe.load_default_context()
            prompt = (
                "Suggest the next 3-5 development steps for uDOS. "
                "Consider devlog, roadmap, and recent logs."
            )
            return vibe.generate(prompt=prompt, system=context)
        except Exception as exc:
            return f"Failed to generate suggestions: {exc}"

    def deactivate(self) -> Dict[str, Any]:
        if not self.active:
            return {"status": "not_active", "message": "Dev mode is not active"}

        try:
            if self.dashboard_watch_process:
                self.logger.info("[WIZ-DEV] Stopping dashboard watcher")
                self.dashboard_watch_process.terminate()
                try:
                    self.dashboard_watch_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.dashboard_watch_process.kill()
                    self.dashboard_watch_process.wait()

            self.active = False
            self.start_time = None
            self.dashboard_watch_process = None
            self.services_status = {k: False for k in self.services_status}
            self._append_dev_log("Dev mode deactivated")

            return {
                "status": "deactivated",
                "message": "Dev mode deactivated successfully",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as exc:
            self.logger.error(f"[WIZ-DEV] Failed to deactivate dev mode: {exc}")
            return {"status": "error", "message": str(exc)}

    def get_status(self) -> Dict[str, Any]:
        uptime_seconds = int(time.time() - self.start_time) if self.active and self.start_time else 0
        if self.dashboard_watch_process and self.dashboard_watch_process.poll() is not None:
            self.logger.warning("[WIZ-DEV] Dashboard watch process has exited unexpectedly")
            self.dashboard_watch_process = None
            self.services_status["dashboard_watch"] = False

        requirements = self.check_requirements(force=False)

        return {
            "active": self.active,
            "uptime_seconds": uptime_seconds,
            "dev_root": str(self._dev_root()),
            "goblin_root": str(self._goblin_root()),
            "scripts_root": str(self._scripts_root()),
            "tests_root": str(self._tests_root()),
            "sandbox_root": str(self._sandbox_root()),
            "services": self.services_status,
            "requirements": requirements,
            "dev_commands": self.get_dev_commands_manifest(),
            "timestamp": datetime.now().isoformat(),
        }

    def get_logs(self, lines: int = 50) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}
        active_error = self.ensure_active()
        if active_error:
            return {"status": "error", "message": active_error}

        log_file = self.wizard_root / "memory" / "logs" / "dev-mode.log"
        logs: List[str] = []
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as handle:
                    all_lines = handle.readlines()
                    logs = [line.rstrip() for line in all_lines[-max(0, lines):]]
            except Exception as exc:
                logs = [f"Error reading logs: {exc}"]

        return {
            "status": "running" if self.active else "inactive",
            "log_file": str(log_file),
            "logs": logs,
            "total_lines": len(logs),
        }

    def restart(self) -> Dict[str, Any]:
        deactivate_result = self.deactivate()
        if deactivate_result["status"] == "error":
            return deactivate_result
        time.sleep(1)
        return self.activate()

    def get_health(self) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "healthy": False, "message": requirements_error}

        if not self.active:
            return {
                "status": "inactive",
                "healthy": False,
                "message": "Dev mode inactive. Activate to run /dev operations.",
            }

        scripts_ok = self._scripts_root().exists()
        tests_ok = self._tests_root().exists()
        healthy = scripts_ok or tests_ok

        return {
            "status": "active",
            "healthy": healthy,
            "services": {
                "dev_workspace": {
                    "status": "healthy" if healthy else "unhealthy",
                    "scripts_root": str(self._scripts_root()),
                    "tests_root": str(self._tests_root()),
                    "sandbox_root": str(self._sandbox_root()),
                }
            },
        }

    def list_scripts(self) -> List[str]:
        if self.ensure_requirements() or self.ensure_active():
            return []
        root = self._scripts_root()
        if not root.exists():
            return []
        out: List[str] = []
        for path in sorted(root.rglob("*")):
            if path.is_file() and self._allowed_script(path):
                out.append(str(path.relative_to(root)))
        return out

    def list_tests(self) -> List[str]:
        if self.ensure_requirements() or self.ensure_active():
            return []
        root = self._tests_root()
        if not root.exists():
            return []
        out: List[str] = []
        for path in sorted(root.rglob("*")):
            if path.is_file() and self._allowed_test(path):
                out.append(str(path.relative_to(root)))
        return out

    def run_script(self, rel_path: str, args: Optional[List[str]] = None, timeout: int = 300) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}
        active_error = self.ensure_active()
        if active_error:
            return {"status": "error", "message": active_error}

        script = self._safe_resolve(self._scripts_root(), rel_path)
        if not script or not script.exists() or not script.is_file() or not self._allowed_script(script):
            return {"status": "error", "message": f"Script not allowed: {rel_path}"}

        cmd = ["python", str(script)] if script.suffix.lower() == ".py" else ["bash", str(script)]
        if args:
            cmd.extend(args)

        self._append_dev_log(f"RUN SCRIPT: {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.wizard_root),
                capture_output=True,
                text=True,
                timeout=max(10, timeout),
            )
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "command": cmd,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def run_tests(self, rel_path: Optional[str] = None, args: Optional[List[str]] = None, timeout: int = 600) -> Dict[str, Any]:
        requirements_error = self.ensure_requirements()
        if requirements_error:
            return {"status": "error", "message": requirements_error}
        active_error = self.ensure_active()
        if active_error:
            return {"status": "error", "message": active_error}

        args = args or []
        if rel_path:
            test_path = self._safe_resolve(self._tests_root(), rel_path)
            if not test_path or not test_path.exists() or not test_path.is_file() or not self._allowed_test(test_path):
                return {"status": "error", "message": f"Test not allowed: {rel_path}"}

            if test_path.suffix.lower() == ".sh":
                cmd = ["bash", str(test_path)] + args
            else:
                cmd = ["python", "-m", "pytest", str(test_path)] + args
        else:
            cmd = ["python", "-m", "pytest", str(self._tests_root())] + args

        self._append_dev_log(f"RUN TESTS: {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.wizard_root),
                capture_output=True,
                text=True,
                timeout=max(30, timeout),
            )
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "command": cmd,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        except Exception as exc:
            return {"status": "error", "message": str(exc)}


_dev_mode_service: Optional[DevModeService] = None


def get_dev_mode_service() -> DevModeService:
    global _dev_mode_service
    if _dev_mode_service is None:
        _dev_mode_service = DevModeService()
    return _dev_mode_service
