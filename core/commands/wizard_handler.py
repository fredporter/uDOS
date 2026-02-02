"""WIZARD command handler - Wizard server maintenance tasks."""

from typing import List, Dict
import subprocess
import os
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_service import get_logger, get_repo_root

logger = get_logger("wizard-handler")


class WizardHandler(BaseCommandHandler):
    """Handler for WIZARD command - maintenance and rebuild."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._show_help()

        action = params[0].lower().strip()
        if not action:
            return self._show_help()

        if action in {"rebuild", "--rebuild"}:
            return self._rebuild_wizard()
        elif action in {"start", "--start"}:
            return self._start_wizard()
        elif action in {"stop", "--stop"}:
            return self._stop_wizard()
        elif action in {"status", "--status"}:
            return self._wizard_status()
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
                "WIZARD REBUILD    Rebuild Wizard dashboard artifacts",
                "WIZARD HELP       Show this help",
            ]
        )

    def _show_help(self) -> Dict:
        return {"status": "success", "output": self._help_text()}

    def _start_wizard(self) -> Dict:
        """Start Wizard server."""
        import requests
        import time

        banner = OutputToolkit.banner("WIZARD START")
        output_lines = [banner, ""]

        # Check if already running
        try:
            resp = requests.get("http://127.0.0.1:8765/health", timeout=2)
            if resp.status_code == 200:
                output_lines.append("✅ Wizard already running on http://127.0.0.1:8765")
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
            for attempt in range(20):
                try:
                    resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                    if resp.status_code == 200:
                        output_lines.append("✅ Wizard Server started")
                        output_lines.append("📍 Server: http://127.0.0.1:8765")
                        output_lines.append("📍 Dashboard: http://127.0.0.1:8765/dashboard")
                        return {
                            "status": "success",
                            "output": "\n".join(output_lines),
                        }
                except requests.exceptions.RequestException:
                    pass
                time.sleep(0.5)

            # Timeout
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
            time.sleep(1)

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

        try:
            resp = requests.get("http://127.0.0.1:8765/health", timeout=2)
            if resp.status_code == 200:
                output_lines.append("✅ Wizard running on http://127.0.0.1:8765")
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
