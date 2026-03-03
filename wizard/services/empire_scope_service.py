"""Scope resolution for Empire master and binder targets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from wizard.services.path_utils import get_repo_root, get_vault_dir


class EmpireScopeService:
    """Resolve Empire operation scope to canonical workspace locations."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.vault_dir = get_vault_dir()
        self.binders_root = self.vault_dir / "@binders"

    def list_binders(self) -> list[dict[str, str]]:
        if not self.binders_root.exists():
            return []
        items: list[dict[str, str]] = []
        for path in sorted(self.binders_root.iterdir()):
            if not path.is_dir():
                continue
            items.append(
                {
                    "binder_id": path.name,
                    "path": str(path),
                }
            )
        return items

    def resolve(self, scope: str = "master", binder_id: str | None = None) -> dict[str, Any]:
        normalized = (scope or "master").strip().lower()
        if normalized not in {"master", "binder"}:
            raise ValueError("scope must be master or binder")
        if normalized == "master":
            return {
                "scope": "master",
                "binder_id": None,
                "label": "Master workspace",
                "vault_path": str(self.vault_dir),
                "db_path": str(self.repo_root / "extensions" / "empire" / "data" / "empire.db"),
            }
        if not binder_id:
            raise ValueError("binder_id required when scope=binder")
        binder_path = self.binders_root / binder_id
        if not binder_path.exists() or not binder_path.is_dir():
            raise ValueError(f"Unknown binder: {binder_id}")
        return {
            "scope": "binder",
            "binder_id": binder_id,
            "label": f"Binder: {binder_id}",
            "vault_path": str(binder_path),
            "db_path": str(binder_path / "uDOS-table.db"),
        }


_service: EmpireScopeService | None = None


def get_empire_scope_service() -> EmpireScopeService:
    global _service
    if _service is None:
        _service = EmpireScopeService()
    return _service

