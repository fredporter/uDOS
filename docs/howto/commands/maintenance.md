# Maintenance Commands

> [!WARNING]
> Archived legacy page (v1.1). Keep for historical workflow context only.
> Current maintenance/system commands are documented in:
> - `/Users/fredbook/Code/uDOS/docs/howto/commands/system.md`
> - `/Users/fredbook/Code/uDOS/docs/howto/UCODE-COMMAND-REFERENCE.md`

> **Version:** Core v1.1.0.0

Commands for file organization, cleanup, backups, and version history.

---

## TIDY

Organize files into appropriate folders.

### Syntax

```bash
TIDY [scope] [--backup] [--dry-run]
```

### Scopes

| Scope | Description |
| ----- | ----------- |
| (none) | Interactive menu |
| `current` | Current directory only |
| `+subfolders` | Current + subdirectories |
| `workspace` | Entire workspace |
| `all` | Everything including knowledge |

### Examples

```bash
TIDY                  # Interactive menu
TIDY current          # Tidy current dir
TIDY workspace --backup
TIDY all --dry-run    # Preview only
```

### Organization Rules

Files matching patterns are moved to:

| Pattern | Destination |
| ------- | ----------- |
| `*.backup`, `*.bak` | `.archive/` |
| `*.tmp`, `*.temp` | `.tmp/` |
| `*.wip`, `*.draft` | `.dev/` |
| `*.log` (old) | `.archive/logs/` |

---

## CLEAN

Delete files from local-only folders.

### Syntax

```bash
CLEAN [scope] [--type] [--days=N] [--backup] [--dry-run]
```

### Type Flags

| Flag | Description |
| ---- | ----------- |
| `--archives` | Clean `.archive/` folders |
| `--tmp` | Clean `.tmp/` folders |
| `--dev` | Clean `.dev/` folders |
| `--logs` | Clean `memory/logs/` |
| `--backups` | Delete `.backup/` folders |

### Examples

```bash
CLEAN                 # Interactive menu
CLEAN --archives --dry-run
CLEAN workspace --tmp
CLEAN all --days=7    # Keep last 7 days
CLEAN --logs --days=30
```

### Safety

- Requires confirmation for destructive ops
- `--backup` creates backup before cleaning
- `--dry-run` shows what would be deleted
- Respects retention policies

---

## BACKUP

Create timestamped file backups.

### Syntax

```bash
BACKUP <file|folder> [destination]
```

### Examples

```bash
BACKUP config.json            # Backup single file
BACKUP memory/ucode/          # Backup folder
BACKUP important.py ~/backups/
```

### Backup Location

Default location: `.backup/`

```
.backup/
├── 2026-01-07T10-30-00/
│   ├── config.json
│   └── script-example.md
└── 2026-01-06T15-45-00/
    └── ...
```

---

## UNDO

Revert file changes using version history.

### Syntax

```bash
UNDO [file] [--list] [--version N]
```

### Examples

```bash
UNDO                  # Undo last change (any file)
UNDO config.json      # Undo changes to specific file
UNDO config.json --list    # Show version history
UNDO config.json --version 3  # Restore version 3
```

### Version History

Tracked in `.state/versions/`:

```
.state/versions/
└── config.json/
    ├── v001.json
    ├── v002.json
    └── v003.json
```

---

## REDO

Redo undone changes.

### Syntax

```bash
REDO [file]
```

### Examples

```bash
REDO                  # Redo last undo
REDO config.json      # Redo specific file
```

---

## ARCHIVE

Manage archived content.

### Syntax

```bash
ARCHIVE [LIST|SEARCH|RESTORE|COMPRESS]
```

### Examples

```bash
ARCHIVE LIST          # List archived items
ARCHIVE SEARCH "old config"
ARCHIVE RESTORE .archive/2026-01-06/config.json
ARCHIVE COMPRESS      # Compress old archives
```

---

## Folder Conventions

uDOS uses consistent local-only folders:

| Folder | Purpose | Git Status |
| ------ | ------- | ---------- |
| `.archive/` | Version history, completed work | Ignored |
| `.backup/` | Timestamped snapshots | Ignored |
| `.dev/` | Development notes, WIP | Ignored |
| `.tmp/` | Temporary files | Ignored |
| `.cache/` | Computed/cached data | Ignored |
| `.state/` | System state files | Ignored |

### Cleanup Priority

```
.tmp/ → delete freely (temp files)
.cache/ → delete safely (regeneratable)
.dev/ → review before delete (WIP)
.archive/ → keep longer (history)
.backup/ → keep by policy (recovery)
```

---

## Related

- [System Commands](system.md) - SYSTEM REPAIR
- [File Commands](navigation.md#file) - FILE operations
- [TinyCore](../tinycore/README.md) - Persistence

---

*Part of the [Command Reference](README.md)*
