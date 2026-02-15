"""
Sonic plugin loader for uDOS extensions system.

Provides dynamic loading of Sonic Screwdriver components from library/sonic.
"""

from pathlib import Path
from typing import Optional, Any, Dict
import sys


class SonicPluginLoader:
    """Dynamic loader for Sonic plugin components."""

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize plugin loader.

        Args:
            repo_root: Repository root path (auto-detected if None)
        """
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[1]

        self.repo_root = Path(repo_root)
        self.library_path = self.repo_root / "library" / "sonic"
        self._ensure_paths()

    def _ensure_paths(self) -> None:
        """Ensure library paths are in sys.path."""
        library_root = str(self.repo_root / "library")
        if library_root not in sys.path:
            sys.path.insert(0, library_root)

    def load_schemas(self):
        """Load Sonic schemas module.

        Returns:
            Schemas module
        """
        try:
            from library.sonic.schemas import (
                Device,
                DeviceQuery,
                DeviceStats,
                FlashPackSpec,
                LayoutSpec,
                PartitionSpec,
                PayloadSpec,
                WindowsSpec,
                WizardSpec,
                SyncStatus,
            )
            return type('SonicSchemas', (), {
                'Device': Device,
                'DeviceQuery': DeviceQuery,
                'DeviceStats': DeviceStats,
                'FlashPackSpec': FlashPackSpec,
                'LayoutSpec': LayoutSpec,
                'PartitionSpec': PartitionSpec,
                'PayloadSpec': PayloadSpec,
                'WindowsSpec': WindowsSpec,
                'WizardSpec': WizardSpec,
                'SyncStatus': SyncStatus,
            })()
        except ImportError as e:
            raise RuntimeError(f"Failed to load Sonic schemas: {e}")

    def load_api(self):
        """Load Sonic API service.

        Returns:
            API module with SonicPluginService
        """
        try:
            from library.sonic.api import SonicPluginService, get_sonic_service
            return type('SonicAPI', (), {
                'SonicPluginService': SonicPluginService,
                'get_sonic_service': get_sonic_service,
            })()
        except ImportError as e:
            raise RuntimeError(f"Failed to load Sonic API: {e}")

    def load_sync(self):
        """Load Sonic database sync service.

        Returns:
            Sync module with DeviceDatabaseSync
        """
        try:
            from library.sonic.sync import DeviceDatabaseSync, get_sync_service
            return type('SonicSync', (), {
                'DeviceDatabaseSync': DeviceDatabaseSync,
                'get_sync_service': get_sync_service,
            })()
        except ImportError as e:
            raise RuntimeError(f"Failed to load Sonic sync: {e}")

    def load_all(self) -> Dict[str, Any]:
        """Load all Sonic plugin components.

        Returns:
            Dict with all loaded components
        """
        return {
            'schemas': self.load_schemas(),
            'api': self.load_api(),
            'sync': self.load_sync(),
            'loader': self,
        }

    def get_plugin_info(self) -> Dict[str, Any]:
        """Get Sonic plugin information.

        Returns:
            Plugin metadata
        """
        container_path = self.library_path / "container.json"

        if not container_path.exists():
            return {
                "installed": False,
                "path": str(self.library_path),
            }

        import json
        try:
            with open(container_path, "r") as f:
                container = json.load(f)

            return {
                "installed": True,
                "path": str(self.library_path),
                "id": container.get("container", {}).get("id"),
                "name": container.get("container", {}).get("name"),
                "version": container.get("container", {}).get("version"),
                "type": container.get("container", {}).get("type"),
                "capabilities": container.get("capabilities", {}),
            }
        except Exception as e:
            return {
                "installed": True,
                "path": str(self.library_path),
                "error": f"Failed to read container.json: {e}",
            }

    def is_available(self) -> bool:
        """Check if Sonic plugin is available.

        Returns:
            True if plugin can be loaded
        """
        try:
            self.load_schemas()
            return True
        except Exception:
            return False


def get_sonic_loader(repo_root: Optional[Path] = None) -> SonicPluginLoader:
    """Get Sonic plugin loader instance.

    Args:
        repo_root: Repository root path (auto-detected if None)

    Returns:
        SonicPluginLoader instance
    """
    return SonicPluginLoader(repo_root)


# Convenience function for quick access
def load_sonic_plugin(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    """Load Sonic plugin with all components.

    Args:
        repo_root: Repository root path (auto-detected if None)

    Returns:
        Dict with loaded components: schemas, api, sync, loader
    """
    loader = get_sonic_loader(repo_root)
    return loader.load_all()


__all__ = [
    "SonicPluginLoader",
    "get_sonic_loader",
    "load_sonic_plugin",
]
