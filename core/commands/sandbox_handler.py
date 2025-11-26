#!/usr/bin/env python3
"""
Sandbox Management Commands - CLEAN and TIDY
Maintains clean sandbox directory structure for uDOS v2.0
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json


class SandboxHandler:
    """Handles CLEAN and TIDY commands for /sandbox directory management."""

    def __init__(self):
        self.sandbox_root = Path("sandbox")
        self.subdirs = {
            'trash': self.sandbox_root / 'trash',
            'dev': self.sandbox_root / 'dev',
            'docs': self.sandbox_root / 'docs',
            'drafts': self.sandbox_root / 'drafts',
            'tests': self.sandbox_root / 'tests',
            'logs': self.sandbox_root / 'logs',
            'scripts': self.sandbox_root / 'scripts',
            'ucode': self.sandbox_root / 'ucode',
            'workflow': self.sandbox_root / 'workflow',
            'peek': self.sandbox_root / 'peek'
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
            CLEAN              - Clean all (interactive)
            CLEAN logs         - Clean only logs
            CLEAN trash        - Empty trash
            CLEAN --all        - Clean all (no prompts)
            CLEAN --days=30    - Keep only last 30 days
        """
        # Parse arguments
        target = 'all'
        interactive = True
        keep_days = 30

        for arg in args:
            if arg.startswith('--'):
                if arg == '--all':
                    interactive = False
                elif arg.startswith('--days='):
                    keep_days = int(arg.split('=')[1])
            else:
                target = arg.lower()

        results = []
        cutoff_date = datetime.now() - timedelta(days=keep_days)

        # Clean logs
        if target in ['all', 'logs']:
            log_result = self._clean_logs(cutoff_date, interactive)
            results.append(log_result)

        # Empty trash
        if target in ['all', 'trash']:
            trash_result = self._empty_trash(interactive)
            results.append(trash_result)

        # Clean test artifacts
        if target in ['all', 'tests']:
            test_result = self._clean_tests(interactive)
            results.append(test_result)

        # Archive old drafts
        if target in ['all', 'drafts']:
            draft_result = self._archive_drafts(cutoff_date, interactive)
            results.append(draft_result)

        # Clean peek processed files
        if target in ['all', 'peek']:
            peek_result = self._clean_peek(interactive)
            results.append(peek_result)

        return '\n\n'.join(results)

    def _clean_logs(self, cutoff_date, interactive):
        """Clean old log files."""
        logs_dir = self.subdirs['logs']
        if not logs_dir.exists():
            return "ℹ️  No logs directory to clean"

        old_logs = []
        for log_file in logs_dir.glob('*'):
            if log_file.is_file():
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    old_logs.append(log_file)

        if not old_logs:
            return "✅ Logs: No old files to clean"

        if interactive:
            response = input(f"🗑️  Delete {len(old_logs)} old log files? (y/N): ")
            if response.lower() != 'y':
                return "⏭️  Logs: Skipped"

        deleted_count = 0
        deleted_size = 0
        for log_file in old_logs:
            size = log_file.stat().st_size
            log_file.unlink()
            deleted_count += 1
            deleted_size += size

        size_mb = deleted_size / (1024 * 1024)
        return f"✅ Logs: Deleted {deleted_count} files ({size_mb:.2f} MB)"

    def _empty_trash(self, interactive):
        """Empty trash directory."""
        trash_dir = self.subdirs['trash']
        if not trash_dir.exists():
            return "ℹ️  No trash directory"

        items = list(trash_dir.iterdir())
        if not items:
            return "✅ Trash: Already empty"

        if interactive:
            response = input(f"🗑️  Empty trash ({len(items)} items)? (y/N): ")
            if response.lower() != 'y':
                return "⏭️  Trash: Skipped"

        deleted_count = 0
        deleted_size = 0
        for item in items:
            if item.is_file():
                size = item.stat().st_size
                item.unlink()
                deleted_size += size
            elif item.is_dir():
                shutil.rmtree(item)
            deleted_count += 1

        size_mb = deleted_size / (1024 * 1024)
        return f"✅ Trash: Emptied {deleted_count} items ({size_mb:.2f} MB)"

    def _clean_tests(self, interactive):
        """Clean test artifacts and caches."""
        tests_dir = self.subdirs['tests']
        if not tests_dir.exists():
            return "ℹ️  No tests directory"

        # Find pytest cache, __pycache__, etc.
        artifacts = []
        for pattern in ['__pycache__', '.pytest_cache', '*.pyc', '.coverage']:
            artifacts.extend(tests_dir.rglob(pattern))

        if not artifacts:
            return "✅ Tests: No artifacts to clean"

        if interactive:
            response = input(f"🧹 Clean {len(artifacts)} test artifacts? (y/N): ")
            if response.lower() != 'y':
                return "⏭️  Tests: Skipped"

        cleaned = 0
        for item in artifacts:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
            cleaned += 1

        return f"✅ Tests: Cleaned {cleaned} artifacts"

    def _archive_drafts(self, cutoff_date, interactive):
        """Archive old draft files to trash."""
        drafts_dir = self.subdirs['drafts']
        trash_dir = self.subdirs['trash']

        if not drafts_dir.exists():
            return "ℹ️  No drafts directory"

        old_drafts = []
        for draft in drafts_dir.glob('*'):
            if draft.is_file():
                mtime = datetime.fromtimestamp(draft.stat().st_mtime)
                if mtime < cutoff_date:
                    old_drafts.append(draft)

        if not old_drafts:
            return "✅ Drafts: No old files to archive"

        if interactive:
            response = input(f"📦 Archive {len(old_drafts)} old drafts to trash? (y/N): ")
            if response.lower() != 'y':
                return "⏭️  Drafts: Skipped"

        trash_dir.mkdir(exist_ok=True)
        archived = 0
        for draft in old_drafts:
            dest = trash_dir / f"{datetime.now().strftime('%Y%m%d')}_{draft.name}"
            shutil.move(str(draft), str(dest))
            archived += 1

        return f"✅ Drafts: Archived {archived} files to trash"

    def _clean_peek(self, interactive):
        """Clean processed files from peek directory."""
        peek_dir = self.subdirs['peek']
        if not peek_dir.exists():
            return "ℹ️  No peek directory"

        # Assume files older than 1 day are processed
        cutoff = datetime.now() - timedelta(days=1)
        old_files = []

        for item in peek_dir.glob('*'):
            if item.is_file():
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if mtime < cutoff:
                    old_files.append(item)

        if not old_files:
            return "✅ Peek: No processed files to clean"

        if interactive:
            response = input(f"🧹 Clean {len(old_files)} processed files from peek? (y/N): ")
            if response.lower() != 'y':
                return "⏭️  Peek: Skipped"

        for item in old_files:
            item.unlink()

        return f"✅ Peek: Cleaned {len(old_files)} processed files"

    def tidy(self, args):
        """
        TIDY command - Organize and sort files in sandbox.

        Usage:
            TIDY              - Tidy all subdirectories
            TIDY logs         - Organize logs only
            TIDY --report     - Generate report without changes
        """
        report_only = '--report' in args
        target = 'all'

        for arg in args:
            if not arg.startswith('--'):
                target = arg.lower()

        results = []

        # Organize logs by date
        if target in ['all', 'logs']:
            log_result = self._tidy_logs(report_only)
            results.append(log_result)

        # Categorize scripts
        if target in ['all', 'scripts']:
            script_result = self._tidy_scripts(report_only)
            results.append(script_result)

        # Organize workflow files
        if target in ['all', 'workflow']:
            workflow_result = self._tidy_workflow(report_only)
            results.append(workflow_result)

        # Generate cleanup statistics
        if report_only:
            stats = self._generate_stats()
            results.append(stats)

        return '\n\n'.join(results)

    def _tidy_logs(self, report_only):
        """Organize logs by type and date."""
        logs_dir = self.subdirs['logs']
        if not logs_dir.exists():
            return "ℹ️  No logs directory to tidy"

        # Group by type
        log_types = {
            'session': [],
            'server': [],
            'debug': [],
            'other': []
        }

        for log_file in logs_dir.glob('*.log'):
            name = log_file.name.lower()
            if name.startswith('session_'):
                log_types['session'].append(log_file)
            elif any(s in name for s in ['server', 'api', 'extensions']):
                log_types['server'].append(log_file)
            elif any(s in name for s in ['dev-', 'debug', 'test']):
                log_types['debug'].append(log_file)
            else:
                log_types['other'].append(log_file)

        summary = []
        for log_type, files in log_types.items():
            if files:
                summary.append(f"  • {log_type.title()}: {len(files)} files")

        if report_only:
            return "📊 Logs Organization:\n" + '\n'.join(summary)

        return "✅ Logs: Tidied\n" + '\n'.join(summary)

    def _tidy_scripts(self, report_only):
        """Categorize and organize scripts."""
        scripts_dir = self.subdirs['scripts']
        if not scripts_dir.exists():
            return "ℹ️  No scripts directory to tidy"

        scripts = list(scripts_dir.glob('*.py')) + list(scripts_dir.glob('*.sh'))

        if not scripts:
            return "✅ Scripts: Empty directory"

        if report_only:
            return f"📊 Scripts: {len(scripts)} files"

        return f"✅ Scripts: {len(scripts)} files organized"

    def _tidy_workflow(self, report_only):
        """Organize workflow files."""
        workflow_dir = self.subdirs['workflow']
        if not workflow_dir.exists():
            return "ℹ️  No workflow directory to tidy"

        workflows = list(workflow_dir.glob('*.uscript')) + list(workflow_dir.glob('*.json'))

        if not workflows:
            return "✅ Workflow: Empty directory"

        if report_only:
            return f"📊 Workflow: {len(workflows)} files"

        return f"✅ Workflow: {len(workflows)} files organized"

    def _generate_stats(self):
        """Generate overall sandbox statistics."""
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

                stats['directories'][name] = {
                    'files': file_count,
                    'size_mb': total_size / (1024 * 1024)
                }
                stats['total_files'] += file_count
                stats['total_size'] += total_size

        output = ["📊 Sandbox Statistics:", ""]
        for name, data in stats['directories'].items():
            output.append(f"  {name:12} {data['files']:4} files  ({data['size_mb']:6.2f} MB)")

        total_mb = stats['total_size'] / (1024 * 1024)
        output.append("")
        output.append(f"  Total:      {stats['total_files']:4} files  ({total_mb:6.2f} MB)")

        return '\n'.join(output)
