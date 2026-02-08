"""
Library Management Service - Migrate from Goblin to Wizard

Provides library/plugin management capabilities:
- Scanning /library and /dev/library for integrations
- Installing/activating plugins via APK packages
- Managing enabled integrations
- Building and distributing packages
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from wizard.services.plugin_factory import APKBuilder, BuildResult
from wizard.services.system_info_service import LibraryStatus, LibraryIntegration


@dataclass
class InstallResult:
    """Result of plugin installation."""

    success: bool
    plugin_name: str
    action: str  # "installed", "updated", "enabled", "disabled"
    message: str = ""
    error: str = ""


class LibraryManagerService:
    """
    Manages library integrations and plugin installation.

    Migrated from Goblin to Wizard for centralized management.
    """

    def __init__(self, repo_root: Path):
        """Initialize library manager."""
        self.repo_root = repo_root
        self.library_root = repo_root / "library"
        self.dev_library_root = repo_root / "dev" / "library"
        self.enabled_config_path = repo_root / "memory" / "wizard" / "plugins.enabled"
        self.apk_builder = APKBuilder()

        # Ensure directories exist
        self.library_root.mkdir(parents=True, exist_ok=True)
        self.enabled_config_path.parent.mkdir(parents=True, exist_ok=True)

    def get_library_status(self) -> LibraryStatus:
        """Get comprehensive library status."""
        from wizard.services.system_info_service import get_system_info_service

        return get_system_info_service(self.repo_root).get_library_status()

    def get_dependency_inventory(self) -> Dict[str, Any]:
        """Collect dependency inventory from container.json manifests."""
        status = self.get_library_status()
        inventory: Dict[str, Any] = {}
        for integration in status.integrations:
            try:
                container_path = Path(integration.path) / "container.json"
                if not container_path.exists():
                    # Fallback to definition in /library/<name>/container.json
                    definition_path = self.library_root / integration.name / "container.json"
                    if definition_path.exists():
                        container_path = definition_path
                if not container_path.exists():
                    continue
                manifest = json.loads(container_path.read_text())
                deps = {
                    "apk_dependencies": manifest.get("apk_dependencies", []),
                    "brew_dependencies": manifest.get("brew_dependencies", []),
                    "apt_dependencies": manifest.get("apt_dependencies", []),
                    "pip_dependencies": manifest.get("pip_dependencies", []),
                    "python_version": manifest.get("python_version", ""),
                }
                inventory[integration.name] = {
                    "path": integration.path,
                    "source": integration.source,
                    "deps": deps,
                }
            except Exception:
                continue
        return inventory

    def update_alpine_toolchain(
        self, packages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update Alpine toolchain packages (python3, pip, etc.)."""
        from wizard.services.system_info_service import get_system_info_service

        os_info = get_system_info_service(self.repo_root).get_os_info()
        if not os_info.is_alpine:
            return {
                "success": False,
                "message": "Toolchain updates only supported on Alpine",
            }

        pkg_list = packages or [
            "python3",
            "py3-pip",
            "py3-setuptools",
            "py3-wheel",
            "py3-virtualenv",
        ]

        try:
            update = subprocess.run(
                ["apk", "update"], capture_output=True, text=True, timeout=120
            )
            if update.returncode != 0:
                return {
                    "success": False,
                    "message": f"apk update failed: {update.stderr.strip()}",
                }

            cmd = ["apk", "add", "--upgrade", "--no-cache"] + pkg_list
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": f"apk add --upgrade failed: {result.stderr.strip()}",
                }

            return {
                "success": True,
                "message": "Toolchain updated",
                "packages": pkg_list,
            }
        except Exception as e:
            return {"success": False, "message": f"Toolchain update error: {str(e)}"}

    def get_integration(self, name: str) -> Optional[LibraryIntegration]:
        """Get specific integration by name."""
        status = self.get_library_status()
        return next((i for i in status.integrations if i.name == name), None)

    def install_integration(self, name: str) -> InstallResult:
        """
        Install an integration from /library or /dev/library.

        Steps:
        1. Find integration container.json
        2. Run setup.sh if present
        3. Build APK package if APKBUILD exists
        4. Install via package manager (apk, brew, apt)
        """
        integration = self.get_integration(name)
        if not integration:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="install",
                error=f"Integration not found: {name}",
            )

        if integration.installed:
            return InstallResult(
                success=True,
                plugin_name=name,
                action="install",
                message="Already installed",
            )

        try:
            integration_path = Path(integration.path)
            container_path = integration_path / "container.json"
            if not container_path.exists():
                definition_path = self.library_root / name / "container.json"
                if definition_path.exists():
                    manifest = json.loads(definition_path.read_text())
                    repo_path = manifest.get("repo_path")
                    if repo_path:
                        candidate = Path(repo_path)
                        if not candidate.is_absolute():
                            candidate = self.repo_root / candidate
                        integration_path = candidate
                        container_path = definition_path

            # 1. Run setup script if present
            setup_result = self._run_setup_script(integration_path)
            if not setup_result[0]:
                return InstallResult(
                    success=False,
                    plugin_name=name,
                    action="install",
                    error=f"Setup failed: {setup_result[1]}",
                )

            # 2. Build APK if APKBUILD exists
            apkbuild_path = integration_path / "APKBUILD"
            if apkbuild_path.exists():
                build_result = self.apk_builder.build_apk(
                    name, container_path=integration_path
                )
                if not build_result.success:
                    return InstallResult(
                        success=False,
                        plugin_name=name,
                        action="install",
                        error=f"APK build failed: {build_result.error}",
                    )

            # 3. Install via package manager
            package_result = self._install_via_package_manager(name, integration_path)
            if not package_result[0]:
                return InstallResult(
                    success=False,
                    plugin_name=name,
                    action="install",
                    error=f"Package install failed: {package_result[1]}",
                )

            return InstallResult(
                success=True,
                plugin_name=name,
                action="installed",
                message="Installation successful",
            )

        except Exception as e:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="install",
                error=f"Install failed: {str(e)}",
            )

    def enable_integration(self, name: str) -> InstallResult:
        """
        Enable an installed integration.

        Adds to plugins.enabled config file.
        """
        integration = self.get_integration(name)
        if not integration:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="enable",
                error=f"Integration not found: {name}",
            )

        if not integration.installed:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="enable",
                error="Must install integration before enabling",
            )

        if integration.enabled:
            return InstallResult(
                success=True,
                plugin_name=name,
                action="enable",
                message="Already enabled",
            )

        # Add to enabled plugins config
        enabled_plugins = self._load_enabled_plugins()
        if name not in enabled_plugins:
            enabled_plugins.add(name)
            self._save_enabled_plugins(enabled_plugins)

        return InstallResult(
            success=True,
            plugin_name=name,
            action="enabled",
            message="Integration enabled",
        )

    def disable_integration(self, name: str) -> InstallResult:
        """
        Disable an integration.

        Removes from plugins.enabled config file.
        """
        integration = self.get_integration(name)
        if not integration:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="disable",
                error=f"Integration not found: {name}",
            )

        if not integration.enabled:
            return InstallResult(
                success=True,
                plugin_name=name,
                action="disable",
                message="Already disabled",
            )

        # Remove from enabled plugins config
        enabled_plugins = self._load_enabled_plugins()
        enabled_plugins.discard(name)
        self._save_enabled_plugins(enabled_plugins)

        return InstallResult(
            success=True,
            plugin_name=name,
            action="disabled",
            message="Integration disabled",
        )

    def uninstall_integration(self, name: str) -> InstallResult:
        """
        Uninstall an integration.

        1. Disable if enabled
        2. Remove via package manager
        3. Clean up build artifacts
        """
        integration = self.get_integration(name)
        if not integration:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="uninstall",
                error=f"Integration not found: {name}",
            )

        if not integration.installed:
            return InstallResult(
                success=True,
                plugin_name=name,
                action="uninstall",
                message="Not installed",
            )

        try:
            # 1. Disable if enabled
            if integration.enabled:
                disable_result = self.disable_integration(name)
                if not disable_result.success:
                    return InstallResult(
                        success=False,
                        plugin_name=name,
                        action="uninstall",
                        error=f"Failed to disable: {disable_result.error}",
                    )

            # 2. Uninstall via package manager
            uninstall_result = self._uninstall_via_package_manager(name)
            if not uninstall_result[0]:
                return InstallResult(
                    success=False,
                    plugin_name=name,
                    action="uninstall",
                    error=f"Package removal failed: {uninstall_result[1]}",
                )

            # 3. Clean up build artifacts
            integration_path = Path(integration.path)
            build_dir = integration_path / "build"
            if build_dir.exists():
                import shutil

                shutil.rmtree(build_dir)

            return InstallResult(
                success=True,
                plugin_name=name,
                action="uninstalled",
                message="Uninstallation successful",
            )

        except Exception as e:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="uninstall",
                error=f"Uninstall failed: {str(e)}",
            )

    def _run_setup_script(self, integration_path: Path) -> Tuple[bool, str]:
        """Run setup.sh script if present."""
        setup_script = integration_path / "setup.sh"
        if not setup_script.exists():
            return True, "No setup script"

        try:
            # Make executable
            os.chmod(setup_script, 0o755)

            # Run script
            result = subprocess.run(
                [str(setup_script)],
                cwd=str(integration_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                return False, f"Setup script failed: {result.stderr}"

            return True, "Setup completed"

        except subprocess.TimeoutExpired:
            return False, "Setup script timeout"
        except Exception as e:
            return False, f"Setup script error: {str(e)}"

    def _install_via_package_manager(
        self, name: str, integration_path: Path
    ) -> Tuple[bool, str]:
        """Install integration via system package manager."""
        from wizard.services.system_info_service import get_system_info_service

        os_info = get_system_info_service(self.repo_root).get_os_info()

        # Load container.json for package info
        try:
            container_json = integration_path / "container.json"
            if container_json.exists():
                with open(container_json) as f:
                    manifest = json.load(f)
            else:
                manifest = {}
        except Exception:
            manifest = {}

        # Get package dependencies from manifest
        if os_info.is_alpine:
            packages = manifest.get("apk_dependencies", [])
            if packages:
                return self._install_apk_packages(packages)
        elif os_info.is_macos:
            packages = manifest.get("brew_dependencies", [])
            if packages:
                return self._install_brew_packages(packages)
        elif os_info.is_ubuntu:
            packages = manifest.get("apt_dependencies", [])
            if packages:
                return self._install_apt_packages(packages)

        # No packages to install
        return True, "No package dependencies"

    def _install_apk_packages(self, packages: List[str]) -> Tuple[bool, str]:
        """Install APK packages on Alpine."""
        try:
            if shutil.which("apk") is None:
                return False, "apk not found. This installer requires Alpine APK tools."
            cmd = ["apk", "add"] + packages
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                return False, f"apk add failed: {result.stderr}"

            return True, f"Installed APK packages: {', '.join(packages)}"
        except Exception as e:
            return False, f"APK install error: {str(e)}"

    def _install_brew_packages(self, packages: List[str]) -> Tuple[bool, str]:
        """Install Homebrew packages on macOS."""
        try:
            if shutil.which("brew") is None:
                return False, "Homebrew not found. Install Homebrew or use a supported package manager."
            cmd = ["brew", "install"] + packages
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                return False, f"brew install failed: {result.stderr}"

            return True, f"Installed Homebrew packages: {', '.join(packages)}"
        except Exception as e:
            return False, f"Homebrew install error: {str(e)}"

    def _install_apt_packages(self, packages: List[str]) -> Tuple[bool, str]:
        """Install APT packages on Ubuntu."""
        try:
            if shutil.which("apt") is None and shutil.which("apt-get") is None:
                return False, "apt not found. This installer requires APT on Ubuntu/Debian."
            # Update package list first
            update_cmd = ["apt", "update"] if shutil.which("apt") else ["apt-get", "update"]
            subprocess.run(update_cmd, capture_output=True, timeout=60)

            install_cmd = ["apt", "install", "-y"] if shutil.which("apt") else ["apt-get", "install", "-y"]
            cmd = install_cmd + packages
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                return False, f"apt install failed: {result.stderr}"

            return True, f"Installed APT packages: {', '.join(packages)}"
        except Exception as e:
            return False, f"APT install error: {str(e)}"

    def _uninstall_via_package_manager(self, name: str) -> Tuple[bool, str]:
        """Uninstall packages via system package manager."""
        # STUB: package removal
        # This requires tracking which packages were installed for each integration
        return True, "Package removal not yet implemented"

    def _load_enabled_plugins(self) -> set:
        """Load enabled plugins from config file."""
        enabled = set()
        if self.enabled_config_path.exists():
            try:
                with open(self.enabled_config_path) as f:
                    enabled.update(line.strip() for line in f if line.strip())
            except Exception:
                pass
        return enabled

    def _save_enabled_plugins(self, enabled: set):
        """Save enabled plugins to config file."""
        with open(self.enabled_config_path, "w") as f:
            for plugin in sorted(enabled):
                f.write(f"{plugin}\n")


def get_library_manager(repo_root: Optional[Path] = None) -> LibraryManagerService:
    """Get singleton instance of LibraryManagerService."""
    if repo_root is None:
        from wizard.services.path_utils import get_repo_root

        repo_root = get_repo_root()

    return LibraryManagerService(repo_root)
