"""Binder Handler

Core binder operations for TUI:
- BINDER            -> open file picker for binder folder
- BINDER PICK [dir] -> pick binder folder from start dir
- BINDER COMPILE <binder_id> [formats...]
- BINDER CHAPTERS <binder_id>
"""

from __future__ import annotations

from pathlib import Path

from core.binder import BinderCompiler
from core.commands.base import BaseCommandHandler
from core.services.error_contract import CommandError
from core.services.vibe_binder_service import get_binder_service
from core.services.logging_api import get_repo_root
from core.tui.file_browser import FileBrowser
from core.tui.output import OutputToolkit


class BinderHandler(BaseCommandHandler):
    """Handler for BINDER command - binder selection and compilation."""

    def __init__(self):
        super().__init__()
        self._spatial_handler = None

    def handle(self, command: str, params: list[str], grid, parser) -> dict:
        if not params:
            return self._pick_binder(".")

        subcommand = params[0].upper()

        if subcommand in {"OPEN", "LIST", "ADD"}:
            return self._handle_workspace_subcommand(command, subcommand, params[1:])

        if subcommand == "PICK":
            start_dir = params[1] if len(params) > 1 else "."
            return self._pick_binder(start_dir)

        if subcommand == "IMPORT-RESEARCH":
            if len(params) < 3:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Usage: BINDER IMPORT-RESEARCH <binder_id> <note_id> [action]",
                    recovery_hint="Provide a binder ID and persisted research note id",
                    level="INFO",
                )
            binder_id = params[1]
            note_id = params[2]
            action = params[3].lower() if len(params) > 3 else "research"
            result = get_binder_service().import_research_artifact(
                binder_id,
                note_id,
                action=action,
            )
            if result.get("status") != "success":
                return result
            output = "\n".join([
                OutputToolkit.banner("BINDER IMPORT RESEARCH"),
                f"Binder: {binder_id}",
                f"Note: {note_id}",
                f"Action: {action}",
                f"Imported copy: {result['imported']['target_path']}",
                f"Processed snapshot: {result['imported']['processed_snapshot']}",
                f"Move: {result['move'].get('id', result.get('move_id', 'n/a'))}",
            ])
            result["output"] = output
            return result

        if subcommand == "COMPILE":
            
            from core.services.user_service import is_ghost_mode

            if is_ghost_mode():
                logger.warning(
                    "[TESTING ALERT] Ghost Mode active: BINDER COMPILE in demo mode (v1.5). "
                    "Enforcement will be added before v1.5 release."
                )

            if len(params) < 2:
                picker = FileBrowser(
                    start_dir=str(self._default_binder_root()), pick_directories=True
                )
                selected = picker.pick()
                if not selected:
                    return {
                        "status": "cancelled",
                        "message": "Binder selection cancelled",
                    }
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
            output = "\n".join([
                OutputToolkit.banner("BINDER COMPILE"),
                f"Binder: {binder_id}",
                f"Formats: {', '.join(formats) if formats else 'default'}",
                "",
                OutputToolkit.table(["format", "path", "status"], rows)
                if rows
                else "No outputs produced.",
            ])
            return {
                "status": "success",
                "message": "Binder compiled",
                "output": output,
                "binder_id": binder_id,
                "result": result,
            }

        if subcommand == "CHAPTERS":
            if len(params) < 2:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Usage: BINDER CHAPTERS <binder_id>",
                    recovery_hint="Provide a binder ID",
                    level="INFO",
                )
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
            output = "\n".join([
                OutputToolkit.banner("BINDER CHAPTERS"),
                OutputToolkit.table(["id", "title", "status", "words"], rows)
                if rows
                else "No chapters found.",
            ])
            return {
                "status": "success",
                "message": "Binder chapters",
                "output": output,
                "binder_id": binder_id,
                "chapters": chapters,
            }

        raise CommandError(
            code="ERR_COMMAND_NOT_FOUND",
            message=f"Unknown BINDER subcommand: {subcommand}",
            recovery_hint="Use BINDER PICK, IMPORT-RESEARCH, COMPILE, or CHAPTERS",
            level="INFO",
        )

    def _pick_binder(self, start_dir: str) -> dict:
        browser = FileBrowser(start_dir=start_dir, pick_directories=True)
        selected = browser.pick()
        if not selected:
            return {"status": "warning", "message": "Binder selection cancelled"}
        output = "\n".join([
            OutputToolkit.banner("BINDER PICK"),
            f"Selected: {selected}",
        ])
        return {
            "status": "success",
            "message": "Binder selected",
            "output": output,
            "binder_path": str(selected),
        }

    def _default_binder_root(self) -> Path:
        return get_repo_root() / "memory" / "vault" / "bank" / "binders"

    def _handle_workspace_subcommand(
        self, command: str, subcommand: str, params: list[str]
    ) -> dict:
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
