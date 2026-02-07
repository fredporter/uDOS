"""Integration command handler - GitHub + Mistral/Ollama status and wiring."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.services.logging_api import get_repo_root
from core.services.user_service import get_user_manager, Permission
from core.tui.output import OutputToolkit


class IntegrationHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handler for INTEGRATION command - surfaces GitHub/Mistral wiring."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """Entry point for INTEGRATION command."""
        with self.trace_command(command, params) as trace:
            user, error = self._require_permission()
            if error:
                return error

            action = (params[0].lower() if params else "status")
            if action == "status":
                result = self._status()
            elif action == "github":
                result = self._github_section()
            elif action in {"mistral", "ollama"}:
                result = self._mistral_section()
            else:
                result = {
                    "status": "error",
                    "message": "Unknown action",
                    "output": self._usage(),
                }

            if isinstance(result, dict):
                trace.set_status(result.get("status", "success"))
            return result

    def _require_permission(self):
        user_mgr = get_user_manager()
        user = user_mgr.current()
        if not user_mgr.has_permission(Permission.CONFIG):
            self.log_permission_denied("INTEGRATION", "missing config permission")
            return None, {
                "status": "error",
                "message": "Permission denied for INTEGRATION (CONFIG required)",
            }
        return user, None

    def _status(self) -> Dict:
        lines = [OutputToolkit.banner("INTEGRATION STATUS"), ""]
        lines.extend(self._github_section().get("lines", []))
        lines.append("")
        lines.extend(self._mistral_section().get("lines", []))
        lines.append("")
        lines.append("Playbook:")
        lines.append("  • Use CONFIG $GITHUB_TOKEN <token> or the Wizard config page (Config → Integrations → GitHub) to wire GitHub CLI/auto-sync.")
        lines.append("  • Use CONFIG $MISTRAL_API_KEY and CONFIG $OLLAMA_API_KEY, then run the Wizard AI settings (Config → AI → Vibe/Ollama) to enable offline engines.")
        lines.append("  • REPAIR --refresh-runtime wipes the integration caches so the latest GitHub/Mistral assets can reinstall cleanly.")
        return {"status": "success", "output": "\n".join(lines)}

    def _github_section(self) -> Dict:
        repo_root = get_repo_root()
        wizard_root = repo_root.parent / "wizard"
        github_dir = wizard_root / "github_integration"
        is_present = github_dir.exists()
        token = self._read_env_var("GITHUB_TOKEN")
        mask = self._mask_value(token)
        lines = [
            "GitHub Integration:",
            f"  • Module folder: {github_dir} ({'found' if is_present else 'missing'})",
            f"  • Token configured: {'yes' if token else 'no'} ({mask})",
            "  • CLI focus: run `python -m wizard.github_integration` tasks or press HELP → Github → CLI to see available commands.",
        ]
        return {"status": "success", "lines": lines}

    def _mistral_section(self) -> Dict:
        repo_root = get_repo_root()
        root_parent = repo_root.parent
        library_root = root_parent / "library"
        wizard_root = root_parent / "wizard"
        vibe_dir = library_root / "mistral-vibe"
        ollama_dir = library_root / "ollama"
        vibe_service = wizard_root / "services" / "mistral_vibe.py"
        ollama_cli = shutil.which("ollama") is not None
        env_keys = {
            "MISTRAL_API_KEY": self._mask_value(self._read_env_var("MISTRAL_API_KEY")),
            "OLLAMA_API_KEY": self._mask_value(self._read_env_var("OLLAMA_API_KEY")),
        }
        lines = [
            "Mistral / Ollama Integration:",
            f"  • Vibe CLI folder: {vibe_dir} ({'present' if vibe_dir.exists() else 'missing'})",
            f"  • Vibe service loader: {vibe_service} ({'ready' if vibe_service.exists() else 'missing'})",
            f"  • Ollama container: {ollama_dir} ({'present' if ollama_dir.exists() else 'missing'})",
            f"  • Ollama CLI on PATH: {'yes' if ollama_cli else 'no'}",
            f"  • Keys: MISTRAL={env_keys['MISTRAL_API_KEY']}, OLLAMA={env_keys['OLLAMA_API_KEY']}",
            "  • Wizard config (Config → AI) toggles: Vibe Agent, Ollama provider, local key material.",
        ]
        return {"status": "success", "lines": lines}

    def _usage(self) -> str:
        return (
            "Usage: INTEGRATION [status|github|mistral|ollama]\n"
            "  status  - Show both GitHub and Mistral/Ollama wiring\n"
            "  github  - Show GitHub integration status\n"
            "  mistral - Show Mistral/Ollama assets and API key wiring (Ollama included)\n"
        )

    def _read_env_var(self, key: str) -> Optional[str]:
        env_file = get_repo_root() / ".env"
        if not env_file.exists():
            return os.environ.get(key)
        for line in env_file.read_text().splitlines():
            if not line.strip() or line.strip().startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == key:
                return v.strip()
        return os.environ.get(key)

    def _mask_value(self, value: Optional[str]) -> str:
        if not value:
            return "<not set>"
        if len(value) <= 8:
            return value
        return f"{value[:4]}...{value[-4:]}"
