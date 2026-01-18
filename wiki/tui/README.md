# TUI (Terminal User Interface)

> **Version:** Core v1.0.0.64

The uDOS TUI is a teletext-inspired terminal interface with a 40x25 character grid, rainbow splash, and tile-based navigation.

---

## Overview

### Design Philosophy

- **Teletext Aesthetic**: Retro 40-column design
- **Tile Navigation**: Page-number based navigation (100-899)
- **Color Modes**: Rainbow splash, themes, syntax highlighting
- **Keyboard-First**: Full keyboard navigation
- **Offline-Ready**: No network required for core features

### Screen Layout

```
┌────────────────────────────────────────┐
│ uDOS v1.0.0.64 ░░░░░░░░░░░░░░░░░ P:100 │  ← Header
├────────────────────────────────────────┤
│                                        │
│                                        │
│           Content Area                 │  ← 40x20
│           (40 x 20 chars)              │
│                                        │
│                                        │
├────────────────────────────────────────┤
│ > █                                    │  ← Input
├────────────────────────────────────────┤
│ F1:Help F2:Index F3:Back F4:Home       │  ← Status
└────────────────────────────────────────┘
```

---

## Starting uDOS

```bash
# Interactive mode
./start_udos.sh

# Run a script
./start_udos.sh memory/ucode/scripts/example.upy

# With specific command
./start_udos.sh -c "TILE 100"
```

### Startup Sequence

1. **Environment Check**: Verifies Python venv
2. **Config Load**: Reads `core/config/settings.json`
3. **Rainbow Splash**: Animated startup (if enabled)
4. **Home Tile**: Loads TILE 100

---

## Navigation

### Tile Numbers

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

### Navigation Commands

```bash
TILE 100              # Go to specific tile
TILE +                # Next tile
TILE -                # Previous tile
TILE HOME             # Go to home (100)
TILE INDEX            # Show tile index
```

### Keyboard Shortcuts

| Key | Action |
| --- | ------ |
| F1 | Help |
| F2 | Tile Index |
| F3 | Back |
| F4 | Home (Tile 100) |
| Ctrl+C | Exit |
| Tab | Autocomplete |
| ↑/↓ | Command history |

---

## Color System

### Themes

```bash
COLOR rainbow         # Enable rainbow mode
COLOR teletext        # Classic teletext
COLOR dark            # Dark theme
COLOR light           # Light theme
COLOR retro           # CRT-style
```

### Palette Commands

```bash
PALETTE LIST          # Show available palettes
PALETTE SHOW retro    # Preview palette
PALETTE SET retro     # Apply palette
PALETTE EDIT          # Open palette editor
```

### Syntax Highlighting

The TUI supports syntax highlighting in code views:

- **Python**: `.py` files
- **Markdown**: `.md` files
- **uPY Scripts**: `.upy` files
- **JSON/YAML**: Config files

---

## Prompt Modes

Change the input prompt style:

```bash
MODE GHOST            # Minimal prompt
MODE TOMB             # Gothic style
MODE CRYPT            # Encrypted look
MODE DEFAULT          # Standard prompt
```

### Mode Examples

```
Default:  > █
Ghost:    _ 
Tomb:     ⚰ 
Crypt:    🔐 
```

---

## Pager System

Long content uses the built-in pager:

### Pager Controls

| Key | Action |
| --- | ------ |
| Space | Next page |
| b | Previous page |
| q | Quit pager |
| / | Search |
| n | Next search result |
| g | Go to top |
| G | Go to bottom |

### Pager Indicators

```
── Page 1 of 5 ── [Space: next, b: back, q: quit] ──
```

---

## Dev Mode UI

When Dev Mode is active:

```
┌────────────────────────────────────────┐
│ uDOS v1.0.0.64 🧙 DEV ░░░░░░░░░ P:100 │
├────────────────────────────────────────┤
│ Provider: mistral                      │
│ Quota: 80/100                          │
├────────────────────────────────────────┤
```

### Debug Panel

```bash
DEV MODE ON
L                     # Open debug panel
```

Shows:
- Recent log entries
- Command trace
- Error details
- Performance metrics

---

## Configuration

### Settings File

`core/config/settings.json`:

```json
{
  "tui": {
    "width": 40,
    "height": 25,
    "rainbow_splash": true,
    "theme": "teletext",
    "prompt_mode": "default"
  }
}
```

### Environment Variables

```bash
UDOS_NO_COLOR=1       # Disable colors
UDOS_DEBUG=1          # Enable debug output
UDOS_WIDTH=80         # Override width
```

---

## Troubleshooting

### Common Issues

**TUI won't start:**
```bash
# Check virtual environment
source .venv/bin/activate
python --version  # Should be 3.10+

# Check logs
tail -f memory/logs/session-commands-$(date +%Y-%m-%d).log
```

**Colors not showing:**
```bash
# Check terminal support
echo $TERM          # Should be xterm-256color or similar
COLOR STATUS        # Check color system
```

**Tiles not loading:**
```bash
TILE STATUS         # Check tile system
FILE LIST knowledge/ # Verify knowledge files
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│                  TUI                     │
│  ┌─────────────────────────────────┐    │
│  │          Grid Renderer          │    │
│  │      (40x25 character grid)     │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│  ┌──────────────┴──────────────────┐    │
│  │         Smart Prompt            │    │
│  │   (Input parsing & completion)  │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│  ┌──────────────┴──────────────────┐    │
│  │       Command Router            │    │
│  │    (uDOS_commands.py)           │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│  ┌──────────────┴──────────────────┐    │
│  │    Handler Layer                │    │
│  │  (95+ command handlers)         │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## Related

- [Commands](commands/README.md) - Command reference
- [uCODE](../VISION.md#ucode) - uCODE syntax
- [Dev Mode](wizard/README.md#dev-mode) - Wizard features

---

*Part of the [uDOS Wiki](README.md)*
