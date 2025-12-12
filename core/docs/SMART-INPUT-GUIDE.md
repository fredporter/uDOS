# Smart Input System - User Guide

**Version:** uDOS v1.2.22+  
**Status:** Enhanced Dynamic Autocomplete

---

## Overview

The Smart Input system provides **real-time, dynamic autocomplete** with visual feedback as you type. No need to press Tab constantly - suggestions appear automatically!

---

## Key Features

### 1. **Auto-Show Completions**
- Completions appear **automatically as you type**
- No need to press Tab to see suggestions
- Real-time feedback for every character

### 2. **Multi-Word Command Support**
Intelligent handling of two-word commands:
- `POKE START` / `POKE STOP` / `POKE STATUS`
- `CLOUD GENERATE` / `CLOUD RESOLVE` / `CLOUD BUSINESS`
- `CONFIG GET` / `CONFIG SET` / `CONFIG LIST`
- `WORKFLOW NEW` / `WORKFLOW RUN` / `WORKFLOW STATUS`
- `MISSION START` / `MISSION PAUSE` / `MISSION COMPLETE`
- `TUI ENABLE` / `TUI DISABLE`
- `GUIDE WATER` / `GUIDE FIRE` / `GUIDE SHELTER`

### 3. **Smart Selection**
- **Arrow Keys** (↑/↓) navigate through suggestions
- **Tab** or **Right Arrow** (→) accepts current suggestion
- **Enter** executes the command you typed
- **Escape** closes the menu

### 4. **Visual Feedback**
- **Green text** on black background for visibility
- **Bold highlight** on selected completion
- **Gray ghost text** shows history suggestions
- **Metadata** displays command descriptions and options

### 5. **History Integration**
- Gray "ghost text" suggests commands from history
- **Ctrl+R** for reverse search
- **↑/↓** browse history when no completions shown

---

## Keyboard Shortcuts

### Navigation
| Key | Action |
|-----|--------|
| **↑** | Previous completion / Previous history item |
| **↓** | Next completion / Next history item |
| **←** | Move cursor left / Close menu at start |
| **→** | Move cursor right / Accept completion at end |
| **Tab** | Accept current completion / Show completions |
| **Ctrl+Space** | Force show all completions |

### Execution
| Key | Action |
|-----|--------|
| **Enter** | Execute command (closes menu first) |
| **Escape** | Close menu / Clear input / Exit |

### Editing
| Key | Action |
|-----|--------|
| **Ctrl+A** | Move to start of line |
| **Ctrl+E** | Move to end of line |
| **Ctrl+K** | Delete from cursor to end |
| **Ctrl+U** | Delete from cursor to start |
| **Ctrl+W** | Delete previous word |
| **Ctrl+D** | Delete character under cursor |
| **Ctrl+L** | Clear screen |

### History
| Key | Action |
|-----|--------|
| **Ctrl+R** | Reverse search history |
| **Ctrl+P** | Previous in history (like ↑) |
| **Ctrl+N** | Next in history (like ↓) |

### Help
| Key | Action |
|-----|--------|
| **F1** | Show help for current command |

---

## Usage Examples

### Example 1: Single-Word Command
```
Type: STA
↓ Autocomplete shows:
  ► STATUS        Show system status
    START         Start service
    STATS         Show statistics
    
Press Tab or → to accept "STATUS"
Press Enter to execute "STA" (partial command)
```

### Example 2: Multi-Word Command
```
Type: POKE
↓ Autocomplete shows:
  ► POKE          Pokémon battle system → START, STOP, STATUS, EXPORT, IMPORT

Type: POKE S
↓ Autocomplete shows:
  ► START         Start Pokémon battle simulation
    STOP          Stop current battle
    STATUS        Show battle status
    
Press Tab to complete "START"
Final: POKE START
```

### Example 3: With Options
```
Type: CLOUD GENERATE
↓ Autocomplete shows:
  ► KEYWORDS      Generate keywords with AI
    
Type: CLOUD GENERATE KEYWORDS
↓ Autocomplete shows:
  ► --location    Location context
    --type        Business type
    --upy         Export as uPY variables
    
Press Tab to accept "--location"
Type: CLOUD GENERATE KEYWORDS --location "Sydney"
```

### Example 4: Using History
```
(Previous command: STATUS --health)

Type: ST
↓ Gray ghost text appears: "ATUS --health"
Press → to accept the suggestion
Press Enter to execute
```

---

## Configuration

### Enable/Disable Smart Input
```bash
# In uDOS
TUI ENABLE SMART_INPUT   # Enable smart input
TUI DISABLE SMART_INPUT  # Disable (fallback to basic input)
```

### Fallback Mode
Smart Input automatically falls back to basic mode if:
- Terminal doesn't support advanced features
- `TERM=dumb` or `TERM=unknown`
- Not running in a TTY (e.g., piped input)
- Smart input disabled in TUI config

---

## Multi-Word Commands Reference

### CLOUD (Business Intelligence)
- `CLOUD GENERATE` - Generate keywords/data
- `CLOUD RESOLVE` - Resolve location to TILE code
- `CLOUD BUSINESS` - Business search
- `CLOUD EMAIL` - Email operations
- `CLOUD CONTACTS` - Contact management
- `CLOUD WEBSITE` - Website parsing
- `CLOUD SOCIAL` - Social media enrichment
- `CLOUD ENRICH` - Data enrichment
- `CLOUD LINK` - Link messages/data
- `CLOUD PRUNE` - Archive old data
- `CLOUD EXPORT` - Export data (CSV/JSON)
- `CLOUD STATS` - Show statistics

### POKE (Pokémon Battle System)
- `POKE START` - Start battle simulation
- `POKE STOP` - Stop current battle
- `POKE STATUS` - Show battle status
- `POKE EXPORT` - Export battle data
- `POKE IMPORT` - Import Pokémon data

### CONFIG (Configuration)
- `CONFIG GET` - Get configuration value
- `CONFIG SET` - Set configuration value
- `CONFIG LIST` - List all settings
- `CONFIG CHECK` - Check configuration
- `CONFIG FIX` - Fix configuration issues
- `CONFIG BACKUP` - Backup configuration
- `CONFIG RESTORE` - Restore configuration

### WORKFLOW (Workflow Automation)
- `WORKFLOW NEW` - Create new workflow
- `WORKFLOW LIST` - List workflows
- `WORKFLOW RUN` - Execute workflow
- `WORKFLOW PAUSE` - Pause workflow
- `WORKFLOW RESUME` - Resume workflow
- `WORKFLOW STOP` - Stop workflow
- `WORKFLOW STATUS` - Show workflow status

### MISSION (Mission Management)
- `MISSION NEW` - Create new mission
- `MISSION LIST` - List missions
- `MISSION START` - Start mission
- `MISSION PAUSE` - Pause mission
- `MISSION RESUME` - Resume mission
- `MISSION COMPLETE` - Mark complete
- `MISSION FAIL` - Mark failed

### TUI (Terminal UI)
- `TUI ENABLE` - Enable TUI feature
- `TUI DISABLE` - Disable TUI feature
- `TUI STATUS` - Show TUI status

### GUIDE (Knowledge Bank)
- `GUIDE WATER` - Water survival guides
- `GUIDE FIRE` - Fire-making guides
- `GUIDE SHELTER` - Shelter building
- `GUIDE FOOD` - Food procurement
- `GUIDE MEDICAL` - Medical guides
- `GUIDE NAVIGATION` - Navigation guides

---

## Tips & Tricks

### 1. Faster Navigation
- Use **↓** once to see all completions
- Use **Ctrl+Space** to force show menu if it doesn't appear
- Use **Tab** repeatedly to cycle through options

### 2. Quick Command Entry
- Type first few letters → Press **Tab** → Press **Space** → Continue
- Example: `CL` → Tab → `CLOUD` → Space → `GE` → Tab → `GENERATE`

### 3. History Shortcuts
- **↑** on empty line = browse history
- **Ctrl+R** then type = search history
- Gray ghost text = quick history completion

### 4. Error Recovery
- **Escape** = close menu without clearing input
- **Ctrl+U** = clear line and start over
- **Ctrl+W** = delete last word

### 5. Multi-Column Display
Completions now show in multi-column format for better visibility:
```
STATUS          Show system status          
START           Start service               
STATS           Show statistics             
```

---

## Troubleshooting

### Completions Not Showing?
1. Check if smart input is enabled: `TUI STATUS`
2. Try **Ctrl+Space** to force show menu
3. Verify terminal supports advanced features (check `$TERM`)

### Menu Flickering?
- Normal for very fast typing
- Completions update in real-time
- Use **Tab** to lock in selection

### Wrong Completion Accepted?
- **Enter** executes what you typed, not the selection
- Use **Tab** or **→** to accept suggestion before **Enter**

### Fallback Mode Activated?
```
⚠️  Fallback mode: <reason>
```
Check the reason and fix terminal settings if needed.

---

## Performance

- **<10ms** completion generation
- **Real-time** updates as you type
- **No lag** on slow terminals
- **Minimal memory** footprint

---

## Version History

**v1.2.22** (Current)
- ✅ Auto-show completions while typing
- ✅ Multi-word command support (POKE START, CLOUD GENERATE, etc.)
- ✅ Smart selection with arrow keys
- ✅ Visual feedback improvements
- ✅ History integration with ghost text
- ✅ Better keyboard shortcuts

**v1.2.15**
- Basic autocomplete with Tab completion
- Command predictor integration
- TUI keypad support

---

## Future Enhancements

- [ ] Context-aware parameter suggestions
- [ ] Variable name completion (`{$VARIABLE}`)
- [ ] Path completion for file commands
- [ ] Smart error correction (typo suggestions)
- [ ] Syntax validation as you type
- [ ] Command preview pane

---

**Happy commanding with Smart Input!** 🚀
