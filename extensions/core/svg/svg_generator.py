"""
SVG Generator Service - v1.0.0
AI-powered SVG diagram generation with multiple artistic styles

Features:
  - 4 artistic styles: lineart, blueprint, sketch, isometric
  - Gemini AI integration for SVG generation
  - SVG validation (well-formed XML)
  - Post-processing and refinement
  - Terminal preview (ASCII conversion)
  - Export to sandbox/drafts/svg/

Author: uDOS Core Team
Version: 1.0.0
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, Any, List
import re
from datetime import datetime

try:
    from core.config import Config
    from core.services.gemini_generator import get_gemini_generator
except ImportError:
    # Fallback for testing
    Config = None
    get_gemini_generator = None


class SVGGenerator:
    """AI-powered SVG diagram generator with artistic styles"""

    # Artistic styles with descriptions
    STYLES = {
        'lineart': {
            'name': 'Line Art',
            'description': 'Clean, minimal black lines on white background',
            'stroke_width': 2,
            'fill': 'none',
            'colors': False
        },
        'blueprint': {
            'name': 'Blueprint',
            'description': 'Technical blueprint style with blue background',
            'stroke_width': 1,
            'fill': 'none',
            'colors': ['#4A90E2', '#E8F4F8'],
            'background': '#003366'
        },
        'sketch': {
            'name': 'Hand Sketch',
            'description': 'Hand-drawn sketch style with rough lines',
            'stroke_width': 2,
            'fill': 'none',
            'roughness': True,
            'colors': ['#333333', '#666666']
        },
        'isometric': {
            'name': 'Isometric',
            'description': '3D isometric projection with depth',
            'stroke_width': 2,
            'fill': True,
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
            'projection': 'isometric'
        }
    }

    def __init__(self, config: Optional[Any] = None):
        """Initialize SVG generator

        Args:
            config: Optional Config instance
        """
        self.config = config or (Config() if Config else None)
        self.output_dir = Path('sandbox/drafts/svg')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Get Gemini generator if available
        self.gemini = None
        if get_gemini_generator:
            try:
                self.gemini = get_gemini_generator()
            except Exception:
                pass  # AI optional

    def generate(self, description: str, style: str = 'lineart',
                 save_path: Optional[str] = None) -> str:
        """Generate SVG diagram from description

        Args:
            description: Text description of what to diagram
            style: Artistic style (lineart, blueprint, sketch, isometric)
            save_path: Optional path to save SVG file

        Returns:
            SVG content as string
        """
        # Validate style
        style = style.lower()
        if style not in self.STYLES:
            raise ValueError(f"Unknown style: {style}. Use: {', '.join(self.STYLES.keys())}")

        # Build AI prompt
        prompt = self._build_prompt(description, style)

        # Generate SVG with AI or fallback
        svg_content = self._generate_with_ai(prompt, description, style)

        # Post-process (adds xmlns, viewBox, etc.)
        svg_content = self._post_process(svg_content, style)

        # Validate SVG after post-processing
        if not self._validate_svg(svg_content):
            # If validation fails, try template as last resort
            print("Post-processing validation failed, using template fallback")
            svg_content = self._generate_template(description, style)
            svg_content = self._post_process(svg_content, style)

            # Final validation
            if not self._validate_svg(svg_content):
                raise ValueError("Generated SVG is not well-formed XML")

        # Save if requested
        if save_path:
            self._save_svg(svg_content, save_path)

        return svg_content

    def _build_prompt(self, description: str, style: str) -> str:
        """Build AI prompt for SVG generation

        Args:
            description: User's diagram description
            style: Artistic style

        Returns:
            Complete prompt for AI
        """
        style_info = self.STYLES[style]

        prompt = f"""Generate an SVG diagram with the following specifications:

DESCRIPTION: {description}

ARTISTIC STYLE: {style_info['name']}
- {style_info['description']}
- Stroke width: {style_info['stroke_width']}
- Fill: {'yes' if style_info.get('fill') else 'no'}

TECHNICAL REQUIREMENTS:
- Valid SVG 1.1 XML format
- ViewBox: 0 0 800 600 (width height)
- Clean, semantic markup
- No external dependencies
- Self-contained (embedded styles if needed)

STYLE GUIDELINES:
"""

        if style == 'lineart':
            prompt += """
- Use only black (#000000) lines
- Stroke width: 2
- No fills (fill="none")
- Clean, precise paths
- Minimal detail, focus on key elements
"""
        elif style == 'blueprint':
            prompt += """
- Blue background (#003366)
- White/light blue lines (#4A90E2, #E8F4F8)
- Technical drawing style
- Add grid background (optional)
- Include measurement indicators
- Clean, technical appearance
"""
        elif style == 'sketch':
            prompt += """
- Hand-drawn appearance
- Slightly rough, organic lines
- Gray tones (#333333, #666666)
- Add subtle variations in stroke
- Natural, informal feel
- No perfect circles/straight lines
"""
        elif style == 'isometric':
            prompt += """
- 3D isometric projection (30° angles)
- Multiple colors: reds, blues, teals
- Solid fills with outlines
- Show depth and dimensionality
- Layer elements for 3D effect
- Clear perspective
"""

        prompt += """

EXAMPLE SVG STRUCTURE:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <title>{description}</title>
  <desc>Generated diagram</desc>

  <!-- Your diagram elements here -->
  <rect x="100" y="100" width="200" height="150" stroke="#000" fill="none"/>
  <circle cx="400" cy="300" r="50" stroke="#000" fill="none"/>
  <path d="M 100 100 L 400 300" stroke="#000"/>
  <text x="200" y="175" font-family="sans-serif" font-size="16">Label</text>
</svg>
```

Generate ONLY the SVG code (no markdown, no explanations). Start with <svg> and end with </svg>.
"""

        return prompt

    def _generate_with_ai(self, prompt: str, description: str, style: str) -> str:
        """Generate SVG using AI or fallback

        Args:
            prompt: AI prompt (contains style requirements)
            description: User description
            style: Artistic style

        Returns:
            SVG content
        """
        if self.gemini:
            try:
                # Extract requirements from prompt for Gemini API
                style_config = self.STYLES.get(style, {})
                requirements = [
                    f"Style: {style}",
                    f"Description: {style_config.get('description', style)}",
                ]

                # Add style-specific colors if available
                if 'colors' in style_config and isinstance(style_config['colors'], list):
                    requirements.append(f"Colors: {', '.join(style_config['colors'])}")

                # Use Gemini to generate SVG
                # The generate_svg method returns (svg_content, metadata)
                svg_content, metadata = self.gemini.generate_svg(
                    subject=description,
                    diagram_type=style,
                    requirements=requirements
                )

                # Validate the SVG
                if svg_content and '<svg' in svg_content:
                    # Extract just the SVG if it's wrapped in markdown
                    extracted = self._extract_svg(svg_content)
                    if extracted:
                        # Validate extracted SVG before returning
                        if self._validate_svg(extracted):
                            return extracted
                        # If invalid, try raw content
                        if self._validate_svg(svg_content):
                            return svg_content
                    # If extraction failed, try raw content
                    elif self._validate_svg(svg_content):
                        return svg_content

                # If we got here, AI generated invalid SVG
                print(f"AI generated invalid SVG, falling back to template")

            except AttributeError as e:
                print(f"AI generation failed: {e}, falling back to template")
            except Exception as e:
                print(f"AI generation error: {e}, falling back to template")

        # Fallback to simple template
        return self._generate_template(description, style)

    def _extract_svg(self, text: str) -> Optional[str]:
        """Extract SVG code from AI response

        Args:
            text: AI response text

        Returns:
            SVG content or None
        """
        # Try to find SVG in markdown code blocks
        svg_match = re.search(r'```(?:xml|svg)?\s*(<svg.*?</svg>)\s*```', text, re.DOTALL)
        if svg_match:
            return svg_match.group(1)

        # Try to find raw SVG
        svg_match = re.search(r'(<svg.*?</svg>)', text, re.DOTALL)
        if svg_match:
            return svg_match.group(1)

        return None

    def _generate_template(self, description: str, style: str) -> str:
        """Generate simple SVG template (fallback)

        Args:
            description: Diagram description
            style: Artistic style

        Returns:
            Simple SVG template
        """
        style_info = self.STYLES[style]

        # Basic template with style
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <title>{description}</title>
  <desc>Generated by uDOS SVG Generator (template fallback)</desc>

'''

        if style == 'blueprint':
            svg += '  <rect width="800" height="600" fill="#003366"/>\n'
            svg += '  <g stroke="#4A90E2" stroke-width="0.5" opacity="0.3">\n'
            for i in range(0, 800, 50):
                svg += f'    <line x1="{i}" y1="0" x2="{i}" y2="600"/>\n'
            for i in range(0, 600, 50):
                svg += f'    <line x1="0" y1="{i}" x2="800" y2="{i}"/>\n'
            svg += '  </g>\n'

        # Add simple diagram elements
        stroke_color = '#000000'
        if style == 'blueprint':
            stroke_color = '#4A90E2'
        elif style == 'sketch':
            stroke_color = '#333333'

        fill = 'none' if not style_info.get('fill') else '#4ECDC4'

        svg += f'''  <g id="diagram" stroke="{stroke_color}" stroke-width="{style_info['stroke_width']}" fill="{fill}">
    <rect x="200" y="150" width="400" height="300" rx="10"/>
    <circle cx="400" cy="300" r="80"/>
    <text x="400" y="310" text-anchor="middle" font-family="sans-serif" font-size="24" fill="{stroke_color}">
      {description[:20]}...
    </text>
  </g>
</svg>'''

        return svg

    def _validate_svg(self, svg_content: str) -> bool:
        """Validate SVG is well-formed XML

        Args:
            svg_content: SVG XML content

        Returns:
            True if valid, False otherwise
        """
        try:
            ET.fromstring(svg_content)
            return True
        except ET.ParseError:
            return False

    def _post_process(self, svg_content: str, style: str) -> str:
        """Post-process SVG content

        Args:
            svg_content: Raw SVG content
            style: Artistic style

        Returns:
            Processed SVG content
        """
        # Simple string-based post-processing (no XML parsing to avoid namespace issues)

        # Add xmlns if missing
        if 'xmlns=' not in svg_content:
            svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1)

        # Add viewBox if missing
        if 'viewBox=' not in svg_content and 'viewbox=' not in svg_content.lower():
            svg_content = svg_content.replace('<svg', '<svg viewBox="0 0 800 600"', 1)

        return svg_content

    def _save_svg(self, svg_content: str, filepath: str) -> str:
        """Save SVG to file

        Args:
            svg_content: SVG XML content
            filepath: Output file path

        Returns:
            Absolute path to saved file
        """
        path = Path(filepath)

        # Default to output directory if relative path
        if not path.is_absolute():
            path = self.output_dir / path

        # Ensure .svg extension
        if path.suffix != '.svg':
            path = path.with_suffix('.svg')

        # Create parent directories
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        path.write_text(svg_content, encoding='utf-8')

        return str(path.absolute())

    def preview_ascii(self, svg_content: str, width: int = 80) -> str:
        """Generate ASCII preview of SVG (basic)

        Args:
            svg_content: SVG XML content
            width: Terminal width for preview

        Returns:
            ASCII representation
        """
        # Very basic ASCII preview (just show structure)
        try:
            root = ET.fromstring(svg_content)

            preview = f"╔{'═' * (width - 2)}╗\n"
            preview += f"║ SVG Preview{' ' * (width - 15)}║\n"
            preview += f"╠{'═' * (width - 2)}╣\n"

            # Count elements
            rects = len(root.findall('.//{http://www.w3.org/2000/svg}rect') + root.findall('.//rect'))
            circles = len(root.findall('.//{http://www.w3.org/2000/svg}circle') + root.findall('.//circle'))
            paths = len(root.findall('.//{http://www.w3.org/2000/svg}path') + root.findall('.//path'))
            texts = len(root.findall('.//{http://www.w3.org/2000/svg}text') + root.findall('.//text'))

            preview += f"║ Elements: {rects} rects, {circles} circles, {paths} paths, {texts} text{' ' * (width - 50)}║\n"
            preview += f"╚{'═' * (width - 2)}╝\n"

            return preview
        except:
            return "Error generating preview"


# Helper functions
def generate_svg(description: str, style: str = 'lineart',
                save_path: Optional[str] = None) -> str:
    """Quick SVG generation helper

    Args:
        description: What to diagram
        style: Artistic style
        save_path: Optional save path

    Returns:
        SVG content
    """
    generator = SVGGenerator()
    return generator.generate(description, style, save_path)


def quick_svg(description: str) -> str:
    """Ultra-quick SVG generation (lineart style)

    Args:
        description: What to diagram

    Returns:
        SVG content
    """
    return generate_svg(description, 'lineart')
