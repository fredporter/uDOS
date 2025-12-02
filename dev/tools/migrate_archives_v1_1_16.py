#!/usr/bin/env python3
"""
uDOS v1.1.16 - Archive System Migration Script

Migrates existing archive folders to new .archive/ structure:
- memory/system/archived/* → memory/workflows/missions/.archive/completed/
- memory/system/backup/* → memory/system/user/.archive/backups/
- memory/workflows/.archive/archived/* → memory/workflows/missions/.archive/completed/

Usage:
    python dev/tools/migrate_archives_v1_1_16.py [--dry-run] [--verbose]
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


class ArchiveMigration:
    """Handles migration of legacy archive folders to v1.1.16 structure."""

    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.migrations = []
        self.errors = []

    def log(self, message):
        """Log message if verbose mode."""
        if self.verbose:
            print(f"  {message}")

    def migrate_system_archived(self):
        """Migrate memory/system/archived/* to memory/workflows/missions/.archive/completed/"""
        source = Path("memory/system/archived")
        dest = Path("memory/workflows/missions/.archive/completed")

        if not source.exists():
            self.log("No memory/system/archived/ found - skipping")
            return

        print(f"\n📦 Migrating: {source} → {dest}")

        if not self.dry_run:
            dest.mkdir(parents=True, exist_ok=True)

        # Move all mission folders
        for item in source.glob("missions/*"):
            if item.is_dir():
                dest_path = dest / item.name
                if self.dry_run:
                    print(f"  [DRY RUN] Would move: {item.name}")
                else:
                    try:
                        shutil.move(str(item), str(dest_path))
                        self.migrations.append((item, dest_path))
                        print(f"  ✅ Moved: {item.name}")
                    except Exception as e:
                        self.errors.append((item, str(e)))
                        print(f"  ❌ Error moving {item.name}: {e}")

        # Handle workflow archives
        workflow_source = source / "workflows"
        workflow_dest = Path("memory/workflows/.archive/completed")

        if workflow_source.exists():
            if not self.dry_run:
                workflow_dest.mkdir(parents=True, exist_ok=True)

            for item in workflow_source.iterdir():
                if item.is_dir():
                    dest_path = workflow_dest / item.name
                    if self.dry_run:
                        print(f"  [DRY RUN] Would move: workflows/{item.name}")
                    else:
                        try:
                            shutil.move(str(item), str(dest_path))
                            self.migrations.append((item, dest_path))
                            print(f"  ✅ Moved: workflows/{item.name}")
                        except Exception as e:
                            self.errors.append((item, str(e)))
                            print(f"  ❌ Error moving workflows/{item.name}: {e}")

    def migrate_system_backup(self):
        """Migrate memory/system/backup/* to memory/system/user/.archive/backups/"""
        source = Path("memory/system/backup")
        dest = Path("memory/system/user/.archive/backups")

        if not source.exists():
            self.log("No memory/system/backup/ found - skipping")
            return

        print(f"\n💾 Migrating: {source} → {dest}")

        if not self.dry_run:
            dest.mkdir(parents=True, exist_ok=True)

        # Move all backup files
        for item in source.iterdir():
            if item.is_file():
                dest_path = dest / item.name
                if self.dry_run:
                    print(f"  [DRY RUN] Would move: {item.name}")
                else:
                    try:
                        shutil.move(str(item), str(dest_path))
                        self.migrations.append((item, dest_path))
                        print(f"  ✅ Moved: {item.name}")
                    except Exception as e:
                        self.errors.append((item, str(e)))
                        print(f"  ❌ Error moving {item.name}: {e}")

    def migrate_workflows_archived(self):
        """Migrate memory/workflows/.archive/archived/* to completed/"""
        source = Path("memory/workflows/.archive/archived")
        dest = Path("memory/workflows/.archive/completed")

        if not source.exists():
            self.log("No memory/workflows/.archive/archived/ found - skipping")
            return

        print(f"\n📋 Migrating: {source} → {dest}")

        if not self.dry_run:
            dest.mkdir(parents=True, exist_ok=True)

        # Move all archived items
        for item in source.iterdir():
            dest_path = dest / item.name
            if self.dry_run:
                print(f"  [DRY RUN] Would move: {item.name}")
            else:
                try:
                    if item.is_dir():
                        shutil.move(str(item), str(dest_path))
                    else:
                        shutil.copy2(str(item), str(dest_path))
                    self.migrations.append((item, dest_path))
                    print(f"  ✅ Moved: {item.name}")
                except Exception as e:
                    self.errors.append((item, str(e)))
                    print(f"  ❌ Error moving {item.name}: {e}")

    def cleanup_old_folders(self):
        """Remove empty old archive folders."""
        folders_to_check = [
            Path("memory/system/archived"),
            Path("memory/system/backup"),
            Path("memory/workflows/.archive/archived")
        ]

        print("\n🧹 Cleaning up old folders:")

        for folder in folders_to_check:
            if not folder.exists():
                continue

            # Check if empty or only has subdirectories that are empty
            try:
                items = list(folder.rglob('*'))
                if not items or all(not item.is_file() for item in items):
                    if self.dry_run:
                        print(f"  [DRY RUN] Would remove: {folder}")
                    else:
                        shutil.rmtree(folder)
                        print(f"  ✅ Removed: {folder}")
                else:
                    print(f"  ⚠️  Not empty, keeping: {folder}")
            except Exception as e:
                print(f"  ❌ Error checking {folder}: {e}")

    def generate_report(self):
        """Generate migration summary report."""
        print("\n" + "="*60)
        print("📊 MIGRATION SUMMARY")
        print("="*60)

        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes made")

        print(f"\n✅ Successful migrations: {len(self.migrations)}")
        if self.verbose and self.migrations:
            for source, dest in self.migrations:
                print(f"   {source.name} → {dest}")

        if self.errors:
            print(f"\n❌ Errors encountered: {len(self.errors)}")
            for source, error in self.errors:
                print(f"   {source.name}: {error}")

        print("\n💡 Next steps:")
        if self.dry_run:
            print("   • Run without --dry-run to perform migration")
        else:
            print("   • Run CLEAN --scan to verify archive structure")
            print("   • Run STATUS to check archive health metrics")
            print("   • Test BACKUP, UNDO, REPAIR RECOVER commands")

        print("="*60)

    def run(self):
        """Execute full migration."""
        print("="*60)
        print("🚀 uDOS v1.1.16 Archive System Migration")
        print("="*60)

        if self.dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made\n")

        # Run migrations
        self.migrate_system_archived()
        self.migrate_system_backup()
        self.migrate_workflows_archived()

        # Cleanup
        self.cleanup_old_folders()

        # Report
        self.generate_report()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate legacy archive folders to v1.1.16 structure"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be migrated without making changes"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Show detailed migration steps"
    )

    args = parser.parse_args()

    migration = ArchiveMigration(dry_run=args.dry_run, verbose=args.verbose)
    migration.run()


if __name__ == "__main__":
    main()
