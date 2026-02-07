"""
Plugin Repository Manager
==========================

Provides helpers for listing plugins, reading manifests, and serving download
data for the Wizard plugin ecosystem.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from wizard.services.path_utils import get_repo_root


@dataclass
class PluginEntry:
    id: str
    name: str
    description: str
    version: str
    category: str
    license: str
    homepage: Optional[str]
    documentation: Optional[str]
    installed: bool
    installed_version: Optional[str]
    update_available: bool
    dependencies: List[str]
    extras: Dict[str, Any] = None


class PluginRepository:
    """Manage the distribution/plugins catalog."""

    def __init__(self, base_dir: Path = None):
        repo_root = get_repo_root()
        self.base_dir = base_dir or (repo_root / "distribution" / "plugins")
        self.index_path = self.base_dir / "index.json"
        self.schema = self.base_dir / "plugin.schema.json"

    def _load_index(self) -> Dict[str, Any]:
        if not self.index_path.exists():
            return {"version": "0.0.0", "plugins": {}}
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def list_plugins(self) -> List[PluginEntry]:
        index = self._load_index()
        plugins = []
        for plugin_id, data in index.get("plugins", {}).items():
            plugins.append(self._from_dict(data))
        return plugins

    def get_plugin(self, plugin_id: str) -> Optional[PluginEntry]:
        index = self._load_index()
        data = index.get("plugins", {}).get(plugin_id)
        if not data:
            return None
        return self._from_dict(data)

    def manifest_path(self, plugin_id: str) -> Path:
        return self.base_dir / plugin_id / "manifest.json"

    def list_packages(self, plugin_id: str) -> List[Path]:
        plugin_dir = self.base_dir / plugin_id
        if not plugin_dir.exists():
            return []
        packages = []
        for ext in ("*.tar.gz", "*.tcz"):
            packages.extend(sorted(plugin_dir.glob(ext)))
        return packages

    def read_manifest(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        manifest = self.manifest_path(plugin_id)
        if not manifest.exists():
            return None
        return json.loads(manifest.read_text(encoding="utf-8"))

    def _from_dict(self, data: Dict[str, Any]) -> PluginEntry:
        return PluginEntry(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            version=data.get("version"),
            category=data.get("category"),
            license=data.get("license"),
            homepage=data.get("homepage"),
            documentation=data.get("documentation"),
            installed=data.get("installed", False),
            installed_version=data.get("installed_version"),
            update_available=data.get("update_available", False),
            dependencies=data.get("dependencies", []),
            extras={k: v for k, v in data.items() if k not in {
                "id", "name", "description", "version", "category", "license",
                "homepage", "documentation", "installed", "installed_version",
                "update_available", "dependencies"
            }}
        )
