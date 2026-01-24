"""
Alpine Linux Adapter - APK package management, OpenRC services, lbu backup

Implements OS-specific operations for Alpine Linux:
- Package management via apk
- Service management via rc-service/rc-update (OpenRC)
- Persistence via lbu (Local Backup Utility)
- Disk operations via standard Linux tools
"""

import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from core.os_specific.base import BaseOSAdapter


class AlpineAdapter(BaseOSAdapter):
    """Alpine Linux OS adapter."""

    def __init__(self):
        super().__init__()
        self.platform_name = "alpine"

    # Package Management (APK)

    def install_package(self, package: str) -> Tuple[bool, str]:
        """Install package via apk."""
        try:
            result = subprocess.run(
                ["apk", "add", package], capture_output=True, text=True, check=True
            )
            return True, f"Installed {package}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to install {package}: {e.stderr}"

    def remove_package(self, package: str) -> Tuple[bool, str]:
        """Remove package via apk."""
        try:
            result = subprocess.run(
                ["apk", "del", package], capture_output=True, text=True, check=True
            )
            return True, f"Removed {package}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to remove {package}: {e.stderr}"

    def list_installed_packages(self) -> List[str]:
        """List installed APK packages."""
        try:
            result = subprocess.run(
                ["apk", "list", "--installed"],
                capture_output=True,
                text=True,
                check=True,
            )
            packages = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    # Format: package-version
                    pkg_name = line.split()[0].rsplit("-", 2)[0]
                    packages.append(pkg_name)
            return packages
        except subprocess.CalledProcessError:
            return []

    # Disk/Filesystem Operations

    def format_disk(
        self, device: str, filesystem: str, label: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Format disk using mkfs."""
        if filesystem not in ["ext4", "ext3", "ext2", "fat32", "exfat"]:
            return False, f"Filesystem {filesystem} not supported"

        cmd = []
        if filesystem.startswith("ext"):
            cmd = ["mkfs.ext4", device]
            if label:
                cmd.extend(["-L", label])
        elif filesystem == "fat32":
            cmd = ["mkfs.vfat", "-F", "32", device]
            if label:
                cmd.extend(["-n", label])

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True, f"Formatted {device} as {filesystem}"
        except subprocess.CalledProcessError as e:
            return False, f"Format failed: {e.stderr.decode()}"

    def mount_disk(self, device: str, mountpoint: str) -> Tuple[bool, str]:
        """Mount disk."""
        Path(mountpoint).mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(["mount", device, mountpoint], check=True)
            return True, f"Mounted {device} at {mountpoint}"
        except subprocess.CalledProcessError as e:
            return False, f"Mount failed: {str(e)}"

    def unmount_disk(self, mountpoint: str) -> Tuple[bool, str]:
        """Unmount disk."""
        try:
            subprocess.run(["umount", mountpoint], check=True)
            return True, f"Unmounted {mountpoint}"
        except subprocess.CalledProcessError as e:
            return False, f"Unmount failed: {str(e)}"

    # System Services (OpenRC)

    def start_service(self, service: str) -> Tuple[bool, str]:
        """Start service via rc-service."""
        try:
            subprocess.run(
                ["rc-service", service, "start"], check=True, capture_output=True
            )
            return True, f"Started {service}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to start {service}: {e.stderr.decode()}"

    def stop_service(self, service: str) -> Tuple[bool, str]:
        """Stop service via rc-service."""
        try:
            subprocess.run(
                ["rc-service", service, "stop"], check=True, capture_output=True
            )
            return True, f"Stopped {service}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to stop {service}: {e.stderr.decode()}"

    def enable_service(self, service: str) -> Tuple[bool, str]:
        """Enable service to start on boot via rc-update."""
        try:
            subprocess.run(
                ["rc-update", "add", service], check=True, capture_output=True
            )
            return True, f"Enabled {service}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to enable {service}: {e.stderr.decode()}"

    # Backup/Persistence (lbu - Local Backup Utility)

    def create_backup(self, path: str, destination: str) -> Tuple[bool, str]:
        """Create backup using lbu."""
        try:
            # lbu commit creates backup to /dev/mmcblk0p1 (or specified media)
            subprocess.run(["lbu", "commit"], check=True, capture_output=True)
            return True, "Alpine backup committed via lbu"
        except subprocess.CalledProcessError as e:
            return False, f"Backup failed: {e.stderr.decode()}"

    def restore_backup(self, backup_path: str) -> Tuple[bool, str]:
        """Restore from lbu backup (requires reboot)."""
        return False, "lbu restore requires system reboot with apkovl file"

    # Platform Info

    def get_platform_info(self) -> Dict[str, str]:
        """Get Alpine-specific info."""
        info = super().get_platform_info()

        # Get Alpine version
        try:
            alpine_release = Path("/etc/alpine-release")
            if alpine_release.exists():
                info["alpine_version"] = alpine_release.read_text().strip()
        except Exception:
            pass

        return info
