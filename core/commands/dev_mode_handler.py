"""DEV MODE command handler - Activate/deactivate development mode via Wizard Server."""

from typing import List, Dict, Optional
from pathlib import Path
import requests
import json
import os

try:
    from core.services.logging_api import get_logger
    logger = get_logger("core", category="dev-mode", name="dev-mode-handler")
except ImportError:
    import logging

    logger = logging.getLogger("dev-mode-handler")

from core.services.rate_limit_helpers import guard_wizard_endpoint

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit


class DevModeHandler(BaseCommandHandler):
    """Handler for DEV MODE command - managed by Wizard Server."""

    def __init__(self):
        """Initialize dev mode handler."""
        super().__init__()
        self.wizard_host = "127.0.0.1"
        self.wizard_port = 8765

    def _admin_token(self) -> str:
        return os.getenv("WIZARD_ADMIN_TOKEN", "").strip()

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        token = self._admin_token()
        if token:
            headers["X-Admin-Token"] = token
        return headers

    def _admin_guard(self) -> Optional[Dict]:
        try:
            from core.services.user_service import get_user_manager, Permission

            user_mgr = get_user_manager()
            if not user_mgr.has_permission(Permission.ADMIN):
                output = "\n".join(
                    [
                        OutputToolkit.banner("DEV MODE"),
                        "Dev mode is restricted to admin role users.",
                        "Tip: Use USER ROLE or SETUP to switch to admin.",
                    ]
                )
                return {
                    "status": "error",
                    "message": "Admin role required for dev mode",
                    "output": output,
                }
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to verify admin role: {exc}",
            }
        return None

    def _dev_templates_guard(self) -> Optional[Dict]:
        try:
            from core.services.logging_api import get_repo_root

            repo_root = get_repo_root()
            dev_root = repo_root / "dev"
            if not dev_root.exists():
                output = "\n".join(
                    [
                        OutputToolkit.banner("DEV MODE"),
                        "Dev submodule not present (/dev missing).",
                        "Hint: Clone github.com/fredporter/uDOS-dev.",
                    ]
                )
                return {
                    "status": "error",
                    "message": "Dev submodule missing",
                    "output": output,
                }
            marker_paths = [
                dev_root / "README.md",
                dev_root / "goblin" / "README.md",
                dev_root / "goblin" / "dev_mode_commands.json",
                dev_root / "goblin" / "scripts",
                dev_root / "goblin" / "tests",
            ]
            if not any(path.exists() for path in marker_paths):
                output = "\n".join(
                    [
                        OutputToolkit.banner("DEV MODE"),
                        "Dev submodule is missing required templates.",
                        "Hint: Re-clone or update /dev.",
                    ]
                )
                return {
                    "status": "error",
                    "message": "Dev templates missing",
                    "output": output,
                }
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to verify /dev templates: {exc}",
            }
        return None

    def _dev_manifest(self) -> Dict:
        try:
            from core.services.logging_api import get_repo_root

            manifest_path = get_repo_root() / "dev" / "goblin" / "dev_mode_commands.json"
            if not manifest_path.exists():
                return {}
            with open(manifest_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def _resolve_action(self, raw_action: str) -> str:
        action = (raw_action or "status").strip().lower()
        manifest = self._dev_manifest()
        actions = manifest.get("actions") or {}
        for canonical, meta in actions.items():
            aliases = [str(item).strip().lower() for item in (meta or {}).get("aliases", []) if str(item).strip()]
            if action == canonical.lower() or action in aliases:
                return canonical.lower()
        return action

    def _dev_syntax(self) -> str:
        manifest = self._dev_manifest()
        syntax = manifest.get("syntax")
        if isinstance(syntax, str) and syntax.strip():
            return syntax.strip()
        return "DEV [on|off|status|restart|logs|health|clear]"

    def _throttle_guard(self, endpoint: str) -> Optional[Dict]:
        """Return throttle response when rate limit exceeded."""
        return guard_wizard_endpoint(endpoint)

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
        action = self._resolve_action(params[0] if params else "status")
        if action in {"on", "activate", "start"}:
            return self._activate_dev_mode()
        if action in {"off", "deactivate", "stop"}:
            return self._deactivate_dev_mode()
        if action in {"status", "stat"}:
            return self._get_dev_status()
        if action in {"restart"}:
            return self._restart_dev_mode()
        if action in {"logs", "log"}:
            return self._get_dev_logs()
        if action in {"health"}:
            return self._get_dev_health()
        if action in {"clear"}:
            return self._clear_dev_mode()

        output = "\n".join(
            [
                OutputToolkit.banner("DEV MODE"),
                f"Usage: {self._dev_syntax()}",
            ]
        )
        return {
            "status": "error",
            "message": "Unknown DEV action",
            "output": output,
        }

    def _activate_dev_mode(self) -> Dict:
        """Activate dev mode via Wizard."""
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/activate")
            if guard:
                return guard
            response = requests.post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/activate",
                headers=self._headers(),
                timeout=10,
            )
            if response.status_code in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response.status_code == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev submodule missing",
                }
            if response.status_code == 409:
                result = response.json()
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.json()
            if not response.ok:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode activation failed",
                }
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
            guard = self._admin_guard()
            if guard:
                return guard
            guard = self._throttle_guard("/api/dev/deactivate")
            if guard:
                return guard
            response = requests.post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/deactivate",
                headers=self._headers(),
                timeout=10,
            )
            if response.status_code in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response.status_code == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev submodule missing",
                }
            result = response.json()
            if not response.ok:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode deactivation failed",
                }
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
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/status")
            if guard:
                return guard
            response = requests.get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/status",
                headers=self._headers(),
                timeout=5,
            )
            if response.status_code in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response.status_code == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev submodule missing",
                }
            result = response.json()
            if not response.ok:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode status failed",
                }
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
                            ["dev_root", str(result.get("dev_root"))],
                            ["scripts_root", str(result.get("scripts_root"))],
                            ["tests_root", str(result.get("tests_root"))],
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
                "dev_root": result.get("dev_root"),
                "scripts_root": result.get("scripts_root"),
                "tests_root": result.get("tests_root"),
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
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/restart")
            if guard:
                return guard
            response = requests.post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/restart",
                headers=self._headers(),
                timeout=15,
            )
            if response.status_code in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response.status_code == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev submodule missing",
                }
            if response.status_code == 409:
                result = response.json()
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.json()
            if not response.ok:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode restart failed",
                }
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
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/logs")
            if guard:
                return guard
            response = requests.get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/logs?lines={lines}",
                headers=self._headers(),
                timeout=5,
            )
            if response.status_code in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response.status_code == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev submodule missing",
                }
            if response.status_code == 409:
                result = response.json()
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.json()
            if not response.ok:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode logs failed",
                }
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
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/health")
            if guard:
                return guard
            response = requests.get(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/health",
                headers=self._headers(),
                timeout=5,
            )
            if response.status_code in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response.status_code == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev submodule missing",
                }
            if response.status_code == 409:
                result = response.json()
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.json()
            if not response.ok:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode health failed",
                }
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

    def _clear_dev_mode(self) -> Dict:
        """Clear dev mode caches/rebuilds via Wizard."""
        try:
            guard = self._admin_guard()
            if guard:
                return guard
            dev_guard = self._dev_templates_guard()
            if dev_guard:
                return dev_guard
            guard = self._throttle_guard("/api/dev/clear")
            if guard:
                return guard
            response = requests.post(
                f"http://{self.wizard_host}:{self.wizard_port}/api/dev/clear",
                headers=self._headers(),
                timeout=20,
            )
            if response.status_code in {401, 403}:
                return self._admin_guard() or {
                    "status": "error",
                    "message": "Admin token required for dev mode",
                }
            if response.status_code == 412:
                return self._dev_templates_guard() or {
                    "status": "error",
                    "message": "Dev submodule missing",
                }
            if response.status_code == 409:
                result = response.json()
                return {
                    "status": "error",
                    "message": result.get("detail") or "Dev mode is not active",
                }
            result = response.json()
            if not response.ok:
                return {
                    "status": "error",
                    "message": result.get("detail") or result.get("message") or "Dev mode clear failed",
                }
            return {
                "status": "success",
                "message": "Dev mode clear complete",
                "output": "\n".join(
                    [
                        OutputToolkit.banner("DEV MODE CLEAR"),
                        json.dumps(result, indent=2),
                    ]
                ),
                "state": "cleared",
            }
        except Exception as exc:
            logger.error(f"[DEV] Failed to clear dev mode: {exc}")
            return {
                "status": "error",
                "message": str(exc),
            }
