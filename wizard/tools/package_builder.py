"""
TCZ Package Builder
Alpha v1.0.3.0+

Build TinyCore Extension (TCZ) packages for uDOS distribution.

Usage:
    python -m wizard.tools.package_builder build core
    python -m wizard.tools.package_builder build all
    python -m wizard.tools.package_builder bundle standard
"""

import json
import hashlib
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.services.logging_api import get_logger

logger = get_logger("wizard-packaging")


class PackageBuilder:
    """
    Build TCZ packages for TinyCore Linux distribution.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or PROJECT_ROOT
        self.distribution_dir = self.project_root / "distribution"
        self.build_dir = self.distribution_dir / "build"
        self.packages_dir = self.distribution_dir / "packages"

        # Ensure directories exist
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.packages_dir.mkdir(parents=True, exist_ok=True)

        # Package definitions
        self.packages = self._load_package_definitions()

    def _load_package_definitions(self) -> Dict:
        """Load package definitions"""
        return {
            "core": {
                "name": "udos-core",
                "description": "uDOS TUI and TypeScript Runtime",
                "version_module": "core",
                "sources": [
                    ("core", "opt/udos/core"),
                    ("start_udos.sh", "opt/udos/bin/udos"),
                ],
                "dependencies": ["python3.11"],
                "exclude": ["__pycache__", "*.pyc", ".git", "tests"],
            },
            "api": {
                "name": "udos-api",
                "description": "uDOS REST/WebSocket API Server",
                "version_module": "api",
                "sources": [
                    ("extensions/api", "opt/udos/extensions/api"),
                ],
                "dependencies": ["udos-core", "python3.11"],
                "exclude": ["__pycache__", "*.pyc", ".git"],
            },
            "groovebox": {
                "name": "udos-groovebox",
                "description": "MML Music Production Extension",
                "version_module": "groovebox",
                "sources": [
                    ("groovebox", "opt/udos/extensions/groovebox"),
                ],
                "dependencies": ["udos-core"],
                "exclude": ["__pycache__", "*.pyc", ".git", "tests"],
            },
            "transport": {
                "name": "udos-transport",
                "description": "MeshCore, QR, and Audio Transport",
                "version_module": "transport",
                "sources": [
                    ("extensions/transport", "opt/udos/extensions/transport"),
                ],
                "dependencies": ["udos-core"],
                "exclude": ["__pycache__", "*.pyc", ".git"],
            },
            "knowledge": {
                "name": "udos-knowledge",
                "description": "Offline Knowledge Bank",
                "version_module": "knowledge",
                "sources": [
                    ("knowledge", "opt/udos/knowledge"),
                ],
                "dependencies": ["udos-core"],
                "exclude": [".git"],
            },
            "wizard": {
                "name": "udos-wizard",
                "description": "Wizard Server with AI Providers",
                "version_module": "wizard",
                "sources": [
                    ("wizard", "opt/udos/wizard"),
                ],
                "dependencies": ["udos-core", "udos-api"],
                "exclude": ["__pycache__", "*.pyc", ".git", "library"],
            },
        }

    def _get_version(self, module: str) -> str:
        """Get version for a module"""
        try:
            from core.version import get_all_versions

            versions = get_all_versions()
            return versions.get(module, "1.0.0.0")
        except Exception:
            return "1.0.0.0"

    def build(self, package_id: str) -> Optional[Path]:
        """
        Build a single TCZ package.

        Args:
            package_id: Package identifier (core, api, groovebox, etc.)

        Returns:
            Path to built TCZ file, or None on failure
        """
        if package_id not in self.packages:
            logger.error(f"Unknown package: {package_id}")
            return None

        pkg = self.packages[package_id]
        pkg_name = pkg["name"]
        version = self._get_version(pkg.get("version_module", package_id))

        logger.info(f"[WIZ] Building {pkg_name} v{version}")

        # Create build directory
        pkg_build_dir = self.build_dir / pkg_name
        if pkg_build_dir.exists():
            shutil.rmtree(pkg_build_dir)
        pkg_build_dir.mkdir(parents=True)

        # Copy sources
        for src, dest in pkg["sources"]:
            src_path = self.project_root / src
            dest_path = pkg_build_dir / dest

            if not src_path.exists():
                logger.warning(f"Source not found: {src_path}")
                continue

            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if src_path.is_dir():
                shutil.copytree(
                    src_path,
                    dest_path,
                    ignore=shutil.ignore_patterns(*pkg.get("exclude", [])),
                )
            else:
                shutil.copy2(src_path, dest_path)

        # Create TCZ (squashfs)
        tcz_path = self.packages_dir / f"{pkg_name}.tcz"

        # Check if mksquashfs is available
        if shutil.which("mksquashfs"):
            result = subprocess.run(
                [
                    "mksquashfs",
                    str(pkg_build_dir),
                    str(tcz_path),
                    "-b",
                    "4096",
                    "-no-xattrs",
                    "-noappend",
                    "-quiet",
                ],
                capture_output=True,
            )
            if result.returncode != 0:
                logger.error(f"mksquashfs failed: {result.stderr.decode()}")
                # Fall back to tar.gz
                self._create_tarball(pkg_build_dir, pkg_name)
        else:
            # Fall back to tar.gz for non-TinyCore systems
            logger.info("mksquashfs not found, creating tar.gz instead")
            tcz_path = self._create_tarball(pkg_build_dir, pkg_name)

        # Generate metadata files
        self._create_dep_file(pkg_name, pkg["dependencies"])
        self._create_info_file(pkg_name, pkg["description"], version, tcz_path)
        self._create_md5_file(tcz_path)

        logger.info(f"[WIZ] Built: {tcz_path}")
        return tcz_path

    def _create_tarball(self, src_dir: Path, pkg_name: str) -> Path:
        """Create tar.gz fallback for non-TinyCore systems"""
        tarball_path = self.packages_dir / f"{pkg_name}.tar.gz"
        shutil.make_archive(str(self.packages_dir / pkg_name), "gztar", src_dir)
        return tarball_path

    def _create_dep_file(self, pkg_name: str, dependencies: List[str]):
        """Create .dep dependency file"""
        dep_path = self.packages_dir / f"{pkg_name}.tcz.dep"
        with open(dep_path, "w") as f:
            for dep in dependencies:
                if not dep.endswith(".tcz"):
                    dep = f"{dep}.tcz"
                f.write(f"{dep}\n")

    def _create_info_file(
        self, pkg_name: str, description: str, version: str, tcz_path: Path
    ):
        """Create .info metadata file"""
        size = "N/A"
        if tcz_path.exists():
            size_bytes = tcz_path.stat().st_size
            if size_bytes > 1024 * 1024:
                size = f"{size_bytes / (1024 * 1024):.1f}M"
            else:
                size = f"{size_bytes / 1024:.1f}K"

        info_path = self.packages_dir / f"{pkg_name}.tcz.info"
        with open(info_path, "w") as f:
            f.write(f"Title:          {pkg_name}\n")
            f.write(f"Description:    {description}\n")
            f.write(f"Version:        {version}\n")
            f.write(f"Author:         uDOS Team\n")
            f.write(f"Original-site:  https://github.com/udos-project/udos\n")
            f.write(f"Copying-policy: MIT\n")
            f.write(f"Size:           {size}\n")
            f.write(f"Extension_by:   uDOS Wizard Server\n")
            f.write(f"Comments:       Offline-first knowledge system\n")
            f.write(f"Change-log:     Built {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Current:        {version}\n")

    def _create_md5_file(self, tcz_path: Path):
        """Create MD5 checksum file"""
        if not tcz_path.exists():
            return

        md5_hash = hashlib.md5()
        with open(tcz_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5_hash.update(chunk)

        md5_path = tcz_path.parent / f"{tcz_path.name}.md5.txt"
        with open(md5_path, "w") as f:
            f.write(f"{md5_hash.hexdigest()}  {tcz_path.name}\n")

    def build_all(self) -> Dict[str, Optional[Path]]:
        """Build all packages"""
        results = {}
        for pkg_id in self.packages:
            results[pkg_id] = self.build(pkg_id)
        return results

    def bundle(self, profile: str) -> Optional[Path]:
        """
        Create a distribution bundle for a profile.

        Profiles:
            minimal: core only
            standard: core, api, knowledge
            full: core, api, knowledge, groovebox, transport
            wizard: core, api, wizard, transport
        """
        profiles = {
            "minimal": ["core"],
            "standard": ["core", "api", "knowledge"],
            "full": ["core", "api", "knowledge", "groovebox", "transport"],
            "wizard": ["core", "api", "wizard", "transport"],
        }

        if profile not in profiles:
            logger.error(f"Unknown profile: {profile}")
            return None

        packages = profiles[profile]
        logger.info(f"[WIZ] Building {profile} bundle: {packages}")

        # Build all packages in profile
        for pkg_id in packages:
            self.build(pkg_id)

        # Create manifest
        self._create_manifest(profile, packages)

        # Create bundle archive
        bundle_path = self.distribution_dir / f"udos-{profile}-bundle.tar.gz"

        # Collect package files
        bundle_dir = self.build_dir / f"bundle-{profile}"
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)
        bundle_dir.mkdir()

        for pkg_id in packages:
            pkg_name = self.packages[pkg_id]["name"]
            for ext in [".tcz", ".tar.gz", ".tcz.dep", ".tcz.info", ".tcz.md5.txt"]:
                src = self.packages_dir / f"{pkg_name}{ext}"
                if src.exists():
                    shutil.copy2(src, bundle_dir)

        # Copy manifest
        manifest_src = self.distribution_dir / "manifest.json"
        if manifest_src.exists():
            shutil.copy2(manifest_src, bundle_dir)

        # Create bundle archive
        shutil.make_archive(
            str(self.distribution_dir / f"udos-{profile}-bundle"), "gztar", bundle_dir
        )

        logger.info(f"[WIZ] Bundle created: {bundle_path}")
        return bundle_path

    def _create_manifest(self, profile: str, packages: List[str]):
        """Create distribution manifest"""
        manifest = {
            "version": self._get_version("core"),
            "build_date": datetime.now().isoformat(),
            "profile": profile,
            "packages": {},
        }

        for pkg_id in packages:
            pkg = self.packages[pkg_id]
            pkg_name = pkg["name"]

            # Get package info
            tcz_path = self.packages_dir / f"{pkg_name}.tcz"
            tar_path = self.packages_dir / f"{pkg_name}.tar.gz"
            pkg_path = tcz_path if tcz_path.exists() else tar_path

            size = "N/A"
            md5 = "N/A"

            if pkg_path.exists():
                size_bytes = pkg_path.stat().st_size
                if size_bytes > 1024 * 1024:
                    size = f"{size_bytes / (1024 * 1024):.1f}M"
                else:
                    size = f"{size_bytes / 1024:.1f}K"

                md5_hash = hashlib.md5()
                with open(pkg_path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        md5_hash.update(chunk)
                md5 = md5_hash.hexdigest()

            manifest["packages"][pkg_id] = {
                "name": pkg_name,
                "version": self._get_version(pkg.get("version_module", pkg_id)),
                "size": size,
                "md5": md5,
                "dependencies": pkg["dependencies"],
            }

        manifest_path = self.distribution_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"[WIZ] Manifest created: {manifest_path}")

    def list_packages(self) -> List[Dict]:
        """List all available packages"""
        result = []
        for pkg_id, pkg in self.packages.items():
            result.append(
                {
                    "id": pkg_id,
                    "name": pkg["name"],
                    "description": pkg["description"],
                    "version": self._get_version(pkg.get("version_module", pkg_id)),
                    "dependencies": pkg["dependencies"],
                }
            )
        return result

    def clean(self):
        """Clean build directories"""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            self.build_dir.mkdir()
        logger.info("[WIZ] Build directory cleaned")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="uDOS TCZ Package Builder")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build a package")
    build_parser.add_argument("package", help="Package ID (core, api, all, etc.)")

    # Bundle command
    bundle_parser = subparsers.add_parser("bundle", help="Create distribution bundle")
    bundle_parser.add_argument(
        "profile", help="Profile (minimal, standard, full, wizard)"
    )

    # List command
    subparsers.add_parser("list", help="List available packages")

    # Clean command
    subparsers.add_parser("clean", help="Clean build directories")

    args = parser.parse_args()
    builder = PackageBuilder()

    if args.command == "build":
        if args.package == "all":
            results = builder.build_all()
            for pkg_id, path in results.items():
                status = "✅" if path else "❌"
                print(f"{status} {pkg_id}: {path or 'FAILED'}")
        else:
            path = builder.build(args.package)
            if path:
                print(f"✅ Built: {path}")
            else:
                print(f"❌ Build failed for: {args.package}")
                sys.exit(1)

    elif args.command == "bundle":
        path = builder.bundle(args.profile)
        if path:
            print(f"✅ Bundle: {path}")
        else:
            print(f"❌ Bundle failed for profile: {args.profile}")
            sys.exit(1)

    elif args.command == "list":
        packages = builder.list_packages()
        print("📦 Available Packages:\n")
        for pkg in packages:
            print(f"  {pkg['id']}: {pkg['name']} v{pkg['version']}")
            print(f"      {pkg['description']}")
            print(f"      Dependencies: {', '.join(pkg['dependencies'])}")
            print()

    elif args.command == "clean":
        builder.clean()
        print("✅ Build directory cleaned")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
