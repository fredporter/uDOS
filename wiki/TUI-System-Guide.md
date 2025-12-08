# TUI System User Guide (v1.2.13)

**Complete Terminal User Interface** with keypad navigation, smart command prediction, enhanced paging, and workspace-aware file browsing.

---

## Quick Start

### Enable Keypad Navigation
```
CONFIG SET keypad_enabled true
```

### Keypad Layout (NumPad Style)
```
+------+------+------+
|  7   |  8   |  9   |
| Undo |  ↑   | Redo |
+------+------+------+
|  4   |  5   |  6   |
|  ←   | Sel  |  →   |
+------+------+------+
|  1   |  2   |  3   |
|Hist- |  ↓   |Hist+ |
+------+------+------+
       |  0   |
       | Menu |
       +------+
```

### Key Functions

**Movement (4-way arrows)**
- `8` → Move Up
- `2` → Move Down
- `4` → Move Left
- `6` → Move Right

**Editing**
- `7` → Undo (like Ctrl+Z)
- `9` → Redo (like Ctrl+Y)
- `5` → Select / Confirm / Enter

**History Navigation**
- `1` → History Back (previous command)
- `3` → History Forward (next command)

**Extra / Global**
- `0` → Menu / Browser / Mode Toggle

---

## Features

### 1. Smart Command Prediction

As you type, uDOS suggests commands based on:
- **Schema**: Valid commands from system registry
- **History**: Commands you've used before
- **Fuzzy**: Similar commands (handles typos)

**Example:**
```
uDOS> G█
  Predictions:
  GUIDE     █████ Core system guide (confidence: 95%)
  GET       ████  Get system variable (confidence: 85%)
  GENERATE  ███   Generate content (confidence: 60%)
```

**Syntax Highlighting:**
```
uDOS> GUIDE water --detailed
      ^^^^^  ^^^^^ ^^^^^^^^^^
      green  white cyan (flag)
      (valid) (arg) 
```

**Colors:**
- 🟢 **Green** - Valid command
- 🟡 **Yellow** - Unknown command
- 🔵 **Cyan** - Flag (--flag)
- 🟣 **Magenta** - Path (file/folder)
- ⚪ **White** - Argument

### 2. Enhanced Pager

Scroll through long outputs while still being able to type new commands.

**Pager Controls:**
- `8` or `↑` - Scroll up one line
- `2` or `↓` - Scroll down one line
- `Space` or `PgDn` - Page down
- `PgUp` - Page up
- `g` - Jump to top
- `G` - Jump to bottom

**Visual Indicators:**
```
▲ (More above - Press 8 or PgUp to scroll)
... content ...
▼ (More below - 45% - Press 2 or PgDn to scroll)

Lines 21-40 of 100 (45%)
```

**Features:**
- **Scroll-while-prompting**: Output stays visible while typing
- **Preserve position**: Scroll position maintained across commands
- **Search**: Find text in output (forward/backward)

### 3. Workspace-Aware File Browser

Navigate files across 5 predefined workspaces with filtered views.

**Workspaces:**
1. **knowledge/** - Core knowledge base (read-only)
2. **memory/docs/** - User documentation
3. **memory/drafts/** - Work in progress
4. **memory/ucode/sandbox/** - Experimental scripts
5. **memory/ucode/scripts/** - User scripts

**File Filter:**
- `.upy` files (🐍 Python scripts)
- `.md` files (📄 Markdown docs)
- `.json` files (📊 Data files)

**Browser Interface:**
```
═══════════════════════════════════════
📁 scripts > utilities > helpers
───────────────────────────────────────
  ▲ More above
▶ 🐍 water_filter.upy              2.4KB
  📄 README.md                      1.2KB
  📁 archived/                      <DIR>
  🐍 fire_starter.upy               3.1KB
  ▼ More below
───────────────────────────────────────
Total: 15 items (12 files) | Filter: .upy, .md, .json
8/2: Navigate | 4: Parent | 6: Enter | 5: Select | 0: Switch Workspace
```

**Browser Controls:**
- `8`/`2` - Move selection up/down
- `4` - Go to parent directory
- `6` - Enter directory
- `5` - Select file/folder
- `0` - Cycle to next workspace

### 4. Command History

Navigate your command history with ease.

**History Controls:**
- `1` - Previous command (history back)
- `3` - Next command (history forward)
- `↑` - Same as `1` (when in command mode)
- `↓` - Same as `3` (when in command mode)

**Features:**
- Last 100 commands saved
- Persistent across sessions
- Frequency tracking (most-used commands prioritized)

### 5. Undo/Redo

Undo and redo command edits before execution.

**Undo/Redo Controls:**
- `7` - Undo last edit
- `9` - Redo undone edit
- Stack-based (multiple undo/redo levels)

---

## Configuration

### TUI Settings

All settings stored in `memory/system/user/tui_config.json`

**Available Settings:**
```json
{
  "keypad_enabled": false,          // Enable numpad navigation
  "preserve_scroll": true,          // Keep scroll position
  "show_scroll_indicators": true,   // Show ▲/▼ in pager
  "prediction_max_results": 5,      // Number of predictions
  "browser_filter": [".upy", ".md", ".json"],  // File extensions
  "auto_save_state": true,          // Save state on exit
  "syntax_highlighting": true       // Enable token colors
}
```

**CONFIG Commands:**
```bash
# Enable keypad navigation
CONFIG SET keypad_enabled true

# Change prediction count
CONFIG SET prediction_max_results 10

# Disable scroll preservation
CONFIG SET preserve_scroll false

# Add more file extensions to browser
CONFIG SET browser_filter [".upy", ".md", ".json", ".txt"]
```

### State Persistence

TUI state automatically saved to:
- `memory/system/user/keypad_state.json` - Navigation state
- `memory/system/user/predictor_state.json` - Learning data
- `memory/system/user/tui_config.json` - User preferences

**Manual Save:**
```python
from core.ui.tui_controller import get_tui

tui = get_tui()
tui.save_states()
```

---

## Usage Examples

### Example 1: Quick Command with Prediction
```
uDOS> GU█
  Predictions:
  GUIDE     █████ 95%
  
uDOS> GUIDE █
  Predictions:
  water     ████  Recent: GUIDE water
  fire      ███   Schema: Fire guides
  shelter   ███   Schema: Shelter guides
  
uDOS> GUIDE water█
[Executes command]
```

### Example 2: Browse and Select File
```
uDOS> [Press 0 to open browser]

📁 scripts
───────────────────────────────────────
▶ 🐍 water_filter.upy              2.4KB
  📄 README.md                      1.2KB
  
[Press 5 to select water_filter.upy]
[File path inserted into command: EDIT memory/ucode/scripts/water_filter.upy]
```

### Example 3: Scroll Through Output
```
uDOS> GUIDE water --detailed
[Long output appears]

▲ (More above)
... water purification methods ...
... boiling procedure ...
▼ (More below - 30%)

[Press 8 to scroll up, 2 to scroll down]
[Type new command while output is still visible]

uDOS> GUIDE fire█
```

### Example 4: History Navigation
```
uDOS> GUIDE water
[Executes]

uDOS> STATUS
[Executes]

uDOS> [Press 1 for history back]
uDOS> STATUS█

uDOS> [Press 1 again]
uDOS> GUIDE water█

uDOS> [Press 3 for history forward]
uDOS> STATUS█
```

### Example 5: Undo/Redo Edits
```
uDOS> GUIDE wter█
      [Oops, typo]

uDOS> [Press 7 to undo]
uDOS> GUIDE █

uDOS> [Type correct text]
uDOS> GUIDE water█

uDOS> [Press 7 to undo]
uDOS> GUIDE █

uDOS> [Press 9 to redo]
uDOS> GUIDE water█
```

---

## Modes

The TUI system operates in 3 modes:

### 1. Command Mode (Default)
- Type commands
- Get predictions
- Navigate history
- Standard terminal behavior

**Active Keys:** All keypad keys

### 2. Browser Mode
- Navigate file system
- Select files/folders
- Switch workspaces
- Breadcrumb navigation

**Activate:** Press `0` from command mode
**Exit:** Press `0` again to return to command mode

### 3. Pager Mode
- Scroll through output
- Search in content
- Preserve scroll position
- Status line visible

**Activate:** Automatically when output > viewport
**Exit:** Scroll to bottom or start new command

---

## Accessibility

### Screen Reader Support
Keypad navigation can interfere with screen readers. To disable:
```
CONFIG SET keypad_enabled false
```

### Verbose Mode
Enable detailed announcements for non-visual users:
```
CONFIG SET verbose_mode true
```

### Standard Keys Still Work
Even with keypad enabled:
- Arrow keys (↑↓←→) still function
- Ctrl+Z for undo (in some terminals)
- Standard terminal shortcuts active

---

## Troubleshooting

### Keypad Not Working
1. Check if enabled: `CONFIG GET keypad_enabled`
2. Enable if needed: `CONFIG SET keypad_enabled true`
3. Verify NumLock is ON (hardware keyboard)

### Predictions Not Showing
1. Check setting: `CONFIG GET prediction_max_results`
2. Verify commands.json exists: `core/data/commands.json`
3. Rebuild predictor state: Delete `memory/system/user/predictor_state.json`

### File Browser Empty
1. Check workspace exists: Navigate to folder manually
2. Verify filter: `CONFIG GET browser_filter`
3. Try toggling hidden files in browser

### Scroll Position Not Preserving
1. Check setting: `CONFIG GET preserve_scroll`
2. Enable: `CONFIG SET preserve_scroll true`
3. Restart uDOS for changes to take effect

### State Not Persisting
1. Check: `CONFIG GET auto_save_state`
2. Enable: `CONFIG SET auto_save_state true`
3. Verify write permissions: `memory/system/user/`

---

## Advanced Features

### Custom Workspaces
Extend file browser with custom workspaces:
```python
from core.ui.file_browser import FileBrowser, Workspace

browser = FileBrowser()
browser.workspaces[Workspace.CUSTOM] = Path("/custom/path")
browser.set_workspace(Workspace.CUSTOM)
```

### Prediction Learning
Predictor learns from your usage:
- Tracks command frequency
- Prioritizes recent commands
- Improves suggestions over time

**View stats:**
```python
from core.ui.command_predictor import CommandPredictor

predictor = CommandPredictor()
print(predictor.frequency_map)  # Command usage counts
```

### Search in Pager
Search for text in paged output:
```python
from core.ui.pager import Pager

pager = Pager()
found = pager.search("water", forward=True)  # Search forward
found = pager.search("fire", forward=False)  # Search backward
```

---

## Developer Integration

### Initialize TUI in Code
```python
from core.ui.tui_controller import initialize_tui, get_tui

# Initialize with custom config
tui = initialize_tui({
    "keypad_enabled": True,
    "prediction_max_results": 10
})

# Get global instance
tui = get_tui()
```

### Add Custom Predictions
```python
predictor = tui.predictor
predictor.commands["CUSTOM"] = {
    "description": "Custom command",
    "syntax": "CUSTOM [args]",
    "category": "user"
}
```

### Hook Into Key Events
```python
def on_keypress(key):
    result = tui.handle_key(key)
    if result:
        print(f"Action: {result['action']}")

# In main loop
while True:
    key = get_key_press()
    on_keypress(key)
```

---

## See Also

- **CONFIG Command Reference** - `HELP CONFIG`
- **File Management** - `HELP FILE`
- **Command Syntax** - `HELP COMMANDS`
- **Workspace Structure** - `TREE`

---

**Version:** 1.2.13
**Last Updated:** December 7, 2025
