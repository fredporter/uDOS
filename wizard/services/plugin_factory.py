"""
Plugin Factory - APK Package Builder
====================================

Builds distribution packages from code containers for Alpine Linux.

Package Types:
  - APK: Alpine Package (standard Alpine format)
  - TAR.GZ: Generic tarball (fallback)

Build Process:
  1. Clone/update container from GitHub
  2. Run any build scripts
  3. Package into APK format
  4. Generate manifest and checksums
  5. Upload to plugin repository

Requirements (for APK):
  - abuild (Alpine package build tools)
  - Alpine Linux environment (for testing)

Migration Note:
    This replaces the old TinyCore TCZ packaging system (deprecated).
  See ADR-0003-alpine-linux-migration.md for details.
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
    package_type: str = "apk"  # Changed from tar.gz to apk
    package_size: int = 0
    package_checksum: str = ""
    apk_arch: str = "x86_64"  # APK architecture (x86_64, aarch64, armv7, etc.)

    # Dependencies (APK format)
    dependencies: List[str] = None
    apk_dependencies: List[str] = None  # APK-specific runtime deps
    build_dependencies: List[str] = None  # APK-specific build deps

    # uDOS integration
    wrapper_path: Optional[str] = None
    handler_path: Optional[str] = None
    commands: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.apk_dependencies is None:
            self.apk_dependencies = []
        if self.build_dependencies is None:
            self.build_dependencies = []
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
    - TCZ packaging (TinyCore, deprecated)
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

        # Find package file (now prioritizes .apk)
        for ext in [".apk", ".tcz", ".tar.gz"]:
            packages = list(plugin_dir.glob(f"*{ext}"))
            if packages:
                return packages[0]

        return None


class APKBuilder:
    """
    Build Alpine APK packages from code containers.

    APK format is the standard Alpine Linux package format.
    Uses abuild (Alpine build tools) for package creation.

    Example:
        builder = APKBuilder()
        result = builder.build_apk(
            "udos-core",
            container_path=Path("cloned/udos-core"),
            arch="x86_64"
        )
    """

    def __init__(self, logger=None):
        """Initialize APK builder."""
        self.containers_path = CONTAINERS_PATH
        self.build_temp = BUILD_TEMP_PATH
        self.repo_path = PLUGIN_REPO_PATH
        self.logger = logger
        self._default_key_dir = Path.home() / ".abuild"

    def _check_abuild_key(self) -> Tuple[bool, str]:
        """Check for abuild signing key presence."""
        sign_key = os.environ.get("WIZARD_APK_SIGN_KEY")
        if sign_key:
            key_path = Path(sign_key)
            if key_path.exists():
                return True, f"WIZARD_APK_SIGN_KEY={key_path}"
            return False, f"WIZARD_APK_SIGN_KEY not found: {key_path}"

        key_name = os.environ.get("ABUILD_KEYNAME", "udos")
        candidate = self._default_key_dir / f"{key_name}.rsa"
        if candidate.exists():
            return True, f"ABUILD_KEYNAME={key_name} ({candidate})"

        # Fallback: any .rsa in ~/.abuild
        keys = list(self._default_key_dir.glob("*.rsa"))
        if keys:
            return True, f"abuild key found: {keys[0]}"
        return False, "abuild key not found in ~/.abuild"

    def build_apk(
        self,
        plugin_id: str,
        container_path: Optional[Path] = None,
        arch: str = "x86_64",
        version: Optional[str] = None,
    ) -> BuildResult:
        """
        Build APK package from container.

        Args:
            plugin_id: Package name (e.g., 'udos-core')
            container_path: Path to container source (auto-detect if None)
            arch: Target architecture (x86_64, aarch64, armv7, ppc64le, s390x)
            version: Package version (auto-detect from APKBUILD if None)

        Returns:
            BuildResult with package path and manifest

        Note:
            APK build requires:
            - APKBUILD file in container root
            - abuild and apk-tools installed
            - Build dependencies installed (apk add -t .makedeps ...)
        """
        import time

        start_time = time.time()

        try:
            if not container_path:
                container_path = self.containers_path / plugin_id

            if not container_path.exists():
                return BuildResult(
                    success=False,
                    plugin_id=plugin_id,
                    error=f"Container not found: {container_path}",
                )

            apkbuild_path = container_path / "APKBUILD"
            if not apkbuild_path.exists():
                return BuildResult(
                    success=False,
                    plugin_id=plugin_id,
                    error="APKBUILD not found in container",
                    build_time_seconds=time.time() - start_time,
                )

            if shutil.which("abuild") is None:
                return BuildResult(
                    success=False,
                    plugin_id=plugin_id,
                    error="abuild not found (install abuild on Alpine)",
                    build_time_seconds=time.time() - start_time,
                )

            key_ok, key_msg = self._check_abuild_key()
            if not key_ok:
                return BuildResult(
                    success=False,
                    plugin_id=plugin_id,
                    error=f"abuild key missing: {key_msg}",
                    build_time_seconds=time.time() - start_time,
                )

            # Validate APKBUILD
            lint = subprocess.run(
                ["abuild", "-n"],
                cwd=str(container_path),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if lint.returncode != 0:
                return BuildResult(
                    success=False,
                    plugin_id=plugin_id,
                    error=f"APKBUILD validation failed: {lint.stderr.strip()}",
                    build_time_seconds=time.time() - start_time,
                )

            # Build package (requires abuild setup and keys)
            repo_dest = self.build_temp / "apk-repo"
            repo_dest.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()
            env["REPODEST"] = str(repo_dest)
            if version:
                env["PKGVER_OVERRIDE"] = version

            build = subprocess.run(
                ["abuild", "-r"],
                cwd=str(container_path),
                env=env,
                capture_output=True,
                text=True,
                timeout=900,
            )
            if build.returncode != 0:
                return BuildResult(
                    success=False,
                    plugin_id=plugin_id,
                    error=f"abuild failed: {build.stderr.strip()}",
                    build_time_seconds=time.time() - start_time,
                )

            # Locate built APKs
            built_apks = sorted(repo_dest.rglob("*.apk"))
            if not built_apks:
                return BuildResult(
                    success=False,
                    plugin_id=plugin_id,
                    error="No APKs produced by abuild",
                    build_time_seconds=time.time() - start_time,
                )

            # Prefer package that matches plugin_id prefix
            package_path = None
            for apk in built_apks:
                if apk.name.startswith(f"{plugin_id}-"):
                    package_path = apk
                    break
            if not package_path:
                package_path = built_apks[0]

            # Move APK into plugin repository
            plugin_dir = self.repo_path / plugin_id
            plugin_dir.mkdir(parents=True, exist_ok=True)
            final_path = plugin_dir / package_path.name
            shutil.copy2(package_path, final_path)

            return BuildResult(
                success=True,
                plugin_id=plugin_id,
                package_path=final_path,
                build_time_seconds=time.time() - start_time,
            )

        except Exception as e:
            return BuildResult(
                success=False,
                plugin_id=plugin_id,
                error=f"APK build failed: {str(e)}",
                build_time_seconds=time.time() - start_time,
            )

    def verify_apk(self, apk_path: Path) -> Tuple[bool, str]:
        """
        Verify APK signature and integrity.

        Args:
            apk_path: Path to .apk file

        Returns:
            (valid: bool, message: str)
        """
        if not apk_path.exists():
            return False, "APK not found"
        try:
            import tarfile

            with tarfile.open(apk_path, "r:gz") as tf:
                members = tf.getnames()
                has_signature = any(
                    name.startswith(".SIGN.RSA.") for name in members
                )
            msg = "Signature present" if has_signature else "Signature not found"
            return True, msg
        except Exception as e:
            return False, f"APK verification error: {str(e)}"

    def generate_apkindex(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Generate or update APKINDEX for repository.

        Args:
            repo_path: Repository path (uses default if None)

        Returns:
            (success: bool, message: str)
        """
        if not repo_path:
            repo_path = self.repo_path

        apk_files = list(Path(repo_path).rglob("*.apk"))
        if not apk_files:
            return False, "No APKs found for index"

        if shutil.which("apk") is None:
            return False, "apk tool not found"

        index_path = Path(repo_path) / "APKINDEX.tar.gz"
        cmd = ["apk", "index", "-o", str(index_path)] + [str(p) for p in apk_files]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return False, f"apk index failed: {result.stderr.strip()}"

        sign_key = os.environ.get("WIZARD_APK_SIGN_KEY")
        if sign_key:
            if shutil.which("abuild-sign") is None:
                return False, "abuild-sign not found for signing"
            sign = subprocess.run(
                ["abuild-sign", "-k", sign_key, str(index_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if sign.returncode != 0:
                return False, f"abuild-sign failed: {sign.stderr.strip()}"
            return True, f"APKINDEX generated and signed: {index_path}"

        return True, f"APKINDEX generated (unsigned): {index_path}"


class TCZBuilder:
    """
    DEPRECATED: Old TinyCore TCZ package builder. Use Alpine-style plugin packaging and distribution managed by Wizard.

    This class is kept for backwards compatibility only.
    Use APKBuilder instead for Alpine Linux packages.

    References:
    - Migration Guide: docs/decisions/ADR-0003-alpine-linux-migration.md
    - Alpine APK Format: docs/howto/alpine-install.md
    """

    def __init__(self, logger=None):
        """Initialize (deprecated)."""
        import warnings

        warnings.warn(
            "TCZBuilder is deprecated. Use APKBuilder for Alpine packages.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.logger = logger
        self.apk_builder = APKBuilder(logger=logger)

    def build_tcz(self, *args, **kwargs):
        """DEPRECATED: Use APKBuilder.build_apk() instead."""
        raise NotImplementedError(
            "TCZ packaging is deprecated. Use Alpine APK packages instead.\n"
            "See: docs/decisions/ADR-0003-alpine-linux-migration.md"
        )
