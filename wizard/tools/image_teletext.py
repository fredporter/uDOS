"""
Image to Teletext Converter
============================

Converts images to Teletext-compatible character graphics
for display in uDOS terminal UI.

Modes:
  - Block graphics (2x3 sixel-style characters)
  - ASCII art (character density mapping)
  - Dither patterns (Floyd-Steinberg)

Output formats:
  - Raw character grid
  - ANSI colored output
  - Teletext page format

Note: Requires Pillow for image processing.
"""

import math
from typing import Optional, List, Tuple
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

from wizard.services.logging_api import get_logger

logger = get_logger("image-teletext")

# Check for Pillow
try:
    from PIL import Image

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class ConversionMode(Enum):
    """Image to text conversion modes."""

    BLOCK = "block"  # Unicode block characters (best quality)
    ASCII = "ascii"  # Traditional ASCII art
    TELETEXT = "teletext"  # BBC Micro teletext blocks


@dataclass
class TeletextImage:
    """Result of image conversion."""

    success: bool
    width: int
    height: int
    content: str
    mode: ConversionMode
    error: Optional[str] = None


# Character sets for different modes
ASCII_CHARS = " .:-=+*#%@"
BLOCK_CHARS = " ░▒▓█"

# Teletext 2x3 block characters (sixel-style)
# Each character represents 6 pixels in a 2x3 grid
# Using Unicode Block Elements
TELETEXT_BLOCKS = {
    0b000000: " ",
    0b000001: "▗",
    0b000010: "▖",
    0b000011: "▄",
    0b000100: "▝",
    0b000101: "▐",
    0b000110: "▞",
    0b000111: "▟",
    0b001000: "▘",
    0b001001: "▚",
    0b001010: "▌",
    0b001011: "▙",
    0b001100: "▀",
    0b001101: "▜",
    0b001110: "▛",
    0b001111: "█",
}


class ImageToTeletext:
    """
    Converts images to text-based representations.
    """

    # Default dimensions (Teletext standard: 40x25)
    DEFAULT_WIDTH = 40
    DEFAULT_HEIGHT = 25

    # Minimum dimensions
    MIN_WIDTH = 10
    MIN_HEIGHT = 5

    # Maximum dimensions (prevent huge output)
    MAX_WIDTH = 200
    MAX_HEIGHT = 100

    def __init__(
        self,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        mode: ConversionMode = ConversionMode.BLOCK,
    ):
        """
        Initialize converter.

        Args:
            width: Output width in characters
            height: Output height in characters
            mode: Conversion mode
        """
        self.width = max(self.MIN_WIDTH, min(self.MAX_WIDTH, width))
        self.height = max(self.MIN_HEIGHT, min(self.MAX_HEIGHT, height))
        self.mode = mode

    def convert_file(self, path: str) -> TeletextImage:
        """
        Convert an image file to text.

        Args:
            path: Path to image file

        Returns:
            TeletextImage result
        """
        if not PILLOW_AVAILABLE:
            return TeletextImage(
                success=False,
                width=0,
                height=0,
                content="",
                mode=self.mode,
                error="Pillow not installed. Run: pip install Pillow",
            )

        image_path = Path(path)
        if not image_path.exists():
            return TeletextImage(
                success=False,
                width=0,
                height=0,
                content="",
                mode=self.mode,
                error=f"File not found: {path}",
            )

        try:
            img = Image.open(image_path)
            return self._convert_image(img)
        except Exception as e:
            return TeletextImage(
                success=False,
                width=0,
                height=0,
                content="",
                mode=self.mode,
                error=f"Failed to open image: {str(e)}",
            )

    def convert_bytes(self, data: bytes) -> TeletextImage:
        """
        Convert image bytes to text.

        Args:
            data: Raw image bytes

        Returns:
            TeletextImage result
        """
        if not PILLOW_AVAILABLE:
            return TeletextImage(
                success=False,
                width=0,
                height=0,
                content="",
                mode=self.mode,
                error="Pillow not installed. Run: pip install Pillow",
            )

        try:
            from io import BytesIO

            img = Image.open(BytesIO(data))
            return self._convert_image(img)
        except Exception as e:
            return TeletextImage(
                success=False,
                width=0,
                height=0,
                content="",
                mode=self.mode,
                error=f"Failed to parse image: {str(e)}",
            )

    def _convert_image(self, img: "Image.Image") -> TeletextImage:
        """Internal image conversion."""
        # Convert to grayscale
        img = img.convert("L")

        # Calculate aspect ratio correction
        # Characters are typically ~2x taller than wide
        aspect_ratio = img.width / img.height

        if self.mode == ConversionMode.TELETEXT:
            # Teletext uses 2x3 pixel blocks per character
            char_width = self.width * 2
            char_height = self.height * 3
        else:
            # Standard characters use ~2:1 aspect
            char_width = self.width
            char_height = int(self.height / 2)  # Correct for tall chars

        # Resize image
        img = img.resize((char_width, char_height), Image.Resampling.LANCZOS)

        # Convert based on mode
        if self.mode == ConversionMode.TELETEXT:
            content = self._to_teletext_blocks(img)
        elif self.mode == ConversionMode.BLOCK:
            content = self._to_block_chars(img)
        else:
            content = self._to_ascii(img)

        return TeletextImage(
            success=True,
            width=self.width,
            height=self.height,
            content=content,
            mode=self.mode,
        )

    def _to_ascii(self, img: "Image.Image") -> str:
        """Convert to ASCII art using character density."""
        pixels = list(img.getdata())
        width = img.width

        lines = []
        for y in range(img.height):
            line = ""
            for x in range(width):
                pixel = pixels[y * width + x]
                # Map 0-255 to character set
                char_index = int(pixel / 255 * (len(ASCII_CHARS) - 1))
                line += ASCII_CHARS[char_index]
            lines.append(line)

        return "\n".join(lines)

    def _to_block_chars(self, img: "Image.Image") -> str:
        """Convert using Unicode block characters."""
        pixels = list(img.getdata())
        width = img.width

        lines = []
        for y in range(img.height):
            line = ""
            for x in range(width):
                pixel = pixels[y * width + x]
                # Map 0-255 to block characters
                char_index = int(pixel / 255 * (len(BLOCK_CHARS) - 1))
                line += BLOCK_CHARS[char_index]
            lines.append(line)

        return "\n".join(lines)

    def _to_teletext_blocks(self, img: "Image.Image") -> str:
        """
        Convert using teletext 2x3 sixel-style blocks.

        Each output character represents a 2x3 pixel grid.
        """
        pixels = list(img.getdata())
        width = img.width
        height = img.height

        # Threshold for black/white
        threshold = 128

        lines = []
        for y in range(0, height, 3):
            line = ""
            for x in range(0, width, 2):
                # Build 6-bit pattern from 2x3 block
                pattern = 0

                # Top row (bits 3, 2)
                if y < height and x < width:
                    if pixels[y * width + x] > threshold:
                        pattern |= 0b001000
                if y < height and x + 1 < width:
                    if pixels[y * width + x + 1] > threshold:
                        pattern |= 0b000100

                # Middle row (bits 1, 0 of upper nibble becomes bits 1, 0)
                if y + 1 < height and x < width:
                    if pixels[(y + 1) * width + x] > threshold:
                        pattern |= 0b000010
                if y + 1 < height and x + 1 < width:
                    if pixels[(y + 1) * width + x + 1] > threshold:
                        pattern |= 0b000001

                # We only have 4-bit block chars, so simplify
                # Map to available Unicode block elements
                block_char = self._get_block_char(pattern)
                line += block_char

            lines.append(line)

        return "\n".join(lines)

    def _get_block_char(self, pattern: int) -> str:
        """Map 4-bit pattern to Unicode block character."""
        # Simplified 4-bit to block char mapping
        # Using quadrant characters
        QUAD_BLOCKS = {
            0b0000: " ",  # Empty
            0b0001: "▗",  # Bottom right
            0b0010: "▖",  # Bottom left
            0b0011: "▄",  # Bottom half
            0b0100: "▝",  # Top right
            0b0101: "▐",  # Right half
            0b0110: "▞",  # Diagonal (top right, bottom left)
            0b0111: "▟",  # All except top left
            0b1000: "▘",  # Top left
            0b1001: "▚",  # Diagonal (top left, bottom right)
            0b1010: "▌",  # Left half
            0b1011: "▙",  # All except top right
            0b1100: "▀",  # Top half
            0b1101: "▜",  # All except bottom left
            0b1110: "▛",  # All except bottom right
            0b1111: "█",  # Full block
        }

        # Reduce 6-bit to 4-bit by ignoring bottom row
        reduced = (pattern >> 2) & 0b1111
        return QUAD_BLOCKS.get(reduced, "█")


def convert_image(
    path: str, width: int = 40, height: int = 25, mode: str = "block"
) -> TeletextImage:
    """
    Convenience function to convert an image file.

    Args:
        path: Path to image file
        width: Output width in characters
        height: Output height in characters
        mode: Conversion mode ('block', 'ascii', 'teletext')

    Returns:
        TeletextImage result
    """
    conversion_mode = ConversionMode(mode.lower())
    converter = ImageToTeletext(width, height, conversion_mode)
    return converter.convert_file(path)


def image_to_page(path: str, title: str = "") -> str:
    """
    Convert image to a full Teletext page format.

    Args:
        path: Path to image file
        title: Page title

    Returns:
        Formatted teletext page string
    """
    result = convert_image(path, 38, 20, "block")

    if not result.success:
        return f"ERROR: {result.error}"

    lines = []
    lines.append("┌" + "─" * 38 + "┐")

    if title:
        title_text = title[:36].center(38)
        lines.append(f"│{title_text}│")
        lines.append("├" + "─" * 38 + "┤")

    for line in result.content.split("\n"):
        padded = line[:38].ljust(38)
        lines.append(f"│{padded}│")

    # Pad to 25 rows
    while len(lines) < 24:
        lines.append("│" + " " * 38 + "│")

    lines.append("└" + "─" * 38 + "┘")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Image to Teletext Converter")
    print("=" * 40)
    print(f"Pillow available: {PILLOW_AVAILABLE}")
    print()
    print("Modes:")
    for mode in ConversionMode:
        print(f"  {mode.value}: {mode.name}")
