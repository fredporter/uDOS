"""DEV MODE command handler - Activate/deactivate development mode via Wizard Server."""

from typing import List, Dict, Optional
from pathlib import Path
import requests
import json

try:
    from wizard.services.logging_manager import get_logger
    from wizard.services.rate_limiter import rate_limiter
except ImportError:
    # Fallback if wizard module not available
    import logging

    logger = logging.getLogger("dev-mode-handler")

    class _NoopRateLimiter:
        def allow(self, endpoint: str, provider: str = "wizard-api") -> bool:
            return True

    rate_limiter = _NoopRateLimiter()
else:
    logger = get_logger("dev-mode-handler")

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit


class DevModeHandler(BaseCommandHandler):
    """Handler for DEV MODE command - managed by Wizard Server."""

    def __init__(self):
        """Initialize dev mode handler."""
        super().__init__()
        self.wizard_host = "127.0.0.1"
        self.wizard_port = 8765

    def _throttle_guard(self, endpoint: str) -> Optional[Dict]:
        """Return throttle response when rate limit exceeded."""
        if not rate_limiter.allow(endpoint, provider="wizard-api"):
            message = f"Rate limit reached for {endpoint} (momentary window)."
            return {
                "status": "throttled",
                "message": message,
                "output": (
                    "⚠️ You're hitting the Wizard API too fast. "
                    "Wait a few seconds and try again."
                ),
                "hint": "Reduce dev mode toggles or wait for rate limit window to reset.",
            }
        return None

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle DEV MODE command.

        Args:
            command: Command name (DEV MODE)
            params: [activate|deactivate|status|restart|logs] (default: status)
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with dev mode status
        """
        output = "\n".join(
            [
                OutputToolkit.banner("DEV MODE"),
                "Dev Mode operations are handled by Wizard TUI.",
                "Run the Wizard server and use its TUI console for DEV ON/OFF.",
            ]
        )
        return {
            "status": "wizard_required",
            "message": "Run Wizard server for DEV mode operations",
            "output": output,
        }

    def _activate_dev_mode(self) -> Dict:
        """Activate dev mode via Wizard."""
        try:
            guard = self._throttle_guard("/api/v1/dev/activate")
            if guard:
                return guard
            response = requests.post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/v1/dev/activate",
                timeout=10,
            )
            result = response.json()
            logger.info(f"[DEV] Dev mode activated: {result.get('message')}")
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE ACTIVATED"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["endpoint", str(result.get("goblin_endpoint"))],
                            ["pid", str(result.get("goblin_pid"))],
                        ],
                    ),
                ]
            )
            return {
                "status": "success",
                "message": result.get("message"),
                "output": output,
                "state": "activated",
                "goblin_endpoint": result.get("goblin_endpoint"),
                "goblin_pid": result.get("goblin_pid"),
            }
        except requests.exceptions.ConnectionError:
            logger.error("[DEV] Cannot connect to Wizard Server")
            return {
                "status": "error",
                "message": "Wizard Server not running on 127.0.0.1:8765",
                "hint": "Start Wizard with: python -m wizard.server",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to activate dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _deactivate_dev_mode(self) -> Dict:
        """Deactivate dev mode via Wizard."""
        try:
            guard = self._throttle_guard("/api/v1/dev/deactivate")
            if guard:
                return guard
            response = requests.post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/v1/dev/deactivate",
                timeout=10,
            )
            result = response.json()
            logger.info(f"[DEV] Dev mode deactivated: {result.get('message')}")
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE DEACTIVATED"),
                    result.get("message", ""),
                ]
            )
            return {
                "status": "success",
                "message": result.get("message"),
                "output": output,
                "state": "deactivated",
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Wizard Server not running",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to deactivate dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _get_dev_status(self) -> Dict:
        """Get dev mode status from Wizard."""
        try:
            guard = self._throttle_guard("/api/v1/dev/status")
            if guard:
                return guard
            response = requests.get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/v1/dev/status",
                timeout=5,
            )
            result = response.json()
            services = result.get("services") or {}
            service_rows = [[name, str(active)] for name, active in services.items()]
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE STATUS"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["active", str(result.get("active"))],
                            ["uptime_sec", str(result.get("uptime_seconds"))],
                            ["endpoint", str(result.get("goblin_endpoint"))],
                            ["pid", str(result.get("goblin_pid"))],
                        ],
                    ),
                    "",
                    "Services:",
                    OutputToolkit.table(["service", "active"], service_rows)
                    if service_rows
                    else "No services reported.",
                ]
            )
            return {
                "status": "success",
                "message": "Dev mode status",
                "output": output,
                "state": "status",
                "active": result.get("active"),
                "uptime_seconds": result.get("uptime_seconds"),
                "goblin_endpoint": result.get("goblin_endpoint"),
                "goblin_pid": result.get("goblin_pid"),
                "services": result.get("services"),
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "wizard_offline",
                "message": "Wizard Server not running",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to get dev status: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _restart_dev_mode(self) -> Dict:
        """Restart dev mode via Wizard."""
        try:
            guard = self._throttle_guard("/api/v1/dev/restart")
            if guard:
                return guard
            response = requests.post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/v1/dev/restart",
                timeout=15,
            )
            result = response.json()
            logger.info(f"[DEV] Dev mode restarted: {result.get('message')}")
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE RESTARTED"),
                    result.get("message", ""),
                ]
            )
            return {
                "status": "success",
                "message": result.get("message"),
                "output": output,
                "state": "restarted",
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Wizard Server not running",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to restart dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _get_dev_logs(self, lines: int = 50) -> Dict:
        """Get dev mode logs from Wizard."""
        try:
            guard = self._throttle_guard("/api/v1/dev/logs")
            if guard:
                return guard
            response = requests.get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/v1/dev/logs?lines={lines}",
                timeout=5,
            )
            result = response.json()
            log_lines = result.get("logs", [])
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE LOGS"),
                    "\n".join(log_lines) if log_lines else "No logs available.",
                ]
            )
            return {
                "status": "success",
                "message": "Dev mode logs",
                "output": output,
                "state": "logs",
                "goblin_pid": result.get("goblin_pid"),
                "log_file": result.get("log_file"),
                "logs": result.get("logs", []),
                "total_lines": result.get("total_lines"),
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to get dev logs: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }

    def _get_dev_health(self) -> Dict:
        """Get dev mode health from Wizard."""
        try:
            guard = self._throttle_guard("/api/v1/dev/health")
            if guard:
                return guard
            response = requests.get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/v1/dev/health",
                timeout=5,
            )
            result = response.json()
            services = result.get("services") or {}
            service_rows = [[name, str(active)] for name, active in services.items()]
            output = "\n".join(
                [
                    OutputToolkit.banner("DEV MODE HEALTH"),
                    OutputToolkit.table(
                        ["key", "value"],
                        [
                            ["healthy", str(result.get("healthy"))],
                            ["dev_active", str(result.get("status") == "active")],
                        ],
                    ),
                    "",
                    "Services:",
                    OutputToolkit.table(["service", "healthy"], service_rows)
                    if service_rows
                    else "No services reported.",
                ]
            )
            return {
                "status": "success",
                "message": "Dev mode health",
                "output": output,
                "state": "health",
                "healthy": result.get("healthy"),
                "dev_active": result.get("status") == "active",
                "services": result.get("services"),
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "wizard_offline",
                "healthy": False,
                "dev_active": False,
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to get dev health: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }
