# TUI Help Command Quick Reference

**Version:** v1.1.0 (Improved)  
**Date:** 2026-01-24

---

## HELP Command Usage

### Basic

```bash
HELP                        # Show all commands (grouped by category)
HELP GOTO                   # Detailed help for GOTO command
HELP CATEGORY Navigation    # List all navigation commands
HELP SYNTAX SAVE            # Show full syntax with all options
```

### Command Categories

| Category                 | Commands                                                          |
| ------------------------ | ----------------------------------------------------------------- |
| **Navigation**           | MAP, PANEL, GOTO, FIND, TELL                                      |
| **Inventory**            | BAG, GRAB, SPAWN                                                  |
| **NPCs & Dialogue**      | NPC, TALK, REPLY                                                  |
| **Files & State**        | SAVE, LOAD, NEW, EDIT                                             |
| **System & Maintenance** | SHAKEDOWN, REPAIR, BACKUP, RESTORE, TIDY, CLEAN, COMPOST, DESTROY |
| **Advanced**             | BINDER, RUN, DATASET, CONFIG, PROVIDER                            |

---

## All Commands (32 Total)

### Navigation Commands

**MAP** — Display location tile grid

```
Syntax: MAP [--follow] [--zoom N] [location_id]
Usage:  MAP [location_id]
Example: MAP L300-BJ10
Notes:  Shows 80x30 grid with tiles, objects, sprites
```

**PANEL** — Show location information panel

```
Syntax: PANEL [--details] [location_id]
Usage:  PANEL [location_id]
Example: PANEL
Notes:  Displays metadata, coordinates, timezone, connections
```

**GOTO** — Navigate to connected location

```
Syntax: GOTO <north|south|east|west|up|down|location_id>
Usage:  GOTO [direction|location_id]
Example: GOTO north or GOTO L300-BK10
Notes:  Directions: north/south/east/west/up/down (or n/s/e/w/u/d)
```

**FIND** — Search for locations by name/type/region

```
Syntax: FIND <query> [--type <type>] [--region <region>] [--limit N]
Usage:  FIND [query] [--type TYPE] [--region REGION]
Example: FIND tokyo or FIND --type major-city
Notes:  Search is case-insensitive
```

**TELL** — Show rich location description

```
Syntax: TELL [--verbose] [location_id]
Usage:  TELL [location_id]
Example: TELL
Notes:  Displays full description with coordinates and connections
```

### Inventory Commands

**BAG** — Manage character inventory

```
Syntax: BAG <list|add|remove|drop|equip> [item] [quantity]
Usage:  BAG [action] [item] [quantity]
Example: BAG list or BAG add sword 1
Notes:  Actions: list, add, remove, drop, equip
```

**GRAB** — Pick up objects at current location

```
Syntax: GRAB <object_name> [quantity]
Usage:  GRAB [object_name]
Example: GRAB sword
Notes:  Adds objects to your inventory
```

**SPAWN** — Create objects/sprites at locations

```
Syntax: SPAWN <object|sprite> <char> <name> at <location_id> <cell>
Usage:  SPAWN [type] [char] [name] at [location] [cell]
Example: SPAWN object key at L300-BJ10 AA00
Notes:  Types: object, sprite
```

### NPC & Dialogue Commands

**NPC** — List NPCs at current or specified location

```
Syntax: NPC [location_id] [--filter <role>]
Usage:  NPC [location_id]
Example: NPC or NPC L300-BJ10
Notes:  Shows NPCs with name, role, disposition, and dialogue state
```

**TALK** — Start conversation with NPC

```
Syntax: TALK <npc_name> [--skip-intro]
Usage:  TALK [npc_name]
Example: TALK Kenji or TALK Elder Tanaka
Notes:  Initiates dialogue tree, presents conversation options
```

**REPLY** — Select dialogue option during conversation

```
Syntax: REPLY <option_number>
Usage:  REPLY [option_number]
Example: REPLY 1 or REPLY 2
Notes:  Continue conversation by choosing numbered option
```

### File & State Commands

**SAVE** — Save file (editor) or game state

```
Syntax: SAVE [path] | SAVE GAME <slot_name> [--force]
Usage:  SAVE [path] | SAVE GAME [slot_name]
Example: SAVE notes.md or SAVE GAME mysave
Notes:  Opens editor for files or saves game state when using SAVE GAME
```

**LOAD** — Load file (editor) or game state

```
Syntax: LOAD [path] | LOAD GAME <slot_name> [--force]
Usage:  LOAD [path] | LOAD GAME [slot_name]
Example: LOAD notes.md or LOAD GAME mysave
Notes:  Opens editor for files or restores game state when using LOAD GAME
```

**NEW** — Create a new markdown file in /memory

```
Syntax: NEW <name> [--no-edit] [--template <type>]
Usage:  NEW [name]
Example: NEW daily-notes
Notes:  Creates/open /memory/<name>.md in editor
```

**EDIT** — Edit a markdown file in /memory

```
Syntax: EDIT <path> [--readonly]
Usage:  EDIT [path]
Example: EDIT notes.md
Notes:  Opens editor for /memory/<path>
```

### System & Maintenance Commands

**SHAKEDOWN** — System validation and diagnostics

```
Syntax: SHAKEDOWN [--verbose] [--focus <module>]
Usage:  SHAKEDOWN
Example: SHAKEDOWN
Notes:  Checks core components, handlers, locations
```

**REPAIR** — Self-healing and system maintenance

```
Syntax: REPAIR [--pull] [--install] [--check] [--dry-run]
Usage:  REPAIR [--pull|--install|--check]
Example: REPAIR --pull
Notes:  Git sync, installer check, dependency verification
```

**BACKUP** — Create a workspace snapshot in .backup

```
Syntax: BACKUP <current|+subfolders|workspace|all> [label] [--compress]
Usage:  BACKUP [current|+subfolders|workspace|all] [label]
Example: BACKUP workspace pre-clean
Notes:  Creates a tar.gz backup in the target .backup folder
```

**RESTORE** — Restore from the latest backup in .backup

```
Syntax: RESTORE <current|+subfolders|workspace|all> [--force] [--date YYYY-MM-DD]
Usage:  RESTORE [current|+subfolders|workspace|all] [--force]
Example: RESTORE workspace
Notes:  Restores the most recent backup (use --force to overwrite)
```

**TIDY** — Organize junk files into .archive

```
Syntax: TIDY <current|+subfolders|workspace|all> [--dry-run]
Usage:  TIDY [current|+subfolders|workspace|all]
Example: TIDY workspace
Notes:  Moves stray/temporary files into .archive (no deletion)
```

**CLEAN** — Reset workspace to default state (archive extras)

```
Syntax: CLEAN <current|+subfolders|workspace|all> [--aggressive] [--dry-run]
Usage:  CLEAN [current|+subfolders|workspace|all]
Example: CLEAN workspace
Notes:  Moves non-default files into .archive (no deletion)
```

**COMPOST** — Collect .archive/.backup/.tmp into /.compost

```
Syntax: COMPOST <current|+subfolders|workspace|all> [--compress]
Usage:  COMPOST [current|+subfolders|workspace|all]
Example: COMPOST all
Notes:  Moves archive/backup/temp folders into repo /.compost
```

**DESTROY** — Wipe and reinstall (Dev TUI only)

```
Syntax: DESTROY [--confirm]
Usage:  DESTROY
Example: DESTROY
Notes:  Use Dev TUI to run DESTROY with confirmation
```

### Advanced Commands

**CONFIG** — Manage Wizard configuration

```
Syntax: CONFIG <SHOW|LIST|EDIT|SETUP> [file] [--validate]
Usage:  CONFIG [SHOW|LIST|EDIT <file>|SETUP]
Example: CONFIG SHOW or CONFIG EDIT wizard.json
Notes:  View status, list config files, edit configs, run provider setup
```

**PROVIDER** — Manage AI/service providers

```
Syntax: PROVIDER <LIST|STATUS|ENABLE|DISABLE|SETUP> [<id>] [--test]
Usage:  PROVIDER [LIST|STATUS <id>|ENABLE <id>|DISABLE <id>|SETUP <id>]
Example: PROVIDER LIST or PROVIDER ENABLE github
Notes:  Configure AI providers (ollama, github, openai, etc.)
```

**BINDER** — Core binder operations

```
Syntax: BINDER <PICK|COMPILE|CHAPTERS|HELP> [<id>] [--output <dir>]
Usage:  BINDER [PICK|COMPILE <id>|CHAPTERS <id>|HELP]
Example: BINDER PICK or BINDER COMPILE my-binder markdown json
Notes:  Compile binder outputs and browse files
```

**RUN** — Execute TS markdown runtime script

```
Syntax: RUN <file> [section_id] | RUN PARSE <file> [--verbose]
Usage:  RUN <file> [section_id] | RUN PARSE <file>
Example: RUN core/examples/sample.md intro
Notes:  Executes a markdown script or lists parsed sections
```

**DATASET** — List and validate datasets

```
Syntax: DATASET <LIST|VALIDATE|BUILD|REGEN> [<id>] [--force]
Usage:  DATASET [LIST|VALIDATE <id>|BUILD <id>|REGEN <id>]
Example: DATASET LIST or DATASET REGEN locations
Notes:  Validates and regenerates datasets for 80x30 layers
```

---

## Smart Prompt Features

### Autocomplete (Press Tab)

- Shows matching commands with descriptions and categories
- Shows matching options with hints for flags
- Supports partial matching (e.g., "G" → "GOTO", "GRAB")
- Displays syntax hints for context-aware help

### Syntax Highlighting

Commands are displayed with color coding:

- **Bold Green** — Command names
- **Cyan** — Subcommands
- **White** — Arguments
- **Yellow** — Flags/options
- **Magenta** — File paths

### Example Help Integration

```bash
uDOS> HELP[ENTER]
  ┌─────────────────────────────────┐
  │ uDOS Command Reference (v1.1.0) │
  └─────────────────────────────────┘

  Navigation:
    MAP          - Display location tile grid
    PANEL        - Show location information
    GOTO         - Navigate to connected location
    FIND         - Search for locations
    TELL         - Show rich location description

  ... (5 more categories)

  Type 'HELP [command]' for detailed help.
  Example: HELP GOTO or HELP TALK
```

---

## Tips & Tricks

1. **Quick Help:** Type command and press Tab to see description
2. **Category Help:** `HELP CATEGORY Navigation` shows all nav commands
3. **Full Syntax:** `HELP SYNTAX SAVE` shows all options for a command
4. **Partial Matching:** `HELP GO` auto-completes to `GOTO`
5. **History:** Use arrow keys to browse previous commands
6. **Search:** Use Ctrl+R to search command history

---

## See Also

- [HELP-COMMAND-IMPROVEMENTS.md](HELP-COMMAND-IMPROVEMENTS.md) — Full documentation
- [docs/specs/core-runtime-status.md](specs/core-runtime-status.md) — Command status
- [AGENTS.md](../AGENTS.md) — Development guidelines

---

**Status:** v1.1.0 (Current)  
**Last Updated:** 2026-01-24
