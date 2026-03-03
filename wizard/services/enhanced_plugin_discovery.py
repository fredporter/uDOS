"""Enhanced Plugin Discovery Service
==================================

Discovers and catalogs all uDOS plugins and extensions from:
- ~/uDOS/distribution/plugins/ (distribution packages)
- ~/uDOS/library/ (containerized plugins)
- ~/uDOS/extensions/ (API extensions, transport, etc)

Includes git/version control metadata, installer pathways, and update tracking.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from pathlib import Path
import subprocess
from typing import Any

from core.services.container_catalog_service import get_container_catalog_service
from core.services.unified_config_loader import get_config
from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("plugin-discovery")


@dataclass
class GitMetadata:
    """Git information for a plugin/extension."""

    remote_url: str | None = None
    branch: str = "main"
    commit_hash: str | None = None
    commit_date: str | None = None
    tags: list[str] = field(default_factory=list)
    is_dirty: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PluginMetadata:
    """Enhanced plugin metadata with git and installer info."""

    # Identity
    id: str
    name: str
    description: str
    category: str
    tier: str  # "core" | "library" | "extension" | "transport" | "api"

    # Versioning
    version: str
    installed: bool = False
    installed_version: str | None = None
    update_available: bool = False

    # Metadata
    license: str = "MIT"
    author: str = ""
    homepage: str = ""
    documentation: str = ""

    # Paths
    source_path: str = ""  # Path relative to UDOS_ROOT
    config_path: str | None = None

    # Git info
    git: GitMetadata | None = None

    # Installation
    installer_type: str = "git"  # "git" | "apk" | "manual" | "container"
    installer_script: str | None = None
    package_file: str | None = None

    # Dependencies
    dependencies: list[str] = field(default_factory=list)

    # Status
    available: bool = True
    health_check_url: str | None = None
    running: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.git:
            data["git"] = self.git.to_dict()
        return data


class EnhancedPluginDiscovery:
    """Discover plugins from multiple sources with git/version metadata."""

    PLUGIN_SOURCES = {
        "distribution": {
            "path": "distribution/plugins",
            "tier": "core",
            "category": "plugin",
        },
        "library": {"path": "library", "tier": "library", "category": "container"},
        "extensions_root": {
            "path": "extensions",
            "tier": "extension",
            "category": "extension",
        },
        "extensions_transport": {
            "path": "extensions/transport",
            "tier": "extension",
            "category": "transport",
        },
        "extensions_api": {
            "path": "extensions/api",
            "tier": "extension",
            "category": "api",
        },
    }

    def __init__(self, repo_root: Path = None):
        """Initialize plugin discovery."""
        self.repo_root = Path(repo_root or get_repo_root())
        self._explicit_repo_root = repo_root is not None
        self.udos_root = self._get_udos_root()
        self.plugins: dict[str, PluginMetadata] = {}
        self.last_scan = None

        logger.info(f"[DISCOVERY] Initialized with UDOS_ROOT={self.udos_root}")

    def _get_udos_root(self) -> Path:
        """Get UDOS_ROOT from env or use repo_root."""
        if self._explicit_repo_root:
            return self.repo_root
        udos_root_env = get_config("UDOS_ROOT", "")
        if udos_root_env:
            return Path(udos_root_env).expanduser()
        return self.repo_root

    def discover_all(self) -> dict[str, PluginMetadata]:
        """Discover all plugins from all sources."""
        logger.info("[DISCOVERY] Starting plugin discovery scan")
        self.plugins.clear()

        for source_key, source_info in self.PLUGIN_SOURCES.items():
            self._discover_source(source_key, source_info)

        self.last_scan = datetime.now().isoformat()
        logger.info(f"[DISCOVERY] Found {len(self.plugins)} plugins")

        return self.plugins

    def _discover_source(self, source_key: str, source_info: dict[str, str]):
        """Discover plugins from a specific source."""
        source_path = self.udos_root / source_info["path"]

        if not source_path.exists():
            logger.debug(f"[DISCOVERY] Source path does not exist: {source_path}")
            return

        logger.info(f"[DISCOVERY] Scanning {source_key} at {source_path}")

        if source_key == "distribution":
            self._discover_distribution_plugins(source_path, source_info)
        elif source_key == "library":
            self._discover_library_containers(source_path, source_info)
        else:  # extensions
            self._discover_extensions(source_path, source_info)

    def _discover_distribution_plugins(
        self, plugin_dir: Path, source_info: dict[str, str]
    ):
        """Discover plugins from distribution/plugins."""
        # Load index.json if it exists
        index_path = plugin_dir / "index.json"
        if index_path.exists():
            try:
                index = json.loads(index_path.read_text())
                for plugin_id, plugin_data in index.get("plugins", {}).items():
                    metadata = PluginMetadata(
                        id=plugin_id,
                        name=plugin_data.get("name", plugin_id),
                        description=plugin_data.get("description", ""),
                        category=source_info["category"],
                        tier=source_info["tier"],
                        version=plugin_data.get("version", "0.0.0"),
                        license=plugin_data.get("license", "MIT"),
                        author=plugin_data.get("author", ""),
                        homepage=plugin_data.get("homepage", ""),
                        documentation=plugin_data.get("documentation", ""),
                        source_path=f"distribution/plugins/{plugin_id}",
                        package_file=plugin_data.get("package_file"),
                        installed=plugin_data.get("installed", False),
                        installed_version=plugin_data.get("installed_version"),
                        dependencies=plugin_data.get("dependencies", []),
                    )

                    # Get git info if available
                    plugin_path = plugin_dir / plugin_id
                    metadata.git = self._get_git_metadata(plugin_path)

                    # Check for installer script
                    installer_script = plugin_data.get("install_script")
                    if installer_script:
                        metadata.installer_script = installer_script

                    self.plugins[plugin_id] = metadata
                    logger.debug(f"[DISCOVERY] Found plugin: {plugin_id}")
            except Exception as e:
                logger.error(f"[DISCOVERY] Error reading {index_path}: {e!s}")

    def _discover_library_containers(
        self, library_dir: Path, source_info: dict[str, str]
    ):
        """Discover containerized plugins from library/."""
        catalog = get_container_catalog_service(self.udos_root)
        for entry in catalog.list_by_kind("library"):
            try:
                package_dependencies = entry.metadata.get("package_dependencies", {})
                plugin_id = entry.entry_id
                metadata = PluginMetadata(
                    id=plugin_id,
                    name=entry.label or plugin_id,
                    description=entry.summary,
                    category=source_info["category"],
                    tier=source_info["tier"],
                    version=entry.version or "0.0.0",
                    license=str(entry.metadata.get("license") or "MIT"),
                    author=str(entry.metadata.get("author") or ""),
                    homepage=str(entry.metadata.get("homepage") or ""),
                    documentation=str(entry.metadata.get("documentation") or ""),
                    source_path=entry.path,
                    config_path=entry.metadata.get("manifest_path"),
                    installer_type="container",
                    health_check_url=entry.metadata.get("health_check_url"),
                    dependencies=list(entry.metadata.get("integration_dependencies") or [])
                    + list(package_dependencies.get("system_dependencies") or []),
                )
                repo_path = Path(entry.metadata.get("resolved_repo_path") or (self.udos_root / entry.path))
                metadata.git = self._get_git_metadata(repo_path)

                manifest_path = (
                    self.udos_root
                    / "distribution"
                    / "plugins"
                    / plugin_id
                    / "manifest.json"
                )
                if manifest_path.exists():
                    metadata.package_file = str(manifest_path.relative_to(self.udos_root))

                self.plugins[plugin_id] = metadata
                logger.debug(f"[DISCOVERY] Found container: {plugin_id}")
            except Exception as e:
                logger.error(f"[DISCOVERY] Error reading container {entry.entry_id}: {e!s}")

    def _discover_extensions(self, ext_dir: Path, source_info: dict[str, str]):
        """Discover extensions (transport, API, etc)."""
        if not ext_dir.exists():
            return

        catalog = get_container_catalog_service(self.udos_root)
        category = source_info["category"]
        for entry in catalog.list_by_kind("extension"):
            entry_path = self.udos_root / entry.path
            if entry_path.parent != ext_dir:
                continue

            metadata = PluginMetadata(
                id=entry.entry_id,
                name=entry.label or entry.entry_id.replace("-", " ").title(),
                description=entry.summary or str(entry.metadata.get("description") or ""),
                category=category,
                tier=source_info["tier"],
                version=entry.version or "0.0.0",
                license="MIT",
                source_path=entry.path,
                config_path=entry.metadata.get("manifest_path"),
                installer_type="git",
                installed=entry.available,
            )
            metadata.git = self._get_git_metadata(entry_path)

            self.plugins[entry.entry_id] = metadata
            logger.debug(f"[DISCOVERY] Found extension: {entry.entry_id}")

    def _get_git_metadata(self, plugin_path: Path) -> GitMetadata | None:
        """Extract git metadata from a plugin directory."""
        try:
            if not (plugin_path / ".git").exists() and not self._is_git_submodule(
                plugin_path
            ):
                return None

            git_meta = GitMetadata()

            # Get remote URL
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=str(plugin_path),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    git_meta.remote_url = result.stdout.strip()
            except Exception:
                pass

            # Get current branch
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=str(plugin_path),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    git_meta.branch = result.stdout.strip()
            except Exception:
                pass

            # Get commit hash
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(plugin_path),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    git_meta.commit_hash = result.stdout.strip()[:8]
            except Exception:
                pass

            # Get commit date
            try:
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%ai"],
                    cwd=str(plugin_path),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    git_meta.commit_date = result.stdout.strip()
            except Exception:
                pass

            # Check if dirty
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=str(plugin_path),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    git_meta.is_dirty = bool(result.stdout.strip())
            except Exception:
                pass

            return git_meta
        except Exception as e:
            logger.debug(
                f"[DISCOVERY] Error getting git metadata for {plugin_path}: {e!s}"
            )
            return None

    def _is_git_submodule(self, path: Path) -> bool:
        """Check if path is a git submodule."""
        try:
            gitmodules = self.udos_root / ".gitmodules"
            if gitmodules.exists():
                content = gitmodules.read_text()
                relative_path = path.relative_to(self.udos_root)
                return str(relative_path) in content
        except Exception:
            pass
        return False

    def get_plugin(self, plugin_id: str) -> PluginMetadata | None:
        """Get a specific plugin's metadata."""
        return self.plugins.get(plugin_id)

    def get_plugins_by_tier(self, tier: str) -> list[PluginMetadata]:
        """Get all plugins in a specific tier."""
        return [p for p in self.plugins.values() if p.tier == tier]

    def get_plugins_by_category(self, category: str) -> list[PluginMetadata]:
        """Get all plugins in a specific category."""
        return [p for p in self.plugins.values() if p.category == category]

    def search_plugins(self, query: str) -> list[PluginMetadata]:
        """Search plugins by name or description."""
        query_lower = query.lower()
        results = []
        for plugin in self.plugins.values():
            if (
                query_lower in plugin.name.lower()
                or query_lower in plugin.description.lower()
                or query_lower in plugin.id.lower()
            ):
                results.append(plugin)
        return results


# Singleton instance
_discovery_instance: EnhancedPluginDiscovery | None = None


def get_discovery_service(repo_root: Path = None) -> EnhancedPluginDiscovery:
    """Get or create the plugin discovery service."""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = EnhancedPluginDiscovery(repo_root)
    return _discovery_instance
