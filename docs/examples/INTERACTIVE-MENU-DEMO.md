---
uid: udos-interactive-menu-demo-20260130
title: Interactive Menu Guidance Demo
tags: [tui, demo, guide, interaction]
status: living
updated: 2026-01-30
---

# Interactive Menu Guidance Demo

## Overview

The uDOS TUI now features **interactive menu guidance** for complex commands. Instead of typing long command strings like:

```bash
DESTROY --reset-all --confirm
```

You can simply type:

```bash
DESTROY
```

And the TUI will **guide you through the options** using the new standardized menu handler.

---

## DESTROY Command Example

### Before (Old Way)

```
[uCODE] > DESTROY --reset-all --confirm

╔════════════════════════════════════════╗
║    ⚠️  NUCLEAR RESET CONFIRMATION ⚠️     ║
╚════════════════════════════════════════╝

This will DESTROY:
  • All user profiles and permissions
  • All configuration files
  • All memory/logs
  • All API keys and credentials
  • System will RESET to factory defaults

... (long output)
```

**Problem:** Must remember command flags and arguments.

### After (New Way)

```
[uCODE] > DESTROY

╔════════════════════════════════════════╗
║      DESTROY/CLEANUP OPTIONS           ║
╚════════════════════════════════════════╝

  1. Wipe User Data (clear users, API keys)
  2. Archive Memory (compost /memory)
  3. Wipe + Archive + Reload (complete cleanup)
  4. Nuclear Reset (factory defaults - DANGER!)
  0. Help

Choose an option [0-4]  1
```

**Benefits:**
- Clear menu with descriptions
- No need to remember flags
- Guided step-by-step
- Easy to understand what each option does

---

## Interactive Flow Example

### Scenario: User wants to reset everything

**Step 1:** Type command
```
[uCODE] > DESTROY
```

**Step 2:** See the menu
```
╔════════════════════════════════════════╗
║      DESTROY/CLEANUP OPTIONS           ║
╚════════════════════════════════════════╝

  1. Wipe User Data (clear users, API keys)
  2. Archive Memory (compost /memory)
  3. Wipe + Archive + Reload (complete cleanup)
  4. Nuclear Reset (factory defaults - DANGER!)
  0. Help

Choose an option [0-4]
```

**Step 3:** Enter your choice
```
Choose an option [0-4]  4
```

**Step 4:** Get confirmation (for nuclear only)
```
Are you absolutely sure? [Yes/No/OK] (Enter=NO)  yes
```

**Step 5:** Action executes
```
🗑️  Wiping user profiles and variables...
   ✓ Deleted 0 users
   ✓ Reset admin user variables and environment
   ✓ Cleared all API keys and credentials
📦 Archiving /memory (logs, bank, private, wizard)...
   ✓ Archived to .archive/compost/2026-01-30_104727
   ✓ Recreated memory directories

✅ Nuclear reset complete!
```

---

## Menu Handler Features

### 1. Numeric Selection
```
Choose an option [1-4]  2
```
- Accepts any number in the valid range
- Re-prompts if out of range
- Helpful error messages

### 2. Enter for Default
```
Choose an option [0-4]  [Enter]
```
- Default behavior depends on context
- For DESTROY: selecting 0 = Help
- For other menus: Enter cancels

### 3. Invalid Input Recovery
```
Choose an option [1-4]  99
❌ Please enter a number between 1-4
Choose an option [1-4]  2
```
- Automatically re-prompts
- Clear error messages
- No need to re-type entire command

### 4. Yes/No/OK Confirmation
```
Are you absolutely sure? [Yes/No/OK] (Enter=NO)  y
```
- Accepts: `y`, `yes`, `n`, `no`, `ok`, `okay`
- Case-insensitive
- `OK` counts as affirmative (like yes)
- Default shown in prompt

---

## How to Use Interactive Menus

### For Complex Commands
Any command with sub-options can now use interactive guidance:

```bash
DESTROY              # Interactive menu
WIZARD               # (future) Interactive Wizard menu
USER                 # (future) Interactive user management
CONFIG               # (future) Interactive config wizard
```

### For Questions
Any yes/no question now uses [Yes/No/OK]:

```
Delete all user data? [Yes/No/OK] (Enter=NO)
Do you want to proceed? [Yes/No/OK] (Enter=YES)
```

---

## Implementation Details

### SmartPrompt Layer
```python
# Menu choice
choice = prompt.ask_menu_choice(
    "Choose an action",
    num_options=4,
    allow_zero=True
)
# Returns: 1-4 or None

# Yes/No/OK
response = prompt.ask_yes_no_ok(
    "Continue",
    default="no"
)
# Returns: "yes", "no", or "ok"
```

### uCODE TUI Layer
```python
# Menu choice
choice = self._ask_menu_choice(
    "Select option",
    5,
    allow_cancel=True
)
# Returns: 1-5 or None

# Yes/No/OK
result = self._ask_yes_no(
    "Confirm deletion",
    default=False
)
# Returns: True or False (ok counts as True)
```

---

## Benefits

✅ **User-Friendly** — Clear descriptions for each option  
✅ **Discoverable** — No need to memorize flags  
✅ **Safe** — Guided confirmations for dangerous ops  
✅ **Consistent** — Same look and feel across all commands  
✅ **Robust** — Automatic re-prompting on invalid input  
✅ **Accessible** — Works in piped contexts (uses simple input)  

---

## Backward Compatibility

All old command formats **still work**:

```bash
DESTROY 1                    # Numeric choice (direct)
DESTROY --reset-all --confirm # Flag format (legacy)
DESTROY --help               # Help (legacy)
```

**New way is recommended** for better UX, but legacy support remains.

---

## Examples by Use Case

### Clear User Data
```
[uCODE] > DESTROY
Choose an option [0-4]  1
```

### Archive Memory
```
[uCODE] > DESTROY
Choose an option [0-4]  2
```

### Complete Cleanup
```
[uCODE] > DESTROY
Choose an option [0-4]  3
```

### Nuclear Reset (with confirmation)
```
[uCODE] > DESTROY
Choose an option [0-4]  4
Are you absolutely sure? [Yes/No/OK] (Enter=NO)  yes
```

### Show Help
```
[uCODE] > DESTROY
Choose an option [0-4]  0
```

---

## Troubleshooting

### Menu doesn't appear
- Check that parser/prompt object was passed to handler
- Verify SmartPrompt is initialized
- Try numeric choice directly: `DESTROY 1`

### Can't select an option
- Make sure you press Enter after typing the number
- Use numbers only (1-4), not letters
- Try again if you see error message

### Doesn't show confirmation
- Some operations auto-execute
- Nuclear reset (option 4) always confirms
- Use `--confirm` flag to skip confirmations (legacy)

---

## Future Commands

The interactive menu pattern is now available for any command:

- **WIZARD** — Server control menu
- **USER** — User management menu
- **CONFIG** — Configuration wizard
- **BACKUP** — Backup/restore menu
- **PLUGIN** — Plugin installation menu

---

**Status:** Live reference  
**Last Updated:** 2026-01-30  
**Version:** v1.0.0
