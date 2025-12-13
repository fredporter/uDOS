# Archive System

**Version:** v1.1.16
**Status:** Active
**Last Updated:** December 3, 2025

Universal `.archive/` folder system for version history, backups, soft-deletes, and completed work archival.

---

## Overview

The Archive System provides a consistent, workspace-wide approach to file versioning, backups, recovery, and archival. Every directory in uDOS can have a hidden `.archive/` folder with standardized subdirectories for different archive types.

### Design Principles

1. **Universal Pattern** - Any folder can have `.archive/` subfolder
2. **Distributed Storage** - Archives live with source files, not centralized
3. **Auto-Managed** - Retention policies enforce automatic cleanup
4. **Recoverable** - 7-day soft-delete window for file recovery
5. **Transparent** - Clear organization, easy to navigate

---

## Directory Structure

### Standard .archive/ Layout

```
any-folder/
├── .archive/              # Hidden archive folder
│   ├── versions/          # File version history (90-day retention)
│   ├── backups/           # Timestamped snapshots (30-day retention)
│   ├── deleted/           # Soft-deleted files (7-day recovery window)
│   ├── completed/         # Archived work (missions, workflows)
│   └── metadata.json      # Archive configuration and tracking
├── active_file.txt        # Active working files
└── working_data.json
```

### Example Locations

```
memory/
├── workflows/
│   ├── .archive/
│   │   ├── backups/       # Workflow backups
│   │   └── completed/     # Completed workflows
│   ├── missions/
│   │   ├── .archive/
│   │   │   └── completed/ # Completed missions
│   │   └── mission-001.upy
│   └── checkpoints/
│       └── .archive/
│           ├── backups/   # Checkpoint backups
│           └── deleted/   # Deleted checkpoints
├── system/
│   └── user/
│       └── .archive/
│           ├── backups/   # Config backups
│           └── versions/  # Config version history
└── logs/
    └── .archive/
        ├── backups/       # Log snapshots
        └── deleted/       # Old log files
```

---

## Archive Types

### 1. Versions (`versions/`)

**Purpose:** Track file modification history
**Retention:** 90 days
**Max Versions:** 10 per file
**Format:** `YYYYMMDD_HHMMSS_filename.ext`

**How It Works:**
- Automatic version creation on file save
- Most recent version listed first
- Older versions auto-purged after 90 days
- Use UNDO/REDO to navigate versions

**Commands:**
```bash
UNDO config.json              # Revert to previous version
UNDO --list config.json       # List all versions
UNDO --to-version 20251203_120000_config.json config.json
```

### 2. Backups (`backups/`)

**Purpose:** Timestamped snapshots for safe experimentation
**Retention:** 30 days (configurable)
**Format:** `YYYYMMDD_HHMMSS_filename.ext`

**How It Works:**
- Manual backup creation via BACKUP command
- Workspace-wide search for file backups
- Restore to original or custom location
- Retention-based cleanup

**Commands:**
```bash
BACKUP config.json            # Create backup
BACKUP LIST config.json       # List backups
BACKUP RESTORE 20251203_120000_config.json
BACKUP CLEAN 7                # Remove backups older than 7 days
```

### 3. Deleted Files (`deleted/`)

**Purpose:** Soft-delete recovery window
**Retention:** 7 days
**Format:** Original filename preserved

**How It Works:**
- File deletion moves to `.archive/deleted/` (not permanent)
- 7-day recovery window before auto-purge
- REPAIR RECOVER lists and restores deleted files
- Permanent delete: `DELETE --permanent`

**Commands:**
```bash
DELETE config.json            # Soft delete (recoverable)
REPAIR RECOVER                # List recoverable files
REPAIR RECOVER config.json    # Restore deleted file
DELETE config.json --permanent # Permanent delete (no recovery)
```

### 4. Completed Work (`completed/`)

**Purpose:** Archive finished missions/workflows/checklists
**Retention:** Permanent (manual cleanup)
**Format:** `<id>_YYYYMMDD_HHMMSS/` directories

**How It Works:**
- ARCHIVE command moves completed work
- Preserves metadata and related files
- LIST and RESTORE subcommands
- Organized by type (missions, workflows, checklists)

**Commands:**
```bash
ARCHIVE mission knowledge-gen-001    # Archive mission
ARCHIVE LIST mission                 # List archived missions
ARCHIVE restore mission knowledge-gen-001
```

---

## Retention Policies

### Default Settings

```json
{
  "deleted_days": 7,      // Soft-delete recovery window
  "backups_days": 30,     // Backup retention
  "versions_days": 90,    // Version history retention
  "max_versions": 10      // Max versions per file
}
```

### Custom Configuration

Edit `<directory>/.archive/metadata.json`:

```json
{
  "created": "2025-12-03T12:00:00Z",
  "version": "1.1.16",
  "purpose": "User configuration backups",
  "retention_policies": {
    "deleted_days": 14,    // Custom: 14-day recovery
    "backups_days": 60,    // Custom: 2-month backup retention
    "versions_days": 180,  // Custom: 6-month version history
    "max_versions": 20     // Custom: 20 versions per file
  }
}
```

---

## Commands

### CLEAN (Enhanced v1.1.16)

Workspace cleanup and archive health monitoring.

**Modes:**
```bash
CLEAN                     # Review sandbox (legacy mode)
CLEAN --scan              # Scan all .archive/ folders, show health
CLEAN --purge [days]      # Purge old files (default: 30 days)
CLEAN --dry-run           # Preview deletions without executing
CLEAN --path <dir>        # Target specific directory
```

**Health Metrics:**
- Total archives found
- Total files in archives
- Total size (MB)
- Warnings:
  - Large archives (>100 MB)
  - Unpurged deleted files (>7 days)
  - Excessive versions (>10 per file)

**Example Output:**
```
╔═══════════════════════════════════════════════════════════╗
║               Archive System Health Report                ║
╠═══════════════════════════════════════════════════════════╣
║  Total Archives:        12                                ║
║  Total Files:          347                                ║
║  Total Size:        24.5 MB                               ║
╠═══════════════════════════════════════════════════════════╣
║  Warnings:                                                ║
║    ⚠️  Large archive: memory/logs/.archive (156 MB)      ║
║    ⚠️  Unpurged deleted files: 45 files (8-30 days old)  ║
╚═══════════════════════════════════════════════════════════╝
```

### BACKUP (New v1.1.16)

File backup lifecycle management.

**Subcommands:**
```bash
BACKUP <file>                       # Create timestamped backup
BACKUP <file> --to <path>           # Backup to specific archive
BACKUP LIST [file]                  # List backups
BACKUP RESTORE <backup>             # Restore backup
BACKUP RESTORE <backup> --to <path> # Custom restore location
BACKUP CLEAN [days]                 # Purge old backups
BACKUP CLEAN --dry-run              # Preview cleanup
BACKUP HELP                         # Command reference
```

**Features:**
- Timestamped backup creation
- Workspace-wide backup search
- Restoration to original or custom location
- Retention-based cleanup with dry-run

### UNDO / REDO (New v1.1.16)

Version history navigation.

**Subcommands:**
```bash
UNDO <file>                         # Revert to previous version
UNDO --list <file>                  # List version history
UNDO --to-version <version> <file>  # Revert to specific version
REDO <file>                         # Re-apply undone changes
```

**Features:**
- Automatic version tracking on file save
- Session-based redo stack
- Direct version selection
- 90-day version history

### REPAIR RECOVER (Enhanced v1.1.16)

Soft-delete file recovery.

**Subcommands:**
```bash
REPAIR RECOVER                      # List recoverable files
REPAIR RECOVER <filename>           # Restore specific file
```

**Features:**
- 7-day recovery window
- Lists files with deletion timestamp
- One-step restoration
- Warning if file already exists

---

## Migration from v1.1.15

The v1.1.16 release includes automatic migration of legacy archive folders:

### Migration Script

```bash
python dev/tools/migrate_archives_v1_1_16.py --dry-run  # Preview
python dev/tools/migrate_archives_v1_1_16.py --verbose  # Execute
```

### Migrations Performed

| Old Location | New Location | Type |
|--------------|--------------|------|
| `memory/system/archived/missions/*` | `memory/workflows/missions/.archive/completed/` | Completed missions |
| `memory/system/archived/workflows/*` | `memory/workflows/.archive/completed/` | Completed workflows |
| `memory/system/backup/*` | `memory/system/user/.archive/backups/` | Config backups |
| `memory/workflows/.archive/archived/*` | `memory/workflows/.archive/completed/` | Legacy archives |

### Post-Migration

Empty folders are automatically removed. Verify migration:

```bash
CLEAN --scan              # Check archive structure
STATUS                    # View archive health metrics
```

---

## .gitignore Integration

All `.archive/` folders are excluded from git tracking:

```gitignore
# Backups & Archives (v1.1.16+)
# Universal .archive/ folders (version history, backups, soft-deletes)
.archive/
**/.archive/
```

**Rationale:**
- User data and working state (not source code)
- Auto-managed with retention policies
- Large files (logs, backups) bloat git history
- Distributed across workspace (many locations)

---

## Health Monitoring

### STATUS Command Integration

The STATUS command now includes archive health metrics:

```
╔══════════════════════════════════════════════════════════╗
║                  uDOS SYSTEM STATUS                      ║
╠══════════════════════════════════════════════════════════╣
║ ... (connectivity, display, user info) ...               ║
╠══════════════════════════════════════════════════════════╣
║  📦 ARCHIVE SYSTEM                                       ║
║  ─────────────────────────────────────────────────────── ║
║  Archives: 12  Files: 347  Size: ✅ 24.5 MB             ║
║  ⚠️  Large archive: memory/logs/.archive (156 MB)       ║
╚══════════════════════════════════════════════════════════╝
```

### Health Indicators

| Emoji | Condition | Meaning |
|-------|-----------|---------|
| ✅ | Size < 100 MB | Healthy |
| ⚠️ | Size 100-500 MB | Warning |
| 🔴 | Size > 500 MB | Critical |

---

## Best Practices

### 1. Regular Cleanup

```bash
# Weekly: Scan archives
CLEAN --scan

# Monthly: Purge old files
CLEAN --purge 30

# Before major changes: Create backup
BACKUP important-config.json
```

### 2. Pre-Modification Backups

```bash
# Before risky edit
BACKUP config.json
EDIT config.json

# If things break
BACKUP RESTORE 20251203_120000_config.json
```

### 3. Version History for Configs

Critical configuration files automatically tracked:
- `memory/system/user/*.json`
- `*.upy` workflow scripts
- Theme files

Access via UNDO/REDO commands.

### 4. Soft-Delete First

```bash
# Default: Soft delete (recoverable for 7 days)
DELETE temp-file.txt

# Only if truly permanent
DELETE temp-file.txt --permanent
```

---

## Troubleshooting

### Archive Too Large

**Symptoms:** STATUS shows 🔴 (>500 MB) for archive

**Solution:**
```bash
# Check what's taking space
CLEAN --scan

# Purge old files
CLEAN --purge 14                # Older than 14 days
CLEAN --path memory/logs        # Target specific archive

# Manual cleanup (if needed)
# Inspect .archive/backups/ and .archive/versions/
```

### Cannot Recover File

**Symptoms:** `REPAIR RECOVER <file>` says "File not found"

**Causes:**
1. File was permanently deleted (`--permanent` flag)
2. More than 7 days since deletion (auto-purged)
3. File was deleted before v1.1.16

**Solution:**
- Check BACKUP LIST for backup copies
- Check UNDO --list for version history

### Version History Missing

**Symptoms:** `UNDO --list <file>` shows "No version history found"

**Causes:**
1. File created before v1.1.16
2. File never modified since creation
3. Versions auto-purged (90-day retention)

**Solution:**
- Create backup before next edit: `BACKUP <file>`
- Edit file to start tracking versions

---

## Technical Details

### Timestamp Format

All timestamps use `YYYYMMDD_HHMMSS` format for:
- Sortable by filename (newest first when reversed)
- Human-readable
- Filesystem-safe (no colons)
- Timezone-independent

Example: `20251203_143022_config.json`

### Metadata Schema

```json
{
  "created": "2025-12-03T14:30:22Z",
  "version": "1.1.16",
  "purpose": "Description of archive purpose",
  "retention_policies": {
    "deleted_days": 7,
    "backups_days": 30,
    "versions_days": 90,
    "max_versions": 10
  },
  "last_purge": "2025-12-03T14:30:22Z",
  "stats": {
    "total_files": 42,
    "total_size_bytes": 12582912
  }
}
```

### Storage Overhead

Typical overhead by archive type:
- **Versions:** 10-20% of working file size (10 versions × 10-20 KB each)
- **Backups:** Variable (manual creation)
- **Deleted:** Minimal (7-day window, auto-purged)
- **Completed:** Permanent (manual cleanup)

**Example:**
- 50 KB config file
- 10 versions = ~500 KB
- 5 backups = ~250 KB
- Total overhead: ~750 KB (15x original)

---

## API Reference

### ArchiveManager Class

```python
from core.utils.archive_manager import ArchiveManager

archive_mgr = ArchiveManager()

# Create archive structure
archive_mgr.create_archive(directory, subdirs=['versions', 'backups'])

# Add version
archive_mgr.add_version(file_path, archive_dir)

# Add backup
backup_path = archive_mgr.add_backup(file_path, archive_dir)

# Soft delete
deleted_path = archive_mgr.soft_delete(file_path, archive_dir)

# Restore deleted
archive_mgr.restore_deleted(deleted_path, restore_path)

# Scan workspace
archives = archive_mgr.scan_archives(root_dir='.')

# Get statistics
stats = archive_mgr.get_archive_stats(archive_path)

# Purge old files
archive_mgr.purge_old_files(archive_path, dry_run=False)

# Health metrics
health = archive_mgr.get_health_metrics()
```

---

## Future Enhancements

Planned for future releases:

- **v1.1.17:** Compression for old versions (reduce storage)
- **v1.1.18:** Cloud sync for .archive/ folders
- **v1.1.19:** Archive comparison tools (diff between versions)
- **v1.1.20:** Automated archival triggers (on mission completion)
- **v1.2.23:** Unified task system integration, monthly folder organization, TIDY by date/location

---

## v1.2.23 Updates: Unified Task System Integration

### Task and Project Archiving

Complete task/project archiving with automatic monthly organization.

#### ARCHIVE task

Archive completed tasks to monthly folders.

```bash
ARCHIVE task <task_id>

# Example
ARCHIVE task 20251213-163000UTC-task-0001

# Result
# → Moved to: memory/workflows/tasks/.archive/2025-12/
# → Filename: 20251213-archived-task-0001.json
# → Removed from active unified_tasks.json
```

**Requirements**:
- Task must have status = "done"
- Task data preserved in archive file
- References updated in unified_tasks.json

#### ARCHIVE project

Archive completed projects with all linked tasks.

```bash
ARCHIVE project <project_id>

# Example
ARCHIVE project 20251213-160000UTC-project-camp-setup

# Result
# → Project archived to: .archive/2025-12/20251213-archived-project-camp.json
# → All linked tasks archived together
# → Project completion: 100% required
```

**Features**:
- Archives project and all child tasks
- Maintains task-project relationships
- Creates single archive bundle
- Monthly folder organization (YYYY-MM/)

### Monthly Folder Organization

Automatic organization by creation date.

**Structure**:
```
memory/workflows/tasks/.archive/
├── 2025-12/
│   ├── 20251213-archived-task-0001.json
│   ├── 20251213-archived-task-0002.json
│   └── 20251213-archived-project-camp.json
├── 2025-11/
│   ├── 20251115-archived-task-0100.json
│   └── 20251120-archived-project-recon.json
└── 2025-10/
    └── 20251010-archived-task-0050.json
```

**Benefits**:
- Chronological organization
- Easy cleanup of old archives
- Predictable location (YYYY-MM/)
- Fast date-based searches

### TIDY Integration

Organize existing files by date or location.

#### TIDY tasks

Organize task files into monthly folders.

```bash
TIDY tasks
# Groups files matching: YYYYMMDD-*-task-*.json
# Into: YYYY-MM/ folders
```

#### TIDY missions

Organize missions by TILE code.

```bash
TIDY missions
# Groups files matching: *-TILE-mission-*.upy
# Into: TILE/ folders
```

#### TIDY --by-date

Workspace-wide date organization.

```bash
TIDY --by-date [--report]
# Organizes all uDOS ID format files
# Creates YYYY-MM/ folders
# Use --report for preview
```

#### TIDY --by-location

Workspace-wide location organization.

```bash
TIDY --by-location [--report]
# Groups files by TILE code
# Creates TILE/ folders
# Use --report for preview
```

### Format Recognition

TIDY recognizes uDOS ID format automatically.

**Pattern Detection**:
```python
# Regex: ^\d{8}-\d{6}[A-Z]{3,4}-
# Matches: 20251213-163000UTC-task-name.json
#          20251213-163000PST-AA340-mission.upy

# Date extraction: YYYYMMDD (first 8 chars)
# Location extraction: TILE code between timestamps and name
```

**Files Recognized**:
- `20251213-163000UTC-task-collect-water.json` → `2025-12/`
- `20251213-163000UTC-AA340-mission-camp.upy` → `AA340/`
- `20251115-140000UTC-project-recon.json` → `2025-11/`

**Files Ignored**:
- `unified_tasks.json` (main data file)
- `config.json` (system files)
- `legacy-task.json` (no uDOS ID format)

### Version Control for Tasks

UNDO/REDO/BACKUP integrated with unified_tasks.json.

#### BACKUP unified_tasks.json

Auto-incremental backups for space efficiency.

```bash
BACKUP memory/workflows/tasks/unified_tasks.json

# Auto-detected as unified_tasks.json
# → Incremental backup enabled
# → Only changed data stored
# → Space-efficient versioning
```

#### UNDO unified_tasks.json

Special handling for task data file.

```bash
UNDO memory/workflows/tasks/unified_tasks.json

# → Restores previous backup
# → Current state saved for REDO
# → Task relationships preserved
# → Atomic revert (all or nothing)
```

#### REDO unified_tasks.json

Restore undone changes.

```bash
REDO memory/workflows/tasks/unified_tasks.json

# → Restores state before UNDO
# → Maintains redo stack
# → Full state recovery
```

### Archive Management

CLEAN command integration for archive maintenance.

#### CLEAN archives

Remove old .archive/ contents workspace-wide.

```bash
CLEAN archives [--dry-run] [--force]

Options:
  --dry-run    Preview what would be cleaned
  --force      Skip confirmation prompts

# Scans all .archive/ folders
# Applies retention policies
# Confirms before deletion (unless --force)
```

**Retention Policies**:
- Versions: 90 days (10 max per file)
- Backups: 30 days
- Deleted: 7 days (recovery window)
- Completed: Indefinite (manual cleanup)

#### CLEAN with stats

View archive space usage.

```bash
CLEAN --stats

Output:
  Archive Statistics:
  
  memory/workflows/.archive/: 45MB
  - Backups: 20MB (15 files, oldest: 28 days)
  - Completed: 25MB (50 files)
  
  memory/missions/.archive/: 12MB
  - Completed: 12MB (25 files)
  
  Total archive space: 57MB
```

### Migration Guide (v1.2.22 → v1.2.23)

Migrate existing archives to new structure.

#### Step 1: Backup Current Archives

```bash
# Backup entire .archive/ structure
tar -czf archive-backup-20251213.tar.gz \
  memory/*/.archive/ \
  memory/*/*/.archive/
```

#### Step 2: Run Migration

```bash
# Migrate tasks to unified system
python dev/tools/migrate_to_unified_tasks.py

# Rename files to uDOS ID format
python dev/tools/rename_distributable_files.py
```

#### Step 3: Organize Existing Files

```bash
# Organize by date
TIDY tasks
TIDY --by-date

# Organize by location
TIDY missions
TIDY --by-location
```

#### Step 4: Verify Structure

```bash
# Check for issues
CONFIG CHECK

# Fix any problems
CONFIG FIX

# View organization
TREE memory/workflows/tasks/.archive/ --sizes
```

### New Commands Summary

| Command | Description | v1.2.23 |
|---------|-------------|---------|
| `ARCHIVE task <id>` | Archive completed task | ✅ NEW |
| `ARCHIVE project <id>` | Archive project + tasks | ✅ NEW |
| `TIDY tasks` | Organize by date (YYYY-MM/) | ✅ NEW |
| `TIDY missions` | Organize by location (TILE/) | ✅ NEW |
| `TIDY --by-date` | Workspace-wide date org | ✅ NEW |
| `TIDY --by-location` | Workspace-wide location org | ✅ NEW |
| `CLEAN archives` | Clean all .archive/ folders | ✅ NEW |
| `BACKUP unified_tasks.json` | Auto-incremental backup | ✅ ENHANCED |
| `UNDO unified_tasks.json` | Special task file handling | ✅ ENHANCED |

---

## See Also

- [Command Reference](Command-Reference.md) - All archive system commands
- [Configuration](Configuration.md) - Retention policy configuration
- [Developers Guide](Developers-Guide.md) - ArchiveManager API
- [Task Management](Task-Management.md) - Unified task system (v1.2.23)
- [Filename Convention](Filename-Convention.md) - uDOS ID format (v1.2.23)

---

**Last Updated:** 20251213-165000UTC (December 13, 2025)
**Version:** v1.2.23
