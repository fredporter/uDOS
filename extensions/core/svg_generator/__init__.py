"""
SVG Generator Extension - v1.0.0
AI-powered SVG diagram generation with artistic styles

Provides:
  - GENERATE SVG command
  - Multiple artistic styles (lineart, blueprint, sketch, isometric)
  - Gemini AI integration for diagram generation
  - SVG validation and post-processing
  - Terminal preview (ASCII conversion)

Author: uDOS Core Team
License: MIT
"""

from .svg_generator import SVGGenerator, generate_svg, quick_svg

__version__ = "1.0.0"
__all__ = ["SVGGenerator", "generate_svg", "quick_svg"]
