# Phase 7: CLI/TUI/MCP Integration

**Status**: ✅ Complete (v1.4.4)  
**Date**: 2026-02-20  
**Tests**: 134/134 passing

## Overview

Phase 7 integrates the unified task management system (Phase 6 Extension) with user-facing interfaces:
- **uCLI** = Terminal User Interface (CLI shell)
- **uCODE** = Command protocol (runs inside uCLI)
- **Wizard MCP** = AI-assisted task/binder work through LLM tools
- **Vibe Skills** = Unified interface across all contexts

## Components

### 1. Wizard MCP Tools (vibe_mcp_integration.py)

14 new MCP tools exposing binder and uCLI functionality to Wizard/Vibe.

#### Binder Tools (data operations)
- `vibe_binder_list()` — List all binders/missions
- `vibe_binder_create()` — Create mission with optional template
- `vibe_binder_get()` — Get mission details
- `vibe_binder_add_task()` — Add task with metadata
- `vibe_binder_add_calendar_event()` — Add calendar event to mission
- `vibe_binder_add_import()` — Import item from external system (calendar, email, Jira, etc.)
- `vibe_binder_list_tasks()` — List moves with filtering (status, type)
- `vibe_binder_complete_task()` — Mark task done, move to milestones
- `vibe_binder_ai_summary()` — Get AI ingestion-friendly task summary

#### uCLI Tools (TUI views)
- `vibe_ucli_binder()` — Interactive binder/missions explorer
- `vibe_ucli_tasks()` — Tasks/moves browser with filtering
- `vibe_ucli_missions()` — Missions selector with detail view
- `vibe_ucli_search()` — Full-text search interface
- `vibe_ucli_statistics()` — Metrics and statistics dashboard
- `vibe_ucli_help()` — Help and documentation viewer

### 2. uCLI Command Handlers (vibe_cli_handler.py)

Shell commands for binder and TUI operations.

#### BINDER Commands
```
ucli BINDER LIST                              # List missions
ucli BINDER CREATE mission-id name [template] # New mission
ucli BINDER GET mission-id                   # Mission details
ucli BINDER ADD_TASK mission-id title [desc] # Add task
ucli BINDER ADD_CALENDAR mission-id title    # Add event
ucli BINDER ADD_IMPORT mission-id title src  # Import item
ucli BINDER LIST_TASKS mission-id [status]   # List tasks
ucli BINDER COMPLETE mission-id move-id      # Complete task
ucli BINDER AI_SUMMARY mission-id            # AI summary
```

#### UCLI Commands (TUI views)
```
ucli UCLI BINDER [mission-id]                  # Binder explorer
ucli UCLI TASKS mission-id [status] [type]    # Tasks browser
ucli UCLI MISSIONS                            # Missions selector
ucli UCLI SEARCH [query]                      # Search interface
ucli UCLI STATISTICS [mission-id]             # Dashboard
ucli UCLI HELP [topic]                        # Help viewer
```

### 3. Vibe Skill Mapper (vibe_skill_mapper.py)

Two unified skills:

#### binder Skill
Name: `binder`  
Type: Data operations  
Actions: 10 (list, create, get, add_task, add_calendar, add_import, list_tasks, update_task, complete_task, ai_summary)

#### ucli Skill
Name: `ucli`  
Type: TUI views  
Actions: 6 (binder, tasks, missions, search, statistics, help)

**Backward Compatibility**: `ucode` is aliased to `ucli` in registry for old scripts.

### 4. TUI Service Layer (vibe_tui_service.py)

Orchestrates interactive terminal UI operations.

```python
service = get_tui_service()

# Launch interactive viewers
service.launch_binder_ui(mission_id)
service.launch_tasks_ui(mission_id, status, item_type)
service.launch_missions_ui()
service.launch_search_ui(query)
service.launch_statistics_view(mission_id)
service.launch_help_ui(topic)
```

Returns JSON with:
- `status`: success/error
- `mode`: "interactive" or "view"
- `view`: name of view
- `controls`: keyboard/nav actions
- `rendered`: ASCII preview

## Usage Examples

### Shell (uCLI)
```bash
# Create a software project
ucli BINDER CREATE webui "Web UI Redesign" software_project

# Add tasks
ucli BINDER ADD_TASK webui "Design mockups" "Create component library designs"
ucli BINDER ADD_TASK webui "Frontend dev" "Implement React components"

# List tasks
ucli BINDER LIST_TASKS webui

# Mark complete
ucli BINDER COMPLETE webui move-uuid-1

# Launch interactive explorer
ucli UCLI BINDER webui

# List tasks interactively  
ucli UCLI TASKS webui

# Search everything
ucli UCLI SEARCH "component"
```

### AI/Wizard (MCP Tools)
```python
# Claude/Vibe can call these
{
  "tool_name": "vibe_binder_list",
  "arguments": {}
}

# Returns all missions with task counts, completion rates

{
  "tool_name": "vibe_binder_add_task",
  "arguments": {
    "mission_id": "webui",
    "title": "Setup CI/CD",
    "description": "Configure GitHub Actions for automated tests"
  }
}

# Returns created task with ID, timestamps, metadata

{
  "tool_name": "vibe_ucli_tasks",
  "arguments": {
    "mission_id": "webui",
    "status": "in_progress"
  }
}

# Returns interactive UI controls and preview
```

### Python (Services)
```python
from core.services.vibe_binder_service import get_binder_service
from core.services.vibe_tui_service import get_tui_service
from core.services.vibe_cli_handler import get_cli_handler

# Data operations
binder = get_binder_service()
binder.add_move("webui", "Design", "Create designs", "task")
binder.add_calendar_event("webui", "Design review", "2026-02-25", "2026-02-25")
summary = binder.get_task_summary_for_ai("webui")

# TUI operations
tui = get_tui_service()
tui.launch_binder_ui("webui")
tui.launch_tasks_ui("webui", status="in_progress")
tui.launch_search_ui("component")

# CLI routing
cli = get_cli_handler()
result = cli.execute("BINDER LIST")
result = cli.execute("UCLI MISSIONS")
```

## Architecture

### Data Flow
1. **Shell Input** (uCLI) → `vibe_cli_handler.execute()`
2. **Skill Router** → `_handle_binder()` or `_handle_ucli()`
3. **Service Calls** → `vibe_binder_service` or `vibe_tui_service`
4. **JSON Response** → Formatted for CLI/MCP/Wizard

### Skill Dispatch
```
Input: "BINDER LIST"
  ↓
Skill Detection: "binder" (lowercase from input)
  ↓
Handler: _handle_binder("LIST", [])
  ↓
Service: get_binder_service().list_binders()
  ↓
Response: {"status": "success", "binders": [...]}
```

### Aliasing
```
Input: "UCODE BINDER"
  ↓
Skill Lookup: get_skill("ucode")
  ↓
Registry: {"ucode": UCLI_SKILL} → UCLI_SKILL
  ↓
Handler: _handle_ucli("BINDER", [mission_id])
```

## Integration Points

### With Existing Systems
- **ucode dispatcher**: Routes BINDER/UCLI to new handlers
- **Vibe skills**: binder + ucli registered as 12 total actions
- **Wizard MCP**: 14 tools for Claude/Vibe integration
- **Vault**: Missions stored in vault/@binders/ with moves.json

### With Phase 6 Extension
- Uses unified JSON task format (moves.json)
- Supports all 5 item types (task, calendar, invite, reminder, imported)
- AI summary generation for LLM consumption
- Source tracking for imported items

## Testing

All tests passing (134/134):
- Unit tests for new handlers and services
- MCP integration tests for all 14 tools
- Backward compatibility tests (ucode alias)
- Format validation for CLI output

## What's Next (Phase 8)

External system sync:
- Calendar sync (Google, Outlook, Apple)
- Email ingestion pipeline
- Jira/Linear webhook handlers
- Slack integration
- Analytics and reporting

## Key Files

| File | Purpose |
|------|---------|
| `core/services/vibe_binder_service.py` | Unified task data layer (Phase 6) |
| `core/services/mission_templates.py` | Template system (Phase 6) |
| `core/services/vibe_tui_service.py` | TUI orchestration (Phase 7) |
| `core/services/vibe_cli_handler.py` | Command routing (updated) |
| `core/services/vibe_skill_mapper.py` | Skill registry (updated) |
| `wizard/mcp/vibe_mcp_integration.py` | MCP tool registration (updated) |
| `docs/TASK-JSON-FORMAT-AI-INGESTION.md` | Schema reference |
| `docs/WORKFLOW-TASK-IMPLEMENTATION-GUIDE.md` | Implementation patterns |

## Status Summary

✅ **Implemented**:
- 2 skills (binder data, ucli TUI views)
- 14 MCP tools
- 18 CLI commands (BINDER + UCLI)
- Full MCP integration
- TUI service layer
- Backward compatibility (ucode alias)

✅ **Tested**: All 134 tests passing

✅ **Documented**: This guide + method docstrings + examples

⏭️ **Next Phase**: External system synchronization

