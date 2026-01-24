"""
Plugin Discovery & Registry System

Scans library/ and plugins/ folders to build a registry of available plugins.
Supports both shipping (active) and experimental (archived) plugins.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from core.services.logging_manager import get_logger

logger = get_logger("plugin-discovery")


@dataclass
class PluginMetadata:
    """Plugin metadata from discovery"""

    name: str  # Plugin name
    type: str  # "transport", "api", "extension", "library"
    tier: str  # "ucode", "wizard", "experimental"
    path: Path  # Absolute path
    version: str  # Version if available
    description: str = ""  # Plugin description
    author: str = ""  # Author/owner
    homepage: str = ""  # GitHub/project URL
    tags: List[str] = None  # Tags (e.g., "networking", "database")
    dependencies: List[str] = None  # Required plugins
    active: bool = True  # If False, deprecated/archived
    last_updated: str = ""  # Last modification time

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []

    def to_dict(self):
        """Convert to serializable dict"""
        data = asdict(self)
        data["path"] = str(data["path"])
        return data


class PluginDiscovery:
    """Discover and catalog plugins"""

    # Plugin directory patterns
    SHIPPING_PATHS = {
        "plugins": {
            "api": ("api", "REST/WebSocket API"),
            "transport": ("transport", "Network transports"),
        },
        "library/ucode": {
            "micro": ("micro", "Minimal Core Linux"),
            "marp": ("marp", "Presentation framework"),
            "alpine": ("alpine", "Alpine Linux"),
            "meshcore": ("meshcore", "P2P mesh networking"),
        },
    }

    WIZARD_PATHS = {
        "library/wizard": {
            "ollama": ("ollama", "Local LLM runtime"),
            "mistral-vibe": ("mistral-vibe", "Offline AI interface"),
            "gemini-cli": ("gemini-cli", "Google AI CLI"),
            "nethack": ("nethack", "Roguelike game"),
            "home-assistant": ("home-assistant", "Home automation"),
        }
    }

    EXPERIMENTAL_PATHS = {
        "plugins/.archive": {
            "groovebox": ("groovebox", "Music production"),
            "vscode": ("vscode", "VS Code extension"),
            "tauri": ("tauri", "Desktop app framework"),
            "assistant": ("assistant", "AI assistant"),
        }
    }

    def __init__(self, root_path: Path = None):
        """
        Initialize plugin discovery.

        Args:
            root_path: Root of uDOS repo (defaults to current directory)
        """
        self.root_path = Path(root_path or ".")
        self.registry: Dict[str, PluginMetadata] = {}
        self.timestamp = datetime.now().isoformat()

        logger.info(f"[WIZ] PluginDiscovery initialized at {self.root_path}")

    def discover_all(self) -> Dict[str, PluginMetadata]:
        """
        Discover all plugins (shipping, wizard, experimental).

        Returns:
            Dictionary of plugin_name -> PluginMetadata
        """
        logger.info("[WIZ] Starting plugin discovery...")

        # Scan shipping plugins
        self._scan_tier(self.SHIPPING_PATHS, tier="ucode")

        # Scan wizard plugins
        self._scan_tier(self.WIZARD_PATHS, tier="wizard")

        # Scan experimental plugins
        self._scan_tier(self.EXPERIMENTAL_PATHS, tier="experimental")

        logger.info(f"[WIZ] Discovered {len(self.registry)} plugins")
        return self.registry

    def _scan_tier(self, paths_config: Dict, tier: str):
        """Scan plugins in a tier (ucode, wizard, experimental)"""
        for base_dir, plugins_config in paths_config.items():
            base_path = self.root_path / base_dir

            if not base_path.exists():
                logger.warning(f"[WIZ] Path not found: {base_path}")
                continue

            for plugin_name, (folder_name, description) in plugins_config.items():
                plugin_path = base_path / folder_name

                if not plugin_path.exists():
                    logger.warning(f"[WIZ] Plugin not found: {plugin_path}")
                    continue

                metadata = self._create_metadata(
                    plugin_name, plugin_path, tier, description
                )
                self.registry[plugin_name] = metadata

    def _create_metadata(
        self, name: str, path: Path, tier: str, description: str
    ) -> PluginMetadata:
        """Create metadata for a plugin"""
        # Try to read version.json
        version = self._read_version(path)

        # Get last modified time
        try:
            mtime = path.stat().st_mtime
            last_updated = datetime.fromtimestamp(mtime).isoformat()
        except OSError:
            last_updated = ""

        # Determine plugin type from path
        plugin_type = self._determine_type(path, tier)

        # Read metadata if available
        author, homepage, tags, deps = self._read_plugin_config(path)

        metadata = PluginMetadata(
            name=name,
            type=plugin_type,
            tier=tier,
            path=path,
            version=version,
            description=description,
            author=author,
            homepage=homepage,
            tags=tags or [],
            dependencies=deps or [],
            active=(tier != "experimental"),
            last_updated=last_updated,
        )

        logger.info(f"[WIZ] Discovered: {name} ({plugin_type}) v{version}")
        return metadata

    def _read_version(self, path: Path) -> str:
        """Read version from version.json"""
        version_file = path / "version.json"

        try:
            if version_file.exists():
                with open(version_file) as f:
                    data = json.load(f)
                    version = data.get("version", data.get("build", "1.0.0"))
                    return str(version)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"[WIZ] Could not read version from {path}: {e}")

        return "unknown"

    def _determine_type(self, path: Path, tier: str) -> str:
        """Determine plugin type from path or structure"""
        path_str = str(path)

        # Check path patterns
        if "transport" in path_str:
            return "transport"
        elif "api" in path_str:
            return "api"
        elif tier == "wizard":
            return "library"
        elif path_str.endswith("meshcore"):
            return "transport"

        # Default based on tier
        return "library" if tier in ["ucode", "wizard"] else "extension"

    def _read_plugin_config(self, path: Path) -> Tuple[str, str, List[str], List[str]]:
        """
        Read plugin configuration from README or config files.

        Returns:
            (author, homepage, tags, dependencies)
        """
        author = ""
        homepage = ""
        tags = []
        deps = []

        # Try plugin.json (for VS Code extensions)
        plugin_json = path / "plugin.json"
        if plugin_json.exists():
            try:
                with open(plugin_json) as f:
                    data = json.load(f)
                    author = data.get("author", "")
                    homepage = data.get("homepage", data.get("repository", ""))
                    tags = data.get("keywords", [])
            except (json.JSONDecodeError, KeyError):
                pass

        # Try package.json
        package_json = path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    author = data.get("author", {}).get("name", data.get("author", ""))
                    homepage = data.get(
                        "homepage", data.get("repository", {}).get("url", "")
                    )
                    deps = list(data.get("dependencies", {}).keys())[:5]  # First 5
            except (json.JSONDecodeError, KeyError):
                pass

        return author, homepage, tags, deps

    def get_plugin(self, name: str) -> Optional[PluginMetadata]:
        """Get plugin by name"""
        return self.registry.get(name)

    def list_plugins(
        self, tier: str = None, plugin_type: str = None, active_only: bool = True
    ) -> List[PluginMetadata]:
        """
        List plugins with optional filtering.

        Args:
            tier: Filter by tier ("ucode", "wizard", "experimental")
            plugin_type: Filter by type ("api", "transport", "library", "extension")
            active_only: If True, exclude experimental/archived

        Returns:
            List of matching plugins
        """
        results = []

        for plugin in self.registry.values():
            # Apply filters
            if tier and plugin.tier != tier:
                continue
            if plugin_type and plugin.type != plugin_type:
                continue
            if active_only and not plugin.active:
                continue

            results.append(plugin)

        return sorted(results, key=lambda p: p.name)

    def get_dependencies(
        self, plugin_name: str, recursive: bool = False
    ) -> List[PluginMetadata]:
        """
        Get plugin dependencies.

        Args:
            plugin_name: Plugin to check
            recursive: If True, include transitive dependencies

        Returns:
            List of dependency plugins
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return []

        deps = []
        for dep_name in plugin.dependencies:
            dep = self.get_plugin(dep_name)
            if dep:
                deps.append(dep)

                # Recursive
                if recursive:
                    deps.extend(self.get_dependencies(dep_name, recursive=True))

        return deps

    def get_dependents(self, plugin_name: str) -> List[PluginMetadata]:
        """Get plugins that depend on this one"""
        results = []

        for plugin in self.registry.values():
            if plugin_name in plugin.dependencies:
                results.append(plugin)

        return sorted(results, key=lambda p: p.name)

    def validate_dependencies(self) -> Dict[str, List[str]]:
        """
        Validate all plugin dependencies.

        Returns:
            Dictionary of plugin_name -> [missing_dependencies]
        """
        missing = {}

        for name, plugin in self.registry.items():
            missing_deps = []

            for dep in plugin.dependencies:
                if dep not in self.registry:
                    missing_deps.append(dep)

            if missing_deps:
                missing[name] = missing_deps
                logger.warning(f"[WIZ] {name} missing dependencies: {missing_deps}")

        return missing

    def save_registry(self, output_path: Path = None):
        """
        Save plugin registry to JSON file.

        Args:
            output_path: Where to save (defaults to memory/plugin-registry.json)
        """
        if not output_path:
            output_path = Path("memory/plugin-registry.json")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        registry_data = {
            "timestamp": self.timestamp,
            "version": "1.0.0",
            "total": len(self.registry),
            "plugins": {
                name: plugin.to_dict() for name, plugin in self.registry.items()
            },
        }

        with open(output_path, "w") as f:
            json.dump(registry_data, f, indent=2)

        logger.info(f"[WIZ] Saved registry to {output_path}")

    def load_registry(self, input_path: Path = None) -> Dict[str, PluginMetadata]:
        """
        Load plugin registry from JSON file.

        Args:
            input_path: Where to load from (defaults to memory/plugin-registry.json)

        Returns:
            Loaded registry
        """
        if not input_path:
            input_path = Path("memory/plugin-registry.json")

        if not input_path.exists():
            logger.warning(f"[WIZ] Registry file not found: {input_path}")
            return {}

        try:
            with open(input_path) as f:
                data = json.load(f)

            self.registry = {}
            for name, plugin_data in data.get("plugins", {}).items():
                plugin_data["path"] = Path(plugin_data["path"])
                self.registry[name] = PluginMetadata(**plugin_data)

            logger.info(f"[WIZ] Loaded {len(self.registry)} plugins from {input_path}")
            return self.registry

        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"[WIZ] Failed to load registry: {e}")
            return {}

    def format_plugin_list(self, plugins: List[PluginMetadata] = None) -> str:
        """
        Format plugin list for display.

        Args:
            plugins: Plugins to display (defaults to all)

        Returns:
            Formatted string
        """
        if plugins is None:
            plugins = sorted(self.registry.values(), key=lambda p: (p.tier, p.name))

        if not plugins:
            return "No plugins found"

        lines = []
        lines.append("")
        lines.append("╔═══════════════════════════════════════════════════════════╗")
        lines.append("║                    PLUGIN REGISTRY                        ║")
        lines.append("╚═══════════════════════════════════════════════════════════╝")
        lines.append("")

        # Group by tier
        by_tier = {}
        for plugin in plugins:
            if plugin.tier not in by_tier:
                by_tier[plugin.tier] = []
            by_tier[plugin.tier].append(plugin)

        for tier in ["ucode", "wizard", "experimental"]:
            if tier not in by_tier:
                continue

            tier_plugins = by_tier[tier]
            tier_name = {
                "ucode": "📦 Shipping (Production)",
                "wizard": "🧙 Wizard Server",
                "experimental": "🧪 Experimental",
            }.get(tier, tier)

            lines.append(f"{tier_name}")
            lines.append("─" * 60)

            for plugin in sorted(tier_plugins, key=lambda p: p.name):
                status = "✅" if plugin.active else "⚠️ "
                lines.append(
                    f"{status} {plugin.name:20} {plugin.type:12} v{plugin.version:8} "
                    f"({plugin.description[:30]}...)"
                )

            lines.append("")

        lines.append(f"Total: {len(plugins)} plugins")
        lines.append("")

        return "\n".join(lines)
