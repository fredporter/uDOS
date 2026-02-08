"""
Pixel-to-Teletext Graphics Lookup Tables
========================================

Comprehensive lookup tables for converting pixel grids (2×3, 4×6, etc.) to
Unicode teletext characters with fallback chains.

Version: 1.0.0
Status: Locked for v1.0.7.0
"""

from enum import IntEnum
from typing import Dict, List, Tuple, Optional

# =============================================================================
# TELETEXT CHARACTER ENCODING
# =============================================================================

class TeletextMask(IntEnum):
    """6-bit teletext pixel positions (2×3 grid)."""
    TOP_LEFT = 1      # 0b000001
    TOP_RIGHT = 2     # 0b000010
    MID_LEFT = 4      # 0b000100
    MID_RIGHT = 8     # 0b001000
    BOT_LEFT = 16     # 0b010000
    BOT_RIGHT = 32    # 0b100000


# Unicode Teletext Block Characters (2×3 pixel grid)
# Mapping from 6-bit pattern (0-63) to teletext character
TELETEXT_CHARS = {
    0b000000: " ",   # Empty
    0b100000: "🬀",   # 1px: bottom-right
    0b010000: "🬁",   # 1px: bottom-left
    0b110000: "▄",   # 2px: bottom
    0b001000: "🬂",   # 1px: mid-right
    0b101000: "🬃",   # 2px: right (top+mid)
    0b011000: "🬄",   # 2px: bottom+mid-left
    0b111000: "🬅",   # 3px: bottom + mid column
    0b000100: "🬆",   # 1px: mid-left
    0b100100: "🬇",   # 2px: bottom-right + mid-left
    0b010100: "🬈",   # 2px: bottom + mid-left
    0b110100: "🬉",   # 3px: bottom + mid
    0b001100: "🬊",   # 2px: mid column
    0b101100: "🬋",   # 3px: right + bottom-left
    0b011100: "🬌",   # 3px: mid+bottom
    0b111100: "▀",   # 4px: top + mid + bottom (inv)
    0b000010: "🬍",   # 1px: top-right
    0b100010: "🬎",   # 2px: top-right + bottom-right
    0b010010: "🬏",   # 2px: top-right + bottom-left
    0b110010: "🬐",   # 3px: top-right + bottom
    0b001010: "🬑",   # 2px: top-right + mid-right
    0b101010: "█",   # 4px: right column (all)
    0b011010: "🬒",   # 3px: top-right + mid-right + bottom-left
    0b111010: "🬓",   # 4px: top-right + mid + bottom
    0b000110: "🬔",   # 2px: top-right + mid-left
    0b100110: "🬕",   # 3px: top-right + mid-left + bottom-right
    0b010110: "🬖",   # 3px: top-right + mid + bottom-left
    0b110110: "🬗",   # 4px: top-right + mid + bottom
    0b001110: "🬘",   # 3px: top-right + mid
    0b101110: "🬙",   # 4px: right + mid + bottom-left
    0b011110: "🬚",   # 4px: top-right + mid + bottom
    0b111110: "█",   # 5px: all except bottom-left
    0b000001: "🬛",   # 1px: top-left
    0b100001: "🬜",   # 2px: top-left + bottom-right
    0b010001: "🬝",   # 2px: top-left + bottom-left
    0b110001: "🬞",   # 3px: top-left + bottom
    0b001001: "🬟",   # 2px: top-left + mid-right
    0b101001: "🬠",   # 3px: top-left + right
    0b011001: "🬡",   # 3px: top-left + mid + bottom-left
    0b111001: "🬢",   # 4px: top-left + mid + bottom
    0b000101: "🬣",   # 2px: top-left + mid-left
    0b100101: "🬤",   # 3px: top-left + mid-left + bottom-right
    0b010101: "█",   # 3px: left column (all)
    0b110101: "🬥",   # 4px: top-left + mid + bottom
    0b001101: "🬦",   # 3px: top-left + mid
    0b101101: "🬧",   # 4px: top-left + right + bottom-left
    0b011101: "🬨",   # 4px: top-left + mid + bottom
    0b111101: "█",   # 5px: all except top-right
    0b000011: "🬩",   # 2px: top row
    0b100011: "🬪",   # 3px: top + bottom-right
    0b010011: "🬫",   # 3px: top + bottom
    0b110011: "▀",   # Full top row (inverse)
    0b001011: "🬬",   # 3px: top + mid-right
    0b101011: "🬭",   # 4px: top + right
    0b011011: "🬮",   # 4px: top + mid + bottom-left
    0b111011: "█",   # 5px: all except mid-left
    0b000111: "🬯",   # 3px: top + mid-left
    0b100111: "█",   # 4px: top + mid + bottom-right
    0b010111: "█",   # 4px: top + mid + bottom
    0b110111: "█",   # All except one pixel
    0b001111: "█",   # 4px: top + mid
    0b101111: "█",   # 5px: all except mid-left+bottom-left
    0b011111: "█",   # 5px: all except mid-right
    0b111111: "█",   # All 6 pixels (full block)
}


# =============================================================================
# ASCII_BLOCK CHARACTER ENCODING (FALLBACK 1)
# =============================================================================

class AsciiMask(IntEnum):
    """4-bit ascii pixel positions (2×2 grid)."""
    TOP_LEFT = 1     # 0b0001
    TOP_RIGHT = 2    # 0b0010
    BOT_LEFT = 4     # 0b0100
    BOT_RIGHT = 8    # 0b1000


ASCII_BLOCK_CHARS = {
    0b0000: " ",     # Empty
    0b0001: "▘",     # Top-left
    0b0010: "▝",     # Top-right
    0b0011: "▀",     # Top half
    0b0100: "▖",     # Bottom-left
    0b0101: "▌",     # Left half
    0b0110: "▞",     # Bottom-left + top-right
    0b0111: "▙",     # Top + bottom-left
    0b1000: "▗",     # Bottom-right
    0b1001: "▚",     # Top-left + bottom-right
    0b1010: "▐",     # Right half
    0b1011: "▜",     # Top-right + bottom
    0b1100: "▄",     # Bottom half
    0b1101: "▟",     # Bottom + top-left
    0b1110: "▛",     # Top + bottom-right
    0b1111: "█",     # Full
}


# =============================================================================
# SHADE CHARACTER ENCODING (FALLBACK 2)
# =============================================================================

# Density-based shading (1-4 levels of fill)
SHADE_CHARS = {
    0: " ",     # 0% (empty)
    1: "░",     # ~25% (sparse dots)
    2: "▒",     # ~50% (checkerboard)
    3: "▓",     # ~75% (dense dots)
    4: "█",     # 100% (full)
}


# =============================================================================
# ASCII FALLBACK (FALLBACK 3)
# =============================================================================

ASCII_FALLBACK = {
    0: " ",     # 0% (empty)
    1: ".",     # ~25%
    2: ":",     # ~50%
    3: "#",     # ~75%
    4: "@",     # 100%
}


# =============================================================================
# FALLBACK CHAIN SYSTEM
# =============================================================================

def teletext_to_ascii(teletext_mask: int) -> int:
    """
    Convert 6-bit teletext pattern (2×3) to 4-bit ascii pattern (2×2).
    Strategy: average each ascii's pixels.

    Teletext layout:        Ascii layout:
      0 1                    0 1
      2 3                    2 3
      4 5
    """
    # Map teletext pixel positions to ascii
    # TL: teletext 0 only
    # TR: teletext 1 only
    # BL: teletext 2,4 average
    # BR: teletext 3,5 average

    tl = (teletext_mask & 1) >> 0
    tr = (teletext_mask & 2) >> 1
    bl = ((teletext_mask & 4) >> 2) | ((teletext_mask & 16) >> 4)  # avg 2,4
    br = ((teletext_mask & 8) >> 3) | ((teletext_mask & 32) >> 5)  # avg 3,5

    return (bl & 1) | ((tr & 1) << 1) | ((bl & 1) << 2) | ((br & 1) << 3)


def ascii_to_shade(ascii_mask: int) -> int:
    """
    Convert 4-bit ascii pattern to 1-4 shade level.
    Count filled asciis: 0=empty, 4=full.
    """
    return bin(ascii_mask).count('1')


def teletext_to_shade(teletext_mask: int) -> int:
    """
    Convert 6-bit teletext pattern directly to shade level.
    Simpler: just count pixels.
    """
    return bin(teletext_mask).count('1')


def shade_to_ascii(shade_level: int) -> str:
    """Map shade level (0-4) to ASCII character."""
    return ASCII_FALLBACK.get(shade_level, " ")


# =============================================================================
# MAIN LOOKUP FUNCTIONS
# =============================================================================

def pixel_grid_to_teletext(grid_2x3: List[List[int]]) -> str:
    """
    Convert a 2×3 pixel grid to a teletext character.

    Args:
        grid_2x3: 2D array of 2×3 (rows=2, cols=3) with values 0 or 1

    Returns:
        Teletext Unicode character

    Example:
        grid = [
            [1, 1, 0],  # top row
            [1, 0, 1]   # mid row
        ]
        ch = pixel_grid_to_teletext(grid)  # Returns teletext character
    """
    if len(grid_2x3) != 2 or len(grid_2x3[0]) != 3:
        raise ValueError("Grid must be 2×3")

    # Convert 2D grid to 6-bit pattern
    pattern = 0
    for row in range(2):
        for col in range(3):
            if grid_2x3[row][col]:
                pattern |= (1 << (row * 3 + col))

    return TELETEXT_CHARS.get(pattern, " ")


def pixel_grid_to_fallback(grid_2x3: List[List[int]], style: str = "ascii") -> str:
    """
    Convert pixel grid to fallback character (non-teletext).

    Args:
        grid_2x3: 2D pixel grid (2×3)
        style: "ascii", "shade", or "ascii"

    Returns:
        Fallback character
    """
    # Count filled pixels as percentage
    total = sum(sum(row) for row in grid_2x3)
    density = total / 6  # 0.0 to 1.0

    if style == "shade":
        shade_level = round(density * 4)
        return SHADE_CHARS.get(shade_level, " ")

    elif style == "ascii":
        shade_level = round(density * 4)
        return ASCII_FALLBACK.get(shade_level, " ")

    elif style == "ascii":
        # Convert to 4-bit ascii pattern
        pattern = teletext_to_ascii(
            sum(1 << i for i, cell in enumerate([
                grid_2x3[0][0], grid_2x3[0][1:3],
                grid_2x3[1][0], grid_2x3[1][1:3]
            ]) if (any(cell) if isinstance(cell, (list, tuple)) else cell))
        )
        return ASCII_BLOCK_CHARS.get(pattern, " ")

    else:
        return " "


def get_fallback_chain(teletext_mask: int) -> Dict[str, str]:
    """
    Get all fallback options for a teletext pattern.
    Returns dict with keys: "teletext", "ascii", "shade", "ascii".
    """
    return {
        "teletext": TELETEXT_CHARS.get(teletext_mask, " "),
        "ascii": ASCII_BLOCK_CHARS.get(teletext_to_ascii(teletext_mask), " "),
        "shade": SHADE_CHARS.get(teletext_to_shade(teletext_mask), " "),
        "ascii": ASCII_FALLBACK.get(teletext_to_shade(teletext_mask), " "),
    }


def choose_character(teletext_mask: int, style: str) -> str:
    """
    Choose character based on style preference.
    Falls back if style is unsupported.

    Args:
        teletext_mask: 6-bit pattern (0-63)
        style: "teletext", "ascii", "shade", or "ascii"

    Returns:
        Best available character for the style
    """
    fallback = get_fallback_chain(teletext_mask)

    if style in fallback:
        ch = fallback[style]
        return ch if ch != " " else fallback.get("ascii", " ")

    # Fallback chain: teletext → ascii → shade → ascii
    for key in ["teletext", "ascii", "shade", "ascii"]:
        if fallback[key] != " ":
            return fallback[key]

    return " "


# =============================================================================
# COLOR PALETTE (16-color ANSI)
# =============================================================================

ANSI_COLORS = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "bright_black": 90,
    "bright_red": 91,
    "bright_green": 92,
    "bright_yellow": 93,
    "bright_blue": 94,
    "bright_magenta": 95,
    "bright_cyan": 96,
    "bright_white": 97,
}


def colorize(character: str, color: Optional[str] = None) -> str:
    """
    Wrap character with ANSI color code.

    Args:
        character: Single character
        color: Color name (from ANSI_COLORS) or None

    Returns:
        ANSI-wrapped character or plain character
    """
    if not color or color not in ANSI_COLORS:
        return character

    code = ANSI_COLORS[color]
    return f"\x1b[{code}m{character}\x1b[0m"


# =============================================================================
# PIXEL ARRAY TO STRING CONVERSION
# =============================================================================

def pixels_to_string(
    pixel_array: List[List[int]],
    tile_width: int = 16,
    tile_height: int = 24,
    style: str = "teletext"
) -> str:
    """
    Convert a pixel array (16×24 or any size) to a rendered string.

    Args:
        pixel_array: 2D list of pixel values (0 or 1)
        tile_width: Tile width (default 16)
        tile_height: Tile height (default 24)
        style: "teletext", "ascii", "shade", "ascii"

    Returns:
        Rendered string (newline-separated rows)

    Example:
        pixels = [[0]*16 for _ in range(24)]
        pixels[0][0] = 1  # Set one pixel
        output = pixels_to_string(pixels, style="teletext")
        print(output)
    """
    if not pixel_array or not pixel_array[0]:
        return ""

    rows = []

    # Process in 2×3 chunks (teletext size)
    for y in range(0, len(pixel_array), 2):
        row_chars = []
        for x in range(0, len(pixel_array[0]), 3):
            # Extract 2×3 grid
            grid = []
            for dy in range(2):
                grid_row = []
                for dx in range(3):
                    py, px = y + dy, x + dx
                    if py < len(pixel_array) and px < len(pixel_array[0]):
                        grid_row.append(pixel_array[py][px])
                    else:
                        grid_row.append(0)
                grid.append(grid_row)

            # Get teletext character
            try:
                ch = pixel_grid_to_teletext(grid) if style == "teletext" else pixel_grid_to_fallback(grid, style)
                row_chars.append(ch)
            except Exception:
                row_chars.append(" ")

        rows.append("".join(row_chars))

    return "\n".join(rows)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("🎨 Pixel-to-Teletext Lookup Tables v1.0.0")
    print("=" * 60)

    # Test 1: Simple teletext patterns
    print("\n📊 Teletext Character Samples:")
    patterns = [
        (0b000000, "Empty"),
        (0b111111, "Full"),
        (0b110000, "Bottom half"),
        (0b001100, "Mid column"),
        (0b010101, "Left column"),
    ]
    for pattern, desc in patterns:
        ch = TELETEXT_CHARS.get(pattern, "?")
        print(f"  {desc:20s} → {ch}")

    # Test 2: Fallback chain
    print("\n🔗 Fallback Chain (pattern 0b010101):")
    chain = get_fallback_chain(0b010101)
    for style, ch in chain.items():
        print(f"  {style:12s} → {ch}")

    # Test 3: Pixel grid conversion
    print("\n🖼️  Pixel Grid → Teletext:")
    grid = [
        [1, 1, 0],
        [1, 0, 1]
    ]
    ch = pixel_grid_to_teletext(grid)
    print(f"  Grid pattern → {ch}")

    # Test 4: Full tile rendering
    print("\n🎯 Full 16×24 Tile Rendering (teletext):")
    pixels = [[0] * 16 for _ in range(24)]
    # Draw a circle
    for y in range(24):
        for x in range(16):
            dist = ((x - 8) ** 2 + (y - 12) ** 2) ** 0.5
            if dist < 6:
                pixels[y][x] = 1

    output = pixels_to_string(pixels, style="teletext")
    print(output)

    print("\n✅ All tests completed.")
