#!/usr/bin/env python3
"""
Batch Generator - Cycle 2
Focus on balancing categories and reaching 100 diagrams
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Setup (same as batch 1)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

diagrams_dir = project_root / "knowledge" / "diagrams"
ascii_dir = diagrams_dir / "ascii"
teletext_dir = diagrams_dir / "teletext"

ascii_dir.mkdir(parents=True, exist_ok=True)
teletext_dir.mkdir(parents=True, exist_ok=True)

# Batch 2 Queue - Focus on underserved categories
DIAGRAM_QUEUE = [
    # Shelter (priority - only 4/70 = 5.7%)
    {
        'category': 'shelter',
        'subject': 'Emergency bivouac',
        'description': 'Quick overnight shelter using natural materials',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'shelter',
        'subject': 'Snow cave construction',
        'description': 'Winter emergency shelter with ventilation and sleeping platform',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'shelter',
        'subject': 'Shelter site selection',
        'description': 'Decision tree for choosing shelter location (drainage, wind, hazards)',
        'formats': ['ascii'],
        'svg_style': None
    },

    # Food (priority - only 3/60 = 5.0%)
    {
        'category': 'food',
        'subject': 'Snare trap types',
        'description': 'Simple snare, spring snare, and deadfall trap designs',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'food',
        'subject': 'Cooking methods',
        'description': 'Rock boiling, hot stone cooking, ember roasting techniques',
        'formats': ['ascii'],
        'svg_style': None
    },
    {
        'category': 'food',
        'subject': 'Food safety timeline',
        'description': 'Storage times and spoilage indicators for preserved foods',
        'formats': ['ascii', 'teletext'],
        'svg_style': None
    },

    # Medical (expand from 8/80 = 10%)
    {
        'category': 'medical',
        'subject': 'Splinting techniques',
        'description': 'Improvised splints for arm, leg, and finger injuries',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'medical',
        'subject': 'Wound care steps',
        'description': 'Clean, disinfect, dress, monitor - step-by-step process',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },

    # Tools (expand from 8/60 = 13.3%)
    {
        'category': 'tools',
        'subject': 'Knife safety and grip',
        'description': 'Proper knife handling, safe cutting techniques, and grips',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'tools',
        'subject': 'Improvised cordage',
        'description': 'Making rope from natural fibers - reverse wrap technique',
        'formats': ['ascii', 'svg'],
        'svg_style': 'organic'
    },

    # Navigation (expand from 5/50 = 10%)
    {
        'category': 'navigation',
        'subject': 'Pace counting method',
        'description': 'Distance estimation using step counting and terrain',
        'formats': ['ascii', 'svg'],
        'svg_style': 'technical'
    },
    {
        'category': 'navigation',
        'subject': 'Map reading basics',
        'description': 'Topographic symbols, contour lines, scale interpretation',
        'formats': ['ascii', 'teletext'],
        'svg_style': None
    },
]

# Copy generation functions from batch 1
def generate_ascii(subject, description, category):
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

Output complete HTML file with inline CSS."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def generate_svg(subject, description, category, style='technical'):
    if style == 'technical':
        style_desc = "Technical-Kinetic (geometric, precise, monochromatic)"
        requirements = """- Clean geometric shapes
- Black lines only, stroke-width: 2px
- Professional technical appearance"""
    else:
        style_desc = "Hand-Illustrative (organic, sketchy, imperfect lines)"
        requirements = """- Hand-drawn aesthetic with wavy lines
- Stroke-width: 2-3px with variations
- Organic, natural feel"""

    prompt = f"""Generate a clean SVG diagram.

SUBJECT: {subject}
CATEGORY: {category}
DESCRIPTION: {description}
STYLE: {style_desc}
DIMENSIONS: 400×400px

Requirements:
{requirements}
- Clear component labels
- Scalable and production-ready

Output ONLY the <svg>...</svg> code, no explanations or markdown code blocks."""

    try:
        response = model.generate_content(prompt)
        svg = response.text.strip()

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
    print("BATCH GENERATOR - Cycle 2 (Category Balancing)")
    print("=" * 80)
    print(f"Diagrams to generate: {len(DIAGRAM_QUEUE)}")
    print()

    generated = 0
    failed = 0

    for i, item in enumerate(DIAGRAM_QUEUE, 1):
        category = item['category']
        subject = item['subject']
        description = item['description']
        formats = item['formats']
        svg_style = item.get('svg_style', 'technical')

        print(f"[{i}/{len(DIAGRAM_QUEUE)}] {subject} ({category})")

        category_dir = diagrams_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        filename_base = subject.lower().replace(' ', '-').replace(',', '')

        for format_type in formats:
            if format_type == 'ascii':
                print(f"  📄 Generating ASCII...")
                content = generate_ascii(subject, description, category)
                if content:
                    (ascii_dir / f"{filename_base}.txt").write_text(content)
                    print(f"  ✅ ASCII saved ({len(content)} bytes)")
                    generated += 1
                else:
                    failed += 1
                time.sleep(2)

            elif format_type == 'teletext':
                print(f"  📺 Generating Teletext...")
                content = generate_teletext(subject, description, category)
                if content:
                    (teletext_dir / f"{filename_base}.html").write_text(content)
                    print(f"  ✅ Teletext saved ({len(content)} bytes)")
                    generated += 1
                else:
                    failed += 1
                time.sleep(2)

            elif format_type == 'svg':
                print(f"  📐 Generating SVG ({svg_style})...")
                content = generate_svg(subject, description, category, svg_style)
                if content:
                    (category_dir / f"{filename_base}.svg").write_text(content)
                    print(f"  ✅ SVG saved ({len(content)} bytes)")
                    generated += 1
                else:
                    failed += 1
                time.sleep(2)

        print()

    print("=" * 80)
    print("BATCH 2 COMPLETE")
    print("=" * 80)
    print(f"Generated: {generated} | Failed: {failed}")
    print()

if __name__ == "__main__":
    main()
