#!/usr/bin/env python3
"""
Generate example diagrams using Mac OS System 1 patterns
Demonstrates the pattern library with practical survival/medical diagrams
"""

from pathlib import Path

# Example 1: Tourniquet Application
tourniquet_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <title>Tourniquet Application - 4 Steps</title>
  <desc>Step-by-step guide for applying an improvised tourniquet to control severe bleeding</desc>

  <defs>
    <!-- Mac OS System 1 Patterns -->
    <pattern id="gray-25" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#FFF"/>
      <rect x="0" y="0" width="2" height="2" fill="#000"/>
      <rect x="2" y="2" width="2" height="2" fill="#000"/>
    </pattern>

    <pattern id="gray-50" patternUnits="userSpaceOnUse" width="2" height="2">
      <rect width="2" height="2" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="1" y="1" width="1" height="1" fill="#000"/>
    </pattern>

    <pattern id="gray-75" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#000"/>
      <rect x="0" y="0" width="2" height="2" fill="#FFF"/>
      <rect x="2" y="2" width="2" height="2" fill="#FFF"/>
    </pattern>

    <pattern id="dots" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="2" y="2" width="1" height="1" fill="#000"/>
    </pattern>

    <pattern id="herringbone" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="1" y="1" width="1" height="1" fill="#000"/>
      <rect x="2" y="2" width="1" height="1" fill="#000"/>
      <rect x="3" y="3" width="1" height="1" fill="#000"/>
      <rect x="7" y="0" width="1" height="1" fill="#000"/>
      <rect x="6" y="1" width="1" height="1" fill="#000"/>
      <rect x="5" y="2" width="1" height="1" fill="#000"/>
      <rect x="4" y="3" width="1" height="1" fill="#000"/>
    </pattern>
  </defs>

  <!-- Title -->
  <text x="400" y="40" font-family="monospace" font-size="24" font-weight="bold" text-anchor="middle" fill="#000">
    TOURNIQUET APPLICATION
  </text>

  <!-- Step 1: Position -->
  <g id="step1">
    <rect x="50" y="80" width="150" height="200" fill="none" stroke="#000" stroke-width="2"/>
    <text x="125" y="100" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">1. POSITION</text>

    <!-- Arm with wound -->
    <ellipse cx="125" cy="180" rx="25" ry="80" fill="url(#dots)" stroke="#000" stroke-width="2"/>
    <!-- Wound location -->
    <rect x="100" y="220" width="50" height="15" fill="url(#gray-75)" stroke="#000" stroke-width="2"/>
    <text x="75" y="243" font-family="monospace" font-size="9" fill="#000">WOUND</text>

    <!-- 2-3 inches marker -->
    <line x1="125" y1="150" x2="125" y2="165" stroke="#000" stroke-width="2"/>
    <text x="135" y="160" font-family="monospace" font-size="9" fill="#000">2-3"</text>
    <text x="125" y="270" font-family="monospace" font-size="10" text-anchor="middle" fill="#000">Above wound</text>
  </g>

  <!-- Step 2: Wrap -->
  <g id="step2">
    <rect x="230" y="80" width="150" height="200" fill="none" stroke="#000" stroke-width="2"/>
    <text x="305" y="100" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">2. WRAP</text>

    <!-- Arm -->
    <ellipse cx="305" cy="180" rx="25" ry="80" fill="url(#dots)" stroke="#000" stroke-width="2"/>
    <!-- Cloth wrap -->
    <rect x="275" y="155" width="60" height="12" fill="url(#herringbone)" stroke="#000" stroke-width="2"/>
    <path d="M 275 167 L 280 175 L 330 175 L 335 167" fill="url(#herringbone)" stroke="#000" stroke-width="2"/>

    <text x="305" y="270" font-family="monospace" font-size="10" text-anchor="middle" fill="#000">Wrap cloth 2x</text>
  </g>

  <!-- Step 3: Stick -->
  <g id="step3">
    <rect x="410" y="80" width="150" height="200" fill="none" stroke="#000" stroke-width="2"/>
    <text x="485" y="100" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">3. INSERT</text>

    <!-- Arm with wrap -->
    <ellipse cx="485" cy="180" rx="25" ry="80" fill="url(#dots)" stroke="#000" stroke-width="2"/>
    <rect x="455" y="155" width="60" height="12" fill="url(#herringbone)" stroke="#000" stroke-width="2"/>

    <!-- Stick -->
    <rect x="480" y="140" width="10" height="60" fill="url(#gray-50)" stroke="#000" stroke-width="2"/>
    <text x="530" y="170" font-family="monospace" font-size="9" fill="#000">Stick/rod</text>

    <text x="485" y="270" font-family="monospace" font-size="10" text-anchor="middle" fill="#000">Insert stick</text>
  </g>

  <!-- Step 4: Twist -->
  <g id="step4">
    <rect x="590" y="80" width="150" height="200" fill="none" stroke="#000" stroke-width="2"/>
    <text x="665" y="100" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">4. TIGHTEN</text>

    <!-- Arm with wrap -->
    <ellipse cx="665" cy="180" rx="25" ry="80" fill="url(#dots)" stroke="#000" stroke-width="2"/>
    <rect x="635" y="155" width="60" height="15" fill="url(#herringbone)" stroke="#000" stroke-width="2"/>

    <!-- Stick rotated -->
    <rect x="660" y="125" width="10" height="60" fill="url(#gray-50)" stroke="#000" stroke-width="2" transform="rotate(-30 665 155)"/>

    <!-- Rotation arrows -->
    <path d="M 680 145 Q 690 135 695 145" fill="none" stroke="#000" stroke-width="2"/>
    <polygon points="695,145 693,140 690,145" fill="#000"/>

    <text x="665" y="270" font-family="monospace" font-size="10" text-anchor="middle" fill="#000">Twist until tight</text>
  </g>

  <!-- Warning Box -->
  <rect x="50" y="320" width="690" height="80" fill="url(#gray-25)" stroke="#000" stroke-width="3"/>
  <text x="400" y="345" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">
    ⚠ CRITICAL WARNINGS
  </text>
  <text x="60" y="365" font-family="monospace" font-size="11" fill="#000">
    • Mark time applied with "T" + time on patient's forehead
  </text>
  <text x="60" y="380" font-family="monospace" font-size="11" fill="#000">
    • DO NOT remove once applied - only medical personnel
  </text>
  <text x="60" y="395" font-family="monospace" font-size="11" fill="#000">
    • Maximum safe time: 2 hours (limb viability)
  </text>

  <!-- Materials List -->
  <rect x="50" y="420" width="690" height="140" fill="none" stroke="#000" stroke-width="2"/>
  <text x="400" y="445" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">
    IMPROVISED MATERIALS
  </text>

  <g transform="translate(70, 460)">
    <text x="0" y="15" font-family="monospace" font-size="12" font-weight="bold" fill="#000">Cloth (2" wide):</text>
    <text x="20" y="30" font-family="monospace" font-size="11" fill="#000">• T-shirt strips, towel, bandanna, belt</text>

    <text x="0" y="55" font-family="monospace" font-size="12" font-weight="bold" fill="#000">Windlass (stick):</text>
    <text x="20" y="70" font-family="monospace" font-size="11" fill="#000">• Pen, stick, rod, utensil, carabiner</text>

    <text x="0" y="95" font-family="monospace" font-size="12" font-weight="bold" fill="#000">DO NOT USE:</text>
    <text x="20" y="110" font-family="monospace" font-size="11" fill="#000">• Wire, cord, rope <1" wide (causes tissue damage)</text>
  </g>

  <!-- Footer -->
  <text x="400" y="585" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">
    Mac OS System 1 Pattern Library | Monochrome Technical-Kinetic Design
  </text>
</svg>'''

# Example 2: Simple Fire Triangle
fire_triangle_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 500" width="600" height="500">
  <title>Fire Triangle - Essential Elements</title>
  <desc>Three requirements for fire: heat, fuel, and oxygen</desc>

  <defs>
    <pattern id="gray-50" patternUnits="userSpaceOnUse" width="2" height="2">
      <rect width="2" height="2" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="1" y="1" width="1" height="1" fill="#000"/>
    </pattern>

    <pattern id="diagonal" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="1" y="1" width="1" height="1" fill="#000"/>
      <rect x="2" y="2" width="1" height="1" fill="#000"/>
      <rect x="3" y="3" width="1" height="1" fill="#000"/>
      <rect x="4" y="4" width="1" height="1" fill="#000"/>
      <rect x="5" y="5" width="1" height="1" fill="#000"/>
      <rect x="6" y="6" width="1" height="1" fill="#000"/>
      <rect x="7" y="7" width="1" height="1" fill="#000"/>
    </pattern>

    <pattern id="horizontal" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="8" height="2" fill="#000"/>
      <rect x="0" y="4" width="8" height="2" fill="#000"/>
    </pattern>

    <pattern id="dots" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="2" y="2" width="1" height="1" fill="#000"/>
    </pattern>
  </defs>

  <!-- Title -->
  <text x="300" y="40" font-family="monospace" font-size="24" font-weight="bold" text-anchor="middle" fill="#000">
    THE FIRE TRIANGLE
  </text>

  <!-- Triangle -->
  <polygon points="300,100 150,350 450,350" fill="none" stroke="#000" stroke-width="3"/>

  <!-- Heat (top) -->
  <circle cx="300" cy="100" r="60" fill="url(#diagonal)" stroke="#000" stroke-width="3"/>
  <text x="300" y="110" font-family="monospace" font-size="16" font-weight="bold" text-anchor="middle" fill="#000">
    HEAT
  </text>
  <text x="300" y="50" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">
    Spark, friction, sun
  </text>

  <!-- Fuel (bottom left) -->
  <circle cx="150" cy="350" r="60" fill="url(#horizontal)" stroke="#000" stroke-width="3"/>
  <text x="150" y="355" font-family="monospace" font-size="16" font-weight="bold" text-anchor="middle" fill="#000">
    FUEL
  </text>
  <text x="150" y="430" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">
    Wood, tinder, kindling
  </text>

  <!-- Oxygen (bottom right) -->
  <circle cx="450" cy="350" r="60" fill="url(#dots)" stroke="#000" stroke-width="3"/>
  <text x="450" y="355" font-family="monospace" font-size="16" font-weight="bold" text-anchor="middle" fill="#000">
    OXYGEN
  </text>
  <text x="450" y="430" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">
    Air flow, ventilation
  </text>

  <!-- Center - Fire symbol -->
  <text x="300" y="240" font-family="monospace" font-size="36" font-weight="bold" text-anchor="middle" fill="#000">
    🔥
  </text>
  <text x="300" y="265" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">
    FIRE
  </text>

  <!-- Key principle -->
  <rect x="50" y="460" width="500" height="30" fill="url(#gray-50)" stroke="#000" stroke-width="2"/>
  <text x="300" y="482" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle" fill="#000">
    Remove ANY element → Fire extinguishes
  </text>
</svg>'''

# Save diagrams
output_dir = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams'

medical_dir = output_dir / 'medical'
medical_dir.mkdir(parents=True, exist_ok=True)
(medical_dir / 'tourniquet-application-mac-os.svg').write_text(tourniquet_svg)

fire_dir = output_dir / 'fire'
fire_dir.mkdir(parents=True, exist_ok=True)
(fire_dir / 'fire-triangle-mac-os.svg').write_text(fire_triangle_svg)

print("\n✅ Example diagrams created!")
print(f"   📁 {medical_dir / 'tourniquet-application-mac-os.svg'}")
print(f"   📁 {fire_dir / 'fire-triangle-mac-os.svg'}")
print("\n🎨 Mac OS System 1 aesthetic:")
print("   • Bold 2-3px strokes")
print("   • 8×8 bitmap patterns")
print("   • Generic monospace fonts")
print("   • Pixel-perfect geometric design")
