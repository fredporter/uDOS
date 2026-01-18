"""
Block Graphics Renderer

Handles teletext/sextant block graphics (2×3 mosaic patterns):
- Encode/decode sextant blocks (U+1FB00-U+1FB3B)
- Render to ASCII fallback (quadrant → shades → ASCII)
- Pattern compilation
- Tile rendering
"""

from typing import List, Tuple, Optional
import struct


class TeletextEncoder:
    """Encode/decode 2×3 sextant blocks"""

    # Unicode sextant block range
    SEXTANT_BASE = 0x1FB00  # U+1FB00
    SEXTANT_COUNT = 64  # 2^6 combinations

    # Fallback characters (when sextant not available)
    FALLBACK_QUADRANT = {
        0b000000: " ",  # empty
        0b111111: "█",  # full
        0b110000: "▘",  # top-left
        0b001100: "▝",  # top-right
        0b000011: "▗",  # bottom-right
        0b110011: "▟",  # three corners except top-right
        # ... additional mappings
    }

    FALLBACK_SHADES = [" ", "░", "▒", "▓", "█"]
    FALLBACK_ASCII = [" ", ".", ":", "#", "@"]

    @staticmethod
    def mask_to_sextant(mask: int) -> str:
        """Convert 6-bit mask to sextant character

        Mask format (2×3 grid):
        b0 b1  (top row)
        b2 b3  (middle row)
        b4 b5  (bottom row)
        """
        if mask < 0 or mask >= TeletextEncoder.SEXTANT_COUNT:
            raise ValueError(f"Invalid mask: {mask} (must be 0-63)")

        codepoint = TeletextEncoder.SEXTANT_BASE + mask
        return chr(codepoint)

    @staticmethod
    def sextant_to_mask(char: str) -> Optional[int]:
        """Convert sextant character to 6-bit mask"""
        if len(char) != 1:
            return None

        codepoint = ord(char)
        if (
            codepoint < TeletextEncoder.SEXTANT_BASE
            or codepoint >= TeletextEncoder.SEXTANT_BASE + TeletextEncoder.SEXTANT_COUNT
        ):
            return None

        return codepoint - TeletextEncoder.SEXTANT_BASE

    @staticmethod
    def mask_to_quadrant(mask: int) -> str:
        """Fallback to quadrant blocks"""
        return TeletextEncoder.FALLBACK_QUADRANT.get(mask, "█")

    @staticmethod
    def mask_to_shade(mask: int) -> str:
        """Fallback to shade characters based on density"""
        bit_count = bin(mask).count("1")
        density = bit_count / 6.0
        idx = int(density * (len(TeletextEncoder.FALLBACK_SHADES) - 1))
        return TeletextEncoder.FALLBACK_SHADES[idx]

    @staticmethod
    def mask_to_ascii(mask: int) -> str:
        """Fallback to ASCII characters based on density"""
        bit_count = bin(mask).count("1")
        density = bit_count / 6.0
        idx = int(density * (len(TeletextEncoder.FALLBACK_ASCII) - 1))
        return TeletextEncoder.FALLBACK_ASCII[idx]

    @staticmethod
    def pixel_grid_to_mask(grid: List[List[bool]]) -> int:
        """Convert 2×3 boolean grid to 6-bit mask

        grid[row][col] where row ∈ [0,1,2], col ∈ [0,1]
        """
        if len(grid) != 3:
            raise ValueError("Grid must have 3 rows")
        if any(len(row) != 2 for row in grid):
            raise ValueError("Grid rows must have 2 columns")

        mask = 0
        bit_positions = [
            (0, 0, 0),
            (0, 1, 1),
            (1, 0, 2),
            (1, 1, 3),
            (2, 0, 4),
            (2, 1, 5),
        ]

        for row, col, bit in bit_positions:
            if grid[row][col]:
                mask |= 1 << bit

        return mask


class BlockGraphicsRenderer:
    """Render block graphics patterns"""

    def __init__(self, fallback_mode: str = "sextant"):
        """
        fallback_mode: 'sextant' | 'quadrant' | 'shade' | 'ascii'
        """
        self.fallback_mode = fallback_mode
        self.encoder = TeletextEncoder()

    def render_mask(self, mask: int) -> str:
        """Render a single sextant mask with fallback"""
        if self.fallback_mode == "sextant":
            return self.encoder.mask_to_sextant(mask)
        elif self.fallback_mode == "quadrant":
            return self.encoder.mask_to_quadrant(mask)
        elif self.fallback_mode == "shade":
            return self.encoder.mask_to_shade(mask)
        elif self.fallback_mode == "ascii":
            return self.encoder.mask_to_ascii(mask)
        else:
            raise ValueError(f"Invalid fallback mode: {self.fallback_mode}")

    def render_pattern(
        self, pattern: List[List[int]], width: int, height: int
    ) -> List[str]:
        """Render a pattern grid of sextant masks

        pattern[y][x] = 6-bit mask
        Output is width×height characters
        """
        lines = []
        for y in range(height):
            line = []
            for x in range(width):
                mask = pattern[y][x] if y < len(pattern) and x < len(pattern[y]) else 0
                line.append(self.render_mask(mask))
            lines.append("".join(line))
        return lines

    def create_test_pattern(self) -> List[List[int]]:
        """Generate a test pattern showing all sextant combinations"""
        pattern = []
        for row in range(8):
            line = []
            for col in range(8):
                mask = row * 8 + col
                if mask < 64:
                    line.append(mask)
                else:
                    line.append(0)
            pattern.append(line)
        return pattern

    def create_gradient_pattern(
        self, width: int, height: int, horizontal: bool = True
    ) -> List[List[int]]:
        """Create a density gradient pattern"""
        pattern = []
        for y in range(height):
            line = []
            for x in range(width):
                if horizontal:
                    density = x / max(1, width - 1)
                else:
                    density = y / max(1, height - 1)

                mask = int(density * 63)
                line.append(mask)
            pattern.append(line)
        return pattern

    def create_checkerboard_pattern(
        self, width: int, height: int, cell_size: int = 1
    ) -> List[List[int]]:
        """Create checkerboard pattern with sextant blocks"""
        pattern = []
        for y in range(height):
            line = []
            for x in range(width):
                is_on = ((x // cell_size) + (y // cell_size)) % 2 == 0
                mask = 0b111111 if is_on else 0b000000
                line.append(mask)
            pattern.append(line)
        return pattern


if __name__ == "__main__":
    # Demo rendering
    print("=== Sextant Encoding Demo ===\n")

    encoder = TeletextEncoder()

    # Show first 16 sextant characters
    print("First 16 sextant blocks:")
    for i in range(16):
        char = encoder.mask_to_sextant(i)
        print(f"  Mask {i:02d} (0b{i:06b}): {char}")

    print("\n=== Fallback Rendering ===\n")

    for mode in ["sextant", "quadrant", "shade", "ascii"]:
        print(f"{mode.upper()} mode:")
        renderer = BlockGraphicsRenderer(fallback_mode=mode)

        # Gradient pattern
        pattern = renderer.create_gradient_pattern(16, 3, horizontal=True)
        lines = renderer.render_pattern(pattern, 16, 3)
        for line in lines:
            print(f"  {line}")
        print()
