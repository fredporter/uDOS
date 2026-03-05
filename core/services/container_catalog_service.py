"""Shared catalog for library containers and official extension components."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.services.logging_api import get_repo_root
from core.services.template_workspace_service import get_template_workspace_service


@dataclass(frozen=True)
class ContainerExecutionRules:
    """Canonical execution rules shared across component callers."""

    execution_model: str
    runtime_owner: str
    callable_from: list[str] = field(default_factory=list)
    library_root: str = "library"
    entry_kind: str = "container"
    standalone_capable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContainerCatalogEntry:
    """Unified catalog record for a library container or extension component."""

    entry_id: str
    label: str
    summary: str
    path: str
    kind: str
    profiles: list[str] = field(default_factory=list)
    available: bool = False
    version: str | None = None
    api_prefix: str | None = None
    wizard_route: str | None = None
    visibility: str = "official"
    category: str = "general"
    source: str = ""
    execution: ContainerExecutionRules = field(
        default_factory=lambda: ContainerExecutionRules(
            execution_model="container-catalog-v1",
            runtime_owner="shared",
            callable_from=["core", "wizard", "extensions", "sonic", "uhome"],
        )
    )
    lens_vars: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["execution"] = self.execution.to_dict()
        return data


DEFAULT_EXTENSION_RULES = {
    "execution_model": "shared-component-v1",
    "runtime_owner": "shared",
    "callable_from": ["core", "wizard", "extensions", "sonic", "uhome"],
    "library_root": "library",
    "entry_kind": "extension",
    "standalone_capable": True,
}


class ContainerCatalogService:
    """Discover shared library containers and official extension components."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.library_root = self.repo_root / "library"
        self.release_manifest = (
            self.repo_root / "distribution" / "profiles" / "certified-profiles.json"
        )

    def list_entries(self) -> list[ContainerCatalogEntry]:
        entries: list[ContainerCatalogEntry] = []
        entries.extend(self._discover_library_entries())
        entries.extend(self._discover_extension_entries())
        return sorted(entries, key=lambda item: (item.kind, item.entry_id))

    def list_by_kind(self, kind: str) -> list[ContainerCatalogEntry]:
        normalized = kind.strip().lower()
        return [entry for entry in self.list_entries() if entry.kind == normalized]

    def get_entry(self, entry_id: str) -> ContainerCatalogEntry | None:
        normalized = entry_id.strip().lower()
        for entry in self.list_entries():
            if entry.entry_id == normalized:
                return entry
        return None

    def _discover_library_entries(self) -> list[ContainerCatalogEntry]:
        if not self.library_root.exists():
            return []

        entries: list[ContainerCatalogEntry] = []
        for candidate in sorted(self.library_root.iterdir(), key=lambda path: path.name):
            if not candidate.is_dir():
                continue
            manifest_path = candidate / "container.json"
            if not manifest_path.exists():
                continue
            payload = self._read_json(manifest_path)
            container = payload.get("container", {}) if isinstance(payload, dict) else {}
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            policy = payload.get("policy", {}) if isinstance(payload, dict) else {}
            integration = payload.get("integration", {}) if isinstance(payload, dict) else {}
            service = payload.get("service", {}) if isinstance(payload, dict) else {}
            launch_config = payload.get("launch_config", {}) if isinstance(payload, dict) else {}
            entry_id = str(container.get("id") or candidate.name).strip().lower()
            runtime_owner = (
                "wizard"
                if bool(policy.get("wizard_only"))
                else str(policy.get("runtime_owner") or "shared").strip().lower()
            )
            resolved_repo_path = self._resolve_repo_path(
                payload.get("repo_path"),
                fallback=candidate,
            )
            callable_from = self._normalize_string_list(
                payload.get("callable_from")
                or metadata.get("callable_from")
                or ["core", "wizard", "extensions", "sonic", "uhome"]
            )
            entries.append(
                ContainerCatalogEntry(
                    entry_id=entry_id,
                    label=str(container.get("name") or entry_id).strip(),
                    summary=str(
                        container.get("description")
                        or metadata.get("documentation")
                        or ""
                    ).strip(),
                    path=str(candidate.relative_to(self.repo_root)),
                    kind="library",
                    profiles=self._normalize_string_list(payload.get("profiles") or []),
                    available=True,
                    version=self._coerce_optional_str(container.get("version")),
                    api_prefix=self._coerce_optional_str(service.get("browser_route")),
                    wizard_route=self._coerce_optional_str(integration.get("wrapper_path")),
                    visibility="official",
                    category=str(metadata.get("category") or "container").strip(),
                    source="library",
                    execution=ContainerExecutionRules(
                        execution_model=str(
                            policy.get("execution_model") or "container-library-v1"
                        ).strip(),
                        runtime_owner=runtime_owner,
                        callable_from=callable_from,
                        library_root="library",
                        entry_kind="library",
                        standalone_capable=bool(
                            payload.get("standalone_capable", True)
                        ),
                    ),
                    lens_vars=self._build_lens_vars(
                        entry_id=entry_id,
                        kind="library",
                        runtime_owner=runtime_owner,
                        path=str(candidate.relative_to(self.repo_root)),
                        callable_from=callable_from,
                        profiles=[],
                        standalone_capable=bool(
                            payload.get("standalone_capable", True)
                        ),
                        workspace_ref="@memory/bank/typo-workspace",
                    ),
                    metadata={
                        "manifest_path": str(manifest_path.relative_to(self.repo_root)),
                        "repo_path": self._coerce_optional_str(payload.get("repo_path")),
                        "resolved_repo_path": str(resolved_repo_path),
                        "license": self._coerce_optional_str(metadata.get("license")),
                        "author": self._coerce_optional_str(metadata.get("maintainer")),
                        "homepage": self._coerce_optional_str(metadata.get("homepage")),
                        "container_type": str(container.get("type") or "local").strip(),
                        "git_source": self._coerce_optional_str(container.get("source")),
                        "git_ref": self._coerce_optional_str(container.get("ref")),
                        "git_cloned": bool(
                            container.get("cloned_at") or (resolved_repo_path / ".git").exists()
                        ),
                        "install_script": self._coerce_optional_str(
                            integration.get("install_script")
                        ),
                        "documentation": self._coerce_optional_str(
                            metadata.get("documentation")
                        ),
                        "integration_dependencies": self._extract_integration_dependencies(
                            payload
                        ),
                        "package_dependencies": self._extract_package_dependencies(payload),
                        "source_url": container.get("source"),
                        "browser_route": service.get("browser_route"),
                        "port": service.get("port"),
                        "health_check_url": self._coerce_optional_str(
                            service.get("health_check_url")
                            or launch_config.get("health_check_url")
                        ),
                        "template_workspace": self._template_workspace_entry(entry_id),
                    },
                )
            )
        return entries

    def _discover_extension_entries(self) -> list[ContainerCatalogEntry]:
        payload = self._read_json(self.release_manifest)
        extensions = payload.get("extensions", {}) if isinstance(payload, dict) else {}
        if not isinstance(extensions, dict):
            return []

        entries: list[ContainerCatalogEntry] = []
        for entry_id, raw_meta in sorted(extensions.items()):
            if not isinstance(raw_meta, dict):
                continue
            path = str(raw_meta.get("path") or "").strip()
            target = self.repo_root / path if path else self.repo_root / str(entry_id)
            local_meta = self._read_json(target / "extension.json")
            isolation = self._validate_extension_isolation(target)
            entry_meta = (
                {**local_meta, **raw_meta}
                if isinstance(local_meta, dict)
                else dict(raw_meta)
            )
            runtime_owner = str(
                entry_meta.get("runtime_owner") or DEFAULT_EXTENSION_RULES["runtime_owner"]
            ).strip().lower()
            callable_from = self._normalize_string_list(
                entry_meta.get("callable_from")
                or DEFAULT_EXTENSION_RULES["callable_from"]
            )
            entries.append(
                ContainerCatalogEntry(
                    entry_id=str(entry_id).strip().lower(),
                    label=str(entry_meta.get("label") or entry_id).strip(),
                    summary=str(entry_meta.get("summary") or "").strip(),
                    path=path,
                    kind="extension",
                    profiles=self._normalize_string_list(entry_meta.get("profiles") or []),
                    available=target.exists(),
                    version=self._resolve_extension_version(target),
                    api_prefix=self._coerce_optional_str(entry_meta.get("api_prefix")),
                    wizard_route=self._coerce_optional_str(
                        entry_meta.get("wizard_route") or f"#{entry_id}"
                    ),
                    visibility=str(entry_meta.get("visibility") or "official").strip(),
                    category=str(entry_meta.get("category") or "general").strip(),
                    source="extensions",
                    execution=ContainerExecutionRules(
                        execution_model=str(
                            entry_meta.get("execution_model")
                            or DEFAULT_EXTENSION_RULES["execution_model"]
                        ).strip(),
                        runtime_owner=runtime_owner,
                        callable_from=callable_from,
                        library_root=str(
                            entry_meta.get("library_root")
                            or DEFAULT_EXTENSION_RULES["library_root"]
                        ).strip(),
                        entry_kind=str(
                            entry_meta.get("entry_kind")
                            or DEFAULT_EXTENSION_RULES["entry_kind"]
                        ).strip(),
                        standalone_capable=bool(
                            entry_meta.get(
                                "standalone_capable",
                                DEFAULT_EXTENSION_RULES["standalone_capable"],
                            )
                        ),
                    ),
                    lens_vars=self._build_lens_vars(
                        entry_id=str(entry_id).strip().lower(),
                        kind="extension",
                        runtime_owner=runtime_owner,
                        path=path,
                        callable_from=callable_from,
                        profiles=self._normalize_string_list(entry_meta.get("profiles") or []),
                        standalone_capable=bool(
                            entry_meta.get(
                                "standalone_capable",
                                DEFAULT_EXTENSION_RULES["standalone_capable"],
                            )
                        ),
                        workspace_ref="@memory/bank/typo-workspace",
                    ),
                    metadata={
                        "description": entry_meta.get("description"),
                        "manifest_path": str((target / "extension.json").relative_to(self.repo_root))
                        if (target / "extension.json").exists()
                        else None,
                        "library_refs": self._normalize_string_list(
                            entry_meta.get("library_refs") or []
                        ),
                        "isolation_valid": isolation["valid"],
                        "isolation_errors": isolation["errors"],
                        "template_workspace": self._template_workspace_entry(
                            str(entry_id).strip().lower()
                        ),
                    },
                )
            )
        return entries

    def _validate_extension_isolation(self, extension_root: Path) -> dict[str, Any]:
        """Validate extension layout contract for self-contained install roots."""
        errors: list[str] = []
        if not extension_root.exists():
            errors.append("extension root missing")
            return {"valid": False, "errors": errors}

        manifest = extension_root / "extension.json"
        if not manifest.exists():
            errors.append("extension.json missing")

        allowed_runtime_dirs = ("library", "commands", "providers")
        present_runtime_dirs = [
            item
            for item in allowed_runtime_dirs
            if (extension_root / item).exists()
        ]
        if not present_runtime_dirs:
            errors.append("no runtime directories present (expected one of library/commands/providers)")

        forbidden = [extension_root / "core", extension_root / "wizard"]
        for candidate in forbidden:
            if candidate.exists():
                errors.append(f"forbidden nested path present: {candidate.name}")

        return {"valid": len(errors) == 0, "errors": errors}

    def _resolve_extension_version(self, target: Path) -> str | None:
        for rel in ("version.json", "manifest.json", "extension.json", "package.json"):
            payload = self._read_json(target / rel)
            version = payload.get("version") if isinstance(payload, dict) else None
            if isinstance(version, str) and version.strip():
                return version.strip()
        return None

    def _build_lens_vars(
        self,
        *,
        entry_id: str,
        kind: str,
        runtime_owner: str,
        path: str,
        callable_from: list[str],
        profiles: list[str],
        standalone_capable: bool,
        workspace_ref: str,
    ) -> dict[str, Any]:
        return {
            "lens": f"repo-library:{entry_id}",
            "kind": kind,
            "runtime_owner": runtime_owner,
            "path": path,
            "callable_from": list(callable_from),
            "profiles": list(profiles),
            "standalone_capable": standalone_capable,
            "workspace_ref": workspace_ref,
        }

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _normalize_string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [
            str(item).strip()
            for item in value
            if isinstance(item, str) and str(item).strip()
        ]

    def _coerce_optional_str(self, value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

    def _resolve_repo_path(self, value: Any, *, fallback: Path) -> Path:
        if isinstance(value, str) and value.strip():
            candidate = Path(value.strip()).expanduser()
            if not candidate.is_absolute():
                candidate = self.repo_root / candidate
            return candidate
        return fallback

    def _extract_integration_dependencies(self, payload: dict[str, Any]) -> list[str]:
        deps: list[str] = []
        candidates = [
            payload.get("dependencies"),
            payload.get("requires"),
            (payload.get("integration") or {}).get("depends_on"),
            (payload.get("integration") or {}).get("dependencies"),
        ]
        for candidate in candidates:
            if isinstance(candidate, list):
                for item in candidate:
                    if isinstance(item, str) and item.strip():
                        deps.append(item.strip())
            elif isinstance(candidate, dict):
                for key in ("integrations", "integration", "plugins"):
                    values = candidate.get(key)
                    if isinstance(values, list):
                        for item in values:
                            if isinstance(item, str) and item.strip():
                                deps.append(item.strip())
                    elif isinstance(values, str) and values.strip():
                        deps.append(values.strip())
        return self._dedupe_strings(deps)

    def _extract_package_dependencies(self, payload: dict[str, Any]) -> dict[str, list[str]]:
        def _as_list(value: Any) -> list[str]:
            if not isinstance(value, list):
                return []
            return [str(item).strip() for item in value if isinstance(item, str) and item.strip()]

        system_requirements = payload.get("system_requirements", {})
        return {
            "apk_dependencies": _as_list(payload.get("apk_dependencies")),
            "brew_dependencies": _as_list(payload.get("brew_dependencies")),
            "apt_dependencies": _as_list(payload.get("apt_dependencies")),
            "pip_dependencies": _as_list(payload.get("pip_dependencies")),
            "system_dependencies": _as_list(
                system_requirements.get("dependencies")
                if isinstance(system_requirements, dict)
                else []
            ),
        }

    def _dedupe_strings(self, values: list[str]) -> list[str]:
        deduped: list[str] = []
        seen: set[str] = set()
        for value in values:
            if value not in seen:
                seen.add(value)
                deduped.append(value)
        return deduped

    def _template_workspace_entry(self, component_id: str) -> dict[str, Any]:
        return get_template_workspace_service(self.repo_root).component_contract(
            component_id
        )


def get_container_catalog_service(
    repo_root: Path | None = None,
) -> ContainerCatalogService:
    return ContainerCatalogService(repo_root=repo_root)
