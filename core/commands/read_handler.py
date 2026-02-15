"""READ command handler - parse TS markdown runtime files."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_repo_root
from core.services.ts_runtime_service import TSRuntimeService
from core.tui.output import OutputToolkit


class ReadHandler(BaseCommandHandler):
    """Handler for READ command."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return {"status": "error", "message": "Usage: READ [--ts] <file>"}

        args = params[:]
        if args and args[0].lower() == "--ts":
            args = args[1:]
        if not args:
            return {"status": "error", "message": "Usage: READ [--ts] <file>"}

        file_arg = args[0]
        script_path = self._resolve_path(file_arg)

        service = TSRuntimeService()
        result = service.parse(script_path)
        if result.get("status") != "success":
            return result

        payload = result.get("payload", {})
        sections = payload.get("sections", [])
        if not sections:
            return {
                "status": "success",
                "message": "Parsed script",
                "output": "No sections found.",
            }

        rows = [
            [section.get("id", ""), section.get("title", ""), section.get("blocks", 0)]
            for section in sections
        ]
        output = OutputToolkit.table(["id", "title", "blocks"], rows)
        return {
            "status": "success",
            "message": "Parsed script",
            "output": output,
            "sections": sections,
        }

    def _resolve_path(self, file_arg: str) -> Path:
        path = Path(file_arg)
        if not path.is_absolute():
            return get_repo_root() / path
        return path
