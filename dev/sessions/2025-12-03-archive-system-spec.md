# .archive/ System Specification - v1.1.16

**Date:** December 3, 2025
**Version:** v1.1.16 (Archive System Infrastructure)
**Status:** Specification - Implementation Pending

## Overview

Universal `.archive/` folder system for version history, backups, and file recovery across all uDOS directories. Replaces fragmented `backup/`, `archived/`, `trash/` folders with a consistent, auto-managed approach.

## Core Concept

**Every directory can have a `.archive/` subfolder** containing:
- File version history (old/working versions)
- Backup snapshots (automated and manual)
- Soft-deleted files (recovery before permanent deletion)
- Archived work (completed missions, workflows, checklists)

## Architecture

### Directory Structure Pattern

```
any-folder/
├── .archive/                    # Hidden archive folder (auto-managed)
│   ├── backups/                 # Timestamped backups
│   │   ├── 20251203_143022_config.json
│   │   ├── 20251203_150145_user_settings.json
│   │   └── 20251202_093012_workflow.upy
│   ├── versions/                # File version history
│   │   ├── file_v001.txt
│   │   ├── file_v002.txt
│   │   └── file_v003.txt
│   ├── deleted/                 # Soft-deleted files (7-day window)
│   │   ├── 20251203_old_mission.upy
│   │   └── 20251201_temp_data.json
│   ├── completed/               # Archived completed work
│   │   ├── mission_water-001/
│   │   └── workflow_content-gen/
│   └── metadata.json            # Archive index and stats
├── active_file.txt              # Active working files
└── working_data.json
```

### Key Locations

```
memory/
├── workflows/
│   ├── .archive/                    # Workflow-level archives
│   ├── missions/
│   │   └── .archive/                # Mission-specific archives
│   ├── checkpoints/
│   │   └── .archive/                # Checkpoint history
│   └── state/
│       └── .archive/                # State snapshots
├── system/
│   ├── .archive/                    # System-level backups
│   ├── user/
│   │   └── .archive/                # User config history
│   └── themes/
│       └── .archive/                # Theme backups
├── logs/
│   └── .archive/                    # Log rotation
└── drafts/
    ├── svg/.archive/
    ├── ascii/.archive/
    └── teletext/.archive/

wiki/
└── .archive/                        # Wiki version history (already in use)

core/
└── data/
    └── .archive/                    # System file backups

dev/
└── sessions/
    └── .archive/                    # Old session logs
```

## Command Integration

### CLEAN Command (Enhanced)

**Purpose:** Scan and manage `.archive/` folders across workspace.

**Usage:**
```bash
CLEAN                           # Interactive cleanup
CLEAN --scan                    # Show .archive/ usage stats
CLEAN --purge [days]            # Delete archives older than N days (default: 30)
CLEAN --dry-run                 # Preview cleanup actions
CLEAN --path <folder>           # Clean specific folder's .archive/
```

**Behavior:**
1. Scans all `.archive/` folders recursively
2. Categorizes files by age:
   - Recent (< 7 days): Keep
   - Medium (7-30 days): Review
   - Old (> 30 days): Candidate for deletion
3. Shows size metrics and recommendations
4. Interactive confirmation before deletion

**Example Output:**
```
🧹 CLEAN - Archive Scan Results
================================

📊 Archive Usage Statistics:
  Total .archive/ folders: 12
  Total space used: 45.3 MB
  Files older than 30 days: 156

📂 Top Archive Locations:
  memory/workflows/.archive/        18.2 MB (456 files)
  memory/logs/.archive/             12.1 MB (1,234 files)
  wiki/.archive/                    8.4 MB (8 files)
  memory/system/user/.archive/      3.2 MB (45 files)

⚠️  Cleanup Candidates (> 30 days):
  memory/logs/.archive/             1,012 files (10.8 MB)
  memory/workflows/checkpoints/.archive/  89 files (4.2 MB)

Actions available:
  [1] Purge old logs (> 30 days)
  [2] Purge old checkpoints (> 30 days)
  [3] Review all old files
  [4] Custom purge (specify days)
  [5] Cancel

Choice:
```

### BACKUP Command (New/Enhanced)

**Purpose:** Create timestamped backups in `.archive/` folders.

**Usage:**
```bash
BACKUP <file>                   # Backup specific file
BACKUP <folder>                 # Backup entire folder
BACKUP --config                 # Backup all system configs
BACKUP --user                   # Backup user settings
BACKUP --auto                   # Enable auto-backup (periodic)
```

**Behavior:**
1. Creates timestamped copy in nearest `.archive/backups/`
2. Format: `YYYYMMDD_HHMMSS_filename.ext`
3. Updates `.archive/metadata.json` with backup record
4. Maintains backup history (configurable retention)

**Example:**
```bash
# Backup user config
BACKUP memory/system/user/user.json

# Creates:
# memory/system/user/.archive/backups/20251203_143022_user.json

# Output:
✅ Backup created: user.json
   Location: memory/system/user/.archive/backups/
   Timestamp: 2025-12-03 14:30:22
   Size: 2.4 KB
   Previous backups: 5 (keeping last 10)
```

### REPAIR Command (Enhanced)

**Purpose:** System health check with `.archive/` recovery options.

**Usage:**
```bash
REPAIR                          # Health check with .archive/ stats
REPAIR --recover <file>         # Recover from .archive/
REPAIR --restore <timestamp>    # Restore backup by timestamp
REPAIR --list-backups [file]    # Show available backups
```

**New Features:**
1. Reports `.archive/` space usage in health check
2. Can recover deleted files from `.archive/deleted/`
3. Lists available backups for recovery
4. Restores previous versions by timestamp

**Example:**
```bash
REPAIR --list-backups user.json

📦 Available Backups: user.json
================================

Recent (< 7 days):
  20251203_143022_user.json    2.4 KB    Today 14:30
  20251202_091534_user.json    2.3 KB    Yesterday 09:15
  20251201_153012_user.json    2.3 KB    2 days ago

Older (> 7 days):
  20251125_120000_user.json    2.2 KB    8 days ago
  20251120_080000_user.json    2.1 KB    13 days ago

Use: REPAIR --restore 20251203_143022 user.json
```

### ARCHIVE Command (Enhanced)

**Purpose:** Archive completed work to `.archive/completed/`.

**Current Behavior (v1.1.14):**
- Archives to `memory/system/archived/`

**New Behavior (v1.1.16):**
- Archives to contextual `.archive/completed/` folder
- Mission → `memory/workflows/missions/.archive/completed/`
- Workflow → `memory/workflows/.archive/completed/`
- Checklist → `memory/system/.archive/completed/`

**Usage (unchanged):**
```bash
ARCHIVE mission <id>
ARCHIVE workflow <id>
ARCHIVE checklist <id>
ARCHIVE LIST [type]
ARCHIVE restore <type> <id>
```

### UNDO/REDO Commands (New)

**Purpose:** Version control using `.archive/versions/`.

**Usage:**
```bash
UNDO <file>                     # Revert to previous version
REDO <file>                     # Re-apply undone changes
UNDO --list <file>              # Show version history
UNDO --to-version <n> <file>    # Jump to specific version
```

**Behavior:**
1. Each file save creates version in `.archive/versions/`
2. Maintains last 5-10 versions (configurable)
3. UNDO reverts to previous version
4. REDO re-applies if available
5. Version history tracked in metadata

**Example:**
```bash
UNDO memory/workflows/missions/water-purification.upy

📜 Version History: water-purification.upy
==========================================

Current version: v005 (modified today 14:45)
⬇️  Reverting to: v004 (modified today 14:30)

Changes:
  - Line 23: Removed debug PRINT statement
  - Line 45: Restored original logic
  - Size: 1.2 KB → 1.1 KB

✅ Reverted to version 004
   Original saved to .archive/versions/water-purification_v005.upy
   To redo: REDO water-purification.upy
```

### STATUS Command (Enhanced)

**Purpose:** System health with `.archive/` metrics.

**New Flags:**
```bash
STATUS --health                 # Include .archive/ usage
STATUS --archives               # Detailed .archive/ report
STATUS --cleanup                # Show cleanup recommendations
```

**Example Output:**
```
💚 System Health: GOOD
=======================

System Status:
  Version: v1.1.16
  Uptime: 2h 34m
  Memory: 145 MB / 512 MB

Archive System:
  Total .archive/ folders: 12
  Space used: 45.3 MB
  Files archived: 2,456
  Oldest archive: 45 days ago

Recommendations:
  ⚠️  Logs archive > 30 days (10.8 MB)
      Run: CLEAN --purge 30

  ✅ User configs backed up (5 versions)
  ✅ Workflows archived (12 completed)
```

## Metadata System

### .archive/metadata.json

**Purpose:** Track archive contents, stats, and history.

**Schema:**
```json
{
  "folder": "memory/workflows/missions",
  "created": "2025-12-03T14:30:22Z",
  "last_updated": "2025-12-03T16:45:10Z",
  "stats": {
    "total_files": 156,
    "total_size_bytes": 19087654,
    "oldest_file": "2025-10-15T08:00:00Z",
    "newest_file": "2025-12-03T16:45:10Z"
  },
  "categories": {
    "backups": {
      "count": 45,
      "size_bytes": 4521043,
      "retention_days": 30
    },
    "versions": {
      "count": 89,
      "size_bytes": 8234567,
      "versions_per_file": 5
    },
    "deleted": {
      "count": 12,
      "size_bytes": 1234098,
      "retention_days": 7
    },
    "completed": {
      "count": 10,
      "size_bytes": 5097946
    }
  },
  "cleanup_history": [
    {
      "timestamp": "2025-12-01T10:00:00Z",
      "files_deleted": 234,
      "space_freed_bytes": 8234567
    }
  ],
  "index": {
    "backups": [
      {
        "filename": "20251203_143022_config.json",
        "original": "config.json",
        "size_bytes": 2457,
        "timestamp": "2025-12-03T14:30:22Z"
      }
    ],
    "versions": [
      {
        "filename": "workflow_v004.upy",
        "original": "workflow.upy",
        "version": 4,
        "size_bytes": 1234,
        "timestamp": "2025-12-03T14:30:00Z"
      }
    ]
  }
}
```

## Auto-Management Rules

### Retention Policies

**Backups (`backups/`):**
- Default retention: 30 days
- Keep last 10 versions per file
- User configs: 90 days retention
- System files: 60 days retention

**Versions (`versions/`):**
- Keep last 5-10 versions per file (configurable)
- Compress old versions after 30 days
- Delete versions > 90 days

**Deleted Files (`deleted/`):**
- 7-day recovery window
- Auto-purge after 7 days
- Can be extended to 30 days for critical files

**Completed Work (`completed/`):**
- Permanent until manually cleaned
- User decides retention via CLEAN command

### Cleanup Triggers

**Automatic:**
1. System startup: Scan and flag old archives
2. Periodic (daily): Auto-cleanup deleted files > 7 days
3. Space threshold: Warning when .archive/ > 100 MB

**Manual:**
1. CLEAN command (user-initiated)
2. REPAIR --cleanup (system health)
3. ARCHIVE --purge (specific type)

## Integration Points

### Command Handlers

**Files to Update:**

1. **`core/commands/environment_handler.py`** - CLEAN command
   - Add `.archive/` scanning
   - Add purge logic
   - Add stats reporting

2. **`core/commands/archive_handler.py`** - ARCHIVE command
   - Change from `memory/system/archived/` to `.archive/completed/`
   - Update paths to contextual locations
   - Add metadata tracking

3. **`core/commands/repair_handler.py`** - REPAIR command
   - Add backup listing
   - Add recovery from `.archive/`
   - Add health metrics for `.archive/` usage

4. **`core/commands/system_handler.py`** - STATUS command
   - Add `.archive/` metrics to health check
   - Report total archive usage

5. **`core/commands/file_handler.py`** - File operations
   - Add version tracking on save
   - Soft-delete to `.archive/deleted/`
   - BACKUP integration

**New Handlers:**

6. **`core/commands/undo_handler.py`** - UNDO/REDO commands (NEW)
   - Version history management
   - File rollback logic

7. **`core/commands/backup_handler.py`** - BACKUP command (NEW)
   - Timestamped backup creation
   - Auto-backup scheduling

### Utility Modules

**Create:**

`core/utils/archive_manager.py`:
```python
class ArchiveManager:
    """Manage .archive/ folders across workspace."""

    def scan_archives(self, root_path: Path) -> dict
    def create_backup(self, file_path: Path) -> Path
    def restore_backup(self, backup_path: Path, target: Path) -> bool
    def purge_old_files(self, archive_path: Path, days: int) -> dict
    def get_stats(self, archive_path: Path) -> dict
    def update_metadata(self, archive_path: Path) -> None
```

### Configuration

**Add to `core/data/config.json`:**
```json
{
  "archive_system": {
    "enabled": true,
    "retention": {
      "backups_days": 30,
      "versions_count": 5,
      "deleted_days": 7
    },
    "auto_cleanup": {
      "enabled": true,
      "schedule": "daily",
      "purge_deleted": true,
      "purge_old_backups": false
    },
    "size_limits": {
      "warning_mb": 100,
      "max_mb": 500
    },
    "excluded_paths": [
      "memory/logs/.archive",
      "extensions/cloned"
    ]
  }
}
```

## Migration Plan (v1.1.15 → v1.1.16)

### Phase 1: Create .archive/ Infrastructure

1. Create `.archive/` folders in key locations:
   - `memory/workflows/.archive/`
   - `memory/workflows/missions/.archive/`
   - `memory/workflows/checkpoints/.archive/`
   - `memory/system/.archive/`
   - `memory/system/user/.archive/`
   - `memory/logs/.archive/`

2. Create `core/utils/archive_manager.py`

3. Update `.gitignore` to ignore all `.archive/` folders

### Phase 2: Migrate Existing Archives

1. Move `memory/system/archived/*` → `memory/workflows/missions/.archive/completed/`
2. Move `memory/system/backup/*` → `memory/system/user/.archive/backups/`
3. Clean up old `archived/` and `backup/` folders

### Phase 3: Update Commands

1. Update `environment_handler.py` (CLEAN)
2. Update `archive_handler.py` (ARCHIVE)
3. Update `repair_handler.py` (REPAIR)
4. Update `system_handler.py` (STATUS)
5. Create `backup_handler.py` (BACKUP - new)
6. Create `undo_handler.py` (UNDO/REDO - new)

### Phase 4: Documentation

1. Update `wiki/Command-Reference.md`
2. Update `.github/copilot-instructions.md` (DONE)
3. Create `wiki/Archive-System.md` (new)
4. Update `CHANGELOG.md`

### Phase 5: Testing

1. Create test suite for ArchiveManager
2. Test CLEAN command with multiple .archive/ folders
3. Test BACKUP command with various file types
4. Test UNDO/REDO with version history
5. Integration test with full workflow

## Benefits

1. **Consistency:** Unified approach across all directories
2. **Auto-managed:** CLEAN command handles cleanup automatically
3. **Recovery:** 7-day soft-delete window, version history
4. **Space-aware:** Tracks and reports .archive/ usage
5. **Version control:** Built-in UNDO/REDO for all files
6. **Backup system:** Automated and manual backups
7. **Health metrics:** STATUS command shows archive health

## Success Criteria

- ✅ All `.archive/` folders auto-created as needed
- ✅ CLEAN command scans and manages archives
- ✅ BACKUP command creates timestamped backups
- ✅ UNDO/REDO commands work with version history
- ✅ STATUS --health shows .archive/ metrics
- ✅ REPAIR can recover from .archive/
- ✅ Auto-cleanup removes files > retention period
- ✅ Migration from old `archived/`/`backup/` complete

## Implementation Timeline

**Target Version:** v1.1.16
**Estimated Effort:** 2-3 days

**Day 1:** Infrastructure & ArchiveManager utility
**Day 2:** Command updates (CLEAN, ARCHIVE, REPAIR, STATUS)
**Day 3:** New commands (BACKUP, UNDO/REDO), testing, documentation

---

**Status:** Specification complete - Ready for implementation
**Next Step:** Create `core/utils/archive_manager.py` and begin Phase 1
