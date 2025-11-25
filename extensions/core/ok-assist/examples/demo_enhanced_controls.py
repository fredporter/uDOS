#!/usr/bin/env python3
"""
Demonstration of Enhanced Prompt System with Diagram Controls
v1.4.0 Phase 3 - Design Standards & Content Refresh

Generates example diagrams using the new control system across
complexity levels, styles, and formats.
"""

import sys
import os
from pathlib import Path

# Add project paths - fix doubled path issue
script_dir = Path(__file__).parent  # .../ok-assist/examples
ok_assist_dir = script_dir.parent    # .../ok-assist
prompts_file = ok_assist_dir / "prompts" / "enhanced_prompts.py"
project_root = ok_assist_dir.parent.parent.parent  # .../uDOS

# Import directly using importlib
import importlib.util
spec = importlib.util.spec_from_file_location("enhanced_prompts", prompts_file)
enhanced_prompts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enhanced_prompts)

# Get functions and constants
create_enhanced_prompt = enhanced_prompts.create_enhanced_prompt
COMPLEXITY_SIMPLE = enhanced_prompts.COMPLEXITY_SIMPLE
COMPLEXITY_DETAILED = enhanced_prompts.COMPLEXITY_DETAILED
COMPLEXITY_TECHNICAL = enhanced_prompts.COMPLEXITY_TECHNICAL
STYLE_TECHNICAL = enhanced_prompts.STYLE_TECHNICAL
STYLE_HAND_DRAWN = enhanced_prompts.STYLE_HAND_DRAWN
STYLE_HYBRID = enhanced_prompts.STYLE_HYBRID
PERSPECTIVE_ISOMETRIC = enhanced_prompts.PERSPECTIVE_ISOMETRIC
PERSPECTIVE_TOP_DOWN = enhanced_prompts.PERSPECTIVE_TOP_DOWN
PERSPECTIVE_SIDE = enhanced_prompts.PERSPECTIVE_SIDE
ANNOTATION_LABELS = enhanced_prompts.ANNOTATION_LABELS
ANNOTATION_DIMENSIONS = enhanced_prompts.ANNOTATION_DIMENSIONS
ANNOTATION_CALLOUTS = enhanced_prompts.ANNOTATION_CALLOUTS
ANNOTATION_WARNINGS = enhanced_prompts.ANNOTATION_WARNINGS
def print_section(title):
    """Print formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"{title.center(80)}")
    print(f"{'=' * 80}\n")


def save_prompt(prompt, filename):
    """Save prompt to file for reference."""
    output_dir = project_root / "extensions" / "core" / "ok-assist" / "examples" / "prompts"
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename
    with open(filepath, 'w') as f:
        f.write(prompt)

    print(f"✅ Saved to: {filepath}")
    return filepath


def demo_complexity_levels():
    """Demonstrate three complexity levels with same topic."""
    print_section("COMPLEXITY LEVELS DEMO: Water Purification Filter")

    base_params = {
        "category": "water",
        "topic": "DIY Water Purification Filter",
        "description": "Multi-layer gravity filter using sand, charcoal, and gravel",
        "format_type": "svg",
        "style": STYLE_HYBRID,
        "perspective": PERSPECTIVE_SIDE
    }

    # Simple version
    print("\n1. SIMPLE (Emergency Quick Reference)")
    print("-" * 80)
    simple_prompt = create_enhanced_prompt(
        **base_params,
        complexity=COMPLEXITY_SIMPLE,
        annotations=[ANNOTATION_LABELS]
    )
    print(simple_prompt[:500] + "...\n")
    save_prompt(simple_prompt, "water_filter_simple.txt")

    # Detailed version
    print("\n2. DETAILED (Training Manual)")
    print("-" * 80)
    detailed_prompt = create_enhanced_prompt(
        **base_params,
        complexity=COMPLEXITY_DETAILED,
        annotations=[ANNOTATION_LABELS, ANNOTATION_CALLOUTS, ANNOTATION_WARNINGS]
    )
    print(detailed_prompt[:500] + "...\n")
    save_prompt(detailed_prompt, "water_filter_detailed.txt")

    # Technical version
    print("\n3. TECHNICAL (Expert Reference)")
    print("-" * 80)
    technical_prompt = create_enhanced_prompt(
        **base_params,
        complexity=COMPLEXITY_TECHNICAL,
        annotations=[ANNOTATION_LABELS, ANNOTATION_DIMENSIONS,
                    ANNOTATION_CALLOUTS, ANNOTATION_WARNINGS]
    )
    print(technical_prompt[:500] + "...\n")
    save_prompt(technical_prompt, "water_filter_technical.txt")


def demo_style_variations():
    """Demonstrate three style variations with same topic."""
    print_section("STYLE VARIATIONS DEMO: Debris Hut Construction")

    base_params = {
        "category": "shelter",
        "topic": "Debris Hut Construction",
        "description": "Emergency shelter built from natural materials",
        "format_type": "svg",
        "complexity": COMPLEXITY_DETAILED,
        "perspective": PERSPECTIVE_ISOMETRIC
    }

    # Technical style
    print("\n1. TECHNICAL-KINETIC (Engineering Blueprint)")
    print("-" * 80)
    technical_prompt = create_enhanced_prompt(
        **base_params,
        style=STYLE_TECHNICAL,
        annotations=[ANNOTATION_LABELS, ANNOTATION_DIMENSIONS]
    )
    print(technical_prompt[:500] + "...\n")
    save_prompt(technical_prompt, "debris_hut_technical.txt")

    # Hand-drawn style
    print("\n2. HAND-ILLUSTRATIVE (Field Guide)")
    print("-" * 80)
    hand_prompt = create_enhanced_prompt(
        **base_params,
        style=STYLE_HAND_DRAWN,
        annotations=[ANNOTATION_LABELS, ANNOTATION_CALLOUTS]
    )
    print(hand_prompt[:500] + "...\n")
    save_prompt(hand_prompt, "debris_hut_hand_drawn.txt")

    # Hybrid style
    print("\n3. HYBRID (Professional + Approachable)")
    print("-" * 80)
    hybrid_prompt = create_enhanced_prompt(
        **base_params,
        style=STYLE_HYBRID,
        annotations=[ANNOTATION_LABELS, ANNOTATION_CALLOUTS, ANNOTATION_WARNINGS]
    )
    print(hybrid_prompt[:500] + "...\n")
    save_prompt(hybrid_prompt, "debris_hut_hybrid.txt")


def demo_perspective_options():
    """Demonstrate perspective options with same topic."""
    print_section("PERSPECTIVE OPTIONS DEMO: Campfire Fire Lay")

    base_params = {
        "category": "fire",
        "topic": "Log Cabin Fire Lay",
        "description": "Structured fire lay for long-burning campfire",
        "format_type": "svg",
        "complexity": COMPLEXITY_DETAILED,
        "style": STYLE_TECHNICAL
    }

    # Isometric
    print("\n1. ISOMETRIC (3D View)")
    print("-" * 80)
    iso_prompt = create_enhanced_prompt(
        **base_params,
        perspective=PERSPECTIVE_ISOMETRIC,
        annotations=[ANNOTATION_LABELS]
    )
    print(iso_prompt[:500] + "...\n")
    save_prompt(iso_prompt, "fire_lay_isometric.txt")

    # Top-down
    print("\n2. TOP-DOWN (Plan View)")
    print("-" * 80)
    top_prompt = create_enhanced_prompt(
        **base_params,
        perspective=PERSPECTIVE_TOP_DOWN,
        annotations=[ANNOTATION_LABELS, ANNOTATION_DIMENSIONS]
    )
    print(top_prompt[:500] + "...\n")
    save_prompt(top_prompt, "fire_lay_top_down.txt")

    # Side view
    print("\n3. SIDE (Elevation View)")
    print("-" * 80)
    side_prompt = create_enhanced_prompt(
        **base_params,
        perspective=PERSPECTIVE_SIDE,
        annotations=[ANNOTATION_LABELS, ANNOTATION_CALLOUTS]
    )
    print(side_prompt[:500] + "...\n")
    save_prompt(side_prompt, "fire_lay_side.txt")


def demo_format_variations():
    """Demonstrate same diagram across three formats."""
    print_section("FORMAT VARIATIONS DEMO: CPR Chest Compressions")

    base_params = {
        "category": "medical",
        "topic": "CPR Chest Compressions",
        "description": "Proper hand position and compression technique for adult CPR",
        "complexity": COMPLEXITY_DETAILED,
        "style": STYLE_HYBRID,
        "perspective": PERSPECTIVE_TOP_DOWN
    }

    # ASCII
    print("\n1. ASCII (Terminal/CLI)")
    print("-" * 80)
    ascii_prompt = create_enhanced_prompt(
        **base_params,
        format_type="ascii",
        annotations=[ANNOTATION_LABELS, ANNOTATION_WARNINGS]
    )
    print(ascii_prompt[:500] + "...\n")
    save_prompt(ascii_prompt, "cpr_ascii.txt")

    # Teletext
    print("\n2. TELETEXT (Retro Web)")
    print("-" * 80)
    teletext_prompt = create_enhanced_prompt(
        **base_params,
        format_type="teletext",
        annotations=[ANNOTATION_LABELS, ANNOTATION_WARNINGS]
    )
    print(teletext_prompt[:500] + "...\n")
    save_prompt(teletext_prompt, "cpr_teletext.txt")

    # SVG
    print("\n3. SVG (High Quality)")
    print("-" * 80)
    svg_prompt = create_enhanced_prompt(
        **base_params,
        format_type="svg",
        annotations=[ANNOTATION_LABELS, ANNOTATION_CALLOUTS, ANNOTATION_WARNINGS]
    )
    print(svg_prompt[:500] + "...\n")
    save_prompt(svg_prompt, "cpr_svg.txt")


def demo_control_presets():
    """Demonstrate quick preset configurations."""
    print_section("CONTROL PRESETS DEMO")

    # Emergency reference card
    print("\n1. EMERGENCY REFERENCE CARD (Simple + ASCII)")
    print("-" * 80)
    emergency_prompt = create_enhanced_prompt(
        category="navigation",
        topic="Lost Person STOP Protocol",
        description="Stop, Think, Observe, Plan - emergency procedure when lost",
        format_type="ascii",
        complexity=COMPLEXITY_SIMPLE,
        style=STYLE_TECHNICAL,
        annotations=[ANNOTATION_LABELS]
    )
    print(emergency_prompt[:500] + "...\n")
    save_prompt(emergency_prompt, "preset_emergency.txt")

    # Training manual
    print("\n2. TRAINING MANUAL (Detailed + Hybrid + SVG)")
    print("-" * 80)
    training_prompt = create_enhanced_prompt(
        category="tools",
        topic="Axe Safety and Technique",
        description="Proper axe use including grip, stance, and swing technique",
        format_type="svg",
        complexity=COMPLEXITY_DETAILED,
        style=STYLE_HYBRID,
        perspective=PERSPECTIVE_SIDE,
        annotations=[ANNOTATION_LABELS, ANNOTATION_CALLOUTS, ANNOTATION_WARNINGS]
    )
    print(training_prompt[:500] + "...\n")
    save_prompt(training_prompt, "preset_training.txt")

    # Field guide
    print("\n3. FIELD GUIDE (Detailed + Hand-Drawn + SVG)")
    print("-" * 80)
    field_prompt = create_enhanced_prompt(
        category="food",
        topic="Edible Plant Identification",
        description="Visual guide to identifying safe edible plants vs toxic lookalikes",
        format_type="svg",
        complexity=COMPLEXITY_DETAILED,
        style=STYLE_HAND_DRAWN,
        annotations=[ANNOTATION_LABELS, ANNOTATION_CALLOUTS, ANNOTATION_WARNINGS]
    )
    print(field_prompt[:500] + "...\n")
    save_prompt(field_prompt, "preset_field_guide.txt")


def main():
    """Run all demonstration examples."""
    print_section("ENHANCED PROMPT SYSTEM DEMONSTRATION")
    print("v1.4.0 Phase 3 - Design Standards & Content Refresh")
    print("\nThis demonstration shows the new control system for generating")
    print("consistent, high-quality diagrams across complexity levels,")
    print("visual styles, perspectives, and output formats.")

    try:
        # Run all demos
        demo_complexity_levels()
        demo_style_variations()
        demo_perspective_options()
        demo_format_variations()
        demo_control_presets()

        # Summary
        print_section("DEMONSTRATION COMPLETE")
        print("Generated 15 example prompts showing:")
        print("  ✅ 3 complexity levels (simple, detailed, technical)")
        print("  ✅ 3 visual styles (technical, hand-drawn, hybrid)")
        print("  ✅ 3 perspectives (isometric, top-down, side)")
        print("  ✅ 3 formats (ASCII, Teletext, SVG)")
        print("  ✅ 3 control presets (emergency, training, field guide)")
        print("\nAll prompts saved to: extensions/core/ok-assist/examples/prompts/")
        print("\nNext step: Use these prompts with OK Assist to generate actual diagrams")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
