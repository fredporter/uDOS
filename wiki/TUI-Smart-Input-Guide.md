# TUI Smart Input - Quick Reference (v1.2.22)

## Numpad Dual-Mode Behavior

The smart input system uses **context-aware numpad behavior** that changes based on whether you've typed any text:

### 🔵 Empty Command Line (Navigation Mode)

When the prompt is empty (no characters typed), numpad keys act as navigation shortcuts:

| Key | Icon | Function              | Description                          |
|-----|------|-----------------------|--------------------------------------|
| 8   | ↑    | Up Arrow              | Navigate previous completion/history |
| 2   | ↓    | Down Arrow            | Navigate next completion/history     |
| 4   | ←    | Page Up               | Scroll pager up                      |
| 6   | →    | Page Down             | Scroll pager down                    |
| 5   | ✓    | Select/Enter          | Accept completion or submit command  |
| 1   | ⟲    | History Back          | Previous command in history          |
| 3   | ⟳    | History Forward       | Next command in history              |
| 7   | ↶    | Undo                  | Undo last edit                       |
| 9   | ↷    | Redo                  | Redo last undo                       |
| 0   | ☰    | Menu                  | Toggle file browser                  |

**Example:**
```
🌀 _                    ← Empty prompt
Press 8                 → Navigate to previous command
Press 1                 → Go back in history
```

### 🟢 After Typing (Text Input Mode)

Once you've typed **any character** (even a single letter), numpad keys insert digits normally:

| Key | Inserts | Use Case                           |
|-----|---------|------------------------------------|
| 0-9 | 0-9     | Normal text input (numbers, args)  |

**Example:**
```
🌀 R_                   ← After 'R': numpad inserts digits
Press 8                 → Types "8" → "R8"
Press 2                 → Types "2" → "R82"
Press 5                 → Types "5" → "R825"
```

## Arrow Keys (Always Available)

Arrow keys work in **both modes** for navigation:

| Key         | Function                              |
|-------------|---------------------------------------|
| ↑ (Up)      | Previous completion or history entry  |
| ↓ (Down)    | Next completion or history entry      |
| ← (Left)    | Move cursor left                      |
| → (Right)   | Move cursor right or accept completion|

## Command Completion Features

### 1. Auto-Suggest as You Type
- Start typing a command (e.g., `R`)
- See **up to 25 matching commands** in dropdown
- Examples: `REBOOT`, `REPAIR`, `RUN`, `READ`, `REPORT`, etc.

### 2. Navigate Suggestions
- Use ↑/↓ arrows or numpad 8/2 (when buffer empty)
- Tab key to accept selected suggestion
- Esc key to dismiss suggestions

### 3. Command History Filtering
- Type first letter: `R`
- Press ↑/↓ to browse only commands starting with 'R'
- Smart filtering based on what you've typed

## Keyboard Shortcuts

### Cursor Movement
| Shortcut  | Function            |
|-----------|---------------------|
| Ctrl+A    | Start of line       |
| Ctrl+E    | End of line         |
| Ctrl+K    | Delete to end       |
| Ctrl+U    | Delete to start     |

### Editing
| Shortcut  | Function            |
|-----------|---------------------|
| Ctrl+Z    | Undo (also numpad 7)|
| Ctrl+Y    | Redo (also numpad 9)|
| Tab       | Accept suggestion   |
| Esc       | Cancel/dismiss      |

### History
| Shortcut  | Function            |
|-----------|---------------------|
| Ctrl+R    | Reverse search      |
| ↑/↓       | Navigate history    |
| Numpad 1  | History back        |
| Numpad 3  | History forward     |

## Enable/Disable Keypad Mode

```bash
# Enable keypad navigation
uDOS> TUI ENABLE KEYPAD

# Disable keypad navigation (numpad always types digits)
uDOS> TUI DISABLE KEYPAD

# Check status
uDOS> TUI STATUS
```

## Visual Indicators

### Completion Preview
```
🌀 REBO[OT - Restart uDOS]     ← Inline preview in gray
   ► REBOOT     - Restart uDOS    ← Selected suggestion
     REPAIR     - System health    ← Other matches
     RUN        - Execute script
```

### Scroll Indicators
```
🌀 STATUS                    ▲ 45%  ← Pager not at bottom
🌀 HELP                      ▼ 100% ← Pager at bottom
```

## Troubleshooting

### Numpad Not Working?
1. Check if keypad mode is enabled: `TUI STATUS`
2. Enable if needed: `TUI ENABLE KEYPAD`
3. Verify you're on empty prompt (no text typed)

### Suggestions Not Showing?
1. Type at least one character
2. Wait 100ms for autocomplete to update
3. Press Tab to manually trigger suggestions

### Arrow Keys Not Navigating?
1. Suggestions must be visible (completion menu open)
2. Use ↑/↓ to navigate, → or Tab to accept
3. If no suggestions, arrows navigate command history

## Examples

### Example 1: Quick Command Entry
```
🌀 _                    ← Empty prompt
Type: r                 → Shows: REBOOT, REPAIR, RUN...
Press: ↓ ↓              → Selects REPAIR
Press: Tab              → Accepts: REPAIR
Press: Enter            → Executes command
```

### Example 2: Navigation Without Typing
```
🌀 _                    ← Empty prompt
Press: 1                → Previous command (e.g., STATUS)
Press: 5                → Submit (executes STATUS)
```

### Example 3: Typing Numbers in Command
```
🌀 _                    ← Empty prompt
Type: X                 → XP shown in suggestions
Type: P                 → "XP" complete
Press: Space            → "XP "
Press: 1 0 0            → "XP 100" (numpad inserts digits)
Press: Enter            → Executes: XP 100
```

### Example 4: Browsing History
```
🌀 _                    ← Empty prompt
Type: r                 → Filter history to 'R' commands
Press: ↑                → REPAIR (if used recently)
Press: ↑                → REBOOT (if used before)
Press: ↓                → REPAIR (back to it)
Press: Tab              → Accept
```

## Performance Notes

- Suggestion generation: < 1ms
- Shows up to 25 matches (increased from 10 in v1.2.21)
- Zero lag for numpad mode switching
- Instant context switching between modes

## Version History

- **v1.2.22** - Fixed numpad navigation, strict buffer check
- **v1.2.21** - OK Assistant integration
- **v1.2.15** - TUI system with keypad support
- **v1.0.19** - Initial smart prompt implementation

---

**Need Help?** Run `HELP TUI` or `TUI --help` for more information.
