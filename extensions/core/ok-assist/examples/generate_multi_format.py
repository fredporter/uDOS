#!/usr/bin/env python3
"""
OK Assist - Multi-Format Generation Demo

Demonstrates generating the same content in ASCII, Teletext, and SVG formats
using the unified design system with C64 PetMe as the reference point.
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

# Initialize model
model = genai.GenerativeModel("gemini-2.5-flash")


def demo_water_filter():
    """Generate water filter diagram in all formats"""
    print("=" * 80)
    print("DEMO: Water Filter - All Formats")
    print("=" * 80)

    ok = OKAssist()

    subject = "DIY water filter"
    description = "Multi-layer gravel, sand, and charcoal filtration system with flow direction"

    # 1. ASCII Art (Terminal/CLI)
    print("\n📄 Generating ASCII art (80×24, PetMe character set)...")
    ascii_art = ok.generate_ascii(
        subject=subject,
        description=description,
        width=80,
        height=24,
        style="petme"
    )

    ascii_path = Path("knowledge/diagrams/ascii/water-filter.txt")
    ascii_path.parent.mkdir(parents=True, exist_ok=True)
    ascii_path.write_text(ascii_art)
    print(f"   ✓ Saved ASCII: {ascii_path} ({len(ascii_art)} bytes)")

    # 2. Teletext Graphics (Web/Color)
    print("\n🎨 Generating Teletext mosaic (40×25, WST colors)...")
    teletext_html = ok.generate_teletext(
        subject=subject,
        description=description,
        width=40,
        height=25,
        colors=["BLUE", "CYAN", "YELLOW", "WHITE"],
        style="mosaic"
    )

    teletext_path = Path("knowledge/diagrams/teletext/water-filter.html")
    teletext_path.parent.mkdir(parents=True, exist_ok=True)
    teletext_path.write_text(teletext_html)
    print(f"   ✓ Saved Teletext: {teletext_path} ({len(teletext_html.encode('utf-8')) / 1024:.1f}KB)")

    # 3. SVG Technical (Vector/Print)
    print("\n📐 Generating SVG technical diagram (scalable vector)...")
    svg_technical = ok.generate_svg(
        subject=subject,
        style="technical-kinetic",
        description=description,
        complexity="moderate"
    )

    svg_path = Path("knowledge/diagrams/water/water-filter-technical.svg")
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg_technical)
    print(f"   ✓ Saved SVG: {svg_path} ({len(svg_technical.encode('utf-8')) / 1024:.1f}KB)")

    print("\n✅ Water filter generated in 3 formats!\n")


def demo_heart_anatomy():
    """Generate heart anatomy in all formats"""
    print("=" * 80)
    print("DEMO: Heart Anatomy - All Formats")
    print("=" * 80)

    ok = OKAssist()

    subject = "human heart cross-section"
    description = "Four chambers (atria and ventricles), valves, major vessels with labels"

    # 1. ASCII Art
    print("\n📄 Generating ASCII art (80×24, PetMe character set)...")
    ascii_art = ok.generate_ascii(
        subject=subject,
        description=description,
        width=80,
        height=24,
        style="box-drawing"
    )

    ascii_path = Path("knowledge/diagrams/ascii/heart-anatomy.txt")
    ascii_path.parent.mkdir(parents=True, exist_ok=True)
    ascii_path.write_text(ascii_art)
    print(f"   ✓ Saved ASCII: {ascii_path} ({len(ascii_art)} bytes)")

    # 2. Teletext Graphics
    print("\n🎨 Generating Teletext mosaic (40×25, WST colors)...")
    teletext_html = ok.generate_teletext(
        subject=subject,
        description=description,
        width=40,
        height=25,
        colors=["RED", "BLUE", "MAGENTA", "WHITE"],
        style="contiguous"
    )

    teletext_path = Path("knowledge/diagrams/teletext/heart-anatomy.html")
    teletext_path.parent.mkdir(parents=True, exist_ok=True)
    teletext_path.write_text(teletext_html)
    print(f"   ✓ Saved Teletext: {teletext_path} ({len(teletext_html.encode('utf-8')) / 1024:.1f}KB)")

    # 3. SVG Hand-Illustrative
    print("\n🎨 Generating SVG organic illustration (scalable vector)...")
    svg_organic = ok.generate_svg(
        subject=subject,
        style="hand-illustrative",
        description=description,
        complexity="detailed"
    )

    svg_path = Path("knowledge/diagrams/medical/heart-anatomy-detailed.svg")
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg_organic)
    print(f"   ✓ Saved SVG: {svg_path} ({len(svg_organic.encode('utf-8')) / 1024:.1f}KB)")

    print("\n✅ Heart anatomy generated in 3 formats!\n")


def demo_all_formats_comparison():
    """Generate same subject in all formats for comparison"""
    print("=" * 80)
    print("DEMO: Format Comparison - Fire Triangle")
    print("=" * 80)

    ok = OKAssist()

    subject = "fire triangle"
    description = "Heat, fuel, and oxygen - the three elements needed for fire"

    print(f"\n🔥 Generating '{subject}' in all formats...")

    # Use unified API
    all_formats = ok.generate_all_formats(subject, description)

    # Save each format
    output_dir = Path("knowledge/diagrams")

    # ASCII
    ascii_path = output_dir / "ascii" / "fire-triangle.txt"
    ascii_path.parent.mkdir(parents=True, exist_ok=True)
    ascii_path.write_text(all_formats["ascii"])
    print(f"   ✓ ASCII:             {ascii_path} ({len(all_formats['ascii'])} bytes)")

    # Teletext
    teletext_path = output_dir / "teletext" / "fire-triangle.html"
    teletext_path.parent.mkdir(parents=True, exist_ok=True)
    teletext_path.write_text(all_formats["teletext"])
    print(f"   ✓ Teletext:          {teletext_path} ({len(all_formats['teletext'].encode('utf-8')) / 1024:.1f}KB)")

    # SVG Technical
    svg_tech_path = output_dir / "fire" / "fire-triangle-technical.svg"
    svg_tech_path.parent.mkdir(parents=True, exist_ok=True)
    svg_tech_path.write_text(all_formats["svg_technical"])
    print(f"   ✓ SVG Technical:     {svg_tech_path} ({len(all_formats['svg_technical'].encode('utf-8')) / 1024:.1f}KB)")

    # SVG Organic
    svg_org_path = output_dir / "fire" / "fire-triangle-organic.svg"
    svg_org_path.parent.mkdir(parents=True, exist_ok=True)
    svg_org_path.write_text(all_formats["svg_organic"])
    print(f"   ✓ SVG Organic:       {svg_org_path} ({len(all_formats['svg_organic'].encode('utf-8')) / 1024:.1f}KB)")

    print("\n✅ Fire triangle generated in 4 variations!\n")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("OK ASSIST - MULTI-FORMAT GENERATION DEMO")
    print("Unified Design System: ASCII / Teletext / SVG")
    print("Reference: C64 PetMe Character Set")
    print("=" * 80 + "\n")

    try:
        # Demo 1: Technical subject (water filter)
        demo_water_filter()

        # Demo 2: Organic subject (heart anatomy)
        demo_heart_anatomy()

        # Demo 3: All formats comparison
        demo_all_formats_comparison()

        print("=" * 80)
        print("✅ ALL DEMOS COMPLETE")
        print("=" * 80)
        print("\nGenerated files:")
        print("  - knowledge/diagrams/ascii/*.txt")
        print("  - knowledge/diagrams/teletext/*.html")
        print("  - knowledge/diagrams/{category}/*.svg")
        print("\nView demos:")
        print("  - ASCII: cat knowledge/diagrams/ascii/water-filter.txt")
        print("  - Teletext: open knowledge/diagrams/teletext/water-filter.html")
        print("  - SVG: open knowledge/diagrams/water/water-filter-technical.svg")
        print()

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure GEMINI_API_KEY is set in .env file")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
