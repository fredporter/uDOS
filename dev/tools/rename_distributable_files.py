#!/usr/bin/env python3
"""
Migration Script: Rename Distributable Files (v1.2.23)

Renames existing mission and workflow files to uDOS ID standard format:
- Old: mission_water_collection.upy
- New: 20251213-143022UTC-mission-water-collection.upy

- Old: my_workflow.upy
- New: 20251213-143022UTC-workflow-my-workflow.upy

Features:
- Preserves file modification timestamps
- Updates internal file references
- Archives originals to .archive/deprecated/
- Generates rename report with mapping

Usage:
    python dev/tools/rename_distributable_files.py [--dry-run] [--archive]

Options:
    --dry-run: Show what would be renamed without making changes
    --archive: Archive original files (default: True)
    --pattern <glob>: Specify file pattern (default: *.upy)
    --dir <path>: Target directory (default: memory/workflows/missions)

Author: GitHub Copilot
Date: December 13, 2025
Version: 1.0.0 (v1.2.23 Phase 3)
"""

import sys
from pathlib import Path
from datetime import datetime
import shutil
import argparse
import re


class FileRenamer:
    """Rename files to uDOS ID standard."""
    
    def __init__(self, dry_run=False, archive=True, pattern="*.upy", target_dir=None):
        """
        Initialize renamer.
        
        Args:
            dry_run: Show changes without applying
            archive: Archive original files
            pattern: File pattern to match
            target_dir: Target directory path
        """
        self.dry_run = dry_run
        self.archive = archive
        self.pattern = pattern
        self.target_dir = Path(target_dir or "memory/workflows/missions")
        self.archive_dir = self.target_dir / ".archive" / "deprecated"
        
        # Stats
        self.stats = {
            'files_found': 0,
            'files_renamed': 0,
            'files_archived': 0,
            'files_skipped': 0,
            'errors': []
        }
        
        # Rename mapping for updating references
        self.rename_map = {}
        
    def run(self):
        """Execute rename operation."""
        print("🚀 Starting File Rename to uDOS ID Standard (v1.2.23)\n")
        
        # Create archive directory
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Check target directory exists
        if not self.target_dir.exists():
            print(f"❌ Target directory not found: {self.target_dir}")
            return False
        
        # Find files to rename
        files = list(self.target_dir.glob(self.pattern))
        self.stats['files_found'] = len(files)
        
        print(f"📁 Directory: {self.target_dir}")
        print(f"🔍 Pattern: {self.pattern}")
        print(f"📋 Found {len(files)} files\n")
        
        if not files:
            print("ℹ️  No files to rename")
            return True
        
        # Process each file
        for file_path in files:
            self._process_file(file_path)
        
        # Update file references
        if not self.dry_run and self.rename_map:
            self._update_references()
        
        # Print report
        self._print_report()
        
        return True
    
    def _process_file(self, file_path):
        """Process single file for renaming."""
        # Skip if already in uDOS ID format
        if self._is_udos_format(file_path.name):
            print(f"⏭️  Skipped (already uDOS format): {file_path.name}")
            self.stats['files_skipped'] += 1
            return
        
        # Generate new filename
        new_name = self._generate_new_name(file_path)
        new_path = file_path.parent / new_name
        
        # Check for conflicts
        if new_path.exists():
            error_msg = f"Conflict: {new_name} already exists"
            print(f"   ⚠️  {error_msg}")
            self.stats['errors'].append(error_msg)
            self.stats['files_skipped'] += 1
            return
        
        print(f"📝 Rename:")
        print(f"   Old: {file_path.name}")
        print(f"   New: {new_name}")
        
        if not self.dry_run:
            try:
                # Archive original if requested
                if self.archive:
                    archive_path = self._archive_file(file_path)
                    print(f"   💾 Archived: {archive_path.name}")
                    self.stats['files_archived'] += 1
                
                # Rename file
                file_path.rename(new_path)
                
                # Store mapping for reference updates
                self.rename_map[file_path.name] = new_name
                
                self.stats['files_renamed'] += 1
                print(f"   ✅ Renamed")
                
            except Exception as e:
                error_msg = f"Error renaming {file_path.name}: {e}"
                print(f"   ❌ {error_msg}")
                self.stats['errors'].append(error_msg)
        else:
            print(f"   🔍 DRY RUN - No changes made")
        
        print()
    
    def _is_udos_format(self, filename):
        """Check if filename is already in uDOS ID format."""
        # Format: YYYYMMDD-HHMMSSTZ-name.ext
        pattern = r'^\d{8}-\d{6}[A-Z]{3,4}-'
        return bool(re.match(pattern, filename))
    
    def _generate_new_name(self, file_path):
        """Generate new filename in uDOS ID format."""
        # Get file modification time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        # Format: YYYYMMDD-HHMMSSTZ-type-original-name.ext
        timestamp = mtime.strftime("%Y%m%d-%H%M%S")
        timezone = "UTC"  # Could be enhanced with actual timezone detection
        
        # Determine file type prefix
        original_name = file_path.stem
        if 'mission' in original_name.lower():
            type_prefix = "mission"
        elif 'workflow' in original_name.lower():
            type_prefix = "workflow"
        elif 'test' in original_name.lower():
            type_prefix = "test"
        else:
            type_prefix = "script"
        
        # Clean up original name (remove type prefix if present)
        clean_name = original_name.lower()
        for prefix in ['mission_', 'workflow_', 'test_', 'script_']:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):]
                break
        
        # Replace underscores with hyphens for consistency
        clean_name = clean_name.replace('_', '-')
        
        # Build new filename
        new_name = f"{timestamp}{timezone}-{type_prefix}-{clean_name}{file_path.suffix}"
        
        return new_name
    
    def _archive_file(self, file_path):
        """Archive original file before rename."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive_name = f"{timestamp}-original-{file_path.name}"
        archive_path = self.archive_dir / archive_name
        
        shutil.copy2(file_path, archive_path)
        
        return archive_path
    
    def _update_references(self):
        """Update file references in other files."""
        print("\n🔗 Updating file references...")
        
        # Directories to scan for references
        scan_dirs = [
            Path("memory/workflows"),
            Path("memory/ucode"),
            Path("core/data")
        ]
        
        files_updated = 0
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            
            # Scan for files that might contain references
            for file_path in scan_dir.rglob("*.upy"):
                if self._update_file_references(file_path):
                    files_updated += 1
            
            for file_path in scan_dir.rglob("*.json"):
                if self._update_file_references(file_path):
                    files_updated += 1
        
        print(f"   ✅ Updated {files_updated} files with new references")
    
    def _update_file_references(self, file_path):
        """Update references in a single file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if file contains any old references
            found_refs = False
            new_content = content
            
            for old_name, new_name in self.rename_map.items():
                if old_name in content:
                    new_content = new_content.replace(old_name, new_name)
                    found_refs = True
            
            # Save if changes were made
            if found_refs:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                return True
            
        except Exception as e:
            error_msg = f"Error updating references in {file_path}: {e}"
            self.stats['errors'].append(error_msg)
        
        return False
    
    def _print_report(self):
        """Print rename report."""
        print("\n" + "="*60)
        print("📊 RENAME REPORT")
        print("="*60)
        print(f"Files found:      {self.stats['files_found']}")
        print(f"Files renamed:    {self.stats['files_renamed']}")
        print(f"Files archived:   {self.stats['files_archived']}")
        print(f"Files skipped:    {self.stats['files_skipped']}")
        print(f"Errors:           {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\n⚠️  Errors encountered:")
            for error in self.stats['errors']:
                print(f"   - {error}")
        
        if self.rename_map and not self.dry_run:
            print(f"\n📝 Rename mapping:")
            for old_name, new_name in self.rename_map.items():
                print(f"   {old_name} → {new_name}")
        
        if not self.dry_run:
            print(f"\n📁 Files:")
            print(f"   Target:  {self.target_dir}")
            print(f"   Archive: {self.archive_dir}")
        
        print("\n✨ Rename complete!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Rename files to uDOS ID standard (v1.2.23)"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show changes without applying"
    )
    parser.add_argument(
        '--no-archive',
        action='store_true',
        help="Skip archiving original files"
    )
    parser.add_argument(
        '--pattern',
        default='*.upy',
        help="File pattern to match (default: *.upy)"
    )
    parser.add_argument(
        '--dir',
        help="Target directory (default: memory/workflows/missions)"
    )
    
    args = parser.parse_args()
    
    renamer = FileRenamer(
        dry_run=args.dry_run,
        archive=not args.no_archive,
        pattern=args.pattern,
        target_dir=args.dir
    )
    
    success = renamer.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
