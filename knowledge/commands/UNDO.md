# UNDO Command

## Overview
Reverses the last reversible operation, restoring the system to its previous state.

## Syntax
```
UNDO
```

## uCODE Format
```
[SYSTEM|UNDO]
```

## Description
The UNDO command reverses the most recent action that was recorded in the action history. When an operation is undone, it is moved to the redo stack, allowing you to re-apply it later with the REDO command.

### Move Counter
- Each successful UNDO decrements the move counter by 1
- Failed UNDO attempts (empty stack) do not affect the move counter

## Supported Operations
The following operations can be undone:
- Panel creation (creates → removes)
- Panel deletion (removes → recreates)
- File saves (restores previous content)
- Grid modifications
- Configuration changes

## Examples

### Basic Usage
```
uDOS> UNDO
↩️  Undone: Removed panel 'temp_panel'
```

### Empty Stack
```
uDOS> UNDO
⚠️  Nothing to undo.
```

### Multiple Undo
```
uDOS> UNDO
↩️  Undone: Removed panel 'panel_3'

uDOS> UNDO
↩️  Undone: Removed panel 'panel_2'

uDOS> UNDO
↩️  Undone: Removed panel 'panel_1'
```

## Best Practices

1. **Use Before Critical Operations**: If unsure about a change, remember you can undo it
2. **Check History**: Use `HISTORY` to see what operations are in the undo stack
3. **Redo Available**: Undone operations remain in redo stack until new action performed
4. **Limited Depth**: Undo stack has maximum depth (default: 50 operations)

## Related Commands
- `REDO` - Re-apply last undone operation
- `RESTORE` - Bulk undo to previous session
- `HISTORY` - View command history and statistics

## Technical Details

### Implementation
- **Handler**: `SystemCommandHandler.handle_undo()`
- **Service**: `ActionHistory.undo()` in `history_manager.py`
- **Stack**: Deque-based with configurable max depth

### State Management
- Undo stack: LIFO (Last In, First Out)
- Redo stack: Cleared when new action performed
- Session logging: All undo operations logged for audit trail

## Version History
- **v1.0.7**: Initial implementation with ActionHistory integration
- Move counter adjustment support
- Integration with existing Logger system
