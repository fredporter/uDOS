"""PATTERN command handler - Terminal pattern generator and display."""

from typing import List, Dict, Optional
import sys
import os
from core.commands.base import BaseCommandHandler
from core.services.pattern_generator import PatternGenerator
from core.services.logging_manager import get_logger, LogTags

logger = get_logger("command-pattern")


class PatternHandler(BaseCommandHandler):
    """Handler for PATTERN command - terminal pattern displays."""

    def __init__(self):
        """Initialize pattern handler."""
        super().__init__()
        self.available_patterns = [
            "c64",
            "chevrons",
            "scanlines",
            "raster",
            "progress",
            "mosaic",
        ]
        self.current_pattern = 0

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle PATTERN command - display terminal patterns.

        Syntax:
            PATTERN              - Show next pattern (cycles through all)
            PATTERN <name>       - Show specific pattern (c64, chevrons, scanlines, raster, progress, mosaic)
            PATTERN LIST         - List available patterns
            PATTERN CYCLE        - Run pattern cycling sequence

        Args:
            command: Command name (PATTERN)
            params: List of parameters
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with status and rendered pattern
        """
        if not params:
            # Default: show next pattern in cycle
            return self._show_next_pattern()

        action = params[0].lower()  # Use lowercase for pattern names

        if action == "list":
            return self._list_patterns()
        elif action == "cycle":
            return self._cycle_patterns(params[1:])
        elif action in self.available_patterns:
            return self._show_pattern(action)
        else:
            return {
                "status": "error",
                "message": f"Unknown pattern '{params[0]}'. Use PATTERN LIST to see available patterns.",
                "available": self.available_patterns,
            }

    def _show_next_pattern(self) -> Dict:
        """Show the next pattern in the cycle."""
        pattern = self.available_patterns[self.current_pattern]
        self.current_pattern = (self.current_pattern + 1) % len(self.available_patterns)
        return self._show_pattern(pattern)

    def _show_pattern(self, pattern_name: str) -> Dict:
        """
        Show a specific pattern.

        Args:
            pattern_name: Name of pattern to display

        Returns:
            Dict with rendered pattern
        """
        try:
            # Get terminal dimensions
            width = self._get_terminal_width()
            height = self._get_terminal_height()

            # Detect ASCII-only mode (safer for older terminals)
            ascii_only = os.environ.get("UDOS_ASCII_ONLY", "").lower() in ("1", "true")

            # Generate pattern
            gen = PatternGenerator(width=width, height=height, ascii_only=ascii_only)
            lines = gen.render_pattern(pattern_name, frames=height)

            # Format output
            output = "\n".join(lines)

            logger.info(
                f"{LogTags.LOCAL} PATTERN: Displayed '{pattern_name}' ({len(lines)} lines)"
            )

            return {
                "status": "success",
                "pattern": pattern_name,
                "lines": len(lines),
                "width": width,
                "height": height,
                "output": output,
            }
        except Exception as e:
            logger.error(
                f"{LogTags.LOCAL} PATTERN: Failed to render {pattern_name}: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Failed to render pattern '{pattern_name}': {str(e)}",
            }

    def _cycle_patterns(self, params: List[str]) -> Dict:
        """
        Cycle through all patterns interactively.

        Args:
            params: Optional parameters (e.g., duration)

        Returns:
            Dict with status
        """
        try:
            # Parse optional duration (default 5 seconds per pattern)
            duration = 5
            if params:
                try:
                    duration = int(params[0])
                except ValueError:
                    pass

            logger.info(
                f"{LogTags.LOCAL} PATTERN: Starting cycle ({duration}s per pattern)"
            )

            width = self._get_terminal_width()
            height = self._get_terminal_height()
            ascii_only = os.environ.get("UDOS_ASCII_ONLY", "").lower() in ("1", "true")

            gen = PatternGenerator(width=width, height=height, ascii_only=ascii_only)

            output_lines = []

            for pattern_name in self.available_patterns:
                # Add pattern title
                title = f"\n{'═' * 40}\n  {pattern_name.upper()} PATTERN\n{'═' * 40}\n"
                output_lines.append(title)

                # Generate and append pattern
                lines = gen.render_pattern(pattern_name, frames=height)
                output_lines.extend(lines)
                output_lines.append("")

            return {
                "status": "success",
                "patterns_shown": len(self.available_patterns),
                "duration_per_pattern": duration,
                "output": "\n".join(output_lines),
                "message": f"Cycled through {len(self.available_patterns)} patterns",
            }
        except Exception as e:
            logger.error(f"{LogTags.LOCAL} PATTERN: Cycle failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Pattern cycle failed: {str(e)}",
            }

    def _list_patterns(self) -> Dict:
        """List all available patterns."""
        descriptions = {
            "c64": "Commodore 64-style loading bar with colour cycling",
            "chevrons": "Diagonal chevron scrolling pattern",
            "scanlines": "Horizontal scanline gradient",
            "raster": "Demoscene raster bars with sinusoidal movement",
            "progress": "Chunky progress bar with bouncing head",
            "mosaic": "Colourful mosaic with random tiles",
        }

        pattern_list = []
        for name in self.available_patterns:
            pattern_list.append(
                {
                    "name": name,
                    "description": descriptions.get(name, ""),
                }
            )

        return {
            "status": "success",
            "patterns": pattern_list,
            "count": len(pattern_list),
            "message": f"Available patterns: {', '.join(self.available_patterns)}",
        }

    def _get_terminal_width(self) -> int:
        """Get terminal width (clamped to 80 max)."""
        try:
            width = os.get_terminal_size().columns
            return max(20, min(80, width))
        except Exception:
            return 80

    def _get_terminal_height(self) -> int:
        """Get terminal height (default to 30)."""
        try:
            height = os.get_terminal_size().lines
            return max(10, height)
        except Exception:
            return 30
