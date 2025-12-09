"""
uDOS v1.2.21 - BUILD Command Handler

Pre-downloads and packages online repositories for consolidated offline installation.
Creates distributable packages with all external dependencies included.

Commands:
- BUILD                      - Package system with all repositories
- BUILD --check              - Show repository status
- BUILD --download           - Download missing repositories
- BUILD --package            - Create distribution package
- BUILD HELP                 - Show help
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json
import subprocess
import tarfile
from .base_handler import BaseCommandHandler


class BuildHandler(BaseCommandHandler):
    """Handler for building offline installation packages."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Define external repositories to include
        self.repositories = {
            'meshcore': {
                'url': 'https://github.com/meshcore-dev/MeshCore.git',
                'path': 'extensions/cloned/meshcore',
                'description': 'Mesh networking integration',
                'required': False
            },
            'coreui': {
                'url': 'https://github.com/coreui/coreui-icons.git',
                'path': 'extensions/cloned/coreui',
                'description': 'Icon library',
                'required': False
            }
        }

    def handle(self, params: List[str], grid, parser) -> str:
        """
        Route BUILD commands to appropriate handlers.

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result message
        """
        if not params or params[0].upper() == 'HELP':
            return self._show_help()

        command = params[0].lower() if params else ''

        if command == '--check' or command == 'check':
            return self._check_repository_status()
        elif command == '--download' or command == 'download':
            return self._download_repositories()
        elif command == '--package' or command == 'package':
            return self._create_build_package()
        else:
            # Default: full build process
            return self._full_build()

    def _show_help(self) -> str:
        """Show BUILD command help."""
        return """╔══════════════════════════════════════════════════════════╗
║           BUILD - OFFLINE INSTALLATION PACKAGING        ║
╚══════════════════════════════════════════════════════════╝

Pre-downloads and packages online repositories for offline installation.

USAGE:
  BUILD                      - Full build (check + download + package)
  BUILD --check              - Show repository status
  BUILD --download           - Download missing repositories
  BUILD --package            - Create distribution package
  BUILD HELP                 - Show this help

REPOSITORIES INCLUDED:
  • MeshCore                 - Mesh networking integration (optional)
  • CoreUI Icons             - Icon library (optional)

PACKAGE CONTENTS:
  • Complete uDOS core system
  • Downloaded external repositories
  • User content (if CLONE run first)
  • Installation manifest

OUTPUT:
  Creates timestamped .tar.gz package: udos-build-YYYYMMDD_HHMMSS.tar.gz

WORKFLOW:
  1. BUILD --check           # Verify repository status
  2. BUILD --download        # Download missing repos
  3. CLONE                   # Package user content (optional)
  4. BUILD --package         # Create final distribution

EXAMPLES:
  BUILD                      # Full automated build
  BUILD --check              # Check what's available
  BUILD --download           # Download external repos
  BUILD --package            # Package for distribution

💡 Use CLONE before BUILD to include user content
💡 Resulting package can be installed offline
💡 Extensions are optional - core works without them
"""

    def _check_repository_status(self) -> str:
        """Check status of external repositories."""
        result = "╔══════════════════════════════════════════════════════════╗\n"
        result += "║           REPOSITORY STATUS CHECK                       ║\n"
        result += "╚══════════════════════════════════════════════════════════╝\n\n"

        available = 0
        missing = 0

        for repo_name, repo_info in self.repositories.items():
            path = Path(repo_info['path'])
            if path.exists() and path.is_dir():
                # Check if it's a valid git repo
                git_dir = path / '.git'
                if git_dir.exists():
                    result += f"✅ {repo_name}\n"
                    result += f"   {repo_info['description']}\n"
                    result += f"   Location: {repo_info['path']}\n"
                    result += f"   Status: Cloned\n\n"
                    available += 1
                else:
                    result += f"⚠️  {repo_name}\n"
                    result += f"   {repo_info['description']}\n"
                    result += f"   Location: {repo_info['path']}\n"
                    result += f"   Status: Directory exists but not a git repo\n\n"
                    missing += 1
            else:
                result += f"❌ {repo_name}\n"
                result += f"   {repo_info['description']}\n"
                result += f"   URL: {repo_info['url']}\n"
                result += f"   Status: Not cloned\n\n"
                missing += 1

        result += "─" * 60 + "\n"
        result += f"📊 Status: {available} available, {missing} missing\n\n"

        if missing > 0:
            result += "💡 Run BUILD --download to clone missing repositories\n"
        else:
            result += "✅ All repositories available\n"
            result += "💡 Run BUILD --package to create distribution package\n"

        return result

    def _download_repositories(self) -> str:
        """Download missing external repositories."""
        result = "╔══════════════════════════════════════════════════════════╗\n"
        result += "║           DOWNLOADING REPOSITORIES                      ║\n"
        result += "╚══════════════════════════════════════════════════════════╝\n\n"

        success = 0
        failed = 0

        for repo_name, repo_info in self.repositories.items():
            path = Path(repo_info['path'])
            
            if path.exists():
                result += f"⏭️  {repo_name}: Already exists\n"
                success += 1
                continue

            result += f"📥 Downloading {repo_name}...\n"
            result += f"   URL: {repo_info['url']}\n"

            try:
                # Ensure parent directory exists
                path.parent.mkdir(parents=True, exist_ok=True)

                # Clone repository
                subprocess.run(
                    ['git', 'clone', repo_info['url'], str(path)],
                    capture_output=True,
                    check=True,
                    timeout=300  # 5 minute timeout
                )

                result += f"   ✅ Successfully cloned\n\n"
                success += 1

            except subprocess.CalledProcessError as e:
                result += f"   ❌ Clone failed: {e.stderr.decode() if e.stderr else 'Unknown error'}\n\n"
                failed += 1
            except subprocess.TimeoutExpired:
                result += f"   ❌ Clone timed out after 5 minutes\n\n"
                failed += 1
            except Exception as e:
                result += f"   ❌ Error: {str(e)}\n\n"
                failed += 1

        result += "─" * 60 + "\n"
        result += f"📊 Results: {success} successful, {failed} failed\n\n"

        if failed == 0:
            result += "✅ All repositories downloaded\n"
            result += "💡 Run BUILD --package to create distribution\n"
        else:
            result += "⚠️  Some downloads failed\n"
            result += "💡 Check network connection and try again\n"

        return result

    def _create_build_package(self) -> str:
        """Create complete build package for offline installation."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        package_name = f"udos-build-{timestamp}.tar.gz"
        package_path = Path(package_name)

        result = "╔══════════════════════════════════════════════════════════╗\n"
        result += "║           CREATING BUILD PACKAGE                        ║\n"
        result += "╚══════════════════════════════════════════════════════════╝\n\n"

        try:
            total_files = 0
            total_size = 0

            # Directories to include in build
            build_dirs = [
                'core',
                'extensions',
                'knowledge',
                'wiki',
                'bin'
            ]

            # Essential files
            build_files = [
                'uDOS.py',
                'start_udos.sh',
                'requirements.txt',
                'README.MD',
                'LICENSE.txt',
                'INSTALL.md'
            ]

            with tarfile.open(package_path, 'w:gz') as tar:
                # Add metadata
                metadata = {
                    'created': timestamp,
                    'version': 'v1.2.21',
                    'type': 'offline-build',
                    'description': 'uDOS offline installation package',
                    'includes_repositories': [
                        repo for repo, info in self.repositories.items()
                        if Path(info['path']).exists()
                    ]
                }

                # Create temporary metadata file
                metadata_path = Path('build_metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                tar.add(metadata_path, arcname='build_metadata.json')
                metadata_path.unlink()

                # Add core directories
                for dir_name in build_dirs:
                    dir_path = Path(dir_name)
                    if dir_path.exists():
                        for file_path in dir_path.rglob('*'):
                            if file_path.is_file():
                                # Skip unwanted files
                                if any(x in str(file_path) for x in ['__pycache__', '.pyc', '.DS_Store', '.git']):
                                    continue

                                tar.add(file_path, arcname=file_path)
                                total_files += 1
                                total_size += file_path.stat().st_size

                # Add essential files
                for file_name in build_files:
                    file_path = Path(file_name)
                    if file_path.exists():
                        tar.add(file_path, arcname=file_path)
                        total_files += 1
                        total_size += file_path.stat().st_size

                # Check for user clone package
                clone_packages = sorted(Path('.').glob('udos-clone-*.tar.gz'), reverse=True)
                if clone_packages:
                    latest_clone = clone_packages[0]
                    result += f"📦 Including user content: {latest_clone}\n\n"
                    tar.add(latest_clone, arcname=latest_clone.name)

            package_size = package_path.stat().st_size
            compression_ratio = (1 - package_size / total_size) * 100 if total_size > 0 else 0

            result += f"✅ Build package created successfully\n\n"
            result += f"📦 Package: {package_path}\n"
            result += f"📊 Contents: {total_files} files ({total_size / (1024 * 1024):.2f} MB)\n"
            result += f"💾 Package size: {package_size / (1024 * 1024):.2f} MB\n"
            result += f"📉 Compression: {compression_ratio:.1f}%\n\n"

            # Check for included repositories
            included_repos = [
                repo for repo, info in self.repositories.items()
                if Path(info['path']).exists()
            ]
            if included_repos:
                result += f"🔌 Included repositories: {', '.join(included_repos)}\n"
            else:
                result += f"ℹ️  No external repositories included\n"

            result += f"\n💡 Installation:\n"
            result += f"   1. tar -xzf {package_name}\n"
            result += f"   2. cd uDOS/\n"
            result += f"   3. python3 -m venv .venv\n"
            result += f"   4. source .venv/bin/activate\n"
            result += f"   5. pip install -r requirements.txt\n"
            result += f"   6. ./start_udos.sh\n"

            return result

        except Exception as e:
            return f"❌ Build package creation failed: {str(e)}"

    def _full_build(self) -> str:
        """Execute full build process: check + download + package."""
        result = "╔══════════════════════════════════════════════════════════╗\n"
        result += "║           FULL BUILD PROCESS                            ║\n"
        result += "╚══════════════════════════════════════════════════════════╝\n\n"

        # Step 1: Check status
        result += "📋 Step 1: Checking repository status...\n\n"
        status = self._check_repository_status()
        result += status + "\n"

        # Step 2: Download if needed
        missing = sum(1 for repo, info in self.repositories.items() if not Path(info['path']).exists())
        if missing > 0:
            result += "\n📥 Step 2: Downloading missing repositories...\n\n"
            download = self._download_repositories()
            result += download + "\n"
        else:
            result += "\n⏭️  Step 2: All repositories available, skipping download\n\n"

        # Step 3: Create package
        result += "\n📦 Step 3: Creating build package...\n\n"
        package = self._create_build_package()
        result += package

        return result
