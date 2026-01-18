"""
GitHub Dev Mode - Plugin Factory
================================

Wizard Server only - clones GitHub repos, builds plugins, manages distribution.

This module is ONLY available on Wizard Server (always-on, web-capable).
User devices receive packaged plugins via private transports.

Features:
- Clone public GitHub repositories
- Build TCZ/distribution packages
- Validate licenses (CC0, MIT, Apache, BSD only)
- Version management and updates
- Dependency resolution

Usage:
    from wizard.tools.github_dev import PluginFactory

    factory = PluginFactory()
    factory.clone('rossrobino/typo')
    factory.build('typo', format='tcz')
    factory.distribute('typo', transport='mesh')

Version: v1.0.0.0
"""

import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

# Import logging
try:
    from core.services.logging_manager import get_logger

    logger = get_logger("wizard-github")
except ImportError:
    import logging

    logger = logging.getLogger("wizard-github")


class LicenseType(Enum):
    """Approved license types."""

    MIT = "MIT"
    APACHE2 = "Apache-2.0"
    BSD2 = "BSD-2-Clause"
    BSD3 = "BSD-3-Clause"
    CC0 = "CC0-1.0"
    UNLICENSE = "Unlicense"
    ISC = "ISC"
    UNKNOWN = "unknown"
    REJECTED = "rejected"


# License keywords for detection
LICENSE_KEYWORDS = {
    LicenseType.MIT: ["mit license", "permission is hereby granted, free of charge"],
    LicenseType.APACHE2: ["apache license", "version 2.0"],
    LicenseType.BSD2: ["bsd 2-clause", "simplified bsd"],
    LicenseType.BSD3: ["bsd 3-clause", "new bsd"],
    LicenseType.CC0: ["cc0", "public domain"],
    LicenseType.UNLICENSE: ["unlicense", "this is free and unencumbered"],
    LicenseType.ISC: ["isc license"],
}


@dataclass
class ClonedRepo:
    """Information about a cloned repository."""

    name: str
    owner: str
    url: str
    branch: str
    commit: str
    cloned_at: str
    path: Path
    license: LicenseType
    dependencies: Dict[str, List[str]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "owner": self.owner,
            "url": self.url,
            "branch": self.branch,
            "commit": self.commit,
            "cloned_at": self.cloned_at,
            "path": str(self.path),
            "license": self.license.value,
            "dependencies": self.dependencies,
        }


@dataclass
class BuildResult:
    """Result of a plugin build."""

    success: bool
    package_path: Optional[Path]
    format: str
    size_bytes: int
    checksum: str
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "package_path": str(self.package_path) if self.package_path else None,
            "format": self.format,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "errors": self.errors,
        }


class PluginFactory:
    """
    Plugin Factory for Wizard Server.

    Clones GitHub repos, validates licenses, builds distribution packages.
    """

    def __init__(self, library_path: Optional[Path] = None):
        """
        Initialize Plugin Factory.

        Args:
            library_path: Path to library/ (default: auto-detect)
        """
        if library_path:
            self.library = library_path
        else:
            # Auto-detect from project root (library/ is at root level)
            project_root = Path(__file__).parent.parent.parent
            self.library = project_root / "library"

        self.containers_path = self.library / "containers"
        self.packages_path = self.library / "packages"

        # Create directories
        self.containers_path.mkdir(parents=True, exist_ok=True)
        self.packages_path.mkdir(parents=True, exist_ok=True)

        # Track cloned repos
        self.manifest_path = self.library / "manifest.json"
        self.manifest = self._load_manifest()

        logger.info(f"[WIZ] Plugin Factory initialized: {self.library}")

    def _load_manifest(self) -> Dict[str, Any]:
        """Load or create manifest file."""
        if self.manifest_path.exists():
            return json.loads(self.manifest_path.read_text())
        return {"version": "1.0.0", "repos": {}, "packages": {}, "last_updated": None}

    def _save_manifest(self):
        """Save manifest file."""
        self.manifest["last_updated"] = datetime.utcnow().isoformat()
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2))

    def _detect_license(self, repo_path: Path) -> LicenseType:
        """
        Detect license type from repository.

        Args:
            repo_path: Path to cloned repository

        Returns:
            Detected license type
        """
        # Check LICENSE files
        license_files = [
            "LICENSE",
            "LICENSE.txt",
            "LICENSE.md",
            "COPYING",
            "COPYING.txt",
            "license",
            "license.txt",
        ]

        for filename in license_files:
            license_file = repo_path / filename
            if license_file.exists():
                try:
                    content = license_file.read_text().lower()
                    for license_type, keywords in LICENSE_KEYWORDS.items():
                        if any(kw in content for kw in keywords):
                            logger.info(f"[WIZ] License detected: {license_type.value}")
                            return license_type
                except Exception as e:
                    logger.warning(f"[WIZ] Could not read license file: {e}")

        # Check package.json for npm packages
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                pkg = json.loads(package_json.read_text())
                license_str = pkg.get("license", "").upper()
                for license_type in LicenseType:
                    if license_type.value.upper() in license_str:
                        return license_type
            except Exception:
                pass

        logger.warning(f"[WIZ] Could not detect license for {repo_path}")
        return LicenseType.UNKNOWN

    def _is_license_approved(self, license: LicenseType) -> bool:
        """Check if license is approved for distribution."""
        return license not in [LicenseType.UNKNOWN, LicenseType.REJECTED]

    def _detect_dependencies(self, repo_path: Path) -> Dict[str, List[str]]:
        """
        Detect dependencies from repository.

        Args:
            repo_path: Path to cloned repository

        Returns:
            Dict of dependency types and names
        """
        deps = {"python": [], "node": [], "rust": [], "system": []}

        # Python requirements
        req_file = repo_path / "requirements.txt"
        if req_file.exists():
            deps["python"] = [
                line.strip().split("==")[0].split(">=")[0].split("<=")[0]
                for line in req_file.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            ]

        # Python pyproject.toml
        pyproject = repo_path / "pyproject.toml"
        if pyproject.exists():
            # Basic parsing (full TOML parsing would need a library)
            content = pyproject.read_text()
            if "dependencies" in content:
                deps["python"].append("(see pyproject.toml)")

        # Node.js package.json
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                pkg = json.loads(package_json.read_text())
                deps["node"] = list(pkg.get("dependencies", {}).keys())
            except Exception:
                pass

        # Rust Cargo.toml
        cargo = repo_path / "Cargo.toml"
        if cargo.exists():
            deps["rust"].append("(see Cargo.toml)")

        return {k: v for k, v in deps.items() if v}

    def clone(self, repo: str, branch: str = "main") -> Optional[ClonedRepo]:
        """
        Clone a GitHub repository.

        Args:
            repo: Repository in format "owner/name" or full URL
            branch: Branch to clone (default: main)

        Returns:
            ClonedRepo info or None on failure
        """
        # Parse repo identifier
        if repo.startswith("https://"):
            url = repo
            parts = repo.rstrip("/").split("/")
            owner = parts[-2]
            name = parts[-1].replace(".git", "")
        else:
            parts = repo.split("/")
            if len(parts) != 2:
                logger.error(f"[WIZ] Invalid repo format: {repo}")
                return None
            owner, name = parts
            url = f"https://github.com/{owner}/{name}"

        # Check if already cloned
        repo_path = self.containers_path / name
        if repo_path.exists():
            logger.info(f"[WIZ] Repo already exists: {repo_path}")
            # Return existing info
            if name in self.manifest.get("repos", {}):
                info = self.manifest["repos"][name]
                return ClonedRepo(
                    name=name,
                    owner=owner,
                    url=url,
                    branch=info.get("branch", branch),
                    commit=info.get("commit", ""),
                    cloned_at=info.get("cloned_at", ""),
                    path=repo_path,
                    license=LicenseType(info.get("license", "unknown")),
                    dependencies=info.get("dependencies", {}),
                )

        # Clone repository
        logger.info(f"[WIZ] Cloning {url} (branch: {branch})...")
        try:
            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    branch,
                    url,
                    str(repo_path),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                logger.error(f"[WIZ] Clone failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"[WIZ] Clone timeout for {repo}")
            return None
        except FileNotFoundError:
            logger.error("[WIZ] git command not found")
            return None

        # Get commit hash
        try:
            commit_result = subprocess.run(
                ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
            )
            commit = commit_result.stdout.strip()[:12]
        except Exception:
            commit = "unknown"

        # Detect license and dependencies
        license_type = self._detect_license(repo_path)
        dependencies = self._detect_dependencies(repo_path)

        # Check license approval
        if not self._is_license_approved(license_type):
            logger.warning(f"[WIZ] License not approved: {license_type.value}")
            logger.warning(f"[WIZ] Repo cloned but cannot be distributed")

        # Create repo info
        cloned_repo = ClonedRepo(
            name=name,
            owner=owner,
            url=url,
            branch=branch,
            commit=commit,
            cloned_at=datetime.utcnow().isoformat(),
            path=repo_path,
            license=license_type,
            dependencies=dependencies,
        )

        # Update manifest
        self.manifest["repos"][name] = cloned_repo.to_dict()
        self._save_manifest()

        logger.info(
            f"[WIZ] Cloned {name} (commit: {commit}, license: {license_type.value})"
        )
        return cloned_repo

    def update(self, name: str) -> bool:
        """
        Update a cloned repository.

        Args:
            name: Repository name

        Returns:
            True if updated successfully
        """
        repo_path = self.containers_path / name
        if not repo_path.exists():
            logger.error(f"[WIZ] Repo not found: {name}")
            return False

        logger.info(f"[WIZ] Updating {name}...")
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "pull", "--ff-only"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"[WIZ] Update failed: {result.stderr}")
                return False

            # Update commit in manifest
            commit_result = subprocess.run(
                ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
            )

            if name in self.manifest["repos"]:
                self.manifest["repos"][name]["commit"] = commit_result.stdout.strip()[
                    :12
                ]
                self.manifest["repos"][name][
                    "last_updated"
                ] = datetime.utcnow().isoformat()
                self._save_manifest()

            logger.info(f"[WIZ] Updated {name}")
            return True

        except Exception as e:
            logger.error(f"[WIZ] Update error: {e}")
            return False

    def build(self, name: str, format: str = "tar.gz") -> BuildResult:
        """
        Build distribution package.

        Args:
            name: Repository name
            format: Package format (tar.gz, tcz, zip)

        Returns:
            BuildResult with package info
        """
        repo_path = self.containers_path / name
        if not repo_path.exists():
            return BuildResult(
                success=False,
                package_path=None,
                format=format,
                size_bytes=0,
                checksum="",
                errors=[f"Repository not found: {name}"],
            )

        # Check license before building
        if name in self.manifest.get("repos", {}):
            license_type = LicenseType(
                self.manifest["repos"][name].get("license", "unknown")
            )
            if not self._is_license_approved(license_type):
                return BuildResult(
                    success=False,
                    package_path=None,
                    format=format,
                    size_bytes=0,
                    checksum="",
                    errors=[
                        f"License not approved for distribution: {license_type.value}"
                    ],
                )

        # Build package
        timestamp = datetime.now().strftime("%Y%m%d")
        package_name = f"{name}-{timestamp}.{format}"
        package_path = self.packages_path / package_name

        logger.info(f"[WIZ] Building {package_name}...")

        try:
            if format == "tar.gz":
                import tarfile

                with tarfile.open(package_path, "w:gz") as tar:
                    tar.add(repo_path, arcname=name)

            elif format == "zip":
                shutil.make_archive(
                    str(self.packages_path / f"{name}-{timestamp}"),
                    "zip",
                    repo_path.parent,
                    name,
                )

            elif format == "tcz":
                # TCZ requires mksquashfs (TinyCore tool)
                result = subprocess.run(
                    [
                        "mksquashfs",
                        str(repo_path),
                        str(package_path),
                        "-noappend",
                        "-comp",
                        "xz",
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    return BuildResult(
                        success=False,
                        package_path=None,
                        format=format,
                        size_bytes=0,
                        checksum="",
                        errors=[f"mksquashfs failed: {result.stderr}"],
                    )
            else:
                return BuildResult(
                    success=False,
                    package_path=None,
                    format=format,
                    size_bytes=0,
                    checksum="",
                    errors=[f"Unsupported format: {format}"],
                )

            # Calculate checksum
            import hashlib

            checksum = hashlib.sha256(package_path.read_bytes()).hexdigest()[:16]
            size = package_path.stat().st_size

            # Update manifest
            self.manifest["packages"][package_name] = {
                "source": name,
                "format": format,
                "size_bytes": size,
                "checksum": checksum,
                "built_at": datetime.utcnow().isoformat(),
            }
            self._save_manifest()

            logger.info(f"[WIZ] Built {package_name} ({size} bytes)")

            return BuildResult(
                success=True,
                package_path=package_path,
                format=format,
                size_bytes=size,
                checksum=checksum,
                errors=[],
            )

        except Exception as e:
            logger.error(f"[WIZ] Build error: {e}")
            return BuildResult(
                success=False,
                package_path=None,
                format=format,
                size_bytes=0,
                checksum="",
                errors=[str(e)],
            )

    def list_repos(self) -> List[Dict[str, Any]]:
        """List all cloned repositories."""
        return [
            {"name": name, "path": str(self.containers_path / name), **info}
            for name, info in self.manifest.get("repos", {}).items()
            if (self.containers_path / name).exists()
        ]

    def list_packages(self) -> List[Dict[str, Any]]:
        """List all built packages."""
        return [
            {"filename": name, "path": str(self.packages_path / name), **info}
            for name, info in self.manifest.get("packages", {}).items()
            if (self.packages_path / name).exists()
        ]

    def remove(self, name: str, remove_packages: bool = False) -> bool:
        """
        Remove a cloned repository.

        Args:
            name: Repository name
            remove_packages: Also remove built packages

        Returns:
            True if removed successfully
        """
        repo_path = self.containers_path / name
        if repo_path.exists():
            shutil.rmtree(repo_path)
            logger.info(f"[WIZ] Removed repository: {name}")

        if name in self.manifest.get("repos", {}):
            del self.manifest["repos"][name]

        if remove_packages:
            # Remove associated packages
            for pkg_name in list(self.manifest.get("packages", {}).keys()):
                if pkg_name.startswith(f"{name}-"):
                    pkg_path = self.packages_path / pkg_name
                    if pkg_path.exists():
                        pkg_path.unlink()
                    del self.manifest["packages"][pkg_name]
                    logger.info(f"[WIZ] Removed package: {pkg_name}")

        self._save_manifest()
        return True


# CLI interface
def main():
    """CLI interface for Plugin Factory."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python github_dev.py <command> [args]")
        print("")
        print("Commands:")
        print("  clone <owner/repo>    Clone GitHub repository")
        print("  update <name>         Update repository")
        print("  build <name> [format] Build package (tar.gz, tcz, zip)")
        print("  list                  List cloned repos")
        print("  packages              List built packages")
        print("  remove <name>         Remove repository")
        return

    factory = PluginFactory()
    cmd = sys.argv[1]

    if cmd == "clone" and len(sys.argv) >= 3:
        repo = factory.clone(sys.argv[2])
        if repo:
            print(f"✅ Cloned: {repo.name}")
            print(f"   Path: {repo.path}")
            print(f"   License: {repo.license.value}")
        else:
            print("❌ Clone failed")

    elif cmd == "update" and len(sys.argv) >= 3:
        if factory.update(sys.argv[2]):
            print(f"✅ Updated: {sys.argv[2]}")
        else:
            print("❌ Update failed")

    elif cmd == "build" and len(sys.argv) >= 3:
        fmt = sys.argv[3] if len(sys.argv) >= 4 else "tar.gz"
        result = factory.build(sys.argv[2], fmt)
        if result.success:
            print(f"✅ Built: {result.package_path}")
            print(f"   Size: {result.size_bytes} bytes")
            print(f"   Checksum: {result.checksum}")
        else:
            print("❌ Build failed")
            for err in result.errors:
                print(f"   {err}")

    elif cmd == "list":
        repos = factory.list_repos()
        print(f"📦 Cloned Repositories ({len(repos)}):")
        for repo in repos:
            print(f"  • {repo['name']} ({repo.get('license', 'unknown')})")

    elif cmd == "packages":
        packages = factory.list_packages()
        print(f"📦 Built Packages ({len(packages)}):")
        for pkg in packages:
            print(f"  • {pkg['filename']} ({pkg.get('size_bytes', 0)} bytes)")

    elif cmd == "remove" and len(sys.argv) >= 3:
        factory.remove(sys.argv[2], remove_packages=True)
        print(f"✅ Removed: {sys.argv[2]}")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
