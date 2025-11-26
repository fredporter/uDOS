# Enhanced BLANK Command - v1.0.12

## Overview

The Enhanced BLANK command (also aliased as CLEAR) provides intelligent screen clearing with multiple modes for different scenarios, from smart preserving of status information to complete system cleanup.

## Syntax

```bash
BLANK [mode] [options]
```

## Modes

### 1. Smart Clear (Default)
```bash
BLANK
```
- Clears screen while preserving 3-line status bar
- Keeps important system information visible
- Safe for continuous use
- **Best for**: Regular workflow clearing

### 2. Complete Wipe
```bash
BLANK ALL
```
- Full screen clear including scrollback buffer
- Removes all terminal history
- Fresh start environment
- **Best for**: Presentations, demos, screenshots

### 3. Buffer Only
```bash
BLANK BUFFER
```
- Clears scrollback buffer without touching screen
- Uses ANSI escape sequence `\033[3J`
- Screen content remains visible
- **Best for**: Cleaning up after verbose output

### 4. Precise Line Control
```bash
BLANK LAST <n>
```
- Clears last n lines from screen
- Uses cursor control with `\033[1A` and `\033[2K`
- Perfect for correcting mistakes
- **Best for**: Undoing typos, removing errors

Example:
```bash
LIST /nonexistent
# Error message appears
BLANK LAST 2
# Error removed
```

### 5. Component Clearing (With Safety)

#### Clear Grid Data
```bash
BLANK GRID
```
- Clears all panel content
- **Requires confirmation**
- Creates undo snapshot
- **Best for**: Starting fresh project

#### Clear Log Files
```bash
BLANK LOGS
```
- Removes log files from sandbox/logs/
- **Requires confirmation**
- Backs up before deletion
- **Best for**: Disk space management

#### Clear Command History
```bash
BLANK HISTORY
```
- Clears command history
- **Requires confirmation**
- Does not affect usage statistics
- **Best for**: Privacy or fresh start

## Safety Features

### Confirmation Prompts

Destructive operations require explicit confirmation:
```bash
BLANK GRID
# Output: ⚠️  This will clear all grid data. Continue? (y/n):
```

Type `y` to proceed, any other key to cancel.

### Undo Support

Grid clearing creates undo snapshots:
```bash
BLANK GRID
# Cleared all panels
UNDO
# Grid restored
```

### Backup Creation

Log clearing creates automatic backups:
```bash
BLANK LOGS
# Creates: sandbox/logs/backup_YYYYMMDD_HHMMSS/
```

## Cross-Platform Support

### Unix/Linux/macOS
- Uses `clear` command
- ANSI escape sequences
- Terminal control sequences

### Windows
- Uses `cls` command
- PowerShell compatible
- CMD compatible

## Use Cases

### 1. Daily Workflow
```bash
# Clean screen, keep context
BLANK
```

### 2. Before Screenshot
```bash
# Complete clean slate
BLANK ALL
```

### 3. After Verbose Command
```bash
# Command outputs 100 lines
SOME_COMMAND
# Clear scrollback but keep screen
BLANK BUFFER
```

### 4. Typo Correction
```bash
# Made a mistake
LOAD wrong_file.txt
# Outputs error
BLANK LAST 2
# Error removed
```

### 5. Project Reset
```bash
# Start fresh
BLANK GRID
# Confirm: y
# All panels cleared
```

### 6. Disk Cleanup
```bash
# Check log size
LIST sandbox/logs
# Too large
BLANK LOGS
# Confirm: y
# Logs cleared, backup created
```

## Technical Details

### ScreenManager Service

The ScreenManager (`core/services/screen_manager.py`) handles:
- Cross-platform terminal detection
- ANSI escape sequence generation
- Cursor position management
- Safe confirmation dialogs

### ANSI Sequences Used

- `\033[2J` - Clear screen
- `\033[H` - Move cursor to home
- `\033[3J` - Clear scrollback buffer
- `\033[1A` - Move cursor up one line
- `\033[2K` - Clear current line

### Integration

BLANK integrates with:
- **ActionHistory**: Undo support for grid clearing
- **Logger**: Tracks all clearing operations
- **FileSystem**: Safe file operations with backups

## Tips

### Smart Clearing Strategy

1. **Regular use**: `BLANK` - Smart clear
2. **Major transition**: `BLANK ALL` - Complete wipe
3. **After errors**: `BLANK LAST <n>` - Remove lines
4. **Project switch**: `BLANK GRID` - New workspace
5. **Maintenance**: `BLANK LOGS` - Cleanup storage

### Keyboard Shortcuts

Consider aliasing frequently used modes:
```bash
# In your .bashrc or .zshrc
alias cls='echo BLANK | ./start_udos.sh'
alias clsa='echo BLANK ALL | ./start_udos.sh'
```

### Safety First

Before using destructive modes:
1. Check current state with `STATUS`
2. Ensure work is saved with `SAVE`
3. Create manual backup if uncertain
4. Remember: UNDO works for BLANK GRID

## Related Commands

- **HELP** - Command documentation
- **STATUS** - System state
- **UNDO** - Reverse operations
- **SAVE** - Save work before clearing

## Examples

### Example 1: Clean Demo Environment
```bash
# Prepare for demo
BLANK ALL          # Complete clean
STATUS            # Verify state
HELP              # Show clean help
```

### Example 2: Fix Long Output
```bash
# Command creates huge output
TREE
# Too much scrolling
BLANK BUFFER      # Clear scrollback
# Screen still shows relevant info
```

### Example 3: Fresh Start
```bash
# Check current state
STATUS
SHOW GRID
# Lots of old data
BLANK GRID        # Clear panels
# Confirm: y
NEW GRID 3x3      # Create fresh grid
```

### Example 4: Remove Mistakes
```bash
# Made 3 typos
wrong command 1
wrong command 2
wrong command 3
# Remove them
BLANK LAST 6      # 3 commands × 2 lines each
# Clean slate
```

## Version History

- **v1.0.0**: Basic BLANK command
- **v1.0.12**: Complete enhancement with 7 modes

## See Also

- [v1.0.12 Release Notes](../../docs/releases/v1.0.12-RELEASE-NOTES.md)
- [ScreenManager Service](../../core/services/screen_manager.py)
- [HELP Command](./HELP-ENHANCED.md)
