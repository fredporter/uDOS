"""
Plugin Repository - Package Index and Discovery
=================================================

Manages the plugin repository for uDOS, providing:
- Plugin index/catalog
- Version tracking
- Dependency resolution
- Update checking
- Package verification

Repository Structure:
  distribution/plugins/
    ├── index.json         # Repository index
    ├── packages/          # Built packages
    │   ├── meshcore/
    │   │   ├── meshcore-1.0.0.tar.gz
    │   │   └── manifest.json
    │   └── typo/
    │       └── ...
    └── cache/             # Download cache
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict, field

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("plugin-repository")

REPO_ROOT = get_repo_root()
REPO_BASE = REPO_ROOT / "distribution" / "plugins"
INDEX_PATH = REPO_BASE / "index.json"
PACKAGES_PATH = REPO_BASE / "packages"
CACHE_PATH = REPO_BASE / "cache"


@dataclass
class PluginEntry:
    """Entry in the plugin repository index."""

    id: str
    name: str
    description: str
    version: str
    category: str
    license: str

    # Package info
    package_file: str = ""
    package_size: int = 0
    checksum: str = ""

    # Metadata
    author: str = ""
    homepage: str = ""
    documentation: str = ""

    # Status
    installed: bool = False
    installed_version: str = ""
    update_available: bool = False
    enabled: bool = False

    # Dependencies
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginEntry":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class RepositoryIndex:
    """Repository index containing all available plugins."""

    version: str = "1.0.0"
    updated_at: str = ""
    plugins: Dict[str, PluginEntry] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "updated_at": self.updated_at,
            "plugins": {k: v.to_dict() for k, v in self.plugins.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryIndex":
        plugins = {}
        for k, v in data.get("plugins", {}).items():
            plugins[k] = PluginEntry.from_dict(v)
        return cls(
            version=data.get("version", "1.0.0"),
            updated_at=data.get("updated_at", ""),
            plugins=plugins,
        )


class PluginRepository:
    """
    Plugin repository manager.

    Provides:
    - Plugin discovery and search
    - Version comparison
    - Update checking
    - Package verification
    """

    def __init__(self):
        """Initialize repository."""
        self.repo_base = REPO_BASE
        self.index_path = INDEX_PATH
        self.packages_path = PACKAGES_PATH
        self.cache_path = CACHE_PATH

        # Ensure directories
        self.repo_base.mkdir(parents=True, exist_ok=True)
        self.packages_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(parents=True, exist_ok=True)

        # Load or create index
        self._index = self._load_index()

    def _load_index(self) -> RepositoryIndex:
        """Load repository index from disk."""
        if self.index_path.exists():
            try:
                data = json.loads(self.index_path.read_text())
                return RepositoryIndex.from_dict(data)
            except Exception as e:
                logger.warning(f"Failed to load index: {e}")

        return RepositoryIndex()

    def _save_index(self):
        """Save repository index to disk."""
        self._index.updated_at = datetime.now().isoformat()
        self.index_path.write_text(json.dumps(self._index.to_dict(), indent=2))

    def list_plugins(
        self, category: str = None, installed_only: bool = False
    ) -> List[PluginEntry]:
        """
        List available plugins.

        Args:
            category: Filter by category (optional)
            installed_only: Only show installed plugins

        Returns:
            List of plugin entries
        """
        plugins = list(self._index.plugins.values())

        if category:
            plugins = [p for p in plugins if p.category.lower() == category.lower()]

        if installed_only:
            plugins = [p for p in plugins if p.installed]

        return sorted(plugins, key=lambda p: p.name)

    def search_plugins(self, query: str) -> List[PluginEntry]:
        """
        Search plugins by name or description.

        Args:
            query: Search query

        Returns:
            Matching plugin entries
        """
        query = query.lower()
        results = []

        for plugin in self._index.plugins.values():
            if (
                query in plugin.id.lower()
                or query in plugin.name.lower()
                or query in plugin.description.lower()
            ):
                results.append(plugin)

        return sorted(results, key=lambda p: p.name)

    def get_plugin(self, plugin_id: str) -> Optional[PluginEntry]:
        """Get plugin by ID."""
        return self._index.plugins.get(plugin_id)

    def add_plugin(self, entry: PluginEntry) -> bool:
        """
        Add or update plugin in index.

        Args:
            entry: Plugin entry to add

        Returns:
            True if successful
        """
        self._index.plugins[entry.id] = entry
        self._save_index()
        logger.info(f"Added plugin to repository: {entry.id}")
        return True

    def remove_plugin(self, plugin_id: str) -> bool:
        """
        Remove plugin from index.

        Args:
            plugin_id: ID of plugin to remove

        Returns:
            True if removed
        """
        if plugin_id in self._index.plugins:
            del self._index.plugins[plugin_id]
            self._save_index()
            logger.info(f"Removed plugin from repository: {plugin_id}")
            return True
        return False

    def check_updates(self) -> List[PluginEntry]:
        """
        Check for available updates.

        Returns:
            List of plugins with updates available
        """
        updates = []

        for plugin in self._index.plugins.values():
            if plugin.installed and plugin.update_available:
                updates.append(plugin)

        return updates

    def verify_package(self, package_path: Path) -> bool:
        """
        Verify package integrity.

        Args:
            package_path: Path to package file

        Returns:
            True if checksum matches
        """
        if not package_path.exists():
            return False

        # Find plugin entry
        for plugin in self._index.plugins.values():
            if plugin.package_file == package_path.name:
                # Calculate checksum
                sha256 = hashlib.sha256()
                with open(package_path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha256.update(chunk)

                calculated = sha256.hexdigest()

                if calculated == plugin.checksum:
                    logger.info(f"Package verified: {package_path.name}")
                    return True
                else:
                    logger.warning(f"Checksum mismatch for {package_path.name}")
                    return False

        logger.warning(f"No index entry for package: {package_path.name}")
        return False

    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        categories = set()
        for plugin in self._index.plugins.values():
            if plugin.category:
                categories.add(plugin.category)
        return sorted(categories)

    def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics."""
        installed = sum(1 for p in self._index.plugins.values() if p.installed)
        updates = sum(1 for p in self._index.plugins.values() if p.update_available)
        enabled = sum(1 for p in self._index.plugins.values() if p.enabled)

        return {
            "total_plugins": len(self._index.plugins),
            "installed": installed,
            "enabled": enabled,
            "updates_available": updates,
            "categories": len(self.get_categories()),
            "last_updated": self._index.updated_at,
        }

    def enable_plugin(self, plugin_id: str) -> bool:
        """
        Enable a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if successful, False otherwise
        """
        plugin = self._index.plugins.get(plugin_id)
        if not plugin:
            return False

        plugin.enabled = True
        self._save_index()
        logger.info(f"[PLUGIN] Enabled plugin: {plugin_id}")
        return True

    def disable_plugin(self, plugin_id: str) -> bool:
        """
        Disable a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if successful, False otherwise
        """
        plugin = self._index.plugins.get(plugin_id)
        if not plugin:
            return False

        plugin.enabled = False
        self._save_index()
        logger.info(f"[PLUGIN] Disabled plugin: {plugin_id}")
        return True


# Singleton instance
_repository: Optional[PluginRepository] = None


def get_repository() -> PluginRepository:
    """Get the plugin repository singleton."""
    global _repository
    if _repository is None:
        _repository = PluginRepository()
    return _repository
