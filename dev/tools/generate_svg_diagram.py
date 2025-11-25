#!/usr/bin/env python3
"""
SVG Diagram Generator using Gemini API
Generates Technical-Kinetic compliant monochrome SVG diagrams

Usage:
    python generate_svg_diagram.py "tourniquet application 6 steps" water
    python generate_svg_diagram.py "bow drill assembly exploded view" tools
    python generate_svg_diagram.py "CPR hand placement adult" medical --size 1200x800
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import Optional, Tuple

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extensions.core.ok_assistant import GeminiCLI

# SVG Pattern Library Template (Mac OS System 1 style)
SVG_PATTERN_DEFS = """
  <defs>
    <!-- Mac OS System 1 inspired patterns - 8x8 bitmap style -->

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
"""

TECHNICAL_KINETIC_GUIDELINES = """
## Technical-Kinetic SVG Design Guidelines (Mac OS System 1 Style)

### Core Principles:
1. **MONOCHROME PALETTE**: Black #000000, White #FFFFFF, solid grays, and bitmap patterns
2. **SOLID FILLS & PATTERNS**: Use solid grays (#1A1A1A, #333333, #4D4D4D, #666666, #808080, #999999, #B3B3B3, #CCCCCC, #E6E6E6) for smooth gradients, bitmap patterns for texture
3. **UI COMPONENTS**: Windows, buttons, dialogs, borders from system.css (Apple HI Guidelines 1984-1991)
4. **Generic Monospace Font**: Use font-family="monospace" for ALL text elements (Chicago 12pt simulation)
5. **8×8 Bitmap Patterns**: Classic Mac OS System 1 style patterns for texture effects
6. **Editable Text**: Text must be <text> elements, NEVER converted to paths
7. **Clean Structure**: Properly defined viewBox, width, height attributes
8. **Technical Aesthetic**: Bold geometric patterns + Swiss typography + authentic Mac OS UI

### Color Palette:

**Solid Fills:**
- **#000000** (black): Primary shapes, text, borders
- **#1A1A1A** (90% black): Very dark shadows, deep fills
- **#333333** (80% black): Dark structural elements
- **#4D4D4D** (70% black): Medium-dark fills
- **#666666** (60% black): Medium gray fills
- **#808080** (50% gray): Mid-tone fills
- **#999999** (40% gray): Light-medium fills
- **#B3B3B3** (30% gray): Light fills
- **#CCCCCC** (20% gray): Very light fills
- **#E6E6E6** (10% gray): Subtle backgrounds
- **#FFFFFF** (white): Backgrounds, highlights

### Pattern Library (Mac OS System 1 Style - 17 patterns):

**Grayscale Tones (Bitmap-Based):**
- **black** or fill="#000": Solid black - high-contrast elements, filled shapes, warning boxes
- **white** or fill="#FFF": Solid white - backgrounds, empty areas
- **gray-12**: 12.5% density - very light tint, subtle highlights
- **gray-25**: 25% density - light backgrounds, soft shading
- **gray-37**: 37.5% density - light-medium tone, gentle gradients
- **gray-50**: 50% density - balanced mid-tone, neutral areas
- **gray-62**: 62.5% density - medium-dark shading
- **gray-75**: 75% density - dark backgrounds, heavy shadows
- **gray-87**: 87.5% density - very dark, near-black areas

**Bold Texture Patterns (8×8 bitmap):**
- **brick**: Brick/weave pattern - masonry, stone walls, structural building
- **diagonal**: Bold diagonal lines - directional flow, structural elements
- **cross-hatch**: Bold grid - very dense materials, cast iron, metal surfaces
- **horizontal**: Bold horizontal bars - layered materials, stratification
- **vertical**: Bold vertical bars - wood grain, columnar structures
- **dots**: Bold stipple - soft materials, skin, clouds, atmospheric effects
- **scales**: Fish scales pattern - protective layers, roof tiles, armor, overlapping
- **grid**: Grid lines - technical drawings, measurement grids, coordinates
- **waves**: Blocky wave pattern - water, organic materials, flowing elements
- **herringbone**: Zigzag weave - decorative elements, fancy textiles, premium materials

### Material-to-Pattern Mapping:

**Structural & Mechanical:**
- Metal/tools → cross-hatch, diagonal, or grid
- Stone/masonry → brick or scales
- Wood/timber → vertical or horizontal
- Concrete → gray-50 or gray-62

**Organic & Natural:**
- Skin/flesh → dots (light density)
- Fabric/cloth → herringbone or grid (fine)
- Water (still) → gray-37 or gray-25
- Water (flowing) → waves
- Vegetation → dots or gray-50

**Layered Materials (filters, barriers):**
- Gravel → dots (medium-bold)
- Sand → gray-37 or gray-50
- Charcoal/carbon → gray-75 or gray-87
- Cloth/fabric → cross-hatch or grid

**Special Effects:**
- Shadows → gray-75 or gray-87
- Highlights → gray-12 or white
- Boundaries → black with bold stroke
- Backgrounds → gray-12 or gray-25
- Dense fill → gray-62 or gray-75

### Line Weights (BOLD - Mac OS Style):
- Primary outlines: 2-3px (stroke-width="2" or "3")
- Secondary details: 1.5px
- Fine details: 1px
- Pattern lines: Built into 8×8 patterns

### Text Sizing (BOLD):
- Title/Header: 18-28px, font-weight="bold"
- Section Labels: 14-16px, font-weight="bold"
- Body/Descriptions: 11-13px
- Annotations/Notes: 9-11px

### Mac OS System 1 Design Philosophy:

**Bold & Clear:**
- Use thick stroke weights (2-3px for main lines)
- High contrast between elements
- Clear separation between components
- No subtle anti-aliasing - sharp pixel-perfect edges

**Pattern Density:**
- Use grayscale patterns for tonal variation
- Texture patterns for material identification
- Never mix more than 2 pattern types in close proximity
- Maintain white space for clarity

**Pixel-Perfect Precision:**
- Align elements to whole pixel boundaries when possible
- Use 8×8 pattern grid as spacing guide
- Keep layout geometric and grid-based
- Sharp corners preferred over rounded

### SVG Structure Template:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 WIDTH HEIGHT" width="WIDTH" height="HEIGHT">
  <title>Descriptive Title</title>
  <desc>Detailed description for accessibility</desc>

  <!-- Pattern library goes here in <defs> -->

  <!-- Main diagram content with <g> groups -->
  <g id="descriptive-group-name">
    <!-- Shapes with pattern fills: fill="url(#pattern-name)" -->
    <!-- Text with Mallard font: font-family="Mallard, Arial, sans-serif" -->
  </g>

  <!-- Attribution footer -->
  <text x="CENTER" y="BOTTOM" font-family="Mallard, Arial, sans-serif" font-size="8" text-anchor="middle" fill="#000">
    Technical-Kinetic Design | uDOS Knowledge Bank | Mallard Font | Pattern-based monochrome
  </text>
</svg>

### FORBIDDEN (Will be rejected):
❌ Solid gray fills: fill="#808080" or fill="#999999"
❌ Opacity manipulation: opacity="0.5" for graying
❌ RGB/HSL colors: fill="rgb(128,128,128)"
❌ Arial/Helvetica without Mallard fallback
❌ Text converted to paths: <path d="M..."> instead of <text>
❌ Embedded raster images: <image xlink:href="data:image/png">
❌ Decorative/photorealistic content
❌ File size over 50KB

### REQUIRED (Must include):
✅ viewBox attribute on <svg>
✅ <title> and <desc> elements for accessibility
✅ All patterns defined in <defs> section
✅ Mallard font with @font-face embedding
✅ Pattern-based fills for all toning
✅ Editable <text> elements
✅ Clean, logical <g> grouping
✅ Attribution footer
✅ File size under 50KB
✅ Print-tested at 300dpi (patterns visible)
"""


class SVGDiagramGenerator:
    """Generate Technical-Kinetic compliant SVG diagrams using Gemini API"""

    def __init__(self, env_path: Optional[Path] = None):
        """Initialize generator with Gemini API"""
        # Default to project root .env if not specified
        if env_path is None:
            project_root = Path(__file__).parent.parent.parent
            env_path = project_root / '.env'
        self.gemini = GeminiCLI(env_path=env_path)
        self.output_dir = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams'

    def parse_size(self, size_str: str) -> Tuple[int, int]:
        """Parse size string like '800x600' into (width, height)"""
        match = re.match(r'(\d+)x(\d+)', size_str)
        if not match:
            raise ValueError(f"Invalid size format: {size_str}. Use WIDTHxHEIGHT (e.g., 800x600)")
        return int(match.group(1)), int(match.group(2))

    def build_prompt(self, description: str, category: str, width: int, height: int) -> str:
        """Build comprehensive prompt for Gemini"""
        prompt = f"""Generate a complete, production-ready SVG diagram with the following specifications:

DIAGRAM REQUEST:
Description: {description}
Category: {category}
Dimensions: {width}x{height}px
ViewBox: 0 0 {width} {height}

{TECHNICAL_KINETIC_GUIDELINES}

PATTERN LIBRARY (already defined - reference with fill="url(#pattern-id)"):
{SVG_PATTERN_DEFS}

IMPORTANT INSTRUCTIONS:
1. Generate COMPLETE, valid SVG code - not pseudo-code or placeholders
2. Include the full pattern library in <defs> (provided above)
3. Use descriptive <title> and <desc> elements
4. Group related elements with <g id="meaningful-id">
5. Apply appropriate patterns based on material type
6. Use Mallard font for ALL text: font-family="Mallard, Arial, sans-serif"
7. Include attribution footer at bottom
8. Make it instructive and technically accurate
9. Ensure all shapes/paths are properly closed
10. Output ONLY the SVG code - no explanations, no markdown backticks

PATTERN USAGE EXAMPLE:
- Water container: fill="url(#topo)" (topographic for water)
- Metal tube: fill="url(#hatch)" (hatching for metal)
- Skin/fabric: fill="url(#stipple)" (stipple for soft materials)
- Wood: fill="url(#waves)" (waves for organic)
- Background shade: fill="url(#gray-25)" (light gray pattern)
- Warning box: fill="#000" (solid black for contrast)

Now generate the complete SVG diagram for: {description}

OUTPUT ONLY THE SVG CODE (no markdown, no explanations):"""

        return prompt

    def generate_diagram(
        self,
        description: str,
        category: str,
        size: str = "800x600",
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generate SVG diagram using Gemini API

        Args:
            description: What to draw (e.g., "tourniquet application 6 steps")
            category: Diagram category (water, fire, shelter, food, medical, tools, etc.)
            size: Diagram size as WIDTHxHEIGHT (default: 800x600)
            output_filename: Optional custom filename (auto-generated if None)

        Returns:
            Path to generated SVG file
        """
        print(f"\n🎨 Generating SVG diagram...")
        print(f"   Description: {description}")
        print(f"   Category: {category}")
        print(f"   Size: {size}")

        # Parse dimensions
        width, height = self.parse_size(size)

        # Build prompt
        prompt = self.build_prompt(description, category, width, height)

        print(f"\n📡 Sending request to Gemini API...")

        # Get SVG from Gemini
        response = self.gemini.ask(prompt)

        # Clean up response (remove markdown if present)
        svg_content = response.strip()

        # Remove markdown code blocks if present
        if svg_content.startswith('```'):
            lines = svg_content.split('\n')
            # Remove first line (```svg or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            svg_content = '\n'.join(lines)

        # Validate SVG
        if not svg_content.startswith('<svg'):
            print(f"\n❌ Error: Gemini did not return valid SVG")
            print(f"Response preview: {svg_content[:200]}...")
            sys.exit(1)

        # Generate filename if not provided
        if not output_filename:
            # Create safe filename from description
            safe_name = re.sub(r'[^a-z0-9]+', '-', description.lower()).strip('-')
            output_filename = f"{safe_name}.svg"

        # Ensure category directory exists
        category_dir = self.output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Write SVG file
        output_path = category_dir / output_filename
        output_path.write_text(svg_content, encoding='utf-8')

        file_size = output_path.stat().st_size
        file_size_kb = file_size / 1024

        print(f"\n✅ SVG diagram generated successfully!")
        print(f"   File: {output_path}")
        print(f"   Size: {file_size_kb:.1f}KB")

        if file_size_kb > 50:
            print(f"\n⚠️  Warning: File size ({file_size_kb:.1f}KB) exceeds 50KB target")
            print(f"   Consider simplifying or optimizing the diagram")

        # Validate Technical-Kinetic compliance
        self.validate_compliance(svg_content, output_path)

        return output_path

    def validate_compliance(self, svg_content: str, filepath: Path) -> None:
        """Validate SVG against Technical-Kinetic standards"""
        print(f"\n🔍 Validating Technical-Kinetic compliance...")

        issues = []
        warnings = []

        # Check for forbidden solid grays (matching patterns like #808080, #999999, etc.)
        gray_fills = re.findall(r'fill="#([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})"', svg_content)
        for r, g, b in gray_fills:
            if r == g == b and r not in ['00', 'FF', 'ff']:
                issues.append(f"❌ Found solid gray fill #{r}{g}{b} - use pattern fills instead")
                break

        # Check for forbidden opacity manipulation
        if re.search(r'opacity="0\.[0-9]+"', svg_content) or re.search(r'fill-opacity', svg_content):
            issues.append("❌ Found opacity manipulation - use pattern density instead")

        # Check for non-monochrome colors
        color_pattern = r'fill="#(?!000000|FFFFFF|FFF|000)[0-9A-Fa-f]{6}"'
        if re.search(color_pattern, svg_content):
            warnings.append("⚠️  Found non-monochrome colors - should be black/white only")

        # Check for Mallard font
        if 'Mallard' not in svg_content:
            issues.append("❌ Missing Mallard font - add font-family=\"Mallard, Arial, sans-serif\"")

        # Check for required elements
        if '<title>' not in svg_content:
            issues.append("❌ Missing <title> element for accessibility")
        if '<desc>' not in svg_content:
            issues.append("❌ Missing <desc> element for accessibility")
        if 'viewBox' not in svg_content:
            issues.append("❌ Missing viewBox attribute")

        # Check for pattern definitions
        required_patterns = ['gray-', 'hatch', 'stipple', 'topo']
        missing_patterns = [p for p in required_patterns if p not in svg_content]
        if missing_patterns:
            warnings.append(f"⚠️  Missing pattern definitions: {', '.join(missing_patterns)}")

        # Print results
        if issues:
            print(f"\n❌ COMPLIANCE ISSUES FOUND ({len(issues)}):")
            for issue in issues:
                print(f"   {issue}")

        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"   {warning}")

        if not issues and not warnings:
            print(f"   ✅ All compliance checks passed!")

        if issues:
            print(f"\n💡 Fix these issues before using in production")
            print(f"   Review: {filepath}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Generate Technical-Kinetic SVG diagrams using Gemini API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_svg_diagram.py "tourniquet application 6 steps" medical
  python generate_svg_diagram.py "bow drill assembly exploded view" tools
  python generate_svg_diagram.py "CPR hand placement" medical --size 1200x800
  python generate_svg_diagram.py "water filter cross-section" water -o custom-name.svg
        """
    )

    parser.add_argument(
        'description',
        help='Diagram description (e.g., "tourniquet application 6 steps")'
    )
    parser.add_argument(
        'category',
        help='Diagram category (water, fire, shelter, food, navigation, medical, tools, communication)'
    )
    parser.add_argument(
        '--size', '-s',
        default='800x600',
        help='Diagram size as WIDTHxHEIGHT (default: 800x600)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output filename (auto-generated if not specified)'
    )
    parser.add_argument(
        '--env',
        type=Path,
        help='Path to .env file (default: auto-detect)'
    )

    args = parser.parse_args()

    try:
        # Initialize generator
        generator = SVGDiagramGenerator(env_path=args.env)

        # Generate diagram
        output_path = generator.generate_diagram(
            description=args.description,
            category=args.category,
            size=args.size,
            output_filename=args.output
        )

        print(f"\n🎉 Success! Diagram saved to:")
        print(f"   {output_path}")
        print(f"\n💡 Next steps:")
        print(f"   1. Review the diagram in a browser or SVG viewer")
        print(f"   2. Fix any compliance issues if reported above")
        print(f"   3. Update knowledge/diagrams/README.md progress tracking")
        print(f"   4. Link from relevant guides in knowledge/")

    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
