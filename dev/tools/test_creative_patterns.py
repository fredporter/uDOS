#!/usr/bin/env python3
"""
Quick SVG Test Generator - Creates sample diagram without API call
Tests pattern library and font embedding
"""

import sys
from pathlib import Path

# Sample SVG with all creative patterns
svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="1200" height="800">
  <title>Pattern Library Test - Creative Enhancement</title>
  <desc>Demonstration of all 21 patterns: 7 grayscale + 5 basic + 9 creative textures</desc>

  <defs>
    <!-- Classic Mac OS System 1 inspired patterns - 8x8 bitmap style -->

    <!-- SOLID TONES -->
    <pattern id="black" patternUnits="userSpaceOnUse" width="1" height="1">
      <rect width="1" height="1" fill="#000"/>
    </pattern>

    <pattern id="white" patternUnits="userSpaceOnUse" width="1" height="1">
      <rect width="1" height="1" fill="#FFF"/>
    </pattern>

    <!-- GRAYSCALE PATTERNS (Mac OS System 1 style) -->

    <!-- 12.5% gray - Light dots -->
    <pattern id="gray-12" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
    </pattern>

    <!-- 25% gray - Checkerboard sparse -->
    <pattern id="gray-25" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#FFF"/>
      <rect x="0" y="0" width="2" height="2" fill="#000"/>
      <rect x="2" y="2" width="2" height="2" fill="#000"/>
    </pattern>

    <!-- 37.5% gray - Diagonal sparse -->
    <pattern id="gray-37" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="2" y="2" width="1" height="1" fill="#000"/>
      <rect x="4" y="4" width="1" height="1" fill="#000"/>
      <rect x="6" y="6" width="1" height="1" fill="#000"/>
      <rect x="1" y="1" width="1" height="1" fill="#000"/>
      <rect x="3" y="3" width="1" height="1" fill="#000"/>
      <rect x="5" y="5" width="1" height="1" fill="#000"/>
      <rect x="7" y="7" width="1" height="1" fill="#000"/>
    </pattern>

    <!-- 50% gray - Dense checkerboard -->
    <pattern id="gray-50" patternUnits="userSpaceOnUse" width="2" height="2">
      <rect width="2" height="2" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="1" y="1" width="1" height="1" fill="#000"/>
    </pattern>

    <!-- 62.5% gray - Inverse diagonal -->
    <pattern id="gray-62" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#000"/>
      <rect x="1" y="0" width="1" height="1" fill="#FFF"/>
      <rect x="3" y="2" width="1" height="1" fill="#FFF"/>
      <rect x="5" y="4" width="1" height="1" fill="#FFF"/>
      <rect x="7" y="6" width="1" height="1" fill="#FFF"/>
      <rect x="0" y="1" width="1" height="1" fill="#FFF"/>
      <rect x="2" y="3" width="1" height="1" fill="#FFF"/>
      <rect x="4" y="5" width="1" height="1" fill="#FFF"/>
      <rect x="6" y="7" width="1" height="1" fill="#FFF"/>
    </pattern>

    <!-- 75% gray - Inverse checkerboard -->
    <pattern id="gray-75" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#000"/>
      <rect x="0" y="0" width="2" height="2" fill="#FFF"/>
      <rect x="2" y="2" width="2" height="2" fill="#FFF"/>
    </pattern>

    <!-- 87.5% gray - Dark with white dots -->
    <pattern id="gray-87" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#000"/>
      <rect x="4" y="4" width="1" height="1" fill="#FFF"/>
    </pattern>

    <!-- TEXTURE PATTERNS (Mac OS System 1 classic) -->

    <!-- Brick/Weave pattern -->
    <pattern id="brick" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="4" height="1" fill="#000"/>
      <rect x="4" y="1" width="1" height="3" fill="#000"/>
      <rect x="0" y="4" width="4" height="1" fill="#000"/>
      <rect x="0" y="5" width="1" height="3" fill="#000"/>
    </pattern>

    <!-- Diagonal lines (bold) -->
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

    <!-- Cross-hatch (bold) -->
    <pattern id="cross-hatch" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="8" fill="#000"/>
      <rect x="0" y="0" width="8" height="1" fill="#000"/>
      <rect x="4" y="0" width="1" height="8" fill="#000"/>
      <rect x="0" y="4" width="8" height="1" fill="#000"/>
    </pattern>

    <!-- Horizontal lines (bold) -->
    <pattern id="horizontal" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="8" height="2" fill="#000"/>
      <rect x="0" y="4" width="8" height="2" fill="#000"/>
    </pattern>

    <!-- Vertical lines (bold) -->
    <pattern id="vertical" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="2" height="8" fill="#000"/>
      <rect x="4" y="0" width="2" height="8" fill="#000"/>
    </pattern>

    <!-- Dots/stipple (bold) -->
    <pattern id="dots" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="2" y="2" width="1" height="1" fill="#000"/>
    </pattern>

    <!-- Scales/fish scales -->
    <pattern id="scales" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="4" height="1" fill="#000"/>
      <rect x="0" y="1" width="1" height="1" fill="#000"/>
      <rect x="3" y="1" width="1" height="1" fill="#000"/>
      <rect x="1" y="2" width="2" height="1" fill="#000"/>
      <rect x="4" y="4" width="4" height="1" fill="#000"/>
      <rect x="4" y="5" width="1" height="1" fill="#000"/>
      <rect x="7" y="5" width="1" height="1" fill="#000"/>
      <rect x="5" y="6" width="2" height="1" fill="#000"/>
    </pattern>

    <!-- Grid pattern -->
    <pattern id="grid" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="8" height="1" fill="#000"/>
      <rect x="0" y="0" width="1" height="8" fill="#000"/>
    </pattern>

    <!-- Waves -->
    <pattern id="waves" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="3" width="2" height="2" fill="#000"/>
      <rect x="2" y="2" width="2" height="2" fill="#000"/>
      <rect x="4" y="1" width="2" height="2" fill="#000"/>
      <rect x="6" y="2" width="2" height="2" fill="#000"/>
    </pattern>

    <!-- Herringbone -->
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
      <rect x="0" y="7" width="1" height="1" fill="#000"/>
      <rect x="1" y="6" width="1" height="1" fill="#000"/>
      <rect x="2" y="5" width="1" height="1" fill="#000"/>
      <rect x="3" y="4" width="1" height="1" fill="#000"/>
      <rect x="7" y="7" width="1" height="1" fill="#000"/>
      <rect x="6" y="6" width="1" height="1" fill="#000"/>
      <rect x="5" y="5" width="1" height="1" fill="#000"/>
      <rect x="4" y="4" width="1" height="1" fill="#000"/>
    </pattern>
  </defs>

  <!-- Title -->
  <text x="600" y="40" font-family="monospace" font-size="28" font-weight="bold" text-anchor="middle" fill="#000">
    Mac OS System 1 Pattern Library
  </text>

  <!-- Row 1: Grayscale Patterns -->
  <g id="grayscale-row">
    <rect x="50" y="80" width="100" height="100" fill="url(#gray-12)" stroke="#000" stroke-width="2"/>
    <text x="100" y="200" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">12% gray</text>

    <rect x="170" y="80" width="100" height="100" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
    <text x="220" y="200" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">25% gray</text>

    <rect x="290" y="80" width="100" height="100" fill="url(#gray-37)" stroke="#000" stroke-width="2"/>
    <text x="340" y="200" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">37% gray</text>

    <rect x="410" y="80" width="100" height="100" fill="url(#gray-50)" stroke="#000" stroke-width="2"/>
    <text x="460" y="200" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">50% gray</text>

    <rect x="530" y="80" width="100" height="100" fill="url(#gray-62)" stroke="#000" stroke-width="2"/>
    <text x="580" y="200" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">62% gray</text>

    <rect x="650" y="80" width="100" height="100" fill="url(#gray-75)" stroke="#000" stroke-width="2"/>
    <text x="700" y="200" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">75% gray</text>

    <rect x="770" y="80" width="100" height="100" fill="url(#gray-87)" stroke="#000" stroke-width="2"/>
    <text x="820" y="200" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">87% gray</text>
  </g>

  <!-- Row 2: Texture Patterns -->
  <g id="texture-row">
    <rect x="50" y="230" width="100" height="100" fill="url(#brick)" stroke="#000" stroke-width="2"/>
    <text x="100" y="350" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">brick</text>

    <rect x="170" y="230" width="100" height="100" fill="url(#diagonal)" stroke="#000" stroke-width="2"/>
    <text x="220" y="350" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">diagonal</text>

    <rect x="290" y="230" width="100" height="100" fill="url(#cross-hatch)" stroke="#000" stroke-width="2"/>
    <text x="340" y="350" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">cross-hatch</text>

    <rect x="410" y="230" width="100" height="100" fill="url(#horizontal)" stroke="#000" stroke-width="2"/>
    <text x="460" y="350" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">horizontal</text>

    <rect x="530" y="230" width="100" height="100" fill="url(#vertical)" stroke="#000" stroke-width="2"/>
    <text x="580" y="350" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">vertical</text>

    <rect x="650" y="230" width="100" height="100" fill="url(#dots)" stroke="#000" stroke-width="2"/>
    <text x="700" y="350" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">dots</text>

    <rect x="770" y="230" width="100" height="100" fill="url(#scales)" stroke="#000" stroke-width="2"/>
    <text x="820" y="350" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">scales</text>
  </g>

  <!-- Row 3: More Textures -->
  <g id="texture-row-2">
    <rect x="170" y="380" width="100" height="100" fill="url(#grid)" stroke="#000" stroke-width="2"/>
    <text x="220" y="500" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">grid</text>

    <rect x="290" y="380" width="100" height="100" fill="url(#waves)" stroke="#000" stroke-width="2"/>
    <text x="340" y="500" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">waves</text>

    <rect x="410" y="380" width="100" height="100" fill="url(#herringbone)" stroke="#000" stroke-width="2"/>
    <text x="460" y="500" font-family="monospace" font-size="11" text-anchor="middle" fill="#000">herringbone</text>
  </g>

  <!-- Usage Example: Water Filter Cross-Section -->
  <g id="example-diagram" transform="translate(580, 230)">
    <text x="200" y="0" font-family="monospace" font-size="18" font-weight="bold" text-anchor="middle" fill="#000">
      Example: Water Filter (Mac OS Style)
    </text>

    <!-- Container outline -->
    <rect x="80" y="40" width="240" height="300" fill="url(#white)" stroke="#000" stroke-width="3"/>

    <!-- Gravel layer (dots) -->
    <rect x="80" y="270" width="240" height="70" fill="url(#dots)" stroke="#000" stroke-width="2"/>
    <text x="10" y="305" font-family="monospace" font-size="10" text-anchor="start" fill="#000">Gravel</text>

    <!-- Sand layer (gray-37) -->
    <rect x="80" y="180" width="240" height="90" fill="url(#gray-37)" stroke="#000" stroke-width="2"/>
    <text x="10" y="225" font-family="monospace" font-size="10" text-anchor="start" fill="#000">Sand</text>

    <!-- Charcoal layer (gray-75) -->
    <rect x="80" y="100" width="240" height="80" fill="url(#gray-75)" stroke="#000" stroke-width="2"/>
    <text x="10" y="140" font-family="monospace" font-size="10" text-anchor="start" fill="#000">Charcoal</text>

    <!-- Fine cloth (cross-hatch) -->
    <rect x="80" y="80" width="240" height="20" fill="url(#cross-hatch)" stroke="#000" stroke-width="2"/>
    <text x="10" y="90" font-family="monospace" font-size="10" text-anchor="start" fill="#000">Cloth</text>

    <!-- Water input (waves) -->
    <rect x="80" y="40" width="240" height="40" fill="url(#waves)" stroke="none"/>
    <text x="340" y="60" font-family="monospace" font-size="10" text-anchor="start" fill="#000">Water in</text>

    <!-- Output spout -->
    <rect x="180" y="340" width="40" height="20" fill="url(#white)" stroke="#000" stroke-width="2"/>
    <polygon points="195,360 205,360 200,370" fill="#000"/>
    <text x="215" y="370" font-family="monospace" font-size="10" text-anchor="start" fill="#000">Filtered water</text>

    <!-- Legend -->
    <text x="200" y="400" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">
      Pattern-based textures simulate material density
    </text>
  </g>

  <!-- Footer -->
  <text x="600" y="760" font-family="monospace" font-size="10" text-anchor="middle" fill="#000">
    Mac OS System 1 Patterns | 8×8 bitmap style | Technical-Kinetic Design
  </text>
  <text x="600" y="780" font-family="monospace" font-size="8" text-anchor="middle" fill="#000">
    7 grayscale + 10 texture patterns = 17 total | Generic monospace fonts
  </text>
</svg>'''

# Save to file
output_dir = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'fire'
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / 'pattern-library-test-creative.svg'

output_file.write_text(svg_content)
file_size = output_file.stat().st_size / 1024

print(f"\n✅ Mac OS System 1 Pattern Library SVG Created!")
print(f"   File: {output_file}")
print(f"   Size: {file_size:.1f}KB")
print(f"\n📊 Patterns demonstrated:")
print(f"   ✓ 7 grayscale patterns (12%, 25%, 37%, 50%, 62%, 75%, 87%)")
print(f"   ✓ 10 texture patterns (brick, diagonal, cross-hatch, etc.)")
print(f"   ✓ Generic monospace font")
print(f"   ✓ Water filter example with pattern-based materials")
print(f"\n💡 Open in browser to view classic Mac OS bitmap patterns!")
