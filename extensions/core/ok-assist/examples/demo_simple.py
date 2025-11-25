#!/usr/bin/env python3
"""
OK Assist - Simple Multi-Format Demo

Generates one example in each format: ASCII, Teletext, SVG
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Get project root and load .env
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Output directory
output_dir = project_root / "knowledge" / "diagrams"
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("OK ASSIST - MULTI-FORMAT GENERATION DEMO")
print("=" * 80)
print(f"\nOutput directory: {output_dir}\n")

# =============================================================================
# DEMO 1: ASCII Art (Terminal/CLI)
# =============================================================================
print("📄 Generating ASCII art (80×24, C64 PetMe character set)...")

ascii_prompt = """Generate ASCII art using C64 PetMe/PETSCII characters (UTF-8).

SUBJECT: Simple water filter
DIMENSIONS: 60 columns × 20 rows maximum
STYLE: Box-drawing technical diagram

Requirements:
- Use box-drawing characters: ┌┐└┘├┤┬┴┼─│
- Use ░▒▓ for filter layers (gravel, sand, charcoal)
- Use ≈∙· for water drops/flow
- Show water flowing DOWN through layers
- Label each layer clearly
- Keep it simple and clear

Output ONLY the ASCII art, no explanations or markdown code blocks."""

try:
    response = model.generate_content(ascii_prompt)
    ascii_art = response.text

    # Save to file
    ascii_file = output_dir / "water_filter_ascii.txt"
    ascii_file.write_text(ascii_art)
    print(f"✅ ASCII saved to: {ascii_file}")
    print(f"   Size: {len(ascii_art)} bytes")
    print("\nPreview:")
    print(ascii_art)
    print()
except Exception as e:
    print(f"❌ Error generating ASCII: {e}\n")

# =============================================================================
# DEMO 2: Teletext Graphics (Web)
# =============================================================================
print("📺 Generating Teletext graphics (40×25, WST mosaic blocks)...")

teletext_prompt = """Generate Teletext graphics using HTML mosaic blocks.

SUBJECT: Heart icon
DIMENSIONS: 30 columns × 15 rows maximum
STYLE: Mosaic block graphics (2×3 pixel cells)
COLORS: WST 8-color palette

Requirements:
- Use HTML with <pre> and colored background spans
- Use &#x2588; (█) for solid blocks
- Use &#x2584; (▄) for half blocks
- Colors: red (#ff0000) for heart, black (#000000) for background
- Create a simple heart shape using blocks
- Keep it centered and symmetrical

Output the complete HTML file with inline CSS. Use this template:

<!DOCTYPE html>
<html>
<head>
<style>
body { background: #000; margin: 20px; }
pre {
    font-family: 'Courier New', monospace;
    font-size: 16px;
    line-height: 1.2;
    color: #fff;
}
.r { background: #ff0000; }
.b { background: #000000; }
</style>
</head>
<body>
<pre>[YOUR MOSAIC ART HERE]</pre>
</body>
</html>"""

try:
    response = model.generate_content(teletext_prompt)
    teletext_html = response.text

    # Save to file
    teletext_file = output_dir / "heart_teletext.html"
    teletext_file.write_text(teletext_html)
    print(f"✅ Teletext saved to: {teletext_file}")
    print(f"   Size: {len(teletext_html)} bytes")
    print()
except Exception as e:
    print(f"❌ Error generating Teletext: {e}\n")

# =============================================================================
# DEMO 3: SVG Diagram - Technical-Kinetic Style
# =============================================================================
print("📐 Generating SVG diagram (Technical-Kinetic style)...")

svg_prompt = """Generate a clean SVG diagram in Technical-Kinetic style.

SUBJECT: Fire triangle diagram
STYLE: Technical-Kinetic (geometric, precise, monochromatic)
DIMENSIONS: 400×400px
COMPLEXITY: Simple

Requirements:
- Equilateral triangle with three labeled sides
- Labels: "HEAT", "FUEL", "OXYGEN"
- Clean black lines, stroke-width: 2px
- No fills, no gradients, no colors (black lines only)
- Professional technical appearance
- Center the triangle in viewport
- Add subtle connecting elements at corners

Output ONLY the <svg>...</svg> code, no explanations or markdown code blocks.
The SVG must be complete and valid."""

try:
    response = model.generate_content(svg_prompt)
    svg = response.text.strip()

    # Clean up if wrapped in markdown code blocks
    if svg.startswith("```"):
        svg = svg.split("```")[1]
        if svg.startswith("svg\n"):
            svg = svg[4:]
        svg = svg.strip()

    # Save to file
    svg_file = output_dir / "fire_triangle_technical.svg"
    svg_file.write_text(svg)
    print(f"✅ SVG saved to: {svg_file}")
    print(f"   Size: {len(svg)} bytes")
    print()
except Exception as e:
    print(f"❌ Error generating SVG: {e}\n")

# =============================================================================
# DEMO 4: SVG Diagram - Hand-Illustrative Style
# =============================================================================
print("📐 Generating SVG diagram (Hand-Illustrative style)...")

svg_organic_prompt = """Generate an SVG diagram in Hand-Illustrative style.

SUBJECT: Simple tree with roots
STYLE: Hand-Illustrative (organic, sketchy, imperfect lines)
DIMENSIONS: 300×400px
COMPLEXITY: Simple

Requirements:
- Hand-drawn aesthetic with slightly wavy/imperfect lines
- Tree trunk, branches, and root system
- Use stroke-width: 2-3px with slight variations
- Organic, natural feel
- Black lines only, no fills or gradients
- Simple and charming

Output ONLY the <svg>...</svg> code, no explanations or markdown code blocks.
The SVG must be complete and valid."""

try:
    response = model.generate_content(svg_organic_prompt)
    svg_organic = response.text.strip()

    # Clean up if wrapped in markdown code blocks
    if svg_organic.startswith("```"):
        svg_organic = svg_organic.split("```")[1]
        if svg_organic.startswith("svg\n"):
            svg_organic = svg_organic[4:]
        svg_organic = svg_organic.strip()

    # Save to file
    svg_organic_file = output_dir / "tree_organic.svg"
    svg_organic_file.write_text(svg_organic)
    print(f"✅ SVG saved to: {svg_organic_file}")
    print(f"   Size: {len(svg_organic)} bytes")
    print()
except Exception as e:
    print(f"❌ Error generating SVG: {e}\n")

# =============================================================================
# Summary
# =============================================================================
print("=" * 80)
print("✅ MULTI-FORMAT GENERATION COMPLETE")
print("=" * 80)
print(f"\nGenerated files in: {output_dir}/")
print("\nFormats demonstrated:")
print("  📄 ASCII Art (Terminal/CLI) - water_filter_ascii.txt")
print("  📺 Teletext Graphics (Web) - heart_teletext.html")
print("  📐 SVG Technical-Kinetic - fire_triangle_technical.svg")
print("  📐 SVG Hand-Illustrative - tree_organic.svg")
print("\n" + "=" * 80)
