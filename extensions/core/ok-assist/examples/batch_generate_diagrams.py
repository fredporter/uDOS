#!/usr/bin/env python3
"""
Batch Diagram Generator - Multi-Format

Generates diagrams across multiple categories in ASCII, Teletext, and SVG formats.
Focus on expanding the diagram library efficiently.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Get project root and load .env
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Output directories
diagrams_dir = project_root / "knowledge" / "diagrams"
ascii_dir = diagrams_dir / "ascii"
teletext_dir = diagrams_dir / "teletext"

# Ensure directories exist
ascii_dir.mkdir(parents=True, exist_ok=True)
teletext_dir.mkdir(parents=True, exist_ok=True)

# Diagram generation queue
DIAGRAM_QUEUE = [
    # Shelter category (high priority - only 2/70)
    {
        'category': 'shelter',
        'subject': 'Debris hut construction',
        'description': 'A-frame debris hut with ribbing and insulation layers',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'shelter',
        'subject': 'Lean-to shelter',
        'description': 'Simple lean-to with reflector wall and fire placement',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'shelter',
        'subject': 'Tarp shelter configurations',
        'description': 'Four basic tarp shelter setups: A-frame, lean-to, flying diamond, C-fly',
        'formats': ['ascii'],
        'svg_style': None
    },

    # Food category (high priority - only 1/60)
    {
        'category': 'food',
        'subject': 'Edible vs poisonous plants',
        'description': 'Side-by-side comparison showing key identification features',
        'formats': ['ascii', 'svg'],
        'svg_style': 'organic'
    },
    {
        'category': 'food',
        'subject': 'Fish trap construction',
        'description': 'Funnel trap design with entry and holding chamber',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'food',
        'subject': 'Food preservation methods',
        'description': 'Smoking, drying, salting techniques with equipment',
        'formats': ['ascii'],
        'svg_style': None
    },

    # Fire category (expand from 4/50)
    {
        'category': 'fire',
        'subject': 'Bow drill components',
        'description': 'Bow drill fire starting showing spindle, hearth board, bow, and bearing block',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'fire',
        'subject': 'Fire lay configurations',
        'description': 'Teepee, log cabin, lean-to, and platform fire structures',
        'formats': ['ascii'],
        'svg_style': None
    },

    # Navigation (expand from 5/50)
    {
        'category': 'navigation',
        'subject': 'Shadow stick method',
        'description': 'Finding direction using shadow movement over time',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'navigation',
        'subject': 'Star navigation basics',
        'description': 'Southern Cross and pointer stars for south, with angles',
        'formats': ['ascii', 'teletext'],
        'svg_style': None
    },
]

def generate_ascii(subject, description, category):
    """Generate ASCII art diagram"""
    prompt = f"""Generate ASCII art using C64 PetMe/PETSCII characters (UTF-8).

SUBJECT: {subject}
CATEGORY: {category}
DESCRIPTION: {description}
DIMENSIONS: 70 columns × 25 rows maximum
STYLE: Box-drawing technical diagram

Requirements:
- Use box-drawing characters: ┌┐└┘├┤┬┴┼─│
- Use ░▒▓ for shading/textures/fill
- Use ≈∙· for particles/water/flow
- Use ○●◊◆ for markers/points
- Label all components clearly
- Keep it simple and readable
- Show key features and parts

Output ONLY the ASCII art, no explanations or markdown code blocks."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def generate_teletext(subject, description, category):
    """Generate Teletext HTML diagram"""
    prompt = f"""Generate Teletext graphics using HTML mosaic blocks.

SUBJECT: {subject}
CATEGORY: {category}
DESCRIPTION: {description}
DIMENSIONS: 35 columns × 20 rows maximum
STYLE: Mosaic block graphics (2×3 pixel cells)
COLORS: WST 8-color palette

Requirements:
- Use HTML with <pre> and colored background spans
- Use &#x2588; (█) for solid blocks
- Use &#x2584; (▄) for half blocks
- WST colors: red (#ff0000), green (#00ff00), yellow (#ffff00),
              blue (#0000ff), magenta (#ff00ff), cyan (#00ffff),
              white (#ffffff), black (#000000)
- Create clear, recognizable shapes
- Keep it simple and chunky

Output complete HTML file with inline CSS. Use this structure:
<!DOCTYPE html>
<html>
<head>
<style>
body {{ background: #000; margin: 20px; }}
pre {{ font-family: monospace; font-size: 16px; line-height: 1; }}
.r {{ background: #ff0000; }} .g {{ background: #00ff00; }}
.y {{ background: #ffff00; }} .b {{ background: #0000ff; }}
.m {{ background: #ff00ff; }} .c {{ background: #00ffff; }}
.w {{ background: #ffffff; }}
</style>
</head>
<body>
<pre>[YOUR MOSAIC ART HERE]</pre>
</body>
</html>"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def generate_svg(subject, description, category, style='technical'):
    """Generate SVG diagram"""
    if style == 'technical':
        style_desc = "Technical-Kinetic (geometric, precise, monochromatic)"
        requirements = """- Clean geometric shapes
- Black lines only, stroke-width: 2px
- No gradients or colors
- Professional technical appearance
- Clear labeling with Arial font"""
    else:  # organic
        style_desc = "Hand-Illustrative (organic, sketchy, imperfect lines)"
        requirements = """- Hand-drawn aesthetic with slightly wavy lines
- Stroke-width: 2-3px with variations
- Organic, natural feel
- Black lines only, no fills or gradients
- Simple and charming"""

    prompt = f"""Generate a clean SVG diagram.

SUBJECT: {subject}
CATEGORY: {category}
DESCRIPTION: {description}
STYLE: {style_desc}
DIMENSIONS: 400×400px
COMPLEXITY: Simple to moderate

Requirements:
{requirements}
- Scalable and production-ready
- Clear component labels

Output ONLY the <svg>...</svg> code, no explanations or markdown code blocks.
The SVG must be complete and valid."""

    try:
        response = model.generate_content(prompt)
        svg = response.text.strip()

        # Clean up markdown code blocks if present
        if svg.startswith("```"):
            svg = svg.split("```")[1]
            if svg.startswith("svg\n"):
                svg = svg[4:]
            svg = svg.strip()

        return svg
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def main():
    print("=" * 80)
    print("BATCH DIAGRAM GENERATOR - Multi-Format Expansion")
    print("=" * 80)
    print(f"\nOutput directory: {diagrams_dir}")
    print(f"Diagrams to generate: {len(DIAGRAM_QUEUE)}")
    print()

    generated_count = 0
    failed_count = 0

    for i, item in enumerate(DIAGRAM_QUEUE, 1):
        category = item['category']
        subject = item['subject']
        description = item['description']
        formats = item['formats']
        svg_style = item.get('svg_style', 'technical')

        print(f"[{i}/{len(DIAGRAM_QUEUE)}] {subject} ({category})")

        # Create category directories if needed
        category_dir = diagrams_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename base
        filename_base = subject.lower().replace(' ', '-').replace(',', '')

        # Generate requested formats
        for format_type in formats:
            if format_type == 'ascii':
                print(f"  📄 Generating ASCII...")
                content = generate_ascii(subject, description, category)
                if content:
                    output_file = ascii_dir / f"{filename_base}.txt"
                    output_file.write_text(content)
                    print(f"  ✅ ASCII saved: {output_file.name} ({len(content)} bytes)")
                    generated_count += 1
                else:
                    failed_count += 1
                time.sleep(2)  # Rate limiting

            elif format_type == 'teletext':
                print(f"  📺 Generating Teletext...")
                content = generate_teletext(subject, description, category)
                if content:
                    output_file = teletext_dir / f"{filename_base}.html"
                    output_file.write_text(content)
                    print(f"  ✅ Teletext saved: {output_file.name} ({len(content)} bytes)")
                    generated_count += 1
                else:
                    failed_count += 1
                time.sleep(2)  # Rate limiting

            elif format_type == 'svg':
                print(f"  📐 Generating SVG ({svg_style})...")
                content = generate_svg(subject, description, category, svg_style)
                if content:
                    output_file = category_dir / f"{filename_base}.svg"
                    output_file.write_text(content)
                    print(f"  ✅ SVG saved: {output_file.name} ({len(content)} bytes)")
                    generated_count += 1
                else:
                    failed_count += 1
                time.sleep(2)  # Rate limiting

        print()

    # Summary
    print("=" * 80)
    print("BATCH GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated: {generated_count} files")
    print(f"Failed: {failed_count} files")
    print(f"\nOutput locations:")
    print(f"  ASCII: {ascii_dir}/")
    print(f"  Teletext: {teletext_dir}/")
    print(f"  SVG: {diagrams_dir}/[category]/")
    print()

if __name__ == "__main__":
    main()
