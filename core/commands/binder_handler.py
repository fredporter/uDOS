"""
Binder Handler

Core binder operations for TUI:
- BINDER            -> open file picker for binder folder
- BINDER PICK [dir] -> pick binder folder from start dir
- BINDER COMPILE <binder_id> [formats...]
- BINDER CHAPTERS <binder_id>
"""

from typing import Dict, List

from pathlib import Path

from core.binder import BinderCompiler
from core.commands.base import BaseCommandHandler
from core.tui.file_browser import FileBrowser
from core.tui.output import OutputToolkit
from core.services.logging_api import get_repo_root


class BinderHandler(BaseCommandHandler):
    """Handler for BINDER command - binder selection and compilation."""

    def __init__(self):
        super().__init__()
        self._spatial_handler = None

    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        if not params:
            return self._pick_binder(".")

        subcommand = params[0].upper()

        if subcommand in {"OPEN", "LIST", "ADD"}:
            return self._handle_workspace_subcommand(command, subcommand, params[1:])

        if subcommand == "PICK":
            start_dir = params[1] if len(params) > 1 else "."
            return self._pick_binder(start_dir)

        if subcommand == "COMPILE":
            from core.services.user_service import is_ghost_mode

            if is_ghost_mode():
                return {
                    "status": "warning",
                    "message": "Ghost Mode is read-only (BINDER COMPILE blocked)",
                    "output": "Ghost Mode active: compilation is disabled.",
                }

            if len(params) < 2:
                picker = FileBrowser(start_dir=str(self._default_binder_root()), pick_directories=True)
                selected = picker.pick()
                if not selected:
                    return {"status": "cancelled", "message": "Binder selection cancelled"}
                binder_id = Path(selected).name
            else:
                binder_id = params[1]
            formats = params[2:] if len(params) > 2 else None
            compiler = BinderCompiler()
            result = _run_async(
                compiler.compile_binder(binder_id=binder_id, formats=formats)
            )
            outputs = result.get("outputs", []) if isinstance(result, dict) else []
            rows = [
                [out.get("format", ""), out.get("path", ""), out.get("status", "")]
                for out in outputs
            ]
            output = "\n".join(
                [
                    OutputToolkit.banner("BINDER COMPILE"),
                    f"Binder: {binder_id}",
                    f"Formats: {', '.join(formats) if formats else 'default'}",
                    "",
                    OutputToolkit.table(["format", "path", "status"], rows)
                    if rows
                    else "No outputs produced.",
                ]
            )
            return {
                "status": "success",
                "message": "Binder compiled",
                "output": output,
                "binder_id": binder_id,
                "result": result,
            }

        if subcommand == "CHAPTERS":
            if len(params) < 2:
                return {"status": "error", "message": "BINDER CHAPTERS <binder_id>"}
            binder_id = params[1]
            compiler = BinderCompiler()
            chapters = _run_async(compiler.get_chapters(binder_id=binder_id))
            rows = [
                [
                    chapter.get("chapter_id", ""),
                    chapter.get("title", ""),
                    chapter.get("status", ""),
                    str(chapter.get("word_count", 0)),
                ]
                for chapter in chapters
            ]
            output = "\n".join(
                [
                    OutputToolkit.banner("BINDER CHAPTERS"),
                    OutputToolkit.table(["id", "title", "status", "words"], rows)
                    if rows
                    else "No chapters found.",
                ]
            )
            return {
                "status": "success",
                "message": "Binder chapters",
                "output": output,
                "binder_id": binder_id,
                "chapters": chapters,
            }

        return {"status": "error", "message": f"Unknown BINDER subcommand: {subcommand}"}

    def _pick_binder(self, start_dir: str) -> Dict:
        browser = FileBrowser(start_dir=start_dir, pick_directories=True)
        selected = browser.pick()
        if not selected:
            return {"status": "warning", "message": "Binder selection cancelled"}
        output = "\n".join(
            [
                OutputToolkit.banner("BINDER PICK"),
                f"Selected: {selected}",
            ]
        )
        return {
            "status": "success",
            "message": "Binder selected",
            "output": output,
            "binder_path": str(selected),
        }

    def _default_binder_root(self) -> Path:
        return get_repo_root() / "memory" / "vault" / "bank" / "binders"

    def _handle_workspace_subcommand(
        self, command: str, subcommand: str, params: List[str]
    ) -> Dict:
        from core.commands.spatial_filesystem_handler import (
            SpatialFilesystemHandler,
            dispatch_spatial_command,
        )

        if self._spatial_handler is None:
            self._spatial_handler = SpatialFilesystemHandler()

        args = [command, subcommand] + params
        output = dispatch_spatial_command(self._spatial_handler, args)
        status = "error" if output.startswith("❌") else "success"
        return {
            "status": status,
            "message": output.splitlines()[0] if output else "Binder command complete",
            "output": output,
        }


def _run_async(coro):
    """Run async coroutines from sync handler context."""
    import asyncio

    return asyncio.run(coro)
