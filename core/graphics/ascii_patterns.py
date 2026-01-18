"""
ASCII Pattern Generator

Generates ASCII art patterns for TUI display:
- Geometric patterns (chevrons, scanlines, grids)
- Density ramps (. : # @ %)
- Animation frames
- Pattern tiling
"""

from typing import List, Tuple, Callable
import math


class ASCIIPatternGenerator:
    """Generate ASCII patterns for terminal display"""

    # Character sets by density
    DENSITY_ASCII = [" ", ".", ":", "-", "=", "#", "@", "%", "X", "W", "M", "B"]
    DENSITY_UNICODE = [" ", "░", "▒", "▓", "█"]

    # Geometric primitives
    SLASH = "/"
    BACKSLASH = "\\"
    HORIZONTAL = "-"
    VERTICAL = "|"
    PLUS = "+"
    HASH = "#"

    def __init__(self, width: int = 80, height: int = 30, unicode_mode: bool = True):
        self.width = width
        self.height = height
        self.unicode_mode = unicode_mode
        self.density_chars = (
            self.DENSITY_UNICODE if unicode_mode else self.DENSITY_ASCII
        )

    def generate_chevrons(self, phase: int = 0) -> List[str]:
        """Generate chevron pattern (zigzag lines)"""
        pattern = (self.SLASH * 7 + " " * 8 + self.BACKSLASH * 7 + " " * 8) * 3
        lines = []
        for y in range(self.height):
            offset = (phase + y) % len(pattern)
            line = (pattern[offset:] + pattern[:offset])[: self.width]
            lines.append(line)
        return lines

    def generate_scanlines(self, phase: int = 0, frequency: int = 4) -> List[str]:
        """Generate horizontal scanline pattern"""
        lines = []
        for y in range(self.height):
            intensity = (y + phase) % frequency
            char_idx = int((intensity / frequency) * (len(self.density_chars) - 1))
            char = self.density_chars[char_idx]
            lines.append(char * self.width)
        return lines

    def generate_density_ramp(self, vertical: bool = True, phase: int = 0) -> List[str]:
        """Generate density gradient pattern"""
        lines = []
        num_chars = len(self.density_chars)

        if vertical:
            for y in range(self.height):
                idx = ((y + phase) % self.height) * num_chars // self.height
                char = self.density_chars[idx]
                lines.append(char * self.width)
        else:
            line = []
            for x in range(self.width):
                idx = ((x + phase) % self.width) * num_chars // self.width
                line.append(self.density_chars[idx])
            lines = ["".join(line)] * self.height

        return lines

    def generate_grid(self, cell_width: int = 8, cell_height: int = 4) -> List[str]:
        """Generate grid pattern with boxes"""
        lines = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                if y % cell_height == 0 or x % cell_width == 0:
                    line.append(
                        self.PLUS
                        if (y % cell_height == 0 and x % cell_width == 0)
                        else (
                            self.HORIZONTAL if y % cell_height == 0 else self.VERTICAL
                        )
                    )
                else:
                    line.append(" ")
            lines.append("".join(line))
        return lines

    def generate_wave(
        self, phase: float = 0.0, frequency: float = 0.1, amplitude: float = 5.0
    ) -> List[str]:
        """Generate sine wave pattern"""
        lines = [" " * self.width for _ in range(self.height)]
        line_list = [list(line) for line in lines]

        for x in range(self.width):
            y_pos = int(self.height / 2 + amplitude * math.sin(frequency * x + phase))
            y_pos = max(0, min(self.height - 1, y_pos))
            line_list[y_pos][x] = self.HASH

        return ["".join(line) for line in line_list]

    def generate_mosaic(
        self, tile_chars: str = None, tile_size: int = 2, phase: int = 0
    ) -> List[str]:
        """Generate random mosaic pattern"""
        if tile_chars is None:
            tile_chars = "▀▄█▌▐▖▗▘▙▚▛▜▝▞▟" if self.unicode_mode else "#+=*@%&"

        lines = []
        import random

        random.seed(phase)  # Deterministic based on phase

        for y in range(self.height):
            line = []
            for x in range(0, self.width, tile_size):
                char = random.choice(tile_chars)
                line.append(char * min(tile_size, self.width - x))
            lines.append("".join(line))

        return lines

    def generate_checker(self, cell_size: int = 4, phase: int = 0) -> List[str]:
        """Generate checkerboard pattern"""
        lines = []
        char_on = "█" if self.unicode_mode else "#"
        char_off = " "

        for y in range(self.height):
            line = []
            offset = (phase % 2) if (y // cell_size) % 2 == 0 else ((phase + 1) % 2)
            for x in range(self.width):
                is_on = ((x // cell_size) + offset) % 2 == 0
                line.append(char_on if is_on else char_off)
            lines.append("".join(line))

        return lines

    def tile_pattern(
        self, pattern: List[str], tile_width: int = None, tile_height: int = None
    ) -> List[str]:
        """Tile a small pattern to fill the viewport"""
        if tile_width is None:
            tile_width = len(pattern[0]) if pattern else self.width
        if tile_height is None:
            tile_height = len(pattern)

        lines = []
        for y in range(self.height):
            source_y = y % tile_height
            source_line = (
                pattern[source_y] if source_y < len(pattern) else " " * tile_width
            )

            line = []
            for x in range(0, self.width, tile_width):
                chunk = source_line[: min(tile_width, self.width - x)]
                line.append(chunk)

            lines.append("".join(line))

        return lines


if __name__ == "__main__":
    # Demo patterns
    gen = ASCIIPatternGenerator(80, 24, unicode_mode=True)

    print("=== Chevrons ===")
    for line in gen.generate_chevrons(phase=0)[:5]:
        print(line)

    print("\n=== Scanlines ===")
    for line in gen.generate_scanlines(phase=0)[:5]:
        print(line)

    print("\n=== Grid ===")
    for line in gen.generate_grid(cell_width=10, cell_height=4)[:8]:
        print(line)

    print("\n=== Wave ===")
    for line in gen.generate_wave(phase=0.0, frequency=0.3, amplitude=4)[:8]:
        print(line)
