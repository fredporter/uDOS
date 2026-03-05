"""Binder Manager (Stub).

Provides canonical binder paths and minimal workflow hooks.
All binders live under ``VAULT_ROOT/@binders/<binder_id>`` and contain a
binder-local ``sandbox/`` and ``.compost/`` for work-in-progress and retention.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
import shutil

from core.services.binder_paths import get_binders_root
from core.services.logging_api import get_logger, get_repo_root
from core.services.paths import get_vault_root
from core.services.time_utils import utc_compact_timestamp
from core.binder.validator import BinderValidator

logger = get_logger("binder-manager")


class BinderWorkspace(str, Enum):
    BINDERS = "binders"
    PUBLIC = "public"
    PRIVATE = "private"
    SHARED = "shared"
    SUBMIT = "submit"


@dataclass
class BinderLocation:
    workspace: BinderWorkspace
    path: Path


class BinderManager:
    """Stub manager for binder workspaces and movement."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or get_repo_root()
        self.binders_root = get_binders_root()
        self.binders_root.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_global_sandbox()

    def _migrate_legacy_global_sandbox(self) -> None:
        """Move legacy VAULT_ROOT/@sandbox content into @binders/sandbox/sandbox."""
        legacy_root = get_vault_root() / "@sandbox"
        if not legacy_root.exists() or not legacy_root.is_dir():
            return

        entries = [p for p in legacy_root.iterdir()]
        if not entries:
            try:
                legacy_root.rmdir()
            except OSError:
                pass
            return

        binder_root = self.binders_root / "sandbox"
        if not binder_root.exists():
            BinderValidator.create_binder_structure(
                binder_root,
                config={
                    "name": "sandbox",
                    "version": "0.1.0",
                    "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "author": None,
                    "description": "Legacy global sandbox migration binder",
                    "tags": ["binder", "binders", "migration"],
                },
            )
            self._write_index(
                binder_root, "sandbox", "sandbox", BinderWorkspace.BINDERS
            )

        target_sandbox = binder_root / "sandbox"
        target_sandbox.mkdir(parents=True, exist_ok=True)
        moved_count = 0
        for entry in entries:
            destination = target_sandbox / entry.name
            if destination.exists():
                destination = target_sandbox / f"{entry.name}.{utc_compact_timestamp()}"
            shutil.move(str(entry), str(destination))
            moved_count += 1

        try:
            legacy_root.rmdir()
        except OSError:
            pass

        logger.info(
            f"[LOCAL] Migrated legacy @sandbox workspace into @binders/sandbox/sandbox ({moved_count} entries)"
        )

    def get_workspace_dir(self, workspace: BinderWorkspace) -> Path:
        vault_root = get_vault_root()
        if workspace == BinderWorkspace.BINDERS:
            return self.binders_root
        if workspace == BinderWorkspace.PUBLIC:
            target = vault_root / "public-open-published" / "published" / "binders"
        elif workspace == BinderWorkspace.PRIVATE:
            target = vault_root / "private-explicit" / "binders"
        elif workspace == BinderWorkspace.SHARED:
            target = vault_root / "private-shared" / "binders"
        elif workspace == BinderWorkspace.SUBMIT:
            target = vault_root / "public-open-published" / "submissions" / "pending" / "binders"
        else:
            target = self.binders_root / workspace.value
        target.mkdir(parents=True, exist_ok=True)
        return target

    def list_binders(self, workspace: BinderWorkspace = BinderWorkspace.BINDERS) -> List[Path]:
        root = self.get_workspace_dir(workspace)
        if not root.exists():
            return []
        return sorted([p for p in root.iterdir() if p.is_dir()])

    def create_binder(
        self,
        binder_id: str,
        title: Optional[str] = None,
        workspace: BinderWorkspace = BinderWorkspace.BINDERS,
    ) -> BinderLocation:
        binder_root = self.get_workspace_dir(workspace) / binder_id
        binder_root.mkdir(parents=True, exist_ok=True)
        BinderValidator.create_binder_structure(
            binder_root,
            config={
                "name": title or binder_id,
                "version": "0.1.0",
                "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "author": None,
                "description": "Binder stub (per-binder sandbox)",
                "tags": ["binder", workspace.value],
            },
        )
        self._write_index(binder_root, binder_id, title or binder_id, workspace)
        logger.info(f"[LOCAL] Binder created: {binder_root}")
        return BinderLocation(workspace=workspace, path=binder_root)

    def _write_index(
        self,
        binder_root: Path,
        binder_id: str,
        title: str,
        workspace: BinderWorkspace,
    ) -> None:
        index_path = binder_root / "index.md"
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        content = (
            "---\n"
            f"binder_id: {binder_id}\n"
            "base_version: 0.1.0\n"
            f"status: draft\n"
            f"workspace: {workspace.value}\n"
            "visibility: private\n"
            "owner: user\n"
            f"created_at: {timestamp}\n"
            f"updated_at: {timestamp}\n"
            "index: docs/README.md\n"
            f"title: {title}\n"
            "tags: [binder]\n"
            "---\n\n"
            "# Binder Index\n\n"
            "Describe this binder, its scope, and key documents.\n"
        )
        index_path.write_text(content)

    def move_binder(
        self,
        binder_id: str,
        target_workspace: BinderWorkspace,
    ) -> BinderLocation:
        source = self.binders_root / binder_id
        if not source.exists():
            raise ValueError(f"Binder not found in binders root: {binder_id}")
        target_root = self.get_workspace_dir(target_workspace)
        target = target_root / binder_id
        if target.exists():
            raise ValueError(f"Target binder already exists: {target}")
        shutil.move(str(source), str(target))
        logger.info(
            f"[LOCAL] Binder moved {binder_id} -> {target_workspace.value} ({target})"
        )
        return BinderLocation(workspace=target_workspace, path=target)

    def describe_workspaces(self) -> Dict[str, str]:
        return {
            "binders": str(self.binders_root),
            "public": str(self.get_workspace_dir(BinderWorkspace.PUBLIC)),
            "private": str(self.get_workspace_dir(BinderWorkspace.PRIVATE)),
            "shared": str(self.get_workspace_dir(BinderWorkspace.SHARED)),
            "submit": str(self.get_workspace_dir(BinderWorkspace.SUBMIT)),
        }
