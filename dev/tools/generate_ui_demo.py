#!/usr/bin/env python3
"""
Demo: Mac OS System UI Components in SVG
Showcases all UI elements from system.css in diagram form
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from macos_ui_components import (
    create_button, create_window, create_dialog, create_alert_box,
    create_checkbox, create_radio_button, create_text_box, create_menu_bar
)
from diagram_templates import save_diagram

output_path = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'system'
output_path.mkdir(exist_ok=True)

# Demo SVG showcasing all UI components
svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1200" width="900" height="1200">

  <!-- Title -->
  <text x="450" y="30" font-family="monospace" font-size="24" font-weight="bold"
        text-anchor="middle" fill="#000">Mac OS System UI Components</text>
  <text x="450" y="50" font-family="monospace" font-size="12"
        text-anchor="middle" fill="#000">Based on system.css and Apple HI Guidelines (1984-1991)</text>

  <line x1="50" y1="60" x2="850" y2="60" stroke="#000" stroke-width="1"/>

  <!-- SECTION 1: Buttons -->
  <text x="50" y="85" font-family="monospace" font-size="16" font-weight="bold" fill="#000">Buttons</text>

""" + create_button(50, 95, "Submit") + \
      create_button(120, 95, "Cancel") + \
      create_button(190, 95, "Active", active=True) + \
      create_button(260, 95, "Disabled", disabled=True) + \
      create_button(340, 95, "Find", default=True) + \
      create_button(420, 95, "Long Button Text", width=140) + """

  <!-- SECTION 2: Form Elements -->
  <text x="50" y="145" font-family="monospace" font-size="16" font-weight="bold" fill="#000">Form Elements</text>

""" + create_checkbox(50, 155, "Enable feature", checked=True) + \
      create_checkbox(50, 175, "Disabled option") + \
      create_radio_button(200, 155, "Option A", selected=True) + \
      create_radio_button(200, 175, "Option B") + \
      create_text_box(350, 155, 200, placeholder="Enter text...") + \
      create_text_box(350, 180, 200, value="User input here") + """

  <!-- SECTION 3: Menu Bar -->
  <text x="50" y="225" font-family="monospace" font-size="16" font-weight="bold" fill="#000">Menu Bar</text>

""" + create_menu_bar(50, 235, 500, ["File", "Edit", "View", "Special"]) + """

  <!-- SECTION 4: Windows -->
  <text x="50" y="285" font-family="monospace" font-size="16" font-weight="bold" fill="#000">Windows</text>

""" + create_window(
    50, 295, 300, 150, "Active Window",
    active=True,
    closable=True,
    content="""<text x="0" y="15" font-family="monospace" font-size="9" fill="#000">This is window content.</text>
      <text x="0" y="30" font-family="monospace" font-size="9" fill="#000">Windows can contain text,</text>
      <text x="0" y="45" font-family="monospace" font-size="9" fill="#000">form elements, and more.</text>"""
) + create_window(
    400, 295, 300, 150, "With Details Bar",
    active=True,
    closable=True,
    details_bar="details • more • info",
    content="""<text x="0" y="15" font-family="monospace" font-size="9" fill="#000">Content below details bar</text>"""
) + """

""" + create_window(
    50, 465, 250, 120, "Inactive Window",
    active=False,
    closable=True,
    content="""<text x="0" y="15" font-family="monospace" font-size="9" fill="#808080">Inactive window state</text>"""
) + """

  <!-- SECTION 5: Dialogs -->
  <text x="50" y="615" font-family="monospace" font-size="16" font-weight="bold" fill="#000">Dialogs</text>

""" + create_dialog(
    50, 625, 320, 140, "Modeless Dialog",
    modal=False,
    content="""<text x="0" y="15" font-family="monospace" font-size="9" fill="#000">Find:</text>
      """ + create_text_box(0, 25, 220, placeholder="Search term") + \
      create_button(230, 25, "Find", default=True) + \
      create_button(165, 25, "Cancel")
) + create_dialog(
    420, 625, 350, 180, "Modal Dialog",
    modal=True,
    content="""<text x="0" y="15" font-family="monospace" font-size="9" fill="#000">Modal dialogs have double borders</text>
      <text x="0" y="30" font-family="monospace" font-size="9" fill="#000">and require user interaction.</text>
      """ + create_checkbox(0, 50, "Don't show this again") + \
      create_button(190, 90, "Cancel") + \
      create_button(260, 90, "OK", default=True)
) + """

  <!-- SECTION 6: Alert Boxes -->
  <text x="50" y="835" font-family="monospace" font-size="16" font-weight="bold" fill="#000">Alert Boxes</text>

""" + create_alert_box(
    50, 845, 400,
    "This is a standard alert box.\\nThe text would be placed here.\\nThis is where more text appears.",
    buttons=["Cancel", "OK"],
    icon_space=True
) + create_alert_box(
    480, 845, 360,
    "Are you sure you want to delete\\nthis item? This action cannot\\nbe undone.",
    buttons=["No", "Yes"],
    icon_space=True
) + """

  <!-- SECTION 7: Standard Dialog Example -->
  <text x="50" y="1015" font-family="monospace" font-size="16" font-weight="bold" fill="#000">Standard Dialog</text>

""" + create_dialog(
    50, 1025, 400, 150, "The Macintosh Finder, Version 1.0 (18 Jan 84)",
    modal=False,
    content="""<text x="120" y="35" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">© 1984 Apple Computer</text>"""
) + """

  <!-- Footer -->
  <line x1="50" y1="1190" x2="850" y2="1190" stroke="#000" stroke-width="1"/>
  <text x="450" y="1210" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">All components pixel-perfect SVG • Monochrome only • Generic monospace fonts</text>

</svg>"""

save_diagram(svg, output_path / 'ui-components-demo.svg')

print("\n✅ Mac OS System UI components demo created!")
print("   Location: knowledge/diagrams/system/ui-components-demo.svg")
print("\n📋 Components demonstrated:")
print("   • Buttons (standard, default, active, disabled)")
print("   • Checkboxes and radio buttons")
print("   • Text input boxes")
print("   • Menu bars")
print("   • Windows (active, inactive, with details)")
print("   • Dialogs (modal, modeless)")
print("   • Alert boxes")
print("\n🎨 Ready to use in survival/technical diagrams!")
