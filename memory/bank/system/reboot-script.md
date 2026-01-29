---
title: uCODE Reboot Script
id: reboot
version: 1.0.0
type: script
auto_exec: true
description: Auto-executed after REBOOT command. User-editable restart sequence.
---

# uCODE Reboot Script

This script runs automatically after a REBOOT command.
Customize it to show post-reboot information!

## Reboot Complete Banner

```ucode
PRINT
PATTERN --type wave --width 60 --char "~"
PRINT
PRINT "  ╔══════════════════════════════════════════╗"
PRINT "  ║       🔄 REBOOT COMPLETE                 ║"
PRINT "  ╚══════════════════════════════════════════╝"
PRINT
PATTERN --type wave --width 60 --char "~"
```

## System Status Box

```ucode
BOX --title "System Restored" --width 50 --style double
  PRINT "  ✅ Handlers: Reloaded"
  PRINT "  ✅ Services: Active"
  PRINT "  ✅ State: Restored"
  PRINT "  ✅ Session: $SYS_SESSION_ID"
BOX END
```

## Reload Progress

```ucode
PRINT
PRINT "Restarting services..."
PROGRESS --steps 4 --delay 150 --style bar
  STEP "Reloading command handlers..."
  STEP "Reconnecting services..."
  STEP "Restoring session state..."
  STEP "Complete!"
PROGRESS END
```

## Quick Status Summary

```ucode
PATTERN --type dots --width 50 --count 3
PRINT
BOX --title "Quick Status" --width 40
  PRINT "  User: $USER_NAME"
  PRINT "  Time: $SYS_TIME"
  PRINT "  Mode: Normal"
BOX END
PRINT
PATTERN --type dots --width 50 --count 3
```

## Reboot Tips

```ucode
PRINT
PRINT "  💡 After Reboot:"
PRINT "     • Run STATUS to verify all systems"
PRINT "     • Run LOGS --recent for any errors"
PRINT "     • Your session state was preserved"
PRINT
```

## Ready Message

```ucode
PRINT
PATTERN --type line --char "━" --width 50
PRINT "  System ready. Type any command to continue."
PATTERN --type line --char "━" --width 50
PRINT
```

---

## Customization Guide

### When This Script Runs:
- After `REBOOT` command
- After `RESTART --repair` command
- After `REPAIR --reboot` command

### Available Commands:
- `PRINT "text"` — Display text
- `BOX --title "Title" --style <single|double>` — Bordered boxes
- `PATTERN --type <type>` — Visual patterns
- `PROGRESS --steps N --style <dots|bar|spinner>` — Progress indicators

### Pattern Types:
- `box` — Box border
- `line` — Horizontal line
- `wave` — Wave pattern
- `dots` — Dot separator

### Variables:
- `$SYS_DATE` — Current date
- `$SYS_TIME` — Current time
- `$SYS_SESSION_ID` — Session identifier
- `$USER_NAME` — Current user
- `$REBOOT_REASON` — Why reboot occurred (if available)

### Tips:
1. Keep it brief (reboot should be fast)
2. Show confirmation that systems are working
3. Avoid re-running setup commands
4. Provide quick status at a glance

---

**Location:** /memory/bank/system/reboot-script.md
**Executed:** After REBOOT/RESTART commands
**Editable:** Yes — customize your reboot experience!
