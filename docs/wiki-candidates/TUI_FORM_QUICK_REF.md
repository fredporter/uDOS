# TUI Form System - Quick Reference

## Form Field Types

### Text Input
```yaml
type: text
placeholder: "Enter text"
default: "Value"
required: true
```

### Smart Number Picker
```yaml
type: number
min_value: 0
max_value: 9999
default: 1985
```

### Date Picker
```yaml
type: date
default: "1980-01-01"
```
**Input:** Type digits or use ↑/↓ arrows
- Year: "75" → 1975, "25" → 2025
- Month: 1-12
- Day: 1-31

### Time Picker
```yaml
type: time
default: "10:57:32"
```
**Input:** Type HH/MM/SS or use ↑/↓

### Bar Selector
```yaml
type: select
options:
  - choice1
  - choice2
  - choice3
default: choice1
```
**Navigation:** ↑/↓ arrows to select

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| `↑` / `↓` | Increment/decrement value (numbers, selectors) |
| `0-9` | Type digits (smart parsing for years) |
| `Backspace` | Delete last digit |
| `Tab` / `Enter` | Move to next field / Submit |
| `Esc` | Cancel form |

---

## Smart Number Parsing

### Year Field
- Type `75` → 1975 (before 1930)
- Type `25` → 2025 (after 1930)
- Type `1985` → 1985 (4 digits)

### Month/Day/Hour/Minute/Second
- Type `1` → 01
- Type `31` → 31
- Type `05` → 05 (leading zero)

---

## Story File Example

```markdown
---
title: Setup Form
type: story
---

## User Identity

```story
name: username
label: Username
type: text
required: true
default: "Ghost"
```

```story
name: dob
label: Date of birth
type: date
default: "1980-01-01"
```

```story
name: role
label: Role
type: select
required: true
options:
  - ghost
  - user
  - admin
default: "ghost"
```
```

---

## Field Validation

- `required: true` - Field must have a value
- `default: value` - Pre-fills field
- `placeholder: text` - Hint text for text fields
- `min_value` / `max_value` - Range for numbers

---

## Running Forms in TUI

```bash
# Run setup with interactive form
SETUP

# Run custom story
STORY story-name

# View your profile
SETUP --profile
```

---

## Form Data Location

- **Submitted form data** → `.env` file (for SETUP)
- **Form fields** → Story markdown file
- **Field specifications** → `story` code blocks in markdown

---

## Degradation

If interactive mode unavailable:
- **Number picker** → Simple text prompt
- **Date picker** → Text input "YYYY-MM-DD"
- **Bar selector** → Numbered menu (1, 2, 3, ...)

All forms remain functional in degraded mode.
