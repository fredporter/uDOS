"""
Base OS Adapter - Abstract Interface for OS-Specific Operations

All platform adapters inherit from this base class.
Default implementations raise NotImplementedError or return graceful warnings.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class BaseOSAdapter(ABC):
    """
    Abstract base class for OS-specific operations.

    All platform adapters (Alpine, macOS, Ubuntu, Windows) must implement
    these methods.
    """

    def __init__(self):
        self.platform_name = "unknown"

    # Package Management

    def install_package(self, package: str) -> Tuple[bool, str]:
        """
        Install a package using platform package manager.

        Args:
            package: Package name

        Returns:
            (success: bool, message: str)
        """
        return False, f"Package installation not supported on {self.platform_name}"

    def remove_package(self, package: str) -> Tuple[bool, str]:
        """
        Remove a package using platform package manager.

        Args:
            package: Package name

        Returns:
            (success: bool, message: str)
        """
        return False, f"Package removal not supported on {self.platform_name}"

    def list_installed_packages(self) -> List[str]:
        """
        List all installed packages.

        Returns:
            List of package names
        """
        return []

    # Disk/Filesystem Operations

    def format_disk(
        self, device: str, filesystem: str, label: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Format a disk with specified filesystem.

        Args:
            device: Device path (e.g., /dev/sda1, disk2)
            filesystem: Filesystem type (ext4, apfs, ntfs, etc.)
            label: Optional volume label

        Returns:
            (success: bool, message: str)
        """
        return False, f"Disk formatting not supported on {self.platform_name}"

    def mount_disk(self, device: str, mountpoint: str) -> Tuple[bool, str]:
        """
        Mount a disk at specified mountpoint.

        Args:
            device: Device path
            mountpoint: Mount location

        Returns:
            (success: bool, message: str)
        """
        return False, f"Disk mounting not supported on {self.platform_name}"

    def unmount_disk(self, mountpoint: str) -> Tuple[bool, str]:
        """
        Unmount a disk.

        Args:
            mountpoint: Mount location

        Returns:
            (success: bool, message: str)
        """
        return False, f"Disk unmounting not supported on {self.platform_name}"

    # System Services

    def start_service(self, service: str) -> Tuple[bool, str]:
        """
        Start a system service.

        Args:
            service: Service name

        Returns:
            (success: bool, message: str)
        """
        return False, f"Service management not supported on {self.platform_name}"

    def stop_service(self, service: str) -> Tuple[bool, str]:
        """
        Stop a system service.

        Args:
            service: Service name

        Returns:
            (success: bool, message: str)
        """
        return False, f"Service management not supported on {self.platform_name}"

    def enable_service(self, service: str) -> Tuple[bool, str]:
        """
        Enable a service to start on boot.

        Args:
            service: Service name

        Returns:
            (success: bool, message: str)
        """
        return False, f"Service management not supported on {self.platform_name}"

    # Backup/Persistence

    def create_backup(self, path: str, destination: str) -> Tuple[bool, str]:
        """
        Create system backup.

        Args:
            path: Source path
            destination: Backup destination

        Returns:
            (success: bool, message: str)
        """
        return False, f"Backup not implemented for {self.platform_name}"

    def restore_backup(self, backup_path: str) -> Tuple[bool, str]:
        """
        Restore from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            (success: bool, message: str)
        """
        return False, f"Restore not implemented for {self.platform_name}"

    # Platform Info

    def get_platform_info(self) -> Dict[str, str]:
        """
        Get platform-specific information.

        Returns:
            Dict with platform details
        """
        return {
            "platform": self.platform_name,
            "adapter": self.__class__.__name__,
        }
