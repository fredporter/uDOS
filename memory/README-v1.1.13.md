# Memory - Unified User Workspace (v1.1.13)

**Purpose**: Centralized user-generated content, persistent data, and active work in uDOS.

**Status**: v1.1.13 - Unified workspace structure (consolidated `/sandbox/` functions)

**Philosophy**: Everything user-created lives in `/memory`. Everything system-distributed lives in `/core`, `/extensions`, `/knowledge`.

---

## What Changed in v1.1.13

**Before**: Split between `/memory/` (permanent) and `/sandbox/` (temporary)
**After**: Unified `/memory/` workspace with clear organization patterns

**Rationale**: Simpler mental model, less cognitive overhead, clearer file lifecycle

---

## Directory Structure

```
memory/
├── ucode/                      # 📦 CORE DISTRIBUTABLE
│   ├── *.py                    # Python utilities (migrate_upy.py, etc.)
│   └── test_*.py               # Test suite (111 tests)
│
├── missions/                   # 🎯 MISSION MANAGEMENT
│   ├── active/                 # Current missions in progress
│   ├── completed/              # Finished missions (ready for archive)
│   └── templates/              # Mission templates (JSON)
│
├── workflows/                  # ⚙️ WORKFLOW AUTOMATION
│   ├── active/                 # Running workflows
│   ├── completed/              # Finished workflow runs
│   ├── templates/              # Workflow templates (.upy)
│   ├── checkpoints/            # Workflow state snapshots
│   ├── examples/               # Example workflows
│   └── scripts/                # Helper scripts and guides
│
├── checklists/                 # ✅ CHECKLIST TRACKING
│   ├── active/                 # Current checklists in use
│   ├── completed/              # Finished checklists
│   └── templates/              # Checklist templates (JSON)
│
├── archived/                   # 📦 COMPLETED WORK
│   ├── missions/               # Archived missions (by date)
│   ├── workflows/              # Archived workflow runs
│   └── checklists/             # Archived checklists
│
├── user/                       # 👤 USER DATA & SETTINGS
│   ├── USER.UDT                # Command aliases & preferences
│   ├── planets.json            # Multi-planet configurations
│   ├── checklist_state.json   # Checklist progress (NEW v1.1.14)
│   ├── knowledge.db            # Knowledge search index (SQLite)
│   └── xp.db                   # XP/progression database (SQLite)
│
├── logs/                       # 📋 SESSION & RUNTIME LOGS
│   ├── session_*.log           # Session activity logs
│   ├── *_server.log            # API/extension server logs
│   ├── audit.log, audit.json   # Audit trail
│   └── dev.log                 # Development logs
│
├── private/                    # 🔐 TIER 1: AES-256 encrypted (user-only)
├── shared/                     # 🔒 TIER 2: AES-128 encrypted (team)
├── groups/                     # 📂 TIER 3: Community knowledge
├── public/                     # 🌐 TIER 4: World-readable
│
├── planet/                     # 🌍 PLANET WORKSPACE
├── themes/                     # 🎨 CUSTOM USER THEMES
├── modules/                    # 🧩 USER EXTENSION MODULES
├── barter/                     # 💱 BARTER SYSTEM DATA
└── community/                  # 🤝 COMMUNITY CONTENT
```

---

## Core Principles

### 1. Unified Workspace
- **Before**: Split memory/sandbox caused confusion
- **After**: One location (`/memory/`) with clear subdirectories
- **Benefit**: Easier to find files, simpler backup, clearer organization

### 2. Lifecycle Management
- **Active** → Work in progress (missions, workflows, checklists)
- **Completed** → Finished work (ready for extraction/archival)
- **Archived** → Historical reference (timestamped, read-only)

### 3. Persistent vs Temporary
- **Persistent**: User data, configurations, completed work
- **Temporary**: Logs (auto-cleaned), checkpoints (ephemeral)
- **No more sandbox confusion**: Everything has a clear home

### 4. Git Tracking (Selective)
- **Tracked**: `ucode/` (tests, utilities)
- **Gitignored**: Everything else (user data, logs, active work)
- **Why**: Core utilities distributed, user data private

---

## Usage Patterns

### Starting New Work

```bash
# Create a mission
MISSION CREATE "knowledge-expansion"

# Create workflow from mission
WORKFLOW CREATE --mission knowledge-expansion --template batch-processing

# Track with checklist
CHECKLIST LOAD emergency/72-hour-bug-out-bag
```

### Active Development

```bash
# Work on mission
MISSION STATUS knowledge-expansion
MISSION PROGRESS knowledge-expansion

# Monitor workflow
WORKFLOW STATUS
GET WORKFLOW.PHASE

# Update checklist
CHECKLIST COMPLETE item-12
GET CHECKLIST.COMPLETED_ITEMS
```

### Completion & Archival

```bash
# Mark complete
MISSION COMPLETE knowledge-expansion
WORKFLOW COMPLETE batch-processing-001
CHECKLIST SAVE

# Archive finished work
ARCHIVE mission knowledge-expansion
ARCHIVE workflow batch-processing-001
ARCHIVE checklist emergency-prep-2025-12
```

---

## Folder Guidelines

### `/memory/missions/`

**Purpose**: Mission definitions, progress tracking, resources

**Structure**:
```
missions/
├── active/
│   └── [mission-id]/
│       ├── mission.json        # Mission definition
│       ├── progress.json       # Current progress
│       └── resources/          # Working files
├── completed/
│   └── [mission-id]/           # Ready for archival
└── templates/
    └── *.json                  # Mission templates
```

**Workflow**:
1. Create in `active/`
2. Mark complete → moves to `completed/`
3. Archive → moves to `archived/missions/[YYYY-MM-DD]-[id]/`

---

### `/memory/workflows/`

**Purpose**: Workflow automation, batch processing, scheduled tasks

**Structure**:
```
workflows/
├── active/
│   └── [workflow-id]/
│       ├── workflow.upy        # Workflow script
│       └── state.json          # Current state
├── completed/
│   └── [workflow-id]/          # Finished runs
├── templates/
│   └── *.upy                   # Workflow templates
├── checkpoints/
│   └── [workflow-id]/
│       └── checkpoint_N.json   # State snapshots
├── examples/
│   └── *.upy                   # Example workflows
└── scripts/
    └── *.md, *.sh              # Helper scripts and guides
```

**Key Features**:
- Automatic checkpoint creation
- Background process management
- Rate limiting and batching
- Progress tracking

---

### `/memory/checklists/`

**Purpose**: Interactive checklist tracking with progress persistence

**Structure**:
```
checklists/
├── active/
│   └── [checklist-id].json     # Active checklist + progress
├── completed/
│   └── [checklist-id].json     # Finished checklists
└── templates/
    └── *.json                  # Checklist templates
```

**Schema** (v1.1.14):
```json
{
  "id": "checklist-id",
  "title": "72-Hour Bug-Out Bag",
  "category": "emergency",
  "sections": [
    {
      "id": "pre-check",
      "title": "Pre-Check",
      "items": [
        {
          "id": "item1",
          "text": "Backpack (50L+)",
          "completed": true,
          "notes": "Got Osprey 55L"
        }
      ]
    }
  ],
  "progress": {
    "completed": 45,
    "total": 156,
    "percentage": 28.8
  }
}
```

**Progress Persistence**: `memory/user/checklist_state.json`

---

### `/memory/archived/`

**Purpose**: Historical reference for completed work

**Structure**:
```
archived/
├── missions/
│   └── [YYYY-MM-DD]-[mission-id]/
│       ├── mission.json
│       ├── final_report.md
│       └── resources/
├── workflows/
│   └── [YYYY-MM-DD]-[workflow-id]/
│       ├── workflow.upy
│       ├── final_state.json
│       └── logs/
└── checklists/
    └── [YYYY-MM-DD]-[checklist-id].json
```

**Features**:
- Timestamped for easy browsing
- Metadata preserved (completion stats, duration)
- Read-only reference
- Searchable via ARCHIVE LIST

---

### `/memory/user/`

**Purpose**: User settings, persistent state, databases

**Files**:
- `USER.UDT` - Command aliases, preferences
- `planets.json` - Multi-planet configurations
- `checklist_state.json` - Checklist progress (v1.1.14+)
- `knowledge.db` - SQLite knowledge index
- `xp.db` - SQLite progression database

**Git**: Always gitignored (sensitive user data)

---

### `/memory/logs/`

**Purpose**: Session logs, server logs, audit trail

**Files**:
- `session_*.log` - Session activity
- `*_server.log` - Extension server logs
- `audit.log`, `audit.json` - Audit trail
- `dev.log` - Development logging

**Retention**: 7 days (auto-cleaned by CLEAN command)

---

## Commands Reference

### Mission Management

```bash
MISSION CREATE <name>               # Create new mission
MISSION STATUS <id>                 # Show mission status
MISSION PROGRESS <id>               # Show progress
MISSION COMPLETE <id>               # Mark complete
MISSION LIST                        # List all missions
GET MISSION.PROGRESS                # Get current mission progress
```

### Workflow Automation

```bash
WORKFLOW CREATE --template <name>  # Create from template
WORKFLOW RUN <script>               # Run workflow script
WORKFLOW STATUS                     # Show workflow status
WORKFLOW CHECKPOINT                 # Save checkpoint
GET WORKFLOW.PHASE                  # Get current phase
```

### Checklist Tracking

```bash
CHECKLIST LOAD <id>                 # Load checklist
CHECKLIST LIST                      # List active checklists
CHECKLIST COMPLETE <item-id>        # Mark item complete
CHECKLIST PROGRESS                  # Show progress
CHECKLIST SAVE                      # Save progress
GET CHECKLIST.COMPLETED_ITEMS       # Get completion count
```

### Archive Management

```bash
ARCHIVE mission <id>                # Archive completed mission
ARCHIVE workflow <id>               # Archive workflow run
ARCHIVE checklist <id>              # Archive checklist
ARCHIVE LIST [type]                 # List archived items
ARCHIVE RESTORE <path>              # Restore from archive
```

### Cleanup

```bash
CLEAN                               # Interactive cleanup
CLEAN logs                          # Clean old logs
CLEAN --dry-run                     # Preview cleanup
TIDY workflows                      # Organize workflows
TIDY --auto                         # Auto-organize all
```

---

## Migration from v1.1.12 (Sandbox Split)

### What Moved

**From `/sandbox/` to `/memory/`:**
- `sandbox/workflow/` → `memory/workflows/`
- `sandbox/ucode/` → `memory/ucode/` (user scripts)
- `sandbox/user/` → `memory/user/` (user data)
- `sandbox/logs/` → `memory/logs/`
- `sandbox/drafts/` → `memory/workflows/active/` or `memory/missions/active/`

**What Stayed in `/dev/`:**
- `dev/tools/` - Development utilities (tracked)
- `dev/roadmap/` - Project planning (tracked)
- `dev/sessions/` - Development logs (tracked)
- `dev/scripts/` - Automation scripts (tracked)

### Migration Commands

```bash
# Automatic migration (future)
uDOS MIGRATE v1.1.13

# Manual migration (current)
# Files already moved during v1.1.13 upgrade
# Check /memory structure and verify paths
```

---

## Best Practices

### ✅ Do

- **Start in active/** - All new work in `active/` subdirectories
- **Complete when done** - Move to `completed/` when finished
- **Archive regularly** - Use `ARCHIVE` command to preserve history
- **Track progress** - Use missions, workflows, checklists together
- **Save checkpoints** - Workflows auto-checkpoint, but manual saves help
- **Clean old logs** - Run `CLEAN logs` weekly

### ❌ Don't

- **Don't edit archived/** - Archives are read-only reference
- **Don't mix active/completed** - Keep clear separation
- **Don't skip archival** - Completed work should be archived
- **Don't manually edit state files** - Use commands (MISSION, WORKFLOW, CHECKLIST)
- **Don't commit user data** - Everything in `/memory` is gitignored (except `ucode/`)

---

## Integration with Other Systems

### v1.1.14 Integration

**Mission ↔ Workflow:**
- Missions can have `workflow_script` field
- Workflows auto-update mission progress
- Shared variable space (`MISSION.*`, `WORKFLOW.*`)

**Checklist ↔ Guide:**
- Checklists link to knowledge guides
- Guides show related checklists
- Progress tracked separately

**Dashboard:**
- Real-time view of all active work
- Mission progress bars
- Workflow phase indicators
- Checklist completion meters

---

## Troubleshooting

### "Where did my sandbox files go?"

**Answer**: They're now in `/memory/` subdirectories:
- Workflows → `memory/workflows/`
- Scripts → `memory/ucode/`
- Drafts → `memory/missions/active/` or `memory/workflows/active/`
- User data → `memory/user/`

### "Can I still use /sandbox/?"

**Answer**: No, `/sandbox/` is deprecated in v1.1.13. Use `/memory/` subdirectories instead.

### "How do I backup my work?"

```bash
# Backup entire memory folder
tar -czf memory-backup-$(date +%Y%m%d).tar.gz memory/

# Backup specific types
ARCHIVE mission --all
ARCHIVE workflow --all
ARCHIVE checklist --all
```

### "How do I restore from backup?"

```bash
# Restore entire folder
tar -xzf memory-backup-YYYYMMDD.tar.gz

# Restore specific items
ARCHIVE RESTORE archived/missions/2025-12-01-my-mission/
```

---

## See Also

- [Development Guide](/wiki/Developers-Guide.md)
- [Command Reference](/wiki/Command-Reference.md)
- [Mission System](/wiki/Mission-System.md)
- [Workflow Automation](/wiki/Workflows.md)
- [Dashboard Guide](/wiki/Dashboard-Guide.md) (v1.1.14+)

---

**Last Updated:** v1.1.13 (December 2, 2025)
**Migration Status:** Complete
**Structure:** Unified workspace (active → completed → archived)
**Philosophy:** One workspace to rule them all
