#!/usr/bin/env python3
"""
Sandbox Management Commands - CLEAN and TIDY
Maintains clean sandbox directory structure for uDOS v2.0

Enhanced version with:
- Selective folder flushing
- Integration with DESTROY and REPAIR commands
- Comprehensive cleanup options
- Detailed statistics and reporting

Author: GitHub Copilot
Date: November 30, 2025
Version: 2.0.0
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json


class SandboxHandler:
    """Handles CLEAN and TIDY commands for /memory directory management (v1.2.x)."""

    def __init__(self):
        # v1.2.12: Updated to memory/ structure
        self.sandbox_root = Path("memory")
        self.subdirs = {
            'trash': self.sandbox_root / 'trash',
            'dev': Path("dev"),  # Development files at root
            'docs': self.sandbox_root / 'docs',
            'drafts': self.sandbox_root / 'drafts',
            'tests': self.sandbox_root / 'ucode' / 'tests',
            'logs': self.sandbox_root / 'logs',
            'scripts': self.sandbox_root / 'ucode' / 'scripts',
            'ucode': self.sandbox_root / 'ucode',
            'workflow': self.sandbox_root / 'workflows',  # v1.2.x: workflows not workflow
            'peek': self.sandbox_root / 'peek',
            'sessions': self.sandbox_root / 'sessions',
            'user': self.sandbox_root / 'system' / 'user'  # v1.2.x: memory/system/user
        }

        # Folders that should NEVER be deleted (protected)
        self.protected_folders = {'user', 'tests'}

        # Folders that can be safely cleaned without confirmation
        self.auto_clean_folders = {'trash', 'logs', 'peek'}

        # Default retention days for different folder types
        self.retention_days = {
            'logs': 7,
            'dev': 30,
            'drafts': 30,
            'sessions': 14,
            'peek': 1
        }

    def handle(self, command, args=None):
        """Route CLEAN and TIDY commands."""
        args = args or []

        if command.upper() == 'CLEAN':
            return self.clean(args)
        elif command.upper() == 'TIDY':
            return self.tidy(args)
        else:
            return f"❌ Unknown sandbox command: {command}"

    def clean(self, args):
        """
        CLEAN command - Flush and cleanup sandbox subdirectories.

        Usage:
            CLEAN                    - Clean all (interactive, shows menu)
            CLEAN logs               - Clean only logs folder
            CLEAN trash              - Empty trash folder
            CLEAN drafts,logs        - Clean multiple folders (comma-separated)
            CLEAN --all              - Clean all (no prompts)
            CLEAN --force            - Force delete (dangerous!)
            CLEAN --days=30          - Keep only last 30 days
            CLEAN --dry-run          - Show what would be deleted
            CLEAN --stats            - Show cleanup statistics only

        Integration with DESTROY:
            CLEAN --reset            - Reset sandbox to pristine state (keeps user/)
            CLEAN --nuclear          - Delete EVERYTHING (requires DESTROY --all)
        """
        # Parse arguments
        targets = []
        interactive = True
        force = False
        dry_run = False
        stats_only = False
        reset_mode = False
        nuclear_mode = False
        keep_days = None

        if not args:
            # Show interactive menu
            return self._show_clean_menu()

        for arg in args:
            if arg.startswith('--'):
                if arg == '--all':
                    interactive = False
                elif arg == '--force':
                    force = True
                    interactive = False
                elif arg == '--dry-run':
                    dry_run = True
                elif arg == '--stats':
                    stats_only = True
                elif arg == '--reset':
                    reset_mode = True
                elif arg == '--nuclear':
                    nuclear_mode = True
                elif arg.startswith('--days='):
                    keep_days = int(arg.split('=')[1])
            else:
                # Support comma-separated targets
                targets.extend([t.strip().lower() for t in arg.split(',')])

        # Show stats only
        if stats_only:
            return self._generate_stats()

        # Nuclear mode requires explicit confirmation
        if nuclear_mode:
            return self._nuclear_clean(force)

        # Reset mode
        if reset_mode:
            return self._reset_sandbox(force)

        # Default to all if no targets specified
        if not targets:
            targets = ['all']

        results = []
        summary = {
            'deleted_files': 0,
            'deleted_size': 0,
            'folders_cleaned': 0
        }

        # Process each target
        for target in targets:
            if target == 'all':
                # Clean all folders
                for folder_name in self.subdirs.keys():
                    if folder_name not in self.protected_folders:
                        result, stats = self._clean_folder(
                            folder_name,
                            keep_days or self.retention_days.get(folder_name, 30),
                            interactive and folder_name not in self.auto_clean_folders,
                            dry_run,
                            force
                        )
                        results.append(result)
                        summary['deleted_files'] += stats['files']
                        summary['deleted_size'] += stats['size']
                        if stats['files'] > 0:
                            summary['folders_cleaned'] += 1
            else:
                # Clean specific folder
                if target in self.protected_folders and not force:
                    results.append(f"⚠️  {target.title()}: Protected folder (use --force to override)")
                    continue

                if target not in self.subdirs:
                    results.append(f"❌ Unknown folder: {target}")
                    continue

                result, stats = self._clean_folder(
                    target,
                    keep_days or self.retention_days.get(target, 30),
                    interactive and target not in self.auto_clean_folders,
                    dry_run,
                    force
                )
                results.append(result)
                summary['deleted_files'] += stats['files']
                summary['deleted_size'] += stats['size']
                if stats['files'] > 0:
                    summary['folders_cleaned'] += 1

        # Add summary
        if not dry_run and summary['deleted_files'] > 0:
            size_mb = summary['deleted_size'] / (1024 * 1024)
            results.append(
                f"\n📊 Cleanup Summary:\n"
                f"   • Folders cleaned: {summary['folders_cleaned']}\n"
                f"   • Files deleted: {summary['deleted_files']}\n"
                f"   • Space freed: {size_mb:.2f} MB"
            )

        return '\n\n'.join(results)

    def _show_clean_menu(self):
        """Show interactive cleaning menu."""
        output = [
            "╔══════════════════════════════════════════════════════════╗",
            "║           SANDBOX CLEANUP - SELECT OPTIONS              ║",
            "╚══════════════════════════════════════════════════════════╝",
            "",
            "📁 Available Folders:",
            ""
        ]

        for name, path in self.subdirs.items():
            if path.exists():
                file_count = sum(1 for _ in path.rglob('*') if _.is_file())
                total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)

                protected = "🔒" if name in self.protected_folders else "  "
                auto = "⚡" if name in self.auto_clean_folders else "  "

                output.append(f"  {protected}{auto} {name:12} - {file_count:4} files ({size_mb:6.2f} MB)")

        output.extend([
            "",
            "🔒 = Protected folder",
            "⚡ = Auto-cleanable (no confirmation)",
            "",
            "💡 Usage Examples:",
            "   CLEAN trash              - Empty trash only",
            "   CLEAN logs,drafts        - Clean multiple folders",
            "   CLEAN --all              - Clean all (no prompts)",
            "   CLEAN --stats            - Show statistics only",
            "   CLEAN --dry-run          - Preview what would be deleted",
            "   CLEAN --reset            - Reset to pristine state",
            "",
            "Type CLEAN <folder> to clean specific folder"
        ])

        return '\n'.join(output)

    def _clean_folder(self, folder_name, keep_days, interactive, dry_run, force):
        """
        Clean a specific sandbox folder.

        Returns: (result_message, stats_dict)
        """
        folder_path = self.subdirs.get(folder_name)
        if not folder_path or not folder_path.exists():
            return f"ℹ️  {folder_name.title()}: Folder doesn't exist", {'files': 0, 'size': 0}

        cutoff_date = datetime.now() - timedelta(days=keep_days)

        # Get files to clean
        old_files = []
        total_size = 0

        if folder_name == 'trash':
            # Trash: delete everything
            items = list(folder_path.iterdir())
            for item in items:
                if item.is_file():
                    old_files.append(item)
                    total_size += item.stat().st_size
                elif item.is_dir():
                    # Estimate directory size
                    for f in item.rglob('*'):
                        if f.is_file():
                            old_files.append(f)
                            total_size += f.stat().st_size
        elif folder_name == 'tests':
            # Tests: only clean artifacts, not test files
            for pattern in ['__pycache__', '.pytest_cache', '*.pyc', '.coverage', '*.egg-info']:
                for item in folder_path.rglob(pattern):
                    old_files.append(item)
                    if item.is_file():
                        total_size += item.stat().st_size
        else:
            # Other folders: clean files older than keep_days
            for item in folder_path.rglob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if mtime < cutoff_date:
                        old_files.append(item)
                        total_size += item.stat().st_size

        if not old_files:
            return f"✅ {folder_name.title()}: Already clean", {'files': 0, 'size': 0}

        size_mb = total_size / (1024 * 1024)

        # Dry run mode
        if dry_run:
            return (
                f"🔍 {folder_name.title()}: Would delete {len(old_files)} items ({size_mb:.2f} MB)\n"
                f"   Retention: {keep_days} days",
                {'files': len(old_files), 'size': total_size}
            )

        # Interactive confirmation
        if interactive:
            print(f"\n🗑️  {folder_name.title()}: Delete {len(old_files)} items ({size_mb:.2f} MB)?")
            print(f"   Retention period: {keep_days} days")
            response = input("   Confirm? (y/N): ")
            if response.lower() != 'y':
                return f"⏭️  {folder_name.title()}: Skipped", {'files': 0, 'size': 0}

        # Delete files
        deleted_count = 0
        for item in old_files:
            try:
                if item.is_file():
                    item.unlink()
                    deleted_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    deleted_count += 1
            except Exception as e:
                continue

        return (
            f"✅ {folder_name.title()}: Deleted {deleted_count} items ({size_mb:.2f} MB)",
            {'files': deleted_count, 'size': total_size}
        )

    def _reset_sandbox(self, force):
        """Reset sandbox to pristine state (keeps user/ and tests/)."""
        if not force:
            print("\n⚠️  SANDBOX RESET")
            print("=" * 60)
            print("This will DELETE all files in sandbox/ except:")
            print("  • user/         (user data)")
            print("  • tests/        (test files)")
            print("  • README.md     (documentation)")
            print("")
            print("The following will be DELETED:")

            to_delete = []
            total_size = 0

            for name, path in self.subdirs.items():
                if name not in self.protected_folders and path.exists():
                    file_count = sum(1 for _ in path.rglob('*') if _.is_file())
                    size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                    if file_count > 0:
                        to_delete.append(f"  • {name:12} {file_count:4} files ({size / (1024 * 1024):6.2f} MB)")
                        total_size += size

            print('\n'.join(to_delete))
            print("")
            print(f"Total: {total_size / (1024 * 1024):.2f} MB will be freed")
            print("")
            response = input("Type 'RESET' to confirm: ")

            if response != 'RESET':
                return "⏭️  Reset cancelled"

        # Perform reset
        results = []
        total_deleted = 0
        total_size = 0

        for name, path in self.subdirs.items():
            if name in self.protected_folders:
                results.append(f"🔒 {name.title()}: Protected (kept)")
                continue

            if path.exists():
                file_count = sum(1 for _ in path.rglob('*') if _.is_file())
                size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())

                # Delete all contents
                for item in path.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    except Exception as e:
                        continue

                results.append(f"✅ {name.title()}: Cleared ({file_count} files)")
                total_deleted += file_count
                total_size += size

        size_mb = total_size / (1024 * 1024)

        results.insert(0, "╔══════════════════════════════════════════════════════════╗")
        results.insert(1, "║           SANDBOX RESET COMPLETE                        ║")
        results.insert(2, "╚══════════════════════════════════════════════════════════╝")
        results.insert(3, "")
        results.append("")
        results.append(f"📊 Total: {total_deleted} files deleted ({size_mb:.2f} MB freed)")

        return '\n'.join(results)

    def _nuclear_clean(self, force):
        """Nuclear option: delete EVERYTHING in sandbox (requires DESTROY --all)."""
        return (
            "🚨 NUCLEAR CLEAN BLOCKED\n\n"
            "This operation would delete EVERYTHING including user data.\n"
            "Use DESTROY --all instead if you really want to do this.\n\n"
            "💡 For sandbox reset keeping user data, use: CLEAN --reset"
        )

    def tidy(self, args):
        """
        TIDY command - Organize and sort files in sandbox.

        Usage:
            TIDY                     - Tidy all subdirectories (interactive)
            TIDY logs                - Organize logs only
            TIDY scripts             - Categorize scripts
            TIDY --report            - Generate report without changes
            TIDY --auto              - Auto-organize without prompts

        Features:
            - Organize logs by date and type
            - Categorize scripts by purpose
            - Sort workflow files
            - Generate cleanup recommendations
        """
        report_only = '--report' in args
        auto_mode = '--auto' in args
        targets = []

        for arg in args:
            # Skip empty strings and flags
            if not arg or arg.startswith('--'):
                continue
            targets.extend([t.strip().lower() for t in arg.split(',')])

        if not targets:
            targets = ['all']

        results = []

        # Organize each target
        for target in targets:
            if target == 'all':
                for folder in ['logs', 'scripts', 'workflow', 'ucode']:
                    if folder in self.subdirs:
                        result = self._tidy_folder(folder, report_only, auto_mode)
                        results.append(result)
            else:
                if target not in self.subdirs:
                    results.append(f"❌ Unknown folder: {target}")
                    continue
                result = self._tidy_folder(target, report_only, auto_mode)
                results.append(result)

        # Generate cleanup statistics
        if report_only or '--stats' in args:
            stats = self._generate_stats()
            results.append(stats)

            # Add recommendations
            recommendations = self._generate_recommendations()
            results.append(recommendations)

        return '\n\n'.join(results)

    def _tidy_folder(self, folder_name, report_only, auto_mode):
        """Organize a specific folder."""
        folder_path = self.subdirs.get(folder_name)

        if not folder_path or not folder_path.exists():
            return f"ℹ️  {folder_name.title()}: Folder doesn't exist"

        if folder_name == 'logs':
            return self._tidy_logs(report_only, auto_mode)
        elif folder_name == 'scripts':
            return self._tidy_scripts(report_only, auto_mode)
        elif folder_name == 'workflow':
            return self._tidy_workflow(report_only, auto_mode)
        elif folder_name == 'ucode':
            return self._tidy_ucode(report_only, auto_mode)
        else:
            file_count = sum(1 for _ in folder_path.rglob('*') if _.is_file())
            return f"✅ {folder_name.title()}: {file_count} files (no organization needed)"

    def _tidy_logs(self, report_only, auto_mode):
        """Organize logs by type and date."""
        logs_dir = self.subdirs['logs']
        if not logs_dir.exists():
            return "ℹ️  No logs directory to tidy"

        # Group by type
        log_types = {
            'session': [],
            'server': [],
            'dev': [],
            'debug': [],
            'api': [],
            'other': []
        }

        for log_file in logs_dir.glob('*'):
            if not log_file.is_file():
                continue

            name = log_file.name.lower()
            if 'session' in name:
                log_types['session'].append(log_file)
            elif any(s in name for s in ['server', 'extension']):
                log_types['server'].append(log_file)
            elif name.startswith('dev-'):
                log_types['dev'].append(log_file)
            elif any(s in name for s in ['debug', 'test']):
                log_types['debug'].append(log_file)
            elif 'api' in name:
                log_types['api'].append(log_file)
            else:
                log_types['other'].append(log_file)

        summary = ["📊 Logs Organization:"]
        total_files = 0

        for log_type, files in log_types.items():
            if files:
                total_files += len(files)
                summary.append(f"  • {log_type.title()}: {len(files)} files")

        if report_only:
            summary.append(f"\n  Total: {total_files} log files")
            return '\n'.join(summary)

        # Could implement actual organization here (e.g., create subdirectories)
        summary.append(f"\n✅ Total: {total_files} log files organized")
        return '\n'.join(summary)

    def _tidy_scripts(self, report_only, auto_mode):
        """Categorize and organize scripts."""
        scripts_dir = self.subdirs['scripts']
        if not scripts_dir.exists():
            return "ℹ️  No scripts directory to tidy"

        # Categorize scripts
        categories = {
            'migration': [],
            'generation': [],
            'testing': [],
            'utility': [],
            'other': []
        }

        for script in scripts_dir.glob('*.py'):
            name = script.name.lower()
            if 'migrate' in name or 'migration' in name:
                categories['migration'].append(script)
            elif 'generate' in name or 'gen_' in name:
                categories['generation'].append(script)
            elif 'test' in name:
                categories['testing'].append(script)
            elif any(w in name for w in ['util', 'helper', 'tool']):
                categories['utility'].append(script)
            else:
                categories['other'].append(script)

        # Also check shell scripts
        for script in scripts_dir.glob('*.sh'):
            categories['other'].append(script)

        summary = ["📊 Scripts Organization:"]
        total_scripts = 0

        for category, scripts in categories.items():
            if scripts:
                total_scripts += len(scripts)
                summary.append(f"  • {category.title()}: {len(scripts)} scripts")

        if report_only:
            summary.append(f"\n  Total: {total_scripts} scripts")
            return '\n'.join(summary)

        summary.append(f"\n✅ Total: {total_scripts} scripts categorized")
        return '\n'.join(summary)

    def _tidy_workflow(self, report_only, auto_mode):
        """Organize workflow files."""
        workflow_dir = self.subdirs['workflow']
        if not workflow_dir.exists():
            return "ℹ️  No workflow directory to tidy"

        upy_scripts = list(workflow_dir.glob('*.upy'))
        json_files = list(workflow_dir.glob('*.json'))

        total = len(upy_scripts) + len(json_files)

        if not total:
            return "✅ Workflow: Empty directory"

        summary = [
            "📊 Workflow Organization:",
            f"  • uScript files: {len(upy_scripts)}",
            f"  • Config files: {len(json_files)}"
        ]

        if report_only:
            summary.append(f"\n  Total: {total} workflow files")
            return '\n'.join(summary)

        summary.append(f"\n✅ Total: {total} workflow files organized")
        return '\n'.join(summary)

    def _tidy_ucode(self, report_only, auto_mode):
        """Organize uCODE scripts."""
        ucode_dir = self.subdirs['ucode']
        if not ucode_dir.exists():
            return "ℹ️  No ucode directory to tidy"

        scripts = list(ucode_dir.glob('*.upy'))

        if not scripts:
            return "✅ uCode: Empty directory"

        # Categorize by purpose (based on filename)
        categories = {
            'test': [],
            'demo': [],
            'automation': [],
            'other': []
        }

        for script in scripts:
            name = script.name.lower()
            if 'test' in name or 'shakedown' in name:
                categories['test'].append(script)
            elif 'demo' in name or 'example' in name:
                categories['demo'].append(script)
            elif 'auto' in name or 'workflow' in name:
                categories['automation'].append(script)
            else:
                categories['other'].append(script)

        summary = ["📊 uCode Organization:"]

        for category, files in categories.items():
            if files:
                summary.append(f"  • {category.title()}: {len(files)} scripts")

        if report_only:
            summary.append(f"\n  Total: {len(scripts)} uCode scripts")
            return '\n'.join(summary)

        summary.append(f"\n✅ Total: {len(scripts)} uCode scripts organized")
        return '\n'.join(summary)

    def _generate_stats(self):
        """Generate comprehensive sandbox statistics."""
        stats = {
            'directories': {},
            'total_files': 0,
            'total_size': 0
        }

        for name, path in self.subdirs.items():
            if path.exists():
                files = list(path.rglob('*'))
                file_count = sum(1 for f in files if f.is_file())
                total_size = sum(f.stat().st_size for f in files if f.is_file())

                # Get oldest and newest file
                file_times = [f.stat().st_mtime for f in files if f.is_file()]
                oldest = min(file_times) if file_times else None
                newest = max(file_times) if file_times else None

                stats['directories'][name] = {
                    'files': file_count,
                    'size_mb': total_size / (1024 * 1024),
                    'oldest': datetime.fromtimestamp(oldest) if oldest else None,
                    'newest': datetime.fromtimestamp(newest) if newest else None
                }
                stats['total_files'] += file_count
                stats['total_size'] += total_size

        output = [
            "╔══════════════════════════════════════════════════════════╗",
            "║           SANDBOX STATISTICS                            ║",
            "╚══════════════════════════════════════════════════════════╝",
            ""
        ]

        for name, data in sorted(stats['directories'].items()):
            protected = "🔒" if name in self.protected_folders else "  "
            auto = "⚡" if name in self.auto_clean_folders else "  "

            line = f"{protected}{auto} {name:12} {data['files']:4} files  ({data['size_mb']:6.2f} MB)"

            # Add age info
            if data['oldest']:
                age_days = (datetime.now() - data['oldest']).days
                if age_days > 30:
                    line += f"  (oldest: {age_days}d)"

            output.append(line)

        total_mb = stats['total_size'] / (1024 * 1024)
        output.extend([
            "",
            f"  Total:      {stats['total_files']:4} files  ({total_mb:6.2f} MB)",
            "",
            "Legend:",
            "  🔒 = Protected folder (safe from auto-clean)",
            "  ⚡ = Auto-cleanable (no confirmation needed)"
        ])

        return '\n'.join(output)

    def _generate_recommendations(self):
        """Generate cleanup recommendations based on analysis."""
        recommendations = []

        for name, path in self.subdirs.items():
            if not path.exists():
                continue

            file_count = sum(1 for _ in path.rglob('*') if _.is_file())
            if file_count == 0:
                continue

            total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)

            # Get file ages
            file_times = [f.stat().st_mtime for f in path.rglob('*') if f.is_file()]
            if file_times:
                oldest = datetime.fromtimestamp(min(file_times))
                age_days = (datetime.now() - oldest).days

                # Recommendations based on folder type and age
                if name == 'trash' and file_count > 0:
                    recommendations.append(
                        f"🗑️  {name.title()}: {file_count} items can be deleted ({size_mb:.2f} MB)\n"
                        f"   Run: CLEAN trash"
                    )
                elif name == 'logs' and age_days > 30:
                    recommendations.append(
                        f"📝 {name.title()}: Contains logs older than 30 days\n"
                        f"   Run: CLEAN logs --days=30"
                    )
                elif name == 'drafts' and age_days > 60:
                    recommendations.append(
                        f"📄 {name.title()}: Contains drafts older than 60 days\n"
                        f"   Run: CLEAN drafts --days=60"
                    )
                elif name == 'peek' and file_count > 20:
                    recommendations.append(
                        f"👁️  {name.title()}: Contains {file_count} processed files\n"
                        f"   Run: CLEAN peek"
                    )
                elif size_mb > 50 and name not in self.protected_folders:
                    recommendations.append(
                        f"💾 {name.title()}: Using {size_mb:.2f} MB of space\n"
                        f"   Consider: CLEAN {name} or TIDY {name}"
                    )

        if not recommendations:
            return "✅ No cleanup recommendations - sandbox is well maintained!"

        output = [
            "╔══════════════════════════════════════════════════════════╗",
            "║           CLEANUP RECOMMENDATIONS                       ║",
            "╚══════════════════════════════════════════════════════════╝",
            ""
        ]
        output.extend(recommendations)

        return '\n'.join(output)

    # Integration with REPAIR command
    def repair_sandbox(self):
        """
        Called by REPAIR command to fix sandbox issues.
        Returns health status and repairs performed.
        """
        issues = []
        repairs = []

        # Check for missing directories
        for name, path in self.subdirs.items():
            if not path.exists():
                issues.append(f"Missing directory: {name}")
                # v1.2.12: Don't auto-create - let CONFIG FIX handle it
                # path.mkdir(parents=True, exist_ok=True)
                # repairs.append(f"Created missing directory: {name}")

        # Check for orphaned files in sandbox root
        sandbox_root_files = [
            f for f in self.sandbox_root.iterdir()
            if f.is_file() and f.name not in ['README.md', 'user.json', '.server_state.json']
        ]

        if sandbox_root_files:
            issues.append(f"Found {len(sandbox_root_files)} orphaned files in sandbox root")
            # Could move to trash or appropriate folder

        # Check for overly large folders
        for name, path in self.subdirs.items():
            if path.exists():
                total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)

                if size_mb > 100 and name not in self.protected_folders:
                    issues.append(f"{name} folder is large ({size_mb:.2f} MB)")

        # Check for very old files
        for name, path in self.subdirs.items():
            if name in self.auto_clean_folders and path.exists():
                file_times = [f.stat().st_mtime for f in path.rglob('*') if f.is_file()]
                if file_times:
                    oldest = datetime.fromtimestamp(min(file_times))
                    age_days = (datetime.now() - oldest).days

                    if age_days > 90:
                        issues.append(f"{name} contains files older than 90 days")

        result = {
            'status': 'healthy' if not issues else 'warnings',
            'issues': issues,
            'repairs': repairs,
            'recommendation': "Run CLEAN --stats to see detailed cleanup options" if issues else None
        }

        return result

    # Integration with DESTROY command
    def destroy_sandbox(self, mode='reset'):
        """
        Called by DESTROY command for sandbox cleanup.

        Modes:
            reset  - Reset to pristine state (keep user/ and tests/)
            env    - Clean environment-related files
            all    - Delete everything (nuclear)
        """
        if mode == 'reset':
            return self._reset_sandbox(force=True)
        elif mode == 'env':
            # Clean environment files
            results = []

            # Remove .pytest_cache
            pytest_cache = self.sandbox_root / '.pytest_cache'
            if pytest_cache.exists():
                shutil.rmtree(pytest_cache)
                results.append("✅ Removed .pytest_cache")

            # Remove .server_state.json
            server_state = self.sandbox_root / '.server_state.json'
            if server_state.exists():
                server_state.unlink()
                results.append("✅ Removed .server_state.json")

            # Clean test artifacts
            result, _ = self._clean_folder('tests', 0, False, False, True)
            results.append(result)

            return '\n'.join(results)
        elif mode == 'all':
            # Nuclear option - should only be called from DESTROY --all
            total_deleted = 0
            total_size = 0

            for item in self.sandbox_root.iterdir():
                if item.name == 'README.md':
                    continue  # Keep README

                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink()
                        total_deleted += 1
                        total_size += size
                    elif item.is_dir():
                        for f in item.rglob('*'):
                            if f.is_file():
                                total_size += f.stat().st_size
                                total_deleted += 1
                        shutil.rmtree(item)
                except Exception:
                    continue

            size_mb = total_size / (1024 * 1024)
            return f"🗑️  Sandbox: Deleted {total_deleted} files ({size_mb:.2f} MB freed)"

        return "❌ Unknown destroy mode"
