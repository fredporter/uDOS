# TUI Form System - Field Types & Extension Guide

## Supported Field Types

### Complete Reference Table

| Type | Widget | Input Method | Output Format | Validation |
|------|--------|--------------|---------------|------------|
| `text` | TextInput | Type text | Raw string | Max length (optional) |
| `number` | SmartNumberPicker | ↑/↓ or typing | Integer | Min/max bounds |
| `date` | DatePicker | ↑/↓ or typing YMD | YYYY-MM-DD | Date validation |
| `time` | TimePicker | ↑/↓ or typing HMS | HH:MM:SS | Time validation |
| `select` | BarSelector | ↑/↓ arrows | Selected option | Must be in options |
| `checkbox` | Simple | Space or Y/N | true/false | Binary |
| `textarea` | MultilineInput | Type text (Enter for new line) | String | Max length (optional) |

---

## Field Specification in Story Files

### Text Field
```yaml
name: username
label: Your Username
type: text
required: true
placeholder: "Enter username"
default: "Ghost"
```

### Number Field
```yaml
name: age
label: Age
type: number
min_value: 0
max_value: 150
default: 25
```

### Date Field
```yaml
name: birth_date
label: Date of Birth
type: date
default: "1980-01-01"
required: true
```

### Time Field
```yaml
name: meeting_time
label: Meeting Time
type: time
default: "14:30:00"
```

### Select/Bar Field
```yaml
name: role
label: Select Role
type: select
required: true
options:
  - admin
  - user
  - guest
default: "user"
```

### Checkbox Field
```yaml
name: agree_terms
label: I agree to terms
type: checkbox
default: false
```

### Textarea Field
```yaml
name: bio
label: Biography
type: textarea
placeholder: "Tell us about yourself"
default: ""
```

---

## Keyboard Behavior by Type

### Text Input
```
[Input field]
↑/↓     → Navigate input history (if implemented)
Ctrl+A  → Select all
Ctrl+U  → Clear line
```

### Smart Number
```
[0000]
↑       → +1
↓       → -1
0-9     → Add digit
Bksp    → Delete digit
```

### Date Picker
```
Year  [1985]
Month [11]
Day   [07]

Tab     → Next component
↑/↓     → Adjust current
```

### Time Picker
```
Hour   [14]
Minute [30]
Second [00]

Tab     → Next component
↑/↓     → Adjust current
```

### Bar Selector
```
  ❯ Option 1
    Option 2
    Option 3

↑/↓     → Move selection
Enter   → Confirm
```

---

## Field Configuration Options

### Universal Options (All Fields)
```yaml
name: field_id              # Required: Unique identifier
label: "Display Label"      # Required: User-facing label
type: text|date|select|...  # Required: Field type
required: true              # Default: false
placeholder: "Hint text"    # Text/number fields
default: value              # Pre-fill value
```

### Number-Specific Options
```yaml
type: number
min_value: 0                # Minimum allowed value
max_value: 100              # Maximum allowed value
default: 50                 # Initial value
```

### Select-Specific Options
```yaml
type: select
options:                    # Required for select
  - option1
  - option2
  - option3
default: "option1"          # Must match one option
```

### Text-Specific Options
```yaml
type: text
placeholder: "Enter text"
default: ""
max_length: 255             # Optional length limit
pattern: "^[a-z]+$"         # Optional regex (future)
```

---

## Adding New Field Types

To add a new field type:

### 1. Create Widget Class (in `form_fields.py`)

```python
class CustomPicker:
    """Custom field widget."""
    
    def __init__(self, label: str, **config):
        self.label = label
        self.config = config
        self.value = config.get('default')
    
    def render(self, focused: bool = False) -> str:
        """Render widget. Return string display."""
        if focused:
            return f"❯ {self.label}: [__input__]"
        else:
            return f"  {self.label}: {self.value}"
    
    def handle_input(self, key: str) -> Optional[str]:
        """Handle keyboard input.
        
        Return:
            None if still editing
            Final value (str) if complete
        """
        if key == '\n':
            return self.value
        elif key == 'up':
            # Custom behavior
            pass
        return None
    
    def get_value(self) -> str:
        """Return finalized value."""
        return str(self.value)
```

### 2. Register in TUIFormRenderer

Update `_create_widget()` method:

```python
def _create_widget(self, field: Dict) -> Any:
    # ... existing code ...
    elif ftype == FieldType.CUSTOM:
        return CustomPicker(label, **config)
    # ... rest of code ...
```

### 3. Add FieldType Enum

```python
class FieldType(Enum):
    # ... existing ...
    CUSTOM = "custom"
```

### 4. Add Type Mapping in StoryFormHandler

```python
type_map = {
    # ... existing ...
    'custom': FieldType.CUSTOM,
}
```

### 5. Use in Story File

```markdown
```story
name: my_field
label: My Custom Field
type: custom
```
```

---

## Validation Strategies

### At Entry Time (Recommended)
```python
class SmartNumberPicker:
    def handle_input(self, char: str) -> bool:
        # Validate immediately
        if not char.isdigit():
            return False  # Reject non-digits
        return True
```

### At Submission Time
```python
def _finalize(self) -> None:
    """Validate before returning value."""
    if self.value < self.min_val or self.value > self.max_val:
        raise ValueError(f"Value {self.value} out of bounds")
```

### Custom Validators
```python
renderer.add_field(
    "email",
    "Email Address",
    FieldType.TEXT,
    validation=lambda x: "@" in x  # Basic validation
)
```

---

## Advanced Features

### Conditional Fields (Future)
```yaml
name: role
type: select
options: [admin, user, guest]
---
name: admin_code
type: text
show_if:
  field: role
  value: admin
```

### Dependent Dropdowns (Future)
```yaml
name: country
type: select
options: [US, UK, Canada]
---
name: state
type: select
options_endpoint: /api/states/{country}
depends_on: country
```

### Async Validation (Future)
```yaml
name: username
type: text
validate_url: /api/check-available
```

---

## Error Handling

### Field-Level Errors
```python
try:
    value = picker.handle_input(key)
except ValueError as e:
    print(f"❌ Invalid: {e}")
    # Re-render picker
```

### Form-Level Errors
```python
if result["status"] == "error":
    print(f"Form failed: {result['message']}")
elif result["status"] == "cancelled":
    print("Form cancelled by user")
else:
    data = result["data"]
```

---

## Performance Considerations

### Large Option Lists
For selectors with many options:
- Use pagination (show 5-10 at a time)
- Add search/filter capability
- Group related options

### Long Forms
- Split into multiple story sections
- Show progress indicator
- Remember previous answers
- Allow going back to edit

---

## Terminal Compatibility

### Tested Environments
- ✅ macOS Terminal
- ✅ Linux (bash, zsh)
- ✅ Alpine Linux
- ✅ SSH sessions
- ✅ VS Code integrated terminal

### Known Limitations
- Windows Command Prompt: Fallback mode only
- Some emulators: May not support raw mode
- Screen readers: May need alternative mode

---

## Examples

### Complete Story File

```markdown
---
title: User Registration
type: story
description: Create your account
---

## Personal Information

```story
name: first_name
label: First Name
type: text
required: true
```

```story
name: last_name
label: Last Name
type: text
required: true
```

```story
name: birth_date
label: Date of Birth
type: date
required: true
default: "1990-01-01"
```

## Preferences

```story
name: timezone
label: Timezone
type: select
default: "UTC"
options:
  - UTC
  - America/New_York
  - Europe/London
  - Asia/Tokyo
```

```story
name: notifications
label: Enable notifications
type: checkbox
default: true
```
```

### Processing Story
```bash
STORY user-registration

# Results in .env or form_data:
# first_name=John
# last_name=Doe
# birth_date=1990-01-01
# timezone=America/New_York
# notifications=true
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Keys not captured | Terminal not in raw mode |
| Escape sequences wrong | Different terminal emulator |
| Slow rendering | Clear screen less frequently |
| Arrow keys don't work | Check termios support |
| Form jumps around | Track cursor position |

---

## Best Practices

✅ **DO**
- Use meaningful field names
- Provide sensible defaults
- Test in multiple terminals
- Keep forms under 10 fields
- Validate early (at entry time)
- Use consistent labeling

❌ **DON'T**
- Require field values that have defaults
- Create forms with 20+ fields
- Use ambiguous field names
- Assume specific terminal features
- Forget fallback mode
- Leave validation until submission

---

## Resources

- Implementation: `core/tui/form_fields.py`
- Integration: `core/tui/story_form_handler.py`
- Examples: `memory/story/tui-setup-story.md`
- Documentation: `docs/TUI_FORM_SYSTEM.md`
