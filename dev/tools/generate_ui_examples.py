#!/usr/bin/env python3
"""
Example: Using Mac OS UI components in survival diagrams
Shows how to integrate system.css UI elements into instructional diagrams
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from macos_ui_components import create_window, create_button, create_checkbox, create_alert_box
from diagram_templates import save_diagram

output_path = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'water'

# Water purification decision tree using UI elements
svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 700" width="800" height="700">

  <title>Water Purification Decision System</title>
  <desc>Interactive-style water purification flowchart using Mac OS UI elements</desc>

  <!-- Title -->
  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">WATER PURIFICATION - DECISION SYSTEM</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#000">Mac OS System interface for survival procedures</text>

""" + create_window(
    50, 80, 700, 180, "Water Source Assessment",
    active=True,
    closable=True,
    details_bar="Step 1 of 4 • Source Evaluation",
    content="""
      <text x="0" y="15" font-family="monospace" font-size="11" font-weight="bold" fill="#000">What type of water source?</text>
      """ + create_checkbox(0, 30, "Clear running stream") + \
            create_checkbox(0, 50, "Standing water (pond/lake)") + \
            create_checkbox(0, 70, "Questionable source (muddy/stagnant)") + \
            create_checkbox(0, 90, "Potentially contaminated") + \
            create_button(450, 90, "Cancel") + \
            create_button(520, 90, "Next", default=True)
) + """

""" + create_window(
    50, 280, 340, 200, "Filtration Methods",
    active=True,
    closable=True,
    details_bar="Step 2 • Physical Filtration",
    content="""
      <text x="0" y="15" font-family="monospace" font-size="10" fill="#000">Select filtration layers:</text>
      """ + create_checkbox(0, 35, "Cloth (remove debris)", checked=True) + \
            create_checkbox(0, 55, "Sand (fine particles)", checked=True) + \
            create_checkbox(0, 75, "Charcoal (chemicals)", checked=True) + \
            create_checkbox(0, 95, "Gravel (coarse filter)") + \
            create_button(130, 125, "Back") + \
            create_button(200, 125, "Next", default=True)
) + create_window(
    410, 280, 340, 200, "Purification Methods",
    active=True,
    closable=True,
    details_bar="Step 3 • Kill Pathogens",
    content="""
      <text x="0" y="15" font-family="monospace" font-size="10" fill="#000">Select treatment method:</text>
      """ + create_checkbox(0, 35, "Boil 1 min (most reliable)", checked=True) + \
            create_checkbox(0, 55, "Iodine tablets (chemical)") + \
            create_checkbox(0, 75, "UV light (if available)") + \
            create_checkbox(0, 95, "Solar disinfection (6hrs)") + \
            create_button(130, 125, "Back") + \
            create_button(200, 125, "Next", default=True)
) + """

""" + create_alert_box(
    50, 500, 700,
    "WARNING: Boiling is recommended for 1 minute at low\\naltitudes, 3 minutes above 6,500 feet (2,000m).\\nAlways filter visible debris first.",
    buttons=["Skip", "Understood"],
    icon_space=True
) + """

  <!-- Footer instructions -->
  <rect x="50" y="650" width="700" height="40" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="60" y="670" font-family="monospace" font-size="9" fill="#000">💡 TIP: Combine methods for maximum safety. Filter first, then purify.</text>
  <text x="60" y="682" font-family="monospace" font-size="9" fill="#000">🎯 GOAL: Remove particles (filter) + kill pathogens (purify) = safe drinking water</text>

</svg>"""

save_diagram(svg, output_path / 'purification-decision-ui.svg')

# Emergency shelter setup using dialog boxes
shelter_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">

  <title>Emergency Shelter Setup Checklist</title>
  <desc>Shelter building checklist using Mac OS dialog interface</desc>

  <!-- Title -->
  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">EMERGENCY SHELTER - SETUP CHECKLIST</text>

""" + create_window(
    50, 60, 700, 250, "Shelter Location Checklist",
    active=True,
    closable=True,
    details_bar="Priority: Location is 60% of shelter success",
    content="""
      <text x="0" y="15" font-family="monospace" font-size="11" font-weight="bold" fill="#000">CRITICAL - Check ALL before building:</text>
      """ + create_checkbox(10, 35, "High ground (avoid flash floods)", checked=True) + \
            create_checkbox(10, 55, "Near water source (but not too close)", checked=True) + \
            create_checkbox(10, 75, "Wind protection (natural windbreak)", checked=False) + \
            create_checkbox(10, 95, "No dead trees overhead (widowmakers)") + \
            create_checkbox(10, 115, "Flat, dry ground for sleeping") + \
            create_checkbox(10, 135, "Materials available nearby") + \
            create_checkbox(350, 35, "Not in animal trails/dens") + \
            create_checkbox(350, 55, "Reasonable sun exposure") + \
            create_checkbox(350, 75, "Drainage away from site") + \
            create_button(450, 165, "Reset") + \
            create_button(520, 165, "Continue", default=True)
) + """

""" + create_window(
    50, 330, 340, 160, "Build Priority",
    active=True,
    closable=False,
    content="""
      <text x="0" y="15" font-family="monospace" font-size="10" font-weight="bold" fill="#000">Build in this order:</text>
      <text x="10" y="35" font-family="monospace" font-size="9" fill="#000">1. Ground insulation (6in debris)</text>
      <text x="10" y="50" font-family="monospace" font-size="9" fill="#000">2. Framework (ridgepole + ribs)</text>
      <text x="10" y="65" font-family="monospace" font-size="9" fill="#000">3. Thatching (thick, shingled)</text>
      <text x="10" y="80" font-family="monospace" font-size="9" fill="#000">4. Windbreak at entrance</text>
      <text x="10" y="95" font-family="monospace" font-size="9" fill="#000">5. Drainage trench (if rain)</text>
      """ + create_button(165, 105, "OK", default=True)
) + create_alert_box(
    410, 330, 340,
    "RULE OF THREES\\n3 hours without shelter (cold)\\n3 days without water\\n3 weeks without food",
    buttons=["Got it"],
    icon_space=True
) + """

</svg>"""

save_diagram(shelter_svg, Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'shelter' / 'setup-checklist-ui.svg')

print("\n✅ UI component integration examples created!")
print("\n📊 Generated diagrams:")
print("   • water/purification-decision-ui.svg - Water purification flowchart")
print("   • shelter/setup-checklist-ui.svg - Shelter building checklist")
print("\n🎨 Demonstrates:")
print("   • Windows with title bars and details")
print("   • Checkboxes for multi-step procedures")
print("   • Buttons for navigation/actions")
print("   • Alert boxes for warnings")
print("   • Mac OS System aesthetic in survival context")
