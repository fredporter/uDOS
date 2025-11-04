# REDO Command

## Overview
Re-applies the last operation that was undone with UNDO, restoring forward progress.

## Syntax
```
REDO
```

## uCODE Format
```
[SYSTEM|REDO]
```

## Description
The REDO command re-executes the most recent action that was reversed with UNDO. This allows you to "undo an undo", moving forward through your action history.

### Move Counter
- Each successful REDO increments the move counter by 1
- Failed REDO attempts (empty stack) do not affect the move counter

## Behavior

### Redo Stack Management
- REDO stack is populated when UNDO is used
- Performing a new action clears the entire redo stack
- Multiple REDO operations can be performed in sequence

## Examples

### Basic Undo/Redo Cycle
```
uDOS> CREATE PANEL test
✅ Panel 'test' created

uDOS> UNDO
↩️  Undone: Removed panel 'test'

uDOS> REDO
↪️  Redone: Created panel 'test'
```

### Empty Stack
```
uDOS> REDO
⚠️  Nothing to redo.
```

### Multiple Redo
```
uDOS> UNDO
↩️  Undone: Removed panel 'panel_3'

uDOS> UNDO
↩️  Undone: Removed panel 'panel_2'

uDOS> REDO
↪️  Redone: Created panel 'panel_2'

uDOS> REDO
↪️  Redone: Created panel 'panel_3'
```

### New Action Clears Redo
```
uDOS> UNDO
↩️  Undone: Removed panel 'test'

uDOS> CREATE PANEL new_panel
✅ Panel 'new_panel' created

uDOS> REDO
⚠️  Nothing to redo.  # Redo stack was cleared by new action
```

## Best Practices

1. **Use Immediately After UNDO**: REDO is most useful right after undoing something
2. **Be Aware of Stack Clearing**: Any new action clears the redo stack
3. **Chain Operations**: You can redo multiple operations in sequence
4. **Check Before Acting**: If unsure, use `HISTORY` to see command sequence

## Common Workflows

### Exploratory Changes
```
# Try something
CREATE PANEL experiment

# Don't like it, undo
UNDO

# Actually, bring it back
REDO
```

### Multi-step Reversal
```
# Made 3 changes, undo all
UNDO
UNDO
UNDO

# Actually, keep the last 2
REDO
REDO
```

## Related Commands
- `UNDO` - Reverse last operation
- `RESTORE` - Bulk undo to previous session
- `HISTORY` - View command history

## Technical Details

### Implementation
- **Handler**: `SystemCommandHandler.handle_redo()`
- **Service**: `ActionHistory.redo()` in `history_manager.py`
- **Stack**: Deque-based LIFO structure

### State Management
- Redo stack: Populated by UNDO operations
- Stack clearing: Triggered by any new reversible action
- Move counter: Adjusted forward (+1) on successful redo

## Limitations

1. **Redo Stack Persistence**: Redo stack is session-only (not saved across reboots)
2. **Action Clearing**: Cannot redo after performing new actions
3. **Maximum Depth**: Limited by undo stack depth (default: 50)

## Version History
- **v1.0.7**: Initial implementation
- Integration with ActionHistory system
- Move counter synchronization
