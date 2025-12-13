# Universal Input Device System (v1.2.25)

**Version:** 1.2.25  
**Status:** Complete  
**Lines of Code:** ~3,325 lines  
**Tests:** 69+ passing (19 input system tests)

## Overview

The Universal Input Device System provides a comprehensive, standardized framework for handling all user input in uDOS. It unifies keyboard, mouse, and terminal interactions into a consistent API that works across all TUI components.

## Architecture

```
Input Device System
├── Device Detection (Phase 1)
│   ├── device_manager.py - Hardware capability detection
│   └── device_handler.py - DEVICE command interface
├── Keypad Navigation (Week 2)
│   ├── keypad_handler.py - 0-9 navigation system
│   ├── selector_base.py - Base selector classes
│   └── keypad_demo_handler.py - Demonstrations
├── Mouse Integration (Week 3)
│   ├── mouse_handler.py - Event processing
│   └── mouse_handler.py (commands) - MOUSE interface
└── Selector Framework (Week 4)
    ├── selector_framework.py - Unified selection API
    └── selector_handler.py - SELECTOR interface
```

## Components

### 1. Device Detection System

**Files:**
- `core/services/device_manager.py` (+230 lines)
- `core/commands/device_handler.py` (+230 lines)

**Features:**
- Automatic keyboard detection
- Mouse capability detection (xterm protocol)
- Terminal feature detection (colors, Unicode, size)
- Input mode configuration (keypad/full_keyboard/hybrid)

**Commands:**
```bash
DEVICE STATUS              # Show detected capabilities
DEVICE SETUP               # Configure input modes
DEVICE MODE keypad         # Set input mode
DEVICE ENABLE MOUSE        # Enable mouse support
DEVICE TEST                # Interactive input testing
```

**Example:**
```python
from core.services.device_manager import get_device_manager

dm = get_device_manager()
caps = dm.get_capabilities()

if caps['mouse']:
    print("Mouse support available")
if caps['terminal']['colors'] >= 256:
    print("Full color support")
```

### 2. Keypad Navigation System

**Files:**
- `core/input/keypad_handler.py` (+450 lines)
- `core/ui/selector_base.py` (+170 lines)
- `core/commands/keypad_demo_handler.py` (+343 lines)

**Key Mappings:**
```
8 ↑  - Move up / Scroll up
2 ↓  - Move down / Scroll down
4 ←  - Move left / Previous
6 →  - Move right / Next
5 ⏎  - OK / Select / Confirm
7    - Redo
9    - Undo
1    - Yes / Select Item 1
3    - No / Select Item 3
0    - Menu / More Options
```

**Features:**
- Universal 0-9 navigation across all panels
- Context-aware key handling
- Visual feedback for pressed keys
- Mode-based behavior (menu, list, browser, pager)
- Integration with existing TUI keypad (v1.2.15)

**Commands:**
```bash
KEYPAD DEMO               # Show all demonstrations
KEYPAD MENU               # Menu selector example
KEYPAD LIST               # List selector example
KEYPAD TEST               # Interactive test
KEYPAD KEYS               # Complete key reference
```

**Example:**
```python
from core.input.keypad_handler import KeypadHandler

handler = KeypadHandler()
handler.register_key('5', lambda: print("Selected!"))
handler.register_key('8', lambda: navigate_up())
handler.register_key('2', lambda: navigate_down())
```

### 3. Mouse Integration System

**Files:**
- `core/input/mouse_handler.py` (+540 lines)
- `core/commands/mouse_handler.py` (+350 lines)

**Features:**
- Click detection (left, right, middle buttons)
- Double-click with configurable threshold (300ms)
- Drag and drop with distance threshold (3px)
- Scroll wheel events (up/down)
- Clickable regions with callbacks
- Real-time position tracking
- Usage statistics

**Event Types:**
```python
from core.input.mouse_handler import MouseEventType, MouseButton

# Event types
CLICK          # Button press/release
DOUBLE_CLICK   # Two clicks within threshold
DRAG_START     # Drag initiated
DRAG_MOVE      # Dragging in progress
DRAG_END       # Drag completed
SCROLL         # Mouse wheel
HOVER          # Mouse over region
MOVE           # Position changed
```

**Commands:**
```bash
MOUSE ENABLE              # Turn on mouse input
MOUSE DISABLE             # Turn off mouse input
MOUSE STATUS              # Show state and statistics
MOUSE DEMO                # Interactive demo
MOUSE REGION ADD <name> <x1> <y1> <x2> <y2>
MOUSE REGION LIST         # List clickable regions
MOUSE RESET               # Reset statistics
```

**Example:**
```python
from core.input.mouse_handler import MouseHandler, ClickableRegion

mouse = MouseHandler()

# Define clickable region
def on_click(event):
    print(f"Clicked at {event.position}")

region = ClickableRegion(
    name="button",
    x1=10, y1=5,
    x2=30, y2=7,
    callback=on_click
)
mouse.add_region(region)
```

### 4. Selector Framework

**Files:**
- `core/ui/selector_framework.py` (+520 lines)
- `core/commands/selector_handler.py` (+270 lines)

**Selection Modes:**
```python
SINGLE    # One item at a time (radio button)
MULTI     # Multiple items (checkboxes)
TOGGLE    # Toggle states on/off
NONE      # Display only (no selection)
```

**Navigation Modes:**
```python
LINEAR    # Up/down only
GRID      # 2D navigation (up/down/left/right)
TREE      # Hierarchical (expand/collapse)
WRAP      # Wrap around at edges
```

**Features:**
- Consistent selection API across all components
- Keypad navigation integration
- Mouse click support
- Visual feedback (highlighting, icons)
- Pagination for long lists (configurable page size)
- Multi-select with checkboxes
- Search and filter capability
- Number-based selection (1-9 keys)
- Statistics tracking

**Commands:**
```bash
SELECTOR DEMO             # Interactive demonstrations
SELECTOR TEST single      # Test single-select mode
SELECTOR TEST multi       # Test multi-select mode
SELECTOR STATUS           # Show statistics
```

**Example:**
```python
from core.ui.selector_framework import (
    SelectorFramework, SelectableItem, SelectorConfig,
    SelectionMode
)

# Create selector
config = SelectorConfig(
    mode=SelectionMode.MULTI,
    page_size=10,
    show_numbers=True
)
selector = SelectorFramework(config)

# Add items
items = [
    SelectableItem("1", "Option 1", icon="📄"),
    SelectableItem("2", "Option 2", icon="📁"),
    SelectableItem("3", "Option 3", icon="🔧"),
]
selector.set_items(items)

# Navigation
selector.navigate_down()      # Move down
selector.select_current()     # Select item
selector.select_by_number(5)  # Quick select #5

# Get selections
selected = selector.get_selected_items()
```

## Integration Guide

### Migrating Existing Components

#### Before (Old Pattern):
```python
class MyBrowser:
    def __init__(self):
        self.items = ["item1", "item2", "item3"]
        self.current = 0
    
    def navigate_down(self):
        if self.current < len(self.items) - 1:
            self.current += 1
    
    def select(self):
        return self.items[self.current]
```

#### After (Using Selector Framework):
```python
from core.ui.selector_framework import (
    SelectorFramework, SelectableItem, SelectionMode
)

class MyBrowser:
    def __init__(self):
        self.selector = SelectorFramework()
        items = [
            SelectableItem(str(i), item)
            for i, item in enumerate(["item1", "item2", "item3"])
        ]
        self.selector.set_items(items)
    
    def navigate_down(self):
        self.selector.navigate_down()
    
    def select(self):
        item = self.selector.get_current_item()
        return item.value if item else None
```

### Adding Mouse Support to Panels

```python
from core.input.mouse_handler import MouseHandler, ClickableRegion

class MyPanel:
    def __init__(self, mouse_handler=None):
        self.mouse = mouse_handler or MouseHandler()
        self._setup_regions()
    
    def _setup_regions(self):
        # Add clickable button
        button = ClickableRegion(
            name="ok_button",
            x1=10, y1=20,  # Top-left
            x2=20, y2=22,  # Bottom-right
            callback=self.on_ok_clicked
        )
        self.mouse.add_region(button)
    
    def on_ok_clicked(self, event):
        print(f"OK button clicked at {event.position}")
```

### Keypad Navigation in Custom Components

```python
from core.input.keypad_handler import KeypadHandler

class MyComponent:
    def __init__(self):
        self.keypad = KeypadHandler()
        self._register_keys()
    
    def _register_keys(self):
        self.keypad.register_key('8', self.scroll_up)
        self.keypad.register_key('2', self.scroll_down)
        self.keypad.register_key('5', self.confirm_action)
        self.keypad.register_key('0', self.show_menu)
    
    def handle_input(self, key):
        return self.keypad.handle_key(key)
```

## Best Practices

### 1. Use Selector Framework for All Lists/Menus

✅ **Good:**
```python
selector = SelectorFramework()
selector.set_items(items)
# Automatic keypad + mouse support
```

❌ **Bad:**
```python
# Custom navigation logic
current_index = 0
if key == 'up':
    current_index -= 1
# Reinventing the wheel
```

### 2. Register Mouse Regions Dynamically

✅ **Good:**
```python
def update_layout(self):
    self.mouse.clear_regions()
    for i, item in enumerate(self.visible_items):
        region = ClickableRegion(
            name=f"item_{i}",
            x1=0, y1=i,
            x2=80, y2=i,
            callback=lambda e, idx=i: self.select_item(idx)
        )
        self.mouse.add_region(region)
```

❌ **Bad:**
```python
# Static regions that don't update
region = ClickableRegion(name="item", ...)
mouse.add_region(region)
# Never updated when content changes
```

### 3. Provide Visual Feedback

✅ **Good:**
```python
items = selector.get_display_lines()  # Auto-formatted
for line in items:
    print(line)  # Includes ▶ indicators, numbers, icons
```

❌ **Bad:**
```python
for item in selector.items:
    print(item.label)  # No visual indicators
```

### 4. Check Device Capabilities

✅ **Good:**
```python
dm = get_device_manager()
if dm.has_mouse_support():
    mouse.enable()
else:
    print("⚠️  Mouse not available (keyboard only)")
```

❌ **Bad:**
```python
mouse.enable()  # Fails silently if unsupported
```

## Configuration

### Device Settings

File: `memory/bank/system/device.json`

```json
{
  "input_mode": "keypad",
  "mouse_enabled": true,
  "keyboard_type": "full",
  "terminal_type": "xterm-256color"
}
```

### Selector Settings

```python
config = SelectorConfig(
    mode=SelectionMode.SINGLE,    # Selection mode
    navigation=NavigationMode.LINEAR,  # Navigation type
    wrap_around=True,              # Wrap at edges
    show_numbers=True,             # Show 1-9 numbers
    page_size=10,                  # Items per page
    enable_search=True,            # Search capability
    enable_mouse=True,             # Mouse support
    highlight_color="cyan",        # Highlight color
    select_icon="✓",               # Selection marker
    disabled_icon="✗"              # Disabled marker
)
```

### Mouse Settings

```python
mouse = MouseHandler()
mouse.double_click_threshold = 0.3  # 300ms
mouse.drag_threshold = 3            # 3 pixels
```

## Testing

### Running Tests

```bash
# Full SHAKEDOWN test (69+ tests)
./start_udos.sh memory/ucode/tests/shakedown.upy

# Test specific components
DEVICE STATUS              # Device detection
KEYPAD DEMO                # Keypad navigation
MOUSE STATUS               # Mouse input
SELECTOR DEMO              # Selector framework
```

### Unit Tests

```bash
# Run Python unit tests
pytest core/tests/test_input_system.py -v
pytest core/tests/test_selector_framework.py -v
pytest core/tests/test_mouse_handler.py -v
```

### Manual Testing

1. **Keypad Navigation:**
   - Run `KEYPAD DEMO`
   - Press 8↑ 2↓ to navigate
   - Press 5 to select
   - Press 1-9 for number selection

2. **Mouse Input:**
   - Run `MOUSE DEMO`
   - Click items with mouse
   - Try double-click
   - Test drag and drop
   - Use scroll wheel

3. **Selector Framework:**
   - Run `SELECTOR TEST multi`
   - Navigate with 8↑ 2↓
   - Select with 5
   - Try number keys 1-9
   - Test pagination with 4← 6→

## Troubleshooting

### Mouse Not Working

**Problem:** Mouse clicks not detected

**Solutions:**
1. Check terminal compatibility: `DEVICE STATUS`
2. Enable mouse: `MOUSE ENABLE`
3. Verify xterm protocol support
4. Try different terminal (iTerm2, Terminal.app work best)

### Keypad Navigation Not Responding

**Problem:** Number keys not working

**Solutions:**
1. Check input mode: `DEVICE STATUS`
2. Set keypad mode: `DEVICE MODE keypad`
3. Verify NumLock is ON (if using separate numpad)
4. Check TUI keypad state: `TUI STATUS`

### Selector Not Displaying Items

**Problem:** Empty selector or no items shown

**Solutions:**
1. Verify items added: `selector.set_items(items)`
2. Check page size: Items might be on other pages
3. Clear filters: `selector.clear_filter()`
4. Verify current page: `selector.page = 0`

## Performance

### Benchmarks

- **Keypad Handler:** < 1ms per key press
- **Mouse Events:** < 5ms per event
- **Selector Navigation:** < 1ms per item
- **Region Detection:** < 2ms for 100 regions

### Optimization Tips

1. **Limit clickable regions:** < 100 regions per view
2. **Use pagination:** Keep page size ≤ 20 items
3. **Debounce mouse moves:** Track every 50ms max
4. **Cache selector display:** Regenerate only on change

## API Reference

### Device Manager

```python
from core.services.device_manager import get_device_manager

dm = get_device_manager()

# Detection
dm.detect_keyboard()         # → KeyboardInfo
dm.detect_mouse()            # → MouseInfo
dm.detect_terminal()         # → TerminalInfo
dm.get_capabilities()        # → Dict[str, Any]

# Checks
dm.has_mouse_support()       # → bool
dm.has_numpad()              # → bool
dm.supports_256_colors()     # → bool
```

### Keypad Handler

```python
from core.input.keypad_handler import KeypadHandler

kh = KeypadHandler()

# Registration
kh.register_key('8', callback)
kh.unregister_key('8')
kh.clear_all()

# Handling
kh.handle_key('5')           # → bool (handled)
kh.get_key_action('8')       # → Callable
```

### Mouse Handler

```python
from core.input.mouse_handler import MouseHandler

mh = MouseHandler()

# Control
mh.enable()
mh.disable()
mh.is_enabled()              # → bool

# Regions
mh.add_region(region)
mh.remove_region(name)
mh.find_region_at(position)  # → ClickableRegion
mh.clear_regions()

# Events
mh.parse_mouse_event(data)   # → MouseEvent
mh.process_event(event)      # → bool

# Statistics
mh.get_stats()               # → Dict
mh.reset_stats()
```

### Selector Framework

```python
from core.ui.selector_framework import SelectorFramework

sf = SelectorFramework(config)

# Items
sf.set_items(items)
sf.add_item(item)
sf.remove_item(item_id)
sf.get_item(item_id)         # → SelectableItem
sf.get_current_item()        # → SelectableItem
sf.get_selected_items()      # → List[SelectableItem]

# Navigation
sf.navigate_up()             # → bool
sf.navigate_down()           # → bool
sf.navigate_to(index)        # → bool

# Selection
sf.select_current()          # → bool
sf.select_by_number(n)       # → bool (1-9)
sf.confirm_selection()       # → bool

# Pagination
sf.next_page()               # → bool
sf.prev_page()               # → bool

# Search
sf.filter_items(query)
sf.clear_filter()

# Display
sf.get_display_lines()       # → List[str]
sf.get_stats()               # → Dict
```

## Future Enhancements

### Planned for v1.3.0+

1. **Touch Input Support** (extensions/input)
   - Swipe gestures
   - Pinch to zoom
   - Multi-touch
   - Requires extension installation

2. **Voice Commands** (extensions/voice)
   - Speech recognition
   - Voice navigation
   - Command execution
   - Optional extension

3. **Gamepad Support** (extensions/input)
   - Controller detection
   - Button mapping
   - Analog stick navigation
   - Optional extension

4. **Gesture Recognition**
   - Mouse gesture patterns
   - Quick actions
   - Custom gesture definitions

## Version History

- **v1.2.25** (Dec 2025) - Complete input system
  - Phase 1: Device detection
  - Week 2: Keypad navigation
  - Week 3: Mouse integration
  - Week 4: Selector framework
  - Weeks 5-6: Documentation & testing

- **v1.2.15** (Nov 2025) - TUI system
  - Initial keypad navigator
  - Command predictor
  - Enhanced pager

- **v1.2.14** (Nov 2025) - Grid-first
  - Basic input handling
  - Terminal size detection

## Support

For issues or questions:
- GitHub Issues: https://github.com/fredporter/uDOS/issues
- Documentation: wiki/INPUT-SYSTEM.md
- Tests: memory/ucode/tests/shakedown.upy
- Commands: HELP DEVICE, HELP KEYPAD, HELP MOUSE, HELP SELECTOR

---

**Last Updated:** December 13, 2025  
**Version:** 1.2.25  
**Status:** ✅ Complete
