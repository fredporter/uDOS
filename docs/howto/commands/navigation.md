# Navigation Commands

> **Version:** Core v1.1.0.0

Commands for tile navigation and file operations.

---

## TILE

Navigate content tiles in the TUI.

### Syntax

```bash
TILE [number|+|-|HOME|INDEX|STATUS]
```

### Tile Ranges

| Range | Category |
| ----- | -------- |
| 100-199 | System & Status |
| 200-299 | User Content |
| 300-399 | Knowledge Bank |
| 400-499 | Commands & Help |
| 500-599 | Tools |
| 600-699 | Games |
| 700-799 | Custom |
| 800-899 | Dev/Debug |

### Examples

```bash
TILE 100              # Go to tile 100
TILE +                # Next tile
TILE -                # Previous tile
TILE HOME             # Go to home (100)
TILE INDEX            # Show tile index
TILE STATUS           # Show tile system status
```

### uCODE Format

```
[TILE|100]
[TILE|+]
[TILE|INDEX]
```

---

## FILE

File operations within the workspace.

### Syntax

```bash
FILE [subcommand] [path] [options]
```

### Subcommands

| Command | Description |
| ------- | ----------- |
| `LIST [path]` | List directory contents |
| `SHOW <file>` | Display file contents |
| `EDIT <file>` | Open in editor |
| `NEW <file>` | Create new file |
| `DELETE <file>` | Delete file |
| `COPY <src> <dst>` | Copy file |
| `MOVE <src> <dst>` | Move/rename file |
| `FIND <pattern>` | Search for files |

### Examples

```bash
FILE LIST memory/
FILE LIST memory/ucode/ --all
FILE SHOW readme.md
FILE EDIT script-example.md
FILE NEW notes.md
FILE DELETE old.txt
FILE COPY doc.md backup/doc.md
FILE MOVE old.py new.py
FILE FIND *-script.md
```

### Path Shortcuts

| Shortcut | Expands To |
| -------- | ---------- |
| `~` | Home directory |
| `.` | Current directory |
| `memory/` | User data folder |
| `knowledge/` | Knowledge bank |

---

## EDIT

Open file in editor (alias for FILE EDIT).

### Syntax

```bash
EDIT <file> [--gui]
```

### Examples

```bash
EDIT readme.md        # Edit in TUI
EDIT readme.md --gui  # Open in desktop app
```

---

## OPEN

Open file or URL.

### Syntax

```bash
OPEN <file|url> [--app]
```

### Examples

```bash
OPEN readme.md        # Open in default handler
OPEN document.udos.md --app  # Open in uCode Markdown App
OPEN https://example.com     # Open URL (Wizard only)
```

---

## FIND

Search for files (alias for FILE FIND).

### Syntax

```bash
FIND <pattern> [path] [--content]
```

### Examples

```bash
FIND *-script.md      # Find by naming pattern
FIND test* memory/    # Find in specific path
FIND "TODO" --content # Search file contents
```

---

## SEARCH

Search knowledge bank and documents.

### Syntax

```bash
SEARCH <query> [--type TYPE] [--limit N]
```

### Examples

```bash
SEARCH water purification
SEARCH fire --type knowledge
SEARCH shelter --limit 5
```

### Search Types

| Type | Description |
| ---- | ----------- |
| `all` | Everything (default) |
| `knowledge` | Knowledge bank only |
| `commands` | Command reference |
| `files` | File names |
| `content` | File contents |

---

## HELP

Get help on commands and system.

### Syntax

```bash
HELP [command|topic]
```

### Examples

```bash
HELP                  # General help
HELP TILE             # Command-specific help
HELP navigation       # Topic help
HELP ucode            # uCODE syntax help
```

---

## Related

- [TUI Guide](../tui/README.md) - Interface navigation
- [Content Commands](content.md) - GUIDE, BUNDLE
- [System Commands](system.md) - SYSTEM, DEV

---

*Part of the [Command Reference](README.md)*
