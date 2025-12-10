# uDOS Keyboard Shortcuts (v1.2.22)

Complete reference for all keyboard shortcuts in the TUI smart input system.

## Navigation & Completion

### Arrow Keys (Always Available)
| Key         | Function                                    |
|-------------|---------------------------------------------|
| ↑ (Up)      | Previous completion OR previous history     |
| ↓ (Down)    | Next completion OR next history             |
| ← (Left)    | Move cursor left                            |
| → (Right)   | Move cursor right OR accept completion      |

### Numpad Navigation (When Keypad Enabled)

**Priority 1: Completion Menu Open**
| Key | Function                  | Example                      |
|-----|---------------------------|------------------------------|
| 8   | Navigate UP in menu       | Type 'r' → 8 → REBOOT        |
| 2   | Navigate DOWN in menu     | Type 'r' → 2 → READ          |
| 5   | Accept selected item      | Type 'r' → 8 → 5 → REBOOT    |
| 6   | Accept selected item      | Same as 5                    |

**Priority 2: Buffer Empty (No Menu)**
| Key | Function                  | Example                      |
|-----|---------------------------|------------------------------|
| 8   | Previous command          | Empty → 8 → STATUS (if recent)|
| 2   | Next command              | After 8 → 2 → back to start  |
| 4   | Page up (in pager)        | Scroll output up             |
| 6   | Page down (in pager)      | Scroll output down           |
| 5   | Submit command            | Empty → 5 → execute          |
| 1   | History back              | Go to older command          |
| 3   | History forward           | Go to newer command          |
| 7   | Undo                      | Undo last edit               |
| 9   | Redo                      | Redo last undo               |
| 0   | Toggle file browser       | Open/close file picker       |

**Priority 3: Typing Text (No Menu)**
| Key | Function                  | Example                      |
|-----|---------------------------|------------------------------|
| 0-9 | Insert digit              | "XP " → 100 → "XP 100"       |

### Tab & Escape
| Key   | Function                                    |
|-------|---------------------------------------------|
| Tab   | Trigger completions OR navigate to next     |
| Esc   | Close completion menu                       |

## History Navigation

### Command History (Like Bash)
| Shortcut  | Function                  | Description                    |
|-----------|---------------------------|--------------------------------|
| ↑         | Previous command          | Navigate through history       |
| ↓         | Next command              | Navigate through history       |
| Ctrl+P    | Previous command          | Alternative to ↑               |
| Ctrl+N    | Next command              | Alternative to ↓               |
| Ctrl+R    | Reverse search            | Search history interactively   |
| Numpad 1  | History back              | Go to older command            |
| Numpad 3  | History forward           | Go to newer command            |

**Reverse Search (Ctrl+R):**
```
Press Ctrl+R → Type search term → Match appears → Enter to use
Example: Ctrl+R → "status" → Shows last STATUS command → Enter
```

## Cursor Movement

### Basic Movement
| Shortcut  | Function                  | Like Bash/Emacs |
|-----------|---------------------------|-----------------|
| Ctrl+A    | Start of line             | ✅              |
| Ctrl+E    | End of line               | ✅              |
| Ctrl+B    | Move left (1 char)        | ✅              |
| Ctrl+F    | Move right (1 char)       | ✅              |
| ←         | Move left                 | Standard        |
| →         | Move right                | Standard        |
| Home      | Start of line             | Standard        |
| End       | End of line               | Standard        |

## Text Editing

### Delete/Cut Operations
| Shortcut  | Function                  | Like Bash/Emacs |
|-----------|---------------------------|-----------------|
| Ctrl+K    | Delete to end of line     | ✅              |
| Ctrl+U    | Delete to start of line   | ✅              |
| Ctrl+W    | Delete word before cursor | ✅              |
| Ctrl+D    | Delete char under cursor  | ✅              |
| Backspace | Delete char before cursor | Standard        |
| Delete    | Delete char under cursor  | Standard        |

### Undo/Redo
| Shortcut  | Function                  |
|-----------|---------------------------|
| Ctrl+Z    | Undo last edit            |
| Numpad 7  | Undo (when keypad on)     |
| Numpad 9  | Redo (when keypad on)     |

## Screen Control

| Shortcut  | Function                  | Description                    |
|-----------|---------------------------|--------------------------------|
| Ctrl+L    | Clear screen              | Clears terminal display        |
| Numpad 4  | Page up                   | Scroll pager up                |
| Numpad 6  | Page down                 | Scroll pager down              |

## Completion Menu Controls

### When Menu is Open
| Key       | Function                  |
|-----------|---------------------------|
| ↑/↓       | Navigate suggestions      |
| Numpad 8  | Navigate up               |
| Numpad 2  | Navigate down             |
| Tab       | Next suggestion           |
| Shift+Tab | Previous suggestion       |
| Enter     | Accept selected           |
| Numpad 5  | Accept selected           |
| →         | Accept selected           |
| Numpad 6  | Accept selected           |
| Esc       | Close menu                |

### Triggering Completions
| Action                    | Result                              |
|---------------------------|-------------------------------------|
| Type 'r'                  | Shows: READ, REBOOT, REPAIR, etc.   |
| Type 'reb'                | Shows: REBOOT, REBUILD              |
| Press Tab                 | Manually trigger completions        |
| Keep typing               | Auto-updates suggestions            |

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════════╗
║                  uDOS KEYBOARD SHORTCUTS v1.2.22              ║
╠═══════════════════════════════════════════════════════════════╣
║ NAVIGATION         │ HISTORY           │ EDITING              ║
║ ↑↓ Navigate       │ Ctrl+R Search     │ Ctrl+A Start         ║
║ ←→ Move cursor    │ Ctrl+P/N History  │ Ctrl+E End           ║
║ Tab Suggest       │ 1/3 Back/Forward  │ Ctrl+K Delete→       ║
║ Esc Close menu    │ ↑↓ Prev/Next     │ Ctrl+U Delete←       ║
║                    │                   │ Ctrl+W Del word      ║
╠═══════════════════════════════════════════════════════════════╣
║ NUMPAD (KEYPAD MODE)                                          ║
║ Empty: 8↑ 2↓ 5✓ 1⟲ 3⟳ 4⇞ 6⇟ 0☰                              ║
║ Menu:  8↑ 2↓ 5✓ 6→ (navigate/accept)                          ║
║ Text:  0-9 (insert digits)                                    ║
╚═══════════════════════════════════════════════════════════════╝
```

## Examples

### Example 1: Find and Run Old Command
```
1. Press Ctrl+R (reverse search)
2. Type: "status"
3. Match appears: "STATUS --health"
4. Press Enter → executes command
```

### Example 2: Quick Command Completion
```
1. Type: r
2. Menu shows: READ, REBOOT, REPAIR, RUN, etc.
3. Press 8 (up) → REBOOT selected
4. Press 5 (accept) → "REBOOT" entered
5. Press Enter → executes
```

### Example 3: Edit Command from History
```
1. Press ↑ → previous command appears
2. Press Ctrl+A → cursor to start
3. Type new text
4. Press Ctrl+E → cursor to end
5. Add more text
6. Press Enter → execute modified command
```

### Example 4: Clean Up Mistake
```
1. Type: "STAUTS --health" (typo)
2. Press Ctrl+U → delete entire line
3. Type: "STATUS --health" (correct)
4. Press Enter
```

## Tips & Tricks

1. **Fast History Search:** Ctrl+R is faster than pressing ↑ multiple times
2. **Completion Navigation:** Use 8/2 on numpad for one-handed navigation
3. **Quick Clear:** Ctrl+U deletes entire input (faster than backspace)
4. **Word Delete:** Ctrl+W removes last word (useful for correcting arguments)
5. **Screen Cleanup:** Ctrl+L clears clutter without exiting
6. **Multi-Column View:** Completions show in columns for easier browsing
7. **Context-Aware:** Numpad switches between navigation/text based on context

## Enable/Disable Features

```bash
# Enable keypad navigation
uDOS> TUI ENABLE KEYPAD

# Disable keypad navigation
uDOS> TUI DISABLE KEYPAD

# Check TUI status
uDOS> TUI STATUS
```

## Troubleshooting

**Q: Arrow keys not working?**  
A: Check if you're in fallback mode. Smart input requires TTY support.

**Q: Completions not showing?**  
A: Press Tab to manually trigger. Ensure `complete_while_typing=True`.

**Q: Ctrl+R not working?**  
A: Verify terminal supports it (should work in most terminals).

**Q: Numpad inserting digits when I want navigation?**  
A: Numpad only navigates when:
- Completion menu is open, OR
- Buffer is empty (no text typed)

**Q: Only seeing 1 completion instead of many?**  
A: Ensure `complete_style=MULTI_COLUMN` and `reserve_space_for_menu=15`.

---

**Last Updated:** v1.2.22 (December 9, 2025)  
**See Also:** `wiki/TUI-Smart-Input-Guide.md`, `wiki/TUI-System-Guide.md`
