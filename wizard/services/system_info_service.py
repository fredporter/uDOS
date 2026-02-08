"""
System Information Service - OS Detection and System Stats

Provides OS detection, library management, and system monitoring capabilities
for the Wizard dashboard.
"""

import os
import json
import platform
import psutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class OSInfo:
    """OS detection information."""

    detected_os: str  # "alpine", "macos", "ubuntu", "windows"
    platform_system: str  # Result of platform.system()
    platform_release: str  # OS release
    platform_version: str  # OS version
    python_version: str
    is_alpine: bool
    is_macos: bool
    is_ubuntu: bool
    is_windows: bool
    is_linux: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LibraryIntegration:
    """Single library integration status."""

    name: str  # "ollama", "mistral-vibe", "meshcore", etc.
    path: str  # Path in /library or /dev/library
    source: str  # "library" or "dev_library"
    enabled: bool  # If activated
    installed: bool  # If package is installed
    has_container: bool  # If container.json exists
    can_install: bool  # If can be installed (has container.json)
    description: str = ""
    version: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LibraryStatus:
    """Overall library status."""

    library_root: str  # Path to /library
    dev_library_root: str  # Path to /dev/library
    total_integrations: int
    installed_count: int  # Installed but maybe not enabled
    enabled_count: int  # Actively enabled
    integrations: List[LibraryIntegration]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["integrations"] = [i.to_dict() for i in self.integrations]
        return data


class SystemInfoService:
    """Provides system information, OS detection, and library management."""

    def __init__(self, repo_root: Path):
        """Initialize system info service."""
        self.repo_root = repo_root
        self.library_root = repo_root / "library"
        self.dev_library_root = repo_root / "dev" / "library"
        self._os_info_cache = None

    def get_os_info(self) -> OSInfo:
        """
        Detect OS and return detailed platform information.
        Uses the same detection as core/services/os_detector.py
        """
        if self._os_info_cache:
            return self._os_info_cache

        # Detect which OS
        detected_os = self._detect_os()
        is_alpine = detected_os == "alpine"
        is_macos = detected_os == "macos"
        is_ubuntu = detected_os == "ubuntu"
        is_windows = detected_os == "windows"
        is_linux = detected_os in ["alpine", "ubuntu"]

        info = OSInfo(
            detected_os=detected_os,
            platform_system=platform.system(),
            platform_release=platform.release(),
            platform_version=platform.version(),
            python_version=platform.python_version(),
            is_alpine=is_alpine,
            is_macos=is_macos,
            is_ubuntu=is_ubuntu,
            is_windows=is_windows,
            is_linux=is_linux,
        )

        self._os_info_cache = info
        return info

    def _detect_os(self) -> str:
        """
        Detect OS using same logic as core/services/os_detector.py.

        Returns: "alpine", "macos", "ubuntu", or "windows"
        """
        # Check for Alpine (priority)
        alpine_release = Path("/etc/alpine-release")
        if alpine_release.exists():
            return "alpine"

        # Check for apk command (Alpine on non-standard paths)
        try:
            import shutil

            if shutil.which("apk"):
                return "alpine"
        except Exception:
            pass

        # Check /etc/os-release for alpine (fallback)
        os_release = Path("/etc/os-release")
        if os_release.exists():
            try:
                with open(os_release) as f:
                    content = f.read()
                    if "ID=alpine" in content or "ID='alpine'" in content:
                        return "alpine"
                    elif "ID=ubuntu" in content or "ID='ubuntu'" in content:
                        return "ubuntu"
            except Exception:
                pass

        # Fallback to platform.system()
        system = platform.system()
        if system == "Darwin":
            return "macos"
        elif system == "Linux":
            return "ubuntu"  # Assume Ubuntu if not Alpine
        elif system == "Windows":
            return "windows"

        return "unknown"

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get current system resource statistics.
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            uptime_seconds = None
            if Path("/proc/uptime").exists():
                uptime_seconds = int((Path("/proc/uptime").read_text().split()[0]))
            else:
                uptime_seconds = int(time.time() - psutil.boot_time())
            boot_time = psutil.boot_time()
        except Exception:
            uptime_seconds = 0
            cpu_percent = 0
            memory = None
            disk = None
            boot_time = 0

        return {
            "timestamp": time.time(),
            "cpu": {
                "percent": cpu_percent,
                "count": os.cpu_count() or 1,
            },
            "memory": {
                "percent": memory.percent if memory else 0,
                "available_mb": (memory.available / (1024**2)) if memory else 0,
                "total_mb": (memory.total / (1024**2)) if memory else 0,
            },
            "disk": {
                "percent": disk.percent if disk else 0,
                "free_mb": (disk.free / (1024**2)) if disk else 0,
                "total_mb": (disk.total / (1024**2)) if disk else 0,
            },
            "uptime": {
                "seconds": uptime_seconds,
                "boot_time": boot_time,
            },
            "os": self.get_os_info().to_dict(),
        }

    def get_library_status(self) -> LibraryStatus:
        """
        Scan /library and /dev/library directories for available integrations.

        Returns status of which are installed, enabled, etc.
        """
        integrations: List[LibraryIntegration] = []

        # Scan public library
        if self.library_root.exists():
            for item_path in self.library_root.iterdir():
                if item_path.is_dir() and not item_path.name.startswith("."):
                    integration = self._scan_library_item(item_path, source="library")
                    if integration:
                        integrations.append(integration)

        # Scan dev library (private)
        if self.dev_library_root.exists():
            for item_path in self.dev_library_root.iterdir():
                if item_path.is_dir() and not item_path.name.startswith("."):
                    # Check if already added from public library
                    if not any(i.name == item_path.name for i in integrations):
                        integration = self._scan_library_item(
                            item_path, source="dev_library"
                        )
                        if integration:
                            integrations.append(integration)

        # Determine enabled integrations
        # Check for /etc/udos/plugins.enabled (Alpine) or config
        enabled_names = self._get_enabled_integrations()
        for integration in integrations:
            integration.enabled = integration.name in enabled_names

        total = len(integrations)
        installed = sum(1 for i in integrations if i.installed)
        enabled = sum(1 for i in integrations if i.enabled)

        return LibraryStatus(
            library_root=str(self.library_root),
            dev_library_root=str(self.dev_library_root),
            total_integrations=total,
            installed_count=installed,
            enabled_count=enabled,
            integrations=sorted(integrations, key=lambda x: x.name),
        )

    def _scan_library_item(
        self, item_path: Path, source: str = "library"
    ) -> Optional[LibraryIntegration]:
        """
        Scan a single library item directory.

        Returns LibraryIntegration or None if not a valid directory.
        """
        container_json = item_path / "container.json"
        has_container = container_json.exists()
        repo_path = None

        name = item_path.name
        description = ""
        version = ""

        # Read manifest if exists
        if has_container:
            try:
                with open(container_json) as f:
                    manifest = json.load(f)
                description = manifest.get("container", {}).get("description", "")
                version = manifest.get("container", {}).get("version", "")
                repo_path = manifest.get("repo_path")
            except Exception:
                pass

        # Resolve repo path if manifest points elsewhere
        resolved_path = item_path
        if repo_path:
            candidate = Path(repo_path)
            if not candidate.is_absolute():
                candidate = self.repo_root / candidate
            resolved_path = candidate

        # Check if installed by looking for setup.sh or build output
        installed = self._check_if_installed(resolved_path)

        return LibraryIntegration(
            name=name,
            path=str(resolved_path),
            source=source,
            enabled=False,  # Will be set by get_library_status
            installed=installed,
            has_container=has_container,
            can_install=has_container,  # Can install if has container.json
            description=description,
            version=version,
        )

    def _check_if_installed(self, item_path: Path) -> bool:
        """
        Check if an integration is installed on this system.

        Checks for:
        - setup.sh existence
        - build/ directory with artifacts
        - package manager package name in manifest
        """
        # Check for setup.sh
        setup_sh = item_path / "setup.sh"
        if setup_sh.exists():
            return True

        # Check for build directory with output
        build_dir = item_path / "build"
        if build_dir.exists() and any(build_dir.iterdir()):
            return True

        # STUB: Check package installation via manager
        # (apk list, brew list, apt list, etc.)

        return False

    def _get_enabled_integrations(self) -> set:
        """
        Get list of enabled integrations.

        Checks:
        - /etc/udos/plugins.enabled (Alpine)
        - memory/wizard/plugins.enabled (if set)
        - Config file
        """
        enabled = set()

        # Alpine: /etc/udos/plugins.enabled
        alpine_plugins = Path("/etc/udos/plugins.enabled")
        if alpine_plugins.exists():
            try:
                with open(alpine_plugins) as f:
                    enabled.update(line.strip() for line in f if line.strip())
            except Exception:
                pass

        # Check config if available
        config_path = self.repo_root / "memory" / "wizard" / "plugins.enabled"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    enabled.update(line.strip() for line in f if line.strip())
            except Exception:
                pass

        return enabled


def get_system_info_service(repo_root: Optional[Path] = None) -> SystemInfoService:
    """
    Get singleton instance of SystemInfoService.
    """
    if repo_root is None:
        # Auto-detect repo root
        from wizard.services.path_utils import get_repo_root

        repo_root = get_repo_root()

    return SystemInfoService(repo_root)
