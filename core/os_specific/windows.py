"""
Windows Adapter - Chocolatey, PowerShell, services.msc

Implements OS-specific operations for Windows:
- Package management via Chocolatey
- Service management via PowerShell/sc
- Disk operations via diskpart
"""

import subprocess
from typing import Dict, List, Optional, Tuple

from core.os_specific.base import BaseOSAdapter


class WindowsAdapter(BaseOSAdapter):
    """Windows OS adapter."""

    def __init__(self):
        super().__init__()
        self.platform_name = "windows"

    def install_package(self, package: str) -> Tuple[bool, str]:
        """Install package via Chocolatey."""
        try:
            result = subprocess.run(
                ["choco", "install", "-y", package],
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f"Installed {package} via Chocolatey"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to install {package}: {e.stderr}"
        except FileNotFoundError:
            return (
                False,
                "Chocolatey not installed. Install from https://chocolatey.org",
            )

    def start_service(self, service: str) -> Tuple[bool, str]:
        """Start Windows service."""
        try:
            subprocess.run(["sc", "start", service], check=True, capture_output=True)
            return True, f"Started {service}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to start {service}"
