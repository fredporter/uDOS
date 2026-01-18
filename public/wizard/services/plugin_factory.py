"""
Plugin Factory - TCZ Package Builder
====================================

Builds distribution packages from code containers for Tiny Core Linux.

Package Types:
  - TCZ: Tiny Core Extension (squashfs)
  - TAR.GZ: Generic tarball (fallback)

Build Process:
  1. Clone/update container from GitHub
  2. Run any build scripts
  3. Package into TCZ format
  4. Generate manifest and checksums
  5. Upload to plugin repository

Requirements (for TCZ):
  - mksquashfs (squashfs-tools)
  - Tiny Core Linux environment (for testing)
"""

import os
import json
import shutil
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict

# Paths
CONTAINERS_PATH = Path(__file__).parent.parent / "cloned"
PLUGIN_REPO_PATH = Path(__file__).parent.parent.parent / "distribution" / "plugins"
BUILD_TEMP_PATH = Path(__file__).parent.parent.parent / "distribution" / ".build"


@dataclass
class PluginManifest:
    """Plugin package manifest."""

    id: str
    name: str
    version: str
    description: str
    author: str
    license: str
    source: str

    # Build info
    built_at: str
    built_by: str
    commit: Optional[str] = None

    # Package info
    package_type: str = "tar.gz"
    package_size: int = 0
    package_checksum: str = ""

    # Dependencies
    dependencies: List[str] = None
    tce_dependencies: List[str] = None

    # uDOS integration
    wrapper_path: Optional[str] = None
    handler_path: Optional[str] = None
    commands: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tce_dependencies is None:
            self.tce_dependencies = []
        if self.commands is None:
            self.commands = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class BuildResult:
    """Result of a build operation."""

    success: bool
    plugin_id: str
    package_path: Optional[Path] = None
    manifest: Optional[PluginManifest] = None
    error: Optional[str] = None
    build_time_seconds: float = 0


class PluginFactory:
    """
    Factory for building plugin packages.

    Supports:
    - Building from code containers
    - TCZ packaging (Tiny Core)
    - TAR.GZ fallback
    - Manifest generation
    - Checksum calculation
    """

    def __init__(self, logger=None):
        """Initialize plugin factory."""
        self.logger = logger
        self.containers_path = CONTAINERS_PATH
        self.repo_path = PLUGIN_REPO_PATH
        self.build_path = BUILD_TEMP_PATH

        # Ensure directories
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self.build_path.mkdir(parents=True, exist_ok=True)

    def build_plugin(self, container_id: str, version: str = None) -> BuildResult:
        """
        Build a plugin package from a code container.

        Args:
            container_id: ID of the container to build
            version: Version string (auto-detected if not provided)

        Returns:
            BuildResult with package info or error
        """
        import time

        start_time = time.time()

        container_path = self.containers_path / container_id

        if not container_path.exists():
            return BuildResult(
                success=False,
                plugin_id=container_id,
                error=f"Container not found: {container_id}",
            )

        try:
            # Load container manifest
            container_manifest = self._load_container_manifest(container_path)

            # Determine version
            if not version:
                version = self._detect_version(container_path, container_manifest)

            # Create build directory
            build_dir = self.build_path / f"{container_id}-{version}"
            if build_dir.exists():
                shutil.rmtree(build_dir)
            build_dir.mkdir(parents=True)

            # Copy container contents (excluding .git)
            self._copy_container(container_path, build_dir)

            # Run build script if present
            self._run_build_script(build_dir)

            # Try TCZ first, fall back to tar.gz
            package_path, package_type = self._create_package(
                build_dir, container_id, version
            )

            # Calculate checksum
            checksum = self._calculate_checksum(package_path)

            # Create manifest
            manifest = self._create_manifest(
                container_id,
                version,
                container_manifest,
                package_path,
                package_type,
                checksum,
            )

            # Move to repository
            plugin_dir = self.repo_path / container_id
            plugin_dir.mkdir(parents=True, exist_ok=True)

            final_package = plugin_dir / package_path.name
            shutil.move(str(package_path), str(final_package))

            # Save manifest
            manifest_path = plugin_dir / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest.to_dict(), f, indent=2)

            # Cleanup build dir
            shutil.rmtree(build_dir)

            build_time = time.time() - start_time

            if self.logger:
                self.logger.info(
                    f"[PLUGIN] Built {container_id} v{version} in {build_time:.1f}s"
                )

            return BuildResult(
                success=True,
                plugin_id=container_id,
                package_path=final_package,
                manifest=manifest,
                build_time_seconds=build_time,
            )

        except Exception as e:
            return BuildResult(
                success=False,
                plugin_id=container_id,
                error=str(e),
                build_time_seconds=time.time() - start_time,
            )

    def _load_container_manifest(self, container_path: Path) -> Dict[str, Any]:
        """Load container.json manifest."""
        manifest_path = container_path / "container.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                return json.load(f)
        return {}

    def _detect_version(self, container_path: Path, manifest: Dict[str, Any]) -> str:
        """Detect version from container."""
        # Try container manifest
        if "container" in manifest:
            if manifest["container"].get("version"):
                return manifest["container"]["version"]
            if manifest["container"].get("commit"):
                return manifest["container"]["commit"][:8]

        # Try git
        if (container_path / ".git").exists():
            try:
                result = subprocess.run(
                    [
                        "git",
                        "-C",
                        str(container_path),
                        "describe",
                        "--tags",
                        "--always",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass

        # Fallback to date
        return datetime.utcnow().strftime("%Y%m%d")

    def _copy_container(self, src: Path, dst: Path):
        """Copy container contents, excluding .git."""
        for item in src.iterdir():
            if item.name == ".git":
                continue
            if item.is_dir():
                shutil.copytree(item, dst / item.name)
            else:
                shutil.copy2(item, dst / item.name)

    def _run_build_script(self, build_dir: Path):
        """Run build script if present."""
        # Check for common build scripts
        scripts = ["build.sh", "setup.py", "Makefile"]
        for script in scripts:
            script_path = build_dir / script
            if script_path.exists():
                if self.logger:
                    self.logger.info(f"[PLUGIN] Running {script}")
                # TODO: Execute build script safely
                break

    def _create_package(
        self, build_dir: Path, plugin_id: str, version: str
    ) -> Tuple[Path, str]:
        """Create package file (TCZ or tar.gz)."""
        package_name = f"{plugin_id}-{version}"

        # Try TCZ (squashfs) first
        if self._can_create_tcz():
            tcz_path = self.build_path / f"{package_name}.tcz"
            try:
                subprocess.run(
                    [
                        "mksquashfs",
                        str(build_dir),
                        str(tcz_path),
                        "-comp",
                        "gzip",
                        "-noappend",
                    ],
                    check=True,
                    capture_output=True,
                    timeout=120,
                )
                return tcz_path, "tcz"
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass  # Fall back to tar.gz

        # Create tar.gz
        tar_path = self.build_path / f"{package_name}.tar.gz"
        subprocess.run(
            ["tar", "-czf", str(tar_path), "-C", str(self.build_path), build_dir.name],
            check=True,
            timeout=60,
        )
        return tar_path, "tar.gz"

    def _can_create_tcz(self) -> bool:
        """Check if mksquashfs is available."""
        try:
            result = subprocess.run(
                ["which", "mksquashfs"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def _calculate_checksum(self, path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _create_manifest(
        self,
        plugin_id: str,
        version: str,
        container_manifest: Dict[str, Any],
        package_path: Path,
        package_type: str,
        checksum: str,
    ) -> PluginManifest:
        """Create plugin manifest."""
        container = container_manifest.get("container", {})
        integration = container_manifest.get("integration", {})
        metadata = container_manifest.get("metadata", {})

        return PluginManifest(
            id=plugin_id,
            name=container.get("name", plugin_id),
            version=version,
            description=container.get("description", ""),
            author=metadata.get("maintainer", "uDOS Wizard Server"),
            license=metadata.get("license", "Unknown"),
            source=container.get("source", ""),
            built_at=datetime.utcnow().isoformat() + "Z",
            built_by="uDOS Wizard Server",
            commit=container.get("commit"),
            package_type=package_type,
            package_size=package_path.stat().st_size,
            package_checksum=checksum,
            wrapper_path=integration.get("wrapper_path"),
            handler_path=integration.get("handler_path"),
        )

    def list_built_plugins(self) -> List[Dict[str, Any]]:
        """List all built plugins in repository."""
        plugins = []

        if self.repo_path.exists():
            for item in self.repo_path.iterdir():
                if item.is_dir():
                    manifest_path = item / "manifest.json"
                    if manifest_path.exists():
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                        plugins.append(manifest)

        return plugins

    def get_plugin_package(self, plugin_id: str) -> Optional[Path]:
        """Get path to plugin package file."""
        plugin_dir = self.repo_path / plugin_id

        if not plugin_dir.exists():
            return None

        # Find package file
        for ext in [".tcz", ".tar.gz"]:
            packages = list(plugin_dir.glob(f"*{ext}"))
            if packages:
                return packages[0]

        return None
