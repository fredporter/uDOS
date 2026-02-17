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
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass

from wizard.services.plugin_factory import APKBuilder, BuildResult
from wizard.services.system_info_service import LibraryStatus, LibraryIntegration


@dataclass
class InstallStep:
    """A single step in an install pipeline."""

    n: int           # Step number (1-based)
    total: int       # Total steps in pipeline
    name: str        # Short label e.g. "setup", "apk_build", "pkg_install"
    ok: bool
    detail: str = ""


@dataclass
class InstallResult:
    """Result of plugin installation."""

    success: bool
    plugin_name: str
    action: str  # "installed", "updated", "enabled", "disabled"
    message: str = ""
    error: str = ""
    steps: Any = None  # List[InstallStep] — populated by install pipeline


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

    def _resolve_manifest_path(self, integration: LibraryIntegration) -> Optional[Path]:
        integration_path = Path(integration.path)
        container_path = integration_path / "container.json"
        if container_path.exists():
            return container_path
        definition_path = self.library_root / integration.name / "container.json"
        if definition_path.exists():
            return definition_path
        return None

    def _load_integration_manifest(self, integration: LibraryIntegration) -> Dict[str, Any]:
        manifest_path = self._resolve_manifest_path(integration)
        if not manifest_path:
            return {}
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def get_integration_versions(self, name: str) -> Dict[str, Any]:
        integration = self.get_integration(name)
        if not integration:
            return {"integration": name, "found": False, "current_version": None, "available_versions": []}

        manifest = self._load_integration_manifest(integration)
        container = manifest.get("container", {}) if isinstance(manifest, dict) else {}
        current = container.get("version") or integration.version or "latest"
        available: List[str] = []

        raw_candidates = []
        for key in ("versions", "releases"):
            value = manifest.get(key)
            if isinstance(value, list):
                raw_candidates.extend(value)
        container_versions = container.get("versions")
        if isinstance(container_versions, list):
            raw_candidates.extend(container_versions)

        for item in raw_candidates:
            if isinstance(item, str):
                available.append(item)
            elif isinstance(item, dict):
                version = item.get("version")
                if version:
                    available.append(str(version))

        repo_path = self.repo_root / "library" / "containers" / name
        git_dir = repo_path / ".git"
        if git_dir.exists():
            try:
                tags = subprocess.run(
                    ["git", "tag", "--list"],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=8,
                )
                if tags.returncode == 0:
                    available.extend([line.strip() for line in tags.stdout.splitlines() if line.strip()])
            except Exception:
                pass

        deduped: List[str] = []
        seen = set()
        for version in [str(current), *available]:
            if version not in seen:
                seen.add(version)
                deduped.append(version)

        return {
            "integration": integration.name,
            "found": True,
            "current_version": str(current),
            "available_versions": deduped,
        }

    def _extract_integration_dependencies(self, manifest: Dict[str, Any]) -> List[str]:
        deps: List[str] = []
        if not isinstance(manifest, dict):
            return deps

        candidates = [
            manifest.get("dependencies"),
            manifest.get("requires"),
            (manifest.get("integration") or {}).get("depends_on"),
            (manifest.get("integration") or {}).get("dependencies"),
        ]
        for candidate in candidates:
            if isinstance(candidate, list):
                for item in candidate:
                    if isinstance(item, str) and item:
                        deps.append(item)
            elif isinstance(candidate, dict):
                for key in ("integrations", "integration", "plugins"):
                    values = candidate.get(key)
                    if isinstance(values, list):
                        for item in values:
                            if isinstance(item, str) and item:
                                deps.append(item)
                    elif isinstance(values, str) and values:
                        deps.append(values)

        cleaned = []
        seen = set()
        for dep in deps:
            dep_name = dep.strip()
            if dep_name and dep_name not in seen:
                seen.add(dep_name)
                cleaned.append(dep_name)
        return cleaned

    def _extract_package_dependencies(self, manifest: Dict[str, Any]) -> Dict[str, List[str]]:
        def _as_list(value: Any) -> List[str]:
            if isinstance(value, list):
                return [str(item) for item in value if item]
            return []

        system_requirements = manifest.get("system_requirements", {}) if isinstance(manifest, dict) else {}
        return {
            "apk_dependencies": _as_list(manifest.get("apk_dependencies")),
            "brew_dependencies": _as_list(manifest.get("brew_dependencies")),
            "apt_dependencies": _as_list(manifest.get("apt_dependencies")),
            "pip_dependencies": _as_list(manifest.get("pip_dependencies")),
            "system_dependencies": _as_list(system_requirements.get("dependencies")) if isinstance(system_requirements, dict) else [],
        }

    def resolve_integration_dependencies(self, name: str) -> Dict[str, Any]:
        integration = self.get_integration(name)
        if not integration:
            return {
                "integration": name,
                "found": False,
                "direct_integrations": [],
                "install_order": [],
                "missing_integrations": [],
                "package_dependencies": {},
            }

        status = self.get_library_status()
        available_names = {item.name for item in status.integrations}
        manifest = self._load_integration_manifest(integration)
        direct = self._extract_integration_dependencies(manifest)
        package_dependencies = self._extract_package_dependencies(manifest)

        missing = sorted([dep for dep in direct if dep not in available_names and dep != name])
        visited: Set[str] = set()
        visiting: Set[str] = set()
        order: List[str] = []
        cycle_detected = False

        def _visit(dep_name: str) -> None:
            nonlocal cycle_detected
            if dep_name in visited or dep_name == name:
                return
            if dep_name in visiting:
                cycle_detected = True
                return
            dep_integration = self.get_integration(dep_name)
            if not dep_integration:
                return
            visiting.add(dep_name)
            dep_manifest = self._load_integration_manifest(dep_integration)
            for nested in self._extract_integration_dependencies(dep_manifest):
                if nested in available_names:
                    _visit(nested)
            visiting.remove(dep_name)
            visited.add(dep_name)
            order.append(dep_name)

        for dep in direct:
            if dep in available_names:
                _visit(dep)

        return {
            "integration": integration.name,
            "found": True,
            "direct_integrations": direct,
            "install_order": order,
            "missing_integrations": missing,
            "cycle_detected": cycle_detected,
            "package_dependencies": package_dependencies,
        }

    def install_integration(self, name: str) -> InstallResult:
        return self._install_integration_internal(name, set())

    def _install_integration_internal(self, name: str, installing: Set[str]) -> InstallResult:
        """
        Install an integration from /library or /dev/library.

        Steps:
        1. Find integration container.json
        2. Run setup.sh if present
        3. Build APK package if APKBUILD exists
        4. Install via package manager (apk, brew, apt)
        """
        if name in installing:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="install",
                error="Dependency cycle detected during install",
            )

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

        dependency_resolution = self.resolve_integration_dependencies(name)
        missing = dependency_resolution.get("missing_integrations", [])
        if missing:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="install",
                error=f"Missing integration dependencies: {', '.join(missing)}",
            )

        # Determine total steps: deps + setup + (apk_build?) + pkg_install
        dep_order = dependency_resolution.get("install_order", [])
        integration_path_tmp = Path(integration.path)
        apkbuild_exists = (integration_path_tmp / "APKBUILD").exists()
        total_steps = len(dep_order) + 1 + (1 if apkbuild_exists else 0) + 1
        steps: List[InstallStep] = []

        try:
            installing.add(name)

            # Install dependencies first
            for i, dep in enumerate(dep_order, start=1):
                dep_integration = self.get_integration(dep)
                if dep_integration and not dep_integration.installed:
                    dep_result = self._install_integration_internal(dep, installing)
                    steps.append(InstallStep(n=i, total=total_steps, name=f"dep:{dep}", ok=dep_result.success, detail=dep_result.message or dep_result.error))
                    if not dep_result.success:
                        return InstallResult(
                            success=False,
                            plugin_name=name,
                            action="install",
                            error=f"Dependency install failed ({dep}): {dep_result.error or dep_result.message}",
                            steps=steps,
                        )
                else:
                    steps.append(InstallStep(n=i, total=total_steps, name=f"dep:{dep}", ok=True, detail="already installed"))

            step_n = len(dep_order) + 1

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

            # Recompute totals now that we know the real integration_path
            apkbuild_path = integration_path / "APKBUILD"
            if apkbuild_path.exists() and not apkbuild_exists:
                total_steps += 1
            for s in steps:
                s.total = total_steps

            # Step: run setup script
            setup_result = self._run_setup_script(integration_path)
            steps.append(InstallStep(n=step_n, total=total_steps, name="setup", ok=setup_result[0], detail=setup_result[1]))
            step_n += 1
            if not setup_result[0]:
                return InstallResult(
                    success=False,
                    plugin_name=name,
                    action="install",
                    error=f"Setup failed: {setup_result[1]}",
                    steps=steps,
                )

            # Step: build APK if APKBUILD exists
            if apkbuild_path.exists():
                build_result = self.apk_builder.build_apk(
                    name, container_path=integration_path
                )
                steps.append(InstallStep(n=step_n, total=total_steps, name="apk_build", ok=build_result.success, detail=build_result.error or "ok"))
                step_n += 1
                if not build_result.success:
                    return InstallResult(
                        success=False,
                        plugin_name=name,
                        action="install",
                        error=f"APK build failed: {build_result.error}",
                        steps=steps,
                    )

            # Step: install via package manager
            package_result = self._install_via_package_manager(name, integration_path)
            steps.append(InstallStep(n=step_n, total=total_steps, name="pkg_install", ok=package_result[0], detail=package_result[1]))
            if not package_result[0]:
                return InstallResult(
                    success=False,
                    plugin_name=name,
                    action="install",
                    error=f"Package install failed: {package_result[1]}",
                    steps=steps,
                )

            return InstallResult(
                success=True,
                plugin_name=name,
                action="installed",
                message=f"Installation successful ({len(steps)}/{total_steps} steps)",
                steps=steps,
            )

        except Exception as e:
            return InstallResult(
                success=False,
                plugin_name=name,
                action="install",
                error=f"Install failed: {str(e)}",
                steps=steps,
            )
        finally:
            installing.discard(name)

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
