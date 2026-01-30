---
uid: udos-enhanced-prompt-quick-ref-20260130
title: Enhanced Prompt Quick Reference
tags: [tui, input, reference, quick-ref]
status: living
updated: 2026-01-30
---

# Enhanced Prompt Quick Reference

**Quick guide for using the 2-line context display system.**

---

## Confirmation (Yes/No)

```python
result = prompt.ask_confirmation(
    question="Proceed with action",
    default=True,
    help_text="Optional help text",
    context="Optional context"
)
```

**User inputs:**
- `1`, `y`, `yes`, `ok`, `Enter` (if default=True) → `True`
- `0`, `n`, `no`, `x`, `cancel`, `Enter` (if default=False) → `False`

---

## Menu Selection

```python
choice = prompt.ask_menu(
    title="Menu Title",
    options=["Option 1", "Option 2", "Option 3"],
    help_text="Optional help",
    allow_cancel=True
)
# Returns: 1, 2, 3, or None (if cancelled)
```

---

## Variable Input

```python
value = prompt.ask_variable(
    var_name="VAR_NAME",
    current_value="current_val",
    var_type="text",
    help_text="Enter value",
    required=False
)
```

---

## Story Form Field

```python
field = {
    "name": "fieldname",
    "label": "Field Label",
    "type": "text|select|checkbox",
    "required": True,
    "options": []  # For select type
}

value = prompt.ask_story_field(field, previous_value)
```

---

## Standard Format

**All prompts show:**

```
  ╭─ Line 1: Current value / Predictions / Context
  ╰─ Line 2: Help text / Syntax / Options
Prompt text > _
```

---

## Toggle Features

```python
# Disable/enable context display
prompt.toggle_context_display(False)  # Disable
prompt.toggle_context_display(True)   # Enable
prompt.toggle_context_display()       # Toggle

# Disable/enable predictions
prompt.toggle_predictions(False)
```

---

## In uCODE TUI

```python
# Already integrated - use as normal
result = self._ask_yes_no(
    "Question",
    help_text="Help",
    context="Context"
)

choice = self._ask_menu_choice(
    "Choose",
    num_options=3,
    help_text="Help"
)

# Story fields automatically use enhanced prompt
response = self._collect_field_response(field, previous_value)
```

---

**See:** [ENHANCED-PROMPT-SYSTEM.md](ENHANCED-PROMPT-SYSTEM.md) for full documentation
