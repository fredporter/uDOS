#!/usr/bin/env python3
"""
v1.4.0 Content Population Script
=================================

Automates generation of 1000+ survival guides and 500+ SVG diagrams
using the GENERATE commands from v1.3.0.

Usage:
    python3 dev/tools/generate_content_v1_4_0.py --category water --count 10
    python3 dev/tools/generate_content_v1_4_0.py --batch config/batch_water.json
    python3 dev/tools/generate_content_v1_4_0.py --all

Categories:
    - water: Water procurement, purification, storage
    - fire: Fire starting, maintenance, safety
    - shelter: Shelter building, insulation, weatherproofing
    - food: Food foraging, preservation, cooking
    - navigation: Navigation, signaling, rescue
    - medical: First aid, medical, wellness
    - tools: Tools, equipment, maintenance
    - communication: Communication, community, security
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import Gemini service for AI generation
try:
    from core.services.gemini_service import GeminiCLI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini service not available - will use placeholders only")

# Content generation targets for v1.4.0
CONTENT_TARGETS = {
    "water": {
        "guides": 150,
        "diagrams": 80,
        "topics": [
            "finding water sources",
            "water purification methods",
            "water storage techniques",
            "rainwater collection",
            "solar still construction",
            "water filtration systems",
            "water quality testing",
            "emergency water sources",
            "water conservation",
            "well digging basics"
        ]
    },
    "fire": {
        "guides": 100,
        "diagrams": 50,
        "topics": [
            "fire starting techniques",
            "tinder preparation",
            "fire maintenance",
            "fire safety zones",
            "smokeless fires",
            "signal fires",
            "cooking fires",
            "fire in wet conditions",
            "friction fire methods",
            "fire starter materials"
        ]
    },
    "shelter": {
        "guides": 120,
        "diagrams": 70,
        "topics": [
            "shelter site selection",
            "emergency shelters",
            "debris huts",
            "lean-to construction",
            "A-frame shelters",
            "insulation techniques",
            "weatherproofing",
            "knot tying",
            "lashing techniques",
            "shelter ventilation"
        ]
    },
    "food": {
        "guides": 180,
        "diagrams": 60,
        "topics": [
            "edible plants identification",
            "foraging safety",
            "food preservation",
            "smoking meat",
            "drying foods",
            "wild game preparation",
            "fishing techniques",
            "trapping basics",
            "cooking methods",
            "nutrition planning"
        ]
    },
    "navigation": {
        "guides": 100,
        "diagrams": 50,
        "topics": [
            "map reading",
            "compass use",
            "natural navigation",
            "star navigation",
            "sun navigation",
            "terrain features",
            "signaling techniques",
            "rescue signals",
            "SOS procedures",
            "route planning"
        ]
    },
    "medical": {
        "guides": 150,
        "diagrams": 80,
        "topics": [
            "first aid basics",
            "wound care",
            "fracture treatment",
            "burns treatment",
            "hypothermia prevention",
            "heat exhaustion",
            "snake bites",
            "plant poisons",
            "emergency CPR",
            "wilderness medicine"
        ]
    },
    "tools": {
        "guides": 100,
        "diagrams": 60,
        "topics": [
            "knife maintenance",
            "axe use and safety",
            "saw techniques",
            "tool sharpening",
            "makeshift tools",
            "rope making",
            "cordage techniques",
            "tool repairs",
            "equipment care",
            "multi-tool uses"
        ]
    },
    "communication": {
        "guides": 100,
        "diagrams": 50,
        "topics": [
            "radio basics",
            "morse code",
            "hand signals",
            "whistle codes",
            "mirror signals",
            "smoke signals",
            "community coordination",
            "emergency communication",
            "message systems",
            "security protocols"
        ]
    }
}


class ContentGenerator:
    """Generates knowledge bank content using v1.3.0 GENERATE commands"""

    def __init__(self, dry_run=False, use_ai=True):
        self.dry_run = dry_run
        self.use_ai = use_ai and GEMINI_AVAILABLE
        self.gemini = None
        self.stats = {
            "guides_generated": 0,
            "diagrams_generated": 0,
            "errors": 0,
            "skipped": 0,
            "api_calls": 0
        }

        # Initialize Gemini if AI mode enabled
        if self.use_ai:
            try:
                # Get project root (.env location)
                project_root = Path(__file__).parent.parent.parent
                env_path = project_root / '.env'

                self.gemini = GeminiCLI(env_path=env_path)
                print("✅ Gemini AI initialized for content generation")
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {e}")
                print("⚠️  Falling back to placeholder mode")
                self.use_ai = False

    def generate_guides(self, category: str, count: int):
        """Generate guides for a category"""
        if category not in CONTENT_TARGETS:
            print(f"❌ Unknown category: {category}")
            return

        target = CONTENT_TARGETS[category]
        topics = target["topics"]

        print(f"\n📚 Generating {count} guides for category: {category}")
        print(f"Target: {target['guides']} guides")

        for i in range(min(count, len(topics))):
            topic = topics[i % len(topics)]

            if self.dry_run:
                print(f"  [DRY RUN] Would generate: {topic}")
                self.stats["guides_generated"] += 1
            else:
                # TODO: Call actual GENERATE GUIDE command
                # For now, create placeholder
                output_path = self._generate_guide_placeholder(category, topic)
                if output_path:
                    print(f"  ✅ Generated: {output_path}")
                    self.stats["guides_generated"] += 1
                else:
                    print(f"  ❌ Failed: {topic}")
                    self.stats["errors"] += 1

    def generate_diagrams(self, category: str, count: int):
        """Generate SVG diagrams for a category"""
        if category not in CONTENT_TARGETS:
            print(f"❌ Unknown category: {category}")
            return

        target = CONTENT_TARGETS[category]

        print(f"\n🎨 Generating {count} diagrams for category: {category}")
        print(f"Target: {target['diagrams']} diagrams")

        for i in range(count):
            topic = target["topics"][i % len(target["topics"])]

            if self.dry_run:
                print(f"  [DRY RUN] Would generate diagram: {topic}")
                self.stats["diagrams_generated"] += 1
            else:
                # TODO: Call actual GENERATE SVG command
                output_path = self._generate_diagram_placeholder(category, topic)
                if output_path:
                    print(f"  ✅ Generated: {output_path}")
                    self.stats["diagrams_generated"] += 1
                else:
                    print(f"  ❌ Failed: {topic}")
                    self.stats["errors"] += 1

    def _generate_guide_placeholder(self, category: str, topic: str) -> Path:
        """Generate guide using Gemini AI or placeholder"""
        # Create knowledge directory structure
        output_dir = Path("knowledge") / category
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        filename = topic.replace(" ", "_").lower() + ".md"
        output_path = output_dir / filename

        # Skip if exists
        if output_path.exists():
            self.stats["skipped"] += 1
            return None

        # Generate content with AI if available
        if self.use_ai and self.gemini:
            try:
                content = self._generate_guide_with_ai(category, topic)
                self.stats["api_calls"] += 1
                # Small delay to respect rate limits
                time.sleep(0.5)
            except Exception as e:
                print(f"    ⚠️  AI generation failed: {e}, using placeholder")
                content = self._create_placeholder_guide(category, topic)
        else:
            content = self._create_placeholder_guide(category, topic)

        # Write to file
        output_path.write_text(content)
        return output_path

    def _generate_guide_with_ai(self, category: str, topic: str) -> str:
        """Use Gemini AI to generate comprehensive survival guide"""
        prompt = f"""Generate a comprehensive survival guide about {topic} for the {category} category.

Requirements:
- Write 800-1200 words
- Use clear, practical language
- Include specific step-by-step instructions
- Add safety warnings where appropriate
- List materials needed
- Mention common mistakes to avoid
- Suggest related topics

Format as markdown with these sections:
1. Title: # {topic.title()}
2. Metadata: Category, Difficulty, Generated date
3. Overview (2-3 paragraphs)
4. Materials Needed (bulleted list)
5. Step-by-Step Instructions (numbered, with subsections)
6. Safety Considerations (bulleted list)
7. Common Mistakes (bulleted list)
8. Related Topics (bulleted list)

Make it practical, detailed, and focused on real survival scenarios."""

        response = self.gemini.ask(prompt)

        # Add metadata header if not included
        if not response.startswith("#"):
            response = f"""# {topic.title()}

**Category:** {category}
**Difficulty:** beginner
**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**AI-Generated:** ✅

{response}
"""

        return response

    def _create_placeholder_guide(self, category: str, topic: str) -> str:
        """Create placeholder guide content"""
        return f"""# {topic.title()}

**Category:** {category}
**Difficulty:** beginner
**Generated:** {datetime.now().strftime('%Y-%m-%d')}

## Overview

[Placeholder - To be generated with GENERATE GUIDE command]

## Materials Needed

- Material 1
- Material 2
- Material 3

## Step-by-Step Instructions

### Step 1: Preparation
[Instructions]

### Step 2: Execution
[Instructions]

### Step 3: Verification
[Instructions]

## Safety Considerations

- Safety point 1
- Safety point 2
- Safety point 3

## Common Mistakes

- Mistake 1
- Mistake 2

## Related Topics

- Related topic 1
- Related topic 2

---

*Generated as part of v1.4.0 content expansion*
"""

    def _generate_diagram_placeholder(self, category: str, topic: str) -> Path:
        """Generate SVG diagram using Gemini AI or placeholder"""
        output_dir = Path("knowledge") / "reference" / "diagrams" / category
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = topic.replace(" ", "_").lower() + ".svg"
        output_path = output_dir / filename

        if output_path.exists():
            self.stats["skipped"] += 1
            return None

        # Generate SVG with AI if available
        if self.use_ai and self.gemini:
            try:
                svg_content = self._generate_diagram_with_ai(category, topic)
                self.stats["api_calls"] += 1
                # Small delay to respect rate limits
                time.sleep(0.5)
            except Exception as e:
                print(f"    ⚠️  AI diagram generation failed: {e}, using placeholder")
                svg_content = self._create_placeholder_diagram(category, topic)
        else:
            svg_content = self._create_placeholder_diagram(category, topic)

        output_path.write_text(svg_content)
        return output_path

    def _generate_diagram_with_ai(self, category: str, topic: str) -> str:
        """Use Gemini AI to generate SVG diagram"""
        prompt = f"""Generate a technical SVG diagram illustrating {topic} for the {category} category.

Requirements:
- SVG format (800x600 viewBox)
- Technical-Kinetic style (clean, geometric, instructional)
- Use Polaroid 8-color palette ONLY:
  * Red: #FF0000
  * Green: #00FF00
  * Yellow: #FFFF00
  * Blue: #0000FF
  * Purple: #FF00FF
  * Cyan: #00FFFF
  * White: #FFFFFF
  * Black: #000000
- Flat design (no gradients, shadows, or curves unless essential)
- Include labels and annotations
- Show step-by-step process or key components
- Use arrows and callouts
- Monospace font for all text
- Clear, educational focus

The diagram should be informative and help someone understand the practical aspects of {topic}."""

        response = self.gemini.ask(prompt)

        # Extract SVG from response if wrapped in markdown
        if "```svg" in response:
            svg_start = response.find("```svg") + 6
            svg_end = response.find("```", svg_start)
            response = response[svg_start:svg_end].strip()
        elif "```" in response:
            svg_start = response.find("```") + 3
            svg_end = response.find("```", svg_start)
            response = response[svg_start:svg_end].strip()

        # Validate it starts with <svg
        if not response.strip().startswith("<svg"):
            print(f"    ⚠️  Response not valid SVG, using placeholder")
            return self._create_placeholder_diagram(category, topic)

        return response

    def _create_placeholder_diagram(self, category: str, topic: str) -> str:
        """Create placeholder SVG content"""
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <defs>
    <style>
      .title {{ font-family: monospace; font-size: 24px; fill: #00FF00; }}
      .subtitle {{ font-family: monospace; font-size: 14px; fill: #FFFFFF; }}
    </style>
  </defs>

  <rect width="800" height="600" fill="#000000"/>

  <text x="400" y="250" class="title" text-anchor="middle">{topic.title()}</text>
  <text x="400" y="300" class="subtitle" text-anchor="middle">Category: {category}</text>
  <text x="400" y="350" class="subtitle" text-anchor="middle">[Placeholder - Generate with GENERATE SVG]</text>

  <!-- Polaroid 8-color palette -->
  <rect x="50" y="500" width="80" height="40" fill="#FF0000"/>
  <rect x="150" y="500" width="80" height="40" fill="#00FF00"/>
  <rect x="250" y="500" width="80" height="40" fill="#FFFF00"/>
  <rect x="350" y="500" width="80" height="40" fill="#0000FF"/>
  <rect x="450" y="500" width="80" height="40" fill="#FF00FF"/>
  <rect x="550" y="500" width="80" height="40" fill="#00FFFF"/>
  <rect x="650" y="500" width="80" height="40" fill="#FFFFFF"/>
</svg>
"""

        output_path.write_text(svg_content)
        return output_path

    def print_stats(self):
        """Print generation statistics"""
        print("\n" + "="*60)
        print("📊 Content Generation Statistics")
        print("="*60)
        print(f"Guides generated:   {self.stats['guides_generated']}")
        print(f"Diagrams generated: {self.stats['diagrams_generated']}")
        print(f"API calls:          {self.stats['api_calls']}")
        print(f"Errors:             {self.stats['errors']}")
        print(f"Skipped (exists):   {self.stats['skipped']}")
        print(f"Total:              {self.stats['guides_generated'] + self.stats['diagrams_generated']}")
        print(f"Mode:               {'AI-Powered' if self.use_ai else 'Placeholder'}")
        print("="*60)


def generate_all_content(dry_run=False, use_ai=True):
    """Generate all content for v1.4.0"""
    generator = ContentGenerator(dry_run=dry_run, use_ai=use_ai)

    print("🚀 v1.4.0 Content Population - Full Generation")
    print(f"Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")

    for category, target in CONTENT_TARGETS.items():
        print(f"\n{'='*60}")
        print(f"Category: {category.upper()}")
        print(f"{'='*60}")

        generator.generate_guides(category, target["guides"])
        generator.generate_diagrams(category, target["diagrams"])

    generator.print_stats()

    # Print progress toward v1.4.0 goals
    total_guides_target = sum(t["guides"] for t in CONTENT_TARGETS.values())
    total_diagrams_target = sum(t["diagrams"] for t in CONTENT_TARGETS.values())

    print(f"\n📈 Progress Toward v1.4.0 Goals:")
    print(f"Guides: {generator.stats['guides_generated']}/{total_guides_target} ({generator.stats['guides_generated']/total_guides_target*100:.1f}%)")
    print(f"Diagrams: {generator.stats['diagrams_generated']}/{total_diagrams_target} ({generator.stats['diagrams_generated']/total_diagrams_target*100:.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="v1.4.0 Content Population Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("--category", choices=list(CONTENT_TARGETS.keys()),
                       help="Generate content for specific category")
    parser.add_argument("--count", type=int, default=10,
                       help="Number of items to generate (default: 10)")
    parser.add_argument("--all", action="store_true",
                       help="Generate all content for v1.4.0")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be generated without creating files")
    parser.add_argument("--diagrams-only", action="store_true",
                       help="Generate only diagrams")
    parser.add_argument("--guides-only", action="store_true",
                       help="Generate only guides")
    parser.add_argument("--no-ai", action="store_true",
                       help="Use placeholders instead of AI generation")

    args = parser.parse_args()

    use_ai = not args.no_ai

    if args.all:
        generate_all_content(dry_run=args.dry_run, use_ai=use_ai)
    elif args.category:
        generator = ContentGenerator(dry_run=args.dry_run, use_ai=use_ai)

        if not args.diagrams_only:
            generator.generate_guides(args.category, args.count)
        if not args.guides_only:
            generator.generate_diagrams(args.category, args.count)

        generator.print_stats()
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print("  python3 dev/tools/generate_content_v1_4_0.py --category water --count 10")
        print("  python3 dev/tools/generate_content_v1_4_0.py --category fire --count 5 --no-ai")
        print("  python3 dev/tools/generate_content_v1_4_0.py --all --dry-run")
        print("  python3 dev/tools/generate_content_v1_4_0.py --category fire --diagrams-only")


if __name__ == "__main__":
    main()
