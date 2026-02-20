"""WIZARD command handler - Wizard server maintenance tasks."""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import json
import os
import secrets
import subprocess
import threading
import webbrowser
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.commands.interactive_menu_mixin import InteractiveMenuMixin
from core.tui.output import OutputToolkit
from core.tui.ui_elements import Spinner
from core.services.logging_api import get_logger, get_repo_root
from core.services.destructive_ops import remove_path, resolve_vault_root, scrub_directory
from core.services.error_contract import CommandError

logger = get_logger("wizard-handler")


class WizardHandler(BaseCommandHandler, InteractiveMenuMixin):
    """Handler for WIZARD command - maintenance and rebuild."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            base_url, dashboard_url = self._wizard_urls()
            choice = self.show_menu(
                "WIZARD",
                [
                    ("Start server", "start", "Launch Wizard server"),
                    ("Stop server", "stop", "Stop Wizard server"),
                    ("Status", "status", "Check Wizard health"),
                    ("Reset keystore", "reset", "Wipe Wizard secret store + admin token"),
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

        if is_ghost_mode() and action in {"rebuild", "--rebuild", "start", "--start", "stop", "--stop", "reset", "--reset"}:
            return {
                "status": "warning",
                "message": "Ghost Mode is read-only (Wizard control blocked)",
                "output": self._help_text(),
            }

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
        elif action in {"prov", "provider"}:
            return self._wizard_provider(params[1:])
        elif action in {"integ", "integration"}:
            return self._wizard_integration(params[1:])
        elif action in {"check", "fullcheck", "full"}:
            return self._wizard_full_check(params[1:])
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

    def _rebuild_wizard(self) -> Dict:
        """Rebuild wizard dashboard artifacts."""
        repo_root = get_repo_root()
        banner = OutputToolkit.banner("WIZARD REBUILD")
        output_lines = [banner, ""]

        # Validate repo root exists
        if not repo_root or not Path(repo_root).exists():
            logger.error("[LOCAL] Invalid repo root for wizard rebuild")
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message="Wizard root not found",
                recovery_hint="Ensure uDOS is running from repository root",
                level="ERROR",
            )

        # Validate build script exists
        build_script = Path(repo_root) / "bin" / "udos-common.sh"
        if not build_script.exists():
            logger.error(f"[LOCAL] Build script not found: {build_script}")
            raise CommandError(
                code="ERR_IO_FILE_NOT_FOUND",
                message="Build infrastructure not found",
                recovery_hint=f"Missing: {build_script}",
                level="ERROR",
            )

        try:
            rebuild_cmd = (
                f"source \"{repo_root}/bin/udos-common.sh\" "
                "&& export UDOS_FORCE_REBUILD=1 "
                "&& rebuild_wizard_dashboard"
            )

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
                logger.error(f"[LOCAL] Wizard rebuild failed with code {result.returncode}")
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
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message="Rebuild timed out (exceeded 5 minutes)",
                recovery_hint="Try rebuilding manually: source bin/udos-common.sh && rebuild_wizard_dashboard",
                level="ERROR",
            )
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
        return "\n".join(
            [
                OutputToolkit.banner("WIZARD"),
                "WIZARD START      Start Wizard server",
                "WIZARD STOP       Stop Wizard server (graceful)",
                "WIZARD KILL       Force kill Wizard process (port conflict fix)",
                "WIZARD RESTART    Kill and restart Wizard",
                "WIZARD STATUS     Check Wizard server status",
                "WIZARD PROV ...   Provider operations (LIST|STATUS|ENABLE|DISABLE|SETUP|GENSECRET)",
                "WIZARD INTEG ...  Integration wiring checks (status|github|mistral|ollama)",
                "WIZARD CHECK      Full Wizard-side shakedown",
                "WIZARD RESET      Wipe Wizard keystore + admin token (destructive)",
                "  --wipe-profile  Also delete memory/user/profile.json",
                "  --scrub-vault   Also delete VAULT_ROOT contents",
                "WIZARD REBUILD    Rebuild Wizard dashboard artifacts",
                "WIZARD HELP       Show this help",
            ]
        )

    def _show_help(self) -> Dict:
        return {"status": "success", "output": self._help_text()}

    def _wizard_provider(self, params: List[str]) -> Dict:
        """Route provider operations through Wizard API surface."""
        sub = (params[0].upper() if params else "LIST")
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
                lines.append(f"  Config: {configured}  Available: {available}  Enabled: {enabled}")
            return {"status": "success", "message": "Provider list loaded", "output": "\n".join(lines)}

        if sub == "STATUS":
            if not args:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Usage: WIZARD PROV STATUS <id>",
                    recovery_hint="Provide a provider ID (e.g., github, mistral)",
                    level="INFO",
                )
            provider_id = args[0]
            ok, payload, err = self._wizard_api_json("GET", f"/api/providers/{provider_id}/status")
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message=err,
                    recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                    level="ERROR",
                )
            provider = payload.get("provider", {})
            lines = [OutputToolkit.banner(f"WIZARD PROV STATUS {provider_id.upper()}"), ""]
            lines.append(f"ID: {provider.get('id', provider_id)}")
            lines.append(f"Name: {provider.get('name', provider_id)}")
            lines.append(f"Configured: {'yes' if provider.get('configured') else 'no'}")
            lines.append(f"Available: {'yes' if provider.get('available') else 'no'}")
            lines.append(f"Enabled: {'yes' if provider.get('enabled') else 'no'}")
            return {"status": "success", "message": "Provider status loaded", "output": "\n".join(lines)}

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
            return {"status": "success", "message": payload.get("message", f"{sub} complete")}

        if sub == "SETUP":
            if not args:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Usage: WIZARD PROV SETUP <id>",
                    recovery_hint="Provide a provider ID (e.g., github, mistral)",
                    level="INFO",
                )
            provider_id = args[0]
            ok, payload, err = self._wizard_api_json("POST", "/api/providers/setup/run", {"provider_id": provider_id})
            if not ok:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message=err,
                    recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                    level="ERROR",
                )
            lines = [OutputToolkit.banner(f"WIZARD PROV SETUP {provider_id.upper()}"), ""]
            lines.append(payload.get("message", "Setup payload ready"))
            for cmd in payload.get("commands", []):
                ctype = cmd.get("type", "cmd")
                cval = cmd.get("cmd", "")
                lines.append(f"  {ctype}: {cval}")
            return {"status": "success", "message": "Provider setup instructions loaded", "output": "\n".join(lines)}

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

    def _wizard_integration(self, params: List[str]) -> Dict:
        """Route integration checks through Wizard API/system surfaces."""
        sub = (params[0].lower() if params else "status")
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
                lines.append(f"Integrations: total={total} installed={installed} enabled={enabled}")
            return {"status": "success", "message": "Integration status loaded", "output": "\n".join(lines)}
        if sub in {"github", "mistral", "ollama"}:
            ok, payload, err = self._wizard_api_json("GET", f"/api/providers/{sub}/status")
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
            return {"status": "success", "message": "Integration provider status loaded", "output": "\n".join(lines)}
        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Usage: WIZARD INTEG [status|github|mistral|ollama]",
            recovery_hint="Choose a valid integration option",
            level="INFO",
        )

    def _wizard_full_check(self, params: List[str]) -> Dict:
        """Run full Wizard-side checks via monitoring diagnostics."""
        ok, payload, err = self._wizard_api_json("GET", "/api/monitoring/diagnostics")
        if not ok:
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message=err,
                recovery_hint="Check if Wizard server is running (WIZARD STATUS)",
                level="ERROR",
            )
        health = (payload.get("health") or {})
        summary = health.get("summary") or {}
        lines = [OutputToolkit.banner("WIZARD CHECK"), ""]
        if summary:
            lines.append(f"Services: {summary.get('total', '?')} total")
            lines.append(f"Healthy: {summary.get('healthy', '?')}")
            lines.append(f"Degraded: {summary.get('degraded', '?')}")
            lines.append(f"Unhealthy: {summary.get('unhealthy', '?')}")
        else:
            lines.append("Diagnostics fetched; no summary data returned.")
        return {"status": "success", "message": "Wizard diagnostics complete", "output": "\n".join(lines), "payload": payload}

    def _wizard_api_json(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """Call Wizard API using curl subprocess to avoid direct HTTP client imports."""
        base_url, _ = self._wizard_urls()
        url = f"{base_url}{path}"
        cmd = ["curl", "-sS", "-m", "10", "-X", method.upper(), "-H", "Accept: application/json", url]
        if body is not None:
            cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(body)])
        token = os.environ.get("WIZARD_ADMIN_TOKEN", "").strip()
        if token:
            cmd.extend(["-H", f"Authorization: Bearer {token}"])
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            if result.returncode != 0:
                return False, {}, f"Wizard API call failed ({path}): {result.stderr.strip() or result.stdout.strip()}"
            text = (result.stdout or "").strip()
            if not text:
                return True, {}, ""
            try:
                return True, json.loads(text), ""
            except json.JSONDecodeError:
                return False, {}, f"Wizard API returned non-JSON payload for {path}"
        except Exception as exc:
            return False, {}, f"Wizard API call error ({path}): {exc}"

    def _open_dashboard(self) -> Dict:
        banner = OutputToolkit.banner("WIZARD DASHBOARD")
        _, dashboard_url = self._wizard_urls()
        try:
            webbrowser.open(dashboard_url)
            return {"status": "success", "output": banner + "\n✅ Opened Wizard Dashboard"}
        except Exception as exc:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(exc),
                recovery_hint=f"Manually open: {dashboard_url}",
                level="ERROR",
                cause=exc,
            )

    def _start_wizard(self) -> Dict:
        """Start Wizard server."""
        import requests
        import time
        import socket

        banner = OutputToolkit.banner("WIZARD START")
        output_lines = [banner, ""]
        base_url, dashboard_url = self._wizard_urls()
        host, port = self._wizard_host_port()
        connect_host = self._wizard_connect_host(host)

        # Check if already running
        try:
            resp = requests.get(f"{base_url}/health", timeout=2)
            if resp.status_code == 200:
                output_lines.append(f"✅ Wizard already running on {base_url}")
                self._maybe_open_dashboard(output_lines)
                return {
                    "status": "success",
                    "output": "\n".join(output_lines),
                }
        except requests.exceptions.ConnectionError:
            pass  # Not running, proceed
        except Exception as exc:
            logger.warning(f"[LOCAL] Health check failed: {exc}")

        # Start wizard server
        output_lines.append("Starting Wizard Server...")
        repo_root = get_repo_root()

        try:
            # Validate python module
            if not subprocess.run(
                [
                    "python",
                    "-c",
                    "import importlib; importlib.import_module('wizard.server')",
                ],
                capture_output=True,
                timeout=5
            ).returncode == 0:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message="Wizard module not available",
                    recovery_hint="Ensure wizard package is installed in current Python environment",
                    level="ERROR",
                )

            # Start in background
            subprocess.Popen(
                ["python", "-m", "wizard.server", "--no-interactive"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(repo_root),
            )

            # Wait for server to be ready (max 60 seconds with better feedback)
            stop = threading.Event()
            spinner = Spinner(label="Waiting for Wizard", show_elapsed=True)
            thread = spinner.start_background(stop)

            max_attempts = 120  # 120 * 0.5s = 60 seconds
            for attempt in range(max_attempts):
                try:
                    resp = requests.get(f"{base_url}/health", timeout=1)
                    if resp.status_code == 200:
                        stop.set()
                        thread.join(timeout=1)
                        spinner.stop("Wizard ready")
                        output_lines.append("✅ Wizard Server started")
                        output_lines.append(f"📍 Server: {base_url}")
                        output_lines.append(f"📍 Dashboard: {dashboard_url}")
                        self._maybe_open_dashboard(output_lines)
                        return {
                            "status": "success",
                            "output": "\n".join(output_lines),
                        }
                except requests.exceptions.RequestException:
                    pass
                time.sleep(0.5)

            # Timeout after 60 seconds
            stop.set()
            thread.join(timeout=1)
            spinner.stop("Wizard start timed out")
            port_in_use = False
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.25)
                port_in_use = sock.connect_ex((connect_host, port)) == 0
                sock.close()
            except Exception:
                pass

            if port_in_use:
                # Port occupied - offer self-healing options
                from core.services.provider_registry import get_provider, ProviderType, ProviderNotAvailableError
                try:
                    pm = get_provider(ProviderType.PORT_MANAGER)
                    occupant = pm.get_port_occupant(port)
                except ProviderNotAvailableError:
                    pm = None
                    occupant = None

                if occupant:
                    output_lines.append(
                        f"⚠️  Port {port} occupied by PID {occupant.get('pid')} ({occupant.get('process')})"
                    )
                    output_lines.append("")
                    output_lines.append("Self-heal options:")
                    output_lines.append(f"  • WIZARD KILL     — Kill existing process")
                    output_lines.append(f"  • WIZARD RESTART  — Kill and restart Wizard")
                    output_lines.append("")
                    output_lines.append("Or manually: lsof -i :{} | kill -9 <PID>".format(port))
                else:
                    output_lines.append(
                        f"⚠️  Port {port} is in use or Wizard is still booting. "
                        "Check logs or stop the existing process."
                    )
            else:
                # Port is free but health check timed out - check once more
                try:
                    resp = requests.get(f"{base_url}/health", timeout=2)
                    if resp.status_code == 200:
                        output_lines.append("✅ Wizard Server is now responding")
                        output_lines.append(f"📍 Server: {base_url}")
                        output_lines.append(f"📍 Dashboard: {dashboard_url}")
                        self._maybe_open_dashboard(output_lines)
                        return {
                            "status": "success",
                            "output": "\n".join(output_lines),
                        }
                except requests.exceptions.RequestException:
                    pass

                # Still not responding - show diagnostics and offer browser anyway
                output_lines.append("⚠️  Wizard Server started but slow to respond")
                output_lines.append("")
                output_lines.append("Debugging:")

                # Try to show recent logs
                try:
                    repo_root = get_repo_root()
                    log_file = repo_root / "memory" / "logs" / "wizard-server.log"
                    if log_file.exists():
                        tail_result = subprocess.run(
                            ["tail", "-20", str(log_file)],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        if tail_result.stdout.strip():
                            output_lines.append("  Recent logs:")
                            for line in tail_result.stdout.strip().split("\n"):
                                output_lines.append(f"    {line}")
                except Exception:
                    pass

                output_lines.append("")
                output_lines.append("Options:")
                output_lines.append(f"  • View live: tail -f memory/logs/wizard-server.log")
                output_lines.append(f"  • Restart: WIZARD RESTART")
                output_lines.append(f"  • Manual: python -m wizard.server --debug")

                # Still offer to open browser
                self._maybe_open_dashboard(output_lines)

        except Exception as exc:
            logger.error(f"[LOCAL] Failed to start Wizard: {exc}")
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(exc),
                recovery_hint="Check wizard server logs or try manual start: python -m wizard.server",
                level="ERROR",
                cause=exc,
            )

    def _maybe_open_dashboard(self, output_lines: List[str]) -> None:
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

    def _stop_wizard(self) -> Dict:
        """Stop Wizard server."""
        import subprocess
        import requests

        banner = OutputToolkit.banner("WIZARD STOP")
        output_lines = [banner, ""]

        try:
            # Kill wizard processes
            subprocess.run(
                ["pkill", "-f", "wizard\\.server"],
                capture_output=True,
                timeout=5,
            )
            output_lines.append("Stopping Wizard Server...")
            import time
            stop = threading.Event()
            spinner = Spinner(label="Stopping Wizard", show_elapsed=False)
            thread = spinner.start_background(stop)
            time.sleep(1)
            stop.set()
            thread.join(timeout=1)
            spinner.stop("Wizard stop complete")

            # Verify stopped
            try:
                resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                if resp.status_code == 200:
                    output_lines.append("⚠️  Wizard still responding after stop")
                else:
                    output_lines.append("✅ Wizard stopped")
            except requests.exceptions.ConnectionError:
                output_lines.append("✅ Wizard stopped")

            return {"status": "success", "output": "\n".join(output_lines)}
        except Exception as exc:
            logger.error(f"[LOCAL] Failed to stop Wizard: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "output": "\n".join(output_lines) + f"\n❌ Error: {exc}",
            }

    def _kill_wizard(self) -> Dict:
        """Force kill Wizard server using port manager."""
        banner = OutputToolkit.banner("WIZARD KILL")
        output_lines = [banner, ""]

        try:
            from core.services.provider_registry import (
                get_provider,
                ProviderType,
                ProviderNotAvailableError,
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

    def _restart_wizard(self) -> Dict:
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

        return {
            "status": start_result["status"],
            "output": "\n".join(output_lines),
        }

    def _stop_wizard_old(self) -> Dict:
        """Stop Wizard server (old method)."""
        import subprocess
        import requests

        banner = OutputToolkit.banner("WIZARD STOP")
        output_lines = [banner, ""]

        try:
            # Kill wizard processes
            subprocess.run(
                ["pkill", "-f", "wizard\\.server"],
                capture_output=True,
                timeout=5,
            )
            output_lines.append("Stopping Wizard Server...")
            import time
            stop = threading.Event()
            spinner = Spinner(label="Stopping Wizard", show_elapsed=False)
            thread = spinner.start_background(stop)
            time.sleep(1)
            stop.set()
            thread.join(timeout=1)
            spinner.stop("Wizard stop complete")

            # Verify stopped
            try:
                resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                if resp.status_code == 200:
                    output_lines.append("⚠️  Wizard still responding after stop")
                else:
                    output_lines.append("✅ Wizard Server stopped")
            except requests.exceptions.ConnectionError:
                output_lines.append("✅ Wizard Server stopped")

            return {
                "status": "success",
                "output": "\n".join(output_lines),
            }

        except Exception as exc:
            logger.error(f"[LOCAL] Failed to stop Wizard: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "output": "\n".join(output_lines) + f"\n❌ Error: {exc}",
            }

    def _wizard_status(self) -> Dict:
        """Check Wizard server status."""
        import requests

        banner = OutputToolkit.banner("WIZARD STATUS")
        output_lines = [banner, ""]
        base_url, _ = self._wizard_urls()

        try:
            resp = requests.get(f"{base_url}/health", timeout=2)
            if resp.status_code == 200:
                output_lines.append(f"✅ Wizard running on {base_url}")
                try:
                    data = resp.json()
                    if "version" in data:
                        output_lines.append(f"📦 Version: {data['version']}")
                    if "services" in data:
                        services = data["services"]
                        output_lines.append(f"🔌 Services:")
                        for service, enabled in services.items():
                            status = "✓" if enabled else "✗"
                            output_lines.append(f"   {status} {service}")
                except Exception:
                    pass
                return {
                    "status": "success",
                    "output": "\n".join(output_lines),
                }
            else:
                output_lines.append("⚠️  Wizard not responding")
                return {
                    "status": "error",
                    "output": "\n".join(output_lines),
                }
        except requests.exceptions.ConnectionError:
            output_lines.append("❌ Wizard not running")
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
        if host in {"0.0.0.0", "::"}:
            return "127.0.0.1"
        return host

    def _wizard_urls(self) -> tuple:
        host, port = self._wizard_host_port()
        connect_host = self._wizard_connect_host(host)
        base_url = f"http://{connect_host}:{port}"
        dashboard_url = f"{base_url}/dashboard"
        return base_url, dashboard_url

    def _reset_wizard(self, args: List[str]) -> Dict:
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
