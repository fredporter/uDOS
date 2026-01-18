"""
Graphics module for uDOS Core

Text-first graphics capabilities:
- ASCII pattern generation
- Block graphics (teletext/sextant)
- Diagram rendering
- Pattern compilation
- Feed generation/consumption

This module is TUI-first and operates on text representations.
SVG/web rendering is delegated to Wizard server.
"""

from .ascii_patterns import ASCIIPatternGenerator
from .block_graphics import BlockGraphicsRenderer, TeletextEncoder
from .diagram_parser import DiagramParser
from .feed_handler import FeedHandler

__all__ = [
    "ASCIIPatternGenerator",
    "BlockGraphicsRenderer",
    "TeletextEncoder",
    "DiagramParser",
    "FeedHandler",
]

__version__ = "1.0.0"
