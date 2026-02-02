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
        if action in {"help", "--help", "?"}:
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

            # Add timeout to prevent hanging
            result = subprocess.run(
                ["bash", "-lc", rebuild_cmd],
                capture_output=True,
                text=True,
                check=False,
                timeout=300,  # 5 minute timeout
                cwd=str(repo_root),
            )

            if result.stdout:
                output_lines.append(result.stdout.strip())
            if result.stderr:
                output_lines.append(result.stderr.strip())

            if result.returncode != 0:
                logger.error(f"[LOCAL] Wizard rebuild failed with code {result.returncode}")
                return {
                    "status": "error",
                    "message": f"Rebuild failed (exit {result.returncode})",
                    "output": "\n".join(output_lines),
                }

            output_lines.append("\n✅ Wizard rebuild complete")
            logger.info("[LOCAL] Wizard rebuild successful")
            return {
                "status": "success",
                "output": "\n".join(output_lines),
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
                "WIZARD REBUILD    Rebuild Wizard dashboard artifacts",
                "WIZARD HELP       Show this help",
            ]
        )

    def _show_help(self) -> Dict:
        return {"status": "success", "output": self._help_text()}
