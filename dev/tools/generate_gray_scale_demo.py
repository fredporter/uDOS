#!/usr/bin/env python3
"""
Demonstrate solid grays + bitmap patterns in Mac OS style
Generates example showing both approaches
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from diagram_templates import PATTERN_DEFS, save_diagram

output_path = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'fire'

# Generate gradient comparison diagram
svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
{PATTERN_DEFS}

  <!-- Title -->
  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">GRAYSCALE TECHNIQUES - MAC OS STYLE</text>

  <text x="400" y="50" font-family="monospace" font-size="12"
        text-anchor="middle" fill="#000">Solid grays for gradients • Bitmap patterns for texture</text>

  <!-- Solid Gray Gradient -->
  <text x="150" y="90" font-family="monospace" font-size="14" font-weight="bold"
        text-anchor="middle" fill="#000">SOLID GRAYS (Smooth)</text>

  <rect x="50" y="100" width="40" height="40" fill="#000" stroke="#000" stroke-width="1"/>
  <text x="70" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">#000</text>

  <rect x="90" y="100" width="40" height="40" fill="#1A1A1A" stroke="#000" stroke-width="1"/>
  <text x="110" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">90%</text>

  <rect x="130" y="100" width="40" height="40" fill="#333333" stroke="#000" stroke-width="1"/>
  <text x="150" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">80%</text>

  <rect x="170" y="100" width="40" height="40" fill="#4D4D4D" stroke="#000" stroke-width="1"/>
  <text x="190" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">70%</text>

  <rect x="210" y="100" width="40" height="40" fill="#666666" stroke="#000" stroke-width="1"/>
  <text x="230" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">60%</text>

  <!-- Bitmap Pattern Gradient -->
  <text x="550" y="90" font-family="monospace" font-size="14" font-weight="bold"
        text-anchor="middle" fill="#000">BITMAP PATTERNS (Texture)</text>

  <rect x="450" y="100" width="40" height="40" fill="#000" stroke="#000" stroke-width="1"/>
  <text x="470" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">black</text>

  <rect x="490" y="100" width="40" height="40" fill="url(#gray-87)" stroke="#000" stroke-width="1"/>
  <text x="510" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">87%</text>

  <rect x="530" y="100" width="40" height="40" fill="url(#gray-75)" stroke="#000" stroke-width="1"/>
  <text x="550" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">75%</text>

  <rect x="570" y="100" width="40" height="40" fill="url(#gray-62)" stroke="#000" stroke-width="1"/>
  <text x="590" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">62%</text>

  <rect x="610" y="100" width="40" height="40" fill="url(#gray-50)" stroke="#000" stroke-width="1"/>
  <text x="630" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">50%</text>

  <rect x="650" y="100" width="40" height="40" fill="url(#gray-37)" stroke="#000" stroke-width="1"/>
  <text x="670" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">37%</text>

  <rect x="690" y="100" width="40" height="40" fill="url(#gray-25)" stroke="#000" stroke-width="1"/>
  <text x="710" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">25%</text>

  <rect x="730" y="100" width="40" height="40" fill="url(#gray-12)" stroke="#000" stroke-width="1"/>
  <text x="750" y="150" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">12%</text>

  <!-- Combined Example: Fire Layering -->
  <text x="400" y="200" font-family="monospace" font-size="14" font-weight="bold"
        text-anchor="middle" fill="#000">COMBINED APPROACH - Fire Layers</text>

  <!-- Flame shape with solid gray gradient -->
  <path d="M 350 450 Q 350 350, 380 300 Q 390 320, 400 250 Q 410 320, 420 300 Q 450 350, 450 450 Z"
        fill="#333333" stroke="#000" stroke-width="2"/>
  <text x="400" y="470" font-family="monospace" font-size="10"
        text-anchor="middle" fill="#FFF">Outer flame (solid #333)</text>

  <!-- Inner flame with lighter solid -->
  <path d="M 370 440 Q 370 380, 390 330 Q 395 350, 400 290 Q 405 350, 410 330 Q 430 380, 430 440 Z"
        fill="#808080" stroke="#000" stroke-width="2"/>
  <text x="400" y="455" font-family="monospace" font-size="10"
        text-anchor="middle" fill="#000">Mid flame (solid #808)</text>

  <!-- Hot core with pattern -->
  <path d="M 385 430 Q 385 400, 395 360 Q 398 375, 400 330 Q 402 375, 405 360 Q 415 400, 415 430 Z"
        fill="url(#dots)" stroke="#000" stroke-width="2"/>
  <text x="400" y="440" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">Core (dots pattern)</text>

  <!-- Fuel/wood base with pattern -->
  <rect x="360" y="450" width="80" height="20" fill="url(#horizontal)"
        stroke="#000" stroke-width="2"/>
  <text x="400" y="485" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">Wood fuel (horizontal pattern)</text>

  <!-- Usage guide -->
  <text x="50" y="230" font-family="monospace" font-size="12" font-weight="bold" fill="#000">WHEN TO USE:</text>

  <text x="50" y="250" font-family="monospace" font-size="10" fill="#000">✓ Solid grays:</text>
  <text x="60" y="265" font-family="monospace" font-size="9" fill="#333">• Smooth gradients (fire, shadows)</text>
  <text x="60" y="278" font-family="monospace" font-size="9" fill="#333">• Depth/distance effects</text>
  <text x="60" y="291" font-family="monospace" font-size="9" fill="#333">• Atmospheric perspective</text>
  <text x="60" y="304" font-family="monospace" font-size="9" fill="#333">• Subtle shading</text>

  <text x="50" y="330" font-family="monospace" font-size="10" fill="#000">✓ Bitmap patterns:</text>
  <text x="60" y="345" font-family="monospace" font-size="9" fill="#333">• Material textures (wood, metal)</text>
  <text x="60" y="358" font-family="monospace" font-size="9" fill="#333">• Structural fills (barriers)</text>
  <text x="60" y="371" font-family="monospace" font-size="9" fill="#333">• Technical diagrams</text>
  <text x="60" y="384" font-family="monospace" font-size="9" fill="#333">• Classic Mac OS aesthetic</text>

  <text x="50" y="410" font-family="monospace" font-size="10" fill="#000">✓ Combined:</text>
  <text x="60" y="425" font-family="monospace" font-size="9" fill="#333">• Layer solid gradients with patterns</text>
  <text x="60" y="438" font-family="monospace" font-size="9" fill="#333">• Create depth and detail together</text>

</svg>"""

save_diagram(svg, output_path / 'grayscale-techniques-demo.svg')

print("\n✅ Grayscale techniques demo created!")
print("   Shows solid grays + bitmap patterns")
print("   Fire example combines both approaches")
