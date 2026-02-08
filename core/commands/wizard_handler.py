"""WIZARD command handler - Wizard server maintenance tasks."""

from typing import List, Dict
from datetime import datetime
import json
import subprocess
import threading
import os
import webbrowser
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.commands.interactive_menu_mixin import InteractiveMenuMixin
from core.tui.output import OutputToolkit
from core.tui.ui_elements import Spinner
from core.services.logging_api import get_logger, get_repo_root

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
        elif action in {"status", "--status"}:
            return self._wizard_status()
        elif action in {"reset", "--reset"}:
            return self._reset_wizard(params[1:])
        elif action in {"help", "--help", "?"}:
            return self._show_help()

        return {
            "status": "error",
            "message": f"Unknown option: {action}",
            "output": self._help_text(),
        }

    def _rebuild_wizard(self) -> Dict:
        """Rebuild wizard dashboard artifacts."""
        repo_root = get_repo_root()
        banner = OutputToolkit.banner("WIZARD REBUILD")
        output_lines = [banner, ""]

        # Validate repo root exists
        if not repo_root or not Path(repo_root).exists():
            logger.error("[LOCAL] Invalid repo root for wizard rebuild")
            return {
                "status": "error",
                "message": "Wizard root not found",
                "output": banner + "\n❌ Invalid repository root",
            }

        # Validate build script exists
        build_script = Path(repo_root) / "bin" / "udos-common.sh"
        if not build_script.exists():
            logger.error(f"[LOCAL] Build script not found: {build_script}")
            return {
                "status": "error",
                "message": "Build infrastructure not found",
                "output": banner + f"\n❌ Missing: {build_script}",
            }

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
                return {
                    "status": "error",
                    "message": f"Rebuild failed (exit {result.returncode})",
                    "output": banner + "\n❌ Build failed - check output above",
                }

            logger.info("[LOCAL] Wizard rebuild successful")
            return {
                "status": "success",
                "output": banner + "\n✅ Wizard rebuild complete",
            }
        except subprocess.TimeoutExpired:
            logger.error("[LOCAL] Wizard rebuild timed out (300s)")
            return {
                "status": "error",
                "message": "Rebuild timed out (exceeded 5 minutes)",
                "output": "\n".join(output_lines) + "\n❌ Build process exceeded timeout",
            }
        except Exception as exc:
            logger.error(f"[LOCAL] Wizard rebuild failed: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "output": "\n".join(output_lines) + f"\n❌ Error: {exc}",
            }

    def _help_text(self) -> str:
        return "\n".join(
            [
                OutputToolkit.banner("WIZARD"),
                "WIZARD START      Start Wizard server",
                "WIZARD STOP       Stop Wizard server",
                "WIZARD STATUS     Check Wizard server status",
                "WIZARD RESET      Wipe Wizard keystore + admin token (destructive)",
                "  --wipe-profile  Also delete memory/user/profile.json",
                "  --scrub-vault   Also delete VAULT_ROOT contents",
                "WIZARD REBUILD    Rebuild Wizard dashboard artifacts",
                "WIZARD HELP       Show this help",
            ]
        )

    def _show_help(self) -> Dict:
        return {"status": "success", "output": self._help_text()}

    def _open_dashboard(self) -> Dict:
        banner = OutputToolkit.banner("WIZARD DASHBOARD")
        _, dashboard_url = self._wizard_urls()
        try:
            webbrowser.open(dashboard_url)
            return {"status": "success", "output": banner + "\n✅ Opened Wizard Dashboard"}
        except Exception as exc:
            return {"status": "error", "message": str(exc), "output": banner + f"\n❌ {exc}"}

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
                ["python", "-c", "import wizard.server"],
                capture_output=True,
                timeout=5
            ).returncode == 0:
                output_lines.append("❌ Wizard module not found")
                return {
                    "status": "error",
                    "message": "Wizard module not available",
                    "output": "\n".join(output_lines),
                }

            # Start in background
            subprocess.Popen(
                ["python", "-m", "wizard.server", "--no-interactive"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(repo_root),
            )

            # Wait for server to be ready (max 10 seconds)
            stop = threading.Event()
            spinner = Spinner(label="Waiting for Wizard", show_elapsed=True)
            thread = spinner.start_background(stop)
            for attempt in range(20):
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

            # Timeout
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
                output_lines.append(
                    f"⚠️  Port {port} is in use or Wizard is still booting. "
                    "Check logs or stop the existing process."
                )
            else:
                output_lines.append("⚠️  Wizard Server started but slow to respond (check logs)")
            return {
                "status": "success",
                "output": "\n".join(output_lines),
            }

        except Exception as exc:
            logger.error(f"[LOCAL] Failed to start Wizard: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "output": "\n".join(output_lines) + f"\n❌ Error: {exc}",
            }

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
        archive_root = Path(repo_root) / ".archive" / "wizard-reset"
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
                if token_path.exists():
                    token_path.unlink()
                    output_lines.append(f"✅ Removed {token_path}")
            except Exception as exc:
                output_lines.append(f"⚠️  Failed to remove {token_path}: {exc}")

        if wipe_profile:
            profile_path = Path(repo_root) / "memory" / "user" / "profile.json"
            try:
                if profile_path.exists():
                    profile_path.unlink()
                    output_lines.append(f"✅ Removed {profile_path}")
            except Exception as exc:
                output_lines.append(f"⚠️  Failed to remove {profile_path}: {exc}")

        if scrub_vault:
            vault_root = Path(os.getenv("VAULT_ROOT", "")) if os.getenv("VAULT_ROOT") else Path(repo_root) / "vault-md"
            try:
                if vault_root.exists():
                    import shutil
                    shutil.rmtree(vault_root)
                    vault_root.mkdir(parents=True, exist_ok=True)
                output_lines.append(f"✅ Scrubbed VAULT_ROOT at {vault_root}")
            except Exception as exc:
                output_lines.append(f"⚠️  Failed to scrub VAULT_ROOT: {exc}")

        output_lines.append("")
        output_lines.append("Next steps:")
        output_lines.append("  1. Set WIZARD_KEY in .env")
        output_lines.append("  2. Run WIZARD START")
        output_lines.append("  3. Re-run SETUP to sync profile")

        return {"status": "success", "output": "\n".join(output_lines)}
