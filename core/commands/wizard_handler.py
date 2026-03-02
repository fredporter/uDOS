"""WIZARD command handler - Wizard server maintenance tasks."""

from __future__ import annotations

from datetime import datetime
import getpass
import json
from pathlib import Path
import secrets
import subprocess
from typing import Any
import webbrowser

from core.commands.base import BaseCommandHandler
from core.commands.interactive_menu_mixin import InteractiveMenuMixin
from core.services.background_service_manager import get_wizard_process_manager
from core.services.destructive_ops import (
    remove_path,
    resolve_vault_root,
    scrub_directory,
)
from core.services.error_contract import CommandError
from core.services.logging_api import get_repo_root
from core.services.logging_manager import get_logger
from core.services.permission_handler import Permission
from core.services.wizard_mode_state import (
    get_wizard_mode_active,
    set_wizard_mode_active,
)
from core.tui.output import OutputToolkit

logger = get_logger("wizard-handler")


class WizardHandler(BaseCommandHandler, InteractiveMenuMixin):
    """Handler for WIZARD command - maintenance and rebuild."""

    _LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})

    def handle(self, command: str, params: list[str], grid=None, parser=None) -> dict:
        if not params:
            base_url, dashboard_url = self._wizard_urls()
            choice = self.show_menu(
                "WIZARD",
                [
                    ("Start server", "start", "Launch Wizard server"),
                    ("Stop server", "stop", "Stop Wizard server"),
                    ("Status", "status", "Check Wizard health"),
                    ("Key management", "key", "Manage MISTRAL_API_KEY in .env"),
                    (
                        "Reset keystore",
                        "reset",
                        "Wipe Wizard secret store + admin token",
                    ),
                    ("Rebuild dashboard", "rebuild", "Rebuild dashboard assets"),
                    ("Open dashboard", "open", f"Open {dashboard_url}"),
                    ("Help", "help", "Show WIZARD help"),
                ],
            )
            if choice is None:
                return self._show_help()
            if choice == "open":
                return self._open_dashboard()
            params = [choice]

        action = params[0].lower().strip()
        if not action:
            return self._show_help()

        from core.services.user_service import is_ghost_mode

        if is_ghost_mode() and action in {
            "rebuild",
            "--rebuild",
            "start",
            "--start",
            "stop",
            "--stop",
            "reset",
            "--reset",
        }:
            logger.warning(
                "[TESTING ALERT] Ghost Mode active: WIZARD %s in demo mode (v1.5). "
                "Enforcement will be added before v1.5 release.",
                action,
            )

        if action in {"rebuild", "--rebuild"}:
            return self._rebuild_wizard()
        elif action in {"start", "--start"}:
            return self._start_wizard()
        elif action in {"stop", "--stop"}:
            return self._stop_wizard()
        elif action in {"kill", "--kill"}:
            return self._kill_wizard()
        elif action in {"restart", "--restart"}:
            return self._restart_wizard()
        elif action in {"status", "--status"}:
            return self._wizard_status()
        elif action in {"key", "keys", "--key", "--keys"}:
            return self._wizard_key(params[1:])
        elif action in {"prov", "provider"}:
            return self._wizard_provider(params[1:])
        elif action in {"integ", "integration"}:
            return self._wizard_integration(params[1:])
        elif action in {"check", "fullcheck", "full"}:
            return self._wizard_full_check(params[1:])
        elif action == "mode":
            return self._wizard_mode(params[1:])
        elif action in {"reset", "--reset"}:
            return self._reset_wizard(params[1:])
        elif action in {"help", "--help", "?"}:
            return self._show_help()

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message=f"Unknown option: {action}",
            recovery_hint="Run WIZARD --help for available options",
            level="INFO",
        )

    def _rebuild_wizard(self) -> dict:
        """Rebuild wizard dashboard artifacts."""
        repo_root = get_repo_root()
        banner = OutputToolkit.banner("WIZARD REBUILD")
        output_lines = [banner, ""]
        used_dashboard_fallback = False

        # Validate repo root exists
        if not repo_root or not Path(repo_root).exists():
            logger.error("[LOCAL] Invalid repo root for wizard rebuild")
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message="Wizard root not found",
                recovery_hint="Ensure uDOS is running from repository root",
                level="ERROR",
            )

        try:
            build_script = Path(repo_root) / "bin" / "udos-common.sh"
            dashboard_root = Path(repo_root) / "wizard" / "dashboard"

            if build_script.exists():
                rebuild_cmd = (
                    f'source "{repo_root}/bin/udos-common.sh" '
                    "&& export UDOS_FORCE_REBUILD=1 "
                    "&& rebuild_wizard_dashboard"
                )
            elif dashboard_root.exists():
                used_dashboard_fallback = True
                npm_bin = subprocess.run(
                    ["bash", "-lc", "command -v npm"],
                    capture_output=True,
                    text=True,
                    check=False,
                    cwd=str(repo_root),
                )
                if npm_bin.returncode != 0:
                    logger.warning(
                        "[LOCAL] npm is unavailable; keeping fallback dashboard content"
                    )
                    return {
                        "status": "warning",
                        "output": (
                            banner
                            + "\n⚠️ Build tooling unavailable (npm not found). "
                            "Fallback dashboard remains active."
                        ),
                    }

                output_lines.append(
                    "Build infrastructure script missing; using dashboard-local self-heal path."
                )
                rebuild_cmd = "npm install --no-audit --no-fund && npm run build"
                repo_root = dashboard_root
            else:
                logger.warning("[LOCAL] Wizard dashboard source not found; skipping rebuild")
                return {
                    "status": "warning",
                    "output": (
                        banner
                        + "\n⚠️ Dashboard source missing; keeping current dashboard artifacts."
                    ),
                }

            # Run without capturing output so spinner can use terminal directly
            result = subprocess.run(
                ["bash", "-lc", rebuild_cmd],
                capture_output=False,  # Let spinner write to terminal
                text=True,
                check=False,
                timeout=300,  # 5 minute timeout
                cwd=str(repo_root),
            )

            if result.returncode != 0:
                logger.error(
                    f"[LOCAL] Wizard rebuild failed with code {result.returncode}"
                )
                if used_dashboard_fallback:
                    return {
                        "status": "warning",
                        "output": (
                            banner
                            + "\n⚠️ Dashboard build attempted but failed; fallback dashboard remains active."
                            + "\nTry: cd wizard/dashboard && rm -rf node_modules && npm install && npm run build"
                        ),
                    }
                raise CommandError(
                    code="ERR_RUNTIME_UNEXPECTED",
                    message=f"Rebuild failed (exit {result.returncode})",
                    recovery_hint="Check build output above for details",
                    level="ERROR",
                )

            logger.info("[LOCAL] Wizard rebuild successful")
            return {
                "status": "success",
                "output": banner + "\n✅ Wizard rebuild complete",
            }
        except subprocess.TimeoutExpired:
            logger.error("[LOCAL] Wizard rebuild timed out (300s)")
            if used_dashboard_fallback:
                return {
                    "status": "warning",
                    "output": (
                        banner
                        + "\n⚠️ Dashboard rebuild timed out; fallback dashboard remains active."
                    ),
                }
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message="Rebuild timed out (exceeded 5 minutes)",
                recovery_hint="Try rebuilding manually: source bin/udos-common.sh && rebuild_wizard_dashboard",
                level="ERROR",
            )
        except CommandError:
            raise
        except Exception as exc:
            logger.error(f"[LOCAL] Wizard rebuild failed: {exc}")
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(exc),
                recovery_hint="Check wizard dashboard build logs",
                level="ERROR",
                cause=exc,
            )

    def _help_text(self) -> str:
        return "\n".join([
            OutputToolkit.banner("WIZARD"),
            "WIZARD START      Start Wizard server",
            "WIZARD STOP       Stop Wizard server (graceful)",
            "WIZARD KILL       Force kill Wizard process (port conflict fix)",
            "WIZARD RESTART    Kill and restart Wizard",
            "WIZARD STATUS     Check Wizard server status",
            "WIZARD KEY ...    Manage MISTRAL_API_KEY (status|set|clear)",
            "WIZARD PROV ...   Provider operations (LIST|STATUS|ENABLE|DISABLE|SETUP|GENSECRET)",
            "WIZARD INTEG ...  Integration wiring checks (status|github|mistral|ollama)",
            "WIZARD CHECK      Full Wizard-side shakedown",
            "WIZARD MODE ...   Toggle wizard-admin mode (on|off|status)",
            "WIZARD RESET      Wipe Wizard keystore + admin token (destructive)",
            "  --wipe-profile  Also delete memory/user/profile.json",
            "  --scrub-vault   Also delete VAULT_ROOT contents",
            "WIZARD REBUILD    Rebuild Wizard dashboard artifacts",
            "WIZARD HELP       Show this help",
        ])

    def _wizard_key(self, params: list[str]) -> dict:
        sub = params[0].lower() if params else "status"

        from core.services.config_sync_service import ConfigSyncManager

        sync = ConfigSyncManager()

        if sub in {"status", "show"}:
            env_data = sync.load_env_dict()
            key = (env_data.get("MISTRAL_API_KEY") or "").strip()
            banner = OutputToolkit.banner("WIZARD KEY STATUS")
            if key:
                preview = "*" * max(4, len(key) - 4) + key[-4:]
                return {
                    "status": "success",
                    "output": "\n".join([
                        banner,
                        "",
                        "MISTRAL_API_KEY: set",
                        f"Preview: {preview}",
                    ]),
                }
            return {
                "status": "warning",
                "output": "\n".join([
                    banner,
                    "",
                    "MISTRAL_API_KEY: missing",
                    "Set one with: WIZARD KEY SET <key>",
                ]),
            }

        if sub in {"set", "add", "update"}:
            key_value = ""
            if len(params) > 1:
                key_value = " ".join(params[1:]).strip()
            elif sub == "set":
                try:
                    key_value = getpass.getpass("Enter Mistral API key: ").strip()
                except Exception:
                    key_value = ""

            if not key_value:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Usage: WIZARD KEY SET <key>",
                    recovery_hint="Provide key as argument, or run interactively and enter when prompted",
                    level="INFO",
                )

            ok, message = sync.update_env_vars({"MISTRAL_API_KEY": key_value})
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_UNEXPECTED",
                    message=message,
                    recovery_hint="Check .env write permissions",
                    level="ERROR",
                )
            return {
                "status": "success",
                "output": "\n".join([
                    OutputToolkit.banner("WIZARD KEY SET"),
                    "",
                    "✅ MISTRAL_API_KEY updated in .env",
                    "Restart Vibe to pick up the new key value.",
                ]),
            }

        if sub in {"clear", "unset", "remove", "delete"}:
            ok, message = sync.update_env_vars({"MISTRAL_API_KEY": None})
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_UNEXPECTED",
                    message=message,
                    recovery_hint="Check .env write permissions",
                    level="ERROR",
                )
            return {
                "status": "success",
                "output": "\n".join([
                    OutputToolkit.banner("WIZARD KEY CLEAR"),
                    "",
                    "✅ MISTRAL_API_KEY removed from .env",
                ]),
            }

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Usage: WIZARD KEY [STATUS|SET|CLEAR]",
            recovery_hint="Examples: WIZARD KEY STATUS | WIZARD KEY SET <key> | WIZARD KEY CLEAR",
            level="INFO",
        )

    def _wizard_mode(self, params: list[str]) -> dict:
        sub = params[0].lower() if params else "status"
        match sub:
            case "status" | "show":
                active = get_wizard_mode_active()
                return {
                    "status": "success",
                    "message": f"Wizard mode {'on' if active else 'off'}",
                    "output": "\n".join([
                        OutputToolkit.banner("WIZARD MODE"),
                        f"Active: {'on' if active else 'off'}",
                        "Scope: admin packaging/distribution operations",
                        "Boundary: core/extension source contribution still requires DEV mode",
                    ]),
                }
            case "on" | "enable":
                self._require_admin()
                set_wizard_mode_active(True)
                return {
                    "status": "success",
                    "message": "Wizard mode enabled",
                    "output": "Wizard mode is now on (admin operations enabled).",
                }
            case "off" | "disable":
                self._require_admin()
                set_wizard_mode_active(False)
                return {
                    "status": "success",
                    "message": "Wizard mode disabled",
                    "output": "Wizard mode is now off.",
                }
            case _:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=f"Unknown WIZARD MODE option: {sub}",
                    recovery_hint="Usage: WIZARD MODE [on|off|status]",
                    level="INFO",
                )

    def _require_admin(self) -> None:
        from core.services.permission_handler import get_permission_handler

        if get_permission_handler().require(Permission.ADMIN, action="wizard_mode"):
            return
        raise CommandError(
            code="ERR_AUTH_FORBIDDEN",
            message="Admin permissions required",
            recovery_hint="Switch to an admin user before changing Wizard mode",
            level="INFO",
        )

    def _show_help(self) -> dict:
        return {"status": "success", "output": self._help_text()}

    def _wizard_provider(self, params: list[str]) -> dict:
        """Route provider operations through Wizard API surface."""
        sub = params[0].upper() if params else "LIST"
        args = params[1:] if len(params) > 1 else []

        if sub == "LIST":
            ok, payload, err = self._wizard_api_json("GET", "/api/providers/list")
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message=err,
                    recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                    level="ERROR",
                )
            providers = payload.get("providers", [])
            lines = [OutputToolkit.banner("WIZARD PROV LIST"), ""]
            for provider in providers:
                pid = provider.get("id", "?")
                name = provider.get("name", pid)
                status = provider.get("status", {})
                configured = "OK" if status.get("configured") else "X"
                available = "OK" if status.get("available") else "X"
                enabled = "OK" if provider.get("enabled") else "X"
                lines.append(f"{name} ({pid})")
                lines.append(
                    f"  Config: {configured}  Available: {available}  Enabled: {enabled}"
                )
            return {
                "status": "success",
                "message": "Provider list loaded",
                "output": "\n".join(lines),
            }

        if sub == "STATUS":
            if not args:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Usage: WIZARD PROV STATUS <id>",
                    recovery_hint="Provide a provider ID (e.g., github, mistral)",
                    level="INFO",
                )
            provider_id = args[0]
            ok, payload, err = self._wizard_api_json(
                "GET", f"/api/providers/{provider_id}/status"
            )
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message=err,
                    recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                    level="ERROR",
                )
            provider = payload.get("provider", {})
            lines = [
                OutputToolkit.banner(f"WIZARD PROV STATUS {provider_id.upper()}"),
                "",
            ]
            lines.append(f"ID: {provider.get('id', provider_id)}")
            lines.append(f"Name: {provider.get('name', provider_id)}")
            lines.append(f"Configured: {'yes' if provider.get('configured') else 'no'}")
            lines.append(f"Available: {'yes' if provider.get('available') else 'no'}")
            lines.append(f"Enabled: {'yes' if provider.get('enabled') else 'no'}")
            return {
                "status": "success",
                "message": "Provider status loaded",
                "output": "\n".join(lines),
            }

        if sub in {"ENABLE", "DISABLE"}:
            if not args:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=f"Usage: WIZARD PROV {sub} <id>",
                    recovery_hint="Provide a provider ID (e.g., github, mistral)",
                    level="INFO",
                )
            provider_id = args[0]
            method = "POST"
            path = f"/api/providers/{provider_id}/{sub.lower()}"
            ok, payload, err = self._wizard_api_json(method, path)
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message=err,
                    recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                    level="ERROR",
                )
            return {
                "status": "success",
                "message": payload.get("message", f"{sub} complete"),
            }

        if sub == "SETUP":
            if not args:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Usage: WIZARD PROV SETUP <id>",
                    recovery_hint="Provide a provider ID (e.g., github, mistral)",
                    level="INFO",
                )
            provider_id = args[0]
            ok, payload, err = self._wizard_api_json(
                "POST", "/api/providers/setup/run", {"provider_id": provider_id}
            )
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message=err,
                    recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                    level="ERROR",
                )
            lines = [
                OutputToolkit.banner(f"WIZARD PROV SETUP {provider_id.upper()}"),
                "",
            ]
            lines.append(payload.get("message", "Setup payload ready"))
            for cmd in payload.get("commands", []):
                ctype = cmd.get("type", "cmd")
                cval = cmd.get("cmd", "")
                lines.append(f"  {ctype}: {cval}")
            return {
                "status": "success",
                "message": "Provider setup instructions loaded",
                "output": "\n".join(lines),
            }

        if sub == "GENSECRET":
            length = 48
            if args and args[0].isdigit():
                length = max(24, min(128, int(args[0])))
            token = secrets.token_urlsafe(length)
            lines = [OutputToolkit.banner("WIZARD PROV GENSECRET"), ""]
            lines.append("Generated local provider secret:")
            lines.append(token)
            lines.append("")
            lines.append("Tip: use TOKEN --len N for additional local tokens.")
            return {
                "status": "success",
                "message": "Generated local secret",
                "output": "\n".join(lines),
                "token": token,
            }

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Usage: WIZARD PROV [LIST|STATUS|ENABLE|DISABLE|SETUP|GENSECRET] ...",
            recovery_hint="Run WIZARD PROV LIST to see available providers",
            level="INFO",
        )

    def _wizard_integration(self, params: list[str]) -> dict:
        """Route integration checks through Wizard API/system surfaces."""
        sub = params[0].lower() if params else "status"
        if sub == "status":
            ok, payload, err = self._wizard_api_json("GET", "/api/system/library")
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message=err,
                    recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                    level="ERROR",
                )
            lines = [OutputToolkit.banner("WIZARD INTEG STATUS"), ""]
            total = payload.get("total_integrations")
            enabled = payload.get("enabled_integrations")
            installed = payload.get("installed_integrations")
            if total is not None:
                lines.append(
                    f"Integrations: total={total} installed={installed} enabled={enabled}"
                )
            return {
                "status": "success",
                "message": "Integration status loaded",
                "output": "\n".join(lines),
            }
        if sub in {"github", "mistral", "ollama"}:
            ok, payload, err = self._wizard_api_json(
                "GET", f"/api/providers/{sub}/status"
            )
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message=err,
                    recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                    level="ERROR",
                )
            provider = payload.get("provider", {})
            lines = [OutputToolkit.banner(f"WIZARD INTEG {sub.upper()}"), ""]
            lines.append(f"Configured: {'yes' if provider.get('configured') else 'no'}")
            lines.append(f"Available: {'yes' if provider.get('available') else 'no'}")
            lines.append(f"Enabled: {'yes' if provider.get('enabled') else 'no'}")
            return {
                "status": "success",
                "message": "Integration provider status loaded",
                "output": "\n".join(lines),
            }
        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Usage: WIZARD INTEG [status|github|mistral|ollama]",
            recovery_hint="Choose a valid integration option",
            level="INFO",
        )

    def _wizard_full_check(self, params: list[str]) -> dict:
        """Run full Wizard-side checks via monitoring diagnostics."""
        ok, payload, err = self._wizard_api_json("GET", "/api/monitoring/diagnostics")
        if not ok:
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message=err,
                recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                level="ERROR",
            )
        health = payload.get("health") or {}
        summary = health.get("summary") or {}
        lines = [OutputToolkit.banner("WIZARD CHECK"), ""]
        if summary:
            lines.append(f"Services: {summary.get('total', '?')} total")
            lines.append(f"Healthy: {summary.get('healthy', '?')}")
            lines.append(f"Degraded: {summary.get('degraded', '?')}")
            lines.append(f"Unhealthy: {summary.get('unhealthy', '?')}")
        else:
            lines.append("Diagnostics fetched; no summary data returned.")
        return {
            "status": "success",
            "message": "Wizard diagnostics complete",
            "output": "\n".join(lines),
            "payload": payload,
        }

    def _wizard_api_json(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> tuple[bool, dict[str, Any], str]:
        """Call Wizard API using curl subprocess to avoid direct HTTP client imports."""
        base_url, _ = self._wizard_urls()
        try:
            status = get_wizard_process_manager().ensure_running(
                base_url=base_url, wait_seconds=30
            )
            if not status.connected:
                return False, {}, f"Wizard unavailable: {status.message}"
        except Exception as exc:
            return False, {}, f"Wizard startup failed: {exc}"
        url = f"{base_url}{path}"
        cmd = [
            "curl",
            "-sS",
            "-m",
            "10",
            "-X",
            method.upper(),
            "-H",
            "Accept: application/json",
            url,
        ]
        if body is not None:
            cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(body)])
        from core.services.unified_config_loader import get_config

        token = get_config("WIZARD_ADMIN_TOKEN", "").strip()
        if token:
            cmd.extend(["-H", f"Authorization: Bearer {token}"])
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            if result.returncode != 0:
                return (
                    False,
                    {},
                    f"Wizard API call failed ({path}): {result.stderr.strip() or result.stdout.strip()}",
                )
            text = (result.stdout or "").strip()
            if not text:
                return True, {}, ""
            try:
                return True, json.loads(text), ""
            except json.JSONDecodeError:
                return False, {}, f"Wizard API returned non-JSON payload for {path}"
        except Exception as exc:
            return False, {}, f"Wizard API call error ({path}): {exc}"

    def _open_dashboard(self) -> dict:
        banner = OutputToolkit.banner("WIZARD DASHBOARD")
        _, dashboard_url = self._wizard_urls()
        try:
            webbrowser.open(dashboard_url)
            return {
                "status": "success",
                "output": banner + "\n✅ Opened Wizard Dashboard",
            }
        except Exception as exc:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(exc),
                recovery_hint=f"Manually open: {dashboard_url}",
                level="ERROR",
                cause=exc,
            )

    def _start_wizard(self) -> dict:
        """Start Wizard server."""
        banner = OutputToolkit.banner("WIZARD START")
        output_lines = [banner, ""]
        base_url, dashboard_url = self._wizard_urls()
        manager = get_wizard_process_manager()
        try:
            before = manager.status(base_url=base_url)
            status = manager.ensure_running(base_url=base_url, wait_seconds=60)
            if status.connected:
                verb = "already running" if before.connected else "started"
                output_lines.append(f"✅ Wizard {verb} on {base_url}")
                output_lines.append(f"📍 Server: {base_url}")
                output_lines.append(f"📍 Dashboard: {dashboard_url}")
                self._maybe_open_dashboard(output_lines)
                return {"status": "success", "output": "\n".join(output_lines)}

            output_lines.append(f"❌ Wizard unavailable ({status.message})")
            output_lines.append("📄 Log: memory/logs/wizard-daemon.log")
            output_lines.append("Try: WIZARD RESTART")
            return {"status": "error", "output": "\n".join(output_lines)}

        except Exception as exc:
            logger.error(f"[LOCAL] Failed to start Wizard: {exc}")
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(exc),
                recovery_hint="Check wizard server logs or try manual start: uv run wizard/server.py --no-interactive",
                level="ERROR",
                cause=exc,
            )

    def _maybe_open_dashboard(self, output_lines: list[str]) -> None:
        _, dashboard_url = self._wizard_urls()
        try:
            response = input("Open Wizard Dashboard...? [Yes|No|OK] ").strip().lower()
        except Exception:
            output_lines.append("No response; Wizard Dashboard not opened")
            return
        if response in {"", "yes", "y", "ok", "okay"}:
            try:
                webbrowser.open(dashboard_url)
                output_lines.append("✅ Opened Wizard Dashboard")
            except Exception as exc:
                logger.error(f"[LOCAL] Failed to open Wizard Dashboard: {exc}")
                output_lines.append(f"❌ Failed to open Wizard Dashboard: {exc}")
        elif response in {"no", "n"}:
            output_lines.append("Skipped opening Wizard Dashboard")
        else:
            output_lines.append("No response; Wizard Dashboard not opened")

    def _stop_wizard(self) -> dict:
        """Stop Wizard server."""
        banner = OutputToolkit.banner("WIZARD STOP")
        output_lines = [banner, ""]
        base_url, _ = self._wizard_urls()
        manager = get_wizard_process_manager()

        try:
            status = manager.stop(base_url=base_url, timeout_seconds=8)
            if status.connected or status.running:
                output_lines.append("⚠️  Wizard still running after stop request")
                output_lines.append("Try: WIZARD KILL")
                return {"status": "warning", "output": "\n".join(output_lines)}
            output_lines.append("✅ Wizard stopped")
            return {"status": "success", "output": "\n".join(output_lines)}
        except Exception as exc:
            logger.error(f"[LOCAL] Failed to stop Wizard: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "output": "\n".join(output_lines) + f"\n❌ Error: {exc}",
            }

    def _kill_wizard(self) -> dict:
        """Force kill Wizard server using port manager."""
        banner = OutputToolkit.banner("WIZARD KILL")
        output_lines = [banner, ""]

        try:
            from core.services.provider_registry import (
                ProviderNotAvailableError,
                ProviderType,
                get_provider,
            )

            pm = get_provider(ProviderType.PORT_MANAGER)

            host, port = self._wizard_host_port()
            occupant = pm.get_port_occupant(port)

        except ProviderNotAvailableError:
            output_lines.append("⚠️  Wizard port manager unavailable")
            output_lines.append("   ▶ Start Wizard or install Wizard services")
            return {"status": "error", "output": "\n".join(output_lines)}

            if not occupant:
                output_lines.append(f"✅ Port {port} is free (Wizard not running)")
                return {"status": "success", "output": "\n".join(output_lines)}

            pid = occupant.get("pid")
            process = occupant.get("process")

            output_lines.append(f"Found process on port {port}: PID {pid} ({process})")

            success = pm.kill_service("wizard")

            if success:
                output_lines.append(f"✅ Killed process {pid}")
            else:
                output_lines.append(f"❌ Failed to kill process {pid}")
                return {
                    "status": "error",
                    "message": f"Failed to kill PID {pid}",
                    "output": "\n".join(output_lines),
                }

            return {"status": "success", "output": "\n".join(output_lines)}

        except Exception as exc:
            logger.error(f"[LOCAL] Failed to kill Wizard: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "output": "\n".join(output_lines) + f"\n❌ Error: {exc}",
            }

    def _restart_wizard(self) -> dict:
        """Kill and restart Wizard server."""
        banner = OutputToolkit.banner("WIZARD RESTART")
        output_lines = [banner, ""]

        # Kill first
        kill_result = self._kill_wizard()
        if kill_result["status"] == "error":
            return {
                "status": "error",
                "message": "Failed to kill existing Wizard process",
                "output": "\n".join(output_lines) + "\n" + kill_result["output"],
            }

        output_lines.extend(kill_result["output"].split("\n")[2:])  # Skip banner
        output_lines.append("")

        # Brief pause
        import time

        time.sleep(1)

        # Start
        start_result = self._start_wizard()
        output_lines.extend(start_result["output"].split("\n")[2:])  # Skip banner

        return {"status": start_result["status"], "output": "\n".join(output_lines)}

    def _wizard_status(self) -> dict:
        """Check Wizard server status."""
        banner = OutputToolkit.banner("WIZARD STATUS")
        output_lines = [banner, ""]
        base_url, _ = self._wizard_urls()
        manager = get_wizard_process_manager()

        key_state = "unknown"
        key_preview = ""
        try:
            from core.services.config_sync_service import ConfigSyncManager

            env_data = ConfigSyncManager().load_env_dict()
            key = (env_data.get("MISTRAL_API_KEY") or "").strip()
            if key:
                key_state = "set"
                key_preview = "*" * max(4, len(key) - 4) + key[-4:]
            else:
                key_state = "missing"
        except Exception:
            pass

        try:
            status = manager.status(base_url=base_url)
            if status.connected:
                output_lines.append(f"✅ Wizard running on {base_url}")
                output_lines.append(f"🔐 Mistral key: {key_state}")
                if key_preview:
                    output_lines.append(f"   Preview: {key_preview}")
                try:
                    data = status.health
                    if "version" in data:
                        output_lines.append(f"📦 Version: {data['version']}")
                    if "services" in data:
                        services = data["services"]
                        output_lines.append("🔌 Services:")
                        for service, enabled in services.items():
                            status = "✓" if enabled else "✗"
                            output_lines.append(f"   {status} {service}")
                except Exception:
                    pass
                return {"status": "success", "output": "\n".join(output_lines)}
            output_lines.append("❌ Wizard not running")
            output_lines.append(f"🔐 Mistral key: {key_state}")
            if key_preview:
                output_lines.append(f"   Preview: {key_preview}")
            output_lines.append("Run: WIZARD START")
            if status.pid:
                output_lines.append(f"PID file process: {status.pid} (unhealthy)")
            return {
                "status": "error",
                "message": "Wizard server not running",
                "output": "\n".join(output_lines),
            }
        except Exception as exc:
            logger.error(f"[LOCAL] Status check failed: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "output": "\n".join(output_lines) + f"\n❌ Error: {exc}",
            }

    def _wizard_host_port(self) -> tuple:
        host = "127.0.0.1"
        port = 8765
        try:
            config_path = get_repo_root() / "wizard" / "config" / "wizard.json"
            if config_path.exists():
                data = json.loads(config_path.read_text())
                if isinstance(data, dict):
                    raw_port = data.get("port")
                    if isinstance(raw_port, int):
                        port = raw_port
                    elif isinstance(raw_port, str) and raw_port.isdigit():
                        port = int(raw_port)
                    raw_host = data.get("host")
                    if isinstance(raw_host, str) and raw_host.strip():
                        host = raw_host.strip()
        except Exception:
            pass
        return host, port

    def _wizard_connect_host(self, host: str) -> str:
        normalized = (host or "").strip().lower()
        if normalized in {"0.0.0.0", "::"}:
            return "127.0.0.1"
        if normalized in self._LOOPBACK_HOSTS:
            return normalized
        logger.warning(
            "[BoundaryPolicy] blocked non-loopback wizard host '%s'; using 127.0.0.1",
            host,
        )
        return "127.0.0.1"

    def _wizard_urls(self) -> tuple:
        host, port = self._wizard_host_port()
        connect_host = self._wizard_connect_host(host)
        base_url = f"http://{connect_host}:{port}"
        dashboard_url = f"{base_url}/dashboard"
        return base_url, dashboard_url

    def _reset_wizard(self, args: list[str]) -> dict:
        """Reset Wizard keystore and admin token (destructive)."""
        banner = OutputToolkit.banner("WIZARD RESET")
        output_lines = [banner, ""]

        wipe_profile = "--wipe-profile" in args
        scrub_vault = "--scrub-vault" in args

        warning = (
            "This will permanently delete the Wizard keystore (secrets.tomb)\n"
            "and remove admin token files. This cannot be undone."
        )
        if wipe_profile:
            warning += "\n- Will delete memory/user/profile.json"
        if scrub_vault:
            warning += "\n- Will delete VAULT_ROOT contents"
        output_lines.append(warning)

        try:
            response = input("Type RESET to confirm: ").strip()
        except Exception:
            response = ""

        if response != "RESET":
            output_lines.append("Cancelled.")
            return {"status": "cancelled", "output": "\n".join(output_lines)}

        repo_root = get_repo_root()
        archive_root = Path(repo_root) / ".compost" / "wizard-reset"
        archive_root.mkdir(parents=True, exist_ok=True)

        tomb_path = Path(repo_root) / "wizard" / "secrets.tomb"
        if tomb_path.exists():
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                archived = archive_root / f"secrets.tomb.backup.{timestamp}"
                tomb_path.rename(archived)
                output_lines.append(f"✅ Archived secrets.tomb to {archived}")
            except Exception as exc:
                output_lines.append(f"⚠️  Failed to archive secrets.tomb: {exc}")
        else:
            output_lines.append("ℹ️  secrets.tomb not found")

        token_paths = [
            Path(repo_root) / "memory" / "private" / "wizard_admin_token.txt",
            Path(repo_root) / "memory" / "bank" / "private" / "wizard_admin_token.txt",
        ]
        for token_path in token_paths:
            try:
                if remove_path(token_path):
                    output_lines.append(f"✅ Removed {token_path}")
            except Exception as exc:
                output_lines.append(f"⚠️  Failed to remove {token_path}: {exc}")

        if wipe_profile:
            profile_path = Path(repo_root) / "memory" / "user" / "profile.json"
            try:
                if remove_path(profile_path):
                    output_lines.append(f"✅ Removed {profile_path}")
            except Exception as exc:
                output_lines.append(f"⚠️  Failed to remove {profile_path}: {exc}")

        if scrub_vault:
            vault_root = resolve_vault_root(Path(repo_root))
            try:
                scrub_directory(vault_root, recreate=True)
                output_lines.append(f"✅ Scrubbed VAULT_ROOT at {vault_root}")
            except Exception as exc:
                output_lines.append(f"⚠️  Failed to scrub VAULT_ROOT: {exc}")

        output_lines.append("")
        output_lines.append("Next steps:")
        output_lines.append("  1. Set WIZARD_KEY in .env")
        output_lines.append("  2. Run WIZARD START")
        output_lines.append("  3. Re-run SETUP to sync profile")

        return {"status": "success", "output": "\n".join(output_lines)}
