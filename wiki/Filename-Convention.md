# Filename Convention Guide

**Date:** 20251213-164000UTC (December 13, 2025)  
**Location:** Documentation - Wiki  
**Version:** v1.2.23

## Overview

uDOS uses a standardized filename format called the **uDOS ID Standard** for all distributable content. Introduced in v1.2.23, this format enables chronological sorting, location awareness, and machine-readable filenames.

---

## uDOS ID Standard Format

### Full Format

```
YYYYMMDD-HHMMSSTZ-TILE-type-name.ext
```

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| `YYYYMMDD` | Date (sortable, ISO-like) | `20251213` |
| `HHMMSS` | Time (24-hour format) | `163000` |
| `TZ` | Timezone abbreviation | `UTC`, `PST`, `EST` |
| `TILE` | Grid location code (optional) | `AA340`, `JF57` |
| `type` | Entity type | `task`, `mission`, `workflow` |
| `name` | Descriptive name (kebab-case) | `collect-water` |
| `ext` | File extension | `.upy`, `.json`, `.md` |

### Variations

**Date Only**:
```
YYYYMMDD-name.ext
20251213-daily-log.md
```

**Date + Time**:
```
YYYYMMDD-HHMMSSTZ-name.ext
20251213-163000UTC-backup.json
```

**Date + Time + Location**:
```
YYYYMMDD-HHMMSSTZ-TILE-name.ext
20251213-163000UTC-AA340-mission.upy
```

**Date + Time + Location + Type**:
```
YYYYMMDD-HHMMSSTZ-TILE-type-name.ext
20251213-163000UTC-AA340-mission-establish-camp.upy
```

---

## FILE NEW Command

### Basic Usage

```bash
FILE NEW <filename>
# Creates: <filename>
```

### With Flags (v1.2.23)

#### --dated

Add date prefix.

```bash
FILE NEW log.md --dated
# Creates: 20251213-log.md
```

#### --timed

Add date and time prefix.

```bash
FILE NEW backup.json --timed
# Creates: 20251213-163000UTC-backup.json
```

#### --located

Add location (TILE code). Requires `--tile` flag.

```bash
FILE NEW mission.upy --timed --located --tile AA340
# Creates: 20251213-163000UTC-AA340-mission.upy
```

#### --tile <code>

Specify TILE code for location.

```bash
FILE NEW report.md --dated --located --tile AA340
# Creates: 20251213-AA340-report.md
```

### Combined Examples

```bash
# Mission with full format
FILE NEW establish-camp.upy --timed --located --tile AA340
# → 20251213-163022UTC-AA340-establish-camp.upy

# Daily log with date
FILE NEW daily-tasks.md --dated
# → 20251213-daily-tasks.md

# Backup with timestamp
FILE NEW system-backup.json --timed
# → 20251213-163022UTC-system-backup.json
```

---

## FilenameGenerator Service

### Programmatic Use

```python
from core.services.filename_generator import FilenameGenerator

# Initialize
gen = FilenameGenerator(config=config)

# Generate with date
filename = gen.generate(
    base_name="mission",
    extension=".upy",
    include_date=True
)
# → "20251213-mission.upy"

# Generate with time
filename = gen.generate(
    base_name="backup",
    extension=".json",
    include_date=True,
    include_time=True
)
# → "20251213-163000UTC-backup.json"

# Generate with location
filename = gen.generate(
    base_name="recon",
    extension=".upy",
    include_date=True,
    include_time=True,
    tile_code="AA340"
)
# → "20251213-163000UTC-AA340-recon.upy"
```

### Handler Integration

6 handlers use FilenameGenerator (v1.2.23):
- `calendar_handler.py` - Event/appointment files
- `workflow_handler.py` - Workflow scripts
- `ok_handler.py` - OK Assistant generated files
- `sandbox_handler.py` - Temporary/test files
- `system_handler.py` - System snapshots
- `file_handler.py` - User-created files

---

## Document Timestamp Standard

### Python Files

```python
"""
Module: unified_task_manager.py
Date: 20251213-143500UTC
Location: Core Services
Version: 1.2.23
"""
```

### Markdown Files

```markdown
# Document Title

**Date:** 20251213-145000UTC (December 13, 2025)  
**Location:** Documentation - Wiki  
**Version:** v1.2.23
```

### Session Logs

```markdown
# Development Session

**Date:** 20251213-104000UTC (December 13, 2025)  
**Location:** Development Session  
**Session:** v1.2.23 Implementation
```

---

## Naming Patterns

### Tasks

```
20251213-163000UTC-task-collect-water.json
20251213-170000UTC-task-purify-water.json
```

### Projects

```
20251213-160000UTC-project-camp-setup.json
20251213-180000UTC-project-water-system.json
```

### Missions

```
20251213-140000UTC-AA340-mission-establish-camp.upy
20251215-090000UTC-AB350-mission-reconnaissance.upy
```

### Workflows

```
20251213-120000UTC-workflow-daily-backup.upy
20251213-180000UTC-workflow-system-check.upy
```

### Backups

```
20251213-163000UTC-unified_tasks.json
20251213-170000UTC-config-backup.json
```

### Archives

```
20251213-archived-task-0001.json
20251213-archived-project-camp.json
```

---

## TIDY Organization

### By Date

Organizes files into `YYYY-MM/` folders.

```bash
TIDY tasks
TIDY --by-date
```

**Pattern Recognition**:
- Regex: `^\d{8}-\d{6}[A-Z]{3,4}-`
- Extracts: `YYYYMMDD` from filename
- Creates: `YYYY-MM/` folders
- Moves: Files to monthly folders

**Before**:
```
tasks/
├── 20251213-163000UTC-task-water.json
├── 20251115-140000UTC-task-shelter.json
└── 20251020-100000UTC-task-fire.json
```

**After**:
```
tasks/
├── 2025-12/
│   └── 20251213-163000UTC-task-water.json
├── 2025-11/
│   └── 20251115-140000UTC-task-shelter.json
└── 2025-10/
    └── 20251020-100000UTC-task-fire.json
```

### By Location

Organizes files into TILE code folders.

```bash
TIDY missions
TIDY --by-location
```

**Pattern Recognition**:
- Regex: `^\d{8}-\d{6}[A-Z]{3,4}-([A-Z]{2,}\d+)-`
- Extracts: TILE code from filename
- Creates: `TILE/` folders
- Moves: Files to location folders

**Before**:
```
missions/
├── 20251213-163000UTC-AA340-mission-camp.upy
├── 20251210-140000UTC-AB350-mission-recon.upy
└── 20251205-090000UTC-AA340-mission-water.upy
```

**After**:
```
missions/
├── AA340/
│   ├── 20251213-163000UTC-AA340-mission-camp.upy
│   └── 20251205-090000UTC-AA340-mission-water.upy
└── AB350/
    └── 20251210-140000UTC-AB350-mission-recon.upy
```

---

## Migration Tools

### rename_distributable_files.py

Renames legacy files to uDOS ID format.

```bash
# Dry run (preview changes)
python dev/tools/rename_distributable_files.py --dry-run

# Actual rename
python dev/tools/rename_distributable_files.py

Output:
  ✅ Renamed 35 files to uDOS ID format
  ✅ Updated 12 references in scripts
  ✅ Backup created: .archive/rename-backup/
```

**Detection Patterns**:
- `mission_*.upy` → `YYYYMMDD-HHMMSSTZ-mission-*.upy`
- `task_*.json` → `YYYYMMDD-HHMMSSTZ-task-*.json`
- `workflow_*.upy` → `YYYYMMDD-HHMMSSTZ-workflow-*.upy`

**Reference Updates**:
- Scans `.upy` files for old filenames
- Updates references to new format
- Preserves functionality

---

## Best Practices

### DO

✅ **Use FILE NEW with flags** for new content
```bash
FILE NEW mission.upy --timed --located --tile AA340
```

✅ **Include timezone** in timestamps
```bash
20251213-163000UTC-backup.json  # Good
```

✅ **Use kebab-case** for names
```bash
establish-camp.upy  # Good (not establishCamp.upy)
```

✅ **Be descriptive** but concise
```bash
20251213-collect-water-from-stream.json  # Good
```

✅ **Include type** for clarity
```bash
20251213-163000UTC-task-collect-water.json  # Clear
```

### DON'T

❌ **Don't omit timezone**
```bash
20251213-163000-backup.json  # Bad (which timezone?)
```

❌ **Don't use spaces**
```bash
20251213 backup file.json  # Bad (use hyphens)
```

❌ **Don't use camelCase or snake_case**
```bash
collectWaterTask.json  # Bad
collect_water_task.json  # Bad
```

❌ **Don't create inconsistent formats**
```bash
dec-13-2025-task.json  # Bad (not sortable)
```

---

## Examples by Use Case

### Daily Logs

```bash
FILE NEW daily-log.md --dated
# → 20251213-daily-log.md
```

### Mission Scripts

```bash
FILE NEW establish-camp.upy --timed --located --tile AA340
# → 20251213-163022UTC-AA340-establish-camp.upy
```

### System Backups

```bash
BACKUP memory/workflows/tasks/unified_tasks.json
# → backups/20251213-163000UTC-unified_tasks.json
```

### Task Exports

```bash
TASK EXPORT --format json
# → exports/20251213-163000UTC-tasks-export.json
```

### Archive Files

```bash
ARCHIVE task 20251213-163000UTC-task-0001
# → .archive/2025-12/20251213-archived-task-0001.json
```

---

## Configuration

### Set Current Location

```bash
CONFIG SET current_tile AA340
# Used for --located flag default
```

### Set Timezone

```bash
TIME SET UTC
# Used for timestamp generation
```

### View Settings

```bash
CONFIG SHOW
# Displays current_tile, timezone, etc.
```

---

**Last Updated:** 20251213-164000UTC (December 13, 2025)  
**Version:** v1.2.23  
**Status:** Production Ready

## See Also

- [Task Management](Task-Management.md)
- [Workflow System](Workflow-System.md)
- [Archive System](Archive-System.md)
- [File Commands](Command-Reference.md#file-commands)
