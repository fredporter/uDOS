#!/usr/bin/env python3
"""
Mac OS System UI Components Library - SVG Edition
Based on system.css and Apple Human Interface Guidelines (1984-1991)

Provides reusable SVG functions for classic Mac UI elements:
- Windows (title bars, borders, dialogs)
- Buttons (standard, default, disabled)
- Form elements (checkboxes, radio buttons, text boxes)
- Menu bars and dropdowns
- Alert boxes and modal dialogs
"""

from typing import Optional, List, Tuple

# UI Constants from System.css
BUTTON_HEIGHT = 20
BUTTON_WIDTH = 59
BUTTON_BORDER_RADIUS = 8
TITLE_BAR_HEIGHT = 19
WINDOW_BORDER = 1
DIALOG_BORDER = 2  # Double outline

# Chicago 12pt simulation (using monospace)
TITLE_FONT_SIZE = 12
MENU_FONT_SIZE = 12
BUTTON_FONT_SIZE = 11
BODY_FONT_SIZE = 9

def create_button(x: int, y: int, text: str, width: Optional[int] = None,
                  default: bool = False, disabled: bool = False, active: bool = False) -> str:
    """
    Create a Mac OS System button (rounded rectangle with text)

    Args:
        x, y: Position
        text: Button label
        width: Custom width (default 59px)
        default: Default button has thick border
        disabled: Grayed out text
        active: Inverted (pressed state)

    Returns:
        SVG string for button
    """
    w = width or BUTTON_WIDTH
    h = BUTTON_HEIGHT
    r = BUTTON_BORDER_RADIUS

    # Button states
    if active:
        fill = "#000"
        text_fill = "#FFF"
        stroke_width = 1
    else:
        fill = "#FFF"
        text_fill = "#000" if not disabled else "#808080"
        stroke_width = 3 if default else 1

    return f"""
  <!-- Button: {text} -->
  <g class="button">
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}"
          fill="{fill}" stroke="#000" stroke-width="{stroke_width}"/>
    <text x="{x + w//2}" y="{y + h//2 + 4}"
          font-family="monospace" font-size="{BUTTON_FONT_SIZE}"
          text-anchor="middle" fill="{text_fill}">{text}</text>
  </g>"""

def create_window(x: int, y: int, width: int, height: int, title: str,
                  active: bool = True, closable: bool = True,
                  content: Optional[str] = None, details_bar: Optional[str] = None) -> str:
    """
    Create a Mac OS System window with title bar

    Args:
        x, y: Position
        width, height: Dimensions (minimum height includes title bar)
        title: Window title text
        active: Active (black stripes) vs inactive (white stripes)
        closable: Show close box
        content: Inner content HTML/SVG
        details_bar: Details bar content (below title)

    Returns:
        SVG string for complete window
    """
    tb_height = TITLE_BAR_HEIGHT
    content_y = y + tb_height
    content_height = height - tb_height

    # Racing stripes pattern (title bar)
    stripes_color = "#000" if active else "#FFF"
    stripes = ""
    for i in range(5):
        stripe_x = x + 4 + (i * 2)
        stripes += f'<line x1="{stripe_x}" y1="{y + 3}" x2="{stripe_x}" y2="{y + tb_height - 3}" stroke="{stripes_color}" stroke-width="1"/>\n    '

    # Close box
    close_box = ""
    if closable:
        close_box = f"""
    <rect x="{x + 7}" y="{y + 5}" width="9" height="9" fill="#FFF" stroke="#000" stroke-width="1"/>
    <rect x="{x + 9}" y="{y + 7}" width="5" height="5" fill="#000"/>"""

    # Details bar
    details = ""
    if details_bar:
        details_y = content_y
        content_y += 14
        content_height -= 14
        details += f"""
    <rect x="{x + 1}" y="{details_y}" width="{width - 2}" height="14" fill="#FFF" stroke="none"/>
    <line x1="{x + 1}" y1="{details_y}" x2="{x + width - 1}" y2="{details_y}" stroke="#000" stroke-width="1"/>
    <text x="{x + 6}" y="{details_y + 10}" font-family="monospace" font-size="{BODY_FONT_SIZE}" fill="#000">{details_bar}</text>"""

    # Content pane
    content_pane = ""
    if content:
        content_pane = f"""
    <rect x="{x + 1}" y="{content_y}" width="{width - 2}" height="{content_height - 1}" fill="#FFF" stroke="none"/>
    <g transform="translate({x + 6}, {content_y + 6})">
      {content}
    </g>"""

    return f"""
  <!-- Window: {title} -->
  <g class="window">
    <!-- Window border -->
    <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#FFF" stroke="#000" stroke-width="{WINDOW_BORDER}"/>

    <!-- Title bar -->
    <rect x="{x + 1}" y="{y + 1}" width="{width - 2}" height="{tb_height - 1}" fill="#FFF" stroke="none"/>
    <line x1="{x + 1}" y1="{y + tb_height}" x2="{x + width - 1}" y2="{y + tb_height}" stroke="#000" stroke-width="1"/>

    <!-- Racing stripes -->
    {stripes}
    {close_box}

    <!-- Title text -->
    <text x="{x + width // 2}" y="{y + 14}"
          font-family="monospace" font-size="{TITLE_FONT_SIZE}" font-weight="bold"
          text-anchor="middle" fill="#000">{title}</text>
    {details}
    {content_pane}
  </g>"""

def create_dialog(x: int, y: int, width: int, height: int, title: str,
                  modal: bool = False, content: Optional[str] = None) -> str:
    """
    Create a Mac OS System dialog box

    Args:
        x, y: Position
        width, height: Dimensions
        title: Dialog title
        modal: Modal (double border) vs modeless (single border like window)
        content: Dialog content

    Returns:
        SVG string for dialog
    """
    if modal:
        # Modal dialog: double outline border
        border_offset = DIALOG_BORDER
        inner_x = x + border_offset
        inner_y = y + border_offset
        inner_width = width - (border_offset * 2)
        inner_height = height - (border_offset * 2)

        outer_border = f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="none" stroke="#000" stroke-width="{WINDOW_BORDER}"/>'

        return f"""
  <!-- Modal Dialog: {title} -->
  <g class="modal-dialog">
    <!-- Outer border -->
    {outer_border}

    <!-- Inner border and content -->
    <rect x="{inner_x}" y="{inner_y}" width="{inner_width}" height="{inner_height}" fill="#FFF" stroke="#000" stroke-width="{WINDOW_BORDER}"/>

    <!-- Title bar (simplified for dialog) -->
    <text x="{x + width // 2}" y="{y + 16}"
          font-family="monospace" font-size="{TITLE_FONT_SIZE}" font-weight="bold"
          text-anchor="middle" fill="#000">{title}</text>

    <line x1="{inner_x + 1}" y1="{inner_y + 20}" x2="{inner_x + inner_width - 1}" y2="{inner_y + 20}" stroke="#000" stroke-width="1"/>

    <!-- Content -->
    <g transform="translate({inner_x + 8}, {inner_y + 28})">
      {content or ''}
    </g>
  </g>"""
    else:
        # Modeless dialog: like a window without size/zoom boxes
        return create_window(x, y, width, height, title, active=True, closable=True, content=content)

def create_alert_box(x: int, y: int, width: int, message: str,
                     buttons: Optional[List[str]] = None, icon_space: bool = True) -> str:
    """
    Create a Mac OS System alert box (modal dialog with icon space and buttons)

    Args:
        x, y: Position
        width: Width (height auto-calculated)
        message: Alert message text
        buttons: List of button labels (default ["Cancel", "OK"])
        icon_space: Reserve space for alert icon (left side)

    Returns:
        SVG string for alert box
    """
    buttons = buttons or ["Cancel", "OK"]

    # Calculate dimensions
    icon_width = 40 if icon_space else 0
    text_width = width - icon_width - 40
    line_height = 12
    lines = message.split('\n')
    text_height = len(lines) * line_height + 10

    button_area_height = 40
    content_height = text_height + button_area_height
    total_height = content_height + 50  # Title + padding

    # Icon placeholder (empty square for icon)
    icon = ""
    if icon_space:
        icon = f'<rect x="10" y="0" width="32" height="32" fill="none" stroke="#000" stroke-width="1"/>'

    # Message text
    text_x = icon_width + 10
    text_lines = ""
    for i, line in enumerate(lines):
        text_y = 10 + (i * line_height)
        text_lines += f'<text x="{text_x}" y="{text_y}" font-family="monospace" font-size="{BODY_FONT_SIZE}" fill="#000">{line}</text>\n      '

    # Buttons (right-aligned)
    button_y = text_height
    button_spacing = 10
    total_button_width = sum(BUTTON_WIDTH for _ in buttons) + (len(buttons) - 1) * button_spacing
    button_x = width - total_button_width - 50

    buttons_svg = ""
    for i, btn_text in enumerate(buttons):
        is_default = (i == len(buttons) - 1)  # Last button is default
        buttons_svg += create_button(button_x, button_y, btn_text, default=is_default)
        button_x += BUTTON_WIDTH + button_spacing

    content = f"""
      {icon}
      {text_lines}
      {buttons_svg}
    """

    return create_dialog(x, y, width, total_height, "Alert", modal=True, content=content)

def create_checkbox(x: int, y: int, label: str, checked: bool = False) -> str:
    """Create a Mac OS System checkbox"""
    check_mark = ""
    if checked:
        check_mark = f"""
    <line x1="{x + 2}" y1="{y + 6}" x2="{x + 5}" y2="{y + 9}" stroke="#000" stroke-width="2"/>
    <line x1="{x + 5}" y1="{y + 9}" x2="{x + 10}" y2="{y + 2}" stroke="#000" stroke-width="2"/>"""

    return f"""
  <!-- Checkbox: {label} -->
  <g class="checkbox">
    <rect x="{x}" y="{y}" width="12" height="12" fill="#FFF" stroke="#000" stroke-width="1"/>
    {check_mark}
    <text x="{x + 16}" y="{y + 9}" font-family="monospace" font-size="{BODY_FONT_SIZE}" fill="#000">{label}</text>
  </g>"""

def create_radio_button(x: int, y: int, label: str, selected: bool = False) -> str:
    """Create a Mac OS System radio button"""
    inner_circle = ""
    if selected:
        inner_circle = f'<circle cx="{x + 6}" cy="{y + 6}" r="4" fill="#000"/>'

    return f"""
  <!-- Radio: {label} -->
  <g class="radio">
    <circle cx="{x + 6}" cy="{y + 6}" r="6" fill="#FFF" stroke="#000" stroke-width="1"/>
    {inner_circle}
    <text x="{x + 16}" y="{y + 9}" font-family="monospace" font-size="{BODY_FONT_SIZE}" fill="#000">{label}</text>
  </g>"""

def create_text_box(x: int, y: int, width: int, placeholder: str = "", value: str = "") -> str:
    """Create a Mac OS System text input box"""
    display_text = value or placeholder
    text_color = "#000" if value else "#808080"

    return f"""
  <!-- Text Box -->
  <g class="text-box">
    <rect x="{x}" y="{y}" width="{width}" height="16" fill="#FFF" stroke="#000" stroke-width="1"/>
    <text x="{x + 4}" y="{y + 11}" font-family="monospace" font-size="{BODY_FONT_SIZE}" fill="{text_color}">{display_text}</text>
  </g>"""

def create_menu_bar(x: int, y: int, width: int, items: List[str]) -> str:
    """Create a Mac OS System menu bar"""
    menu_bar_height = 20

    menu_items = ""
    item_x = x + 8
    for item in items:
        menu_items += f"""
    <text x="{item_x}" y="{y + 14}" font-family="monospace" font-size="{MENU_FONT_SIZE}" font-weight="bold" fill="#000">{item}</text>"""
        item_x += len(item) * 8 + 16

    return f"""
  <!-- Menu Bar -->
  <g class="menu-bar">
    <rect x="{x}" y="{y}" width="{width}" height="{menu_bar_height}" fill="#FFF" stroke="#000" stroke-width="1"/>
    {menu_items}
  </g>"""


# Example usage
if __name__ == "__main__":
    print("🖥️  Mac OS System UI Components Library - SVG Edition")
    print("\nAvailable components:")
    print("  • create_button() - Standard, default, disabled, active states")
    print("  • create_window() - Windows with title bars, close boxes, details bars")
    print("  • create_dialog() - Modal and modeless dialogs")
    print("  • create_alert_box() - Alert boxes with icon space and buttons")
    print("  • create_checkbox() - Checkboxes with labels")
    print("  • create_radio_button() - Radio buttons with labels")
    print("  • create_text_box() - Text input boxes")
    print("  • create_menu_bar() - Menu bars with items")
    print("\nBased on system.css and Apple HI Guidelines (1984-1991)")
    print("Use in SVG diagrams for authentic Mac OS System look!")
