"""WIZARD command handler - Wizard server maintenance tasks."""

from typing import List, Dict
import subprocess
from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_service import get_logger, get_repo_root

logger = get_logger("wizard-handler")


class WizardHandler(BaseCommandHandler):
    """Handler for WIZARD command - maintenance and rebuild."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._show_help()

        action = params[0].lower()
        if action in {"rebuild", "--rebuild"}:
            return self._rebuild_wizard()
        if action in {"help", "--help"}:
            return self._show_help()

        return {
            "status": "error",
            "message": f"Unknown option: {action}",
            "output": self._help_text(),
        }

    def _rebuild_wizard(self) -> Dict:
        repo_root = get_repo_root()
        banner = OutputToolkit.banner("WIZARD REBUILD")
        output_lines = [banner, ""]

        try:
            rebuild_cmd = (
                f"source \"{repo_root}/bin/udos-common.sh\" "
                "&& export UDOS_FORCE_REBUILD=1 "
                "&& rebuild_wizard_dashboard"
            )
            result = subprocess.run(
                ["bash", "-lc", rebuild_cmd],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout:
                output_lines.append(result.stdout.strip())
            if result.stderr:
                output_lines.append(result.stderr.strip())

            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": "Wizard rebuild failed",
                    "output": "\n".join(output_lines),
                }

            output_lines.append("\n✅ Wizard rebuild complete")
            return {
                "status": "success",
                "output": "\n".join(output_lines),
            }
        except Exception as exc:
            logger.error(f"[LOCAL] Wizard rebuild failed: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "output": "\n".join(output_lines),
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
