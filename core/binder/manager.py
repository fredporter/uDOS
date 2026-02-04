"""
Binder Manager (Stub)

Provides the canonical binder workspace paths and minimal workflow hooks.
Binders are authored and compiled in the sandbox, then moved into
publishable workspaces (public/private/shared/submit).

This module is intentionally minimal until full binder functionality lands.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
import shutil

from core.services.logging_service import get_logger, get_repo_root
from core.binder.validator import BinderValidator

logger = get_logger("binder-manager")


class BinderWorkspace(str, Enum):
    SANDBOX = "sandbox"
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
        vault_root = self.repo_root / "vault"
        self.sandbox_root = vault_root / "sandbox" / "binders"
        self.workspace_root = vault_root / "bank" / "binders"
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    def get_workspace_dir(self, workspace: BinderWorkspace) -> Path:
        vault_root = self.repo_root / "vault"
        if workspace == BinderWorkspace.SANDBOX:
            return self.sandbox_root
        if workspace == BinderWorkspace.PUBLIC:
            target = vault_root / "public-open-published" / "published" / "binders"
        elif workspace == BinderWorkspace.PRIVATE:
            target = vault_root / "private-explicit" / "binders"
        elif workspace == BinderWorkspace.SHARED:
            target = vault_root / "private-shared" / "binders"
        elif workspace == BinderWorkspace.SUBMIT:
            target = vault_root / "public-open-published" / "submissions" / "pending" / "binders"
        else:
            target = self.workspace_root / workspace.value
        target.mkdir(parents=True, exist_ok=True)
        return target

    def list_binders(self, workspace: BinderWorkspace = BinderWorkspace.SANDBOX) -> List[Path]:
        root = self.get_workspace_dir(workspace)
        if not root.exists():
            return []
        return sorted([p for p in root.iterdir() if p.is_dir()])

    def create_binder(
        self,
        binder_id: str,
        title: Optional[str] = None,
        workspace: BinderWorkspace = BinderWorkspace.SANDBOX,
    ) -> BinderLocation:
        binder_root = self.get_workspace_dir(workspace) / binder_id
        binder_root.mkdir(parents=True, exist_ok=True)
        BinderValidator.create_binder_structure(
            binder_root,
            config={
                "name": title or binder_id,
                "version": "0.1.0",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "author": None,
                "description": "Binder stub (sandbox)",
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
        timestamp = datetime.utcnow().isoformat() + "Z"
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
        source = self.sandbox_root / binder_id
        if not source.exists():
            raise ValueError(f"Binder not found in sandbox: {binder_id}")
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
            "sandbox": str(self.sandbox_root),
            "public": str(self.get_workspace_dir(BinderWorkspace.PUBLIC)),
            "private": str(self.get_workspace_dir(BinderWorkspace.PRIVATE)),
            "shared": str(self.get_workspace_dir(BinderWorkspace.SHARED)),
            "submit": str(self.get_workspace_dir(BinderWorkspace.SUBMIT)),
        }
