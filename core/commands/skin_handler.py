"""SKIN command handler - Wizard GUI theme packs (HTML/CSS)."""

from typing import Dict, List, Optional
import json
import os
from pathlib import Path

from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.services.config_sync_service import ConfigSyncManager
from core.services.error_contract import CommandError
from core.services.logging_api import get_repo_root
from core.services.logging_manager import get_logger
from core.tui.output import OutputToolkit


class SkinHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Manage Wizard GUI skins stored under /themes."""

    ENV_SKIN = "UDOS_WIZARD_SKIN"

    def __init__(self) -> None:
        super().__init__()
        self.logger = get_logger("skin-handler")
        self.sync = ConfigSyncManager()
        self.repo_root = get_repo_root()
        self.skin_root = self.repo_root / "themes"

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        with self.trace_command(command, params) as trace:
            if not params:
                result = self._status()
                trace.set_status(result.get("status", "success"))
                return result

            subcommand = params[0].upper()
            args = params[1:]

            if subcommand in {"LIST", "LS"}:
                result = self._list_skins()
            elif subcommand in {"SHOW", "INFO"}:
                name = args[0] if args else self._active_skin()
                result = self._show_skin(name)
            elif subcommand in {"SET", "USE"}:
                if not args:
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="Skin name required",
                        recovery_hint="Usage: SKIN SET <name>",
                        level="INFO",
                    )
                result = self._set_skin(args[0])
            elif subcommand in {"CLEAR", "RESET", "DEFAULT"}:
                result = self._clear_skin()
            else:
                result = self._set_skin(params[0])

            trace.set_status(result.get("status", "success"))
            return result

    def _active_skin(self) -> str:
        value = os.environ.get(self.ENV_SKIN)
        if value:
            return value
        env = self.sync.load_env_dict()
        return env.get(self.ENV_SKIN, "default")

    def _skin_dirs(self) -> List[Path]:
        if not self.skin_root.exists():
            return []
        return sorted([p for p in self.skin_root.iterdir() if p.is_dir()])

    def _skin_meta(self, skin_name: str) -> Optional[Dict[str, str]]:
        skin_dir = self.skin_root / skin_name
        meta_path = skin_dir / "theme.json"
        if not meta_path.exists():
            return None
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            return {
                "name": str(data.get("name") or skin_name),
                "version": str(data.get("version") or ""),
                "description": str(data.get("description") or ""),
            }
        except Exception as exc:
            self.logger.warning(f"Failed to read skin metadata: {exc}")
            return {"name": skin_name, "version": "", "description": ""}

    def _available_skins(self) -> List[str]:
        skins = []
        for skin_dir in self._skin_dirs():
            if (skin_dir / "theme.json").exists():
                skins.append(skin_dir.name)
        return skins

    def _status(self) -> Dict:
        active = self._active_skin()
        output = [OutputToolkit.banner("WIZARD GUI SKINS"), ""]
        output.append(f"Active: {active}")
        output.append("")
        output.append("Skins:")
        for name in self._available_skins():
            marker = "*" if name == active else "-"
            output.append(f"  {marker} {name}")
        output.append("")
        output.append("Use: SKIN SET <name> | SKIN SHOW <name>")
        return {"status": "success", "output": "\n".join(output)}

    def _list_skins(self) -> Dict:
        return self._status()

    def _show_skin(self, name: str) -> Dict:
        skins = self._available_skins()
        if name not in skins:
            raise CommandError(
                code="ERR_VALIDATION_INVALID_ID",
                message=f"Unknown skin: {name}",
                recovery_hint=f"Available: {', '.join(skins)}",
                level="INFO",
            )

        meta = self._skin_meta(name) or {"name": name, "version": "", "description": ""}
        output = [OutputToolkit.banner(f"SKIN: {name}"), ""]
        output.append(f"Name: {meta.get('name', name)}")
        if meta.get("version"):
            output.append(f"Version: {meta.get('version')}")
        if meta.get("description"):
            output.append(f"Description: {meta.get('description')}")
        output.append("")
        output.append("Use: SKIN SET <name>")
        return {"status": "success", "output": "\n".join(output)}

    def _set_skin(self, name: str) -> Dict:
        skins = self._available_skins()
        if name != "default" and name not in skins:
            raise CommandError(
                code="ERR_VALIDATION_INVALID_ID",
                message=f"Unknown skin: {name}",
                recovery_hint=f"Available: {', '.join(skins)}",
                level="INFO",
            )

        updates = {self.ENV_SKIN: None if name == "default" else name}
        ok, message = self.sync.update_env_vars(updates)
        if name == "default":
            os.environ.pop(self.ENV_SKIN, None)
        else:
            os.environ[self.ENV_SKIN] = name

        status = "success" if ok else "warning"
        output = f"Active skin set to {name}. {message}"
        return {"status": status, "output": output}

    def _clear_skin(self) -> Dict:
        updates = {self.ENV_SKIN: None}
        ok, message = self.sync.update_env_vars(updates)
        os.environ.pop(self.ENV_SKIN, None)
        status = "success" if ok else "warning"
        output = f"Skin override cleared. {message}"
        return {"status": status, "output": output}
