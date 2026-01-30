---
uid: udos-enhanced-prompt-quickstart-20260130
title: Enhanced Prompt System - Quick Start
tags: [tui, input, quickstart, guide]
status: living
updated: 2026-01-30
---

# Enhanced Prompt System - Quick Start

**Get started with the new 2-line context display in 5 minutes.**

---

## What's New?

Before you type, you now see:
```
  ╭─ Line 1: Current value or context
  ╰─ Line 2: Help text or options
Your prompt > _
```

Plus standardized `[1|0|Yes|No|OK|Cancel]` confirmations:
- Type `1` or `y` or `yes` or `ok` for Yes
- Type `0` or `n` or `no` or `x` for No/Cancel
- Press `Enter` for default

---

## Try It Now

### 1. Test the Interactive Suite

```bash
cd /Users/fredbook/Code/uDOS
python core/tests/test_enhanced_prompt_interactive.py
```

This will walk you through:
- Confirmations with context
- Menu selections
- Variable input
- Story form fields
- Context toggle

### 2. Use in uCODE TUI

```bash
python uDOS.py
```

Then try:
```
STORY wizard-setup    # See enhanced form collection
DESTROY               # See enhanced confirmation menus
HELP                  # Any command with prompts
```

---

## Quick Examples

### In Your Code

```python
from core.input import EnhancedPrompt

prompt = EnhancedPrompt()

# Confirmation
proceed = prompt.ask_confirmation(
    question="Deploy to production",
    default=False,  # No by default (safer)
    help_text="[1|0|Yes|No|OK|Cancel] - This cannot be undone",
    context="3 services will be restarted"
)

# Menu
choice = prompt.ask_menu(
    title="Select environment",
    options=["Dev", "Staging", "Production"],
    help_text="Choose deployment target",
    allow_cancel=True
)

# Variable
api_key = prompt.ask_variable(
    var_name="API_KEY",
    current_value=os.getenv("API_KEY"),
    var_type="secret",
    help_text="Get from https://platform.example.com/keys",
    required=True
)
```

---

## In uCODE TUI Handlers

Your existing code still works, but you can enhance it:

```python
class MyHandler(BaseCommandHandler):
    def handle(self, command, params, grid, parser):
        from core.tui.ucode import uCODETUI
        tui = uCODETUI()
        
        # Old way (still works)
        result = tui._ask_yes_no("Continue")
        
        # New way (enhanced)
        result = tui._ask_yes_no(
            question="Continue",
            default=True,
            help_text="This will modify 3 files",
            context="Backup created at /path/to/backup"
        )
```

---

## Key Shortcuts

| Input | Meaning | Context |
|-------|---------|---------|
| `1` | Yes (quick) | Confirmations |
| `0` | No (quick) | Confirmations |
| `Enter` | Default | All prompts |
| `x` | Cancel/Exit | Confirmations |
| Number | Select option | Menus |

---

## Common Patterns

### 1. Risky Operations

```python
confirm = prompt.ask_confirmation(
    question="Delete all user data",
    default=False,  # MUST be False for dangerous ops
    help_text="⚠️  This CANNOT be undone - type NO to cancel",
    context="3 user accounts will be permanently deleted"
)
```

### 2. Multi-Step Workflows

```python
# Step 1: Choose
env = prompt.ask_menu("Choose environment", ["Dev", "Prod"])

# Step 2: Confirm with context
if env == 2:  # Production
    confirm = prompt.ask_confirmation(
        "Deploy to production",
        default=False,
        context=f"Selected: Production (env #{env})",
        help_text="⚠️  Live users will be affected"
    )
```

### 3. Optional Configuration

```python
advanced = prompt.ask_confirmation(
    "Configure advanced settings",
    default=False,
    help_text="Skip for default configuration",
    context="Most users don't need this"
)

if advanced:
    # Show advanced options
    pass
```

---

## Troubleshooting

### Context Lines Not Showing

```python
# Check if context is enabled
print(f"Context enabled: {prompt.show_context}")

# Enable it
prompt.toggle_context_display(True)
```

### Want Old Behavior

```python
# Disable context display
prompt.toggle_context_display(False)

# Now prompts work like before
result = prompt.ask_confirmation("Question", default=True)
```

---

## Documentation

- **Full Docs:** [ENHANCED-PROMPT-SYSTEM.md](ENHANCED-PROMPT-SYSTEM.md)
- **Quick Ref:** [ENHANCED-PROMPT-QUICK-REF.md](ENHANCED-PROMPT-QUICK-REF.md)
- **Summary:** [UCODE-TUI-REBUILD-SUMMARY.md](UCODE-TUI-REBUILD-SUMMARY.md)

---

## What's Next?

1. **Try the interactive tests** — Get familiar with the new system
2. **Use it in your handlers** — Add `help_text` and `context` to prompts
3. **Enjoy faster input** — Use `1` and `0` for quick yes/no

---

**Status:** Ready to Use  
**Version:** v1.0.0  
**Updated:** 2026-01-30
