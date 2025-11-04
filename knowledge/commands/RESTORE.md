# RESTORE Command

## Overview
Display session history and perform bulk undo operations to return to previous session states.

## Syntax
```
RESTORE              # Show session history (same as RESTORE LIST)
RESTORE LIST         # Show session history
RESTORE <session#>   # Restore to specific session (future feature)
```

## uCODE Format
```
[SYSTEM|RESTORE]        # Lists sessions
[SYSTEM|RESTORE*LIST]   # Lists sessions
[SYSTEM|RESTORE*42]     # Restore to session 42 (planned)
```

## Description
The RESTORE command provides session-level recovery capabilities. It displays the current session number and allows viewing session history. Future versions will support bulk undo operations to restore to previous sessions.

## Current Features (v1.0.7)

### Session History Display
Shows current session number and usage instructions.

```
╔════════════════════════════════════════════════════════════════════════════╗
║  📜 SESSION HISTORY                                                        ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Current Session: #194                                                     ║
║                                                                            ║
║  Use RESTORE <session_num> to restore to a previous session.               ║
║  All actions after that session will be undone.                            ║
║                                                                            ║
║  💡 Tip: Use HISTORY command for detailed command history.                 ║
╚════════════════════════════════════════════════════════════════════════════╝
```

## Examples

### Check Current Session
```
uDOS> RESTORE
╔════════════════════════════════════════════════════════════════════════════╗
║  📜 SESSION HISTORY                                                        ║
║  Current Session: #150                                                     ║
╚════════════════════════════════════════════════════════════════════════════╝
```

### Alias Usage
```
uDOS> RESTORE LIST
# Same output as RESTORE
```

## Planned Features (v1.0.8+)

### Bulk Undo to Session
```
uDOS> RESTORE 100
🔄 Restoring to session #100...

✅ Restored 50 operations
📍 Current position: Session #100
```

### Named Checkpoints
```
uDOS> HISTORY SNAPSHOT before_changes
✅ Checkpoint 'before_changes' created at session #145

uDOS> RESTORE before_changes
🔄 Restoring to checkpoint 'before_changes'...
✅ Restored to session #145
```

### Timeline View
```
uDOS> HISTORY STATES
╔════════════════════════════════════════════════════════════════════════════╗
║  📊 STATE TIMELINE                                                         ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Session #140  ─  Initial state                                           ║
║  Session #145  ●  'before_changes' checkpoint                              ║
║  Session #148  │  3 panel operations                                       ║
║  Session #150  ▶  Current position                                         ║
╚════════════════════════════════════════════════════════════════════════════╝
```

## Best Practices

1. **Check Before Restore**: Use `HISTORY` to review what will be undone
2. **Create Checkpoints**: Before major changes, create named checkpoints (future)
3. **Session Awareness**: Session numbers persist across uDOS restarts
4. **Combine with UNDO**: Use UNDO for recent changes, RESTORE for older sessions

## Related Commands
- `UNDO` - Reverse single operation
- `REDO` - Re-apply undone operation
- `HISTORY` - View detailed command history
- `HISTORY SNAPSHOT` - Create named checkpoint (planned)
- `HISTORY STATES` - View state timeline (planned)

## Technical Details

### Implementation
- **Handler**: `SystemCommandHandler.handle_restore()`
- **Logger Integration**: Uses `Logger.get_move_stats()` for session info
- **Bulk Undo**: Calls `ActionHistory.undo()` multiple times (planned)

### Session Management
- **Session Number**: Incremented on each uDOS startup
- **Persistence**: Stored in logger database
- **History Integration**: All commands logged with session context

## Use Cases

### Before Major Changes
```
uDOS> RESTORE  # Note current session
Current Session: #100

# Make changes...

# If something goes wrong:
uDOS> RESTORE 100  # Return to state before changes (future)
```

### Exploratory Work
```
# Try experimental features
uDOS> # ... various commands ...

# Return to known good state
uDOS> RESTORE <earlier_session>  # (future)
```

### Session Recovery
```
# After crash or unexpected behavior
uDOS> RESTORE
Current Session: #205

uDOS> HISTORY  # Review what happened
uDOS> RESTORE 200  # Go back before issues (future)
```

## Limitations

1. **Current Version**: v1.0.7 only shows session info (no actual restoration)
2. **Session-Based**: Cannot restore to arbitrary timestamps, only session numbers
3. **No Partial Restore**: Restores ALL actions since target session (bulk undo)

## Version History
- **v1.0.7**: Initial implementation with session display
- Session history integration with Logger
- Foundation for future bulk undo features
- **v1.0.8** (planned): Bulk undo to session numbers
- **v1.0.9** (planned): Named checkpoints and timeline view
