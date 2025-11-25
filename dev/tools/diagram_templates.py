#!/usr/bin/env python3
"""
SVG Diagram Template Library - Mac OS System 1 Patterns
Provides reusable templates for common diagram types
"""

from pathlib import Path
from typing import Dict

# Common pattern definitions (reusable across all templates)
PATTERN_DEFS = """
  <defs>
    <!-- Grayscale Patterns -->
    <pattern id="gray-12" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
    </pattern>

    <pattern id="gray-25" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#FFF"/>
      <rect x="0" y="0" width="2" height="2" fill="#000"/>
      <rect x="2" y="2" width="2" height="2" fill="#000"/>
    </pattern>

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

    <pattern id="gray-50" patternUnits="userSpaceOnUse" width="2" height="2">
      <rect width="2" height="2" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="1" y="1" width="1" height="1" fill="#000"/>
    </pattern>

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

    <pattern id="gray-75" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#000"/>
      <rect x="0" y="0" width="2" height="2" fill="#FFF"/>
      <rect x="2" y="2" width="2" height="2" fill="#FFF"/>
    </pattern>

    <!-- Texture Patterns -->
    <pattern id="brick" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="4" height="1" fill="#000"/>
      <rect x="4" y="1" width="1" height="3" fill="#000"/>
      <rect x="0" y="4" width="4" height="1" fill="#000"/>
      <rect x="0" y="5" width="1" height="3" fill="#000"/>
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

    <pattern id="cross-hatch" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="8" fill="#000"/>
      <rect x="0" y="0" width="8" height="1" fill="#000"/>
      <rect x="4" y="0" width="1" height="8" fill="#000"/>
      <rect x="0" y="4" width="8" height="1" fill="#000"/>
    </pattern>

    <pattern id="dots" patternUnits="userSpaceOnUse" width="4" height="4">
      <rect width="4" height="4" fill="#FFF"/>
      <rect x="0" y="0" width="1" height="1" fill="#000"/>
      <rect x="2" y="2" width="1" height="1" fill="#000"/>
    </pattern>

    <pattern id="horizontal" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="8" height="2" fill="#000"/>
      <rect x="0" y="4" width="8" height="2" fill="#000"/>
    </pattern>

    <pattern id="vertical" patternUnits="userSpaceOnUse" width="8" height="8">
      <rect width="8" height="8" fill="#FFF"/>
      <rect x="0" y="0" width="2" height="8" fill="#000"/>
      <rect x="4" y="0" width="2" height="8" fill="#000"/>
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
"""

TEMPLATES: Dict[str, str] = {}

# Template 1: Step-by-step process (4 steps)
TEMPLATES['4-step-process'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <title>{title}</title>
  <desc>{description}</desc>
{patterns}
  <!-- Title -->
  <text x="400" y="40" font-family="monospace" font-size="24" font-weight="bold" text-anchor="middle" fill="#000">
    {title_upper}
  </text>

  <!-- Step 1 -->
  <g id="step1">
    <rect x="50" y="80" width="150" height="200" fill="none" stroke="#000" stroke-width="2"/>
    <text x="125" y="100" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">1. {step1_title}</text>
    <!-- Add step content here -->
  </g>

  <!-- Step 2 -->
  <g id="step2">
    <rect x="230" y="80" width="150" height="200" fill="none" stroke="#000" stroke-width="2"/>
    <text x="305" y="100" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">2. {step2_title}</text>
    <!-- Add step content here -->
  </g>

  <!-- Step 3 -->
  <g id="step3">
    <rect x="410" y="80" width="150" height="200" fill="none" stroke="#000" stroke-width="2"/>
    <text x="485" y="100" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">3. {step3_title}</text>
    <!-- Add step content here -->
  </g>

  <!-- Step 4 -->
  <g id="step4">
    <rect x="590" y="80" width="150" height="200" fill="none" stroke="#000" stroke-width="2"/>
    <text x="665" y="100" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#000">4. {step4_title}</text>
    <!-- Add step content here -->
  </g>

  <!-- Footer -->
  <text x="400" y="580" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">
    Mac OS System 1 Patterns | Technical-Kinetic Design
  </text>
</svg>'''

# Template 2: Layered cross-section
TEMPLATES['layered-cross-section'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
  <title>{title}</title>
  <desc>{description}</desc>
{patterns}
  <!-- Title -->
  <text x="300" y="40" font-family="monospace" font-size="24" font-weight="bold" text-anchor="middle" fill="#000">
    {title_upper}
  </text>

  <!-- Container -->
  <rect x="150" y="80" width="300" height="400" fill="#FFF" stroke="#000" stroke-width="3"/>

  <!-- Layer 4 (Bottom) -->
  <rect x="150" y="380" width="300" height="100" fill="url(#{layer4_pattern})" stroke="#000" stroke-width="2"/>
  <text x="60" y="430" font-family="monospace" font-size="12" fill="#000">{layer4_label}</text>

  <!-- Layer 3 -->
  <rect x="150" y="280" width="300" height="100" fill="url(#{layer3_pattern})" stroke="#000" stroke-width="2"/>
  <text x="60" y="330" font-family="monospace" font-size="12" fill="#000">{layer3_label}</text>

  <!-- Layer 2 -->
  <rect x="150" y="180" width="300" height="100" fill="url(#{layer2_pattern})" stroke="#000" stroke-width="2"/>
  <text x="60" y="230" font-family="monospace" font-size="12" fill="#000">{layer2_label}</text>

  <!-- Layer 1 (Top) -->
  <rect x="150" y="80" width="300" height="100" fill="url(#{layer1_pattern})" stroke="#000" stroke-width="2"/>
  <text x="60" y="130" font-family="monospace" font-size="12" fill="#000">{layer1_label}</text>

  <!-- Footer -->
  <text x="300" y="580" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">
    Mac OS System 1 Patterns | Technical-Kinetic Design
  </text>
</svg>'''

# Template 3: Triangle diagram (3 elements)
TEMPLATES['triangle-3-elements'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 500" width="600" height="500">
  <title>{title}</title>
  <desc>{description}</desc>
{patterns}
  <!-- Title -->
  <text x="300" y="40" font-family="monospace" font-size="24" font-weight="bold" text-anchor="middle" fill="#000">
    {title_upper}
  </text>

  <!-- Triangle -->
  <polygon points="300,100 150,350 450,350" fill="none" stroke="#000" stroke-width="3"/>

  <!-- Element 1 (Top) -->
  <circle cx="300" cy="100" r="60" fill="url(#{element1_pattern})" stroke="#000" stroke-width="3"/>
  <text x="300" y="110" font-family="monospace" font-size="16" font-weight="bold" text-anchor="middle" fill="#000">
    {element1_label}
  </text>

  <!-- Element 2 (Bottom Left) -->
  <circle cx="150" cy="350" r="60" fill="url(#{element2_pattern})" stroke="#000" stroke-width="3"/>
  <text x="150" y="360" font-family="monospace" font-size="16" font-weight="bold" text-anchor="middle" fill="#000">
    {element2_label}
  </text>

  <!-- Element 3 (Bottom Right) -->
  <circle cx="450" cy="350" r="60" fill="url(#{element3_pattern})" stroke="#000" stroke-width="3"/>
  <text x="450" y="360" font-family="monospace" font-size="16" font-weight="bold" text-anchor="middle" fill="#000">
    {element3_label}
  </text>

  <!-- Center label -->
  <text x="300" y="240" font-family="monospace" font-size="18" font-weight="bold" text-anchor="middle" fill="#000">
    {center_label}
  </text>

  <!-- Footer -->
  <text x="300" y="480" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">
    Mac OS System 1 Patterns | Technical-Kinetic Design
  </text>
</svg>'''

# Template 4: Simple labeled diagram
TEMPLATES['labeled-object'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <title>{title}</title>
  <desc>{description}</desc>
{patterns}
  <!-- Title -->
  <text x="300" y="30" font-family="monospace" font-size="20" font-weight="bold" text-anchor="middle" fill="#000">
    {title_upper}
  </text>

  <!-- Main object area (customize as needed) -->
  <g id="main-object" transform="translate(300, 200)">
    <circle r="100" fill="url(#{main_pattern})" stroke="#000" stroke-width="3"/>
  </g>

  <!-- Labels (add as needed) -->
  <text x="300" y="350" font-family="monospace" font-size="12" text-anchor="middle" fill="#000">
    {main_label}
  </text>

  <!-- Footer -->
  <text x="300" y="390" font-family="monospace" font-size="9" text-anchor="middle" fill="#000">
    Mac OS System 1 Patterns | Technical-Kinetic Design
  </text>
</svg>'''

def generate_from_template(template_name: str, **kwargs) -> str:
    """Generate SVG from template with parameters"""
    if template_name not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")

    template = TEMPLATES[template_name]
    kwargs['patterns'] = PATTERN_DEFS

    # Auto-uppercase title if title_upper not provided
    if 'title' in kwargs and 'title_upper' not in kwargs:
        kwargs['title_upper'] = kwargs['title'].upper()

    return template.format(**kwargs)

def save_diagram(svg_content: str, filepath: Path):
    """Save SVG content to file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(svg_content)
    size_kb = filepath.stat().st_size / 1024
    print(f"✓ Created: {filepath} ({size_kb:.1f}KB)")

if __name__ == "__main__":
    print("\n📋 SVG Template Library - Mac OS System 1 Patterns\n")
    print("Available templates:")
    for name in TEMPLATES.keys():
        print(f"  • {name}")
    print("\nUsage:")
    print("  from diagram_templates import generate_from_template, save_diagram")
    print("  svg = generate_from_template('4-step-process', title='My Process', ...)")
    print("  save_diagram(svg, Path('output.svg'))")
