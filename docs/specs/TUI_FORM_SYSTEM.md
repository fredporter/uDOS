# TUI Form System - Modern Interactive Form Fields

## Overview

The TUI Form System provides a modern, feature-rich framework for collecting data in interactive terminal applications. It includes:

- **SmartNumberPicker**: Intelligent number input with keyboard/typing support
- **DatePicker**: Interactive date selector with YY/MM/DD fields
- **TimePicker**: Interactive time selector with HH/MM/SS fields
- **BarSelector**: Multi-option visual selector
- **TUIFormRenderer**: Complete form management system

## Components

### SmartNumberPicker

Smart number input that understands context and allows both typing and arrow keys.

**Features:**
- Intelligent year parsing: typing "75" → 1975, "25" → 2025
- Arrow key increment/decrement
- Auto-finalization on Tab/Enter
- Visual display with cursor feedback
- Range validation (min/max)

**Example:**
```python
picker = SmartNumberPicker("Year", min_val=1900, max_val=2100, default=2000)
```

### DatePicker

Interactive date picker with separate Year, Month, Day fields.

**Features:**
- Smart year parsing (see SmartNumberPicker)
- Tab navigation between fields
- Visual block layout
- YYYY-MM-DD output format

**Example:**
```python
date_picker = DatePicker("Date of birth", default="1980-01-01")
```

### TimePicker

Interactive time picker with separate Hour, Minute, Second fields.

**Features:**
- Smart number input for each component
- 24-hour time format
- Tab navigation between fields
- HH:MM:SS output format

**Example:**
```python
time_picker = TimePicker("Setup time", default="10:57:32")
```

### BarSelector

Visual bar selector for multiple choice options.

**Features:**
- Arrow key navigation (↑/↓)
- Visual highlighting of selected option
- Supports any number of options
- Clean, scannable interface

**Example:**
```python
selector = BarSelector("Role", ["ghost", "user", "admin"], default_index=0)
```

## Form Field Types

Supported field types in story files:

| Type | Widget | Features |
|------|--------|----------|
| `text` | TextInput | Simple text entry |
| `number` | SmartNumberPicker | Intelligent number input |
| `date` | DatePicker | Interactive date selector |
| `time` | TimePicker | Interactive time selector |
| `select` | BarSelector | Multi-option selector |
| `checkbox` | Simple checkbox | Binary choice |
| `textarea` | TextArea | Multi-line text |

## Story File Specification

Define forms in story markdown files using the `story` code blocks:

```markdown
---
title: My Form
type: story
---

## Section Name

```story
name: field_name
label: Display Label
type: select
required: true
options:
  - option1
  - option2
  - option3
default: option1
```

```story
name: birth_date
label: Date of birth
type: date
required: true
default: "1980-01-01"
```

```story
name: username
label: Username
type: text
required: true
placeholder: "Enter your username"
default: "Ghost"
```
```

## Keyboard Shortcuts

### Global
- `Escape`: Cancel form
- `Tab`: Move to next field
- `Enter`: Submit form/field value

### Number/Date/Time Pickers
- `↑`: Increment value
- `↓`: Decrement value
- `0-9`: Type digits (smart parsing)
- `Backspace`: Delete digit from input buffer

### Bar Selector
- `↑`: Previous option
- `↓`: Next option
- `Enter`: Confirm selection

## Implementation in TUI

### Using the Form Handler

```python
from core.tui.story_form_handler import get_form_handler

# Get appropriate handler (interactive or fallback)
handler = get_form_handler()

# Process form specification
result = handler.process_story_form({
    "title": "User Setup",
    "description": "Configure your identity",
    "fields": [
        {
            "name": "username",
            "label": "Username",
            "type": "text",
            "default": "Ghost",
        },
        {
            "name": "role",
            "label": "Role",
            "type": "select",
            "options": ["ghost", "user", "admin"],
            "default": "ghost",
        },
    ]
})

# Use collected data
if result["status"] == "success":
    data = result["data"]
    print(f"Username: {data['username']}")
    print(f"Role: {data['role']}")
```

### Creating Story Forms

Story forms are automatically detected and processed by the TUI when:
1. A story file contains `story` code blocks with field definitions
2. Fields have required properties: `name`, `label`, `type`
3. The story handler executes and processes interactive input

**Example Workflow:**
```
STORY tui-setup
  ↓
Story handler parses fields
  ↓
Form renderer creates widgets
  ↓
Interactive form displayed
  ↓
User provides input with keyboard
  ↓
Data collected and returned
  ↓
Setup handler saves to .env
```

## Degradation Strategy

The form system includes a **fallback mode** for environments where interactive TUI is unavailable:

- Interactive fields → Simple `input()` prompts
- Smart pickers → Accept any input
- Bar selectors → Numbered menu (1-based)

This ensures forms remain usable in all environments.

## Design Principles

1. **Smart Input**: Understand user intent (e.g., "75" → "1975")
2. **Keyboard First**: All input via keyboard, no mouse required
3. **Visual Feedback**: Clear indication of current field, focus state
4. **Robust**: Handles unexpected input gracefully
5. **Degradable**: Falls back to simple input if necessary
6. **Cross-Compatible**: Works in any terminal

## File Structure

```
core/tui/
  form_fields.py           - Core form components
  story_form_handler.py    - Interactive form integration
  
core/commands/
  story_handler.py         - Story execution with form support
  setup_handler.py         - Uses forms for configuration
```

## Testing Components

Test individual components:

```bash
# Test form fields
python -m core.tui.form_fields

# Test with setup story
SETUP

# Test with custom story
STORY tui-setup
```

## Future Enhancements

- [ ] Mouse support for terminal emulators
- [ ] Async form validation
- [ ] Custom validators in story files
- [ ] Multi-step form navigation
- [ ] Form submission hooks
- [ ] Template-based form generation
