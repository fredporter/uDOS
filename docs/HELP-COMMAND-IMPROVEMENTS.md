# TUI Command Help & Smart Prompt Improvements

**Date:** 2026-01-24  
**Components:** Core TUI (help_handler.py, smart_prompt.py)  
**Status:** Implemented ✅

---

## Overview

Enhanced the uDOS TUI core with:

1. **Expanded HELP command** with category grouping and syntax reference
2. **Improved smart-prompt** with syntax highlighting and command hints
3. **Better autocomplete** with metadata and option descriptions

---

## 1. HELP Command Expansion (help_handler.py)

### New Features

#### 1.1 Command Categories

All 32 commands organized into 6 logical groups:

- **Navigation:** MAP, PANEL, GOTO, FIND, TELL
- **Inventory:** BAG, GRAB, SPAWN
- **NPCs & Dialogue:** NPC, TALK, REPLY
- **Files & State:** SAVE, LOAD, NEW, EDIT
- **System & Maintenance:** SHAKEDOWN, REPAIR, BACKUP, RESTORE, TIDY, CLEAN, COMPOST, DESTROY
- **Advanced:** BINDER, RUN, DATASET, CONFIG, PROVIDER

#### 1.2 Enhanced Command Metadata

Each command now includes:

```python
{
    "description": "Short description",
    "usage": "USAGE [args]",
    "example": "EXAMPLE usage",
    "notes": "Additional context",
    "category": "Category Name",           # ← NEW
    "syntax": "FULL SYNTAX [options]",     # ← NEW (comprehensive)
}
```

#### 1.3 New Help Modes

| Mode         | Usage                      | Purpose                                            |
| ------------ | -------------------------- | -------------------------------------------------- |
| **Default**  | `HELP`                     | Shows all commands grouped by category             |
| **Specific** | `HELP GOTO`                | Detailed help for a command with category + syntax |
| **Category** | `HELP CATEGORY Navigation` | List all commands in a category                    |
| **Syntax**   | `HELP SYNTAX SAVE`         | Show full syntax reference with options            |

### Examples

```
HELP
  → Grouped help by 6 categories with descriptions

HELP GOTO
  → Category: Navigation
  → Description: Navigate to connected location
  → Syntax: GOTO <north|south|east|west|up|down|location_id>
  → Usage: GOTO [direction|location_id]
  → Example: GOTO north or GOTO L300-BK10
  → Notes: Directions with shortcuts

HELP CATEGORY Navigation
  → Lists: MAP, PANEL, GOTO, FIND, TELL
  → Each with description and syntax

HELP SYNTAX BACKUP
  → Displays full syntax: BACKUP <current|+subfolders|workspace|all> [label] [--compress]
  → With example and notes
```

### Implementation Details

**New Methods:**

1. `_show_all_commands()` — Displays categorized command list
2. `_show_command_help(cmd_name)` — Detailed help with category + syntax
3. `_show_category(category)` — Commands within a category
4. `_show_syntax(cmd_name)` — Full syntax reference

**Enhanced `handle()` method:**

- Parses `HELP CATEGORY <cat>` syntax
- Parses `HELP SYNTAX <cmd>` syntax
- Partial command matching (e.g., `HELP GO` → `HELP GOTO`)

---

## 2. Smart Prompt Improvements (smart_prompt.py)

### New Features

#### 2.1 Syntax Highlighting

**Enhanced `get_highlighted_command()` method:**

```python
# ANSI color codes for better readability
colors = {
    "command": "\033[1;32m",    # Bold green
    "subcommand": "\033[36m",    # Cyan
    "argument": "\033[37m",      # White
    "option": "\033[33m",        # Yellow
    "path": "\033[35m",          # Magenta
    "reset": "\033[0m",
}
```

**Usage:**

```python
prompt = SmartPrompt()
highlighted = prompt.get_highlighted_command("SAVE notes.md")
# Output: Green "SAVE" + White "notes.md"
```

#### 2.2 Command Help Hints

**New Method: `get_command_help_hint(command)`**

Returns quick help for a command:

```python
hint = prompt.get_command_help_hint("GOTO north")
# Output:
# GOTO (Navigation) → Navigate to connected location
#               Syntax: GOTO <north|south|east|west|up|down|location_id>
```

#### 2.3 Syntax Examples

**New Method: `get_syntax_examples(command, max_examples=3)`**

Extracts example usages from help handler:

```python
examples = prompt.get_syntax_examples("SAVE")
# Output: ["SAVE notes.md", "SAVE GAME mysave"]
```

#### 2.4 Autocomplete with Metadata

**Enhanced `CoreCompleter.get_completions()`:**

- Shows command descriptions on Tab completion
- Shows option hints for flags (--verbose, --force, etc.)
- Displays category for each command
- Uses `display_meta` for visual hints

**Example autocomplete output:**

```
uDOS> G[TAB]
  GOTO   | Navigate to connected location | Navigation
  GRAB   | Pick up objects at location | Inventory
```

#### 2.5 Improved Styling

**Enhanced prompt_toolkit Style:**

```python
self.style = Style.from_dict(
    {
        "prompt": "ansigreen bold",           # Bold green prompt
        "completion": "ansiwhite",             # White completions
        "completion.meta": "ansiyellow",       # Yellow hints
        "scrollbar": "ansicyan",               # Cyan scrollbar
        "scrollbar.background": "ansiblack",   # Dark background
    }
)
```

### CoreCompleter Enhancements

**New Helper Methods:**

1. `_get_command_help(command)` — Returns cached description + category
2. `_get_option_hint(command, option)` — Context-specific hints for flags

**Option Hints Dictionary:**

```python
hints = {
    "--help": "Show help for this command",
    "--verbose": "Verbose output",
    "--force": "Force operation without confirmation",
    "--dry-run": "Show what would be done without doing it",
    "--limit": "Limit results to N items",
    # ... 18 common options with hints
}
```

---

## 3. Usage Examples

### HELP Command Examples

```bash
# Show all commands grouped by category
> HELP

# Get detailed help for GOTO
> HELP GOTO

# List all Navigation commands
> HELP CATEGORY Navigation

# Show full syntax for BACKUP
> HELP SYNTAX BACKUP
```

### Smart Prompt Examples

```bash
# Type "G" and press Tab → shows GOTO, GRAB suggestions with hints
> G[TAB]
  GOTO   | Navigate to connected location | Navigation
  GRAB   | Pick up objects at location | Inventory

# Type "SAVE" and press Tab → shows subcommand/file suggestions
> SAVE [TAB]
  GAME    | Save game state
  --force | Force operation

# Type partial command → see highlighted and predicted options
> GOTO no[TAB]
  → GOTO north (suggested with syntax hint)
```

---

## 4. Architecture

### File Structure

```
core/
├── commands/
│   └── help_handler.py          # HELP command (32 commands + 6 categories)
├── input/
│   ├── smart_prompt.py          # SmartPrompt class with highlighting
│   ├── autocomplete.py          # AutocompleteService
│   └── command_predictor.py     # CommandPredictor
└── ...
```

### Data Flow

```
User Input → SmartPrompt.ask()
    ↓
[Tab/autocomplete] → CoreCompleter.get_completions()
    ↓
    → _get_command_help() → [description | category]
    → _get_option_hint() → [hint for option]
    ↓
Display: command [hint] with syntax highlighting
    ↓
User selects → return input → CommandPredictor.record_command()
```

---

## 5. Testing Checklist

- [ ] `HELP` shows categorized list
- [ ] `HELP GOTO` shows detailed help with category + syntax
- [ ] `HELP CATEGORY Navigation` lists navigation commands
- [ ] `HELP SYNTAX SAVE` shows full syntax with options
- [ ] Tab completion shows hints for commands
- [ ] Tab completion shows hints for options
- [ ] Syntax highlighting renders colors in terminal
- [ ] Fallback mode (basic input) still works
- [ ] Command history works in advanced mode
- [ ] Partial matches work (e.g., `HELP GO` → `GOTO`)

---

## 6. Backward Compatibility

✅ **All changes are backward compatible:**

- Existing code using `help_handler.COMMANDS` dict works unchanged
- New fields (`category`, `syntax`) are optional
- SmartPrompt fallback mode unchanged
- API signatures preserved
- Graceful degradation if prompt_toolkit unavailable

---

## 7. Future Enhancements

Potential improvements:

1. **Command aliases** — `HELP G` → matches `GOTO`
2. **Fuzzy search** — `HELP NAV` → shows all Navigation commands
3. **Interactive tutorial** — `HELP TUTORIAL` → step-by-step guide
4. **Command chaining** — Show which commands can chain together
5. **Context-aware help** — Show relevant commands based on current state
6. **Search history** — `HELP SEARCH` → find commands by keyword
7. **Man page format** — Export help as markdown/PDF

---

## 8. References

- [AGENTS.md](../AGENTS.md) — Development guidelines
- [core/commands/help_handler.py](../core/commands/help_handler.py) — Implementation
- [core/input/smart_prompt.py](../core/input/smart_prompt.py) — Smart prompt
- [docs/specs/core-runtime-status.md](specs/core-runtime-status.md) — Command reference

---

**Status:** ✅ Implemented and documented  
**Last Updated:** 2026-01-24
