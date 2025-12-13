# Universal Input Device System - Examples

Practical examples demonstrating the v1.2.25 Universal Input Device System.

## Examples

### 1. File Browser (`file_browser_example.py`)
Interactive file browser using selector framework with keypad navigation.

**Features:**
- Directory navigation with 0-9 keys
- Mouse click selection (if available)
- Pagination for large directories
- Search/filter functionality

**Usage:**
```bash
python examples/input_system/file_browser_example.py
```

### 2. Menu System (`menu_system_example.py`)
Multi-level menu system with both keypad and mouse input.

**Features:**
- Hierarchical menu navigation
- Quick selection with number keys
- Mouse hover and click support
- Back/forward navigation

**Usage:**
```bash
python examples/input_system/menu_system_example.py
```

### 3. Configuration Panel (`config_panel_example.py`)
Settings configuration interface with various input methods.

**Features:**
- Toggle settings with keypad
- Mouse-based drag controls
- Keyboard shortcuts
- Real-time validation

**Usage:**
```bash
python examples/input_system/config_panel_example.py
```

### 4. Custom Component (`custom_component_example.py`)
Building a custom UI component using the input system APIs.

**Features:**
- Custom selector implementation
- Hybrid input handling
- Event callbacks
- State management

**Usage:**
```bash
python examples/input_system/custom_component_example.py
```

## Key Concepts

### Device Detection
```python
from core.services.device_manager import DeviceManager

manager = DeviceManager()
caps = manager.detect_input_capabilities()

if caps["mouse"]["available"]:
    print("Mouse input supported")
```

### Selector Framework
```python
from core.ui.selector_framework import SelectorFramework, SelectionMode

selector = SelectorFramework(
    items=["Option 1", "Option 2", "Option 3"],
    mode=SelectionMode.SINGLE
)

selector.navigate_down()
result = selector.select_current()
```

### Keypad Handler
```python
from core.input.keypad_handler import KeypadHandler, KeypadMode

handler = KeypadHandler()
handler.set_mode(KeypadMode.SELECTION)
handler.set_items(["File", "Edit", "View"])

# User presses '1'
result = handler.handle_key('1')  # Returns "File"
```

### Mouse Handler
```python
from core.input.mouse_handler import MouseHandler, ClickableRegion

handler = MouseHandler()
region = ClickableRegion("button", x=10, y=5, width=20, height=3)
handler.add_region(region, callback=on_click)

handler.enable()
```

## Best Practices

1. **Always detect capabilities first**
   - Check device support before enabling features
   - Provide fallbacks for unavailable input methods

2. **Use appropriate input modes**
   - Keypad mode for simple selection
   - Full keyboard for text editing
   - Hybrid mode for mixed interactions

3. **Handle edge cases**
   - Empty lists in selectors
   - Disabled input states
   - Terminal resize events

4. **Provide visual feedback**
   - Highlight selected items
   - Show available key hints
   - Display mouse hover states

## API Documentation

See `core/docs/INPUT-SYSTEM.md` for complete API reference.

## Migration Guide

See `core/docs/MIGRATION-GUIDE-v1.2.25.md` for migrating existing components.
