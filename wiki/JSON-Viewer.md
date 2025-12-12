# JSON Viewer/Editor Guide

**Version:** v1.2.22+  
**Purpose:** Interactive JSON file viewing and editing with tree navigation  
**Location:** `core/services/json_viewer.py`, `core/commands/json_handler.py`

---

## Overview

The JSON Viewer provides an interactive, tree-based interface for viewing and editing JSON files. Navigate through complex structures, make inline edits, track changes, and save with confidence.

### Key Features

- **Tree Navigation** - Browse nested structures with expand/collapse
- **Visual Indicators** - Color-coded type icons for easy identification
- **Inline Editing** - Edit values directly with type validation
- **Diff View** - See all changes before saving
- **Undo/Redo** - Full history stack for safe editing
- **Path Tracking** - Know exactly where you are in the structure
- **Automatic Backup** - Creates `.backup` files before saving

---

## Quick Start

```bash
# Load a JSON file
uDOS> JSON LOAD memory/bank/user/user.json

# View the tree (default 20 lines)
uDOS> JSON VIEW

# Navigate to a value
uDOS> JSON DOWN
uDOS> JSON DOWN

# Edit the current value
uDOS> JSON EDIT "new_value"

# Check what changed
uDOS> JSON DIFF

# Save changes
uDOS> JSON SAVE
```

---

## Commands Reference

### JSON LOAD

Load a JSON file for viewing/editing.

```bash
JSON LOAD <file>
```

**Examples:**
```bash
JSON LOAD memory/bank/user/user.json
JSON LOAD core/data/themes/galaxy.json
JSON LOAD memory/system/error_patterns.json
```

**Output:**
```
✓ Loaded: memory/bank/user/user.json (245 bytes, 8 keys)
```

---

### JSON VIEW

Display the tree structure with cursor position.

```bash
JSON VIEW [lines]
```

**Parameters:**
- `lines` (optional) - Number of lines to display (default: 20)

**Examples:**
```bash
JSON VIEW          # Show 20 lines
JSON VIEW 50       # Show 50 lines
JSON VIEW 5        # Show 5 lines
```

**Output:**
```
JSON Tree: user.json (8 keys)
─────────────────────────────────────
▶ 📦 user.json: { 8 keys }
    📝 username: "fredporter"
    📝 role: "admin"
    📝 theme: "foundation"
    🔢 xp: 1250
    🔢 level: 5
    📁 settings: { 3 keys }
    📄 recent_commands: [ 5 items ]
    ✓ auto_save: true

[8/8 nodes | Cursor: user.json | ▲/▼ to move, ↔ to expand/collapse]
```

**Tree Symbols:**
- 📦/📁 - Object (collapsed/expanded)
- 📋/📄 - Array (collapsed/expanded)
- 📝 - String value
- 🔢 - Number value
- ✓/✗ - Boolean value (true/false)
- ∅ - Null value
- ▶ - Current cursor position

---

### JSON UP / JSON DOWN

Navigate the cursor through visible nodes.

```bash
JSON UP
JSON DOWN
```

**Examples:**
```bash
# Start at root
JSON VIEW
▶ 📦 user.json: { 8 keys }

# Move down one level
JSON DOWN
  ▶ 📝 username: "fredporter"

# Move down again
JSON DOWN
    ▶ 📝 role: "admin"

# Move back up
JSON UP
  ▶ 📝 username: "fredporter"
```

**Navigation Rules:**
- Only moves through **visible** nodes
- Skips collapsed containers
- Wraps around at top/bottom

---

### JSON EXPAND / JSON COLLAPSE

Toggle expansion of container nodes (objects/arrays).

```bash
JSON EXPAND
JSON COLLAPSE
```

**Examples:**
```bash
# Collapsed object
▶ 📁 settings: { 3 keys }

# After JSON EXPAND
▶ 📦 settings: { 3 keys }
    📝 auto_backup: "true"
    📝 log_level: "info"
    🔢 max_logs: 100

# After JSON COLLAPSE
▶ 📁 settings: { 3 keys }
```

**Rules:**
- Only works on containers (objects/arrays)
- Displays "Not a container" for scalar values
- Default state: containers are expanded

---

### JSON EDIT

Edit the value at the current cursor position.

```bash
JSON EDIT <value>
```

**Parameters:**
- `value` - New value (auto-parsed by type)

**Type Parsing:**
- **Numbers:** `42`, `3.14`, `-10`
- **Booleans:** `true`, `false`
- **Null:** `null`
- **Strings:** `"text"`, `'text'`, or unquoted
- **JSON:** `{"key": "value"}`, `[1, 2, 3]`

**Examples:**
```bash
# Edit string
JSON EDIT "new_username"
✓ Edited: username = "new_username"

# Edit number
JSON EDIT 42
✓ Edited: max_logs = 42

# Edit boolean
JSON EDIT false
✓ Edited: auto_save = false

# Edit null
JSON EDIT null
✓ Edited: theme = null

# Edit JSON object
JSON EDIT {"dark": true, "contrast": "high"}
✓ Edited: settings = {"dark": true, "contrast": "high"}
```

**Rules:**
- Cannot edit keys, only values
- Cannot edit containers directly (use nested edits)
- Changes tracked for diff view

---

### JSON DIFF

Show all changes from the original file.

```bash
JSON DIFF
```

**Output:**
```
JSON Changes: 3 modifications
─────────────────────────────────────
Modified:
  username: "fredporter" → "fred_new"
  max_logs: 100 → 42
  auto_save: true → false

No additions or removals.
```

**Diff Types:**
- **Modified** - Value changed
- **Added** - New key added
- **Removed** - Key deleted
- **Type Changed** - Value type changed (e.g., string → number)
- **Array Changed** - Array length changed

---

### JSON SAVE

Save changes to file (creates `.backup` first).

```bash
JSON SAVE [file]
```

**Parameters:**
- `file` (optional) - Target file (default: original file)

**Examples:**
```bash
# Save to original file
JSON SAVE
✓ Backup created: memory/bank/user/user.json.backup
✓ Saved: memory/bank/user/user.json (258 bytes)

# Save to new file
JSON SAVE memory/bank/user/user_v2.json
✓ Saved: memory/bank/user/user_v2.json (258 bytes)
```

**Safety Features:**
- Automatic backup before overwrite
- Validates JSON before saving
- Preserves original file if save fails

---

### JSON UNDO / JSON REDO

Undo or redo edit operations.

```bash
JSON UNDO
JSON REDO
```

**Examples:**
```bash
# Make an edit
JSON EDIT "test"
✓ Edited: username = "test"

# Undo the change
JSON UNDO
✓ Undone: username = "fredporter"

# Redo the change
JSON REDO
✓ Redone: username = "test"
```

**History Rules:**
- Undo stack stores up to 100 operations
- Redo clears when new edit is made
- History persists until file is reloaded

---

### JSON PATH

Display the full path to the current cursor position.

```bash
JSON PATH
```

**Output:**
```
Current Path: user.json.settings.auto_backup
```

**Path Format:**
- Dot notation for object keys: `obj.key`
- Bracket notation for arrays: `arr[0]`
- Combined: `data.users[0].name`

---

### JSON INFO

Display viewer statistics and status.

```bash
JSON INFO
```

**Output:**
```
JSON Viewer Status
─────────────────────────────────────
File: memory/bank/user/user.json
Size: 245 bytes
Total Nodes: 24
Visible Nodes: 8
Cursor: user.json.settings
Has Changes: Yes
Undo Available: Yes (3 operations)
Redo Available: No
```

---

## Common Workflows

### Editing User Config

```bash
# Load user config
JSON LOAD memory/bank/user/user.json

# Find the theme setting
JSON VIEW
JSON DOWN
JSON DOWN
JSON DOWN  # Navigate to theme key

# Change theme
JSON EDIT "galaxy"

# Verify change
JSON DIFF
# Modified: theme: "foundation" → "galaxy"

# Save
JSON SAVE
```

---

### Exploring Error Patterns

```bash
# Load error patterns
JSON LOAD memory/system/error_patterns.json

# View structure
JSON VIEW 30

# Navigate to a specific error
JSON DOWN
JSON DOWN
JSON EXPAND  # Expand patterns array
JSON DOWN

# Check error details
JSON PATH
# Current Path: error_patterns.json.patterns[0].error
```

---

### Bulk Editing Theme Settings

```bash
# Load theme
JSON LOAD core/data/themes/galaxy.json

# Navigate to colors
JSON DOWN
JSON DOWN
JSON DOWN
JSON EXPAND

# Edit primary color
JSON DOWN
JSON EDIT "#4a9eff"

# Edit secondary color
JSON DOWN
JSON EDIT "#7b68ee"

# Review changes
JSON DIFF

# Save as new theme
JSON SAVE core/data/themes/galaxy_custom.json
```

---

### Recovering from Mistakes

```bash
# Make some edits
JSON EDIT "wrong_value"
JSON EDIT 999
JSON EDIT false

# Oh no! Let's undo all of them
JSON UNDO
JSON UNDO
JSON UNDO

# Or just reload the file
JSON LOAD memory/bank/user/user.json
# All changes discarded
```

---

## Type Parsing Examples

### Strings

```bash
# Quoted strings (recommended)
JSON EDIT "hello world"
JSON EDIT 'hello world'

# Unquoted (parsed as string if not number/bool/null)
JSON EDIT hello_world
```

### Numbers

```bash
# Integers
JSON EDIT 42
JSON EDIT -10

# Floats
JSON EDIT 3.14
JSON EDIT -2.5

# Scientific notation
JSON EDIT 1e6
```

### Booleans

```bash
JSON EDIT true
JSON EDIT false
```

### Null

```bash
JSON EDIT null
```

### JSON Objects

```bash
# Single line
JSON EDIT {"key": "value", "count": 42}

# Multi-line (use quotes)
JSON EDIT '{"settings": {"theme": "dark"}}'
```

### JSON Arrays

```bash
JSON EDIT [1, 2, 3, 4, 5]
JSON EDIT ["red", "green", "blue"]
JSON EDIT [{"id": 1}, {"id": 2}]
```

---

## Tips & Best Practices

### Navigation

1. **Use VIEW with line limits** for large files
   ```bash
   JSON VIEW 10  # See just the top level
   ```

2. **Use PATH to confirm location** before editing
   ```bash
   JSON PATH
   # Current Path: config.database.host
   ```

3. **Expand only what you need** to reduce visual clutter
   ```bash
   JSON COLLAPSE  # Hide details
   JSON EXPAND    # Show details
   ```

### Editing

1. **Always check DIFF before saving**
   ```bash
   JSON DIFF  # Review all changes
   JSON SAVE  # Commit changes
   ```

2. **Use UNDO freely** - it's there to help
   ```bash
   JSON EDIT "test"
   JSON UNDO  # No harm done
   ```

3. **Save to new file for experiments**
   ```bash
   JSON SAVE config_test.json  # Keep original safe
   ```

### Safety

1. **Backup files are automatic** but can be cleaned
   ```bash
   # After saving, you'll have:
   # - config.json (new version)
   # - config.json.backup (previous version)
   ```

2. **Reload to discard all changes**
   ```bash
   JSON LOAD config.json  # Start fresh
   ```

3. **Use INFO to check status**
   ```bash
   JSON INFO  # See if unsaved changes exist
   ```

---

## Troubleshooting

### "No file loaded"

**Problem:** Trying to use commands without loading a file first.

**Solution:**
```bash
JSON LOAD <file>  # Load a file first
```

---

### "Not a container"

**Problem:** Trying to expand/collapse a scalar value (string, number, etc.)

**Solution:** Only use EXPAND/COLLAPSE on objects ({}) and arrays ([]).

---

### "Cannot edit key"

**Problem:** Cursor is on a container node (object/array) rather than a value.

**Solution:** Navigate to a child value first:
```bash
JSON DOWN    # Move to child value
JSON EDIT "new_value"
```

---

### "Invalid JSON"

**Problem:** Edited value is not valid JSON.

**Solution:** Check syntax and try again:
```bash
JSON UNDO  # Undo the bad edit
JSON EDIT {"correct": "syntax"}  # Fix and retry
```

---

### Lost my changes!

**Problem:** Accidentally reloaded file or exited.

**Solution:** Check the backup file:
```bash
# Your changes might be in:
# - <file>.backup (last saved version)
```

---

## Architecture

### Components

1. **JSONNode** (`core/services/json_viewer.py`)
   - Tree node representation
   - Stores key, value, parent, children
   - Tracks expanded state

2. **JSONViewer** (`core/services/json_viewer.py`)
   - Main viewer service
   - Handles navigation, editing, diff
   - Manages undo/redo stack

3. **JSONCommandHandler** (`core/commands/json_handler.py`)
   - Command routing
   - User interface layer
   - Error handling and feedback

### Data Flow

```
User Command → JSONCommandHandler → JSONViewer → JSONNode Tree
     ↓                                    ↓
  Output                             File I/O
```

### File Storage

```
memory/bank/user/
├── user.json           # Current version
└── user.json.backup    # Previous version (auto-created)
```

---

## Integration Examples

### Using in uPY Scripts

```upy
# Load and edit config
(JSON|LOAD|memory/bank/user/user.json)
(JSON|DOWN)
(JSON|EDIT|"new_theme")
(JSON|SAVE)

# Check for changes
(JSON|INFO)
IF {$has_changes} == true
  (JSON|SAVE)
  PRINT ('Saved changes')
END IF
```

### Combining with Other Commands

```bash
# Backup before editing
BACKUP memory/bank/user/user.json
JSON LOAD memory/bank/user/user.json
# ... make edits ...
JSON SAVE

# View JSON, then open in editor
JSON LOAD config.json
JSON VIEW 50
EDIT config.json  # Open in EDIT command
```

---

## Performance Notes

- **Large files (>1MB):** Use VIEW with small line limits
- **Deep nesting (>10 levels):** Collapse upper levels to reduce visible nodes
- **Many changes:** Check DIFF before SAVE to review all modifications
- **Memory usage:** Each undo operation stores a snapshot - cleared on LOAD

---

## See Also

- **EDIT Command** - Text editor for JSON files
- **CONFIG Command** - Manage uDOS configuration
- **BACKUP Command** - Create manual backups
- **TREE Command** - View directory structure

---

## Version History

- **v1.2.22** - Initial JSON Viewer/Editor implementation
  - Tree navigation with expand/collapse
  - Inline editing with type validation
  - Diff view and undo/redo
  - Automatic backup before save
  - Path tracking for nested structures

---

**Navigation:** [Home](Home.md) | [Command Reference](Command-Reference.md) | [Developers Guide](Developers-Guide.md)
