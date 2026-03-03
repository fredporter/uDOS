"""Canonical seed template service for browse, read, and duplicate flows."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from core.services.logging_api import get_repo_root


class SeedTemplateService:
    """Expose the shared v1.5 template inventory across seed/default/user layers."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.seed_root = self.repo_root / "core" / "framework" / "seed" / "bank" / "templates"
        self.workspace_root = self.repo_root / "memory" / "bank" / "templates"

    @property
    def default_root(self) -> Path:
        return self.workspace_root / "default"

    @property
    def user_root(self) -> Path:
        return self.workspace_root / "user"

    def ensure_workspace(self) -> dict[str, str]:
        self.default_root.mkdir(parents=True, exist_ok=True)
        self.user_root.mkdir(parents=True, exist_ok=True)

        for family in self.list_families(seed_only=True):
            (self.default_root / family).mkdir(parents=True, exist_ok=True)
            (self.user_root / family).mkdir(parents=True, exist_ok=True)

        for seeded_file in self.seed_root.rglob("*.md"):
            target = self.default_root / seeded_file.relative_to(self.seed_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copyfile(seeded_file, target)

        return {
            "seed_root": str(self.seed_root),
            "workspace_root": str(self.workspace_root),
            "default_root": str(self.default_root),
            "user_root": str(self.user_root),
        }

    def list_families(self, *, seed_only: bool = False) -> list[str]:
        root = self.seed_root if seed_only else self._prepared_seed_root()
        if not root.exists():
            return []
        return sorted(path.name for path in root.iterdir() if path.is_dir())

    def list_templates(self, family: str) -> list[str]:
        normalized = self._normalize_family(family)
        self.ensure_workspace()
        names: set[str] = set()
        for base in (self.seed_root, self.default_root, self.user_root):
            family_root = base / normalized
            if not family_root.exists():
                continue
            names.update(path.stem for path in family_root.glob("*.md") if path.is_file())
        return sorted(names)

    def template_contract(self, family: str, template_name: str) -> dict[str, str]:
        normalized_family = self._normalize_family(family)
        normalized_template = self._normalize_template_name(template_name)
        self.ensure_workspace()
        rel = Path(normalized_family) / f"{normalized_template}.md"
        return {
            "family": normalized_family,
            "template_name": normalized_template,
            "seeded": str(self.seed_root / rel),
            "default": str(self.default_root / rel),
            "user": str(self.user_root / rel),
        }

    def read_template(self, family: str, template_name: str) -> dict[str, Any]:
        contract = self.template_contract(family, template_name)
        seeded_path = Path(contract["seeded"])
        default_path = Path(contract["default"])
        user_path = Path(contract["user"])
        effective_path, effective_source = self._effective_path(
            seeded_path=seeded_path,
            default_path=default_path,
            user_path=user_path,
        )
        return {
            **contract,
            "effective_source": effective_source,
            "effective_path": str(effective_path),
            "content": effective_path.read_text(encoding="utf-8") if effective_path.exists() else "",
            "exists": effective_path.exists(),
        }

    def duplicate_to_user(
        self,
        family: str,
        template_name: str,
        *,
        target_name: str | None = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        normalized_family = self._normalize_family(family)
        source = self.read_template(normalized_family, template_name)
        if not source["exists"]:
            raise FileNotFoundError(
                f"Template not found: {normalized_family}/{template_name}"
            )

        normalized_target = self._normalize_template_name(target_name or template_name)
        user_path = self.user_root / normalized_family / f"{normalized_target}.md"
        user_path.parent.mkdir(parents=True, exist_ok=True)

        if user_path.exists() and not overwrite:
            raise FileExistsError(f"Template already exists: {user_path}")

        user_path.write_text(str(source["content"]), encoding="utf-8")
        return {
            "family": normalized_family,
            "source_template": self._normalize_template_name(template_name),
            "target_template": normalized_target,
            "target_path": str(user_path),
        }

    def workspace_contract(self) -> dict[str, Any]:
        self.ensure_workspace()
        families = self.list_families()
        return {
            "seed_root": str(self.seed_root),
            "workspace_root": str(self.workspace_root),
            "default_root": str(self.default_root),
            "user_root": str(self.user_root),
            "families": {
                family: {
                    "templates": self.list_templates(family),
                    "seeded_root": str(self.seed_root / family),
                    "default_root": str(self.default_root / family),
                    "user_root": str(self.user_root / family),
                }
                for family in families
            },
        }

    def _prepared_seed_root(self) -> Path:
        self.ensure_workspace()
        return self.seed_root

    def _effective_path(
        self, *, seeded_path: Path, default_path: Path, user_path: Path
    ) -> tuple[Path, str]:
        if user_path.exists():
            return user_path, "user"
        if default_path.exists():
            return default_path, "default"
        return seeded_path, "seeded"

    def _normalize_family(self, family: str) -> str:
        value = (family or "").strip().lower()
        if not value:
            raise ValueError("Template family is required")
        return value

    def _normalize_template_name(self, template_name: str) -> str:
        value = (template_name or "").strip()
        if not value:
            raise ValueError("Template name is required")
        return value[:-3] if value.lower().endswith(".md") else value


def get_seed_template_service(repo_root: Path | None = None) -> SeedTemplateService:
    return SeedTemplateService(repo_root=repo_root)
