# NetHack Container

**Status:** Recipe defined (not cloned)  
**Source:** https://github.com/NetHack/NetHack  
**Version:** 3.6.7

## Overview

NetHack is the classic roguelike dungeon exploration game with ASCII graphics.

## uDOS Integration

- **Layers:** 400-455 (Virtual Game realm)
- **Handler:** `core/commands/nethack_handler.py`
- **Wrapper:** `extensions/play/nethack/`

## Build Requirements (TCZ)

```
ncurses
ncurses-dev
compiletc
```

## Commands

```bash
# Clone (Wizard only)
PLUGIN CLONE nethack

# Package (Wizard only)
PLUGIN PACKAGE nethack

# Install on user device
PLUGIN INSTALL nethack-3.6.7.tar.gz
```

## Notes

- Full source compilation required
- ~20MB final package size
- Runs in terminal mode (ncurses)
