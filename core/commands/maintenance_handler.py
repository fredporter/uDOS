"""Maintenance command handler - BACKUP/RESTORE/TIDY/CLEAN/COMPOST/DESTROY."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Dict, List, Tuple

from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.tui.output import OutputToolkit
from core.tui.ui_elements import ProgressBar
from core.services.logging_api import get_repo_root
from core.services.maintenance_utils import (
    create_backup,
    restore_backup,
    tidy,
    clean,
    compost,
    list_backups,
    default_repo_allowlist,
    default_memory_allowlist,
    get_memory_root,
)


class MaintenanceHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handle maintenance commands (backup/restore/tidy/clean/compost/destroy)."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        with self.trace_command(command, params) as trace:
            result = self._handle_impl(command, params, grid, parser)
            if isinstance(result, dict):
                status = result.get("status")
                if status:
                    trace.set_status(status)
            return result

    def _handle_impl(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        cmd = command.upper()
        try:
            from core.services.user_service import is_ghost_mode

            if is_ghost_mode():
                return self._ghost_mode_block(cmd, params)

            if cmd == "BACKUP":
                return self._handle_backup(params)
            if cmd == "RESTORE":
                return self._handle_restore(params)
            if cmd == "TIDY":
                return self._handle_tidy(params)
            if cmd == "CLEAN":
                return self._handle_clean(params)
            if cmd == "COMPOST":
                return self._handle_compost(params)
            if cmd == "DESTROY":
                return self._handle_destroy(params)
            if cmd == "UNDO":
                return self._handle_undo(params)
        except Exception as exc:
            return {"status": "error", "message": f"{cmd} failed: {exc}"}

        return {"status": "error", "message": f"Unknown command: {cmd}"}

    def _ghost_mode_block(self, cmd: str, params: List[str]) -> Dict:
        """Return a dry-run response for destructive commands in Ghost Mode."""
        scope, remaining = self._parse_scope(params)
        label = " ".join(remaining).strip()
        output = "\n".join(
            [
                OutputToolkit.banner(f"{cmd} (DRY-RUN)"),
                "Ghost Mode active: destructive commands run in check-only mode.",
                f"Scope: {scope}",
                f"Args: {' '.join(params) if params else '(none)'}",
                f"Note: No files were modified. Run SETUP to exit Ghost Mode.",
            ]
        )
        return {
            "status": "warning",
            "message": f"{cmd} blocked in Ghost Mode",
            "output": output,
            "dry_run": True,
            "scope": scope,
            "label": label,
        }

    def _parse_scope(self, params: List[str]) -> Tuple[str, List[str]]:
        if not params:
            return "workspace", []
        scope = params[0].lower()
        if scope in {"current", "+subfolders", "workspace", "all"}:
            return scope, params[1:]
        return "workspace", params

    def _resolve_scope(self, scope: str) -> Tuple[Path, bool]:
        if scope == "current":
            return Path.cwd(), False
        if scope == "+subfolders":
            return Path.cwd(), True
        if scope == "all":
            return get_repo_root(), True
        return get_memory_root(), True

    def _handle_backup(self, params: List[str]) -> Dict:
        scope, remaining = self._parse_scope(params)
        label = "backup" if not remaining else " ".join(remaining)
        target_root, _recursive = self._resolve_scope(scope)

        progress = self._progress_callback("BACKUP")
        archive_path, manifest_path = create_backup(target_root, label, on_progress=progress)
        output = "\n".join(
            [
                OutputToolkit.banner("BACKUP"),
                f"Scope: {scope}",
                f"Target: {target_root}",
                f"Archive: {archive_path}",
                f"Manifest: {manifest_path}",
            ]
        )
        return {"status": "success", "message": "Backup created", "output": output}

    def _handle_restore(self, params: List[str]) -> Dict:
        scope, remaining = self._parse_scope(params)
        target_root, _recursive = self._resolve_scope(scope)
        force = False
        if "--force" in remaining:
            force = True
            remaining = [p for p in remaining if p != "--force"]

        archive = None
        if remaining:
            candidate = Path(remaining[0])
            if candidate.exists():
                archive = candidate
        if archive is None:
            backups = list_backups(target_root)
            if not backups:
                return {
                    "status": "error",
                    "message": f"No backups found in {target_root / '.backup'}",
                }
            archive = backups[0]

        try:
            progress = self._progress_callback("RESTORE")
            message = restore_backup(archive, target_root, force=force, on_progress=progress)
        except FileExistsError as exc:
            return {
                "status": "error",
                "message": str(exc),
                "hint": "Use RESTORE --force to overwrite existing files",
            }

        output = "\n".join(
            [
                OutputToolkit.banner("RESTORE"),
                f"Scope: {scope}",
                f"Archive: {archive}",
                f"Target: {target_root}",
            ]
        )
        return {"status": "success", "message": message, "output": output}

    def _handle_tidy(self, params: List[str]) -> Dict:
        scope, _remaining = self._parse_scope(params)
        target_root, recursive = self._resolve_scope(scope)
        moved, archive_root = tidy(target_root, recursive=recursive)
        output = "\n".join(
            [
                OutputToolkit.banner("TIDY"),
                f"Scope: {scope}",
                f"Target: {target_root}",
                f"Moved: {moved}",
                f"Archive: {archive_root}",
            ]
        )
        return {"status": "success", "message": "Tidy complete", "output": output}

    def _handle_clean(self, params: List[str]) -> Dict:
        scope, _remaining = self._parse_scope(params)
        target_root, recursive = self._resolve_scope(scope)
        if target_root == get_repo_root():
            allowlist = default_repo_allowlist()
        elif target_root == get_memory_root():
            allowlist = default_memory_allowlist()
        else:
            allowlist = []
        moved, archive_root = clean(
            target_root,
            allowed_entries=allowlist,
            recursive=recursive,
        )
        output = "\n".join(
            [
                OutputToolkit.banner("CLEAN"),
                f"Scope: {scope}",
                f"Target: {target_root}",
                f"Moved: {moved}",
                f"Archive: {archive_root}",
            ]
        )
        return {"status": "success", "message": "Clean complete", "output": output}

    def _handle_compost(self, params: List[str]) -> Dict:
        scope, _remaining = self._parse_scope(params)
        target_root, recursive = self._resolve_scope(scope)
        moved, compost_root = compost(target_root, recursive=recursive)
        output = "\n".join(
            [
                OutputToolkit.banner("COMPOST"),
                f"Scope: {scope}",
                f"Target: {target_root}",
                f"Moved: {moved}",
                f"Compost: {compost_root}",
            ]
        )
        return {"status": "success", "message": "Compost complete", "output": output}

    def _handle_destroy(self, params: List[str]) -> Dict:
        return {
            "status": "error",
            "message": "DESTROY is only available from the Dev TUI.",
            "hint": "Launch the Dev TUI and run DESTROY there (requires confirmation).",
        }

    def _handle_undo(self, params: List[str]) -> Dict:
        scope, remaining = self._parse_scope(params)
        target_root, _recursive = self._resolve_scope(scope)

        backups = list_backups(target_root)
        if not backups:
            return {
                "status": "error",
                "message": f"No backups found to undo in {target_root / '.backup'}",
            }

        latest = backups[0]
        try:
            progress = self._progress_callback("RESTORE")
            message = restore_backup(latest, target_root, force=True, on_progress=progress)
        except FileExistsError as exc:
            return {
                "status": "error",
                "message": str(exc),
                "hint": "Use RESTORE --force if you need to overwrite existing files",
            }
        except Exception as exc:
            return {
                "status": "error",
                "message": f"UNDO failed: {exc}",
            }

        output = "\n".join(
            [
                OutputToolkit.banner("UNDO"),
                f"Scope: {scope}",
                f"Archive: {latest.name}",
                f"Target: {target_root}",
                f"Message: {message}",
            ]
        )
        return {"status": "success", "message": "Restored last backup", "output": output}

    def _progress_callback(self, label: str):
        if not sys.stdout.isatty():
            return None

        bar = ProgressBar(total=1, width=28)

        def _callback(current: int, total: int, detail: str) -> None:
            if total > 0:
                bar.total = total
            detail_label = self._format_progress_detail(detail)
            line = bar.render(current, label=label)
            if detail_label:
                line = f"{line} {detail_label}"
            sys.stdout.write("\r" + line)
            sys.stdout.flush()
            if total > 0 and current >= total:
                sys.stdout.write("\n")
                sys.stdout.flush()

        return _callback

    @staticmethod
    def _format_progress_detail(detail: str) -> str:
        if not detail:
            return ""
        if "/" in detail or "\\" in detail:
            detail = Path(detail).name
        if len(detail) > 32:
            return detail[:29] + "..."
        return detail
