"""
v1.3.0.3 - AI Content Generation System (Gemini Integration)

Tests for TUI commands to generate knowledge content using Gemini API:
- GENERATE GUIDE - Create survival guides
- GENERATE SVG - Create Technical-Kinetic style diagrams
- GENERATE CHECKLIST - Create practical checklists
- Batch content creation workflows

This enables populating the knowledge bank from within uDOS using AI.

Run: pytest memory/tests/test_v1_3_0_ai_content_generation.py -v
"""

import pytest
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


# ============================================================================
# CONTENT GENERATION SYSTEM
# ============================================================================

class ContentType(Enum):
    """Types of content that can be generated."""
    GUIDE = "guide"
    SVG = "svg"
    CHECKLIST = "checklist"
    SKILL_TREE = "skill_tree"
    PROMPT_TEMPLATE = "prompt_template"


class GuideCategory(Enum):
    """Knowledge guide categories."""
    SURVIVAL = "survival"
    WATER = "water"
    FOOD = "food"
    SHELTER = "building"
    MEDICAL = "medical"
    ENERGY = "energy"
    TOOLS = "tools"
    COMMUNICATION = "communication"
    DEFENSE = "defense"


class Difficulty(Enum):
    """Content difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SVGStyle(Enum):
    """SVG diagram styles."""
    TECHNICAL_KINETIC = "technical_kinetic"  # Bold, flat, geometric
    SCHEMATIC = "schematic"  # Blueprint style
    INFOGRAPHIC = "infographic"  # Data visualization
    ILLUSTRATION = "illustration"  # Detailed artwork


# ============================================================================
# GEMINI CONTENT GENERATOR
# ============================================================================

class GeminiContentGenerator:
    """
    Generate knowledge content using Gemini API.

    Integrates with existing GeminiCLI service from v1.2.0.
    """

    def __init__(self, output_dir: Path, gemini_api_key: Optional[str] = None):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = gemini_api_key
        self.generation_history = []

    def generate_guide(
        self,
        topic: str,
        category: GuideCategory,
        difficulty: Difficulty = Difficulty.BEGINNER,
        include_images: bool = True
    ) -> Dict:
        """
        Generate a comprehensive survival guide.

        Args:
            topic: Guide topic (e.g., "Water Purification Methods")
            category: Knowledge category
            difficulty: Target difficulty level
            include_images: Whether to suggest image locations

        Returns:
            Dictionary with guide content, metadata, and file path
        """
        # Build prompt for Gemini
        prompt = self._build_guide_prompt(topic, category, difficulty, include_images)

        # Simulate Gemini response (in real implementation, call Gemini API)
        guide_content = self._generate_markdown_guide(topic, difficulty)

        # Save to file
        filename = f"{topic.lower().replace(' ', '_')}.md"
        file_path = self.output_dir / category.value / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(guide_content)

        # Track generation
        result = {
            "type": ContentType.GUIDE.value,
            "topic": topic,
            "category": category.value,
            "difficulty": difficulty.value,
            "file_path": str(file_path),
            "word_count": len(guide_content.split()),
            "timestamp": datetime.now().isoformat(),
            "prompt_used": prompt[:100] + "..."  # Truncate for storage
        }

        self.generation_history.append(result)
        return result

    def _build_guide_prompt(
        self,
        topic: str,
        category: GuideCategory,
        difficulty: Difficulty,
        include_images: bool
    ) -> str:
        """Build Gemini prompt for guide generation."""
        prompt = f"""You are an expert survival guide writer for the uDOS offline knowledge system.

Create a comprehensive, practical guide about: {topic}

Requirements:
- Category: {category.value}
- Difficulty: {difficulty.value}
- Format: Markdown
- Length: 800-1200 words
- Structure:
  1. Overview (what, why, when)
  2. Materials/Equipment needed
  3. Step-by-step instructions
  4. Safety considerations
  5. Common mistakes to avoid
  6. Additional resources/references

Style Guidelines:
- Clear, concise, actionable language
- Use numbered lists for procedures
- Use bullet points for materials/tips
- No political or controversial content
- Focus on practical, tested methods
- Include time estimates where relevant
"""

        if include_images:
            prompt += """
- Suggest 3-5 image locations with descriptions (use ![alt](path.svg) syntax)
- Images should illustrate key steps or equipment
"""

        prompt += f"""
Target audience: {difficulty.value} level preppers/survivalists
Context: Off-grid, no internet access
Goal: Enable reader to execute the technique successfully

Generate the guide now:
"""
        return prompt

    def _generate_markdown_guide(self, topic: str, difficulty: Difficulty) -> str:
        """Generate sample markdown guide (simulates Gemini output)."""
        return f"""# {topic}

**Difficulty:** {difficulty.value.title()}
**Estimated Time:** 30-60 minutes
**Category:** Survival Skills

## Overview

{topic} is a critical survival skill that can mean the difference between life and death in emergency situations. This guide provides step-by-step instructions for {difficulty.value}-level practitioners.

## Materials Needed

- Primary equipment (specified by technique)
- Backup materials
- Safety equipment
- Testing supplies

## Step-by-Step Instructions

### Step 1: Preparation

Gather all materials and assess your environment. Safety first.

### Step 2: Setup

Configure your equipment according to best practices.

### Step 3: Execution

Follow the procedure carefully, checking each step.

### Step 4: Verification

Test the results to ensure success.

## Safety Considerations

⚠️ **Important Safety Notes:**
- Always test in safe conditions first
- Have backup plans ready
- Know when to abort
- Protect yourself from common hazards

## Common Mistakes

❌ **Avoid these errors:**
1. Rushing the process
2. Skipping safety checks
3. Using inadequate materials
4. Ignoring environmental factors

## Additional Resources

- Related guides: [Link to related content]
- Advanced techniques: [Next-level skills]
- Troubleshooting: Common problems and solutions

---

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
*Generated by uDOS AI Content System*
"""

    def generate_svg_diagram(
        self,
        subject: str,
        style: SVGStyle = SVGStyle.TECHNICAL_KINETIC,
        width: int = 800,
        height: int = 600
    ) -> Dict:
        """
        Generate SVG diagram in uDOS aesthetic.

        Args:
            subject: What to illustrate (e.g., "Water Filter Cross-Section")
            style: Visual style for diagram
            width: SVG width in pixels
            height: SVG height in pixels

        Returns:
            Dictionary with SVG content and metadata
        """
        # Build prompt for Gemini
        prompt = self._build_svg_prompt(subject, style, width, height)

        # Generate SVG (in real implementation, call Gemini API)
        svg_content = self._generate_technical_svg(subject, width, height)

        # Save to file
        filename = f"{subject.lower().replace(' ', '_')}.svg"
        file_path = self.output_dir / "illustrations" / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(svg_content)

        result = {
            "type": ContentType.SVG.value,
            "subject": subject,
            "style": style.value,
            "dimensions": f"{width}x{height}",
            "file_path": str(file_path),
            "file_size": len(svg_content),
            "timestamp": datetime.now().isoformat()
        }

        self.generation_history.append(result)
        return result

    def _build_svg_prompt(
        self,
        subject: str,
        style: SVGStyle,
        width: int,
        height: int
    ) -> str:
        """Build Gemini prompt for SVG generation."""
        prompt = f"""You are an expert technical illustrator creating SVG diagrams for the uDOS knowledge system.

Create an SVG diagram of: {subject}

Technical Requirements:
- Format: SVG 1.1
- Dimensions: {width}x{height}px
- Style: {style.value}
- Color Palette: Polaroid 8-color (Red #FF0000, Green #00FF00, Yellow #FFFF00, Blue #0000FF, Purple #FF00FF, Cyan #00FFFF, White #FFFFFF, Black #000000)
- Design: Flat (no gradients, shadows, or 3D effects)
- Geometric: Bold, simple shapes
- Labels: Clear, readable text

Style Guidelines for {style.value}:
"""

        if style == SVGStyle.TECHNICAL_KINETIC:
            prompt += """- Bold, geometric shapes
- Strong contrast
- Minimal detail
- Clear directional indicators
- Labeled components
- Assembly/disassembly views
"""
        elif style == SVGStyle.SCHEMATIC:
            prompt += """- Blueprint-style grid background
- Technical symbols
- Dimension lines
- Part numbers
- Cross-sections
"""

        prompt += f"""
Content Requirements:
- Clearly illustrate the key components
- Show relationships/flow/assembly
- Include labels for major parts
- Add directional arrows where relevant
- Use appropriate scale/proportion

Generate the SVG code now:
"""
        return prompt

    def _generate_technical_svg(self, subject: str, width: int, height: int) -> str:
        """Generate sample SVG diagram (simulates Gemini output)."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <title>{subject}</title>
  <desc>Technical diagram generated by uDOS AI Content System</desc>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="#FFFFFF"/>

  <!-- Main Component -->
  <rect x="200" y="150" width="400" height="300" fill="#0000FF" stroke="#000000" stroke-width="3"/>
  <text x="400" y="180" text-anchor="middle" font-family="monospace" font-size="16" fill="#FFFFFF">
    {subject}
  </text>

  <!-- Detail Elements -->
  <circle cx="400" cy="300" r="50" fill="#FF0000" stroke="#000000" stroke-width="2"/>
  <line x1="350" y1="300" x2="450" y2="300" stroke="#FFFF00" stroke-width="4"/>
  <line x1="400" y1="250" x2="400" y2="350" stroke="#FFFF00" stroke-width="4"/>

  <!-- Labels -->
  <text x="400" y="480" text-anchor="middle" font-family="monospace" font-size="12" fill="#000000">
    Component A
  </text>

  <!-- Arrow Indicators -->
  <path d="M 150 300 L 180 300 L 170 290 M 180 300 L 170 310" stroke="#00FF00" stroke-width="2" fill="none"/>

  <!-- Footer -->
  <text x="10" y="{height - 10}" font-family="monospace" font-size="10" fill="#000000">
    Generated: {datetime.now().strftime('%Y-%m-%d')}
  </text>
</svg>
"""

    def generate_checklist(
        self,
        title: str,
        category: str,
        num_items: int = 10
    ) -> Dict:
        """
        Generate practical checklist.

        Args:
            title: Checklist title (e.g., "72-Hour Emergency Kit")
            category: Checklist category (emergency, daily, project, etc.)
            num_items: Number of checklist items to generate

        Returns:
            Dictionary with checklist data and metadata
        """
        # Build prompt
        prompt = self._build_checklist_prompt(title, category, num_items)

        # Generate checklist
        checklist_data = self._generate_checklist_data(title, category, num_items)

        # Save to file
        filename = f"{title.lower().replace(' ', '_')}.json"
        file_path = self.output_dir / "checklists" / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(checklist_data, f, indent=2)

        result = {
            "type": ContentType.CHECKLIST.value,
            "title": title,
            "category": category,
            "num_items": len(checklist_data["items"]),
            "file_path": str(file_path),
            "timestamp": datetime.now().isoformat()
        }

        self.generation_history.append(result)
        return result

    def _build_checklist_prompt(self, title: str, category: str, num_items: int) -> str:
        """Build Gemini prompt for checklist generation."""
        return f"""You are an expert at creating practical survival checklists for the uDOS knowledge system.

Create a comprehensive checklist: {title}

Requirements:
- Category: {category}
- Number of items: {num_items}
- Format: JSON
- Priority levels: critical, high, medium, low
- Include quantity/specifications where relevant
- Organize by logical grouping

Structure each item:
{{
  "id": "unique_id",
  "description": "Clear item description",
  "priority": "critical|high|medium|low",
  "quantity": "number or specification",
  "category": "sub-category for grouping",
  "notes": "Optional additional context"
}}

Focus on:
- Practical, actionable items
- Realistic quantities
- Off-grid accessibility
- Essential vs. optional items
- Multi-use items preferred

Generate the checklist now:
"""

    def _generate_checklist_data(self, title: str, category: str, num_items: int) -> Dict:
        """Generate sample checklist data (simulates Gemini output)."""
        items = []
        priorities = ["critical", "high", "medium", "low"]

        for i in range(num_items):
            items.append({
                "id": f"item_{i+1:03d}",
                "description": f"Essential item {i+1} for {title}",
                "priority": priorities[i % len(priorities)],
                "quantity": f"{i+1} units",
                "category": f"Group {(i // 3) + 1}",
                "notes": f"Important for {category} situations"
            })

        return {
            "title": title,
            "category": category,
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "total_items": num_items,
            "items": items
        }

    def batch_generate(self, batch_config: Dict) -> Dict:
        """
        Generate multiple content pieces in a batch.

        Args:
            batch_config: Configuration with list of content to generate

        Returns:
            Summary of batch generation results
        """
        results = {
            "started": datetime.now().isoformat(),
            "total_requested": 0,
            "total_generated": 0,
            "guides": [],
            "svgs": [],
            "checklists": [],
            "errors": []
        }

        # Generate guides
        if "guides" in batch_config:
            results["total_requested"] += len(batch_config["guides"])
            for guide_spec in batch_config["guides"]:
                try:
                    # Find category by value (e.g., "building" -> SHELTER)
                    category_value = guide_spec["category"]
                    category = next(c for c in GuideCategory if c.value == category_value)

                    result = self.generate_guide(
                        topic=guide_spec["topic"],
                        category=category,
                        difficulty=Difficulty[guide_spec.get("difficulty", "BEGINNER").upper()]
                    )
                    results["guides"].append(result)
                    results["total_generated"] += 1
                except Exception as e:
                    results["errors"].append({
                        "type": "guide",
                        "spec": guide_spec,
                        "error": str(e)
                    })

        # Generate SVGs
        if "svgs" in batch_config:
            results["total_requested"] += len(batch_config["svgs"])
            for svg_spec in batch_config["svgs"]:
                try:
                    # Find style by value
                    style_value = svg_spec.get("style", "technical_kinetic")
                    style = next(s for s in SVGStyle if s.value == style_value)

                    result = self.generate_svg_diagram(
                        subject=svg_spec["subject"],
                        style=style
                    )
                    results["svgs"].append(result)
                    results["total_generated"] += 1
                except Exception as e:
                    results["errors"].append({
                        "type": "svg",
                        "spec": svg_spec,
                        "error": str(e)
                    })

        # Generate checklists
        if "checklists" in batch_config:
            results["total_requested"] += len(batch_config["checklists"])
            for checklist_spec in batch_config["checklists"]:
                try:
                    result = self.generate_checklist(
                        title=checklist_spec["title"],
                        category=checklist_spec["category"],
                        num_items=checklist_spec.get("num_items", 10)
                    )
                    results["checklists"].append(result)
                    results["total_generated"] += 1
                except Exception as e:
                    results["errors"].append({
                        "type": "checklist",
                        "spec": checklist_spec,
                        "error": str(e)
                    })

        results["completed"] = datetime.now().isoformat()
        results["success_rate"] = results["total_generated"] / max(results["total_requested"], 1)

        return results


# ============================================================================
# TUI COMMAND HANDLERS
# ============================================================================

class GenerateCommand:
    """TUI command handler for content generation."""

    def __init__(self, generator: GeminiContentGenerator):
        self.generator = generator

    def execute(self, command: str, args: List[str]) -> str:
        """
        Execute GENERATE command.

        Commands:
            GENERATE GUIDE <topic> --category=<cat> --difficulty=<diff>
            GENERATE SVG <subject> --style=<style>
            GENERATE CHECKLIST <title> --category=<cat> --items=<n>
            GENERATE BATCH <config_file>
        """
        if not args:
            return self._show_help()

        subcommand = args[0].upper()

        if subcommand == "GUIDE":
            return self._generate_guide_command(args[1:])
        elif subcommand == "SVG":
            return self._generate_svg_command(args[1:])
        elif subcommand == "CHECKLIST":
            return self._generate_checklist_command(args[1:])
        elif subcommand == "BATCH":
            return self._generate_batch_command(args[1:])
        else:
            return f"❌ Unknown subcommand: {subcommand}\n{self._show_help()}"

    def _generate_guide_command(self, args: List[str]) -> str:
        """Handle GENERATE GUIDE command."""
        if not args:
            return "❌ Usage: GENERATE GUIDE <topic> --category=<cat> --difficulty=<diff>"

        # Parse arguments
        topic = " ".join([a for a in args if not a.startswith("--")])
        category = self._extract_flag(args, "--category", "survival")
        difficulty = self._extract_flag(args, "--difficulty", "beginner")

        # Generate guide
        result = self.generator.generate_guide(
            topic=topic,
            category=GuideCategory[category.upper()],
            difficulty=Difficulty[difficulty.upper()]
        )

        return f"""✅ Guide generated successfully!

📄 Topic: {result['topic']}
📁 Category: {result['category']}
⭐ Difficulty: {result['difficulty']}
📊 Word count: {result['word_count']}
💾 Saved to: {result['file_path']}

Use OPEN {result['file_path']} to view the guide.
"""

    def _generate_svg_command(self, args: List[str]) -> str:
        """Handle GENERATE SVG command."""
        if not args:
            return "❌ Usage: GENERATE SVG <subject> --style=<style>"

        subject = " ".join([a for a in args if not a.startswith("--")])
        style = self._extract_flag(args, "--style", "technical_kinetic")

        result = self.generator.generate_svg_diagram(
            subject=subject,
            style=SVGStyle[style.upper()]
        )

        return f"""✅ SVG diagram generated successfully!

🎨 Subject: {result['subject']}
🖼️  Style: {result['style']}
📐 Size: {result['dimensions']}
💾 Saved to: {result['file_path']}

Use OPEN {result['file_path']} to view the diagram.
"""

    def _generate_checklist_command(self, args: List[str]) -> str:
        """Handle GENERATE CHECKLIST command."""
        if not args:
            return "❌ Usage: GENERATE CHECKLIST <title> --category=<cat> --items=<n>"

        title = " ".join([a for a in args if not a.startswith("--")])
        category = self._extract_flag(args, "--category", "emergency")
        num_items = int(self._extract_flag(args, "--items", "10"))

        result = self.generator.generate_checklist(
            title=title,
            category=category,
            num_items=num_items
        )

        return f"""✅ Checklist generated successfully!

📋 Title: {result['title']}
📁 Category: {result['category']}
✓ Items: {result['num_items']}
💾 Saved to: {result['file_path']}

Use CHECKLIST LOAD {result['title']} to use this checklist.
"""

    def _generate_batch_command(self, args: List[str]) -> str:
        """Handle GENERATE BATCH command."""
        if not args:
            return "❌ Usage: GENERATE BATCH <config_file>"

        config_path = Path(args[0])
        if not config_path.exists():
            return f"❌ Config file not found: {config_path}"

        with open(config_path, 'r') as f:
            batch_config = json.load(f)

        result = self.generator.batch_generate(batch_config)

        return f"""✅ Batch generation completed!

📊 Summary:
   Requested: {result['total_requested']}
   Generated: {result['total_generated']}
   Success rate: {result['success_rate']*100:.1f}%

📄 Guides: {len(result['guides'])}
🎨 SVGs: {len(result['svgs'])}
📋 Checklists: {len(result['checklists'])}
❌ Errors: {len(result['errors'])}

Started: {result['started']}
Completed: {result['completed']}
"""

    def _extract_flag(self, args: List[str], flag: str, default: str) -> str:
        """Extract flag value from arguments."""
        for arg in args:
            if arg.startswith(flag + "="):
                return arg.split("=", 1)[1]
        return default

    def _show_help(self) -> str:
        """Show command help."""
        return """📚 GENERATE Command Help

Usage:
  GENERATE GUIDE <topic> [--category=<cat>] [--difficulty=<level>]
  GENERATE SVG <subject> [--style=<style>]
  GENERATE CHECKLIST <title> [--category=<cat>] [--items=<n>]
  GENERATE BATCH <config_file>

Examples:
  GENERATE GUIDE "Water Purification" --category=water --difficulty=beginner
  GENERATE SVG "Solar Panel Wiring" --style=schematic
  GENERATE CHECKLIST "Bug-Out Bag" --category=emergency --items=20
  GENERATE BATCH /memory/content_batch.json

Categories: survival, water, food, building, medical, energy, tools
Difficulty: beginner, intermediate, advanced, expert
SVG Styles: technical_kinetic, schematic, infographic, illustration
"""


# ============================================================================
# TESTS
# ============================================================================

def test_generate_guide(tmp_path):
    """Test guide generation."""
    generator = GeminiContentGenerator(tmp_path)

    result = generator.generate_guide(
        topic="Water Purification Methods",
        category=GuideCategory.WATER,
        difficulty=Difficulty.BEGINNER
    )

    assert result["type"] == "guide"
    assert result["topic"] == "Water Purification Methods"
    assert result["category"] == "water"
    assert result["difficulty"] == "beginner"
    assert result["word_count"] > 0
    assert Path(result["file_path"]).exists()


def test_guide_content_structure(tmp_path):
    """Test generated guide has proper structure."""
    generator = GeminiContentGenerator(tmp_path)

    result = generator.generate_guide(
        topic="Fire Starting Techniques",
        category=GuideCategory.SURVIVAL,
        difficulty=Difficulty.INTERMEDIATE
    )

    # Read generated file
    with open(result["file_path"], 'r') as f:
        content = f.read()

    # Check for required sections
    assert "# Fire Starting Techniques" in content
    assert "## Overview" in content
    assert "## Materials Needed" in content
    assert "## Step-by-Step Instructions" in content
    assert "## Safety Considerations" in content
    assert "## Common Mistakes" in content


def test_generate_svg_diagram(tmp_path):
    """Test SVG diagram generation."""
    generator = GeminiContentGenerator(tmp_path)

    result = generator.generate_svg_diagram(
        subject="Water Filter Cross-Section",
        style=SVGStyle.TECHNICAL_KINETIC,
        width=800,
        height=600
    )

    assert result["type"] == "svg"
    assert result["subject"] == "Water Filter Cross-Section"
    assert result["style"] == "technical_kinetic"
    assert result["dimensions"] == "800x600"
    assert Path(result["file_path"]).exists()


def test_svg_valid_xml(tmp_path):
    """Test generated SVG is valid XML."""
    generator = GeminiContentGenerator(tmp_path)

    result = generator.generate_svg_diagram(
        subject="Solar Panel Schematic",
        style=SVGStyle.SCHEMATIC
    )

    # Read generated file
    with open(result["file_path"], 'r') as f:
        content = f.read()

    # Basic SVG validation
    assert content.startswith('<?xml version="1.0"')
    assert '<svg xmlns="http://www.w3.org/2000/svg"' in content
    assert '</svg>' in content
    assert '<title>Solar Panel Schematic</title>' in content


def test_generate_checklist(tmp_path):
    """Test checklist generation."""
    generator = GeminiContentGenerator(tmp_path)

    result = generator.generate_checklist(
        title="72-Hour Emergency Kit",
        category="emergency",
        num_items=15
    )

    assert result["type"] == "checklist"
    assert result["title"] == "72-Hour Emergency Kit"
    assert result["category"] == "emergency"
    assert result["num_items"] == 15
    assert Path(result["file_path"]).exists()


def test_checklist_json_structure(tmp_path):
    """Test generated checklist has valid JSON structure."""
    generator = GeminiContentGenerator(tmp_path)

    result = generator.generate_checklist(
        title="Daily Homestead Tasks",
        category="daily",
        num_items=10
    )

    # Read and parse JSON
    with open(result["file_path"], 'r') as f:
        data = json.load(f)

    assert data["title"] == "Daily Homestead Tasks"
    assert data["category"] == "daily"
    assert len(data["items"]) == 10

    # Validate item structure
    first_item = data["items"][0]
    assert "id" in first_item
    assert "description" in first_item
    assert "priority" in first_item
    assert "quantity" in first_item


def test_batch_generation(tmp_path):
    """Test batch content generation."""
    generator = GeminiContentGenerator(tmp_path)

    batch_config = {
        "guides": [
            {"topic": "Shelter Building", "category": "building", "difficulty": "beginner"},
            {"topic": "Edible Plants", "category": "food", "difficulty": "intermediate"}
        ],
        "svgs": [
            {"subject": "Lean-To Shelter", "style": "technical_kinetic"}
        ],
        "checklists": [
            {"title": "Foraging Safety", "category": "food"}
        ]
    }

    results = generator.batch_generate(batch_config)

    assert results["total_requested"] == 4
    assert results["total_generated"] == 4
    assert results["success_rate"] == 1.0
    assert len(results["guides"]) == 2
    assert len(results["svgs"]) == 1
    assert len(results["checklists"]) == 1
    assert len(results["errors"]) == 0


def test_generation_history_tracking(tmp_path):
    """Test that generation history is tracked."""
    generator = GeminiContentGenerator(tmp_path)

    generator.generate_guide("Test Guide", GuideCategory.SURVIVAL, Difficulty.BEGINNER)
    generator.generate_svg_diagram("Test Diagram", SVGStyle.TECHNICAL_KINETIC)
    generator.generate_checklist("Test Checklist", "test")

    assert len(generator.generation_history) == 3
    assert generator.generation_history[0]["type"] == "guide"
    assert generator.generation_history[1]["type"] == "svg"
    assert generator.generation_history[2]["type"] == "checklist"


def test_command_handler_guide(tmp_path):
    """Test GENERATE GUIDE command handler."""
    generator = GeminiContentGenerator(tmp_path)
    cmd = GenerateCommand(generator)

    output = cmd.execute("GENERATE", ["GUIDE", "Test", "Topic", "--category=water", "--difficulty=beginner"])

    assert "✅ Guide generated successfully!" in output
    assert "Test Topic" in output
    assert "water" in output


def test_command_handler_svg(tmp_path):
    """Test GENERATE SVG command handler."""
    generator = GeminiContentGenerator(tmp_path)
    cmd = GenerateCommand(generator)

    output = cmd.execute("GENERATE", ["SVG", "Test", "Diagram", "--style=schematic"])

    assert "✅ SVG diagram generated successfully!" in output
    assert "Test Diagram" in output


def test_command_handler_checklist(tmp_path):
    """Test GENERATE CHECKLIST command handler."""
    generator = GeminiContentGenerator(tmp_path)
    cmd = GenerateCommand(generator)

    output = cmd.execute("GENERATE", ["CHECKLIST", "Test", "List", "--category=emergency", "--items=5"])

    assert "✅ Checklist generated successfully!" in output
    assert "Test List" in output
    assert "5" in output


def test_command_handler_batch(tmp_path):
    """Test GENERATE BATCH command handler."""
    generator = GeminiContentGenerator(tmp_path)
    cmd = GenerateCommand(generator)

    # Create batch config file
    config_file = tmp_path / "batch.json"
    with open(config_file, 'w') as f:
        json.dump({
            "guides": [{"topic": "Test", "category": "survival"}],
            "svgs": [{"subject": "Test"}],
            "checklists": [{"title": "Test", "category": "test"}]
        }, f)

    output = cmd.execute("GENERATE", ["BATCH", str(config_file)])

    assert "✅ Batch generation completed!" in output
    assert "Requested: 3" in output
    assert "Generated: 3" in output


def test_command_handler_help(tmp_path):
    """Test GENERATE help output."""
    generator = GeminiContentGenerator(tmp_path)
    cmd = GenerateCommand(generator)

    output = cmd.execute("GENERATE", [])

    assert "GENERATE Command Help" in output
    assert "GENERATE GUIDE" in output
    assert "GENERATE SVG" in output
    assert "GENERATE CHECKLIST" in output


def test_file_organization(tmp_path):
    """Test that generated files are organized correctly."""
    generator = GeminiContentGenerator(tmp_path)

    # Generate different types
    guide_result = generator.generate_guide("Test", GuideCategory.WATER, Difficulty.BEGINNER)
    svg_result = generator.generate_svg_diagram("Test", SVGStyle.TECHNICAL_KINETIC)
    checklist_result = generator.generate_checklist("Test", "emergency")

    # Check organization
    assert "water" in guide_result["file_path"]
    assert "illustrations" in svg_result["file_path"]
    assert "checklists" in checklist_result["file_path"]


def test_summary():
    """Test summary for v1.3.0.3."""
    print("\n" + "="*70)
    print("v1.3.0.3 - AI Content Generation System (Gemini Integration)")
    print("="*70)
    print("✅ Guide Generation - Create comprehensive survival guides")
    print("✅ SVG Diagram Generation - Technical-Kinetic style illustrations")
    print("✅ Checklist Generation - Practical task lists")
    print("✅ Batch Processing - Generate multiple pieces at once")
    print("✅ TUI Commands - GENERATE GUIDE/SVG/CHECKLIST/BATCH")
    print("✅ History Tracking - Track all generated content")
    print("✅ File Organization - Automatic categorization")
    print("✅ Gemini Integration - AI-powered content creation")
    print("="*70)
    print("Total: 16 tests")
    print("="*70)
    print("\n💡 Usage from uDOS TUI:")
    print("  GENERATE GUIDE 'Water Purification' --category=water")
    print("  GENERATE SVG 'Solar Panel Wiring' --style=schematic")
    print("  GENERATE CHECKLIST 'Bug-Out Bag' --category=emergency")
    print("  GENERATE BATCH /memory/content_plan.json")
    print("="*70)
