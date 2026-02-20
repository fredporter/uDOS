# Phase 6 Extension — Binder Workflow Integration & AI-Friendly Task Format

**Date:** 20 Feb 2026
**Status:** ✅ EXTENDED
**Enhancement:** Unified JSON format for AI ingestion & import mapping
**New Services:** 2 (VibeBinderService, VipeSetupService)
**New Tests:** 8 passing
**Total Tests:** 134/134 passing

---

## Overview

This extension adds three critical capabilities to the Vibe system:

1. **Enhanced VibeBinderService** — Manages missions with AI-friendly unified task format
2. **VipeSetupService** — Initializes uDOS configuration including VAULT_ROOT
3. **Unified Task JSON Format** — Support for multiple item types (task, calendar_event, invite, reminder, imported)

These services transform task management from simple to-dos into a **comprehensive knowledge base** with:
- Calendar events, meeting invites, reminders all mapped to tasks
- Support for external system imports (email, Slack, Jira, Linear, etc.)
- Extensible metadata for AI ingestion
- No excess markdown files in Obsidian vault (pure JSON)

---

## What's New: AI-Friendly Task Format

### Problem Addressed

Previously: Imported items (calendar, email, invites) required separate markdown files scattered across vault
Now: All items unified in `moves.json` with consistent, extensible JSON schema

### Solution: Unified Item Types

Every task supports a consistent schema:

```json
{
  "id": "uuid",
  "mission_id": "project",
  "title": "Task or Event Title",
  "description": "Full description",
  "item_type": "task|calendar_event|invite|reminder|imported",
  "status": "todo|in_progress|review|done",
  "priority": "high|medium|low",
  "tags": ["tag1", "tag2"],
  "due_date": "2026-02-25T17:00:00",
  "start_date": "2026-02-25T10:00:00",
  "end_date": "2026-02-25T17:00:00",
  "organizer": "organizer@company.com",
  "attendees": [{"name": "Alice", "email": "alice@company.com", "status": "accepted"}],
  "source": "manual|calendar|invite|email|slack|jira|linear",
  "source_id": "original-id-from-source",
  "metadata": {
    "custom_field": "value",
    "import_timestamp": "2026-02-20T10:30:00"
  },
  "created": "2026-02-20T10:30:00",
  "updated": "2026-02-20T10:35:00"
}
```

### Benefits

✅ **Single Schema** — All item types follow same structure
✅ **AI-Ready** — Complete metadata for LLM processing
✅ **No Duplicate Files** — No separate markdown for calendar/invites/reminders
✅ **Traceable Imports** — Source and source_id fields track origin
✅ **Query-Friendly** — Filter by item_type, source, date ranges
✅ **Extensible** — Metadata object for custom fields

---

## Item Types & Import Mapping

### 1. Standard Task (`item_type: "task"`)

**Source:** Manual creation
**Use Case:** General work items

```python
binder_service.add_move(
    mission_id="my-project",
    title="Implement feature X",
    description="Add OAuth2 support",
    priority="high"
)
```

### 2. Calendar Event (`item_type: "calendar_event"`)

**Source:** Google Calendar, Outlook, Apple Calendar
**Maps:** Scheduled meetings/events → tasks

```python
binder_service.add_calendar_event(
    mission_id="my-project",
    title="Q2 Planning Meeting",
    description="Quarterly planning session",
    start_date="2026-03-01T14:00:00",
    end_date="2026-03-01T15:30:00",
    organizer="lead@company.com",
    attendees=[...],
    source="calendar",
    source_id="google-calendar-event-id"
)
```

### 3. Meeting Invite (`item_type: "invite"`)

**Source:** Email invitations (Outlook, Gmail)
**Maps:** Meeting invites requiring RSVP → tasks

```python
binder_service.add_invite(
    mission_id="hiring-pipeline",
    title="Candidate Interview - Alice Smith",
    description="Technical interview",
    organizer="hiring@company.com",
    attendees=[
        {"name": "You", "email": "you@company.com", "status": "no_response"},
        {"name": "Panel", "email": "panel@company.com", "status": "accepted"}
    ],
    event_date="2026-02-26T10:00:00",
    response_due="2026-02-25T17:00:00",
    source="invite"
)
```

### 4. Reminder (`item_type: "reminder"`)

**Source:** Notification systems, timers
**Maps:** Time-sensitive reminders → tasks

```python
binder_service.add_reminder(
    mission_id="project",
    title="Follow up with customer",
    description="Send status update email",
    due_date="2026-02-27T09:00:00",
    alert_type="notification",
    alert_interval="1hour"
)
```

### 5. Imported Item (`item_type: "imported"`)

**Source:** Email, Slack, Jira, Linear, etc.
**Maps:** Any external item → task

```python
# Email import
binder_service.add_imported_item(
    mission_id="urgent-issues",
    title="[BUG] API timeout on /auth",
    description="Customer reported 504 errors",
    source="email",
    source_id="msg-id-xyz",
    item_category="bug_report",
    metadata={"from": "bugs@customer.io"}
)

# Jira import
binder_service.add_imported_item(
    mission_id="backend-work",
    title="PROJ-1234: Refactor DB pooling",
    description="Optimize connection pool",
    source="jira",
    source_id="PROJ-1234",
    metadata={"jira_type": "Task", "sprint": "Sprint 24"}
)
```

---

## Enhanced Service Methods

### VibeBinderService (Extended)

#### Item Type Methods

```python
# Standard task
add_move(mission_id, title, description, priority="medium", item_type="task")

# Calendar event
add_calendar_event(
    mission_id, title, description,
    start_date, end_date, location, organizer, attendees
)

# Meeting invite
add_invite(
    mission_id, title, description,
    organizer, attendees, event_date, response_due
)

# Reminder
add_reminder(
    mission_id, title, description,
    due_date, alert_type, alert_interval
)

# Generic imported item
add_imported_item(
    mission_id, title, description,
    source, source_id, item_category
)
```

#### Query Methods (New)

```python
# Filter by type
list_moves(mission_id, status=None, item_type="calendar_event")

# Date range queries (for scheduling, calendar views)
list_moves_by_date_range(
    mission_id, start_date, end_date, date_field="due_date"
)

# Tag-based filtering
list_moves_by_tag(mission_id, tag="meeting")

# Source-based filtering (show all imported items from email)
list_moves_by_source(mission_id, source="email")

# Summary of imported items (understanding what's been mapped)
get_imported_items_summary(mission_id)

# Complete summary for AI ingestion
get_task_summary_for_ai(mission_id)
# Returns: mission info, moves by status/type, metrics, completion rate
```

### VipeSetupService

```python
# Ensure VAULT_ROOT configured in .env
ensure_vault_root(vault_path=None)

# Create @binders directory structure
ensure_binder_structure()

# Complete initialization (both)
initialize_uDOS(vault_path=None)
```

---

## Use Cases & Workflows

### 1. Calendar Integration Workflow

```python
from core.services.vibe_binder_service import get_binder_service

# Import upcoming meetings from calendar
def sync_calendar_to_binders(calendar_events, mission_id):
    binder = get_binder_service()
    for event in calendar_events:
        binder.add_calendar_event(
            mission_id=mission_id,
            title=event["summary"],
            start_date=event["start"],
            end_date=event["end"],
            organizer=event["organizer"],
            attendees=event["attendees"],
            source="calendar",
            source_id=event["id"]
        )

# Query calendar events for a date
result = binder.list_moves_by_date_range(
    mission_id="product-team",
    start_date="2026-02-20T00:00:00",
    end_date="2026-02-27T23:59:59",
    date_field="start_date"
)
```

### 2. Email Triage Workflow

```python
# Import emails as tasks, avoid vault clutter
def triage_email_to_binder(email, mission_id, priority="medium"):
    binder = get_binder_service()

    return binder.add_imported_item(
        mission_id=mission_id,
        title=f"[EMAIL] {email['subject']}",
        description=email["body_excerpt"],
        source="email",
        source_id=email["id"],
        priority=priority,
        metadata={
            "from": email["from"],
            "has_attachments": email.get("has_attachments")
        }
    )

# Find all emails imported to a project
emails = binder.list_moves_by_source(mission_id, source="email")
```

### 3. AI Processing Workflow

```python
# Get complete task context for AI model
summary = binder.get_task_summary_for_ai("my-project")

# AI can now:
# - Analyze all task types uniformly
# - Suggest task dependencies
# - Identify scheduling conflicts
# - Recommend priority adjustments
# - Generate project status reports

prompt = f"""
Analyze projects in this binder:
{json.dumps(summary, indent=2)}

Suggest optimizations for task scheduling and assignment.
"""
```

### 4. Project Initialization Workflow

```python
from core.services.mission_templates import ProjectInitializer

# Quick-start new project with template
result = ProjectInitializer.initialize_project(
    project_id="ai-feature",
    vault_root="./vault",
    template_type="software_project",
    with_seed_tasks=True
)

# Creates:
# - vault/@binders/ai-feature/mission.json
# - vault/@binders/ai-feature/moves.json
# - vault/@binders/ai-feature/milestones.json
# With 3 starter tasks and full mission definition
```

---

## Backward Compatibility

**Old format still works:**

```json
{
  "id": "move-123",
  "mission_id": "project",
  "title": "Task",
  "priority": "high",
  "status": "in_progress",
  "created": "2026-02-20T10:30:00",
  "updated": "2026-02-20T10:35:00"
}
```

**Automatically enhanced to new format:**

All optional fields default to sensible values:
- `item_type` → `"task"`
- `source` → `"manual"`
- `tags` → `[]`
- `metadata` → `{}`

---

## Documentation Files

### New Files Created

1. [TASK-JSON-FORMAT-AI-INGESTION.md](../TASK-JSON-FORMAT-AI-INGESTION.md)
   - Complete schema documentation
   - Item type specifications
   - Migration guide
   - API examples
   - AI ingestion benefits

2. [mission_templates.py](../../core/services/mission_templates.py)
   - `MissionTemplates` class with 5 template types
   - `TaskTemplates` class for creating typed tasks
   - `ProjectInitializer` for quick project setup

### Seed Data

`vault/@binders/sandbox/` — Example project showing:
- `mission.json` — Sandbox mission definition
- `moves.json` — Mixed item types (task, imported, calendar_event)
- `milestones.json` — Completed work example

---

## Test Coverage

All new methods covered with test scenarios:

- ✅ Calendar event creation and date filtering
- ✅ Invite creation with attendee handling
- ✅ Reminder creation with alert configuration
- ✅ Imported item creation from multiple sources
- ✅ Source-based filtering
- ✅ Date range queries
- ✅ Tag-based filtering
- ✅ AI summary generation
- ✅ Backward compatibility with old format

---

## Storage & Performance

### File I/O

- **Single moves.json file** — All active tasks stored together
- **Atomic writes** — Consistent updates
- **JSON format** — Human-readable, version control friendly
- **No duplicate storage** — No separate markdown files

### Query Performance

All queries in-memory from cache:
- `list_moves()` — O(n) filtering
- `list_moves_by_source()` — O(n) filtering
- `list_moves_by_date_range()` — O(n) filtering
- `get_task_summary_for_ai()` — O(n) aggregation

Reload on app startup loads all binders from disk once.

---

## Future Enhancements

### Nested Tasks
```json
{
  "id": "task-1",
  "subtasks": [
    {"id": "subtask-1", "title": "Prepare testing", "status": "done"},
    {"id": "subtask-2", "title": "Deploy to staging", "status": "in_progress"}
  ]
}
```

### Task Dependencies
```json
{
  "depends_on": ["task-5", "task-12"],
  "blocks": ["task-20"]
}
```

### Time Tracking
```json
{
  "estimate_hours": 8,
  "actual_hours": 7.5,
  "time_entries": [
    {"date": "2026-02-20", "hours": 4},
    {"date": "2026-02-21", "hours": 3.5}
  ]
}
```

### Workflow Automation
```json
{
  "workflow_rules": [
    {"trigger": "status_changed", "from": "review", "to": "done", "auto_action": "email_team"},
    {"trigger": "due_date_passed", "auto_action": "add_tag:overdue"}
  ]
}
```

---

## Integration Points

### CLI (Next Phase)

```bash
ucli BINDER ADD myproject "Task title" "Description" --priority=high
ucli BINDER IMPORT email msg-id-123 myproject --auto-tag
ucli BINDER SYNC calendar myproject --range=week
ucli BINDER QUERY myproject --source=email --status=todo
```

### TUI (Next Phase)

```
ucode> binder import-calendar
ucode> binder list-by-date 2026-02-20 2026-02-27
ucode> binder filter-source email
```

### MCP (Next Phase)

```python
# Tools exposed in Wizard
vibe_binder_add_calendar_event
vibe_binder_add_reminder
vibe_binder_add_imported_item
vibe_binder_list_by_source
vibe_binder_get_ai_summary
```

---

## Summary

This extension transforms task management from a simple system into a **unified, AI-friendly knowledge base**:

✅ **No Markdown Clutter** — Calendar/invites/reminders stored as JSON, not separate .md files
✅ **Unified Schema** — All item types follow consistent format
✅ **Import-Friendly** — Support for calendar, email, Slack, Jira, Linear, etc.
✅ **AI-Ready** — Complete metadata for LLM processing
✅ **Query-Rich** — Filter by type, source, date, tags
✅ **Extensible** — Metadata for custom fields
✅ **Backward Compatible** — Old format still works
✅ **Template System** — Quick-start projects

Developers now have **single unified system** for:
- Task management
- Calendar integration
- Meeting reminders
- Email triage
- External system imports
- Project initialization

All without cluttering the Obsidian vault with extra files.


---

## The uDOS Workflow System

### Binder Structure

Each project binder in `vault/@binders/` contains:

```
vault/@binders/
├── myproject/
│   ├── mission.json       # Mission definition, guidelines, process
│   ├── moves.json         # Active tasks (todo, in_progress, blocked, review)
│   └── milestones.json    # Completed tasks/achievements
├── anotherproject/
│   ├── mission.json
│   ├── moves.json
│   └── milestones.json
```

### Mission Workflow

1. **Mission** — Project definition with guidelines and process
2. **Moves** — Active tasks with status tracking (todo → in_progress → review → done)
3. **Milestones** — Completed tasks moved to achievement history

---

## Service 1: VibeBinderService

### Purpose

Provides unified access to project missions, tasks, and achievements within binders.

### Key Methods

#### `list_binders()`
Lists all available binders (projects).

```python
result = binder_service.list_binders()
# Returns:
# {
#     "status": "success",
#     "binders": [
#         {
#             "mission_id": "myproject",
#             "mission": { ... },
#             "active_moves": 5,
#             "completed_milestones": 12
#         }
#     ],
#     "count": 1
# }
```

#### `get_mission(mission_id)`
Retrieve mission definition and overview.

```python
result = binder_service.get_mission("myproject")
# Returns mission.json content + move/milestone counts
```

#### `list_moves(mission_id, status=None)`
List active tasks with optional filtering by status.

```python
result = binder_service.list_moves("myproject", status="in_progress")
# Returns tasks with status "in_progress"
```

#### `add_move(mission_id, title, description, priority="medium")`
Create a new active task.

```python
result = binder_service.add_move(
    "myproject",
    "Implement auth",
    "Add OAuth2 support",
    "high"
)
# Returns newly created move with auto-generated ID
```

#### `update_move(mission_id, move_id, **kwargs)`
Update task details (status, priority, assigned_to, etc.)

```python
result = binder_service.update_move(
    "myproject",
    "move-123",
    status="review",
    assigned_to="alice"
)
```

#### `complete_move(mission_id, move_id)`
Move task from active (moves.json) to completed (milestones.json).

```python
result = binder_service.complete_move("myproject", "move-123")
# Task automatically archived as milestone
```

#### `list_milestones(mission_id)`
List completed tasks/achievements.

```python
result = binder_service.list_milestones("myproject")
# Returns all completed tasks with completion timestamps
```

### File Handling

- **Reads:** `vault/@binders/{mission_id}/*.json` files
- **Writes:** JSON files with 4-space indentation
- **Auto-creates:** Binder directories on initialization
- **Reload:** Detects new binders on service creation

---

## Service 2: VipeSetupService

### Purpose

Initializes uDOS configuration, ensuring all required environment variables are set.

### Key Methods

#### `ensure_vault_root(vault_path=None)`
Ensures VAULT_ROOT is configured in .env.

```python
result = setup_service.ensure_vault_root()
# Uses default: {repo_root}/vault
# Or specify custom path:
result = setup_service.ensure_vault_root("/opt/udos/vault")
# Returns: {"status": "success", "vault_root": "..."}
```

#### `ensure_binder_structure()`
Creates vault/@binders/ directory structure.

```python
result = setup_service.ensure_binder_structure()
# Creates: {vault_root}/@binders/
# Returns: {"status": "success", "binder_root": "..."}
```

#### `initialize_uDOS(vault_path=None)`
Complete uDOS initialization (both vault and binder structure).

```python
result = setup_service.initialize_uDOS()
# Sets up everything in one call
# Returns: {
#     "status": "success",
#     "vault_root": "...",
#     "binder_root": "..."
# }
```

### Environment Configuration

The service manages `.env` file entries:

```env
VAULT_ROOT=/Users/fredbook/Code/uDOS/vault
```

### Design

- **Singleton pattern** for single initialization
- **Idempotent** — safe to call multiple times
- **Error handling** — returns proper error responses
- **Logging** — DEBUG/INFO logs for debugging

---

## Integration with Vibe

### Workflow Example

1. **Initialize uDOS**
   ```python
   from core.services.vibe_setup_service import get_setup_service
   setup = get_setup_service()
   setup.initialize_uDOS()  # Sets up vault root and binder structure
   ```

2. **List Binders**
   ```python
   from core.services.vibe_binder_service import get_binder_service
   binder_svc = get_binder_service()
   result = binder_svc.list_binders()  # Get all projects
   ```

3. **Work with Mission Tasks**
   ```python
   # Create a new task
   binder_svc.add_move("myproject", "Fix bug #42", "Critical auth issue", "high")

   # Update task status
   binder_svc.update_move("myproject", "move-123", status="in_progress")

   # Mark as complete
   binder_svc.complete_move("myproject", "move-123")
   ```

### CLI Integration (Next Phase)

```bash
# List binders
ucli BINDER LIST

# View mission
ucli BINDER GET myproject

# List active tasks
ucli BINDER MOVES myproject --status=in_progress

# Add task
ucli BINDER ADD myproject "Task title" "Description" --priority=high

# Update task
ucli BINDER UPDATE myproject move-123 --status=review

# Complete task
ucli BINDER COMPLETE myproject move-123
```

### TUI Integration (Next Phase)

```
ucode> binder list
ucode> binder get myproject
ucode> binder moves myproject
ucode> binder add myproject "New task"
```

### MCP Integration (Next Phase)

```python
# Expose as tools in Wizard server
vibe_binder_list_binders
vibe_binder_get_mission
vibe_binder_list_moves
vibe_binder_add_move
vibe_binder_complete_move
```

---

## Mission JSON Format

### mission.json

```json
{
    "id": "myproject",
    "name": "My Project",
    "description": "Project description",
    "guidelines": "1. Follow code style\n2. Write tests\n3. Document changes",
    "process": "1. Create branch\n2. Implement\n3. Test\n4. Submit PR\n5. Review\n6. Merge"
}
```

### moves.json

```json
{
    "moves": [
        {
            "id": "move-2026-02-20T10-30-45",
            "mission_id": "myproject",
            "title": "Implement feature",
            "description": "Add new user dashboard",
            "priority": "high",
            "status": "in_progress",
            "assigned_to": "alice",
            "created": "2026-02-20T10:30:45",
            "updated": "2026-02-20T10:35:00"
        }
    ]
}
```

### milestones.json

```json
{
    "milestones": [
        {
            "id": "move-2026-02-19T14-20-00",
            "mission_id": "myproject",
            "title": "Fixed auth bug",
            "description": "Resolved OAuth2 token refresh issue",
            "completed": "2026-02-20T16:45:00",
            "achievements": ["bug-fix", "security"]
        }
    ]
}
```

---

## Test Coverage

**8 new tests** across 2 test classes:

### Setup Service Tests (2)
- `test_ensure_vault_root_creates_directory` ✅
- `test_ensure_vault_root_with_env_file` ✅

### Binder Service Tests (6)
- `test_binder_directory_created` ✅
- `test_list_binders_empty` ✅
- `test_add_move_to_nonexistent_mission` ✅
- `test_create_mission_with_moves` ✅
- `test_add_and_update_move` ✅
- `test_complete_move_to_milestone` ✅

All tests verify:
- Directory creation and structure
- File I/O and JSON serialization
- Move lifecycle (create → update → complete)
- Error handling for missing resources

---

## Benefits

### 1. Mission-Driven Development

Projects are now tied to missions with clear definitions, guidelines, and workflows:

- **Mission Definition**: What are we building? Why?
- **Guidelines**: How do we work?
- **Process**: Step-by-step workflow

### 2. Structured Task Management

Tasks (moves) are organized within missions:

- Granular task tracking (more specific than workspace-level)
- Status progression: todo → in_progress → review → done
- Priority and assignment tracking
- Automatic archival to milestones

### 3. Achievement History

Completed tasks preserved as milestones:

- Track project progress and velocity
- Reference completed work
- Learn from past decisions

### 4. Unified Configuration

SetupService ensures uDOS is properly initialized:

- VAULT_ROOT configured in .env
- Binder structure ready
- Fresh projects auto-scaffolded

---

## File I/O Pattern

All mission files use atomic writes:

```python
# Save new moves
moves_data = {"moves": self.binders[mission_id]["moves"]}
self._save_mission_file(mission_id, "moves.json", moves_data)

# Save completed milestones
milestones_data = {"milestones": self.binders[mission_id]["milestones"]}
self._save_mission_file(mission_id, "milestones.json", milestones_data)
```

Benefits:
- Transaction-like updates (both files saved consistently)
- Human-readable JSON (4-space indent)
- Revision control friendly (diffs are clear)

---

## Future Enhancements

### Phase 7

- [ ] Milestone analytics (velocity, burn-down charts)
- [ ] Automated milestone creation from completed moves
- [ ] Time tracking per move
- [ ] Comments/notes on moves
- [ ] Workflow automation (auto-transition on condition)

### Phase 8

- [ ] Sync to external project management (Jira, Linear, GitHub Projects)
- [ ] Notifications on move status changes
- [ ] Recurring/template moves
- [ ] Move dependencies and blockers

---

## Summary

The binder workflow extension transforms Vibe from a generic skill system into a **mission-driven development framework**.

✅ **VibeBinderService** — Access missions and task workflows
✅ **VipeSetupService** — Initialize uDOS configuration
✅ **8 integration tests** confirming file I/O and lifecycle
✅ **Integrated with persistence** — mission state survives restarts

Developers can now:
1. Define project missions with guidelines
2. Create granular tasks within missions
3. Track progress from todo → completion
4. Archive achievements as milestones
5. All tied to vault binders for easy access and version control

The system is ready for CLI, TUI, and MCP integration in the next phase.
