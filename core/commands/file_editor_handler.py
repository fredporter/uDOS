"""File editor commands for Core TUI."""

from typing import List, Dict
from pathlib import Path

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.editor_utils import (
    resolve_workspace_path,
    open_in_editor,
    get_memory_root,
)


class FileEditorHandler(BaseCommandHandler):
    """Handle NEW/EDIT/LOAD/SAVE commands for text files in /memory."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        cmd = command.upper()
        filename = " ".join(params).strip() if params else ""

        if cmd == "NEW":
            return self._open_editor(filename or "untitled")
        if cmd in {"EDIT", "LOAD"}:
            if not filename:
                filename = self.get_state("current_path", "")
            if not filename:
                return {
                    "status": "error",
                    "message": f"{cmd} requires a filename",
                }
            return self._open_editor(filename)
        if cmd == "SAVE":
            if not filename:
                filename = self.get_state("current_path", "")
            if not filename:
                return {
                    "status": "error",
                    "message": "SAVE requires a filename",
                }
            return self._open_editor(filename)

        return {"status": "error", "message": f"Unknown command: {cmd}"}

    def has_active_file(self) -> bool:
        return bool(self.get_state("current_path"))

    def _open_editor(self, filename: str) -> Dict:
        try:
            path = resolve_workspace_path(filename)
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}

        ok, editor_name = open_in_editor(path)
        if not ok:
            return {"status": "error", "message": editor_name}

        memory_root = get_memory_root().resolve()
        try:
            rel = path.resolve().relative_to(memory_root).as_posix()
        except ValueError:
            rel = path.as_posix()
        self.set_state("current_path", rel)

        output = "\n".join(
            [
                OutputToolkit.banner("FILE EDITOR"),
                f"Editor: {editor_name}",
                f"Path: {path}",
            ]
        )
        return {"status": "success", "message": "Editor opened", "output": output}
