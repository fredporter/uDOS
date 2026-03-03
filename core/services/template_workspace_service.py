"""Canonical Markdown workspace contract for shared settings and instructions."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from core.services.logging_api import get_repo_root


class TemplateWorkspaceService:
    """Manage the shared Typo-oriented workspace for seeded/default/user content."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.seed_root = (
            self.repo_root / "core" / "framework" / "seed" / "bank" / "typo-workspace"
        )
        self.workspace_root = self.repo_root / "memory" / "bank" / "typo-workspace"

    @property
    def default_root(self) -> Path:
        return self.workspace_root / "default"

    @property
    def user_root(self) -> Path:
        return self.workspace_root / "user"

    def ensure_workspace(self) -> dict[str, str]:
        for rel in (
            Path("settings"),
            Path("instructions"),
            Path("settings") / "overrides",
            Path("instructions") / "overrides",
        ):
            self._ensure_dir(self.default_root / rel)
            self._ensure_dir(self.user_root / rel)

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

    def component_contract(self, component_id: str) -> dict[str, Any]:
        self.ensure_workspace()
        normalized = self._normalize_component_id(component_id)
        return {
            "component_id": normalized,
            "editor_library_ref": "typo",
            "workspace_ref": "@memory/bank/typo-workspace",
            "workspace_root": str(self.workspace_root),
            "default_root": str(self.default_root),
            "user_root": str(self.user_root),
            "settings": self._file_triplet("settings", normalized),
            "instructions": self._file_triplet("instructions", normalized),
        }

    def component_snapshot(self, component_id: str) -> dict[str, Any]:
        normalized = self._normalize_component_id(component_id)
        contract = self.component_contract(normalized)
        return {
            **contract,
            "settings": self._document_snapshot(
                "settings", normalized, contract["settings"]
            ),
            "instructions": self._document_snapshot(
                "instructions", normalized, contract["instructions"]
            ),
        }

    def read_document(self, section: str, component_id: str) -> dict[str, Any]:
        normalized = self._normalize_component_id(component_id)
        contract = self.component_contract(normalized)
        if section not in ("settings", "instructions"):
            raise ValueError(f"Unsupported template workspace section: {section}")
        return self._document_snapshot(section, normalized, contract[section])

    def read_fields(self, section: str, component_id: str) -> dict[str, str]:
        snapshot = self.read_document(section, component_id)
        return self.parse_fields(str(snapshot.get("effective_content") or ""))

    def write_user_document(
        self, section: str, component_id: str, content: str
    ) -> dict[str, Any]:
        normalized = self._normalize_component_id(component_id)
        contract = self.component_contract(normalized)
        if section not in ("settings", "instructions"):
            raise ValueError(f"Unsupported template workspace section: {section}")
        target = Path(contract[section]["user"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return self._document_snapshot(section, normalized, contract[section])

    def write_user_field(
        self, section: str, component_id: str, field_name: str, value: str
    ) -> dict[str, Any]:
        normalized = self._normalize_component_id(component_id)
        contract = self.component_contract(normalized)
        if section not in ("settings", "instructions"):
            raise ValueError(f"Unsupported template workspace section: {section}")
        snapshot = self._document_snapshot(section, normalized, contract[section])
        content = self._upsert_field_line(
            str(snapshot.get("effective_content") or ""),
            field_name=field_name,
            value=value,
        )
        return self.write_user_document(section, normalized, content)

    def workspace_contract(self) -> dict[str, Any]:
        self.ensure_workspace()
        components = [
            "shared",
            "core",
            "wizard",
            "sonic",
            "uhome",
            "thin-gui",
            "extensions",
        ]
        return {
            "editor_library_ref": "typo",
            "workspace_ref": "@memory/bank/typo-workspace",
            "seed_root": str(self.seed_root),
            "workspace_root": str(self.workspace_root),
            "default_root": str(self.default_root),
            "user_root": str(self.user_root),
            "components": {
                component: self.component_contract(component)
                for component in components
            },
        }

    def parse_fields(self, content: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for line in (content or "").splitlines():
            match = re.match(r"^\s*-\s*([A-Za-z0-9 _-]+?)\s*:\s*(.*?)\s*$", line)
            if not match:
                continue
            key = self._normalize_field_name(match.group(1))
            fields[key] = match.group(2).strip()
        return fields

    def _file_triplet(self, section: str, component_id: str) -> dict[str, str]:
        rel = Path(section) / f"{component_id}.md"
        seeded = self.seed_root / rel
        if not seeded.exists():
            rel = Path(section) / "shared.md"
            seeded = self.seed_root / rel
        return {
            "seeded": str(seeded),
            "default": str(self.default_root / rel),
            "user": str(self.user_root / rel),
        }

    def _document_snapshot(
        self, section: str, component_id: str, paths: dict[str, str]
    ) -> dict[str, Any]:
        seeded_path = Path(paths["seeded"])
        default_path = Path(paths["default"])
        user_path = Path(paths["user"])
        effective_path, effective_source = self._effective_path(
            seeded_path=seeded_path,
            default_path=default_path,
            user_path=user_path,
        )
        return {
            "section": section,
            "component_id": component_id,
            "paths": dict(paths),
            "effective_source": effective_source,
            "effective_path": str(effective_path),
            "effective_content": effective_path.read_text(encoding="utf-8")
            if effective_path.exists()
            else "",
            "user_exists": user_path.exists(),
            "default_exists": default_path.exists(),
            "seeded_exists": seeded_path.exists(),
        }

    def _effective_path(
        self, *, seeded_path: Path, default_path: Path, user_path: Path
    ) -> tuple[Path, str]:
        if user_path.exists():
            return user_path, "user"
        if default_path.exists():
            return default_path, "default"
        return seeded_path, "seeded"

    def _normalize_component_id(self, component_id: str) -> str:
        value = (component_id or "shared").strip().lower()
        return value or "shared"

    def _normalize_field_name(self, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
        return normalized.strip("_")

    def _ensure_dir(self, path: Path) -> None:
        if path.exists():
            if path.is_dir():
                return
            raise NotADirectoryError(f"Expected directory at {path}")
        path.mkdir(parents=True, exist_ok=True)

    def _upsert_field_line(self, content: str, *, field_name: str, value: str) -> str:
        target_key = self._normalize_field_name(field_name)
        display_name = field_name.strip()
        lines = (content or "").splitlines()
        updated: list[str] = []
        replaced = False
        for line in lines:
            match = re.match(r"^(\s*-\s*)([A-Za-z0-9 _-]+?)(\s*:\s*)(.*?)\s*$", line)
            if not match:
                updated.append(line)
                continue
            line_key = self._normalize_field_name(match.group(2))
            if line_key == target_key:
                updated.append(f"{match.group(1)}{display_name}{match.group(3)}{value}")
                replaced = True
            else:
                updated.append(line)
        if not replaced:
            if updated and updated[-1].strip():
                updated.append("")
            updated.append(f"- {display_name}: {value}")
        return "\n".join(updated).rstrip() + "\n"


def get_template_workspace_service(
    repo_root: Path | None = None,
) -> TemplateWorkspaceService:
    return TemplateWorkspaceService(repo_root=repo_root)
