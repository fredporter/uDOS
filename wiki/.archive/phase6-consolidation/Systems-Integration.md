# Systems Integration Guide

**Version:** 1.1.14
**Last Updated:** December 2, 2025

## Overview

uDOS v1.1.14 introduces deep integration between missions, workflows, checklists, and the knowledge bank. This guide explains how these systems work together to create a cohesive survival planning and execution environment.

---

## System Components

### 1. Knowledge Bank (Read-Only Guides)

**Location:** `knowledge/`

- 136+ guides across 6 categories (water, fire, shelter, food, navigation, medical)
- Markdown format with structured content
- Reference material for learning and planning

**Command:** `GUIDE`

```bash
GUIDE LIST water
GUIDE SHOW water/purification
GUIDE START water/purification    # Interactive mode with progress tracking
```

### 2. Checklists (Progress Tracking)

**Location:** `knowledge/checklists/`

- 10 JSON-formatted checklists (emergency, daily, projects, seasonal)
- 126+ actionable items with priority levels
- Persistent progress tracking
- Related to guides and missions

**Command:** `CHECKLIST`

```bash
CHECKLIST LIST
CHECKLIST LOAD water-storage-maintenance
CHECKLIST COMPLETE store water containers
CHECKLIST PROGRESS
```

### 3. Missions (Project Management)

**Location:** `memory/workflows/missions/`

- JSON-defined projects with moves and steps
- Links to workflows, guides, and checklists
- Progress tracking through workflow state
- Metadata for planning and retrospectives

**Command:** `MISSION`

```bash
MISSION CREATE water-prep "Set up water purification"
MISSION START water-prep
MISSION STATUS
```

### 4. Workflows (Automation Scripts)

**Location:** `memory/workflows/missions/`

- `.upy` scripts for automated processes
- System variables ($MISSION, $WORKFLOW, $CHECKPOINT)
- Checkpoint-based state management
- XP and achievement integration

**Command:** `WORKFLOW`

```bash
WORKFLOW RUN water-purification-workflow.upy
WORKFLOW PAUSE
WORKFLOW RESUME
```

### 5. Dashboard (Real-Time Monitoring)

**Location:** `extensions/web/dashboard/`

- Flask web server on port 5050
- Real-time progress visualization
- NES.css retro aesthetic
- Auto-refresh every 5 seconds

**Usage:**

```bash
python extensions/web/dashboard/server.py
# Open http://127.0.0.1:5050
```

---

## Integration Patterns

### Pattern 1: Guide → Checklist

**Use Case:** Convert learning into action

**Flow:**
1. Read guide: `GUIDE SHOW water/purification`
2. See related checklists at bottom of guide
3. Load checklist: `CHECKLIST LOAD water-storage-maintenance`
4. Work through checklist items
5. Track progress automatically

**Example:**

```bash
# Learn about water purification
GUIDE START water/purification

# Guide shows: "📋 Related Checklists: water-storage-maintenance"

# Open checklist
CHECKLIST LOAD water-storage-maintenance

# Complete items
CHECKLIST COMPLETE inspect_containers
CHECKLIST COMPLETE check_seals
```

**Schema Connection:**

```json
{
  "id": "water-storage-maintenance",
  "related_guides": [
    "water/storage-methods",
    "water/purification",
    "water/quality-testing"
  ]
}
```

---

### Pattern 2: Checklist → Mission

**Use Case:** Organize checklists into larger projects

**Flow:**
1. Create mission with related checklists
2. Mission tracks overall progress
3. Checklists track granular tasks
4. Dashboard shows both levels

**Example:**

```json
{
  "id": "water-purification-setup",
  "title": "Water Purification System Setup",
  "related_checklists": [
    "water-storage-maintenance",
    "first-aid-kit-inventory"
  ],
  "moves": [
    {
      "id": 1,
      "title": "Research & Planning",
      "steps": [
        {
          "id": 1,
          "title": "Review water storage checklist",
          "description": "Load CHECKLIST water-storage-maintenance"
        }
      ]
    }
  ]
}
```

---

### Pattern 3: Mission → Workflow

**Use Case:** Automate mission execution

**Flow:**
1. Mission defines `workflow_script` field
2. Workflow executes mission steps
3. Workflow saves checkpoints
4. Mission metrics update from workflow state

**Example:**

```json
{
  "id": "water-purification-setup",
  "workflow_script": "water-purification-workflow.upy",
  "related_guides": ["water/purification"],
  "related_checklists": ["water-storage-maintenance"]
}
```

**Workflow Script (`.upy`):**

```python
# water-purification-workflow.upy
$MISSION.ID = "water-purification-setup"
$MISSION.STATUS = "ACTIVE"

# Run tasks
GUIDE SHOW water/purification
CHECKLIST LOAD water-storage-maintenance

# Save checkpoint
CHECKPOINT SAVE "completed-research"

$MISSION.PROGRESS = "33%"
```

---

### Pattern 4: Variable System Integration

**Use Case:** Access cross-system state

**Flow:**
1. Set mission/checklist/workflow variables
2. Query state from any context
3. Make decisions based on current state

**Commands:**

```bash
# Mission variables
GET MISSION.STATUS          # → "ACTIVE"
GET MISSION.PROGRESS        # → "45/55"
GET MISSION.ID              # → "water-purification-setup"

# Checklist variables
GET CHECKLIST.ACTIVE        # → "3"
GET CHECKLIST.PROGRESS_PCT  # → "67%"

# Workflow variables
GET WORKFLOW.PHASE          # → "EXECUTE"
GET WORKFLOW.ITERATION      # → "5"
GET WORKFLOW.ERRORS         # → "0"
```

**Data Sources:**

| Variable | File | Field |
|----------|------|-------|
| `$MISSION.*` | `memory/workflows/state/current.json` | `current_mission`, `status`, etc. |
| `$CHECKLIST.*` | `memory/system/user/checklist_state.json` | `checklists`, `completed_items` |
| `$WORKFLOW.*` | `memory/workflows/state/current.json` | `status`, `checkpoints_saved` |

---

### Pattern 5: Dashboard Monitoring

**Use Case:** Real-time visibility across all systems

**Flow:**
1. Dashboard polls JSON state files every 5 seconds
2. Displays mission progress, checklist completion, workflow phase
3. Shows XP, achievements, perfect streak
4. No manual refresh needed

**Widgets:**

**📋 Active Missions Widget:**
- Mission title and priority
- Progress bar (completed steps / total steps)
- Total missions count

**✓ Checklists Widget:**
- Active checklist names
- Completion percentage per checklist
- Total items across all checklists

**⚙️ Workflow Status Widget:**
- Current workflow name
- Execution phase (IDLE, INIT, EXECUTE, etc.)
- Checkpoints saved count

**🏆 XP & Achievements Widget:**
- Total XP earned
- Achievement badges
- Perfect run streak

---

## Complete Integration Example

### Scenario: Emergency Water Purification Setup

**Step 1: Learn**

```bash
GUIDE LIST water
# Shows: water/purification, water/storage, water/boiling, etc.

GUIDE SHOW water/purification
# Displays guide with "Related Checklists: water-storage-maintenance"
```

**Step 2: Plan**

```bash
MISSION CREATE water-prep "Emergency Water System" --priority high
# Creates mission JSON with related guides and checklists

MISSION EDIT water-prep
# Add workflow_script: "water-prep-workflow.upy"
# Add related_checklists: ["water-storage-maintenance"]
# Add related_guides: ["water/purification", "water/boiling"]
```

**Step 3: Execute**

```bash
CHECKLIST LOAD water-storage-maintenance
CHECKLIST COMPLETE inspect_containers
CHECKLIST COMPLETE check_seals
CHECKLIST STATUS
# Shows: "5/25 items complete (20%)"

# Check progress via variables
GET CHECKLIST.PROGRESS_PCT
# → "20%"
```

**Step 4: Automate (Optional)**

```bash
WORKFLOW RUN water-prep-workflow.upy
# Workflow automatically:
# - Loads guides
# - Runs checklist items
# - Saves checkpoints
# - Updates mission progress
```

**Step 5: Monitor**

```bash
# Open dashboard
python extensions/web/dashboard/server.py

# View at http://127.0.0.1:5050
# See real-time:
# - Mission: "Emergency Water System" - 20% complete
# - Checklist: "water-storage-maintenance" - 5/25 items
# - Workflow: EXECUTE phase
# - XP: +15 (from completed checklist items)
```

**Step 6: Archive**

```bash
MISSION COMPLETE water-prep

ARCHIVE mission water-prep
# Saves to: memory/system/archived/missions/water-prep_20251202_143000/
# Includes: mission.json, metadata.json, checkpoints/
```

---

## State File Reference

### Mission State: `memory/workflows/state/current.json`

```json
{
  "current_mission": "water-prep",
  "status": "ACTIVE",
  "missions_total": 5,
  "missions_completed": 2,
  "missions_failed": 0,
  "total_xp_earned": 350,
  "checkpoints_saved": 12,
  "achievements_unlocked": ["First Mission", "Perfect Week"],
  "perfect_streak": 3
}
```

### Checklist State: `memory/system/user/checklist_state.json`

```json
{
  "checklists": {
    "water-storage-maintenance": {
      "completed_items": ["inspect_containers", "check_seals"],
      "total_items": 25,
      "last_updated": "2025-12-02T14:30:00Z"
    }
  },
  "last_updated": "2025-12-02T14:30:00Z"
}
```

### Mission JSON: `memory/workflows/missions/water-prep.json`

```json
{
  "id": "water-prep",
  "title": "Emergency Water System",
  "priority": "high",
  "status": "active",
  "workflow_script": "water-prep-workflow.upy",
  "related_guides": ["water/purification", "water/boiling"],
  "related_checklists": ["water-storage-maintenance"],
  "moves": [ /* ... */ ]
}
```

---

## Best Practices

### 1. Start with Guides

Always read relevant guides before starting missions or checklists. Guides provide the knowledge foundation.

### 2. Link Related Systems

When creating missions:
- Add `related_guides` for reference
- Add `related_checklists` for tasks
- Add `workflow_script` for automation

When creating checklists:
- Add `related_guides` for learning
- Add `related_checklists` for dependencies

### 3. Use Variables for Integration

Query state with `GET` commands:
```bash
GET MISSION.PROGRESS
GET CHECKLIST.ACTIVE
GET WORKFLOW.PHASE
```

Use in scripts:
```python
if $MISSION.PROGRESS > 50:
    CHECKPOINT SAVE "halfway-point"
```

### 4. Monitor with Dashboard

Keep dashboard open during active work:
- Real-time progress tracking
- Visual feedback
- XP/achievement motivation

### 5. Archive Completed Work

Keep system clean:
```bash
ARCHIVE mission <id>
ARCHIVE checklist <id>
ARCHIVE workflow <id>
```

Archived items stored with:
- Timestamp
- Metadata
- Complete state snapshot
- Easy restoration

---

## Troubleshooting

### Issue: Guide doesn't show related checklists

**Solution:** Check checklist `related_guides` field matches guide path:

```json
{
  "related_guides": ["water/purification"]  // Must match guide ID
}
```

### Issue: Dashboard shows "No active mission"

**Solution:** Verify `memory/workflows/state/current.json` has `current_mission` set:

```json
{
  "current_mission": "water-prep"  // Must match mission file name
}
```

### Issue: Variables return "no active X"

**Solution:** Ensure state files exist and are valid JSON:
- `memory/workflows/state/current.json` (workflow/mission state)
- `memory/system/user/checklist_state.json` (checklist progress)

---

## API Reference

### GUIDE Commands

| Command | Description |
|---------|-------------|
| `GUIDE LIST [category]` | List available guides |
| `GUIDE SHOW <guide>` | Display guide (shows related checklists) |
| `GUIDE START <guide>` | Interactive mode with progress tracking |

### CHECKLIST Commands

| Command | Description |
|---------|-------------|
| `CHECKLIST LIST` | List all checklists |
| `CHECKLIST LOAD <id>` | Load checklist |
| `CHECKLIST COMPLETE <item>` | Mark item complete |
| `CHECKLIST PROGRESS` | Show completion stats |
| `CHECKLIST STATUS` | Show current state |

### MISSION Commands

| Command | Description |
|---------|-------------|
| `MISSION CREATE <id> <title>` | Create new mission |
| `MISSION START <id>` | Start mission |
| `MISSION STATUS` | Show mission state |
| `MISSION COMPLETE <id>` | Mark mission complete |

### WORKFLOW Commands

| Command | Description |
|---------|-------------|
| `WORKFLOW RUN <script>` | Execute workflow |
| `WORKFLOW PAUSE` | Pause execution |
| `WORKFLOW RESUME` | Resume execution |

### Variable Commands

| Command | Description |
|---------|-------------|
| `GET MISSION.<field>` | Get mission variable |
| `GET CHECKLIST.<field>` | Get checklist variable |
| `GET WORKFLOW.<field>` | Get workflow variable |

### ARCHIVE Commands

| Command | Description |
|---------|-------------|
| `ARCHIVE LIST [type]` | List archived items |
| `ARCHIVE mission <id>` | Archive mission |
| `ARCHIVE checklist <id>` | Archive checklist |
| `ARCHIVE restore <type> <id>` | Restore archived item |

---

## Additional Resources

- **Command Reference:** `wiki/Command-Reference.md`
- **Dashboard Guide:** `wiki/Dashboard-Guide.md`
- **Checklist System:** `knowledge/checklists/README.md`
- **Mission Manager:** `core/services/mission_manager.py`
- **Workflow System:** `memory/workflows/README.md`

---

**Last Updated:** December 2, 2025
**Version:** 1.1.14
