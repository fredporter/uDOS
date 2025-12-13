# Migration Guide: Universal Input Device System

**Target Version:** v1.2.25  
**Audience:** Component developers integrating the new input system  
**Difficulty:** Intermediate

## Overview

This guide helps you migrate existing uDOS components to use the new Universal Input Device System. The system provides standardized APIs for keyboard, mouse, and selection handling.

## Quick Migration Checklist

- [ ] Replace custom navigation with `SelectorFramework`
- [ ] Add `KeypadHandler` for 0-9 navigation
- [ ] Add `MouseHandler` for click support
- [ ] Update display code to use `get_display_lines()`
- [ ] Add device capability checks
- [ ] Update tests for new behavior
- [ ] Remove deprecated selection logic

## Migration Patterns

### Pattern 1: List/Menu Components

#### Before (v1.2.24 and earlier):

```python
class FileListPanel:
    def __init__(self):
        self.files = []
        self.current_index = 0
        self.selected_files = []
    
    def navigate_up(self):
        if self.current_index > 0:
            self.current_index -= 1
    
    def navigate_down(self):
        if self.current_index < len(self.files) - 1:
            self.current_index += 1
    
    def select_current(self):
        file = self.files[self.current_index]
        if file not in self.selected_files:
            self.selected_files.append(file)
    
    def display(self):
        for i, file in enumerate(self.files):
            marker = ">" if i == self.current_index else " "
            selected = "✓" if file in self.selected_files else " "
            print(f"{marker} [{selected}] {file}")
```

#### After (v1.2.25):

```python
from core.ui.selector_framework import (
    SelectorFramework, SelectableItem, SelectorConfig,
    SelectionMode
)

class FileListPanel:
    def __init__(self):
        config = SelectorConfig(
            mode=SelectionMode.MULTI,
            show_numbers=True,
            enable_mouse=True
        )
        self.selector = SelectorFramework(config)
        self.files = []
    
    def set_files(self, files):
        self.files = files
        items = [
            SelectableItem(str(i), file, icon="📄")
            for i, file in enumerate(files)
        ]
        self.selector.set_items(items)
    
    def navigate_up(self):
        return self.selector.navigate_up()
    
    def navigate_down(self):
        return self.selector.navigate_down()
    
    def select_current(self):
        return self.selector.select_current()
    
    def display(self):
        lines = self.selector.get_display_lines()
        for line in lines:
            print(line)
    
    def get_selected_files(self):
        selected = self.selector.get_selected_items()
        return [item.value for item in selected]
```

**Benefits:**
- ✅ Automatic keypad support (8↑ 2↓ 5=select 1-9)
- ✅ Mouse click support (if enabled)
- ✅ Visual feedback (▶ indicator, numbers, icons)
- ✅ Pagination (automatic for long lists)
- ✅ Search/filter capability
- ✅ Consistent UX across all components

### Pattern 2: Configuration Panels

#### Before:

```python
class ConfigPanel:
    def __init__(self):
        self.options = {
            'theme': 'dungeon',
            'mouse_enabled': False,
            'keypad_enabled': True
        }
        self.current_option = 0
    
    def handle_key(self, key):
        if key == 'up':
            self.current_option = (self.current_option - 1) % len(self.options)
        elif key == 'down':
            self.current_option = (self.current_option + 1) % len(self.options)
        elif key == 'enter':
            self.toggle_current()
```

#### After:

```python
from core.ui.selector_framework import (
    SelectorFramework, SelectableItem, SelectionMode
)
from core.input.keypad_handler import KeypadHandler

class ConfigPanel:
    def __init__(self):
        self.selector = SelectorFramework()
        self.keypad = KeypadHandler()
        self._setup_options()
        self._setup_keypad()
    
    def _setup_options(self):
        options = [
            SelectableItem("theme", "Theme", value="dungeon", icon="🎨"),
            SelectableItem("mouse", "Mouse Input", value=False, icon="🖱️"),
            SelectableItem("keypad", "Keypad Navigation", value=True, icon="🎮")
        ]
        self.selector.set_items(options)
    
    def _setup_keypad(self):
        self.keypad.register_key('8', self.selector.navigate_up)
        self.keypad.register_key('2', self.selector.navigate_down)
        self.keypad.register_key('5', self.toggle_current)
        self.keypad.register_key('1', lambda: self.selector.select_by_number(1))
        self.keypad.register_key('2', lambda: self.selector.select_by_number(2))
        # ... register 3-9
    
    def handle_key(self, key):
        return self.keypad.handle_key(key)
    
    def toggle_current(self):
        item = self.selector.get_current_item()
        if item:
            item.selected = not item.selected
            return True
        return False
```

### Pattern 3: Adding Mouse Support

#### Before (No mouse support):

```python
class ButtonPanel:
    def __init__(self):
        self.buttons = ["OK", "Cancel", "Help"]
        self.positions = {
            "OK": (10, 5),
            "Cancel": (20, 5),
            "Help": (32, 5)
        }
    
    # Only keyboard navigation
```

#### After (With mouse):

```python
from core.input.mouse_handler import MouseHandler, ClickableRegion

class ButtonPanel:
    def __init__(self, mouse_handler=None):
        self.buttons = ["OK", "Cancel", "Help"]
        self.positions = {
            "OK": (10, 5),
            "Cancel": (20, 5),
            "Help": (32, 5)
        }
        self.mouse = mouse_handler or MouseHandler()
        self._setup_mouse_regions()
    
    def _setup_mouse_regions(self):
        """Create clickable regions for buttons."""
        for name, (x, y) in self.positions.items():
            width = len(name) + 2  # Button width
            region = ClickableRegion(
                name=f"btn_{name.lower()}",
                x1=x, y1=y,
                x2=x + width, y2=y,
                callback=lambda e, n=name: self.on_button_clicked(n)
            )
            self.mouse.add_region(region)
    
    def on_button_clicked(self, button_name):
        """Handle button click."""
        if button_name == "OK":
            self.handle_ok()
        elif button_name == "Cancel":
            self.handle_cancel()
        elif button_name == "Help":
            self.handle_help()
```

### Pattern 4: File Browser Migration

#### Before:

```python
class FileBrowser:
    def __init__(self, workspace_path):
        self.path = workspace_path
        self.files = []
        self.current = 0
        self.selected = []
        self.load_files()
    
    def load_files(self):
        self.files = list(Path(self.path).iterdir())
    
    def navigate(self, direction):
        if direction == "up" and self.current > 0:
            self.current -= 1
        elif direction == "down" and self.current < len(self.files) - 1:
            self.current += 1
    
    def select_file(self):
        file = self.files[self.current]
        if file in self.selected:
            self.selected.remove(file)
        else:
            self.selected.append(file)
    
    def render(self):
        for i, file in enumerate(self.files):
            cursor = "▶ " if i == self.current else "  "
            check = "[✓]" if file in self.selected else "[ ]"
            icon = "📁" if file.is_dir() else "📄"
            print(f"{cursor}{check} {icon} {file.name}")
```

#### After:

```python
from pathlib import Path
from core.ui.selector_framework import (
    SelectorFramework, SelectableItem, SelectorConfig,
    SelectionMode
)
from core.input.keypad_handler import KeypadHandler
from core.input.mouse_handler import MouseHandler

class FileBrowser:
    def __init__(self, workspace_path, mouse_handler=None):
        self.path = Path(workspace_path)
        
        # Initialize input handlers
        config = SelectorConfig(
            mode=SelectionMode.MULTI,
            page_size=20,
            show_numbers=True,
            enable_search=True
        )
        self.selector = SelectorFramework(config)
        self.keypad = KeypadHandler()
        self.mouse = mouse_handler or MouseHandler()
        
        self._setup_keypad()
        self.load_files()
    
    def _setup_keypad(self):
        """Register keypad shortcuts."""
        self.keypad.register_key('8', self.selector.navigate_up)
        self.keypad.register_key('2', self.selector.navigate_down)
        self.keypad.register_key('5', self.select_file)
        self.keypad.register_key('4', self.selector.prev_page)
        self.keypad.register_key('6', self.selector.next_page)
        # Number keys 1-9 for quick selection
        for i in range(1, 10):
            self.keypad.register_key(
                str(i),
                lambda n=i: self.selector.select_by_number(n)
            )
    
    def load_files(self):
        """Load files and convert to SelectableItems."""
        files = list(self.path.iterdir())
        items = []
        
        for i, file in enumerate(files):
            icon = "📁" if file.is_dir() else "📄"
            item = SelectableItem(
                id=str(i),
                label=file.name,
                value=file,
                icon=icon,
                metadata={'path': str(file), 'is_dir': file.is_dir()}
            )
            items.append(item)
        
        self.selector.set_items(items)
        self._setup_mouse_regions()
    
    def _setup_mouse_regions(self):
        """Create clickable regions for visible files."""
        self.mouse.clear_regions()
        visible = self.selector.get_visible_items()
        
        for i, item in enumerate(visible):
            region = ClickableRegion(
                name=f"file_{i}",
                x1=0, y1=i,
                x2=80, y2=i,
                callback=lambda e, idx=i: self._on_file_clicked(idx)
            )
            self.mouse.add_region(region)
    
    def _on_file_clicked(self, index):
        """Handle file click."""
        self.selector.navigate_to(index)
        self.select_file()
    
    def select_file(self):
        """Toggle selection on current file."""
        return self.selector.select_current()
    
    def handle_key(self, key):
        """Handle keyboard input."""
        return self.keypad.handle_key(key)
    
    def render(self):
        """Render browser with automatic formatting."""
        lines = self.selector.get_display_lines()
        for line in lines:
            print(line)
    
    def get_selected_files(self):
        """Get selected file paths."""
        selected = self.selector.get_selected_items()
        return [item.value for item in selected]
```

## Device Capability Checking

Always check device capabilities before enabling features:

```python
from core.services.device_manager import get_device_manager

class MyComponent:
    def __init__(self):
        self.dm = get_device_manager()
        self._check_capabilities()
    
    def _check_capabilities(self):
        """Check and adapt to device capabilities."""
        caps = self.dm.get_capabilities()
        
        # Mouse support
        if caps['mouse']:
            self.enable_mouse_support()
        else:
            print("ℹ️  Mouse not available (keyboard only)")
        
        # Color support
        colors = caps['terminal']['colors']
        if colors >= 256:
            self.use_full_colors()
        elif colors >= 16:
            self.use_basic_colors()
        else:
            self.use_monochrome()
        
        # Terminal size
        width = caps['terminal']['width']
        height = caps['terminal']['height']
        self.adjust_layout(width, height)
    
    def enable_mouse_support(self):
        from core.input.mouse_handler import MouseHandler
        self.mouse = MouseHandler()
        self.mouse.enable()
    
    def use_full_colors(self):
        self.highlight_color = "cyan"
        self.select_color = "green"
    
    def use_basic_colors(self):
        self.highlight_color = "blue"
        self.select_color = "green"
    
    def use_monochrome(self):
        # Use symbols instead of colors
        pass
```

## Testing Your Migration

### 1. Unit Tests

Create tests for your migrated component:

```python
# tests/test_my_component.py

import pytest
from core.ui.selector_framework import SelectableItem
from my_component import MyComponent

def test_navigation():
    """Test navigation with selector."""
    component = MyComponent()
    items = [SelectableItem(str(i), f"Item {i}") for i in range(5)]
    component.selector.set_items(items)
    
    # Test navigation
    assert component.selector.current_index == 0
    component.selector.navigate_down()
    assert component.selector.current_index == 1
    component.selector.navigate_up()
    assert component.selector.current_index == 0

def test_selection():
    """Test selection functionality."""
    component = MyComponent()
    items = [SelectableItem(str(i), f"Item {i}") for i in range(5)]
    component.selector.set_items(items)
    
    # Test selection
    component.selector.select_current()
    selected = component.selector.get_selected_items()
    assert len(selected) == 1
    assert selected[0].id == "0"

def test_keypad_handling():
    """Test keypad input."""
    component = MyComponent()
    
    # Test key handlers registered
    assert component.keypad.handle_key('8')  # Up
    assert component.keypad.handle_key('2')  # Down
    assert component.keypad.handle_key('5')  # Select
```

### 2. Integration Tests

Add to SHAKEDOWN test:

```upy
# memory/ucode/tests/shakedown.upy

PRINT[ '  📝 TEST: MyComponent Integration' ]
PRINT[ '     Testing: Component uses selector framework' ]
# Test commands here
PRINT[ '     ✅ Component migrated successfully' ]
```

### 3. Manual Testing

Test interactively:

```bash
# Launch your component
./start_udos.sh

# Test keypad navigation
uDOS> MYCOMPONENT
# Press: 8 (up), 2 (down), 5 (select), 1-9 (numbers)

# Test mouse (if supported)
# Click items with mouse
# Try double-click
# Test scroll wheel

# Check status
uDOS> MYCOMPONENT STATUS
```

## Common Migration Issues

### Issue 1: Custom Key Bindings Conflict

**Problem:** Component uses custom keys that conflict with keypad

**Solution:** Use context-aware key handling

```python
from core.input.keypad_handler import KeypadHandler

class MyComponent:
    def __init__(self):
        self.keypad = KeypadHandler()
        self.mode = "normal"  # or "edit"
    
    def handle_key(self, key):
        if self.mode == "edit":
            # Edit mode: keys are literal input
            self.handle_edit_key(key)
        else:
            # Normal mode: keypad navigation
            if not self.keypad.handle_key(key):
                # Key not handled by keypad, custom handling
                self.handle_custom_key(key)
```

### Issue 2: Mouse Regions Not Updating

**Problem:** Clickable regions don't update when content changes

**Solution:** Clear and recreate regions on updates

```python
def update_content(self):
    """Update display and mouse regions."""
    # Update selector items
    self.selector.set_items(new_items)
    
    # Recreate mouse regions
    self._setup_mouse_regions()

def _setup_mouse_regions(self):
    """Always clear before recreating."""
    self.mouse.clear_regions()
    
    visible = self.selector.get_visible_items()
    for i, item in enumerate(visible):
        # Create regions for visible items only
        region = ClickableRegion(...)
        self.mouse.add_region(region)
```

### Issue 3: Pagination Breaking Display

**Problem:** Content disappears when using pagination

**Solution:** Use `get_visible_items()` for display

```python
def render(self):
    """Render current page only."""
    # ✅ Good: Use visible items
    visible = self.selector.get_visible_items()
    
    # ❌ Bad: Use all items
    # items = self.selector.items  # Shows all pages!
    
    for item in visible:
        print(self._format_item(item))
    
    # Show pagination info
    stats = self.selector.get_stats()
    total_pages = (stats['total_items'] + self.selector.page_size - 1) // self.selector.page_size
    print(f"\nPage {self.selector.page + 1}/{total_pages}")
```

### Issue 4: Performance with Large Lists

**Problem:** Slow rendering with 1000+ items

**Solution:** Use pagination and lazy loading

```python
class LargeListComponent:
    def __init__(self):
        config = SelectorConfig(
            page_size=20,  # Smaller page size
            enable_search=True  # Filter to reduce items
        )
        self.selector = SelectorFramework(config)
    
    def load_items_lazy(self):
        """Load items on demand."""
        # Only load current page
        start = self.selector.page * self.selector.page_size
        end = start + self.selector.page_size
        
        items = self._fetch_items(start, end)
        self.selector.set_items(items)
```

## Deprecation Warnings

The following patterns are deprecated and should be migrated:

❌ **Deprecated:**
```python
# Custom navigation logic
if key == 'up':
    index -= 1

# Manual selection tracking
selected_items = []
if item not in selected_items:
    selected_items.append(item)

# Hard-coded display formatting
print(f"{'>' if current else ' '} {item}")
```

✅ **Use instead:**
```python
# Selector framework
selector.navigate_up()

# Automatic selection tracking
selector.select_current()
selected = selector.get_selected_items()

# Automatic formatting
lines = selector.get_display_lines()
for line in lines:
    print(line)
```

## Migration Checklist by Component Type

### File Browsers
- [ ] Replace file list with `SelectableItem` objects
- [ ] Use `SelectorFramework` for navigation
- [ ] Add `KeypadHandler` for 8↑ 2↓ keys
- [ ] Add `MouseHandler` for clicks
- [ ] Support multi-select mode
- [ ] Add pagination for large directories
- [ ] Implement search/filter

### Configuration Panels
- [ ] Convert options to `SelectableItem` format
- [ ] Use toggle or single-select mode
- [ ] Add number keys for quick selection (1-9)
- [ ] Show visual indicators (icons, checkmarks)
- [ ] Support mouse clicks on options
- [ ] Persist selections to config

### Menu Systems
- [ ] Use single-select mode
- [ ] Add icons for menu items
- [ ] Enable number shortcuts
- [ ] Add mouse regions for menu items
- [ ] Show highlighted current item
- [ ] Support nested menus (if needed)

### List Displays
- [ ] Convert items to `SelectableItem`
- [ ] Add pagination for long lists
- [ ] Enable search/filter
- [ ] Support multi-select (if appropriate)
- [ ] Add mouse regions per item
- [ ] Show page indicators

## Getting Help

If you encounter issues during migration:

1. **Check Examples:** Look at existing migrated components
   - `core/commands/keypad_demo_handler.py`
   - `core/commands/selector_handler.py`
   - `core/ui/file_browser.py` (if updated)

2. **Run Tests:** Use SHAKEDOWN to validate
   ```bash
   ./start_udos.sh memory/ucode/tests/shakedown.upy
   ```

3. **Check Documentation:**
   - `core/docs/INPUT-SYSTEM.md` - Full API reference
   - `wiki/Developers-Guide.md` - General development guide

4. **Test Commands:**
   ```bash
   DEVICE STATUS     # Check capabilities
   KEYPAD DEMO       # See keypad examples
   MOUSE STATUS      # Test mouse support
   SELECTOR DEMO     # See selector examples
   ```

---

**Last Updated:** December 13, 2025  
**Version:** 1.2.25  
**Status:** ✅ Complete
