"""
RUN command handler - execute TS markdown runtime scripts.
"""

from pathlib import Path
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_manager import get_repo_root
from core.services.ts_runtime_service import TSRuntimeService
from core.tui.output import OutputToolkit


class RunHandler(BaseCommandHandler):
    """Handler for RUN command - execute TS markdown runtime scripts."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return {
                "status": "error",
                "message": "Usage: RUN <file> [section_id] | RUN PARSE <file>",
            }

        if params[0].upper() == "PARSE":
            if len(params) < 2:
                return {"status": "error", "message": "Usage: RUN PARSE <file>"}
            file_arg = params[1]
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

        file_arg = params[0]
        section_id = params[1] if len(params) > 1 else None

        script_path = self._resolve_path(file_arg)
        service = TSRuntimeService()
        result = service.execute(script_path, section_id=section_id)

        if result.get("status") != "success":
            return result

        payload = result.get("payload", {})
        exec_result = payload.get("result", {})
        output = exec_result.get("output") or ""
        return {
            "status": "success",
            "message": "Script executed",
            "output": output,
            "runtime": payload,
        }

    def _resolve_path(self, file_arg: str) -> Path:
        path = Path(file_arg)
        if not path.is_absolute():
            return get_repo_root() / path
        return path
