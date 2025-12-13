# Task Management System

**Date:** 20251213-163000UTC (December 13, 2025)  
**Location:** Documentation - Wiki  
**Version:** v1.2.23

## Overview

The **Unified Task Management System** provides a single source of truth for all task-like entities in uDOS: tasks, checklist items, workflow steps, and missions. Introduced in v1.2.23, it replaces fragmented task tracking with a cohesive system that includes relationships, location awareness, and complete version control.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Task Types](#task-types)
3. [Commands Reference](#commands-reference)
4. [File Structure](#file-structure)
5. [uDOS ID Format](#udos-id-format)
6. [Task Lifecycle](#task-lifecycle)
7. [Project Management](#project-management)
8. [Version Control](#version-control)
9. [File Organization](#file-organization)
10. [Migration Guide](#migration-guide)
11. [Examples](#examples)
12. [Integration](#integration)

---

## Core Concepts

### Single Source of Truth

All tasks are stored in `memory/workflows/tasks/unified_tasks.json`:

```json
{
  "tasks": [
    {
      "id": "20251213-163000UTC-task-0001",
      "type": "task",
      "description": "Collect water from stream",
      "status": "pending",
      "priority": "high",
      "project": "20251213-160000UTC-project-camp-setup",
      "location": "AA340",
      "timezone": "UTC",
      "created": "2025-12-13T16:30:00Z",
      "updated": "2025-12-13T16:30:00Z"
    }
  ],
  "projects": [
    {
      "id": "20251213-160000UTC-project-camp-setup",
      "name": "Camp Setup",
      "description": "Establish base camp at grid AA340",
      "status": "active",
      "location": "AA340",
      "tasks": ["20251213-163000UTC-task-0001"],
      "created": "2025-12-13T16:00:00Z"
    }
  ],
  "metadata": {
    "version": "1.2.23",
    "last_backup": "2025-12-13T16:30:00Z"
  }
}
```

### Key Features

✅ **Unified Storage**: One file for all task types  
✅ **Relationships**: Link tasks to projects, workflows, missions  
✅ **Location Awareness**: TILE code tracking for geographic context  
✅ **Version Control**: Full UNDO/REDO/BACKUP integration  
✅ **Auto-Archiving**: Monthly folder organization  
✅ **Smart Naming**: uDOS ID format (YYYYMMDD-HHMMSSTZ-type-name)

---

## Task Types

### 1. Task (Standard)

Individual actionable items.

```bash
TASK CREATE "Purify 2L water" --project camp-setup --priority high
```

**Attributes**:
- `id`: Unique identifier (uDOS ID format)
- `description`: What needs to be done
- `status`: pending | in-progress | done | archived
- `priority`: low | normal | high | urgent
- `project`: Parent project ID (optional)
- `location`: TILE code (e.g., AA340)
- `due_date`: ISO timestamp (optional)

### 2. Checklist Item

Sub-task or verification step.

```bash
CHECKLIST CREATE "72-hour kit" --item "Water: 6L per person"
```

**Use Cases**:
- Daily routines
- Equipment verification
- Safety checks
- Step-by-step procedures

### 3. Workflow Step

Part of an automated workflow.

```bash
WORKFLOW CREATE "backup-system" --step "Archive old files"
```

**Features**:
- Sequential execution
- Conditional branching
- Variable passing
- Error handling

### 4. Mission

Large-scale objective with multiple tasks.

```bash
MISSION CREATE "Establish Camp" --location AA340 --duration 3days
```

**Characteristics**:
- Multiple linked tasks
- Location-specific
- Time-bounded
- XP/achievement integration

---

## Commands Reference

### Task Commands

#### CREATE

Create a new task.

```bash
TASK CREATE <description> [options]

Options:
  --project <id>      Link to project
  --priority <level>  low | normal | high | urgent
  --due <date>        Due date (YYYY-MM-DD)
  --location <tile>   TILE code (e.g., AA340)
  --type <type>       task | checklist_item | workflow_step | mission

Examples:
  TASK CREATE "Collect firewood"
  TASK CREATE "Build shelter" --project camp-setup --priority high
  TASK CREATE "Check water filter" --due 2025-12-15 --location AA340
```

#### LIST

List all tasks or filter by criteria.

```bash
TASK LIST [options]

Options:
  --project <id>      Filter by project
  --status <status>   pending | in-progress | done | archived
  --priority <level>  Filter by priority
  --location <tile>   Filter by TILE code
  --type <type>       Filter by task type

Examples:
  TASK LIST
  TASK LIST --status pending
  TASK LIST --project camp-setup
  TASK LIST --priority high --location AA340
```

#### DONE

Mark task as complete.

```bash
TASK DONE <task_id>

Example:
  TASK DONE 20251213-163000UTC-task-0001
```

#### DELETE

Remove a task (with confirmation).

```bash
TASK DELETE <task_id>

Example:
  TASK DELETE 20251213-163000UTC-task-0001
```

#### EDIT

Modify task attributes.

```bash
TASK EDIT <task_id> [options]

Options:
  --description <text>   Update description
  --priority <level>     Change priority
  --due <date>           Set due date
  --status <status>      Change status

Example:
  TASK EDIT 20251213-163000UTC-task-0001 --priority urgent
```

### Project Commands

#### PROJECT CREATE

Create a new project.

```bash
PROJECT CREATE <name> [options]

Options:
  --description <text>  Project description
  --location <tile>     TILE code
  --duration <time>     Estimated duration

Examples:
  PROJECT CREATE "Camp Setup"
  PROJECT CREATE "Water System" --location AA340 --duration 2days
```

#### PROJECT LIST

List all projects.

```bash
PROJECT LIST [options]

Options:
  --status <status>    active | completed | paused
  --location <tile>    Filter by location

Examples:
  PROJECT LIST
  PROJECT LIST --status active
```

#### PROJECT STATUS

View project details and task progress.

```bash
PROJECT STATUS <project_id>

Example:
  PROJECT STATUS 20251213-160000UTC-project-camp-setup

Output:
  Project: Camp Setup
  Status: active
  Location: AA340
  Tasks: 5 total, 3 done, 2 pending
  Progress: 60%
```

#### TASK LINK

Link task to project.

```bash
TASK LINK <task_id> --project <project_id>

Example:
  TASK LINK 20251213-163000UTC-task-0001 --project camp-setup
```

---

## File Structure

### Primary Storage

```
memory/workflows/tasks/
├── unified_tasks.json          # Main data file
├── backups/                    # Auto-backups
│   ├── 20251213-163000UTC-unified_tasks.json
│   └── 20251213-170000UTC-unified_tasks.json
└── .archive/                   # Archived tasks
    ├── 2025-12/                # Monthly folders
    │   ├── 20251213-archived-task-0001.json
    │   └── 20251213-archived-project-camp.json
    └── 2025-11/
```

### Auto-Organization

**TIDY by Date**:
```bash
TIDY tasks
# Organizes into YYYY-MM folders
```

**TIDY by Location**:
```bash
TIDY missions
# Groups by TILE code folders
```

---

## uDOS ID Format

### Standard Format

```
YYYYMMDD-HHMMSSTZ-type-name.ext
```

**Components**:
- `YYYYMMDD`: Date (sortable)
- `HHMMSS`: Time (24-hour)
- `TZ`: Timezone (UTC, PST, EST, etc.)
- `type`: Entity type (task, project, mission)
- `name`: Descriptive name
- `ext`: File extension

### Examples

```
20251213-163000UTC-task-collect-water.json
20251213-160000UTC-project-camp-setup.json
20251213-140000UTC-mission-establish-camp.upy
```

### FILE NEW Integration

Create files with auto-formatting:

```bash
FILE NEW mission.upy --timed --located --tile AA340
# Creates: 20251213-163022UTC-AA340-mission.upy

FILE NEW task.json --dated
# Creates: 20251213-task.json
```

**Flags**:
- `--dated`: Add YYYYMMDD prefix
- `--timed`: Add YYYYMMDD-HHMMSSTZ prefix
- `--located`: Add TILE code (requires --tile)
- `--tile <code>`: Specify TILE code

---

## Task Lifecycle

### 1. Creation

```bash
TASK CREATE "Collect water" --project camp-setup
# → Status: pending
# → ID: 20251213-163000UTC-task-0001
```

### 2. Work in Progress

```bash
TASK EDIT 20251213-163000UTC-task-0001 --status in-progress
# → Status: in-progress
# → Updated timestamp recorded
```

### 3. Completion

```bash
TASK DONE 20251213-163000UTC-task-0001
# → Status: done
# → Completion timestamp recorded
```

### 4. Archiving

```bash
ARCHIVE task 20251213-163000UTC-task-0001
# → Moved to .archive/2025-12/
# → Removed from active tasks
# → Preserved in unified_tasks.json history
```

### Status Flow

```
pending → in-progress → done → archived
   ↓           ↓          ↓
   └─────────→ paused ←──┘
```

---

## Project Management

### Creating Projects

```bash
PROJECT CREATE "Camp Setup" --location AA340 --duration 3days
# → ID: 20251213-160000UTC-project-camp-setup
```

### Adding Tasks

```bash
# Create tasks linked to project
TASK CREATE "Clear site" --project 20251213-160000UTC-project-camp-setup
TASK CREATE "Pitch tent" --project 20251213-160000UTC-project-camp-setup
TASK CREATE "Set up kitchen" --project 20251213-160000UTC-project-camp-setup
```

### Tracking Progress

```bash
PROJECT STATUS 20251213-160000UTC-project-camp-setup

Output:
  Project: Camp Setup
  Location: AA340
  Duration: 3 days
  Status: active
  
  Tasks:
    ✅ Clear site (done)
    🔄 Pitch tent (in-progress)
    ⏳ Set up kitchen (pending)
  
  Progress: 33% (1/3 complete)
```

### Completing Projects

```bash
# Mark all tasks done first
TASK DONE <task_id_1>
TASK DONE <task_id_2>
TASK DONE <task_id_3>

# Archive entire project
ARCHIVE project 20251213-160000UTC-project-camp-setup
# → All tasks archived together
# → Project marked complete
```

---

## Version Control

### BACKUP

Manual backup of task file.

```bash
BACKUP memory/workflows/tasks/unified_tasks.json
# → Creates: backups/20251213-163000UTC-unified_tasks.json
```

**Auto-Backup**:
- Triggers on task modifications
- Incremental backups (space-efficient)
- Configurable retention policy

### UNDO

Revert changes to previous version.

```bash
UNDO memory/workflows/tasks/unified_tasks.json
# → Restores previous backup
# → Current state saved for REDO
```

### REDO

Restore undone changes.

```bash
REDO memory/workflows/tasks/unified_tasks.json
# → Restores state before UNDO
```

### Version History

```bash
# List available backups
ls -lh memory/workflows/tasks/backups/

# Compare versions
diff backups/20251213-163000UTC-unified_tasks.json \
     backups/20251213-170000UTC-unified_tasks.json
```

---

## File Organization

### TIDY Tasks by Date

Organize tasks into monthly folders.

```bash
TIDY tasks
# Groups files matching: YYYYMMDD-*-task-*.json
# Into: YYYY-MM/
```

**Before**:
```
tasks/
├── 20251213-163000UTC-task-water.json
├── 20251213-170000UTC-task-firewood.json
└── 20251115-140000UTC-task-shelter.json
```

**After**:
```
tasks/
├── 2025-12/
│   ├── 20251213-163000UTC-task-water.json
│   └── 20251213-170000UTC-task-firewood.json
└── 2025-11/
    └── 20251115-140000UTC-task-shelter.json
```

### TIDY Missions by Location

Organize missions by TILE code.

```bash
TIDY missions
# Groups files matching: *-TILE-mission-*.upy
# Into: TILE/
```

**Before**:
```
missions/
├── 20251213-163000UTC-AA340-establish-camp.upy
└── 20251210-140000UTC-AB350-recon.upy
```

**After**:
```
missions/
├── AA340/
│   └── 20251213-163000UTC-AA340-establish-camp.upy
└── AB350/
    └── 20251210-140000UTC-AB350-recon.upy
```

### TIDY Preview

Check organization before execution.

```bash
TIDY tasks --report
# Shows what would be organized without making changes
```

---

## Migration Guide

### From v1.2.22 to v1.2.23

#### Step 1: Backup Existing Data

```bash
# Backup old tasks
BACKUP memory/workflows/tasks/tasks.json
BACKUP memory/missions/
BACKUP memory/checklists/
```

#### Step 2: Run Migration Script

```bash
# Dry run first (preview changes)
python dev/tools/migrate_to_unified_tasks.py --dry-run

# Actual migration
python dev/tools/migrate_to_unified_tasks.py

Output:
  ✅ Migrated 15 tasks from tasks.json
  ✅ Migrated 8 missions from missions/
  ✅ Migrated 12 checklist items
  ✅ Created unified_tasks.json
  ✅ Backup created: .archive/migration-backup/
```

#### Step 3: Rename Files to uDOS ID Format

```bash
# Dry run first
python dev/tools/rename_distributable_files.py --dry-run

# Actual rename
python dev/tools/rename_distributable_files.py

Output:
  ✅ Renamed 35 files to uDOS ID format
  ✅ Updated 12 references in scripts
  ✅ Backup created: .archive/rename-backup/
```

#### Step 4: Verify Structure

```bash
CONFIG CHECK
# Validates 16 required directories
# Checks unified_tasks.json format

CONFIG FIX
# Auto-creates missing directories
# Repairs structure issues
```

#### Step 5: Test System

```bash
# Run comprehensive test suite
./start_udos.sh memory/ucode/tests/test_unified_tasks.upy

# Run shakedown validation
./start_udos.sh memory/ucode/tests/shakedown.upy
```

---

## Examples

### Example 1: Daily Water Collection

```bash
# Create project
PROJECT CREATE "Daily Water Collection" --location AA340

# Add tasks
TASK CREATE "Check water source" --project daily-water --priority high
TASK CREATE "Collect 5L water" --project daily-water
TASK CREATE "Purify water" --project daily-water
TASK CREATE "Store in clean containers" --project daily-water

# Execute
TASK LIST --project daily-water
TASK DONE <task_id_1>
TASK DONE <task_id_2>
TASK DONE <task_id_3>
TASK DONE <task_id_4>

# Archive when complete
ARCHIVE project daily-water
```

### Example 2: Emergency Preparation

```bash
# Create checklist
CHECKLIST CREATE "72-hour kit" \
  --item "Water: 6L per person" \
  --item "Food: 3 days non-perishable" \
  --item "First aid kit" \
  --item "Emergency blanket" \
  --item "Flashlight + batteries"

# Verify items
CHECKLIST CHECK "72-hour kit"
# Interactive verification

# Export
CHECKLIST EXPORT "72-hour kit" --format pdf
```

### Example 3: Camp Setup Mission

```bash
# Create mission file
FILE NEW camp-setup.upy --timed --located --tile AA340

# Mission script (memory/workflows/missions/20251213-163000UTC-AA340-camp-setup.upy):
PROJECT CREATE "Camp Setup" --location AA340

# Phase 1: Site preparation
TASK CREATE "Clear site of debris" --project camp-setup --priority high
TASK CREATE "Level ground" --project camp-setup
TASK WAIT ALL

# Phase 2: Shelter
TASK CREATE "Pitch tent" --project camp-setup
TASK CREATE "Secure guy lines" --project camp-setup
TASK WAIT ALL

# Phase 3: Kitchen
TASK CREATE "Set up cooking area" --project camp-setup
TASK CREATE "Organize food storage" --project camp-setup
TASK WAIT ALL

PROJECT STATUS camp-setup
PRINT ('Camp setup complete!')

# Run mission
RUN camp-setup.upy
```

---

## Integration

### With Workflows

```bash
# Workflow with task creation
WORKFLOW CREATE "backup-system"
  TASK CREATE "Archive old files" --project backup
  WAIT 5s
  TASK CREATE "Verify backup" --project backup
  CHECK ERRORS
END WORKFLOW
```

### With OK Assistant

```bash
# Generate task breakdown
OK MAKE MISSION "Establish camp with water and fire systems"
# → Creates mission.upy with task hierarchy

# Analyze task completion
OK ASK "What tasks are blocking project completion?"
# → AI analysis of dependencies
```

### With XP System (Full Tier)

```bash
# Tasks grant XP when completed
TASK DONE <task_id>
# → +50 XP for task completion
# → +100 XP for project completion
# → Achievements unlocked

XP STATUS
# View total XP and achievements
```

---

**Last Updated:** 20251213-163000UTC (December 13, 2025)  
**Version:** v1.2.23  
**Status:** Production Ready

## See Also

- [Workflow System](Workflow-System.md)
- [Filename Convention](Filename-Convention.md)
- [Archive System](Archive-System.md)
- [Installation Guide](Installation-Guide.md)
