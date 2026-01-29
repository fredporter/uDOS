---
title: uCODE Startup Script
id: startup
version: 1.0.0
type: script
auto_exec: true
description: Auto-executed on uCODE TUI startup. User-editable welcome sequence.
---

# uCODE Startup Script

This script runs automatically when uCODE TUI starts.
Edit this file to customize your startup experience!

## Welcome Banner

```ucode
PATTERN --type box --width 60 --char "═"
PRINT
PRINT "   ██╗   ██╗ ██████╗ ██████╗ ██████╗ ███████╗"
PRINT "   ██║   ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝"
PRINT "   ██║   ██║██║     ██║   ██║██║  ██║█████╗  "
PRINT "   ██║   ██║██║     ██║   ██║██║  ██║██╔══╝  "
PRINT "   ╚██████╔╝╚██████╗╚██████╔╝██████╔╝███████╗"
PRINT "    ╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝"
PRINT
PATTERN --type box --width 60 --char "═"
```

## System Info Box

```ucode
BOX --title "Welcome to uCODE" --width 50
  PRINT "  Session: $SYS_SESSION_ID"
  PRINT "  User: $USER_NAME"
  PRINT "  Date: $SYS_DATE"
  PRINT "  Time: $SYS_TIME"
BOX END
```

## Progress Indicator (Visual Flourish)

```ucode
PRINT
PRINT "Loading systems..."
PROGRESS --steps 5 --delay 100
  STEP "Initializing TUI..."
  STEP "Loading handlers..."
  STEP "Connecting services..."
  STEP "Setting up environment..."
  STEP "Ready!"
PROGRESS END
```

## Quick Tips

```ucode
PATTERN --type line --char "─" --width 50
PRINT
PRINT "  💡 Quick Tips:"
PRINT "     • Type HELP for all commands"
PRINT "     • Type STATUS for system info"
PRINT "     • Type MAP for navigation"
PRINT "     • Type PATTERN --help for visuals"
PRINT
PATTERN --type line --char "─" --width 50
```

## Final Welcome

```ucode
PRINT
PRINT "  Type a command to begin, or HELP for assistance."
PRINT
```

---

## Customization Guide

### Available Commands for Startup:
- `PRINT "text"` — Display text
- `BOX --title "Title"` — Create bordered boxes
- `PATTERN --type <type>` — Visual patterns (box, line, dots, wave)
- `PROGRESS --steps N` — Progress indicators

### Variables Available:
- `$SYS_DATE` — Current date
- `$SYS_TIME` — Current time
- `$SYS_SESSION_ID` — Session identifier
- `$USER_NAME` — Current user
- `$SYS_VERSION` — uDOS version

### Tips:
1. Keep startup fast (under 2 seconds)
2. Avoid system commands (SHAKEDOWN, REPAIR, etc.)
3. Use PATTERN for visual flair
4. Personalize your welcome message!

---

**Location:** /memory/bank/system/startup-script.md
**Executed:** On every uCODE TUI startup
**Editable:** Yes — customize freely!
