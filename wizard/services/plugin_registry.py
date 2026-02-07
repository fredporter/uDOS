"""
Plugin Manifest Registry
========================

Builds a registry that merges:
- distribution/plugins/index.json (catalog)
- per-plugin manifest.json files
- package file metadata (tar.gz / tcz)

Provides validation and a clean API surface for Wizard routes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jsonschema import Draft7Validator

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root
from wizard.services.plugin_repository import PluginRepository, PluginEntry

logger = get_logger("plugin-registry")


@dataclass
class ManifestReport:
    plugin_id: str
    manifest_path: Optional[Path]
    manifest: Optional[Dict[str, Any]]
    manifest_type: str
    checksum: Optional[str]
    validation_status: str  # "validated" | "skipped" | "failed"
    issues: List[str]

    def to_dict(self, include_manifest: bool = True) -> Dict[str, Any]:
        data = {
            "plugin_id": self.plugin_id,
            "manifest_path": str(self.manifest_path) if self.manifest_path else None,
            "manifest_type": self.manifest_type,
            "checksum": self.checksum,
            "validation_status": self.validation_status,
            "issues": self.issues,
        }
        if include_manifest:
            data["manifest"] = self.manifest
        return data


class PluginRegistry:
    def __init__(self, base_dir: Optional[Path] = None):
        self.repo_root = get_repo_root()
        self.base_dir = Path(base_dir) if base_dir else (self.repo_root / "distribution" / "plugins")
        self.schema_path = self.base_dir / "plugin.schema.json"
        self.repo = PluginRepository(base_dir=self.base_dir)
        self._registry: Dict[str, Dict[str, Any]] = {}
        self.last_scan: Optional[str] = None
        self._schema = self._load_schema()
        self._validator = Draft7Validator(self._schema) if self._schema else None

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        if not self.schema_path.exists():
            return None
        try:
            return json.loads(self.schema_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"[REGISTRY] Failed to load schema: {exc}")
            return None

    def _iter_plugin_dirs(self) -> List[Path]:
        if not self.base_dir.exists():
            return []
        skip = {"cache", "packages"}
        result = []
        for entry in self.base_dir.iterdir():
            if entry.is_dir() and entry.name not in skip:
                result.append(entry)
        return result

    def _detect_manifest_type(self, manifest: Dict[str, Any]) -> str:
        if not manifest:
            return "missing"
        schema_ref = str(manifest.get("$schema", ""))
        if "plugin.schema.json" in schema_ref:
            return "plugin"
        if "package_type" in manifest or "package_checksum" in manifest:
            return "package"
        if manifest.get("type") == "container" or "launch_config" in manifest:
            return "container"
        if "installation" in manifest or "udos_integration" in manifest:
            return "plugin"
        return "generic"

    def _checksum_file(self, path: Path) -> Optional[str]:
        if not path.exists():
            return None
        hasher = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _load_manifest(self, manifest_path: Path) -> Optional[Dict[str, Any]]:
        if not manifest_path.exists():
            return None
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"[REGISTRY] Failed to read manifest {manifest_path}: {exc}")
            return None

    def _validate_manifest(self, plugin_id: str, manifest: Dict[str, Any], manifest_path: Optional[Path] = None) -> ManifestReport:
        manifest_path = manifest_path or (self.base_dir / plugin_id / "manifest.json")
        manifest_type = self._detect_manifest_type(manifest)
        checksum = self._checksum_file(manifest_path) if manifest else None
        issues: List[str] = []
        validation_status = "skipped"

        if manifest_type == "plugin" and self._validator:
            errors = sorted(self._validator.iter_errors(manifest), key=lambda e: e.path)
            if errors:
                validation_status = "failed"
                for err in errors:
                    path = ".".join(str(p) for p in err.path) if err.path else "manifest"
                    issues.append(f"{path}: {err.message}")
            else:
                validation_status = "validated"
        elif manifest is None:
            validation_status = "failed"
            issues.append("Manifest missing or invalid JSON")

        return ManifestReport(
            plugin_id=plugin_id,
            manifest_path=manifest_path if manifest else None,
            manifest=manifest,
            manifest_type=manifest_type,
            checksum=checksum,
            validation_status=validation_status,
            issues=issues,
        )

    def _collect_packages(self, plugin_id: str, plugin_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        plugin_dir = plugin_dir or (self.base_dir / plugin_id)
        packages_dir = self.base_dir / "packages" / plugin_id
        found: List[Path] = []
        for root in (plugin_dir, packages_dir):
            if root.exists():
                found.extend(sorted(root.glob("*.tar.gz")))
                found.extend(sorted(root.glob("*.tcz")))

        packages = []
        seen = set()
        for path in found:
            if path.name in seen:
                continue
            seen.add(path.name)
            packages.append(
                {
                    "filename": path.name,
                    "path": str(path),
                    "size": path.stat().st_size,
                }
            )
        return packages

    def build_registry(self, refresh: bool = False, include_manifests: bool = True) -> Dict[str, Dict[str, Any]]:
        if self._registry and not refresh:
            return self._registry

        index_plugins = {p.id: p for p in self.repo.list_plugins()}
        manifest_reports: Dict[str, ManifestReport] = {}

        plugin_dirs: Dict[str, Path] = {}
        for plugin_dir in self._iter_plugin_dirs():
            manifest_path = plugin_dir / "manifest.json"
            manifest = self._load_manifest(manifest_path)
            if manifest is None:
                continue
            plugin_id = manifest.get("id") or plugin_dir.name
            manifest_reports[plugin_id] = self._validate_manifest(plugin_id, manifest, manifest_path)
            plugin_dirs[plugin_id] = plugin_dir

        registry: Dict[str, Dict[str, Any]] = {}
        all_ids = set(index_plugins.keys()) | set(manifest_reports.keys())

        for plugin_id in sorted(all_ids):
            index_entry = index_plugins.get(plugin_id)
            manifest_report = manifest_reports.get(plugin_id)
            packages = self._collect_packages(plugin_id, plugin_dirs.get(plugin_id))

            registry[plugin_id] = {
                "plugin_id": plugin_id,
                "registered": index_entry is not None,
                "index_entry": index_entry.to_dict() if index_entry else None,
                "manifest_report": manifest_report.to_dict(include_manifest=include_manifests)
                if manifest_report
                else None,
                "packages": packages,
            }

        self._registry = registry
        self.last_scan = datetime.utcnow().isoformat() + "Z"
        return registry

    def refresh_index(self, write: bool = False) -> Dict[str, Any]:
        """Refresh index entries from manifests and optionally write to disk."""
        registry = self.build_registry(refresh=True, include_manifests=True)
        created = 0
        updated = 0

        for plugin_id, entry in registry.items():
            report = entry.get("manifest_report") or {}
            manifest = report.get("manifest") or {}
            if not manifest:
                continue

            name = manifest.get("name", plugin_id)
            version = manifest.get("version", "0.0.0")
            description = manifest.get("description", "")
            category = manifest.get("category", "utility")
            license_name = manifest.get("license", "UNKNOWN")
            dependencies = manifest.get("dependencies", [])
            if isinstance(dependencies, dict):
                dependencies = dependencies.get("system", []) or []

            packages = entry.get("packages") or []
            package_file = packages[0]["filename"] if packages else ""
            package_size = packages[0]["size"] if packages else 0
            checksum = ""
            if packages:
                checksum = self._checksum_file(Path(packages[0]["path"])) or ""

            index_entry = entry.get("index_entry")
            if index_entry:
                existing = PluginEntry.from_dict(index_entry)
                existing.name = name
                existing.version = version
                existing.description = description
                existing.category = category
                existing.license = license_name
                existing.dependencies = dependencies
                if package_file:
                    existing.package_file = package_file
                    existing.package_size = package_size
                    existing.checksum = checksum
                if write:
                    self.repo.add_plugin(existing)
                updated += 1
            else:
                new_entry = PluginEntry(
                    id=plugin_id,
                    name=name,
                    description=description,
                    version=version,
                    category=category,
                    license=license_name,
                    package_file=package_file,
                    package_size=package_size,
                    checksum=checksum,
                    dependencies=dependencies,
                )
                if write:
                    self.repo.add_plugin(new_entry)
                created += 1

        return {"created": created, "updated": updated, "written": write}


_registry_instance: Optional[PluginRegistry] = None


def get_registry(base_dir: Optional[Path] = None) -> PluginRegistry:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = PluginRegistry(base_dir=base_dir)
    return _registry_instance
