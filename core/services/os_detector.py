"""
OS Detection Service for uDOS Core

Provides platform detection, capability checking, and OS-specific constraint warnings.
Used by command handlers to adapt behavior across Alpine Linux, macOS, Ubuntu, Windows.

Architecture:
- Alpine Linux: Primary target for embedded/TUI deployments
- macOS/Ubuntu/Windows: Development and desktop use

Usage:
    from core.services.os_detector import get_os_detector

    detector = get_os_detector()

    # Check platform
    if detector.is_alpine():
        print("Running on Alpine Linux")

    # Check capabilities
    if detector.can_format_disk("ext4"):
        # Proceed with disk formatting
    else:
        detector.warn_os_constraint("DISK FORMAT", ["alpine", "ubuntu"])
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class OSDetector:
    """
    Detect operating system and provide platform-specific capabilities.

    Singleton pattern - use get_os_detector() to access instance.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._platform = self._detect_platform()
        self._capabilities = self._detect_capabilities()
        self._initialized = True

    def _detect_platform(self) -> str:
        """
        Detect current OS platform.

        Returns:
            'alpine', 'macos', 'ubuntu', 'windows', 'linux', or 'unknown'
        """
        # Check for environment override (testing)
        override = os.environ.get("UDOS_PLATFORM", "").lower()
        if override in ("alpine", "macos", "ubuntu", "windows", "linux"):
            return override

        system = platform.system()

        if system == "Darwin":
            return "macos"

        elif system == "Windows":
            return "windows"

        elif system == "Linux":
            # Detect specific Linux distro
            return self._detect_linux_distro()

        return "unknown"

    def _detect_linux_distro(self) -> str:
        """
        Detect specific Linux distribution.

        Priority:
        1. Alpine Linux (/etc/alpine-release, apk command)
        2. Ubuntu (/etc/lsb-release contains Ubuntu)
        3. Generic Linux (fallback)
        """
        # Check for Alpine Linux
        if Path("/etc/alpine-release").exists():
            return "alpine"

        if self._command_exists("apk"):
            return "alpine"

        # Check for Ubuntu
        try:
            lsb_release = Path("/etc/lsb-release")
            if lsb_release.exists():
                content = lsb_release.read_text().lower()
                if "ubuntu" in content:
                    return "ubuntu"
        except Exception:
            pass

        # Check os-release for generic distro detection
        try:
            os_release = Path("/etc/os-release")
            if os_release.exists():
                content = os_release.read_text().lower()
                if "alpine" in content:
                    return "alpine"
                elif "ubuntu" in content:
                    return "ubuntu"
        except Exception:
            pass

        return "linux"

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            subprocess.run(
                ["which", command],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            return True
        except Exception:
            return False

    def _detect_capabilities(self) -> Dict[str, bool]:
        """
        Detect OS-specific capabilities.

        Returns:
            Dict of capability flags
        """
        caps = {
            # Disk/filesystem operations
            "format_ext4": self._platform in ("alpine", "ubuntu", "linux"),
            "format_apfs": self._platform == "macos",
            "format_ntfs": self._platform == "windows",
            # Package management
            "apk": self._platform == "alpine",
            "apt": self._platform == "ubuntu",
            "brew": self._platform == "macos",
            "choco": self._platform == "windows",
            # System operations
            "systemctl": self._platform in ("ubuntu", "linux"),
            "openrc": self._platform == "alpine",
            "launchctl": self._platform == "macos",
            "services_msc": self._platform == "windows",
            # Virtualization
            "kvm": self._platform in ("alpine", "ubuntu", "linux"),
            "hypervisor": self._platform == "macos",
            "hyper_v": self._platform == "windows",
            # Container runtime
            "docker": self._command_exists("docker"),
            "podman": self._command_exists("podman"),
            # Network tools
            "iptables": self._platform in ("alpine", "ubuntu", "linux"),
            "pf": self._platform == "macos",
            "windows_firewall": self._platform == "windows",
        }

        return caps

    # Platform detection methods

    def get_platform(self) -> str:
        """Get detected platform name."""
        return self._platform

    def is_alpine(self) -> bool:
        """Check if running on Alpine Linux."""
        return self._platform == "alpine"

    def is_macos(self) -> bool:
        """Check if running on macOS."""
        return self._platform == "macos"

    def is_ubuntu(self) -> bool:
        """Check if running on Ubuntu."""
        return self._platform == "ubuntu"

    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return self._platform == "windows"

    def is_linux(self) -> bool:
        """Check if running on any Linux variant."""
        return self._platform in ("alpine", "ubuntu", "linux")

    # Capability checking

    def has_capability(self, capability: str) -> bool:
        """
        Check if OS has specific capability.

        Args:
            capability: Capability name (e.g., 'format_ext4', 'apk', 'docker')

        Returns:
            True if capability available
        """
        return self._capabilities.get(capability, False)

    def can_format_disk(self, filesystem: str) -> bool:
        """
        Check if OS can format disks with given filesystem.

        Args:
            filesystem: 'ext4', 'apfs', 'ntfs', etc.

        Returns:
            True if formatting supported
        """
        capability_map = {
            "ext4": "format_ext4",
            "ext3": "format_ext4",
            "ext2": "format_ext4",
            "apfs": "format_apfs",
            "ntfs": "format_ntfs",
            "fat32": True,  # Most platforms support FAT32
            "exfat": True,  # Most platforms support exFAT
        }

        cap_name = capability_map.get(filesystem.lower())
        if cap_name is True:
            return True
        elif cap_name:
            return self.has_capability(cap_name)
        else:
            return False

    def get_package_manager(self) -> Optional[str]:
        """
        Get primary package manager for current OS.

        Returns:
            'apk', 'apt', 'brew', 'choco', or None
        """
        if self.has_capability("apk"):
            return "apk"
        elif self.has_capability("apt"):
            return "apt"
        elif self.has_capability("brew"):
            return "brew"
        elif self.has_capability("choco"):
            return "choco"
        return None

    # OS constraint warnings

    def warn_os_constraint(self, command: str, required_platforms: List[str]) -> str:
        """
        Generate warning message for OS-constrained commands.

        Args:
            command: Command name (e.g., "DISK FORMAT")
            required_platforms: List of supported platforms

        Returns:
            Warning message string
        """
        current = self.get_platform()
        required_str = ", ".join(required_platforms)

        return (
            f"WARN {command} is not supported on {current}.\n"
            f"   Supported platforms: {required_str}\n"
            f"   Consider running this command on a supported system."
        )

    def suggest_alternative(self, command: str) -> Optional[str]:
        """
        Suggest OS-specific alternative for a command.

        Args:
            command: Command that failed

        Returns:
            Suggestion string or None
        """
        alternatives = {
            # Disk formatting
            (
                "format_disk",
                "macos",
            ): "Use Disk Utility or: diskutil eraseDisk APFS <name> <device>",
            ("format_disk", "ubuntu"): "Use: sudo mkfs.ext4 /dev/<device>",
            ("format_disk", "alpine"): "Use: sudo mkfs.ext4 /dev/<device>",
            ("format_disk", "windows"): "Use Disk Management or: format <drive>:",
            # Package management
            ("install_package", "macos"): "Use Homebrew: brew install <package>",
            ("install_package", "ubuntu"): "Use APT: sudo apt install <package>",
            ("install_package", "alpine"): "Use APK: sudo apk add <package>",
            ("install_package", "windows"): "Use Chocolatey: choco install <package>",
        }

        key = (command, self._platform)
        return alternatives.get(key)

    # Platform information

    def get_platform_info(self) -> Dict[str, str]:
        """
        Get comprehensive platform information.

        Returns:
            Dict with system details
        """
        info = {
            "platform": self._platform,
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        }

        # Add Linux-specific info
        if self.is_linux():
            try:
                if Path("/etc/alpine-release").exists():
                    info["alpine_version"] = (
                        Path("/etc/alpine-release").read_text().strip()
                    )
            except Exception:
                pass

        # Add macOS-specific info
        if self.is_macos():
            info["macos_version"] = platform.mac_ver()[0]

        return info

    def get_capabilities_report(self) -> str:
        """
        Generate human-readable capabilities report.

        Returns:
            Formatted capabilities string
        """
        lines = [
            f"Platform: {self._platform}",
            f"System: {platform.system()} {platform.release()}",
            "",
            "Capabilities:",
        ]

        # Group capabilities by category
        categories = {
            "Package Management": ["apk", "apt", "brew", "choco"],
            "Filesystem": ["format_ext4", "format_apfs", "format_ntfs"],
            "System Services": ["systemctl", "openrc", "launchctl", "services_msc"],
            "Containers": ["docker", "podman"],
        }

        for category, caps in categories.items():
            lines.append(f"\n{category}:")
            for cap in caps:
                status = "OK" if self.has_capability(cap) else "X"
                lines.append(f"  {status} {cap}")

        return "\n".join(lines)


# Singleton accessor
def get_os_detector() -> OSDetector:
    """
    Get OSDetector singleton instance.

    Respects UDOS_PLATFORM overrides across test runs.
    """
    override = os.environ.get("UDOS_PLATFORM", "").lower()
    if OSDetector._instance is None:
        return OSDetector()
    if override and override != OSDetector._instance.get_platform():
        OSDetector._instance = None
        return OSDetector()
    return OSDetector._instance


# Convenience functions for handlers


def is_alpine() -> bool:
    """Check if running on Alpine Linux."""
    return get_os_detector().is_alpine()


def is_macos() -> bool:
    """Check if running on macOS."""
    return get_os_detector().is_macos()


def is_ubuntu() -> bool:
    """Check if running on Ubuntu."""
    return get_os_detector().is_ubuntu()


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_os_detector().is_windows()


def is_linux() -> bool:
    """Check if running on any Linux variant."""
    return get_os_detector().is_linux()


def get_platform() -> str:
    """Get current platform name."""
    return get_os_detector().get_platform()


# Example usage
if __name__ == "__main__":
    detector = get_os_detector()
    print(detector.get_capabilities_report())
    print("\n" + "=" * 50 + "\n")
    print("Platform Info:")
    for key, value in detector.get_platform_info().items():
        print(f"  {key}: {value}")
