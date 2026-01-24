"""
macOS Adapter - Homebrew, diskutil, launchctl

Implements OS-specific operations for macOS:
- Package management via Homebrew
- Disk operations via diskutil
- Service management via launchctl
- Preferences via defaults
"""

import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from core.os_specific.base import BaseOSAdapter


class MacOSAdapter(BaseOSAdapter):
    """macOS OS adapter."""

    def __init__(self):
        super().__init__()
        self.platform_name = "macos"

    def install_package(self, package: str) -> Tuple[bool, str]:
        """Install package via Homebrew."""
        try:
            result = subprocess.run(
                ["brew", "install", package], capture_output=True, text=True, check=True
            )
            return True, f"Installed {package} via Homebrew"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to install {package}: {e.stderr}"
        except FileNotFoundError:
            return False, "Homebrew not installed. Install from https://brew.sh"

    def format_disk(
        self, device: str, filesystem: str, label: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Format disk using diskutil."""
        if filesystem.lower() not in ["apfs", "hfs+", "fat32", "exfat"]:
            return False, f"Filesystem {filesystem} not supported on macOS"

        fs_map = {"apfs": "APFS", "hfs+": "HFS+", "fat32": "FAT32", "exfat": "ExFAT"}

        fs_name = fs_map.get(filesystem.lower(), filesystem)
        volume_name = label or "Untitled"

        try:
            cmd = ["diskutil", "eraseDisk", fs_name, volume_name, device]
            subprocess.run(cmd, check=True, capture_output=True)
            return True, f"Formatted {device} as {fs_name}"
        except subprocess.CalledProcessError as e:
            return False, f"Format failed: {e.stderr.decode()}"

    def get_platform_info(self) -> Dict[str, str]:
        """Get macOS-specific info."""
        info = super().get_platform_info()

        import platform

        info["macos_version"] = platform.mac_ver()[0]

        return info
