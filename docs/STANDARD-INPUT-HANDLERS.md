---
uid: udos-standard-input-handlers-20260130
title: Standard Input Handlers - uDOS TUI
tags: [tui, input, reference, guide]
status: living
updated: 2026-01-30
---

# Standard Input Handlers

The uDOS TUI provides two standardized input handlers for consistent user experience across all interactive components.

## 1. Yes/No/OK Handler

**Purpose:** Ask binary or conditional questions with three possible responses.

### Format

```
Question? [Yes/No/OK] (Enter=DEFAULT)
```

### Behavior

| Input | Result | Notes |
|-------|--------|-------|
| `y` or `yes` | Yes | Case-insensitive |
| `n` or `no` | No | Case-insensitive |
| `ok` or `okay` | OK | Treated as "yes" |
| Enter (empty) | Use default | Default is shown in prompt |

### Python API (SmartPrompt)

```python
response = prompt.ask_yes_no_ok(
    question="Do you want to proceed",
    default="no"  # Options: "yes", "no", "ok"
)

# Returns: "yes", "no", or "ok"
if response in ["yes", "ok"]:
    # User confirmed
    pass
```

### Python API (uCODE TUI)

```python
result = self._ask_yes_no(
    question="Do you want to proceed",
    default=True  # True = Yes, False = No
)

# Returns: True or False (ok counts as yes)
if result:
    # User confirmed
    pass
```

## 2. Menu Choice Handler

**Purpose:** Ask users to select from a numbered list of options.

### Format

```
Choose an option [1-N]
```

### Behavior

| Input | Result | Notes |
|-------|--------|-------|
| `1` to `N` | Select option | Must be valid number |
| Enter (empty) | Cancel (0) or None | Depends on allow_cancel |

### Python API (SmartPrompt)

```python
choice = prompt.ask_menu_choice(
    prompt_text="Choose an action",
    num_options=5,
    allow_zero=True  # Allow cancellation
)

# Returns: 1-5 or 0 (if allow_zero=True) or None (if allow_zero=False)
if choice and choice > 0:
    selected = options[choice - 1]
```

### Python API (uCODE TUI)

```python
choice = self._ask_menu_choice(
    prompt="Choose an action",
    num_options=5,
    allow_cancel=True  # Allow cancellation
)

# Returns: 1-5 or None
if choice:
    selected = options[choice - 1]
```

## Usage Examples

### Example 1: Confirmation Dialog

```python
# In command handler
if self._ask_yes_no("Delete all user data", default=False):
    perform_deletion()
else:
    print("Cancelled")
```

**Output:**
```
Delete all user data? [Yes/No/OK] (Enter=NO) y
```

### Example 2: Menu Selection

```python
# In command handler
options = ["Option A", "Option B", "Option C"]
print("Choose an option:")
for i, opt in enumerate(options, 1):
    print(f"  {i}. {opt}")

choice = self._ask_menu_choice("Select", len(options), allow_cancel=True)
if choice:
    print(f"You selected: {options[choice - 1]}")
else:
    print("Cancelled")
```

**Output:**
```
Choose an option:
  1. Option A
  2. Option B
  3. Option C
Select an option [0-3]  2
You selected: Option B
```

### Example 3: Form Field Selection

```python
# Automatic in form handling
field = {
    "type": "select",
    "label": "Operating System",
    "options": ["macOS", "Linux", "Windows"],
    "required": True
}

# uCODE TUI automatically:
# 1. Shows menu with options
# 2. Calls self._ask_menu_choice()
# 3. Returns selected option
response = self._collect_field_response(field)
```

**Output:**
```
Operating System:
  1. macOS
  2. Linux
  3. Windows
Choose an option [1-3]  1
```

## Error Handling

### Invalid Input (Yes/No/OK)

```
Question? [Yes/No/OK] (Enter=NO) xyz
❌ Please enter Yes, No, or OK
Question? [Yes/No/OK] (Enter=NO) y
```

### Invalid Input (Menu Choice)

```
Choose an option [1-3]  5
❌ Please enter a number between 1-3
Choose an option [1-3]  2
```

### Non-numeric Input (Menu Choice)

```
Choose an option [1-3]  abc
❌ Please enter a valid number (1-3)
Choose an option [1-3]  2
```

## Design Principles

1. **Consistent Format** — Both handlers use standardized prompts and behavior
2. **Clear Defaults** — Default always shown in prompt (YES, NO, or range)
3. **Forgiving Input** — Accept common variations (y/yes, n/no, ok/okay)
4. **Error Recovery** — Invalid input automatically re-prompts
5. **No Terminal Tricks** — Uses simple `input()`, works in piped/script contexts

## Integration Points

### Where These Handlers Are Used

| Component | Usage |
|-----------|-------|
| **Setup Story** | Field collection (select, checkbox) |
| **DESTROY Command** | Confirmation before nuclear reset |
| **System Dialogs** | Any yes/no question in TUI |
| **Menu Navigation** | Option selection in any menu |
| **Plugin Management** | Confirmation prompts |

### How to Add New Uses

In any command handler:

```python
from core.tui.ucode import uCODETUI

class MyHandler:
    def __init__(self, prompt):
        self.prompt = prompt  # SmartPrompt instance
        self.tui = uCODETUI()
    
    def handle_something(self):
        # Use TUI methods
        if self.tui._ask_yes_no("Confirm action"):
            # User said yes/ok
            pass
```

## Reference

### SmartPrompt (core/input/smart_prompt.py)

- `ask_yes_no_ok(question, default="no")` → "yes" | "no" | "ok"
- `ask_menu_choice(prompt_text, num_options, allow_zero=False)` → int | None

### uCODE TUI (core/tui/ucode.py)

- `_ask_yes_no(question, default=True)` → bool
- `_ask_menu_choice(prompt, num_options, allow_cancel=True)` → int | None

---

**Status:** Live reference  
**Last Updated:** 2026-01-30  
**Version:** v1.0.0
