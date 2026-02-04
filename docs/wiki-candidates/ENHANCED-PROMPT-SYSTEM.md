---
uid: udos-enhanced-prompt-system-20260130
title: Enhanced Prompt System - 2-Line Context Display
tags: [tui, input, reference, guide, enhanced]
status: living
updated: 2026-01-30
---

# Enhanced Prompt System

**Version:** v1.0.0  
**Date:** 2026-01-30  
**Component:** core/input/enhanced_prompt.py

---

## Overview

The Enhanced Prompt System provides rich, context-aware input prompts with a standardized 2-line display format that shows users what they're working with before they type.

### Key Features

1. **2-Line Context Display**
   - Line 1: Current/previous value or predictive suggestions
   - Line 2: Help text, syntax hints, or available options

2. **Standardized Confirmations**
   - Format: `[1|0|Yes|No|OK|Cancel]`
   - Mappings: `1, y, yes, ok, Enter (default) → True`
   - Mappings: `0, n, no, x, cancel, Enter (default) → False`

3. **Variable Collection with Context**
   - Shows current values before prompting
   - Displays type hints and requirements
   - Indicates optional vs required fields

4. **Story Form Integration**
   - Enhanced field collection
   - Previous values displayed
   - Type-appropriate prompts

---

## Architecture

### Class Hierarchy

```
SmartPrompt (base)
    ├── ask()
    ├── ask_yes_no_ok()
    └── ask_menu_choice()
         ↓
EnhancedPrompt (extends SmartPrompt)
    ├── ask_with_context()          # General input with 2-line display
    ├── ask_confirmation()           # Standardized [1|0|Yes|No|OK|Cancel]
    ├── ask_menu()                   # Menu selection with context
    ├── ask_variable()               # Variable collection with hints
    ├── ask_story_field()            # Story form field with full context
    ├── toggle_context_display()     # Enable/disable context lines
    └── toggle_predictions()         # Enable/disable predictions
```

---

## Usage Examples

### 1. Basic Confirmation

```python
from core.input import EnhancedPrompt

prompt = EnhancedPrompt()

result = prompt.ask_confirmation(
    question="Proceed with installation",
    default=True,
    help_text="This will install packages and configure settings",
    context="5 packages will be installed, 120MB download"
)
```

**Output:**
```
  ╭─ 5 packages will be installed, 120MB download
  ╰─ This will install packages and configure settings
Proceed with installation? [YES] _
```

**User inputs:** `1` or `y` or `yes` or `ok` or `Enter` → `True`  
**User inputs:** `0` or `n` or `no` or `x` or `cancel` → `False`

---

### 2. Menu Selection

```python
options = ["Development", "Production", "Testing"]

choice = prompt.ask_menu(
    title="Select environment",
    options=options,
    help_text="Choose your deployment target",
    allow_cancel=True
)
```

**Output:**
```
Select environment
  1. Development
  2. Production
  3. Testing

  ╭─ Valid choices: 1-3 or 0 to cancel
  ╰─ Choose your deployment target
Choose an option [1-3] _
```

---

### 3. Variable Collection

```python
api_key = prompt.ask_variable(
    var_name="OPENAI_API_KEY",
    current_value="sk-abc...xyz",
    var_type="api key",
    help_text="Get your key from https://platform.openai.com",
    required=True
)
```

**Output:**
```
  ╭─ Current: sk-abc...xyz
  ╰─ Get your key from https://platform.openai.com (required)
OPENAI_API_KEY > _
```

---

### 4. Story Form Field

```python
field = {
    "name": "timezone",
    "label": "Your timezone",
    "type": "select",
    "required": True,
    "options": ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
}

value = prompt.ask_story_field(field, previous_value="UTC")
```

**Output:**
```
Your timezone:
  1. UTC
  2. America/New_York
  3. Europe/London
  4. Asia/Tokyo

  ╭─ Valid choices: 1-4
  ╰─ Choose from the options above (current: UTC)
Choose an option [1-4] _
```

---

## Integration with uCODE TUI

### In uCODE Constructor

```python
class uCODETUI:
    def __init__(self):
        # Use EnhancedPrompt for better UX
        self.prompt = EnhancedPrompt()
```

### Updated Methods

```python
def _ask_yes_no(self, question: str, default: bool = True, 
                help_text: str = None, context: str = None) -> bool:
    """Ask with 2-line context display."""
    return self.prompt.ask_confirmation(
        question=question,
        default=default,
        help_text=help_text,
        context=context,
    )

def _ask_menu_choice(self, prompt: str, num_options: int, 
                     allow_cancel: bool = True, help_text: str = None) -> Optional[int]:
    """Menu selection with context."""
    # Context display handled automatically
    range_display = f"1-{num_options}" + (" or 0 to cancel" if allow_cancel else "")
    
    if self.prompt.show_context:
        print(f"\n  ╭─ Valid choices: {range_display}")
        if help_text:
            print(f"  ╰─ {help_text}")
        else:
            print(f"  ╰─ Enter number and press Enter")
    
    return self.prompt.ask_menu_choice(prompt, num_options, allow_zero=allow_cancel)

def _collect_field_response(self, field: Dict, previous_value: Optional[str] = None) -> Optional[str]:
    """Story field collection with full context."""
    return self.prompt.ask_story_field(field, previous_value)
```

---

## Standardized Confirmation Format

### The [1|0|Yes|No|OK|Cancel] Standard

All confirmation prompts now use this standardized format:

**Accepted inputs for TRUE:**
- `1` — Quick yes (numeric)
- `y` — Short yes
- `yes` — Full yes
- `ok` — Acknowledge/accept
- `Enter` — If default is True

**Accepted inputs for FALSE:**
- `0` — Quick no (numeric)
- `n` — Short no
- `no` — Full no
- `x` — Cancel/exit
- `cancel` — Explicit cancel
- `Enter` — If default is False

**Error handling:**
- Invalid input shows: `❌ Please enter: 1 (Yes), 0 (No), Yes, No, OK, or Cancel`
- Automatically re-prompts until valid input received

---

## Migration Guide

### From Old SmartPrompt

**Before:**
```python
result = self._ask_yes_no("Continue", default=True)
```

**After (basic):**
```python
result = self._ask_yes_no("Continue", default=True)  # Still works!
```

**After (enhanced):**
```python
result = self._ask_yes_no(
    question="Continue",
    default=True,
    help_text="This will proceed with the operation",
    context="3 files will be modified"
)
```

### From Old Menu Handler

**Before:**
```python
choice = self._ask_menu_choice("Choose", 5, allow_cancel=True)
```

**After:**
```python
choice = self._ask_menu_choice(
    prompt="Choose",
    num_options=5,
    allow_cancel=True,
    help_text="Select your preferred option"
)
```

---

## Configuration

### Toggle Context Display

```python
# Disable context lines
prompt.toggle_context_display(enabled=False)

# Re-enable
prompt.toggle_context_display(enabled=True)

# Toggle current state
prompt.toggle_context_display()
```

### Toggle Predictions

```python
# Disable prediction display
prompt.toggle_predictions(enabled=False)

# Re-enable
prompt.toggle_predictions(enabled=True)
```

---

## Testing

### Manual Testing

```python
# Test confirmation
python -c "
from core.input import EnhancedPrompt
prompt = EnhancedPrompt()
result = prompt.ask_confirmation(
    'Test question',
    help_text='Test help',
    context='Test context'
)
print(f'Result: {result}')
"

# Test menu
python -c "
from core.input import EnhancedPrompt
prompt = EnhancedPrompt()
choice = prompt.ask_menu('Test Menu', ['Option 1', 'Option 2', 'Option 3'])
print(f'Choice: {choice}')
"

# Test variable
python -c "
from core.input import EnhancedPrompt
prompt = EnhancedPrompt()
value = prompt.ask_variable('TEST_VAR', current_value='old_value', var_type='string')
print(f'Value: {value}')
"
```

---

## API Reference

### EnhancedPrompt Class

```python
class EnhancedPrompt(SmartPrompt):
    """Enhanced prompt with 2-line context display."""
    
    def ask_with_context(
        prompt_text: str,
        current_value: Optional[str] = None,
        help_text: Optional[str] = None,
        predictions: Optional[List[str]] = None,
        default: str = ""
    ) -> str
    
    def ask_confirmation(
        question: str,
        default: bool = False,
        help_text: Optional[str] = None,
        context: Optional[str] = None
    ) -> bool
    
    def ask_menu(
        title: str,
        options: List[str],
        help_text: Optional[str] = None,
        allow_cancel: bool = True
    ) -> Optional[int]
    
    def ask_variable(
        var_name: str,
        current_value: Optional[str] = None,
        var_type: str = "text",
        help_text: Optional[str] = None,
        required: bool = False
    ) -> Optional[str]
    
    def ask_story_field(
        field: Dict[str, Any],
        previous_value: Optional[str] = None
    ) -> Optional[str]
    
    def toggle_context_display(enabled: bool = None) -> bool
    
    def toggle_predictions(enabled: bool = None) -> bool
```

---

## Benefits

1. **Improved UX** — Users see context before typing
2. **Reduced Errors** — Clear help text prevents invalid input
3. **Faster Input** — `1` and `0` for quick yes/no
4. **Consistent** — All prompts follow same pattern
5. **Predictive** — Shows suggestions when available
6. **Accessible** — Works in both rich and fallback modes

---

## Known Limitations

1. **Terminal Width** — Context lines may wrap on narrow terminals (<80 cols)
2. **Fallback Mode** — Context display still works but without colors/styling
3. **History** — Predictions based on command history (currently limited)

---

## Future Enhancements

- [ ] Color-coded context lines (green=current, blue=predicted, yellow=help)
- [ ] Smart prediction from command history and aliases
- [ ] Multi-line context for complex operations
- [ ] Inline editing of current values
- [ ] Tab completion integration with predictions

---

## See Also

- [STANDARD-INPUT-HANDLERS.md](STANDARD-INPUT-HANDLERS.md) — Original input system
- [specs/uCODE-v1.3.md](../specs/uCODE-v1.3.md) — Unified Terminal TUI
- [QUICKSTART.md](../QUICKSTART.md) — Getting started guide

---

**Status:** Live Documentation  
**Component:** core/input/enhanced_prompt.py  
**Last Updated:** 2026-01-30  
**Version:** v1.0.0
