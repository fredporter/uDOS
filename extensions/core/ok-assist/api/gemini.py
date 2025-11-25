"""
OK Assist - Gemini API Integration
Wrapper for Google Gemini API with uDOS style constraints

Generates:
- ASCII art (mono, C64 PetMe character set)
- Teletext graphics (color, WST mosaic blocks)
- SVG diagrams (technical-kinetic, hand-illustrative)
"""

import os
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, Literal

# Load .env file if exists
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent.parent.parent / '.env')
except ImportError:
    pass  # dotenv not required if env vars already set

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Run: pip install google-generativeai")


class OKAssist:
    """
    OK Assist - AI Content Generation for uDOS

    Supports:
    - ASCII art generation (C64 PetMe character set)
    - Teletext graphics (WST mosaic blocks, 8-color palette)
    - SVG diagram generation (Technical-Kinetic, Hand-Illustrative)
    - Text generation (survival guides, references)
    - Format conversion (PDF, HTML to Markdown)
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        Initialize OK Assist with Gemini API

        Args:
            api_key: Google API key (or set GEMINI_API_KEY in .env)
            model: Gemini model to use (default: gemini-2.5-flash)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package required. Install: pip install google-generativeai")

        # Get API key from parameter, .env, or environment
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Options:\n"
                "1. Set GEMINI_API_KEY in .env file\n"
                "2. Set GEMINI_API_KEY environment variable\n"
                "3. Pass api_key parameter to OKAssist()"
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)

        # Load style definitions
        prompts_dir = Path(__file__).parent / "prompts"
        with open(prompts_dir / "style_definitions.json") as f:
            self.styles = json.load(f)

        # Asset paths
        self.assets_root = Path(__file__).parent.parent.parent / "assets"

    def generate_svg(
        self,
        subject: str,
        style: Literal["technical-kinetic", "hand-illustrative"] = "technical-kinetic",
        description: str = "",
        complexity: Literal["simple", "moderate", "detailed", "complex"] = "moderate",
        width: int = 800,
        height: int = 600
    ) -> str:
        """
        Generate SVG diagram using Gemini API

        Args:
            subject: What to illustrate (e.g., "water filter system")
            style: Visual style (technical-kinetic or hand-illustrative)
            description: Additional context and requirements
            complexity: Detail level
            width: SVG width
            height: SVG height

        Returns:
            SVG code as string
        """
        # Normalize style name
        style_key = style.replace("-", "_")

        if style_key not in self.styles:
            raise ValueError(f"Unknown style: {style}. Use 'technical-kinetic' or 'hand-illustrative'")

        # Load detailed prompt template
        prompts_dir = Path(__file__).parent / "prompts"
        template_file = prompts_dir / f"{style_key}_prompt.md"

        with open(template_file, 'r') as f:
            prompt_template = f.read()

        # Fill in template variables
        prompt = prompt_template.format(
            subject=subject,
            description=description or f"A detailed {style.replace('-', ' ')} illustration of {subject}",
            width=width,
            height=height
        )

        # Add complexity-specific instructions
        complexity_def = self.styles["complexity_levels"][complexity]
        prompt += f"\n\n## Complexity Level: {complexity.upper()}\n"
        prompt += f"- Target element count: {complexity_def['elements']}\n"
        prompt += f"- Detail level: {complexity_def['detail']}\n"
        prompt += f"- File size target: {complexity_def['file_size']}\n"

        # Generate with Gemini
        response = self.model.generate_content(prompt)

        # Extract SVG code from response
        svg_code = self._extract_svg(response.text)

        # Validate and optimize
        svg_code = self._validate_svg(svg_code)

        return svg_code

    def generate_ascii(
        self,
        subject: str,
        description: str = "",
        width: int = 80,
        height: int = 24,
        style: Literal["petme", "box-drawing", "minimal"] = "petme"
    ) -> str:
        """
        Generate ASCII art diagram using C64 PetMe character set

        Args:
            subject: What to illustrate
            description: Additional context
            width: Character width (default 80×24 terminal)
            height: Character height
            style: ASCII style (petme=C64 chars, box-drawing=Unicode, minimal=basic)

        Returns:
            ASCII art as string
        """
        prompt = f"""Generate ASCII art diagram of: {subject}

DESCRIPTION: {description or f"A clear ASCII art representation of {subject}"}

SPECIFICATIONS:
- Character set: C64 PetMe / PETSCII (UTF-8 compatible)
- Dimensions: {width}×{height} characters
- Style: {style.upper()}
- Monospaced layout

CHARACTER SET (PetMe64):
Box Drawing:
  ┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼ (corners, lines, junctions)
  ╔ ╗ ╚ ╝ ═ ║ ╠ ╣ ╦ ╩ ╬ (double lines)

Block Elements:
  █ (full) ▓ (dark) ▒ (medium) ░ (light)
  ▀ (top half) ▄ (bottom half) ▌ (left half) ▐ (right half)
  ▘ ▝ ▖ ▗ (quarter blocks)

Symbols:
  ♥ ♠ ♣ ♦ ★ ☆ ○ ● ◉ ◯ → ← ↑ ↓ ⚠ ✓ ✗

REQUIREMENTS:
1. Use ONLY monospaced characters (UTF-8 compatible)
2. Exactly {width} characters wide (pad with spaces)
3. Exactly {height} lines tall
4. Clear, recognizable shapes
5. Labels using ASCII text
6. NO color codes, ANSI escape sequences
7. Plain text output ONLY

LAYOUT:
- Center important elements
- Use borders for emphasis
- Add title/labels where appropriate
- Include legend if needed
- Maintain proper spacing

OUTPUT FORMAT:
```
[ASCII art exactly {width}×{height}]
```

Generate clean, terminal-ready ASCII art.
"""

        response = self.model.generate_content(prompt)
        ascii_art = self._extract_code_block(response.text) or response.text.strip()

        # Validate dimensions
        lines = ascii_art.split('\n')
        if len(lines) != height:
            print(f"Warning: ASCII art has {len(lines)} lines, expected {height}")

        return ascii_art

    def generate_teletext(
        self,
        subject: str,
        description: str = "",
        width: int = 40,
        height: int = 25,
        colors: list = None,
        style: Literal["mosaic", "contiguous", "separated"] = "mosaic"
    ) -> str:
        """
        Generate Teletext graphics using WST mosaic blocks

        Args:
            subject: What to illustrate
            description: Additional context
            width: Character width (default 40×25 teletext)
            height: Character height
            colors: WST color names (BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE)
            style: Mosaic mode (mosaic=mixed, contiguous=solid, separated=spaced)

        Returns:
            Teletext HTML with mosaic blocks
        """
        if colors is None:
            colors = ["GREEN", "BLUE", "YELLOW", "RED", "WHITE"]

        prompt = f"""Generate Teletext mosaic graphics for: {subject}

DESCRIPTION: {description or f"Teletext block graphics representation of {subject}"}

SPECIFICATIONS:
- Format: HTML with Teletext mosaic entities
- Dimensions: {width}×{height} characters
- Colors: {', '.join(colors)} (WST palette)
- Mode: {style.upper()}

WST COLOR PALETTE:
- BLACK   #000000 (backgrounds)
- RED     #FF0000 (warnings, fire)
- GREEN   #00FF00 (vegetation, OK status)
- YELLOW  #FFFF00 (highlights, caution)
- BLUE    #0000FF (water, sky)
- MAGENTA #FF00FF (special markers)
- CYAN    #00FFFF (ice, water features)
- WHITE   #FFFFFF (text, highlights)

MOSAIC CHARACTERS (2×3 pixel blocks):
Contiguous (solid): &#xE200; - &#xE23F;
Separated (spaced): &#xE240; - &#xE27F;

Common patterns:
- Empty: &#xE200; (000000)
- Full:  &#xE23F; (111111)
- Left:  &#xE215; (101010)
- Right: &#xE22A; (010101)
- Top:   &#xE203; (110000)
- Bottom:&#xE230; (001100)

REQUIREMENTS:
1. Use mosaic HTML entities (&#xE2XX;)
2. Wrap in color spans: <span class="bg-red">&#xE23F;</span>
3. Create recognizable shapes with blocks
4. Use appropriate colors for subject
5. Include title and labels
6. Exactly {width}×{height} grid

OUTPUT FORMAT:
```html
<!doctype html>
<html>
<head>
<title>{subject}</title>
<style>
  body {{ font-family: 'Teletext', monospace; background: #000; color: #fff; }}
  .bg-black {{ background: #000; }}
  .bg-red {{ background: #F00; }}
  .bg-green {{ background: #0F0; }}
  .bg-yellow {{ background: #FF0; }}
  .bg-blue {{ background: #00F; }}
  .bg-magenta {{ background: #F0F; }}
  .bg-cyan {{ background: #0FF; }}
  .bg-white {{ background: #FFF; color: #000; }}
</style>
</head>
<body>
<pre>[{width}×{height} mosaic grid]</pre>
</body>
</html>
```

Generate complete Teletext HTML with mosaic graphics.
"""

        response = self.model.generate_content(prompt)
        return response.text

    def generate(
        self,
        subject: str,
        description: str = "",
        format: Literal["ascii", "teletext", "svg"] = "svg",
        style: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Unified generation across all formats

        Args:
            subject: What to illustrate
            description: Additional context
            format: Output format (ascii, teletext, svg)
            style: Format-specific style
                   - ascii: "petme", "box-drawing", "minimal"
                   - teletext: "mosaic", "contiguous", "separated"
                   - svg: "technical-kinetic", "hand-illustrative"
            **kwargs: Format-specific parameters

        Returns:
            Generated content
        """
        if format == "ascii":
            return self.generate_ascii(
                subject, description,
                style=style or "petme",
                **kwargs
            )
        elif format == "teletext":
            return self.generate_teletext(
                subject, description,
                style=style or "mosaic",
                **kwargs
            )
        elif format == "svg":
            return self.generate_svg(
                subject,
                style=style or self.auto_detect_style(subject),
                description=description,
                **kwargs
            )
        else:
            raise ValueError(f"Unknown format: {format}")

    def generate_all_formats(
        self,
        subject: str,
        description: str = ""
    ) -> Dict[str, str]:
        """
        Generate ASCII, Teletext, and SVG from single description

        Args:
            subject: What to illustrate
            description: Additional context

        Returns:
            Dictionary with keys: ascii, teletext, svg_technical, svg_organic
        """
        return {
            "ascii": self.generate_ascii(subject, description, width=80, height=24),
            "teletext": self.generate_teletext(subject, description, width=40, height=25),
            "svg_technical": self.generate_svg(subject, "technical-kinetic", description),
            "svg_organic": self.generate_svg(subject, "hand-illustrative", description)
        }

    def generate_guide(
        self,
        topic: str,
        category: str,
        length: Literal["brief", "standard", "comprehensive"] = "standard",
        style: Literal["reference", "tutorial", "checklist"] = "reference"
    ) -> str:
        """
        Generate survival guide markdown

        Args:
            topic: Guide topic (e.g., "fire-starting-methods")
            category: Category (water, fire, shelter, etc.)
            length: Content length
            style: Guide format

        Returns:
            Markdown content
        """
        length_targets = {
            "brief": "500-800 words",
            "standard": "800-1500 words",
            "comprehensive": "1500-3000 words"
        }

        prompt = f"""Generate a survival guide about {topic} in the {category} category.

FORMAT: {style.upper()}
LENGTH: {length_targets[length]}

STRUCTURE:
# {topic.replace('-', ' ').title()}

## Overview
Brief introduction (2-3 sentences)

## {self._get_section_headers(style)}

## Safety Considerations
Critical warnings and precautions

## Related Topics
- Cross-references to related guides

---
**Category**: {category}
**Skill Level**: [Beginner/Intermediate/Advanced]
**Time Required**: [estimate]
**Tools Needed**: [list]

Generate comprehensive, accurate survival information.
Use clear headers, bullet points, and practical steps.
Include safety warnings where critical.
"""

        response = self.model.generate_content(prompt)
        return response.text

    def convert_resource(
        self,
        source: str,
        source_type: Literal["pdf", "url", "html", "doc"] = "url",
        output_format: str = "markdown"
    ) -> str:
        """
        Convert external resource to uDOS format

        Args:
            source: Source path/URL
            source_type: Input format
            output_format: Desired output format

        Returns:
            Converted content
        """
        prompt = f"""Convert this {source_type.upper()} resource to {output_format.upper()} format:

SOURCE: {source}

REQUIREMENTS:
- Preserve all factual information
- Maintain logical structure with proper headers
- Convert tables to markdown tables
- Extract images with descriptions
- Add attribution and source citation
- Format for uDOS knowledge bank

Output clean {output_format} only.
"""

        response = self.model.generate_content(prompt)
        return response.text

    def auto_detect_style(self, subject: str) -> str:
        """
        Automatically detect appropriate style for subject

        Args:
            subject: Subject to illustrate

        Returns:
            Recommended style name
        """
        subject_lower = subject.lower()

        # Check organic/natural keywords first (more specific)
        organic_keywords = self.styles["subject_style_mapping"]["hand_illustrative"]
        if any(keyword in subject_lower for keyword in organic_keywords):
            return "hand-illustrative"

        # Check technical keywords
        technical_keywords = self.styles["subject_style_mapping"]["technical_kinetic"]
        if any(keyword in subject_lower for keyword in technical_keywords):
            return "technical-kinetic"

        # Heuristic: if contains words like "human", "plant", "animal", "natural" -> organic
        organic_indicators = ["human", "body", "organ", "plant", "animal", "tree", "leaf", "flower",
                             "landscape", "mountain", "river", "food", "natural", "organic"]
        if any(word in subject_lower for word in organic_indicators):
            return "hand-illustrative"

        # Default to technical for unclear subjects
        return "technical-kinetic"

    def _extract_svg(self, response_text: str) -> str:
        """Extract SVG code from response"""
        # Look for XML declaration
        match = re.search(r'<\?xml.*?</svg>', response_text, re.DOTALL)
        if match:
            return match.group(0)

        # Try without XML declaration
        match = re.search(r'<svg.*?</svg>', response_text, re.DOTALL)
        if match:
            return f'<?xml version="1.0" encoding="UTF-8"?>\n{match.group(0)}'

        raise ValueError("No valid SVG found in response")

    def _validate_svg(self, svg_code: str) -> str:
        """Basic SVG validation and cleanup"""
        # Check required elements
        if '<svg' not in svg_code:
            raise ValueError("Invalid SVG: missing <svg> tag")

        # Check viewBox
        if 'viewBox' not in svg_code:
            print("Warning: SVG missing viewBox attribute")

        # Check accessibility
        if '<title>' not in svg_code:
            print("Warning: SVG missing <title> element (accessibility)")

        if '<desc>' not in svg_code:
            print("Warning: SVG missing <desc> element (accessibility)")

        # Basic cleanup
        svg_code = svg_code.strip()

        # Check file size
        size_kb = len(svg_code.encode('utf-8')) / 1024
        if size_kb > 50:
            print(f"Warning: SVG size {size_kb:.1f}KB exceeds 50KB target")

        return svg_code

    def _extract_code_block(self, response_text: str) -> Optional[str]:
        """Extract code from markdown code blocks"""
        # Look for triple backtick code blocks
        match = re.search(r'```(?:ascii|txt|html|svg)?\n(.*?)```', response_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _get_section_headers(self, style: str) -> str:
        """Get appropriate section headers for guide style"""
        headers = {
            "reference": "Key Information\n## Techniques\n## Equipment\n## Best Practices",
            "tutorial": "What You'll Need\n## Step-by-Step Instructions\n## Tips and Tricks\n## Troubleshooting",
            "checklist": "Preparation\n## Execution Steps\n## Verification\n## Completion Criteria"
        }
        return headers.get(style, headers["reference"])


# Convenience functions for direct use
def generate_technical_diagram(subject: str, description: str = "", api_key: Optional[str] = None) -> str:
    """Quick technical diagram generation"""
    ok = OKAssist(api_key=api_key)
    return ok.generate_svg(subject, style="technical-kinetic", description=description)


def generate_organic_illustration(subject: str, description: str = "", api_key: Optional[str] = None) -> str:
    """Quick organic illustration generation"""
    ok = OKAssist(api_key=api_key)
    return ok.generate_svg(subject, style="hand-illustrative", description=description)


def generate_survival_guide(topic: str, category: str, api_key: Optional[str] = None) -> str:
    """Quick guide generation"""
    ok = OKAssist(api_key=api_key)
    return ok.generate_guide(topic, category)


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python gemini.py <subject> [format] [style] [description]")
        print("Formats: ascii, teletext, svg (default)")
        print("Styles: ")
        print("  - ASCII: petme, box-drawing, minimal")
        print("  - Teletext: mosaic, contiguous, separated")
        print("  - SVG: technical-kinetic, hand-illustrative, auto")
        sys.exit(1)

    subject = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "svg"
    style = sys.argv[3] if len(sys.argv) > 3 else None
    description = sys.argv[4] if len(sys.argv) > 4 else ""

    ok = OKAssist()

    # Auto-detect style for SVG if requested
    if output_format == "svg" and (style == "auto" or style is None):
        style = ok.auto_detect_style(subject)
        print(f"Auto-detected style: {style}")

    # Generate content
    print(f"Generating {output_format} {f'({style})' if style else ''} of '{subject}'...")

    content = ok.generate(subject, description, format=output_format, style=style)

    # Save to file
    extensions = {"ascii": ".txt", "teletext": ".html", "svg": ".svg"}
    filename = f"{subject.replace(' ', '-')}{extensions.get(output_format, '.txt')}"

    with open(filename, 'w') as f:
        f.write(content)

    size_kb = len(content.encode('utf-8')) / 1024
    print(f"✓ Saved to {filename} ({size_kb:.1f}KB)")
