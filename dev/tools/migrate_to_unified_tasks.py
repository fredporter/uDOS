#!/usr/bin/env python3
"""
Migration Script: Unified Task System (v1.2.23)

Migrates existing task data to unified task management system:
- Reads memory/bank/user/tasks.json (old calendar tasks)
- Scans memory/workflows/missions/*.upy for mission objectives
- Merges into memory/workflows/tasks/unified_tasks.json
- Creates backups in .archive/migration/
- Generates migration report

Usage:
    python dev/tools/migrate_to_unified_tasks.py [--dry-run] [--backup]

Options:
    --dry-run: Show what would be migrated without making changes
    --backup: Create backup before migration (default: True)
    --force: Overwrite existing unified_tasks.json

Author: GitHub Copilot
Date: 20251213-143500UTC
Location: Development
Version: 1.0.0 (v1.2.23 Phase 3)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import shutil
import argparse


class TaskMigrator:
    """Migrate tasks to unified system."""
    
    def __init__(self, dry_run=False, backup=True):
        """
        Initialize migrator.
        
        Args:
            dry_run: Show changes without applying
            backup: Create backups before migration
        """
        self.dry_run = dry_run
        self.backup = backup
        
        # Paths
        self.old_tasks_file = Path("memory/bank/user/tasks.json")
        self.missions_dir = Path("memory/workflows/missions")
        self.unified_file = Path("memory/workflows/tasks/unified_tasks.json")
        self.archive_dir = Path("memory/workflows/tasks/.archive/migration")
        
        # Migration stats
        self.stats = {
            'tasks_migrated': 0,
            'missions_found': 0,
            'projects_created': 0,
            'errors': []
        }
        
    def run(self):
        """Execute migration."""
        print("🚀 Starting Unified Task Migration (v1.2.23)\n")
        
        # Create archive directory
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize unified data
        if self.unified_file.exists():
            print(f"⚠️  unified_tasks.json already exists")
            if not self._confirm("Overwrite existing file?"):
                print("❌ Migration cancelled")
                return False
        
        unified_data = {
            "tasks": [],
            "projects": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "migrated_from": "v1.2.22",
                "version": "1.0.0"
            }
        }
        
        # Backup existing files
        if self.backup:
            self._create_backups()
        
        # Step 1: Migrate old tasks.json
        if self.old_tasks_file.exists():
            print(f"📋 Found old tasks file: {self.old_tasks_file}")
            tasks = self._migrate_calendar_tasks()
            unified_data["tasks"].extend(tasks)
        else:
            print(f"ℹ️  No old tasks.json found (skipping)")
        
        # Step 2: Scan mission files for objectives
        if self.missions_dir.exists():
            print(f"\n🎯 Scanning missions: {self.missions_dir}")
            projects = self._scan_mission_files()
            unified_data["projects"].extend(projects)
        else:
            print(f"ℹ️  No missions directory found (skipping)")
        
        # Step 3: Save unified data
        if not self.dry_run:
            self._save_unified_data(unified_data)
            print(f"\n✅ Saved to: {self.unified_file}")
        else:
            print(f"\n🔍 DRY RUN - No files modified")
        
        # Print report
        self._print_report()
        
        return True
    
    def _migrate_calendar_tasks(self):
        """Migrate tasks from old calendar system."""
        tasks = []
        
        try:
            with open(self.old_tasks_file, 'r') as f:
                old_data = json.load(f)
            
            old_tasks = old_data.get('tasks', [])
            print(f"   Found {len(old_tasks)} tasks to migrate")
            
            for old_task in old_tasks:
                # Convert to unified format
                task = {
                    "id": f"migrated-task-{len(tasks)+1:04d}",
                    "type": "task",
                    "description": old_task.get('description', 'Untitled Task'),
                    "status": old_task.get('status', 'pending'),
                    "priority": old_task.get('priority', 'normal'),
                    "due_date": old_task.get('due_date'),
                    "created": old_task.get('created', datetime.now().isoformat()),
                    "completed": old_task.get('completed'),
                    "progress": old_task.get('progress', 0),
                    
                    # Relationships
                    "parent_id": None,
                    "project": None,
                    "workflow_file": None,
                    "checklist_ref": None,
                    
                    # Location awareness
                    "location": old_task.get('location'),
                    "timezone": old_task.get('timezone', 'UTC'),
                    
                    # Metadata
                    "tags": old_task.get('tags', []),
                    "estimated_hours": old_task.get('estimated_hours'),
                    "actual_hours": old_task.get('actual_hours', 0),
                    
                    # Migration tracking
                    "migrated_from": "calendar_tasks",
                    "original_id": old_task.get('id')
                }
                
                tasks.append(task)
                self.stats['tasks_migrated'] += 1
            
            print(f"   ✅ Migrated {len(tasks)} tasks")
            
        except Exception as e:
            error_msg = f"Error migrating calendar tasks: {e}"
            print(f"   ❌ {error_msg}")
            self.stats['errors'].append(error_msg)
        
        return tasks
    
    def _scan_mission_files(self):
        """Scan .upy mission files for objectives."""
        projects = []
        
        try:
            mission_files = list(self.missions_dir.glob("*.upy"))
            print(f"   Found {len(mission_files)} mission files")
            
            for mission_file in mission_files:
                try:
                    # Parse mission file for metadata
                    with open(mission_file, 'r') as f:
                        content = f.read()
                    
                    # Extract mission name from filename
                    mission_name = mission_file.stem.replace('_', ' ').title()
                    
                    # Look for MISSION.* variables in file
                    mission_id = None
                    objective = None
                    location = None
                    
                    for line in content.split('\n'):
                        if 'MISSION.NAME' in line:
                            # Extract name from SET or PRINT statement
                            if '"' in line:
                                mission_name = line.split('"')[1]
                        elif 'MISSION.ID' in line:
                            if '"' in line:
                                mission_id = line.split('"')[1]
                        elif 'MISSION.OBJECTIVE' in line or 'OBJECTIVE' in line:
                            if '"' in line:
                                objective = line.split('"')[1]
                        elif 'LOCATION' in line or 'TILE' in line:
                            if '"' in line:
                                location = line.split('"')[1]
                    
                    # Create project entry
                    project_id = mission_id or f"migrated-project-{len(projects)+1:04d}"
                    
                    project = {
                        "id": project_id,
                        "name": mission_name,
                        "description": objective or f"Mission: {mission_name}",
                        "status": "active",
                        "created": datetime.fromtimestamp(mission_file.stat().st_ctime).isoformat(),
                        "completed": None,
                        "location": location,
                        "workflow_file": str(mission_file),
                        "task_ids": [],
                        "completion_percentage": 0,
                        "tags": ["mission", "migrated"],
                        
                        # Migration tracking
                        "migrated_from": "mission_file",
                        "original_file": str(mission_file)
                    }
                    
                    projects.append(project)
                    self.stats['missions_found'] += 1
                    self.stats['projects_created'] += 1
                    
                except Exception as e:
                    error_msg = f"Error parsing {mission_file.name}: {e}"
                    print(f"   ⚠️  {error_msg}")
                    self.stats['errors'].append(error_msg)
            
            print(f"   ✅ Created {len(projects)} projects from missions")
            
        except Exception as e:
            error_msg = f"Error scanning mission files: {e}"
            print(f"   ❌ {error_msg}")
            self.stats['errors'].append(error_msg)
        
        return projects
    
    def _create_backups(self):
        """Create backup of files before migration."""
        print("\n💾 Creating backups...")
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%SUTC")
        
        # Backup old tasks.json
        if self.old_tasks_file.exists():
            backup_path = self.archive_dir / f"{timestamp}-tasks.json"
            shutil.copy2(self.old_tasks_file, backup_path)
            print(f"   ✅ Backed up: {backup_path}")
        
        # Backup existing unified_tasks.json if it exists
        if self.unified_file.exists():
            backup_path = self.archive_dir / f"{timestamp}-unified_tasks.json"
            shutil.copy2(self.unified_file, backup_path)
            print(f"   ✅ Backed up: {backup_path}")
    
    def _save_unified_data(self, data):
        """Save unified task data."""
        self.unified_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.unified_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _print_report(self):
        """Print migration report."""
        print("\n" + "="*60)
        print("📊 MIGRATION REPORT")
        print("="*60)
        print(f"Tasks migrated:     {self.stats['tasks_migrated']}")
        print(f"Missions found:     {self.stats['missions_found']}")
        print(f"Projects created:   {self.stats['projects_created']}")
        print(f"Errors:             {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\n⚠️  Errors encountered:")
            for error in self.stats['errors']:
                print(f"   - {error}")
        
        if not self.dry_run:
            print(f"\n📁 Files:")
            print(f"   Unified tasks: {self.unified_file}")
            print(f"   Backups:       {self.archive_dir}")
        
        print("\n✨ Migration complete!")
    
    def _confirm(self, message):
        """Prompt for confirmation."""
        if self.dry_run:
            return True
        
        response = input(f"{message} (y/n): ").lower()
        return response in ['y', 'yes']


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate tasks to unified system (v1.2.23)"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show changes without applying"
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help="Skip backup creation"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Overwrite existing unified_tasks.json without confirmation"
    )
    
    args = parser.parse_args()
    
    migrator = TaskMigrator(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    success = migrator.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
