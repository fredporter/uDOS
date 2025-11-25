#!/usr/bin/env python3
"""
OK Assist Integration Example
Demonstrates technical-kinetic and hand-illustrative SVG generation
"""

import sys
import os
from pathlib import Path

# Add OK Assist to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.gemini import OKAssist


def generate_example_diagrams():
    """Generate example diagrams in both styles"""

    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  GEMINI_API_KEY not set. Set with: export GEMINI_API_KEY='your-key'")
        return

    ok = OKAssist()

    # Output directory
    output_dir = Path(__file__).parent.parent.parent.parent.parent / 'knowledge' / 'diagrams'

    print("\n" + "="*60)
    print("OK ASSIST - SVG GENERATION EXAMPLES")
    print("="*60)

    # ========================================
    # TECHNICAL-KINETIC EXAMPLES
    # ========================================

    print("\n📐 TECHNICAL-KINETIC STYLE (Tools, Systems, UI)")
    print("-" * 60)

    technical_subjects = [
        {
            "subject": "axe safety zones",
            "description": "Safe chopping stance with clearance zones marked",
            "complexity": "moderate",
            "output": output_dir / "tools" / "axe-safety-zones.svg"
        },
        {
            "subject": "water filter cross-section",
            "description": "Multi-layer filtration system showing gravel, sand, charcoal layers",
            "complexity": "moderate",
            "output": output_dir / "water" / "filter-cross-section.svg"
        },
        {
            "subject": "bowline knot diagram",
            "description": "Step-by-step rope path for tying a bowline",
            "complexity": "simple",
            "output": output_dir / "tools" / "bowline-knot-steps.svg"
        }
    ]

    for example in technical_subjects:
        print(f"\n  Generating: {example['subject']}")
        print(f"  Description: {example['description']}")
        print(f"  Complexity: {example['complexity']}")

        try:
            svg = ok.generate_svg(
                subject=example['subject'],
                style="technical-kinetic",
                description=example['description'],
                complexity=example['complexity']
            )

            # Save to file
            example['output'].parent.mkdir(parents=True, exist_ok=True)
            with open(example['output'], 'w') as f:
                f.write(svg)

            size_kb = len(svg.encode('utf-8')) / 1024
            print(f"  ✓ Saved: {example['output'].name} ({size_kb:.1f}KB)")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    # ========================================
    # HAND-ILLUSTRATIVE EXAMPLES
    # ========================================

    print("\n\n🌿 HAND-ILLUSTRATIVE STYLE (Anatomy, Plants, Nature)")
    print("-" * 60)

    organic_subjects = [
        {
            "subject": "human heart anatomy",
            "description": "Cross-section showing four chambers, valves, and major vessels",
            "complexity": "detailed",
            "output": output_dir / "medical" / "heart-anatomy.svg"
        },
        {
            "subject": "oak leaf structure",
            "description": "Detailed leaf showing veins, lobes, and cellular structure",
            "complexity": "moderate",
            "output": output_dir / "food" / "oak-leaf-structure.svg"
        },
        {
            "subject": "rope fiber detail",
            "description": "Close-up of twisted natural fiber rope showing weave pattern",
            "complexity": "simple",
            "output": output_dir / "tools" / "rope-fiber-detail.svg"
        },
        {
            "subject": "mountain landscape with river",
            "description": "Natural scene with layered depth: foreground rocks, midground trees, background peaks",
            "complexity": "moderate",
            "output": output_dir / "navigation" / "mountain-landscape.svg"
        }
    ]

    for example in organic_subjects:
        print(f"\n  Generating: {example['subject']}")
        print(f"  Description: {example['description']}")
        print(f"  Complexity: {example['complexity']}")

        try:
            svg = ok.generate_svg(
                subject=example['subject'],
                style="hand-illustrative",
                description=example['description'],
                complexity=example['complexity']
            )

            # Save to file
            example['output'].parent.mkdir(parents=True, exist_ok=True)
            with open(example['output'], 'w') as f:
                f.write(svg)

            size_kb = len(svg.encode('utf-8')) / 1024
            print(f"  ✓ Saved: {example['output'].name} ({size_kb:.1f}KB)")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    # ========================================
    # AUTO-DETECTION EXAMPLES
    # ========================================

    print("\n\n🤖 AUTO-STYLE DETECTION")
    print("-" * 60)

    auto_subjects = [
        "compass rose",
        "digestive system",
        "shelter frame construction",
        "pine tree cross-section",
        "signal mirror technique",
        "blood circulation"
    ]

    for subject in auto_subjects:
        detected_style = ok.auto_detect_style(subject)
        print(f"  '{subject}' → {detected_style}")

    print("\n" + "="*60)
    print("✓ Example generation complete!")
    print("="*60 + "\n")


def demonstrate_style_comparison():
    """Generate same subject in both styles for comparison"""

    if not os.getenv("GEMINI_API_KEY"):
        return

    ok = OKAssist()
    output_dir = Path(__file__).parent.parent.parent.parent.parent / 'knowledge' / 'diagrams' / 'system'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print("STYLE COMPARISON: Same Subject, Different Styles")
    print("="*60)

    subject = "wood splitting technique"
    description = "Person splitting log with axe, showing proper stance and wedge placement"

    # Technical version
    print(f"\n📐 Technical-Kinetic: {subject}")
    try:
        tech_svg = ok.generate_svg(
            subject=subject,
            style="technical-kinetic",
            description=description + " (diagram with measurement annotations)",
            complexity="moderate"
        )

        tech_file = output_dir / "wood-splitting-technical.svg"
        with open(tech_file, 'w') as f:
            f.write(tech_svg)

        print(f"  ✓ Saved: {tech_file.name} ({len(tech_svg.encode('utf-8')) / 1024:.1f}KB)")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Organic version
    print(f"\n🌿 Hand-Illustrative: {subject}")
    try:
        organic_svg = ok.generate_svg(
            subject=subject,
            style="hand-illustrative",
            description=description + " (natural line-art illustration)",
            complexity="moderate"
        )

        organic_file = output_dir / "wood-splitting-organic.svg"
        with open(organic_file, 'w') as f:
            f.write(organic_svg)

        print(f"  ✓ Saved: {organic_file.name} ({len(organic_svg.encode('utf-8')) / 1024:.1f}KB)")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    generate_example_diagrams()
    demonstrate_style_comparison()
