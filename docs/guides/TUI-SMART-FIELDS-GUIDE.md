# TUI Smart Fields - Setup and Usage Guide

**Status:** ✅ Production Ready (v1.3.12+)
**Date:** 2026-02-09

---

## Overview

uDOS TUI includes a powerful **Smart Fields** system for interactive data collection in story files and forms. Smart fields provide intelligent input handling with arrow keys, type-ahead, and visual feedback.

---

## Smart Field Types

### 1. SmartNumberPicker

Intelligent number input with context-aware parsing.

**Features:**
- Type digits directly (fast entry)
- Arrow keys ↑/↓ to increment/decrement
- Smart year parsing: "75" → 1975, "25" → 2025
- Range validation (min/max)
- Auto-completion on Tab/Enter

**Usage in Story Files:**

```markdown
\`\`\`story
name: birth_year
label: Year of birth
type: number
min_value: 1900
max_value: 2100
default: 1985
\`\`\`
```

**Keyboard:**
- `0-9` - Type digits
- `↑` - Increment value
- `↓` - Decrement value
- `Backspace` - Clear input buffer
- `Tab`/`Enter` - Confirm

---

### 2. DatePicker

Interactive date selector with separate Year/Month/Day fields.

**Features:**
- Tab between fields (Year → Month → Day)
- Arrow keys within each field
- Smart year parsing (see SmartNumberPicker)
- Validates day range based on month
- YYYY-MM-DD output format

**Usage in Story Files:**

```markdown
\`\`\`story
name: dob
label: Date of birth
type: date
required: true
default: "1980-01-01"
\`\`\`
```

**Keyboard:**
- `0-9` - Type digits in current field
- `↑/↓` - Adjust current field value
- `Tab`/`→` - Move to next field
- `←` - Move to previous field
- `Enter` - Confirm date

**Display:**
```
┌─────┬────┬────┐
│ 1980│ 12 │ 25 │
└─────┴────┴────┘
  YEAR  MON  DAY
```

---

### 3. TimePicker

Interactive time selector with HH:MM:SS fields.

**Features:**
- Tab between hours/minutes/seconds
- Arrow keys to adjust values
- 24-hour format (00-23)
- Auto-validation of ranges

**Usage in Story Files:**

```markdown
\`\`\`story
name: meeting_time
label: Meeting time
type: time
default: "14:30:00"
\`\`\`
```

**Keyboard:**
- Same as DatePicker
- Hour: 00-23
- Minute/Second: 00-59

**Display:**
```
┌────┬────┬────┐
│ 14 │ 30 │ 00 │
└────┴────┴────┘
  HH   MM   SS
```

---

### 4. BarSelector

Visual multi-option selector with highlighted selection.

**Features:**
- Arrow keys ↑/↓ to navigate options
- Visual highlight of current selection
- Keyboard shortcuts (type first letter)
- Enter to confirm

**Usage in Story Files:**

```markdown
\`\`\`story
name: user_role
label: Your role
type: select
required: true
options:
  - ghost
  - user
  - admin
default: ghost
\`\`\`
```

**Keyboard:**
- `↑` - Previous option
- `↓` - Next option
- Type first letter (e.g., `a` for "admin")
- `Enter` - Confirm selection

**Display:**
```
Your role:
  ▸ ghost      [selected]
    user
    admin
```

---

### 5. Text Input

Standard text input with placeholder support.

**Usage in Story Files:**

```markdown
\`\`\`story
name: username
label: Username
type: text
required: true
placeholder: "Enter your username"
default: "Ghost"
\`\`\`
```

---

### 6. TextArea

Multi-line text input.

**Usage in Story Files:**

```markdown
\`\`\`story
name: description
label: Description
type: textarea
placeholder: "Enter description..."
\`\`\`
```

---

## Setting Up Smart Fields in Story Files

### Basic Story File Structure

```markdown
---
title: User Setup Form
type: story
version: "1.0"
description: Configure your user profile
---

## Personal Information

\`\`\`story
name: username
label: Username
type: text
required: true
default: "Ghost"
\`\`\`

\`\`\`story
name: dob
label: Date of birth
type: date
default: "1980-01-01"
\`\`\`

\`\`\`story
name: role
label: Role
type: select
required: true
options:
  - ghost
  - user
  - admin
default: ghost
\`\`\`
```

### Field Properties

All field types support:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | ✅ | Field identifier (used in data) |
| `label` | string | ✅ | Display label shown to user |
| `type` | string | ✅ | Field type (text, number, date, time, select, etc.) |
| `required` | boolean | ❌ | Whether field must have a value |
| `default` | any | ❌ | Pre-filled default value |
| `placeholder` | string | ❌ | Hint text (for text fields) |

**Type-specific properties:**

| Type | Additional Properties |
|------|----------------------|
| `number` | `min_value`, `max_value` |
| `select` | `options` (array of strings) |

---

## Running Story Forms

### From TUI

```bash
# Run setup (uses tui-setup.md story)
SETUP

# Run custom story
STORY my-story

# Run with specific section
STORY my-story#section-id
```

### Testing a Story Form

1. Create story file in `memory/system/stories/`:

```bash
touch memory/system/stories/test-form.md
```

2. Add form fields (see examples above)

3. Run from TUI:

```bash
STORY test-form
```

---

## Keyboard Navigation Reference

### Global (all forms)

| Key | Action |
|-----|--------|
| `Escape` | Cancel form |
| `Tab` | Next field |
| `Enter` | Submit/confirm |

### Number/Date/Time Fields

| Key | Action |
|-----|--------|
| `0-9` | Type digits |
| `↑` | Increment |
| `↓` | Decrement |
| `Backspace` | Clear buffer |

### Bar Selector

| Key | Action |
|-----|--------|
| `↑` | Previous option |
| `↓` | Next option |
| Letter | Jump to option |
| `Enter` | Select |

---

## Examples

### Example 1: Simple Profile Form

**File:** `memory/system/stories/user-profile.md`

```markdown
---
title: User Profile
type: story
---

## Your Information

\`\`\`story
name: name
label: Full name
type: text
required: true
\`\`\`

\`\`\`story
name: birth_year
label: Birth year
type: number
min_value: 1900
max_value: 2100
\`\`\`

\`\`\`story
name: country
label: Country
type: select
options:
  - USA
  - Canada
  - UK
  - Other
\`\`\`
```

**Run:** `STORY user-profile`

---

### Example 2: Event Registration

**File:** `memory/system/stories/event-registration.md`

```markdown
---
title: Event Registration
type: story
---

## Registration Details

\`\`\`story
name: attendee_name
label: Name
type: text
required: true
\`\`\`

\`\`\`story
name: event_date
label: Event date
type: date
required: true
\`\`\`

\`\`\`story
name: arrival_time
label: Arrival time
type: time
default: "09:00:00"
\`\`\`

\`\`\`story
name: dietary
label: Dietary preference
type: select
options:
  - None
  - Vegetarian
  - Vegan
  - Gluten-free
\`\`\`
```

**Run:** `STORY event-registration`

---

## Troubleshooting

### Arrow Keys Don't Work

**Ubuntu/Debian users:**

```bash
# Install system dependencies
sudo apt-get install libreadline-dev libncurses5-dev

# Reinstall prompt_toolkit
pip install --upgrade --force-reinstall prompt_toolkit
```

See: [TUI-ARROW-KEYS-UBUNTU.md](../troubleshooting/TUI-ARROW-KEYS-UBUNTU.md)

### Form Falls Back to Simple Input

If interactive mode is unavailable, forms automatically degrade to simple text prompts:

```
Username: Ghost
Date of birth (YYYY-MM-DD): 1980-01-01
Role:
  1. ghost
  2. user
  3. admin
Choice (1-3): 1
```

All functionality remains available - just without visual widgets.

---

## Programmatic Usage

### From Python Code

```python
from core.tui.story_form_handler import get_form_handler

# Get handler (auto-detects interactive vs fallback)
handler = get_form_handler()

# Define form
form_spec = {
    "title": "User Setup",
    "description": "Configure your profile",
    "fields": [
        {
            "name": "username",
            "label": "Username",
            "type": "text",
            "required": True,
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
}

# Process form
result = handler.process_story_form(form_spec)

if result["status"] == "success":
    data = result["data"]
    print(f"Username: {data['username']}")
    print(f"Role: {data['role']}")
```

---

## Design Principles

1. **Smart Input** - Understand user intent (e.g., "75" → "1975")
2. **Keyboard First** - No mouse required
3. **Visual Feedback** - Clear indication of focus and selection
4. **Robust** - Handle unexpected input gracefully
5. **Degradable** - Falls back to simple input if needed
6. **Cross-Platform** - Works on all terminals

---

## Related Documentation

- [TUI_FORM_SYSTEM.md](../specs/TUI_FORM_SYSTEM.md) - Complete technical spec
- [TUI_FORM_QUICK_REF.md](../wiki-candidates/TUI_FORM_QUICK_REF.md) - Quick reference
- [story-format.md](../../app/public/knowledge/formats/story-format.md) - Story format guide
- [INTERACTIVE-MENUS-IMPLEMENTATION.md](../specs/INTERACTIVE-MENUS-IMPLEMENTATION.md) - Menu system

---

## File Locations

```
core/tui/
  form_fields.py              # Smart field widgets
  story_form_handler.py       # Interactive form handler

core/commands/
  story_handler.py            # STORY command handler
  setup_handler.py            # SETUP command (uses forms)

memory/system/stories/
  tui-setup.md                # SETUP form definition
  *.md                        # Custom story forms
```

---

**Last Updated:** 2026-02-09
**Applies To:** uDOS v1.3.12+
