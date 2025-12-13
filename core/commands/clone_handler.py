"""
uDOS v1.2.23 - CLONE Command Handler

Collates unique local user content folders for system duplication.
Packages user-created content for backup or transfer to another installation.

Commands:
- CLONE                      - Create full user content package
- CLONE --check              - Show what would be included
- CLONE --to <path>          - Export to specific location
- CLONE --exclude <pattern>  - Exclude patterns
- CLONE HELP                 - Show help
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime
import json
import shutil
import tarfile
from .base_handler import BaseCommandHandler


class CloneHandler(BaseCommandHandler):
    """Handler for cloning user content folders."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Define user content directories to clone
        self.user_content_dirs = {
            'memory/docs': 'User documentation',
            'memory/drafts': 'Draft content',
            'memory/ucode/scripts': 'User .upy scripts',
            'memory/ucode/sandbox': 'Draft .upy scripts',
            'memory/workflows/missions': 'Mission workflows',
            'memory/bank/user': 'User settings and data',
            'memory/bank/private': 'Private transactions',
            'memory/shared/public': 'Public shared content',
        }

    def handle(self, params: List[str], grid, parser) -> str:
        """
        Route CLONE commands to appropriate handlers.

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result message
        """
        if not params or params[0].upper() == 'HELP':
            return self._show_help()

        # Parse flags
        check_only = '--check' in params
        export_path = None
        exclude_patterns = []

        if '--to' in params:
            idx = params.index('--to')
            if idx + 1 < len(params):
                export_path = Path(params[idx + 1])

        if '--exclude' in params:
            idx = params.index('--exclude')
            if idx + 1 < len(params):
                exclude_patterns.append(params[idx + 1])

        if check_only:
            return self._check_clone_contents()
        else:
            return self._create_clone_package(export_path, exclude_patterns)

    def _show_help(self) -> str:
        """Show CLONE command help."""
        return """╔══════════════════════════════════════════════════════════╗
║           CLONE - USER CONTENT PACKAGING                ║
╚══════════════════════════════════════════════════════════╝

Collates unique local user content for system duplication.

USAGE:
  CLONE                      - Create full user content package
  CLONE --check              - Show what would be included
  CLONE --to <path>          - Export to specific location
  CLONE --exclude <pattern>  - Exclude file patterns
  CLONE HELP                 - Show this help

INCLUDED CONTENT:
  • memory/docs/             - User documentation
  • memory/drafts/           - Draft content
  • memory/ucode/scripts/    - Polished .upy scripts
  • memory/ucode/sandbox/    - Draft .upy scripts
  • memory/workflows/        - Mission workflows
  • memory/bank/user/        - User settings
  • memory/bank/private/     - Private transactions
  • memory/shared/public/    - Public content

EXCLUDED:
  • Logs and temporary files
  • .archive/ folders (use BACKUP for versioning)
  • System-generated files

OUTPUT:
  Creates timestamped .tar.gz package: udos-clone-YYYYMMDD_HHMMSS.tar.gz

EXAMPLES:
  CLONE                      # Package to current directory
  CLONE --check              # Preview contents
  CLONE --to ~/backups/      # Export to specific folder
  CLONE --exclude "*.log"    # Exclude log files

💡 Use BUILD to download external dependencies
💡 Use BACKUP for versioned file history
"""

    def _check_clone_contents(self) -> str:
        """Check what would be included in clone package."""
        result = "╔══════════════════════════════════════════════════════════╗\n"
        result += "║           CLONE CONTENTS PREVIEW                        ║\n"
        result += "╚══════════════════════════════════════════════════════════╝\n\n"

        total_size = 0
        total_files = 0

        for dir_path, description in self.user_content_dirs.items():
            path = Path(dir_path)
            if path.exists():
                file_count = sum(1 for _ in path.rglob('*') if _.is_file())
                size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                size_mb = size / (1024 * 1024)

                result += f"📁 {dir_path}\n"
                result += f"   {description}\n"
                result += f"   {file_count} files ({size_mb:.2f} MB)\n\n"

                total_files += file_count
                total_size += size
            else:
                result += f"⚠️  {dir_path}\n"
                result += f"   {description}\n"
                result += f"   Not found\n\n"

        result += "─" * 60 + "\n"
        result += f"📊 Total: {total_files} files ({total_size / (1024 * 1024):.2f} MB)\n\n"
        result += "💡 Run CLONE to create package\n"

        return result

    def _create_clone_package(self, export_path: Optional[Path] = None, exclude_patterns: List[str] = None) -> str:
        """Create clone package of user content."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        package_name = f"udos-clone-{timestamp}.tar.gz"

        if export_path:
            export_path.mkdir(parents=True, exist_ok=True)
            package_path = export_path / package_name
        else:
            package_path = Path(package_name)

        exclude_patterns = exclude_patterns or []
        exclude_patterns.extend(['*.log', '*.pyc', '__pycache__', '.DS_Store'])

        result = "╔══════════════════════════════════════════════════════════╗\n"
        result += "║           CREATING CLONE PACKAGE                        ║\n"
        result += "╚══════════════════════════════════════════════════════════╝\n\n"

        try:
            total_files = 0
            total_size = 0

            with tarfile.open(package_path, 'w:gz') as tar:
                # Add metadata
                metadata = {
                    'created': timestamp,
                    'version': 'v1.2.23',
                    'description': 'uDOS user content clone',
                    'directories': list(self.user_content_dirs.keys())
                }
                
                # Create temporary metadata file
                metadata_path = Path('clone_metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                tar.add(metadata_path, arcname='clone_metadata.json')
                metadata_path.unlink()

                # Add user content directories
                for dir_path in self.user_content_dirs.keys():
                    path = Path(dir_path)
                    if path.exists():
                        for file_path in path.rglob('*'):
                            if file_path.is_file():
                                # Check exclusions
                                if any(file_path.match(pattern) for pattern in exclude_patterns):
                                    continue
                                # Skip .archive/ folders
                                if '.archive' in file_path.parts:
                                    continue

                                tar.add(file_path, arcname=file_path)
                                total_files += 1
                                total_size += file_path.stat().st_size

            package_size = package_path.stat().st_size
            compression_ratio = (1 - package_size / total_size) * 100 if total_size > 0 else 0

            result += f"✅ Clone package created successfully\n\n"
            result += f"📦 Package: {package_path}\n"
            result += f"📊 Contents: {total_files} files ({total_size / (1024 * 1024):.2f} MB)\n"
            result += f"💾 Package size: {package_size / (1024 * 1024):.2f} MB\n"
            result += f"📉 Compression: {compression_ratio:.1f}%\n\n"
            result += f"💡 Extract with: tar -xzf {package_name}\n"

            return result

        except Exception as e:
            return f"❌ Clone package creation failed: {str(e)}"
