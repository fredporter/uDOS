"""
Sonic plugin service (modular).

Replaces wizard/services/sonic_service.py with modular plugin system.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from extensions.sonic_loader import load_sonic_plugin


class SonicPluginService:
    """
    Modular Sonic plugin service.

    Replaces the legacy SonicService with dynamic plugin loading.
    """

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        """
        Initialize Sonic plugin service.

        Args:
            repo_root: Repository root path (auto-detected if None)
        """
        try:
            self.plugin = load_sonic_plugin(repo_root)
            self.api = self.plugin['api'].get_sonic_service()
            self.sync = self.plugin['sync'].get_sync_service()
            self.available = True
        except Exception as e:
            self.available = False
            self.error = str(e)

    def health(self) -> Dict[str, Any]:
        """Get service health status."""
        if not self.available:
            return {
                "status": "error",
                "message": f"Plugin not available: {self.error}",
                "available": False,
            }

        return self.api.health()

    def is_available(self) -> bool:
        """Check if plugin is available."""
        return self.available


def get_sonic_service(repo_root: Optional[Path] = None) -> SonicPluginService:
    """
    Get Sonic plugin service instance.

    Args:
        repo_root: Repository root path (auto-detected if None)

    Returns:
        SonicPluginService instance
    """
    return SonicPluginService(repo_root)


__all__ = [
    "SonicPluginService",
    "get_sonic_service",
]
