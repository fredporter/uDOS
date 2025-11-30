"""
uDOS v1.1.5 - SVG Command Handler

Generate SVG diagrams from text descriptions using AI.

Commands:
- SVG: Generate SVG diagram from text description

Author: uDOS Core Team
Version: 1.0.0
"""

from pathlib import Path
from typing import Optional


class SVGHandler:
    """Handle SVG diagram generation commands."""

    def __init__(self, viewport=None, logger=None):
        """
        Initialize SVG handler.

        Args:
            viewport: Viewport instance for output display
            logger: Logger instance for logging
        """
        self.viewport = viewport
        self.logger = logger
        self._generator = None  # Lazy load

    @property
    def generator(self):
        """Lazy load SVG generator."""
        if self._generator is None:
            try:
                from extensions.core.svg_generator import SVGGenerator
                self._generator = SVGGenerator()
                if self.logger:
                    self.logger.info("SVG generator loaded successfully")
            except ImportError as e:
                if self.logger:
                    self.logger.error(f"Failed to load SVG generator: {e}")
                raise ImportError(
                    "SVG generator extension not available. "
                    "Install with: POKE INSTALL svg-generator"
                ) from e
        return self._generator

    def handle_command(self, params):
        """
        Handle SVG command.

        Args:
            params: Command parameters [description, options...]

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        # Parse command
        description_parts = []
        style = "lineart"
        save_path = None
        preview = True

        i = 0
        while i < len(params):
            param = params[i]

            if param == "--style":
                if i + 1 < len(params):
                    style = params[i + 1]
                    i += 2
                else:
                    return "❌ --style requires a value\n\n" + self._show_help()

            elif param == "--save":
                if i + 1 < len(params):
                    save_path = params[i + 1]
                    i += 2
                else:
                    return "❌ --save requires a filename\n\n" + self._show_help()

            elif param == "--no-preview":
                preview = False
                i += 1

            else:
                description_parts.append(param)
                i += 1

        # Build description
        description = " ".join(description_parts)

        if not description:
            return "❌ No description provided\n\n" + self._show_help()

        # Validate style
        valid_styles = ["lineart", "blueprint", "sketch", "isometric"]
        if style not in valid_styles:
            return (
                f"❌ Invalid style: {style}\n"
                f"Valid styles: {', '.join(valid_styles)}\n\n"
                + self._show_help()
            )

        # Generate SVG
        try:
            if self.logger:
                self.logger.info(f"Generating SVG: {description} (style: {style})")

            svg_content = self.generator.generate(
                description=description,
                style=style,
                save_path=save_path
            )

            if not svg_content:
                return "❌ Failed to generate SVG diagram"

            # Build response
            response = f"✅ SVG diagram generated: {description}\n"
            response += f"   Style: {style}\n"

            # Save if requested
            if save_path:
                saved_path = self.generator._save_svg(svg_content, save_path)
                response += f"   Saved: {saved_path}\n"
            else:
                # Auto-save to drafts
                from datetime import datetime
                filename = f"{description.replace(' ', '-')[:30]}-{style}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.svg"
                saved_path = self.generator._save_svg(svg_content, filename)
                response += f"   Saved: {saved_path}\n"

            # Show preview if requested
            if preview:
                ascii_preview = self.generator.preview_ascii(svg_content, width=60)
                response += f"\n{ascii_preview}\n"

            # Show next steps
            response += "\n💡 Next Steps:\n"
            response += f"   - View in browser: open {saved_path}\n"
            response += "   - Edit manually: Use any SVG editor\n"
            response += "   - Regenerate: SVG <description> --style <other-style>\n"

            if self.logger:
                self.logger.info(f"SVG generated successfully: {saved_path}")

            return response

        except ImportError as e:
            return (
                f"❌ SVG generator not available: {e}\n\n"
                "The SVG generator extension is not installed or configured.\n"
                "This feature requires:\n"
                "  - Gemini API key (GEMINI_API_KEY in .env)\n"
                "  - svg-generator extension\n\n"
                "Install: POKE INSTALL svg-generator"
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"SVG generation error: {e}", exc_info=True)
            return f"❌ Error generating SVG: {e}"

    def _show_help(self):
        """Show command help."""
        return """
╔══════════════════════════════════════════════════════════════════════╗
║  SVG - Generate SVG Diagrams from Text                               ║
╚══════════════════════════════════════════════════════════════════════╝

USAGE:
  SVG <description> [--style <style>] [--save <file>] [--no-preview]

ARGUMENTS:
  <description>     Text description of diagram (required)
  --style <style>   Artistic style (default: lineart)
  --save <file>     Save to specific file (optional)
  --no-preview      Skip ASCII preview (optional)

STYLES:
  lineart           Clean black lines, minimal (default)
  blueprint         Technical blue background, grid
  sketch            Hand-drawn gray tones, rough lines
  isometric         3D projection, multiple colors

EXAMPLES:
  SVG water filter diagram
    Generate simple line art of water filter

  SVG fire triangle --style blueprint
    Generate technical blueprint of fire triangle

  SVG shelter types comparison --style isometric --save shelter.svg
    Generate 3D isometric view and save to file

  SVG first aid steps --style sketch --no-preview
    Generate sketch-style diagram without preview

OUTPUT:
  Generated SVGs are saved to: sandbox/drafts/svg/
  Files can be opened in any browser or SVG editor

REQUIREMENTS:
  - Gemini API key (GEMINI_API_KEY in .env)
  - svg-generator extension installed

SEE ALSO:
  DRAW       - ASCII diagram generation (offline)
  DIAGRAM    - ASCII art library browser
  GENERATE   - Script generation (AI)
  POKE INFO svg-generator - Extension details
"""


def handle_svg_command(params, viewport=None, logger=None):
    """
    Helper function for SVG command.

    Args:
        params: Command parameters
        viewport: Viewport instance
        logger: Logger instance

    Returns:
        Command result message
    """
    handler = SVGHandler(viewport=viewport, logger=logger)
    return handler.handle_command(params)


# Command metadata for uDOS command system
COMMAND_INFO = {
    'name': 'SVG',
    'version': '1.0.0',
    'category': 'graphics',
    'description': 'Generate SVG diagrams from text descriptions',
    'requires': ['svg-generator extension', 'Gemini API key'],
    'examples': [
        'SVG water filter diagram',
        'SVG fire triangle --style blueprint',
        'SVG shelter types --style isometric --save shelter.svg'
    ],
    'see_also': ['DRAW', 'DIAGRAM', 'GENERATE']
}
