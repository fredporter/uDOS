"""
OS-Specific Command Implementations for uDOS

This package contains OS-specific implementations for commands that require
kernel-level or platform-specific operations.

Architecture:
- alpine/ — Alpine Linux operations (apk, lbu, setup-alpine, rc-service)
- macos/ — macOS operations (diskutil, hdiutil, launchctl, defaults)
- ubuntu/ — Ubuntu operations (apt, systemctl, snap)
- windows/ — Windows operations (PowerShell, diskpart, services)

Usage:
    from core.os_specific import get_os_adapter

    adapter = get_os_adapter()  # Auto-detects platform
    result = adapter.format_disk("/dev/sda1", "ext4")
"""

from core.services.os_detector import get_os_detector


def get_os_adapter():
    """
    Get OS-specific adapter for current platform.

    Returns:
        Platform-specific adapter instance
    """
    detector = get_os_detector()
    platform = detector.get_platform()

    if platform == "alpine":
        from core.os_specific.alpine import AlpineAdapter

        return AlpineAdapter()
    elif platform == "macos":
        from core.os_specific.macos import MacOSAdapter

        return MacOSAdapter()
    elif platform == "ubuntu":
        from core.os_specific.ubuntu import UbuntuAdapter

        return UbuntuAdapter()
    elif platform == "windows":
        from core.os_specific.windows import WindowsAdapter

        return WindowsAdapter()
    else:
        # Fallback to base adapter (no-ops with warnings)
        from core.os_specific.base import BaseOSAdapter

        return BaseOSAdapter()


__all__ = ["get_os_adapter"]
