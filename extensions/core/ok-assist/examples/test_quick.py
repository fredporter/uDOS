#!/usr/bin/env python3
"""
Quick test of OK Assist unified API
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

def main():
    print("=" * 70)
    print("OK ASSIST - QUICK API TEST")
    print("=" * 70)

    try:
        # Initialize Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ Gemini API initialized")
        print(f"   Model: gemini-2.5-flash")

        # Test ASCII generation
        print("\n📄 Testing ASCII art generation...")
        ascii_prompt = """Generate ASCII art using C64 PetMe/PETSCII characters.

SUBJECT: Water purification filter
DIMENSIONS: 40 columns × 20 rows
STYLE: Box-drawing and technical diagram

Create a simple diagram showing water flowing through a filter with layers.
Use characters: ┌┐└┘├┤┬┴┼─│ for structure
Use ░▒▓ for filter layers
Use ≈∙· for water

Output only the ASCII art, no explanations."""

        response = model.generate_content(ascii_prompt)
        ascii_art = response.text
        print("✅ ASCII generated:")
        print(ascii_art)

        # Test SVG generation
        print("\n📐 Testing SVG generation...")
        svg_prompt = """Generate a clean SVG diagram in Technical-Kinetic style.

SUBJECT: Simple water droplet icon
STYLE: Technical-Kinetic (geometric, precise, monochromatic)
DIMENSIONS: 200×200px
COMPLEXITY: Simple

Requirements:
- Clean geometric shapes
- No gradients or colors (black lines only)
- Stroke width: 2px
- Professional technical appearance

Output only the <svg>...</svg> code, no explanations."""

        response = model.generate_content(svg_prompt)
        svg = response.text
        print(f"✅ SVG generated: {len(svg)} bytes")
        print(svg[:200] + "..." if len(svg) > 200 else svg)

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
