# uCODE System Scripts — `/memory/bank/system/`

**Location:** `/memory/bank/system/`
**Purpose:** Auto-executed uCODE scripts for TUI startup and reboot

---

## 📁 Contents

| File | Trigger | Purpose |
|------|---------|---------|
| `startup-script.md` | uCODE TUI starts | Welcome banner, tips |
| `reboot-script.md` | REBOOT command | Post-reboot confirmation |

---

## ✨ How It Works

1. **On Startup:** When uCODE TUI launches, it automatically executes `startup-script.md`
2. **On Reboot:** After REBOOT/RESTART commands, it executes `reboot-script.md`
3. **User Editable:** Both scripts are fully customizable!

---

## 🎨 Available Commands (User-Safe)

These scripts should ONLY use display commands — no system modifications:

```
PRINT "text"              — Display text
BOX --title "Title"       — Create bordered box
PATTERN --type <type>     — Visual patterns (box, line, wave, dots)
PROGRESS --steps N        — Progress indicator
```

### Pattern Types
- `box` — Box border around area
- `line` — Horizontal line (`─`, `━`, `═`)
- `wave` — Wave pattern (`~`)
- `dots` — Dot separator

### Available Variables
- `$SYS_DATE` — Current date
- `$SYS_TIME` — Current time
- `$SYS_SESSION_ID` — Session ID
- `$SYS_VERSION` — uDOS version
- `$USER_NAME` — Current user

---

## ⚠️ Guidelines

### DO:
- ✅ Use PRINT, BOX, PATTERN, PROGRESS
- ✅ Display welcome messages and tips
- ✅ Show brief system status
- ✅ Keep scripts fast (under 2 seconds)

### DON'T:
- ❌ Run SHAKEDOWN, REPAIR, DESTROY
- ❌ Modify system state
- ❌ Access network/external services
- ❌ Run long operations

---

## 📝 Customization Examples

### Simple Welcome
```ucode
PRINT "Welcome to uDOS!"
PRINT "Type HELP for assistance."
```

### Fancy Box
```ucode
BOX --title "uCODE Ready" --width 40 --style double
  PRINT "  User: $USER_NAME"
  PRINT "  Time: $SYS_TIME"
BOX END
```

### Progress Animation
```ucode
PROGRESS --steps 3 --style bar
  STEP "Loading..."
  STEP "Starting..."
  STEP "Ready!"
PROGRESS END
```

---

## 🗂️ Git Status

These template files are tracked in git (not ignored):
- ✅ `startup-script.md` — Tracked
- ✅ `reboot-script.md` — Tracked
- ✅ `README.md` — Tracked

Other files in `/memory/` are gitignored (user data, logs, etc.)

---

**Last Updated:** 2026-01-29
**Version:** 1.0.0
