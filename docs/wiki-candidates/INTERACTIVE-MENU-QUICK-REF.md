# Interactive Menu Quick Reference

**One-page guide to using interactive menus in uDOS handlers.**

---

## Basic Usage

### Step 1: Add Mixin to Handler

```python
from core.commands.base import BaseCommandHandler
from core.commands.interactive_menu_mixin import InteractiveMenuMixin

class MyHandler(BaseCommandHandler, InteractiveMenuMixin):
    def handle(self, command, params, grid, parser):
        # Your handler code here
        pass
```

### Step 2: Show Menu

```python
choice = self.show_menu(
    "What do you want?",
    [
        ("Option 1", "opt1"),
        ("Option 2", "opt2"),
    ]
)

if choice == "opt1":
    # Do something
    pass
```

---

## Common Patterns

### Menu with Help Text

```python
choice = self.show_menu(
    "Database Operations",
    [
        ("Backup", "backup", "Create a backup copy"),
        ("Restore", "restore", "Restore from backup"),
        ("Delete", "delete", "Permanently delete data"),
    ]
)
```

### Yes/No Confirmation

```python
if self.show_confirm("Delete everything?", "Cannot be undone"):
    # User said yes
    return self._delete_all()
else:
    # User said no or cancelled
    return {"status": "cancelled"}
```

### MenuBuilder (Fluent API)

```python
menu = (MenuBuilder("Admin Tools")
    .add_item("Restart", "restart", "Restart system")
    .add_item("Backup", "backup", "Create backup")
    .add_item("Update", "update", "Check for updates")
    .with_cancel(True)
    .build()
)

choice = self.show_builder_menu(menu)
```

### Menu with Actions

```python
def restart_system():
    print("Restarting...")
    # Do restart

def backup_data():
    print("Backing up...")
    # Do backup

self.show_menu_with_actions(
    "System Actions",
    [
        ("Restart", restart_system, "Restart the system"),
        ("Backup", backup_data, "Backup user data"),
    ]
)
```

---

## Return Values

### `show_menu()`
Returns the selected option's **value**:

```python
choice = self.show_menu("Pick", [("A", "a"), ("B", "b")])
# Returns: "a" or "b" or None if cancelled
```

### `show_confirm()`
Returns **boolean**:

```python
confirmed = self.show_confirm("Sure?")
# Returns: True or False
```

### `show_menu_with_actions()`
Returns the selected option's **label**:

```python
label = self.show_menu_with_actions("Pick", [...])
# Returns: "Restart" or "Backup" or None if cancelled
```

---

## Menu Item Options Format

### (label, value) tuple
```python
[
    ("Start Server", "start"),
    ("Stop Server", "stop"),
]
```

### (label, value, help_text) tuple
```python
[
    ("Start Server", "start", "Launch the wizard"),
    ("Stop Server", "stop", "Graceful shutdown"),
]
```

---

## Real-World Examples

### Example 1: Server Control

```python
class ServerHandler(BaseCommandHandler, InteractiveMenuMixin):
    def handle(self, command, params, grid, parser):
        choice = self.show_menu(
            "Server Control",
            [
                ("Start", "start", "Launch the server"),
                ("Stop", "stop", "Shutdown gracefully"),
                ("Restart", "restart", "Restart the server"),
                ("Status", "status", "Check server status"),
            ]
        )

        if choice == "start":
            return self._start()
        elif choice == "stop":
            return self._stop()
        elif choice == "restart":
            return self._restart()
        elif choice == "status":
            return self._status()
        else:
            return {"status": "cancelled"}
```

### Example 2: File Operations

```python
class FileHandler(BaseCommandHandler, InteractiveMenuMixin):
    def handle(self, command, params, grid, parser):
        if not params:
            # Show menu of operations
            op = self.show_menu(
                "File Operations",
                [
                    ("Create", "create", "Create new file"),
                    ("Edit", "edit", "Edit existing file"),
                    ("Delete", "delete", "Delete file"),
                    ("List", "list", "List all files"),
                ]
            )

            if op == "create":
                return self._create_file()
            elif op == "edit":
                filename = input("Filename: ")
                return self._edit_file(filename)
            # ... etc
        else:
            # Explicit operation provided
            return self._handle_explicit_op(params)
```

### Example 3: Setup Wizard

```python
class SetupHandler(BaseCommandHandler, InteractiveMenuMixin):
    def handle(self, command, params, grid, parser):
        if params and params[0] == "--wizard":
            return self._run_wizard_mode()

        # Interactive setup with menu
        choice = self.show_menu(
            "Setup Options",
            [
                ("Quick Setup", "quick", "Use defaults"),
                ("Custom Setup", "custom", "Configure everything"),
                ("View Profile", "profile", "Show current settings"),
            ]
        )

        if choice == "quick":
            return self._quick_setup()
        elif choice == "custom":
            return self._custom_setup()
        elif choice == "profile":
            return self._show_profile()
        else:
            return {"status": "cancelled"}
```

---

## Advanced: MenuBuilder

```python
from core.ui.interactive_menu import MenuBuilder

menu = (MenuBuilder("Advanced Options")
    # Add items
    .add_item("Optimize", "opt", "Optimize performance")
    .add_item("Clean", "clean", "Clean up files")

    # Customize style
    .with_style(MenuStyle.HYBRID)  # NUMBERED, ARROW, or HYBRID

    # Allow/disallow cancel
    .with_cancel(True)  # Default: True

    # Show/hide help text
    .with_help(True)  # Default: True

    # Build the menu
    .build()
)

choice = self.show_builder_menu(menu)
```

---

## Nested Menus (Submenus)

```python
# Create submenu
backup_menu = InteractiveMenu(
    "Backup Options",
    [
        MenuItem("Full Backup", "full", "All data"),
        MenuItem("Incremental", "incremental", "Changes only"),
    ]
)

# Create main menu with submenu
main_menu = InteractiveMenu(
    "Main",
    [
        MenuItem("Backup", submenu=backup_menu),
        MenuItem("Restore", "restore"),
    ]
)

result = main_menu.show()
```

---

## Error Handling

Menus don't raise errors. They return `None` if cancelled:

```python
choice = self.show_menu("Pick", [...])

if choice is None:
    # User cancelled
    return {"status": "cancelled", "message": "User cancelled operation"}
else:
    # User selected something
    return self._handle_choice(choice)
```

---

## Tips & Best Practices

✅ **DO:**
- Use short, clear labels ("Start Server" not "Initiate server process")
- Provide help text for non-obvious options
- Use `show_confirm()` for dangerous operations
- Return `{"status": "cancelled"}` when user exits menu

❌ **DON'T:**
- Use menus for simple yes/no (use `show_confirm()` instead)
- Create menus with >9 items (hard to remember numbers)
- Use non-descriptive values ("x", "y") instead of meaningful ones
- Assume user will read help text (make labels self-explanatory)

---

## Terminal Support

Works in:
- ✅ macOS Terminal
- ✅ Linux terminals
- ✅ Windows (via WSL or Git Bash)
- ✅ iTerm2
- ✅ VS Code Terminal

**Arrow keys:** Works if terminal supports ANSI sequences
**Fallback:** Always supports numeric (1-9) + Enter

---

## Testing

```python
# In your test file
from core.ui.interactive_menu import InteractiveMenu, MenuItem

def test_menu_creation():
    menu = InteractiveMenu(
        "Test",
        [MenuItem("Option", "opt")]
    )
    assert menu.title == "Test"
    assert len(menu.items) == 1
```

---

## Common Issues

**Q: Arrows don't work?**
A: They work if terminal supports ANSI. Use numeric input (1-9) as fallback.

**Q: How do I disable an option?**
A: Set `enabled=False` on the MenuItem:
```python
MenuItem("Disabled", "dis", enabled=False)
```

**Q: How do I run code when option is selected?**
A: Use `show_menu_with_actions()` instead of `show_menu()`.

**Q: How do I add more than 9 options?**
A: Create submenus or use nested menus.

---

## Full API Reference

### `show_menu(title, options, allow_cancel=True)`
- **title** (str): Menu title
- **options** (list of tuples): `[(label, value), ...]` or `[(label, value, help), ...]`
- **allow_cancel** (bool): Show cancel option
- **Returns:** `value` or `None` if cancelled

### `show_confirm(title, help_text="")`
- **title** (str): Question text
- **help_text** (str): Optional help
- **Returns:** `True` if confirmed, `False` otherwise

### `show_menu_with_actions(title, items, allow_cancel=True)`
- **title** (str): Menu title
- **items** (list): `[(label, callable, help_text), ...]`
- **allow_cancel** (bool): Show cancel option
- **Returns:** `label` or `None` if cancelled

### `show_builder_menu(builder)`
- **builder** (MenuBuilder): Built menu
- **Returns:** selected `value` or `None`

---

**For more information, see:**
- [Full Documentation](./docs/INTERACTIVE-MENUS-IMPLEMENTATION.md)
- [Source Code](./core/ui/interactive_menu.py)
- [Tests](./test_interactive_menus.py)
