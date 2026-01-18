"""
Teletext/ANSI pattern generator service for Wizard.

This module exposes lightweight, deterministic frame generators for
teletext-style effects (chevrons, scanlines, mosaic, C64 loader bars,
raster bars, progress loader). Frames are returned as lists of strings so
callers can decide whether to stream them to a TUI, API response, or
file output.

Design choices:
- Offline-only: no external dependencies or network usage.
- Deterministic: seeded state makes tests reproducible.
- Width clamped to 20–80 columns to match teletext grid expectations.
- ASCII fallback: set ascii_only=True to avoid ANSI colour codes.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from wizard.services.logging_manager import get_logger

ESC = "\x1b"
RST = f"{ESC}[0m"

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

Frame = List[str]


def clamp_width(width: int, *, default: int = 80) -> int:
    """Clamp requested width into the 20–80 teletext range."""

    bounded = width if width and width > 0 else default
    return max(20, min(80, bounded))


class PatternName(str, Enum):
    CHEVRONS = "chevrons"
    SCANLINES = "scanlines"
    MOSAIC = "mosaic"
    C64_BARS = "c64"
    RASTER_BARS = "raster"
    PROGRESS_LOADER = "loader"


@dataclass
class _PhaseState:
    phase: float = 0.0


@dataclass
class _MosaicState:
    phase: int = 0
    rng: random.Random = field(default_factory=lambda: random.Random(1))


@dataclass
class _C64State:
    phase: int = 0
    head: int = 0


@dataclass
class _LoaderState:
    phase: int = 0
    pos: int = 0
    direction: int = 1


class TeletextPatternService:
    """Deterministic teletext/ANSI pattern generator."""

    def __init__(self, width: int = 80, ascii_only: bool = False):
        self.width = clamp_width(width)
        self.default_ascii_only = ascii_only
        self.logger = get_logger("teletext-patterns")
        self.logger.info(
            "[WIZ] TeletextPatternService ready",
            extra={"width": self.width, "ascii_only": ascii_only},
        )
        self.reset()

    def reset(self) -> None:
        """Reset internal generator state to deterministic defaults."""

        self._chevron_state = _PhaseState()
        self._scanline_state = _PhaseState()
        self._mosaic_state = _MosaicState()
        self._c64_state = _C64State()
        self._raster_state = _PhaseState()
        self._loader_state = _LoaderState()

    def next_frame(
        self,
        pattern: PatternName,
        *,
        width: int | None = None,
        ascii_only: bool | None = None,
    ) -> Frame:
        """Generate the next frame for the requested pattern."""

        w = clamp_width(width or self.width)
        ascii_flag = self.default_ascii_only if ascii_only is None else ascii_only

        generators: Dict[PatternName, callable] = {
            PatternName.CHEVRONS: self._frame_chevrons,
            PatternName.SCANLINES: self._frame_scanlines,
            PatternName.MOSAIC: self._frame_mosaic,
            PatternName.C64_BARS: self._frame_c64_bars,
            PatternName.RASTER_BARS: self._frame_raster_bars,
            PatternName.PROGRESS_LOADER: self._frame_progress_loader,
        }

        if pattern not in generators:
            raise ValueError(f"Unsupported pattern: {pattern}")

        return generators[pattern](w, ascii_flag)

    def _frame_chevrons(self, width: int, ascii_only: bool) -> Frame:
        phase = int(self._chevron_state.phase)
        a = ("/" * 7) + (" " * 8)
        b = ("\\" * 7) + (" " * 8)
        blocks = (a + b) * 4
        span = len(blocks)
        line = (blocks[phase:phase + width] + blocks[:phase])[:width]
        self._chevron_state.phase = (phase + 1) % span
        return [line]

    def _frame_scanlines(self, width: int, ascii_only: bool) -> Frame:
        phase = int(self._scanline_state.phase)
        chars = " .:-=+*#%@" if ascii_only else "░▒▓█"
        denom = max(1, len(chars) - 1)
        row: List[str] = []
        for x in range(width):
            v = (x * 3 + phase) % (denom * 6)
            idx = min(denom, v // 6)
            row.append(chars[idx])
        # Jump phase by a larger step to ensure visible frame-to-frame change.
        self._scanline_state.phase += max(2, denom)
        return ["".join(row)]

    def _frame_mosaic(self, width: int, ascii_only: bool) -> Frame:
        phase = int(self._mosaic_state.phase)
        tiles = ["#", "+", "*", "=", "@", "%", "&"] if ascii_only else [
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
        cols = ["red", "grn", "ylw", "blu", "mag", "cyn"]
        rng = self._mosaic_state.rng
        row: List[str] = []
        for x in range(width):
            r = (x // 4 + phase) % 19
            ch = tiles[(r * r + x + phase) % len(tiles)]
            if ascii_only:
                row.append(ch)
            else:
                c = cols[(x // 10 + (phase // 2)) % len(cols)]
                row.append(f"{FG[c]}{ch}{RST}")
        self._mosaic_state.phase += 1
        return ["".join(row)[:width]]

    def _frame_c64_bars(self, width: int, ascii_only: bool) -> Frame:
        state = self._c64_state
        block = "#" if ascii_only else "█"

        bar_rows = [(0, 8), (2, 8), (4, 8), (6, 8)]
        lines: Frame = []

        if state.phase % 12 == 0:
            title = "  *** COMMODORE 64 ***   LOADING  "
            padded = (title + " " * width)[:width]
            if ascii_only:
                lines.append(padded)
            else:
                lines.append(f"{BG['bblu']}{FG['bwht']}{padded}{RST}")

        for (offset, _) in bar_rows:
            row: List[str] = []
            for x in range(width):
                band = (x // 4 + (state.phase + offset)) % len(C64_CYCLE_BG)
                bg = C64_CYCLE_BG[band]

                dist = (x - state.head) % width
                is_head = dist < 6
                is_tail = 6 <= dist < 10

                fg = "blk" if bg not in ("blk", "bblk") else "bwht"
                if is_head:
                    bg = "bwht"
                    fg = "blk"
                elif is_tail:
                    bg = "bylw"
                    fg = "blk"

                if ascii_only:
                    row.append(block)
                else:
                    row.append(f"{BG[bg]}{FG[fg]}{block}{RST}")
            lines.append("".join(row)[:width])

        state.phase += 1
        state.head = (state.head + 2) % width
        return lines

    def _frame_raster_bars(self, width: int, ascii_only: bool) -> Frame:
        state = self._raster_state
        block = "=" if ascii_only else "▀"
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

        roll = int((math.sin(state.phase) * 0.5 + 0.5) * (len(palette) - 1))
        row: List[str] = []
        for x in range(width):
            stripe = (x // 2 + roll + int(state.phase * 6)) % len(palette)
            bg = palette[stripe]
            if ascii_only:
                row.append(block)
            else:
                fg = "bwht" if ((x + int(state.phase * 10)) % 16 == 0) else "blk"
                row.append(f"{BG[bg]}{FG[fg]}{block}{RST}")
        state.phase += 0.12
        return ["".join(row)[:width]]

    def _frame_progress_loader(self, width: int, ascii_only: bool) -> Frame:
        state = self._loader_state
        label = "LOADING"
        inner = max(10, width - (len(label) + 6))

        # Advance phase early so each call yields a different fill amount.
        state.phase += 1

        left = "[" if ascii_only else "▕"
        right = "]" if ascii_only else "▏"
        empty_ch = "." if ascii_only else " "
        fill_ch = "#" if ascii_only else "█"

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

        fill = (state.phase // 2) % (inner + 1)

        state.pos += state.direction
        if state.pos >= inner - 1:
            state.direction = -1
        elif state.pos <= 0:
            state.direction = 1

        bar: List[str] = []
        for i in range(inner):
            if i < fill:
                if ascii_only:
                    bar.append(fill_ch)
                else:
                    bg = ramp[(i + state.phase) % len(ramp)]
                    if abs(i - state.pos) <= 1:
                        bar.append(f"{BG['bwht']}{FG['blk']}{fill_ch}{RST}")
                    else:
                        bar.append(f"{BG[bg]}{FG['blk']}{fill_ch}{RST}")
            else:
                bar.append(empty_ch if ascii_only else f"{FG['bblk']}{empty_ch}{RST}")

        pct = int((fill / inner) * 100)
        line = f" {label} {left}" + "".join(bar) + f"{right} {pct:3d}%"
        return [(line + " " * width)[:width]]