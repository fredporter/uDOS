"""
Ubuntu Adapter - APT package management, systemd services

Implements OS-specific operations for Ubuntu:
- Package management via apt
- Service management via systemctl (systemd)
- Disk operations via standard Linux tools
"""

import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from core.os_specific.base import BaseOSAdapter


class UbuntuAdapter(BaseOSAdapter):
    """Ubuntu Linux OS adapter."""

    def __init__(self):
        super().__init__()
        self.platform_name = "ubuntu"

    def install_package(self, package: str) -> Tuple[bool, str]:
        """Install package via apt."""
        try:
            subprocess.run(["apt-get", "update"], check=True, capture_output=True)
            result = subprocess.run(
                ["apt-get", "install", "-y", package],
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f"Installed {package} via apt"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to install {package}: {e.stderr}"

    def start_service(self, service: str) -> Tuple[bool, str]:
        """Start service via systemctl."""
        try:
            subprocess.run(
                ["systemctl", "start", service], check=True, capture_output=True
            )
            return True, f"Started {service}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to start {service}: {e.stderr.decode()}"

    def enable_service(self, service: str) -> Tuple[bool, str]:
        """Enable service to start on boot via systemctl."""
        try:
            subprocess.run(
                ["systemctl", "enable", service], check=True, capture_output=True
            )
            return True, f"Enabled {service}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to enable {service}: {e.stderr.decode()}"
