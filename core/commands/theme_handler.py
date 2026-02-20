"""THEME command handler - TUI message theming (text-only)."""

from typing import Dict, List
import os

from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.services.config_sync_service import ConfigSyncManager
from core.services.error_contract import CommandError
from core.services.logging_manager import get_logger
from core.services.theme_service import get_theme_service
from core.tui.output import OutputToolkit


class ThemeHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Manage TUI message themes (text-only)."""

    def __init__(self) -> None:
        super().__init__()
        self.logger = get_logger("theme-handler")
        self.theme = get_theme_service()
        self.sync = ConfigSyncManager()

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        with self.trace_command(command, params) as trace:
            if not params:
                result = self._status()
                trace.set_status(result.get("status", "success"))
                return result

            subcommand = params[0].upper()
            args = params[1:]

            if subcommand in {"LIST", "LS"}:
                result = self._list_themes()
            elif subcommand in {"SHOW", "INFO"}:
                name = args[0] if args else self._active_theme_name()
                result = self._show_theme(name)
            elif subcommand in {"SET", "USE"}:
                if not args:
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="Theme name required",
                        recovery_hint="Usage: THEME SET <name>",
                        level="INFO",
                    )
                result = self._set_theme(args[0])
            elif subcommand in {"CLEAR", "RESET", "DEFAULT"}:
                result = self._clear_theme()
            else:
                result = self._set_theme(params[0])

            trace.set_status(result.get("status", "success"))
            return result

    def _active_theme_name(self) -> str:
        return self.theme.get_active_message_theme()

    def _available_themes(self) -> List[str]:
        return self.theme.list_message_themes()

    def _status(self) -> Dict:
        active = self._active_theme_name()
        output = [OutputToolkit.banner("TUI MESSAGE THEME"), ""]
        output.append(f"Active: {active}")
        output.append("")
        output.append("Themes:")
        for name in self._available_themes():
            marker = "*" if name == active else "-"
            output.append(f"  {marker} {name}")
        output.append("")
        output.append("Use: THEME SET <name> | THEME SHOW <name>")
        return {"status": "success", "output": "\n".join(output)}

    def _list_themes(self) -> Dict:
        return self._status()

    def _show_theme(self, name: str) -> Dict:
        canonical = self.theme.canonical_message_theme(name)
        themes = self._available_themes()
        if canonical not in themes:
            raise CommandError(
                code="ERR_VALIDATION_INVALID_ID",
                message=f"Unknown theme: {name}",
                recovery_hint=f"Available: {', '.join(themes)}",
                level="INFO",
            )

        sample_lines = [
            "ERROR: Sample error message",
            "WARN: Sample warning",
            "Tip: Sample tip",
            "Health: Sample health",
            "Wizard: Sample label",
        ]
        themed = [self.theme.format_for_theme(line, canonical) for line in sample_lines]

        output = [OutputToolkit.banner(f"THEME: {canonical}"), ""]
        output.extend(themed)
        output.append("")
        output.append("Use: THEME SET <name>")
        return {"status": "success", "output": "\n".join(output)}

    def _set_theme(self, name: str) -> Dict:
        canonical = self.theme.canonical_message_theme(name)
        themes = self._available_themes()
        if canonical not in themes:
            raise CommandError(
                code="ERR_VALIDATION_INVALID_ID",
                message=f"Unknown theme: {name}",
                recovery_hint=f"Available: {', '.join(themes)}",
                level="INFO",
            )

        updates = {self.theme.ENV_MESSAGE_THEME: None if canonical == "default" else canonical}
        ok, message = self.sync.update_env_vars(updates)
        if canonical == "default":
            os.environ.pop(self.theme.ENV_MESSAGE_THEME, None)
        else:
            os.environ[self.theme.ENV_MESSAGE_THEME] = canonical

        status = "success" if ok else "warning"
        output = f"Active theme set to {canonical}. {message}"
        return {"status": status, "output": output}

    def _clear_theme(self) -> Dict:
        updates = {self.theme.ENV_MESSAGE_THEME: None}
        ok, message = self.sync.update_env_vars(updates)
        os.environ.pop(self.theme.ENV_MESSAGE_THEME, None)
        status = "success" if ok else "warning"
        output = f"Theme override cleared. {message}"
        return {"status": status, "output": output}
