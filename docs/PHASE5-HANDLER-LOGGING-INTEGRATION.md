# Phase 5: Handler Logging Integration

**Status:** In Progress  
**Date Started:** 2026-01-28  
**Version:** v1.0.0  
**Author:** GitHub Copilot

## Overview

Phase 5 instruments all 29 command handlers with unified logging and performance tracking. This provides complete visibility into command execution, enabling performance optimization and debugging.

## What Phase 5 Delivers

1. **Handler Instrumentation Mixin** - `HandlerLoggingMixin` for automatic logging
2. **Command Trace Tracking** - Timing, events, errors for each command
3. **High-Value Handler Instrumentation** - First wave on 8 key handlers
4. **Logging Dashboard** - Enhanced LOGS command for handler analysis
5. **Performance Metrics** - Command execution time tracking and aggregation

## Instrumentation Pattern

### Using HandlerLoggingMixin

```python
from core.commands.base_handler import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin

class MapHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handler for MAP command - now with logging."""

    def handle(self, command, params, grid, parser):
        """Execute MAP command with automatic logging."""

        with self.trace_command(command, params) as trace:
            # Validate params
            if not self._validate_params(params):
                self.log_param_error(command, params, "Invalid parameter")
                trace.set_status('error')
                return error_output

            # Mark milestone
            trace.mark_milestone('params_validated')

            # Do work
            result = self._render_map(grid)
            trace.add_event('map_rendered', {'size': len(result)})

            # Mark completion
            trace.set_status('success')
            return result
```

### Key Methods

#### Context Manager: `trace_command()`

```python
with self.trace_command(command, params) as trace:
    # Automatic start/finish logging
    # Automatic error handling
    result = do_work()
    trace.add_event('milestone', {'data': 'value'})
    return result
```

**Features:**

- ✅ Automatic start/finish logging
- ✅ Automatic error tracking
- ✅ Parameter sanitization (removes passwords, API keys)
- ✅ Duration tracking
- ✅ Event recording

#### Record Events

```python
trace.add_event('operation_complete', {
    'items_processed': 42,
    'status': 'ok'
})
```

#### Set Status

```python
trace.set_status('success')  # or 'error', 'partial', 'cancelled'
```

#### Log Param Errors

```python
self.log_param_error(command, params, "Missing required file path")
```

#### Log Permission Errors

```python
self.log_permission_denied(command, "User role cannot execute MAP")
```

## Phase 5 Implementation Plan

### Stage 1: Create Instrumentation (CURRENT)

✅ Create `HandlerLoggingMixin` - DONE  
✅ Create `CommandTrace` class - DONE  
⏳ Document instrumentation pattern - IN PROGRESS

### Stage 2: Instrument High-Value Handlers

Priority order (8 handlers):

1. **MapHandler** - Most frequently used navigation command
   - Track render time, viewport size, layer access
2. **FindHandler** - Complex search with multiple options
   - Track search scope, results count, execution time
3. **PanelHandler** - Grid rendering and display
   - Track panel size, interpolation time, cache hits
4. **GotoHandler** - Location transitions
   - Track transition time, permission checks, pre-post state
5. **BagHandler** - Inventory management
   - Track item operations, inventory size, state changes
6. **GrabHandler** - Item pickup operations
   - Track success rate, weight calculations, grid updates
7. **TalkHandler** - NPC interactions
   - Track dialog parsing, response time, state changes
8. **ConfigHandler** - Settings management
   - Track config loads/saves, validation time, change impacts

**Estimated Time:** 2-3 hours (10-15 min per handler)

### Stage 3: Logging Dashboard

Enhance LOGS command to show:

```
[LOGS]
Command Execution Summary:
  Total Commands: 247
  Avg Duration: 0.045s
  Success Rate: 98.4%

Top 5 Slow Commands:
  1. MAP (0.231s avg)
  2. FIND (0.187s avg)
  3. GOTO (0.156s avg)
  4. PANEL (0.098s avg)
  5. CONFIG (0.087s avg)

Command Timeline (last 10):
  14:32:01 MAP [success] 0.045s
  14:32:05 FIND [success] 0.156s
  14:32:12 GRAB [success] 0.023s
  14:32:15 TALK [success] 0.089s
  ...
```

### Stage 4: Performance Optimization

Based on logging data:

- Identify slow commands
- Add caching where appropriate
- Optimize hot paths
- Track improvements over time

## Logging Output Examples

### Successful Command

```json
{
  "timestamp": "2026-01-28T14:32:01.234Z",
  "category": "command_start_navigation",
  "message": "MAP started",
  "metadata": {
    "command": "MAP",
    "params": ["layer1", "viewport"],
    "timestamp": "2026-01-28T14:32:01.234Z"
  }
}

{
  "timestamp": "2026-01-28T14:32:01.279Z",
  "category": "command_finish_navigation",
  "message": "MAP finished (success)",
  "metadata": {
    "command": "MAP",
    "duration_seconds": 0.045,
    "status": "success",
    "event_count": 2,
    "events": [
      {
        "name": "milestone",
        "timestamp": "2026-01-28T14:32:01.245Z",
        "elapsed_seconds": 0.011,
        "milestone": "params_validated"
      },
      {
        "name": "map_rendered",
        "timestamp": "2026-01-28T14:32:01.275Z",
        "elapsed_seconds": 0.041,
        "size": 2400
      }
    ],
    "timestamp": "2026-01-28T14:32:01.279Z"
  }
}
```

### Failed Command

```json
{
  "timestamp": "2026-01-28T14:33:15.892Z",
  "category": "command_finish_game_state",
  "message": "GRAB finished (error)",
  "metadata": {
    "command": "GRAB",
    "duration_seconds": 0.008,
    "status": "error",
    "event_count": 1,
    "error": "Item not found at location",
    "error_type": "GameError",
    "events": [
      {
        "name": "error_occurred",
        "timestamp": "2026-01-28T14:33:15.900Z",
        "elapsed_seconds": 0.008,
        "error_type": "GameError",
        "error_message": "Item not found at location"
      }
    ]
  }
}
```

## Handler Categories

Handlers are categorized for better analysis:

| Category       | Commands                                | Purpose              |
| -------------- | --------------------------------------- | -------------------- |
| **navigation** | MAP, PANEL, GOTO, FIND, TELL            | Movement and viewing |
| **game_state** | BAG, GRAB, SPAWN, SAVE, LOAD            | Game mechanics       |
| **system**     | SHAKEDOWN, REPAIR, RESTART, SETUP, USER | System operations    |
| **npc**        | NPC, TALK, REPLY                        | NPC interactions     |
| **wizard**     | CONFIG, PROVIDER, WIZARD, AI            | Wizard integration   |
| **other**      | All others                              | Miscellaneous        |

## Sensitive Data Protection

HandlerLoggingMixin automatically redacts:

- `password`, `key`, `token`, `secret`, `api_key`, `credentials`
- Long parameters (>100 chars) are truncated
- All examples shown as `[REDACTED]` in logs

Example:

```python
params = ["--password", "my_secret_123", "--file", "/long/path/to/file.txt"]
# Logged as:
# ["[REDACTED]", "[REDACTED]", "--file", "/long/path/to/file.txt"]
```

## Testing Phase 5

### Test Individual Handler

```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate

# Run TUI
python uDOS.py

# Execute instrumented command
[uCODE] > MAP

# Check logs
[uCODE] > LOGS

# Filter by command
[uCODE] > LOGS filter=MAP

# Show performance stats
[uCODE] > LOGS stats
```

### Test All Instrumented Handlers

```bash
# Run integration test
pytest core/tests/ -k "logging" -v

# Show code coverage for logging
pytest core/tests/ --cov=core/commands --cov-report=html
```

## Files Created This Phase

- `/core/commands/handler_logging_mixin.py` - Mixin and trace classes

## Files to Modify This Phase

1. `/core/commands/map_handler.py`
   - Add `HandlerLoggingMixin` inheritance
   - Wrap handle() with `trace_command()`
2. `/core/commands/find_handler.py`
   - Same pattern as MapHandler
3. `/core/commands/panel_handler.py`
   - Same pattern as MapHandler
4. `/core/commands/goto_handler.py`
   - Same pattern as MapHandler
5. `/core/commands/bag_handler.py`
   - Same pattern as MapHandler
6. `/core/commands/grab_handler.py`
   - Same pattern as MapHandler
7. `/core/commands/talk_handler.py`
   - Same pattern as MapHandler
8. `/core/commands/config_handler.py`
   - Same pattern as MapHandler
9. `/core/services/unified_logging.py`
   - Enhance LOGS command with stats and filtering

## Timeline

- **Stage 1** - Create instrumentation (DONE)
- **Stage 2** - Instrument 8 handlers (2-3 hours)
- **Stage 3** - Enhance LOGS command (1 hour)
- **Stage 4** - Performance optimization (ongoing)

**Total Phase 5 Time:** ~4 hours

## Success Criteria

✅ HandlerLoggingMixin created with full documentation  
✅ CommandTrace class with event tracking  
⏳ 8 high-value handlers instrumented  
⏳ LOGS command enhanced with stats  
⏳ All logs flowing to unified_logging  
⏳ Performance metrics aggregated  
⏳ No regressions in handler behavior

## Git Commits (This Phase)

**Commit 1 (Current):**

```
handler_logging_mixin: Create instrumentation framework

- Add HandlerLoggingMixin for automatic logging
- Add CommandTrace for event tracking
- Add parameter sanitization (redact passwords/keys)
- Add handler categorization system
- Documentation with examples and patterns
```

**Commit 2 (Next):** Instrument MapHandler, FindHandler, etc. (batch)

**Commit 3 (Final):** Enhance LOGS command with stats

## References

- [AGENTS.md](../../AGENTS.md) - Project architecture
- [core.instructions.md](../../.github/instructions/core.instructions.md) - Handler patterns
- [unified_logging.py](../services/unified_logging.py) - Logging system
- [PHASE4-USER-MANAGEMENT-COMPLETE.md](../../docs/PHASE4-USER-MANAGEMENT-COMPLETE.md) - Previous phase

---

**Status:** In Progress (Stage 1 Complete, Stage 2 Starting)  
**Next:** Instrument MapHandler (highest priority - most frequently used)  
**Estimated Completion:** 2026-01-28 (same day, 3-4 hours more work)
