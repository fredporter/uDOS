#!/usr/bin/env python3
"""
Generate navigation diagrams for survival scenarios
Focus: Compass use, celestial navigation, terrain features
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from diagram_templates import generate_from_template, save_diagram, PATTERN_DEFS
from macos_ui_components import create_window, create_button, create_checkbox

output_path = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'navigation'
output_path.mkdir(exist_ok=True)

# 1. Compass basics
compass_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
{PATTERN_DEFS}

  <title>Compass Basics</title>
  <desc>Basic compass orientation and cardinal directions</desc>

  <text x="300" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">COMPASS BASICS</text>

  <!-- Compass circle -->
  <circle cx="300" cy="300" r="180" fill="#FFF" stroke="#000" stroke-width="3"/>
  <circle cx="300" cy="300" r="175" fill="none" stroke="#000" stroke-width="1"/>

  <!-- Cardinal directions -->
  <text x="300" y="140" font-family="monospace" font-size="24" font-weight="bold"
        text-anchor="middle" fill="#000">N</text>
  <text x="300" y="475" font-family="monospace" font-size="24" font-weight="bold"
        text-anchor="middle" fill="#000">S</text>
  <text x="470" y="310" font-family="monospace" font-size="24" font-weight="bold"
        text-anchor="middle" fill="#000">E</text>
  <text x="130" y="310" font-family="monospace" font-size="24" font-weight="bold"
        text-anchor="middle" fill="#000">W</text>

  <!-- Degree markings -->
  <text x="300" y="155" font-family="monospace" font-size="10"
        text-anchor="middle" fill="#666">0°/360°</text>
  <text x="445" y="310" font-family="monospace" font-size="10"
        text-anchor="middle" fill="#666">90°</text>
  <text x="300" y="460" font-family="monospace" font-size="10"
        text-anchor="middle" fill="#666">180°</text>
  <text x="155" y="310" font-family="monospace" font-size="10"
        text-anchor="middle" fill="#666">270°</text>

  <!-- Magnetic needle -->
  <polygon points="300,180 310,300 300,320 290,300" fill="#000" stroke="#000" stroke-width="2"/>
  <polygon points="300,320 310,300 300,420 290,300" fill="#FFF" stroke="#000" stroke-width="2"/>
  <circle cx="300" cy="300" r="8" fill="#000"/>

  <!-- Labels -->
  <text x="340" y="190" font-family="monospace" font-size="9" fill="#000">North-seeking</text>
  <text x="340" y="200" font-family="monospace" font-size="9" fill="#000">(Red/Black)</text>
  <text x="340" y="430" font-family="monospace" font-size="9" fill="#000">South-seeking</text>
  <text x="340" y="440" font-family="monospace" font-size="9" fill="#000">(White)</text>

  <!-- Instructions -->
  <rect x="20" y="510" width="560" height="80" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="30" y="530" font-family="monospace" font-size="10" font-weight="bold" fill="#000">HOW TO USE:</text>
  <text x="40" y="545" font-family="monospace" font-size="9" fill="#000">1. Hold compass flat and level</text>
  <text x="40" y="558" font-family="monospace" font-size="9" fill="#000">2. Rotate body until needle aligns with N (red to north)</text>
  <text x="40" y="571" font-family="monospace" font-size="9" fill="#000">3. Read bearing at direction of travel arrow</text>
  <text x="40" y="584" font-family="monospace" font-size="9" fill="#000">4. Adjust for magnetic declination (varies by location)</text>

</svg>"""
save_diagram(compass_svg, output_path / 'compass-basics.svg')

# 2. Shadow stick method
shadow_stick = generate_from_template(
    '4-step-process',
    title='Shadow Stick Navigation',
    description='Find east-west line using sun and shadows (Northern Hemisphere)',
    step1_title='PLACE STICK',
    step1_desc='Vertical stick in\nground, mark\nshadow tip',
    step2_title='WAIT 15 MIN',
    step2_desc='Shadow moves,\nmark new\ntip position',
    step3_title='DRAW LINE',
    step3_desc='Connect marks\n= East-West\nline',
    step4_title='FIND NORTH',
    step4_desc='Stand on line,\nface sun,\nN is right'
)
save_diagram(shadow_stick, output_path / 'shadow-stick-method.svg')

# 3. North Star (Polaris) finding
north_star_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 600" width="700" height="600">
{PATTERN_DEFS}

  <title>Finding Polaris (North Star)</title>
  <desc>Use Big Dipper to locate Polaris for north direction</desc>

  <text x="350" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">FINDING POLARIS (NORTH STAR)</text>
  <text x="350" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Northern Hemisphere only</text>

  <!-- Night sky background -->
  <rect x="50" y="80" width="600" height="400" fill="#1A1A1A" stroke="#000" stroke-width="2"/>

  <!-- Big Dipper -->
  <circle cx="150" cy="300" r="5" fill="#FFF"/>
  <circle cx="200" cy="280" r="5" fill="#FFF"/>
  <circle cx="250" cy="270" r="5" fill="#FFF"/>
  <circle cx="300" cy="260" r="5" fill="#FFF"/>
  <circle cx="280" cy="320" r="5" fill="#FFF"/>
  <circle cx="230" cy="330" r="5" fill="#FFF"/>
  <circle cx="180" cy="340" r="5" fill="#FFF"/>

  <line x1="150" y1="300" x2="200" y2="280" stroke="#666" stroke-width="1" stroke-dasharray="2,2"/>
  <line x1="200" y1="280" x2="250" y2="270" stroke="#666" stroke-width="1" stroke-dasharray="2,2"/>
  <line x1="250" y1="270" x2="300" y2="260" stroke="#666" stroke-width="1" stroke-dasharray="2,2"/>
  <line x1="300" y1="260" x2="280" y2="320" stroke="#666" stroke-width="1" stroke-dasharray="2,2"/>
  <line x1="280" y1="320" x2="230" y2="330" stroke="#666" stroke-width="1" stroke-dasharray="2,2"/>
  <line x1="230" y1="330" x2="180" y2="340" stroke="#666" stroke-width="1" stroke-dasharray="2,2"/>
  <line x1="180" y1="340" x2="150" y2="300" stroke="#666" stroke-width="1" stroke-dasharray="2,2"/>

  <text x="220" y="370" font-family="monospace" font-size="11" fill="#FFF">BIG DIPPER</text>

  <!-- Pointer stars highlighted -->
  <circle cx="300" cy="260" r="8" fill="none" stroke="#FFF" stroke-width="2"/>
  <circle cx="280" cy="320" r="8" fill="none" stroke="#FFF" stroke-width="2"/>
  <text x="320" y="265" font-family="monospace" font-size="9" fill="#FFF">Pointer</text>
  <text x="320" y="325" font-family="monospace" font-size="9" fill="#FFF">Stars</text>

  <!-- Arrow to Polaris -->
  <line x1="290" y1="290" x2="480" y2="150" stroke="#FFF" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrowhead)"/>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#FFF"/>
    </marker>
  </defs>
  <text x="380" y="215" font-family="monospace" font-size="9" fill="#FFF">5x distance</text>
  <text x="380" y="227" font-family="monospace" font-size="9" fill="#FFF">between pointers</text>

  <!-- Polaris -->
  <circle cx="500" cy="140" r="8" fill="#FFF"/>
  <circle cx="500" cy="140" r="12" fill="none" stroke="#FFF" stroke-width="1"/>
  <circle cx="500" cy="140" r="16" fill="none" stroke="#FFF" stroke-width="1"/>
  <text x="520" y="145" font-family="monospace" font-size="12" font-weight="bold" fill="#FFF">POLARIS</text>
  <text x="520" y="158" font-family="monospace" font-size="9" fill="#FFF">(North Star)</text>

  <!-- Horizon line -->
  <line x1="50" y1="450" x2="650" y2="450" stroke="#FFF" stroke-width="2"/>
  <text x="60" y="470" font-family="monospace" font-size="9" fill="#000">Horizon</text>

  <!-- Instructions -->
  <rect x="50" y="500" width="600" height="85" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="60" y="520" font-family="monospace" font-size="10" font-weight="bold" fill="#000">METHOD:</text>
  <text x="70" y="535" font-family="monospace" font-size="9" fill="#000">1. Locate Big Dipper (7 bright stars in cup/handle pattern)</text>
  <text x="70" y="548" font-family="monospace" font-size="9" fill="#000">2. Find 2 pointer stars on front edge of cup</text>
  <text x="70" y="561" font-family="monospace" font-size="9" fill="#000">3. Draw imaginary line through pointers, extend 5x their separation</text>
  <text x="70" y="574" font-family="monospace" font-size="9" fill="#000">4. Polaris = bright star at end of line = TRUE NORTH direction</text>

</svg>"""
save_diagram(north_star_svg, output_path / 'north-star-polaris.svg')

# 4. Terrain association
terrain_svg = generate_from_template(
    'triangle-3-elements',
    title='Terrain Association',
    description='Navigate by matching visible terrain to map features',
    element1_label='RIDGELINES',
    element1_pattern='diagonal',
    element2_label='WATER FLOW',
    element2_pattern='waves',
    element3_label='PEAKS',
    element3_pattern='dots',
    center_label='LOCATION'
)
save_diagram(terrain_svg, output_path / 'terrain-association.svg')

# 5. Handrail navigation
handrail_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 500" width="700" height="500">
{PATTERN_DEFS}

  <title>Handrail Navigation</title>
  <desc>Follow linear features to maintain direction</desc>

  <text x="350" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">HANDRAIL NAVIGATION</text>
  <text x="350" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Follow linear features to stay on course</text>

  <!-- Terrain -->
  <rect x="50" y="80" width="600" height="340" fill="url(#gray-12)" stroke="#000" stroke-width="2"/>

  <!-- Start point -->
  <circle cx="100" cy="380" r="15" fill="#000" stroke="#FFF" stroke-width="2"/>
  <text x="100" y="386" font-family="monospace" font-size="10" font-weight="bold"
        text-anchor="middle" fill="#FFF">START</text>

  <!-- End point -->
  <circle cx="600" cy="120" r="15" fill="#000" stroke="#FFF" stroke-width="2"/>
  <text x="600" y="126" font-family="monospace" font-size="10" font-weight="bold"
        text-anchor="middle" fill="#FFF">END</text>

  <!-- River (handrail) -->
  <path d="M 120 370 Q 200 350, 250 300 T 350 220 T 450 160 T 580 130"
        fill="none" stroke="#000" stroke-width="4"/>
  <path d="M 120 370 Q 200 350, 250 300 T 350 220 T 450 160 T 580 130"
        fill="none" stroke="url(#waves)" stroke-width="20" opacity="0.5"/>
  <text x="280" y="270" font-family="monospace" font-size="11" font-weight="bold" fill="#000">RIVER</text>

  <!-- Walking path (following river) -->
  <path d="M 100 380 Q 190 358, 240 310 T 340 235 T 440 175 T 600 120"
        fill="none" stroke="#000" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- Arrow markers -->
  <polygon points="180,365 190,363 185,355" fill="#000"/>
  <polygon points="280,290 290,285 283,278" fill="#000"/>
  <polygon points="380,220 390,213 382,207" fill="#000"/>
  <polygon points="480,165 490,158 482,152" fill="#000"/>

  <!-- Instructions -->
  <rect x="50" y="440" width="600" height="50" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="60" y="460" font-family="monospace" font-size="10" font-weight="bold" fill="#000">HANDRAIL FEATURES:</text>
  <text x="70" y="475" font-family="monospace" font-size="9" fill="#000">Rivers • Ridgelines • Roads • Fences • Coastlines • Power lines • Valleys</text>
  <text x="200" y="460" font-family="monospace" font-size="9" fill="#666">→ Follow parallel to feature, staying within sight/sound</text>

</svg>"""
save_diagram(handrail_svg, output_path / 'handrail-navigation.svg')

print("\n✅ Navigation diagrams generated!")
print("\n📊 Created 5 diagrams:")
print("   • compass-basics.svg - Cardinal directions and degree markings")
print("   • shadow-stick-method.svg - Solar navigation technique")
print("   • north-star-polaris.svg - Celestial navigation (Big Dipper)")
print("   • terrain-association.svg - Map-to-ground orientation")
print("   • handrail-navigation.svg - Following linear features")
print("\n🎯 Navigation category: 0 → 5 diagrams")
