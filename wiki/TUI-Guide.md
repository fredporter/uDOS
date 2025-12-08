# TUI Guide - Terminal User Interface (v1.2.15)

The uDOS Terminal User Interface (TUI) provides enhanced navigation and interaction using numpad keys for keyboard-centric workflows.

## Overview

The TUI system consists of four integrated components:

1. **Keypad Navigator** - Numpad-based navigation (0-9 keys)
2. **Command Predictor** - Real-time command suggestions
3. **Enhanced Pager** - Scroll-while-prompting for output
4. **File Browser** - Navigate workspaces with keyboard

## Quick Start

```bash
# Enable keypad navigation
TUI ENABLE KEYPAD

# Check TUI status
TUI STATUS

# Disable keypad
TUI DISABLE KEYPAD
```

## Keypad Navigation

When keypad is enabled, the numpad keys (0-9) control navigation instead of typing numbers.

### Keypad Layout

```
┌───────────────┐
│  7↶  8↑  9↷  │  7 = Undo
│  4←  5✓  6→  │  8 = Up/Previous command
│  1◀  2↓  3▶  │  9 = Redo
│       0☰     │  4 = Left
└───────────────┘  5 = Select/Execute
                   6 = Right
                   2 = Down/Next command
                   1 = History back
                   3 = History forward
                   0 = Menu toggle
```

### Command Mode (Default)

When at the command prompt:

- **8** or **1**: Previous command in history
- **2** or **3**: Next command in history
- **4**: Move cursor left in command
- **6**: Move cursor right in command
- **5**: Execute current command
- **7**: Undo last text edit
- **9**: Redo (not available in prompt_toolkit)
- **0**: Open menu/file browser (planned)

### Navigation Hints

When keypad is enabled, you'll see navigation hints above the prompt:

```
┌─ Keypad: 8↑ 2↓ 4← 6→ 5✓ 7↶ 9↷ 1◀ 3▶ 0☰ ─┐
uDOS>
```

## TUI Commands

### Enable/Disable Components

```bash
# Enable specific component
TUI ENABLE KEYPAD
TUI ENABLE PREDICTOR
TUI ENABLE PAGER
TUI ENABLE ALL

# Disable specific component
TUI DISABLE KEYPAD
TUI DISABLE PREDICTOR
TUI DISABLE ALL

# Toggle keypad on/off
TUI TOGGLE KEYPAD
```

### Check Status

```bash
TUI STATUS
```

Output shows component states:

```
╔═══════════════════════════════════════╗
║       TUI COMPONENT STATUS            ║
╠═══════════════════════════════════════╣
║ Keypad Navigator:  ✅ ENABLED         ║
║ Command Predictor: ✅ ENABLED         ║
║ Enhanced Pager:    ✅ ENABLED         ║
║ File Browser:      ✅ AVAILABLE       ║
╚═══════════════════════════════════════╝

📋 Keypad Controls:
   8↑ 2↓ 4← 6→ = Arrow navigation
   5 = Select/Confirm
   7/9 = Undo/Redo
   1/3 = History back/forward
   0 = Menu/Toggle
```

## Component Details

### OK Assistant Panel (v1.2.21) ✨

**Purpose**: AI-assisted workflow generation and code assistance with context awareness.

**Access**: Press **O** key (uppercase or lowercase) from command mode to open the OK panel.

**Features**:
- **8 Quick Prompts**: Instant access to common AI tasks
  - MAKE WORKFLOW - Generate uPY workflow scripts
  - MAKE SVG - Generate SVG graphics with AI
  - MAKE DOC - Generate documentation (markdown)
  - MAKE TEST - Generate unit tests (pytest)
  - MAKE MISSION - Generate mission scripts
  - Explain code - AI code explanation
  - Optimize code - AI optimization suggestions
  - Custom prompt - Ask anything
- **Conversation History**: Last 10 AI interactions with timestamps
- **Context Display**: Shows workspace, TILE location, current file
- **Two Views**: P (prompts list), H (history view)

**Panel Navigation**:
- 8/2 - Navigate prompts or history entries
- 5 - Select and execute prompt
- P - Switch to prompts view
- H - Switch to history view
- C - Clear conversation history
- ESC - Close panel

**Example Usage**:
```bash
# From uDOS command line, press O key
# Panel opens with 8 quick prompts:

╔═══════════════════════════════════════════════════════════════════╗
║                   OK ASSISTANT PANEL                              ║
╠═══════════════════════════════════════════════════════════════════╣
║ Context:                                                          ║
║   Workspace: /Users/fredbook/Code/uDOS                            ║
║   TILE: AA340-100 (Sydney)                                        ║
║   File: core/commands/ok_handler.py                               ║
╠═══════════════════════════════════════════════════════════════════╣
║ Quick Prompts:                                                    ║
║                                                                   ║
║  ▶ MAKE WORKFLOW - Generate workflow automation script            ║
║    MAKE SVG - Generate SVG diagram from description               ║
║    MAKE DOC - Generate documentation for code                     ║
║    MAKE TEST - Generate unit tests                                ║
║    MAKE MISSION - Generate mission script                         ║
║    Explain code - AI explanation of selected code                 ║
║    Optimize code - AI optimization suggestions                    ║
║    Custom prompt - Ask the AI assistant anything                  ║
╠═══════════════════════════════════════════════════════════════════╣
║ P=Prompts H=History C=Clear ESC=Close                             ║
╚═══════════════════════════════════════════════════════════════════╝

# Navigate with 8/2, select with 5
# OR use CLI commands directly:

OK MAKE WORKFLOW "backup system files"
OK MAKE SVG "water filtration diagram"
OK ASK "how do I optimize this function?"
OK STATUS  # Show usage statistics
```

**Configuration**: Settings in CONFIG panel → [OK] tab:
- Model selection (gemini-2.0-flash-exp, gemini-1.5-pro, etc.)
- Temperature (0.0-2.0, controls creativity)
- Max tokens (100-100k, response length)
- Cost tracking enabled/disabled
- Context length (1-20 commands)
- Auto-save history and retention

**Output Directories**:
- Workflows → `memory/workflows/missions/`
- SVG → `memory/drafts/svg/`
- Documentation → `memory/docs/`
- Tests → `memory/ucode/tests/`
- Missions → `memory/missions/`

**State Persistence**: 
- Config: `memory/system/user/ok_config.json`
- History: `memory/system/user/ok_history.json`

**Requirements**: GEMINI_API_KEY in `.env` file (falls back gracefully if missing)

---

### Keypad Navigator

**Purpose**: Navigate uDOS using numpad keys instead of arrow keys/mouse.

**Features**:
- Command history navigation (8/2 or 1/3)
- Cursor movement in command line (4/6)
- Text undo/redo (7/9)
- Execute commands (5)
- Menu access (0)

**State Persistence**: Keypad settings save to `memory/system/user/tui_config.json`.

### Command Predictor

**Purpose**: Real-time command suggestions with syntax highlighting.

**Features**:
- Autocomplete from `core/data/commands.json`
- Token highlighting (green=valid, yellow=unknown, cyan=flags)
- Learning from command frequency
- Fuzzy matching for typo tolerance

**State Persistence**: Prediction history saves to `memory/system/user/predictor_state.json`.

### Enhanced Pager

**Purpose**: Scroll through command output without losing prompt.

**Features**:
- Scroll-while-prompting (navigate output, keep typing)
- Visual indicators (▲ more above, ▼ more below)
- Preserve scroll position across commands

**Status**: v1.2.15 - Partial integration (works standalone).

### File Browser

**Purpose**: Navigate files in 5 workspaces with keyboard.

**Workspaces**:
- `knowledge/` - Knowledge bank guides
- `docs/` - Documentation
- `drafts/` - User drafts
- `sandbox/` - Experimental code
- `scripts/` - uPY scripts

**File Filters**: Shows only `.upy`, `.md`, `.json` files.

**Navigation**:
- 8/2: Move up/down in file list
- 6: Enter selected directory
- 4: Go up one directory level
- 5: Select file
- 0: Switch workspace

**Status**: v1.2.15 - Component ready, integration pending.

## Configuration

### TUI Settings File

`memory/system/user/tui_config.json`:

```json
{
  "keypad_enabled": true,
  "prediction_enabled": true,
  "pager_enabled": true,
  "prediction_max_results": 10,
  "preserve_scroll": true
}
```

### Manual Configuration

```bash
# Using CONFIG command (alternative)
CONFIG SET keypad_enabled true
CONFIG GET keypad_enabled
```

### Default Settings

- Keypad: **Disabled** (must enable explicitly)
- Predictor: **Enabled** (active in SmartPrompt)
- Pager: **Enabled** (scroll preservation)
- Browser: **Available** (not active by default)

## Keyboard Shortcuts (Non-Keypad)

When keypad is **disabled**, standard keyboard shortcuts work:

- **Tab**: Autocomplete command
- **Ctrl+R**: Reverse history search
- **Ctrl+C**: Cancel/interrupt
- **↑/↓**: History navigation
- **←/→**: Cursor movement
- **Ctrl+A**: Beginning of line
- **Ctrl+E**: End of line
- **Ctrl+U**: Clear line
- **Ctrl+K**: Delete to end of line

## Workflow Examples

### Example 1: Quick Command Recall

```bash
# Enable keypad
TUI ENABLE KEYPAD

# Press 8 repeatedly to cycle through previous commands
# Press 5 to execute selected command
# Press 7 to undo if you made a mistake
```

### Example 2: Editing Long Command

```bash
# Enable keypad
TUI ENABLE KEYPAD

# Type command: GUIDE water --section purification
# Press 4 to move cursor left to "water"
# Edit to "fire"
# Press 5 to execute: GUIDE fire --section purification
```

### Example 3: Reviewing Output

```bash
# With pager enabled (default)
# Run: CATALOG
# Output scrolls, but you can still type next command
# Visual indicators show ▲ (more above) / ▼ (more below)
```

## Troubleshooting

### Keypad Doesn't Work

**Check status**:
```bash
TUI STATUS
```

If keypad shows ❌ DISABLED:
```bash
TUI ENABLE KEYPAD
```

### Numbers Still Type Instead of Navigate

**Verify keypad mode**:
- Look for keypad hints above prompt: `┌─ Keypad: 8↑ 2↓ 4← 6→ ...`
- If missing, keypad isn't enabled

**Re-enable**:
```bash
TUI DISABLE KEYPAD
TUI ENABLE KEYPAD
```

### Settings Don't Persist

**Check config file exists**:
```bash
# In shell
ls -la memory/system/user/tui_config.json
```

**Manually create** (if missing):
```bash
NEW memory/system/user/tui_config.json
```

Add content:
```json
{
  "keypad_enabled": false,
  "prediction_enabled": true,
  "pager_enabled": true
}
```

### Keypad Conflicts with Number Input

**Temporarily disable**:
```bash
TUI DISABLE KEYPAD
# Type numbers normally
# Then re-enable
TUI ENABLE KEYPAD
```

**Or use Toggle**:
```bash
TUI TOGGLE KEYPAD  # Quick on/off
```

## Technical Details

### Component Files

- **Main Loop**: `core/uDOS_main.py` (TUI controller initialization)
- **Key Bindings**: `core/input/smart_prompt.py` (numpad handlers)
- **TUI Controller**: `core/ui/tui_controller.py` (component coordination)
- **Keypad Navigator**: `core/ui/keypad_navigator.py` (navigation logic)
- **Command Predictor**: `core/ui/command_predictor.py` (autocomplete)
- **Pager**: `core/ui/pager.py` (output scrolling)
- **File Browser**: `core/ui/file_browser.py` (file navigation)
- **Configuration**: `core/ui/tui_config.py` (settings management)
- **Command Handler**: `core/commands/tui_handler.py` (TUI commands)

### Key Binding Architecture

When keypad is enabled:

1. User presses numpad key (0-9)
2. `smart_prompt.py` intercepts via `key_bindings`
3. Checks `self.tui.keypad.enabled` status
4. If enabled: Routes to `self.tui.handle_key(key)`
5. TUI controller calls `keypad_navigator.handle_key(key)`
6. Keypad navigator returns action dict: `{"action": "history_back", ...}`
7. Key binding handler executes action on `event.current_buffer`

If keypad disabled: Key inserts normally.

### Action Mapping

| Key | Action | Buffer Operation |
|-----|--------|------------------|
| 8 | `history_back` | `history_backward()` |
| 2 | `history_forward` | `history_forward()` |
| 4 | `move_left` | `cursor_left()` |
| 6 | `move_right` | `cursor_right()` |
| 5 | `execute` | `validate_and_handle()` |
| 7 | `undo` | `undo()` |
| 9 | `redo` | (not available in buffer) |
| 1 | `history_back` | `history_backward()` |
| 3 | `history_forward` | `history_forward()` |
| 0 | `menu_open` | (planned) |

## Version History

### v1.2.15 (Current)

- ✅ Main loop integration complete
- ✅ TUI controller initialized and connected
- ✅ TUI commands (ENABLE/DISABLE/STATUS) working
- ✅ Numpad key bindings functional
- ✅ Settings persistence to tui_config.json
- 📝 Documentation complete (this guide)

### v1.2.13 (Components Created)

- Components coded but not integrated:
  - `keypad_navigator.py` (379 lines)
  - `tui_controller.py` (208 lines)
  - `command_predictor.py`
  - `pager.py`
  - `file_browser.py`

### Future Enhancements (v1.2.16+)

- File browser full integration (0 key opens browser)
- Pager scroll keys while prompting
- Command predictor visual display
- Menu system (0 key context menus)
- Browser workspace switching
- Breadcrumb navigation display
- Visual mode indicator in prompt

## See Also

- [[Command-Reference]] - All uDOS commands
- [[Getting-Started]] - Basic uDOS usage
- [[Developers-Guide]] - TUI component architecture
- [[Extension-Development]] - Building TUI extensions

---

**Last Updated**: December 7, 2025 (v1.2.15)  
**Status**: TUI Integration Complete (4/4 tasks)
