"""EMPIRE command handler - private extension controls."""

from __future__ import annotations

import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("empire-handler")


class EmpireHandler(BaseCommandHandler):
    """Handler for EMPIRE command - start/stop/rebuild and suite launch."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._show_help()

        action = params[0].lower().strip()
        if not action:
            return self._show_help()

        from core.services.user_service import is_ghost_mode

        if is_ghost_mode() and action in {"rebuild", "--rebuild", "start", "--start", "stop", "--stop"}:
            return {
                "status": "warning",
                "message": "Ghost Mode is read-only (Empire control blocked)",
                "output": self._help_text(),
            }

        if action in {"rebuild", "--rebuild"}:
            return self._rebuild_empire()
        if action in {"start", "--start"}:
            return self._start_empire()
        if action in {"stop", "--stop"}:
            return self._stop_empire()
        if action in {"help", "--help", "?"}:
            return self._show_help()

        return {
            "status": "error",
            "message": f"Unknown option: {action}",
            "output": self._help_text(),
        }

    def _empire_root(self) -> Optional[Path]:
        repo_root = get_repo_root()
        path = Path(repo_root) / "empire"
        return path if path.exists() else None

    def _suite_path(self) -> Optional[Path]:
        root = self._empire_root()
        if not root:
            return None
        suite = root / "web" / "index.html"
        return suite if suite.exists() else None

    def _prompt_open_suite(self, suite_path: Path) -> Optional[bool]:
        try:
            response = input("Open Empire Suite...? [Yes|No|OK] ").strip().lower()
        except Exception:
            return None
        if response in {"yes", "y", "ok", "okay"}:
            return True
        if response in {"no", "n"}:
            return False
        return None

    def _open_suite(self, suite_path: Path) -> str:
        try:
            webbrowser.open(suite_path.resolve().as_uri())
            return f"✅ Opened Empire Suite: {suite_path}"
        except Exception as exc:
            logger.error(f"[LOCAL] Failed to open Empire Suite: {exc}")
            return f"❌ Failed to open Empire Suite: {exc}"

    def _show_help(self) -> Dict:
        return {"status": "success", "output": self._help_text()}

    def _help_text(self) -> str:
        return "\n".join(
            [
                OutputToolkit.banner("EMPIRE"),
                "EMPIRE START      Start Empire services",
                "EMPIRE STOP       Stop Empire services",
                "EMPIRE REBUILD    Rebuild Empire suite assets",
                "EMPIRE HELP       Show this help",
            ]
        )

    def _start_empire(self) -> Dict:
        banner = OutputToolkit.banner("EMPIRE START")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        output_lines.append("✅ Empire extension detected")
        suite_path = self._suite_path()
        if suite_path:
            decision = self._prompt_open_suite(suite_path)
            if decision:
                output_lines.append(self._open_suite(suite_path))
            elif decision is False:
                output_lines.append("Skipped opening Empire Suite")
            else:
                output_lines.append("No response; Empire Suite not opened")
        else:
            output_lines.append("⚠️  Empire Suite page not found (web/index.html)")

        return {"status": "success", "output": "\n".join(output_lines)}

    def _stop_empire(self) -> Dict:
        banner = OutputToolkit.banner("EMPIRE STOP")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        output_lines.append("Stopping Empire services...")
        output_lines.append("✅ Empire stopped (no background services running)")
        return {"status": "success", "output": "\n".join(output_lines)}

    def _rebuild_empire(self) -> Dict:
        banner = OutputToolkit.banner("EMPIRE REBUILD")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        web_root = empire_root / "web"
        package_json = web_root / "package.json"
        if package_json.exists():
            try:
                result = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=str(web_root),
                    capture_output=False,
                    check=False,
                )
                if result.returncode != 0:
                    output_lines.append("❌ Empire build failed")
                    return {"status": "error", "output": "\n".join(output_lines)}
                output_lines.append("✅ Empire build complete")
                return {"status": "success", "output": "\n".join(output_lines)}
            except Exception as exc:
                output_lines.append(f"❌ Empire build error: {exc}")
                return {"status": "error", "output": "\n".join(output_lines)}

        output_lines.append("✅ Empire rebuild skipped (no build system detected)")
        return {"status": "success", "output": "\n".join(output_lines)}
