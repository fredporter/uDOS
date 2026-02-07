"""
Dev Mode Service for Wizard Server.

Manages dev mode activation/deactivation.
Coordinates Goblin dev server, monitoring, and API availability.

Dev Mode includes:
- Goblin Dev Server (localhost:8767)
- Task scheduling, runtime executor
- Real-time WebSocket updates
- TUI interface for monitoring
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from wizard.services.logging_manager import get_logger
from wizard.services.workflow_manager import WorkflowManager
from wizard.services.vibe_service import VibeService
from wizard.services.ai_context_store import write_context_bundle


class DevModeService:
    """Manages Wizard dev mode (Goblin + services coordination)."""

    def __init__(self, wizard_root: Optional[Path] = None):
        """Initialize dev mode service."""
        self.wizard_root = wizard_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("dev-mode-service")

        self.goblin_process: Optional[subprocess.Popen] = None
        self.goblin_port = 8767
        self.goblin_host = "127.0.0.1"

        self.active = False
        self.start_time: Optional[float] = None
        self.services_status = {
            "goblin": False,
            "runtime_executor": False,
            "task_scheduler": False,
            "workflow_manager": False,
            "github_integration": False,
        }

    def activate(self) -> Dict[str, Any]:
        """Activate dev mode (start Goblin dev server)."""
        if self.active:
            return {
                "status": "already_active",
                "message": "Dev mode is already active",
                "uptime_seconds": (
                    int(time.time() - self.start_time) if self.start_time else 0
                ),
            }

        self.logger.info("[WIZ-DEV] Activating dev mode...")

        try:
            # Start Goblin dev server
            goblin_script = self.wizard_root / "dev" / "goblin" / "goblin_server.py"
            if not goblin_script.exists():
                self.logger.error(f"[WIZ-DEV] Goblin script not found: {goblin_script}")
                return {
                    "status": "error",
                    "message": f"Goblin dev server not found at {goblin_script}",
                }

            self.logger.info(
                f"[WIZ-DEV] Starting Goblin dev server from {goblin_script}"
            )

            self.goblin_process = subprocess.Popen(
                ["python", str(goblin_script)],
                cwd=str(self.wizard_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait briefly for startup
            time.sleep(2)

            # Check if process started successfully
            if self.goblin_process.poll() is not None:
                stdout, stderr = self.goblin_process.communicate()
                self.logger.error(f"[WIZ-DEV] Goblin startup failed: {stderr}")
                return {
                    "status": "error",
                    "message": f"Goblin dev server failed to start: {stderr}",
                }

            self.active = True
            self.start_time = time.time()
            self.services_status["goblin"] = True

            # Create a Dev Milestone project for task tracking
            workflow = WorkflowManager()
            round_name = f"Dev Milestone {datetime.now().strftime('%Y-%m-%d')}"
            workflow.get_or_create_project(
                round_name,
                description="Auto-created when DEV MODE is activated.",
            )

            self.logger.info(
                f"[WIZ-DEV] Dev mode activated. Goblin running on {self.goblin_host}:{self.goblin_port}"
            )

            return {
                "status": "activated",
                "message": "Dev mode activated successfully",
                "goblin_endpoint": f"http://{self.goblin_host}:{self.goblin_port}",
                "goblin_pid": self.goblin_process.pid,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as exc:
            self.logger.error(f"[WIZ-DEV] Failed to activate dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def clear(self) -> Dict[str, Any]:
        """Clear dev mode caches and trigger rebuild tasks."""
        self.logger.info("[WIZ-DEV] Clearing dev mode caches/rebuilds...")
        results: Dict[str, Any] = {"status": "cleared", "actions": []}

        # Refresh AI context bundle
        try:
            write_context_bundle()
            results["actions"].append({"context": "refreshed"})
        except Exception as exc:
            results["actions"].append({"context": f"error: {exc}"})

        # Rebuild wizard dashboard if needed
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
                subprocess.run(
                    ["npm", "run", "build"],
                    cwd=str(dashboard_dir),
                    check=True,
                )
                results["actions"].append({"dashboard": "rebuilt"})
            except Exception as exc:
                results["actions"].append({"dashboard": f"error: {exc}"})

        return results

    def suggest_next_steps(self) -> str:
        """Generate next-step suggestions using local Vibe (Ollama)."""
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
        """Deactivate dev mode (stop Goblin dev server)."""
        if not self.active:
            return {
                "status": "not_active",
                "message": "Dev mode is not active",
            }

        self.logger.info("[WIZ-DEV] Deactivating dev mode...")

        try:
            if self.goblin_process:
                self.logger.info(
                    f"[WIZ-DEV] Stopping Goblin (PID {self.goblin_process.pid})"
                )
                self.goblin_process.terminate()

                try:
                    self.goblin_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.logger.warning(
                        "[WIZ-DEV] Goblin did not stop gracefully, killing..."
                    )
                    self.goblin_process.kill()
                    self.goblin_process.wait()

            self.active = False
            self.start_time = None
            self.goblin_process = None
            self.services_status = {k: False for k in self.services_status}

            self.logger.info("[WIZ-DEV] Dev mode deactivated")

            return {
                "status": "deactivated",
                "message": "Dev mode deactivated successfully",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as exc:
            self.logger.error(f"[WIZ-DEV] Failed to deactivate dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def get_status(self) -> Dict[str, Any]:
        """Get dev mode status."""
        uptime_seconds = 0
        if self.active and self.start_time:
            uptime_seconds = int(time.time() - self.start_time)

        # Check if Goblin process is still running
        if self.goblin_process and self.goblin_process.poll() is not None:
            # Process has exited
            self.logger.warning("[WIZ-DEV] Goblin process has exited unexpectedly")
            self.active = False
            self.goblin_process = None
            self.services_status["goblin"] = False

        return {
            "active": self.active,
            "uptime_seconds": uptime_seconds,
            "goblin_endpoint": (
                f"http://{self.goblin_host}:{self.goblin_port}" if self.active else None
            ),
            "goblin_pid": self.goblin_process.pid if self.goblin_process else None,
            "services": self.services_status,
            "timestamp": datetime.now().isoformat(),
        }

    def get_logs(self, lines: int = 50) -> Dict[str, Any]:
        """Get Goblin dev server logs."""
        if not self.goblin_process:
            return {
                "status": "not_running",
                "logs": [],
            }

        # Try to read from dev logs directory
        log_dir = self.wizard_root / "memory" / "logs"
        goblin_log = log_dir / "goblin-dev.log"

        logs = []
        if goblin_log.exists():
            try:
                with open(goblin_log, "r") as f:
                    all_lines = f.readlines()
                    logs = [line.rstrip() for line in all_lines[-lines:]]
            except Exception as exc:
                self.logger.error(f"[WIZ-DEV] Failed to read logs: {exc}")
                logs = [f"Error reading logs: {exc}"]

        return {
            "status": "running",
            "goblin_pid": self.goblin_process.pid,
            "log_file": str(goblin_log),
            "logs": logs,
            "total_lines": len(logs),
        }

    def restart(self) -> Dict[str, Any]:
        """Restart dev mode."""
        self.logger.info("[WIZ-DEV] Restarting dev mode...")
        deactivate_result = self.deactivate()
        if deactivate_result["status"] == "error":
            return deactivate_result

        time.sleep(1)
        return self.activate()

    def get_health(self) -> Dict[str, Any]:
        """Check dev mode health."""
        if not self.active:
            return {
                "status": "inactive",
                "healthy": False,
            }

        health = {
            "status": "active",
            "healthy": True,
            "services": {},
        }

        # Check Goblin endpoint
        try:
            import requests

            response = requests.get(
                f"http://{self.goblin_host}:{self.goblin_port}/health",
                timeout=2,
            )
            health["services"]["goblin"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_code": response.status_code,
            }
            if response.status_code != 200:
                health["healthy"] = False
        except Exception as exc:
            health["services"]["goblin"] = {
                "status": "unreachable",
                "error": str(exc),
            }
            health["healthy"] = False

        return health


_dev_mode_service: Optional[DevModeService] = None


def get_dev_mode_service() -> DevModeService:
    global _dev_mode_service
    if _dev_mode_service is None:
        _dev_mode_service = DevModeService()
    return _dev_mode_service
