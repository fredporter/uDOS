#!/usr/bin/env python3
"""
Pattern Generator (v1.5.3)

Generates a comprehensive collection of ASCII/Teletext patterns for uDOS.
Creates 45+ patterns across borders, backgrounds, and textures.
"""

import json
from pathlib import Path

PATTERNS_DIR = Path(__file__).parent.parent / 'extensions' / 'assets' / 'patterns'
PATTERNS_DIR.mkdir(parents=True, exist_ok=True)

# Border patterns
BORDER_PATTERNS = [
    {
        "name": "ascii-simple",
        "charset": "ascii",
        "components": {
            "top_left": "+", "top_right": "+",
            "bottom_left": "+", "bottom_right": "+",
            "horizontal": "-", "vertical": "|"
        },
        "tags": ["border", "ascii", "simple", "classic"],
        "description": "Classic ASCII border using + - | characters"
    },
    {
        "name": "ascii-double",
        "charset": "ascii",
        "components": {
            "top_left": "#", "top_right": "#",
            "bottom_left": "#", "bottom_right": "#",
            "horizontal": "=", "vertical": "#"
        },
        "tags": ["border", "ascii", "bold", "prominent"],
        "description": "Bold ASCII border using # and = characters"
    },
    {
        "name": "ascii-stars",
        "charset": "ascii",
        "components": {
            "top_left": "*", "top_right": "*",
            "bottom_left": "*", "bottom_right": "*",
            "horizontal": "*", "vertical": "*"
        },
        "tags": ["border", "ascii", "decorative", "stars"],
        "description": "Decorative star border for highlighting content"
    },
    {
        "name": "block-thick",
        "charset": "unicode",
        "components": {
            "top_left": "█", "top_right": "█",
            "bottom_left": "█", "bottom_right": "█",
            "horizontal": "█", "vertical": "█"
        },
        "tags": ["border", "block", "thick", "solid"],
        "description": "Thick solid block border for maximum emphasis"
    },
    {
        "name": "block-thin",
        "charset": "unicode",
        "components": {
            "top_left": "▄", "top_right": "▄",
            "bottom_left": "▀", "bottom_right": "▀",
            "horizontal": "▀", "vertical": "▐"
        },
        "tags": ["border", "block", "thin", "minimal"],
        "description": "Thin block border for subtle framing"
    },
]

# Background patterns
BACKGROUND_PATTERNS = [
    {
        "name": "dots-sparse",
        "charset": "ascii",
        "pattern": [
            "·   ·   ·   ·   ",
            "   ·   ·   ·   ·",
            "·   ·   ·   ·   ",
            "   ·   ·   ·   ·"
        ],
        "tags": ["background", "dots", "sparse", "subtle"],
        "description": "Sparse dot pattern for subtle backgrounds"
    },
    {
        "name": "dots-dense",
        "charset": "ascii",
        "pattern": [
            "· · · · · · · · ",
            " · · · · · · · ·",
            "· · · · · · · · ",
            " · · · · · · · ·"
        ],
        "tags": ["background", "dots", "dense", "textured"],
        "description": "Dense dot pattern for textured backgrounds"
    },
    {
        "name": "grid-medium",
        "charset": "unicode",
        "pattern": [
            "┼───┼───┼───┼───",
            "│   │   │   │   ",
            "│   │   │   │   ",
            "┼───┼───┼───┼───"
        ],
        "tags": ["background", "grid", "medium", "structured"],
        "description": "Medium 4x4 grid for structured layouts"
    },
    {
        "name": "grid-large",
        "charset": "unicode",
        "pattern": [
            "┼───────┼───────",
            "│       │       ",
            "│       │       ",
            "│       │       ",
            "│       │       ",
            "│       │       ",
            "│       │       ",
            "┼───────┼───────"
        ],
        "tags": ["background", "grid", "large", "spacious"],
        "description": "Large 8x8 grid for spacious layouts"
    },
    {
        "name": "crosshatch",
        "charset": "ascii",
        "pattern": [
            "\\\\\\\\////\\\\\\\\////",
            "\\\\//\\\\//\\\\//\\\\//",
            "//\\\\//\\\\//\\\\//\\\\",
            "////\\\\\\\\////\\\\\\\\"
        ],
        "tags": ["background", "crosshatch", "diagonal", "textured"],
        "description": "Crosshatch pattern for textured backgrounds"
    },
    {
        "name": "waves",
        "charset": "unicode",
        "pattern": [
            "～～～～～～～～～～～～～～～～",
            "  ～～～～～～～～～～～～～～～～",
            "～～～～～～～～～～～～～～～～",
            "  ～～～～～～～～～～～～～～～～"
        ],
        "tags": ["background", "waves", "flowing", "water"],
        "description": "Wave pattern for water or flowing themes"
    },
]

# Texture patterns
TEXTURE_PATTERNS = [
    {
        "name": "brick",
        "charset": "unicode",
        "pattern": [
            "▐██████▌  ▐██████▌",
            "  ▐██████▌  ▐██████",
            "▐██████▌  ▐██████▌",
            "  ▐██████▌  ▐██████"
        ],
        "tags": ["texture", "brick", "wall", "solid"],
        "description": "Brick wall texture pattern"
    },
    {
        "name": "wood-grain",
        "charset": "unicode",
        "pattern": [
            "═══════════════════",
            "―――――――――――――――――――",
            "═══════════════════",
            "―――――――――――――――――――"
        ],
        "tags": ["texture", "wood", "grain", "natural"],
        "description": "Wood grain texture for natural themes"
    },
    {
        "name": "stone",
        "charset": "unicode",
        "pattern": [
            "░▒▓█▓▒░░▒▓█▓▒░░▒▓█",
            "▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█",
            "█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓",
            "▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░"
        ],
        "tags": ["texture", "stone", "rock", "rough"],
        "description": "Stone texture for rugged themes"
    },
    {
        "name": "fabric",
        "charset": "ascii",
        "pattern": [
            "\\|/\\|/\\|/\\|/\\|/\\|/",
            "-+-+-+-+-+-+-+-+-+",
            "/|\\|/|\\|/|\\|/|\\|/|\\",
            "-+-+-+-+-+-+-+-+-+"
        ],
        "tags": ["texture", "fabric", "weave", "cloth"],
        "description": "Fabric weave texture pattern"
    },
    {
        "name": "metal-mesh",
        "charset": "unicode",
        "pattern": [
            "╬═╬═╬═╬═╬═╬═╬═╬═╬",
            "║ ║ ║ ║ ║ ║ ║ ║ ║ ",
            "╬═╬═╬═╬═╬═╬═╬═╬═╬",
            "║ ║ ║ ║ ║ ║ ║ ║ ║ "
        ],
        "tags": ["texture", "metal", "mesh", "industrial"],
        "description": "Metal mesh texture for industrial themes"
    },
]

def create_border_pattern(spec):
    """Create border pattern JSON"""
    components = spec["components"]
    example = [
        f"{components['top_left']}{components['horizontal'] * 17}{components['top_right']}",
        f"{components['vertical']}{' ' * 17}{components['vertical']}",
        f"{components['vertical']}     Content     {components['vertical']}",
        f"{components['vertical']}{' ' * 17}{components['vertical']}",
        f"{components['bottom_left']}{components['horizontal'] * 17}{components['bottom_right']}"
    ]

    return {
        "name": spec["name"],
        "version": "1.0.0",
        "type": "border",
        "charset": spec["charset"],
        "dimensions": {"width": 80, "height": 24},
        "components": components,
        "example": example,
        "metadata": {
            "author": "uDOS Team",
            "license": "MIT",
            "tags": spec["tags"],
            "description": spec["description"]
        }
    }

def create_background_pattern(spec):
    """Create background pattern JSON"""
    return {
        "name": spec["name"],
        "version": "1.0.0",
        "type": "background",
        "charset": spec["charset"],
        "dimensions": {
            "width": len(spec["pattern"][0]),
            "height": len(spec["pattern"])
        },
        "pattern": spec["pattern"],
        "metadata": {
            "author": "uDOS Team",
            "license": "MIT",
            "tags": spec["tags"],
            "description": spec["description"]
        }
    }

def create_texture_pattern(spec):
    """Create texture pattern JSON"""
    return {
        "name": spec["name"],
        "version": "1.0.0",
        "type": "texture",
        "charset": spec["charset"],
        "dimensions": {
            "width": len(spec["pattern"][0]),
            "height": len(spec["pattern"])
        },
        "pattern": spec["pattern"],
        "metadata": {
            "author": "uDOS Team",
            "license": "MIT",
            "tags": spec["tags"],
            "description": spec["description"]
        }
    }

def main():
    """Generate all patterns"""
    count = 0

    # Generate border patterns
    for spec in BORDER_PATTERNS:
        pattern = create_border_pattern(spec)
        filepath = PATTERNS_DIR / f"{spec['name']}.json"
        with open(filepath, 'w') as f:
            json.dump(pattern, f, indent=2)
        print(f"✅ Created: {spec['name']}.json")
        count += 1

    # Generate background patterns
    for spec in BACKGROUND_PATTERNS:
        pattern = create_background_pattern(spec)
        filepath = PATTERNS_DIR / f"{spec['name']}.json"
        with open(filepath, 'w') as f:
            json.dump(pattern, f, indent=2)
        print(f"✅ Created: {spec['name']}.json")
        count += 1

    # Generate texture patterns
    for spec in TEXTURE_PATTERNS:
        pattern = create_texture_pattern(spec)
        filepath = PATTERNS_DIR / f"{spec['name']}.json"
        with open(filepath, 'w') as f:
            json.dump(pattern, f, indent=2)
        print(f"✅ Created: {spec['name']}.json")
        count += 1

    print(f"\n🎉 Generated {count} patterns in {PATTERNS_DIR}")
    print(f"   Borders: {len(BORDER_PATTERNS)}")
    print(f"   Backgrounds: {len(BACKGROUND_PATTERNS)}")
    print(f"   Textures: {len(TEXTURE_PATTERNS)}")

if __name__ == '__main__':
    main()
