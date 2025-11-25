# Mac OS System UI Components - SVG Library

Complete implementation of classic Mac OS System 1 UI elements (1984-1991) in SVG format, based on [system.css](https://sakofchit.github.io/system.css/) and Apple Human Interface Guidelines.

## Overview

This library provides pixel-perfect SVG recreations of Mac OS System UI components for use in technical diagrams, educational materials, and instructional graphics.

**Library file:** `dev/tools/macos_ui_components.py`

## Available Components

### 1. Buttons

Standard Mac OS rounded rectangle buttons with text labels.

**Function:** `create_button(x, y, text, width=None, default=False, disabled=False, active=False)`

**Parameters:**
- `x, y`: Position coordinates
- `text`: Button label text
- `width`: Custom width (default 59px)
- `default`: Thick border for default action (default False)
- `disabled`: Gray text for disabled state (default False)
- `active`: Inverted colors for pressed state (default False)

**Specifications:**
- Standard size: 59×20px
- Border radius: 8px
- Font: 11pt monospace
- States: normal (white fill, black text), active (black fill, white text), disabled (gray text)

**Example:**
```python
create_button(50, 50, "OK", default=True)
create_button(120, 50, "Cancel")
create_button(190, 50, "Disabled", disabled=True)
```

### 2. Windows

Complete Mac OS System windows with title bars, close boxes, and content areas.

**Function:** `create_window(x, y, width, height, title, active=True, closable=True, content=None, details_bar=None)`

**Parameters:**
- `x, y`: Position coordinates
- `width, height`: Window dimensions (includes title bar)
- `title`: Window title text
- `active`: Active (black racing stripes) vs inactive (white stripes)
- `closable`: Show close box (default True)
- `content`: SVG content string for window pane
- `details_bar`: Optional details bar text below title

**Specifications:**
- Title bar height: 19px
- Border width: 1px
- Title font: 12pt bold monospace
- Racing stripes: 5 vertical lines in title bar
- Close box: 9×9px square with 5×5px inner fill

**Example:**
```python
create_window(
    50, 50, 300, 200, "My Window",
    active=True,
    details_bar="details • info • status",
    content='<text x="10" y="20">Window content</text>'
)
```

### 3. Dialogs

Modal and modeless dialog boxes.

**Function:** `create_dialog(x, y, width, height, title, modal=False, content=None)`

**Parameters:**
- `x, y`: Position coordinates
- `width, height`: Dialog dimensions
- `title`: Dialog title text
- `modal`: Modal (double border) vs modeless (single border)
- `content`: SVG content string

**Specifications:**
- Modal dialogs: 2px double outline border
- Modeless dialogs: Like windows without size/zoom boxes
- Title bar: Simplified, no close box for modal

**Example:**
```python
create_dialog(
    50, 50, 350, 180, "Modal Dialog",
    modal=True,
    content='<text x="10" y="20">Dialog message</text>'
)
```

### 4. Alert Boxes

Standard alert boxes with icon space and button array.

**Function:** `create_alert_box(x, y, width, message, buttons=None, icon_space=True)`

**Parameters:**
- `x, y`: Position coordinates
- `width`: Width (height auto-calculated)
- `message`: Alert message text (use `\n` for line breaks)
- `buttons`: List of button labels (default `["Cancel", "OK"]`)
- `icon_space`: Reserve 32×32px space for alert icon (default True)

**Specifications:**
- Double outline border (modal style)
- Icon space: 32×32px placeholder on left
- Auto-height based on message length
- Right-aligned buttons, last button is default

**Example:**
```python
create_alert_box(
    50, 50, 400,
    "Are you sure you want to\\ndelete this item?",
    buttons=["No", "Yes"],
    icon_space=True
)
```

### 5. Checkboxes

Standard checkboxes with labels.

**Function:** `create_checkbox(x, y, label, checked=False)`

**Parameters:**
- `x, y`: Position coordinates
- `label`: Checkbox label text
- `checked`: Checked state (default False)

**Specifications:**
- Size: 12×12px
- Checkmark: Bold X-shaped mark
- Label font: 9pt monospace, 16px offset from box

**Example:**
```python
create_checkbox(50, 50, "Enable option", checked=True)
create_checkbox(50, 70, "Disabled option")
```

### 6. Radio Buttons

Standard radio buttons with labels.

**Function:** `create_radio_button(x, y, label, selected=False)`

**Parameters:**
- `x, y`: Position coordinates
- `label`: Radio button label text
- `selected`: Selected state (default False)

**Specifications:**
- Outer circle: 12px diameter
- Inner circle: 8px diameter (when selected)
- Label font: 9pt monospace, 16px offset from circle

**Example:**
```python
create_radio_button(50, 50, "Option A", selected=True)
create_radio_button(50, 70, "Option B")
```

### 7. Text Boxes

Text input boxes with optional placeholder/value.

**Function:** `create_text_box(x, y, width, placeholder="", value="")`

**Parameters:**
- `x, y`: Position coordinates
- `width`: Box width
- `placeholder`: Placeholder text (gray)
- `value`: Actual input value (black)

**Specifications:**
- Height: 16px
- Border: 1px black
- Font: 9pt monospace
- Placeholder in gray (#808080), value in black

**Example:**
```python
create_text_box(50, 50, 200, placeholder="Enter text...")
create_text_box(50, 75, 200, value="User input")
```

### 8. Menu Bars

Top menu bar with menu items.

**Function:** `create_menu_bar(x, y, width, items)`

**Parameters:**
- `x, y`: Position coordinates
- `width`: Menu bar width
- `items`: List of menu item labels

**Specifications:**
- Height: 20px
- Font: 12pt bold monospace
- Items spaced 16px apart (plus text width)

**Example:**
```python
create_menu_bar(50, 50, 500, ["File", "Edit", "View", "Special"])
```

## Design Constants

All dimensions based on Apple HI Guidelines (1984-1991):

```python
BUTTON_HEIGHT = 20
BUTTON_WIDTH = 59
BUTTON_BORDER_RADIUS = 8
TITLE_BAR_HEIGHT = 19
WINDOW_BORDER = 1
DIALOG_BORDER = 2  # Double outline

# Font sizes (Chicago/Geneva simulation using monospace)
TITLE_FONT_SIZE = 12      # Chicago 12pt
MENU_FONT_SIZE = 12       # Menu items
BUTTON_FONT_SIZE = 11     # Button labels
BODY_FONT_SIZE = 9        # Geneva 9pt
```

## Usage Examples

### Water Purification Decision Flow

```python
from macos_ui_components import create_window, create_checkbox, create_button

svg = create_window(
    50, 50, 400, 200, "Water Treatment",
    details_bar="Step 1 of 3",
    content=f"""
        <text x="0" y="15">Select methods:</text>
        {create_checkbox(0, 30, "Filter debris", checked=True)}
        {create_checkbox(0, 50, "Boil 1 minute", checked=True)}
        {create_checkbox(0, 70, "Add iodine")}
        {create_button(200, 100, "Next", default=True)}
    """
)
```

### Emergency Alert

```python
from macos_ui_components import create_alert_box

svg = create_alert_box(
    100, 100, 400,
    "WARNING: Shelter required within\\n3 hours in cold conditions.\\nBegin construction now?",
    buttons=["Later", "Start Now"],
    icon_space=True
)
```

### Multi-Step Checklist

```python
from macos_ui_components import create_window, create_checkbox

steps = [
    "Check location safety",
    "Gather materials",
    "Build framework",
    "Add insulation",
    "Test waterproofing"
]

checkboxes = "\\n".join([
    create_checkbox(0, i*20, step)
    for i, step in enumerate(steps)
])

svg = create_window(
    50, 50, 350, 180, "Shelter Checklist",
    content=checkboxes
)
```

## Integration with Diagram Templates

Combine UI components with existing pattern library:

```python
from macos_ui_components import create_window, create_button
from diagram_templates import PATTERN_DEFS

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
{PATTERN_DEFS}

  <!-- Background with pattern -->
  <rect x="0" y="0" width="800" height="600" fill="url(#gray-12)"/>

  <!-- UI elements on top -->
  {create_window(50, 50, 400, 300, "Survival Guide")}

</svg>"""
```

## Design Philosophy

These components follow the original Mac OS System 1 design principles:

1. **Monochrome only** - Black, white, and solid grays
2. **Pixel-perfect** - Precise dimensions from HI Guidelines
3. **Editable text** - All text as `<text>` elements, never paths
4. **Generic fonts** - Monospace simulation of Chicago/Geneva
5. **Geometric clarity** - Bold, clear shapes and borders
6. **Functional design** - Form follows function, no decoration

## File Sizes

All components are optimized for minimal file size:
- Single button: ~200 bytes
- Window with content: ~2-5KB
- Alert box: ~1-3KB
- Complete demo page: ~19KB

## Browser Compatibility

Pure SVG 1.1, compatible with:
- All modern browsers
- Inkscape, Illustrator
- PDF export
- Print (300dpi tested)

## Credits

Based on:
- [system.css](https://sakofchit.github.io/system.css/) by [@sakofchit](https://twitter.com/sakofchit)
- Apple Human Interface Guidelines (1984-1991)
- Chicago 12pt and Geneva 9pt font concepts by [@blogmywiki](https://twitter.com/blogmywiki)

Implemented for uDOS diagram system by converting CSS to SVG components.
