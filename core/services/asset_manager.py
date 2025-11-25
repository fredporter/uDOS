"""
uDOS Asset Manager (v1.5.3+)

Centralized asset management for fonts, icons, patterns, and other shared resources.
Provides loading, caching, versioning, and browsing capabilities for all extensions.

Key Features:
- Unified asset loading from extensions/assets/
- Asset versioning and dependency tracking
- Intelligent caching with hot-reload support
- Asset browser/preview interface
- Cross-extension asset sharing
- Asset metadata and search

Usage:
    from core.services.asset_manager import AssetManager

    # Initialize
    asset_mgr = AssetManager()

    # Load assets
    font = asset_mgr.load_font('chicago')
    icon = asset_mgr.load_icon('water-drop', format='svg')
    pattern = asset_mgr.load_pattern('teletext-grid')

    # Browse assets
    fonts = asset_mgr.list_assets('fonts')
    search_results = asset_mgr.search_assets('water')
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import re


class Asset:
    """
    Represents a single asset with metadata.
    """

    def __init__(
        self,
        name: str,
        asset_type: str,
        path: Path,
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an asset.

        Args:
            name: Asset name/identifier
            asset_type: Type (font, icon, pattern, css, js)
            path: Path to asset file
            version: Semantic version (e.g., "1.0.0")
            metadata: Additional metadata (author, license, tags, etc.)
        """
        self.name = name
        self.type = asset_type
        self.path = path
        self.version = version
        self.metadata = metadata or {}
        self.loaded_at: Optional[datetime] = None
        self._cached_data: Optional[Any] = None

    def load(self) -> Any:
        """Load asset data from disk."""
        if self._cached_data is not None:
            return self._cached_data

        try:
            if self.path.suffix in ['.json']:
                with open(self.path, 'r') as f:
                    self._cached_data = json.load(f)
            elif self.path.suffix in ['.svg', '.css', '.js', '.txt', '.md']:
                with open(self.path, 'r') as f:
                    self._cached_data = f.read()
            else:
                # Binary files (fonts, images)
                with open(self.path, 'rb') as f:
                    self._cached_data = f.read()

            self.loaded_at = datetime.now()
            return self._cached_data
        except Exception as e:
            raise IOError(f"Failed to load asset {self.name}: {e}")

    def reload(self) -> Any:
        """Force reload from disk (hot-reload)."""
        self._cached_data = None
        return self.load()

    def get_info(self) -> Dict[str, Any]:
        """Get asset information."""
        return {
            'name': self.name,
            'type': self.type,
            'path': str(self.path),
            'version': self.version,
            'size': self.path.stat().st_size if self.path.exists() else 0,
            'loaded': self.loaded_at.isoformat() if self.loaded_at else None,
            'metadata': self.metadata
        }

    def __repr__(self) -> str:
        return f"Asset({self.name}, {self.type}, v{self.version})"


class AssetManager:
    """
    Manages all shared assets for uDOS extensions.

    Provides centralized loading, caching, versioning, and browsing
    of fonts, icons, patterns, and other resources.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize Asset Manager.

        Args:
            base_path: Root path of uDOS installation (auto-detected if not provided)
        """
        # Determine base path
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent
        self.base_path = Path(base_path)

        # Asset directories
        self.assets_root = self.base_path / 'extensions' / 'assets'
        self.fonts_dir = self.assets_root / 'fonts'
        self.icons_dir = self.assets_root / 'icons'
        self.patterns_dir = self.assets_root / 'patterns'
        self.css_dir = self.assets_root / 'css'
        self.js_dir = self.assets_root / 'js'

        # Asset registry (name -> Asset)
        self._registry: Dict[str, Asset] = {}

        # Asset index by type
        self._index: Dict[str, List[str]] = {
            'fonts': [],
            'icons': [],
            'patterns': [],
            'css': [],
            'js': [],
            'other': []
        }

        # Dependency tracking (asset_name -> [dependent_assets])
        self._dependencies: Dict[str, List[str]] = {}

        # Load asset catalog
        self._load_catalog()

    def _load_catalog(self) -> None:
        """Scan asset directories and build catalog."""
        # Ensure directories exist
        self.assets_root.mkdir(parents=True, exist_ok=True)
        self.patterns_dir.mkdir(parents=True, exist_ok=True)

        # Scan fonts
        if self.fonts_dir.exists():
            self._scan_directory(self.fonts_dir, 'fonts')

        # Scan icons
        if self.icons_dir.exists():
            self._scan_directory(self.icons_dir, 'icons')

        # Scan patterns
        if self.patterns_dir.exists():
            self._scan_directory(self.patterns_dir, 'patterns')

        # Scan CSS
        if self.css_dir.exists():
            self._scan_directory(self.css_dir, 'css')

        # Scan JS
        if self.js_dir.exists():
            self._scan_directory(self.js_dir, 'js')

    def _scan_directory(self, directory: Path, asset_type: str) -> None:
        """
        Recursively scan directory for assets.

        Args:
            directory: Directory to scan
            asset_type: Type of assets to register
        """
        for item in directory.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                # Skip README and LICENSE files
                if item.name in ['README.md', 'LICENSE', 'CREDITS.md']:
                    continue

                # Create asset name from relative path
                rel_path = item.relative_to(directory)
                asset_name = str(rel_path.with_suffix('')).replace(os.sep, '/')

                # Register asset
                asset = Asset(
                    name=asset_name,
                    asset_type=asset_type,
                    path=item,
                    metadata=self._extract_metadata(item)
                )
                self._registry[f"{asset_type}/{asset_name}"] = asset
                self._index[asset_type].append(asset_name)

    def _extract_metadata(self, path: Path) -> Dict[str, Any]:
        """
        Extract metadata from asset file or companion metadata file.

        Args:
            path: Path to asset file

        Returns:
            Metadata dictionary
        """
        metadata = {
            'format': path.suffix[1:] if path.suffix else 'unknown',
            'size_bytes': path.stat().st_size
        }

        # Check for companion .meta.json file
        meta_file = path.with_suffix(path.suffix + '.meta.json')
        if meta_file.exists():
            try:
                with open(meta_file, 'r') as f:
                    meta_data = json.load(f)
                    metadata.update(meta_data)
            except Exception:
                pass

        return metadata

    def load_font(self, name: str, format: str = 'woff2') -> Optional[Asset]:
        """
        Load a font asset.

        Args:
            name: Font name (e.g., 'chicago', 'C64_User_Mono')
            format: Font format ('woff2', 'woff', 'ttf')

        Returns:
            Asset object or None if not found
        """
        # Try exact match first
        key = f"fonts/{name}"
        if key in self._registry:
            return self._registry[key]

        # Try with format extension
        key_with_format = f"fonts/{name}.{format}"
        if key_with_format in self._registry:
            return self._registry[key_with_format]

        # Search in index
        for font_name in self._index['fonts']:
            if name in font_name and format in font_name:
                return self._registry[f"fonts/{font_name}"]

        return None

    def load_icon(self, name: str, format: str = 'svg') -> Optional[Asset]:
        """
        Load an icon asset.

        Args:
            name: Icon name (e.g., 'water-drop', 'fire')
            format: Icon format ('svg', 'png')

        Returns:
            Asset object or None if not found
        """
        # Try exact match
        key = f"icons/{name}"
        if key in self._registry:
            return self._registry[key]

        # Try with format
        key_with_format = f"icons/{name}.{format}"
        if key_with_format in self._registry:
            return self._registry[key_with_format]

        # Search in index
        for icon_name in self._index['icons']:
            if name in icon_name and format in icon_name:
                return self._registry[f"icons/{icon_name}"]

        return None

    def load_pattern(self, name: str) -> Optional[Asset]:
        """
        Load a pattern asset.

        Args:
            name: Pattern name (e.g., 'teletext-grid', 'mac-checkerboard')

        Returns:
            Asset object or None if not found
        """
        key = f"patterns/{name}"
        if key in self._registry:
            return self._registry[key]

        # Search in index
        for pattern_name in self._index['patterns']:
            if name in pattern_name:
                return self._registry[f"patterns/{pattern_name}"]

        return None

    def load_css(self, name: str) -> Optional[Asset]:
        """Load a CSS asset."""
        key = f"css/{name}"
        if key in self._registry:
            return self._registry[key]

        # Try with .css extension
        if not name.endswith('.css'):
            return self.load_css(f"{name}.css")

        return None

    def load_js(self, name: str) -> Optional[Asset]:
        """Load a JavaScript asset."""
        key = f"js/{name}"
        if key in self._registry:
            return self._registry[key]

        # Try with .js extension
        if not name.endswith('.js'):
            return self.load_js(f"{name}.js")

        return None

    def list_assets(self, asset_type: Optional[str] = None) -> List[str]:
        """
        List all assets of a given type.

        Args:
            asset_type: Type filter ('fonts', 'icons', 'patterns', etc.)
                       If None, returns all assets

        Returns:
            List of asset names
        """
        if asset_type is None:
            return list(self._registry.keys())

        if asset_type not in self._index:
            return []

        return [f"{asset_type}/{name}" for name in self._index[asset_type]]

    def search_assets(self, query: str, asset_type: Optional[str] = None) -> List[Tuple[str, Asset]]:
        """
        Search assets by name or metadata.

        Args:
            query: Search query (supports regex)
            asset_type: Optional type filter

        Returns:
            List of (name, Asset) tuples matching query
        """
        results = []
        pattern = re.compile(query, re.IGNORECASE)

        for name, asset in self._registry.items():
            # Type filter
            if asset_type and not name.startswith(f"{asset_type}/"):
                continue

            # Search in name
            if pattern.search(name):
                results.append((name, asset))
                continue

            # Search in metadata
            metadata_str = json.dumps(asset.metadata)
            if pattern.search(metadata_str):
                results.append((name, asset))

        return results

    def get_asset_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an asset.

        Args:
            name: Asset name (with or without type prefix)

        Returns:
            Asset info dictionary or None
        """
        # Try with type prefix
        if name in self._registry:
            return self._registry[name].get_info()

        # Try searching across all types
        for asset_type in self._index.keys():
            full_name = f"{asset_type}/{name}"
            if full_name in self._registry:
                return self._registry[full_name].get_info()

        return None

    def reload_asset(self, name: str) -> bool:
        """
        Reload an asset from disk (hot-reload).

        Args:
            name: Asset name

        Returns:
            True if successful, False otherwise
        """
        if name not in self._registry:
            return False

        try:
            self._registry[name].reload()
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get asset manager statistics.

        Returns:
            Statistics dictionary
        """
        total_size = sum(
            asset.path.stat().st_size
            for asset in self._registry.values()
            if asset.path.exists()
        )

        loaded_count = sum(
            1 for asset in self._registry.values()
            if asset.loaded_at is not None
        )

        return {
            'total_assets': len(self._registry),
            'by_type': {k: len(v) for k, v in self._index.items()},
            'loaded': loaded_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'assets_root': str(self.assets_root)
        }

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return f"AssetManager({stats['total_assets']} assets, {stats['total_size_mb']}MB)"


# Global instance (initialized on first use)
_global_asset_manager: Optional[AssetManager] = None


def get_asset_manager(base_path: Optional[Path] = None) -> AssetManager:
    """
    Get global AssetManager instance (singleton pattern).

    Args:
        base_path: Root path of uDOS installation (only used on first call)

    Returns:
        Global AssetManager instance
    """
    global _global_asset_manager
    if _global_asset_manager is None:
        _global_asset_manager = AssetManager(base_path)
    return _global_asset_manager


def reset_asset_manager() -> None:
    """Reset global AssetManager (mainly for testing)."""
    global _global_asset_manager
    _global_asset_manager = None
