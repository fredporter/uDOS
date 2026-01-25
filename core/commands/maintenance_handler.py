"""Maintenance command handler - BACKUP/RESTORE/TIDY/CLEAN/COMPOST/DESTROY."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_manager import get_repo_root
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


class MaintenanceHandler(BaseCommandHandler):
    """Handle maintenance commands (backup/restore/tidy/clean/compost/destroy)."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        cmd = command.upper()
        try:
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
        except Exception as exc:
            return {"status": "error", "message": f"{cmd} failed: {exc}"}

        return {"status": "error", "message": f"Unknown command: {cmd}"}

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

        archive_path, manifest_path = create_backup(target_root, label)
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
            message = restore_backup(archive, target_root, force=force)
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
