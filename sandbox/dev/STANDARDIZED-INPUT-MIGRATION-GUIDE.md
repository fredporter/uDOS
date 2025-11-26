# StandardizedInput - Quick Migration Guide
## How to migrate your component to v1.0.31 StandardizedInput

**Last Updated**: November 22, 2025

---

## 🎯 Quick Start

### 1. Import StandardizedInput

```python
from core.services.standardized_input import StandardizedInput
```

### 2. Initialize in your class

```python
class MyComponent:
    def __init__(self):
        self.si = StandardizedInput()
```

### 3. Replace input() calls

See migration patterns below.

---

## 🔄 Migration Patterns

### Basic Text Input

**Before**:
```python
name = input("Enter your name: ").strip()
```

**After**:
```python
name = self.si.input_text("Enter your name")
```

---

### Confirmation Dialog

**Before**:
```python
confirm = input("Are you sure? (y/n): ").strip().lower()
if confirm in ['y', 'yes']:
    do_something()
```

**After**:
```python
if self.si.confirm("Are you sure?", default=False):
    do_something()
```

---

### Text Input with Default

**Before**:
```python
value = input(f"Enter value [{default}]: ").strip()
if not value:
    value = default
```

**After**:
```python
value = self.si.input_text("Enter value", default=default)
```

---

### Text Input with Validation

**Before**:
```python
while True:
    num = input("Enter a number: ").strip()
    if num.isdigit():
        break
    print("Invalid number!")
```

**After**:
```python
num = self.si.input_text(
    "Enter a number",
    validate=lambda x: x.isdigit(),
    required=True
)
```

---

### Menu Selection (Simple)

**Before**:
```python
print("1. Option A")
print("2. Option B")
print("3. Option C")
choice = input("> ").strip()

if choice == '1':
    do_a()
elif choice == '2':
    do_b()
elif choice == '3':
    do_c()
```

**After**:
```python
options = ["Option A", "Option B", "Option C"]
idx, selected = self.si.select_option("Choose an option", options)

if idx == 0:
    do_a()
elif idx == 1:
    do_b()
elif idx == 2:
    do_c()
```

---

### Menu Selection (with Descriptions)

**Before**:
```python
print("Commands:")
print("  e - Edit")
print("  s - Save")
print("  q - Quit")
cmd = input("> ").strip().lower()
```

**After**:
```python
commands = ["Edit", "Save", "Quit"]
descriptions = ["Edit current file", "Save changes", "Exit editor"]
idx, cmd = self.si.select_option(
    "Editor Command",
    commands,
    descriptions=descriptions
)
```

---

### File Selection

**Before**:
```python
files = os.listdir('.')
for i, f in enumerate(files, 1):
    print(f"{i}. {f}")
choice = input("Select file: ").strip()
selected_file = files[int(choice) - 1]
```

**After**:
```python
selected_file = self.si.select_file(
    title="Select a file",
    start_path=".",
    file_types=['.md', '.txt'],
    allow_directories=False
)
```

---

### Multi-Select

**Before**:
```python
print("Select files (space-separated numbers):")
for i, f in enumerate(files, 1):
    print(f"{i}. {f}")
choices = input("> ").strip().split()
selected = [files[int(c)-1] for c in choices]
```

**After**:
```python
selected_indices = self.si.select_multiple(
    "Select files",
    file_names,
    min_select=1,
    max_select=5
)
selected = [files[i] for i in selected_indices]
```

---

### Progress Indication

**Before**:
```python
for i in range(total):
    # do work
    percent = (i + 1) / total * 100
    print(f"Progress: {percent:.0f}%")
```

**After**:
```python
for i in range(total):
    # do work
    progress = self.si.show_progress(i + 1, total, "Processing")
    print(f"\r{progress}", end="", flush=True)
```

---

### Status Messages

**Before**:
```python
print("✓ Success!")
print("❌ Error occurred")
print("⚠️ Warning")
print("ℹ️ Information")
```

**After**:
```python
self.si.show_status("Success!", "success")
self.si.show_status("Error occurred", "error")
self.si.show_status("Warning", "warning")
self.si.show_status("Information", "info")
```

---

### "Press ENTER to continue"

**Before**:
```python
input("Press ENTER to continue...")
```

**After**:
```python
self.si.input_text("Press ENTER to continue", default="")
```

---

## 🎨 Advanced Usage

### Custom Icons

```python
options = ["Home", "Work", "School"]
icons = ["🏠", "💼", "🎓"]
idx, choice = self.si.select_option(
    "Select location",
    options,
    icons=icons
)
```

---

### Suggestions

```python
common_names = ["Alice", "Bob", "Charlie"]
name = self.si.input_text(
    "Enter name",
    suggestions=common_names
)
```

---

### Required Fields

```python
email = self.si.input_text(
    "Email address",
    required=True,
    validate=lambda x: '@' in x and '.' in x
)
```

---

## ✅ Migration Checklist

When migrating a component:

- [ ] Add `from core.services.standardized_input import StandardizedInput`
- [ ] Add `self.si = StandardizedInput()` to `__init__()`
- [ ] Replace all `input()` calls with appropriate `si.*()` methods
- [ ] Replace manual menu printing with `select_option()`
- [ ] Replace y/n prompts with `confirm()`
- [ ] Add validation to text inputs where appropriate
- [ ] Test interactively in terminal
- [ ] Update docstrings to mention StandardizedInput usage
- [ ] Update component version to v1.0.31

---

## 🧪 Testing Your Migration

### Manual Test
```bash
# In uDOS terminal
python3 -m core.ui.micro_editor test.txt
```

### Unit Test Template
```python
import unittest
from core.services.standardized_input import StandardizedInput

class TestMyComponent(unittest.TestCase):
    def setUp(self):
        self.si = StandardizedInput(use_advanced=False)  # Force basic mode

    def test_menu_selection(self):
        # Test with simulated input
        # ...
```

---

## 💡 Tips

1. **Start Simple**: Migrate basic input() first, then complex menus
2. **Test Incrementally**: Test after each migration, not all at once
3. **Use Validation**: Add validation functions to prevent errors
4. **Provide Defaults**: Users appreciate sensible defaults
5. **Visual Feedback**: Use show_status() to confirm actions
6. **Graceful Cancel**: Always handle idx == -1 (user cancelled)

---

## 🚫 Common Mistakes

### ❌ Don't do this:
```python
# Forgetting to handle cancellation
idx, choice = self.si.select_option("Menu", options)
do_something(choice)  # Error if user cancelled!
```

### ✅ Do this:
```python
idx, choice = self.si.select_option("Menu", options)
if idx != -1:
    do_something(choice)
```

---

### ❌ Don't do this:
```python
# Mixing old and new styles
name = input("Name: ")  # Old
age = self.si.input_text("Age")  # New
```

### ✅ Do this:
```python
# Consistent style
name = self.si.input_text("Name")
age = self.si.input_text("Age", validate=lambda x: x.isdigit())
```

---

## 📚 Reference

### Full API Documentation
See: `core/services/standardized_input.py`

### Examples
- `core/ui/micro_editor.py` - Complete migration example
- `core/services/knowledge_file_picker.py` - File picker example

### Support
- Plan: `dev/planning/v1.0.31-STANDARDIZED-INPUT-PLAN.md`
- Summary: `dev/notes/v1.0.31-implementation-summary.md`

---

*Happy migrating! 🚀*
