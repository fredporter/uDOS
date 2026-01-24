"""
Pattern Generator Service

80-column ANSI pattern generators for terminal displays.
Includes C64-style loaders, raster bars, scanlines, and mosaic patterns.

Used for:
- TUI startup displays
- PATTERN command (interactive cycling)
- Dev mode visual feedback

Reference: Teletext/C64-inspired retro terminal aesthetics
"""

import math
import random
import sys
import time
from typing import Optional, Callable, List

# ANSI Control Sequences
ESC = "\x1b"
RST = f"{ESC}[0m"
HIDE_CURSOR = f"{ESC}[?25l"
SHOW_CURSOR = f"{ESC}[?25h"

# Foreground Colors (16-colour ANSI)
FG = {
    "blk": f"{ESC}[30m",
    "red": f"{ESC}[31m",
    "grn": f"{ESC}[32m",
    "ylw": f"{ESC}[33m",
    "blu": f"{ESC}[34m",
    "mag": f"{ESC}[35m",
    "cyn": f"{ESC}[36m",
    "wht": f"{ESC}[37m",
    "bblk": f"{ESC}[90m",
    "bred": f"{ESC}[91m",
    "bgrn": f"{ESC}[92m",
    "bylw": f"{ESC}[93m",
    "bblu": f"{ESC}[94m",
    "bmag": f"{ESC}[95m",
    "bcyn": f"{ESC}[96m",
    "bwht": f"{ESC}[97m",
}

# Background Colors (16-colour ANSI)
BG = {
    "blk": f"{ESC}[40m",
    "red": f"{ESC}[41m",
    "grn": f"{ESC}[42m",
    "ylw": f"{ESC}[43m",
    "blu": f"{ESC}[44m",
    "mag": f"{ESC}[45m",
    "cyn": f"{ESC}[46m",
    "wht": f"{ESC}[47m",
    "bblk": f"{ESC}[100m",
    "bred": f"{ESC}[101m",
    "bgrn": f"{ESC}[102m",
    "bylw": f"{ESC}[103m",
    "bblu": f"{ESC}[104m",
    "bmag": f"{ESC}[105m",
    "bcyn": f"{ESC}[106m",
    "bwht": f"{ESC}[107m",
}

# Unicode block characters
UNICODE_FULL = "█"
UNICODE_HALF = "▀"
ASCII_FULL = "#"

# C64-inspired cycling palette
C64_CYCLE_BG = [
    "bblu",
    "blu",
    "bblk",
    "blk",
    "bgrn",
    "grn",
    "bylw",
    "ylw",
    "bred",
    "red",
    "bmag",
    "mag",
    "bcyn",
    "cyn",
    "bwht",
    "wht",
]


class PatternGenerator:
    """Generator for ANSI terminal patterns"""

    def __init__(self, width: int = 80, height: int = 30, ascii_only: bool = False):
        """
        Initialize pattern generator

        Args:
            width: Terminal width (default 80)
            height: Pattern height (default 30 lines)
            ascii_only: Force ASCII-only mode (no Unicode blocks)
        """
        self.width = max(20, min(80, width))
        self.height = max(10, height)
        self.ascii_only = ascii_only
        self.phase = 0
        self.stop_flag = False

    def generate_c64(self, frames: int = 60, delay: float = 0.03) -> List[str]:
        """
        C64-style loading bar with colour cycling and transfer head animation

        Args:
            frames: Number of frames to generate
            delay: Delay between frames (unused in static generation)

        Returns:
            List of output lines (no trailing newlines)
        """
        block = ASCII_FULL if self.ascii_only else UNICODE_FULL
        output = []

        bar_rows = [(0, 8), (2, 8), (4, 8), (6, 8)]
        title = "  *** COMMODORE 64 ***   LOADING  "
        title = (title + " " * self.width)[: self.width]

        for phase in range(frames):
            if phase % 12 == 0:
                output.append(BG["bblu"] + FG["bwht"] + title + RST)

            head = (phase * 2) % self.width

            for off, _ in bar_rows:
                line = []
                for x in range(self.width):
                    band = (x // 4 + (phase + off)) % len(C64_CYCLE_BG)
                    bg = C64_CYCLE_BG[band]

                    dist = (x - head) % self.width
                    is_head = dist < 6
                    is_tail = 6 <= dist < 10

                    fg = "blk" if bg not in ("blk", "bblk") else "bwht"
                    if is_head:
                        bg = "bwht"
                        fg = "blk"
                    elif is_tail:
                        bg = "bylw"
                        fg = "blk"

                    line.append(BG[bg] + FG[fg] + block + RST)

                output.append("".join(line))

        return output

    def generate_chevrons(self, frames: int = 30, delay: float = 0.03) -> List[str]:
        """
        Diagonal chevron scrolling pattern

        Args:
            frames: Number of frames
            delay: Unused

        Returns:
            List of output lines
        """
        output = []
        a = ("/" * 7) + (" " * 8)
        b = ("\\" * 7) + (" " * 8)
        blocks = (a + b) * 4
        L = len(blocks)

        for phase in range(frames):
            line = (blocks[phase : phase + self.width] + blocks[:phase])[: self.width]
            output.append(line)

        return output

    def generate_scanlines(self, frames: int = 30, delay: float = 0.03) -> List[str]:
        """
        Horizontal scanline pattern with gradient

        Args:
            frames: Number of frames
            delay: Unused

        Returns:
            List of output lines
        """
        output = []
        chars = " .:-=+*#%@" if self.ascii_only else "░▒▓█"
        denom = max(1, len(chars) - 1)

        for phase in range(frames):
            line = []
            for x in range(self.width):
                v = (x * 3 + phase) % (denom * 6)
                idx = min(denom, v // 6)
                line.append(chars[idx])
            output.append("".join(line))

        return output

    def generate_raster_bars(self, frames: int = 60, delay: float = 0.03) -> List[str]:
        """
        Demoscene-style rolling raster bars with sinusoidal movement

        Args:
            frames: Number of frames
            delay: Unused

        Returns:
            List of output lines
        """
        output = []
        block = "=" if self.ascii_only else "▀"
        palette = [
            "bblu",
            "blu",
            "bcyn",
            "cyn",
            "bgrn",
            "grn",
            "bylw",
            "ylw",
            "bred",
            "red",
            "bmag",
            "mag",
        ]

        for phase_int in range(frames):
            phase = phase_int * 0.12
            roll = int((math.sin(phase) * 0.5 + 0.5) * (len(palette) - 1))

            line = []
            for x in range(self.width):
                stripe = (x // 2 + roll + int(phase * 6)) % len(palette)
                bg = palette[stripe]
                fg = "bwht" if ((x + int(phase * 10)) % 16 == 0) else "blk"
                line.append(BG[bg] + FG[fg] + block + RST)

            output.append("".join(line))

        return output

    def generate_progress_loader(
        self, frames: int = 60, delay: float = 0.03
    ) -> List[str]:
        """
        Chunky progress bar with cycling fill and bouncing head

        Args:
            frames: Number of frames
            delay: Unused

        Returns:
            List of output lines
        """
        output = []
        label = "LOADING"
        inner = max(10, self.width - (len(label) + 6))

        left = "[" if self.ascii_only else "▕"
        right = "]" if self.ascii_only else "▏"
        empty_ch = "." if self.ascii_only else " "
        fill_ch = "#" if self.ascii_only else "█"

        ramp = [
            "bblu",
            "blu",
            "bcyn",
            "cyn",
            "bgrn",
            "grn",
            "bylw",
            "ylw",
            "bred",
            "red",
            "bmag",
            "mag",
        ]

        pos = 0
        dirn = 1

        for phase in range(frames):
            fill = (phase // 2) % (inner + 1)

            pos += dirn
            if pos >= inner - 1:
                dirn = -1
            elif pos <= 0:
                dirn = 1

            bar = []
            for i in range(inner):
                if i < fill:
                    bg = ramp[(i + phase) % len(ramp)]
                    if abs(i - pos) <= 1:
                        bar.append(BG["bwht"] + FG["blk"] + fill_ch + RST)
                    else:
                        bar.append(BG[bg] + FG["blk"] + fill_ch + RST)
                else:
                    bar.append(FG["bblk"] + empty_ch + RST)

            pct = int((fill / inner) * 100)
            line = f" {label} {left}" + "".join(bar) + f"{right} {pct:3d}%"
            output.append((line + " " * self.width)[: self.width])

        return output

    def generate_mosaic(self, frames: int = 30, delay: float = 0.03) -> List[str]:
        """
        Colourful mosaic pattern with random character tiles

        Args:
            frames: Number of frames
            delay: Unused

        Returns:
            List of output lines
        """
        output = []
        tiles = (
            ["#", "+", "*", "=", "@", "%", "&"]
            if self.ascii_only
            else [
                "▀",
                "▄",
                "█",
                "▌",
                "▐",
                "▖",
                "▗",
                "▘",
                "▙",
                "▚",
                "▛",
                "▜",
                "▝",
                "▞",
                "▟",
            ]
        )
        cols = ["red", "grn", "ylw", "blu", "mag", "cyn"]

        for phase in range(frames):
            line = []
            for x in range(self.width):
                r = (x // 4 + phase) % 19
                ch = tiles[(r * r + x + phase) % len(tiles)]
                c = cols[(x // 10 + (phase // 2)) % len(cols)]
                line.append(FG[c] + ch + RST)
            output.append("".join(line))

        return output

    def get_available_patterns(self) -> List[str]:
        """Get list of available pattern names"""
        return ["c64", "chevrons", "scanlines", "raster", "progress", "mosaic"]

    def render_pattern(self, pattern_name: str, frames: int = 60) -> List[str]:
        """
        Render named pattern

        Args:
            pattern_name: Name of pattern (c64, chevrons, scanlines, raster, progress, mosaic)
            frames: Number of frames to render

        Returns:
            List of output lines
        """
        pattern_map = {
            "c64": self.generate_c64,
            "chevrons": self.generate_chevrons,
            "scanlines": self.generate_scanlines,
            "raster": self.generate_raster_bars,
            "progress": self.generate_progress_loader,
            "mosaic": self.generate_mosaic,
        }

        if pattern_name not in pattern_map:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        return pattern_map[pattern_name](frames)
