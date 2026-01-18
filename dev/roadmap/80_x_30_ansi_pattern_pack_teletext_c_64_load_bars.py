#!/usr/bin/env python3
"""teletext80.py — 80-column ANSI patterns for terminal fun (incl. C64-ish load bars)

Run:
  python3 teletext80.py c64
  python3 teletext80.py chevrons
  python3 teletext80.py scanlines
  python3 teletext80.py mosaic

Notes:
- Designed for 80 columns; will adapt down if your terminal is narrower.
- Stop with Ctrl+C.
- Uses ANSI escapes + some Unicode blocks. Use --ascii to force ASCII.
"""

import argparse
import math
import os
import random
import shutil
import sys
import time

ESC = "\x1b"
RST = f"{ESC}[0m"
HIDE = f"{ESC}[?25l"
SHOW = f"{ESC}[?25h"

# Simple 16-colour-ish ANSI (portable)
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

# C64-ish palette vibe (approx; terminals vary). We mostly need the *cycling* feel.
C64_CYCLE_BG = [
    "bblu",  # bright blue
    "blu",   # blue
    "bblk",  # dark grey
    "blk",   # black
    "bgrn",  # bright green
    "grn",   # green
    "bylw",  # bright yellow
    "ylw",   # yellow
    "bred",  # bright red
    "red",   # red
    "bmag",  # bright magenta
    "mag",   # magenta
    "bcyn",  # bright cyan
    "cyn",   # cyan
    "bwht",  # bright white
    "wht",   # white
]

UNICODE_FULL = "█"
UNICODE_HALF = "▀"  # can be used for scanline-y looks
ASCII_FULL = "#"


def term_width(default=80) -> int:
    try:
        return shutil.get_terminal_size((default, 24)).columns
    except Exception:
        return default


def clamp_width(w: int) -> int:
    # Always *cap* to 80 as per your spec, but adapt down if narrower.
    return max(20, min(80, w))


def write_line(s: str):
    sys.stdout.write(s + "\n")
    sys.stdout.flush()


def pattern_chevrons(w: int, delay: float, ascii_only: bool):
    phase = 0
    a = ("/" * 7) + (" " * 8)
    b = ("\\" * 7) + (" " * 8)
    blocks = (a + b) * 4
    L = len(blocks)
    while True:
        line = (blocks[phase:phase + w] + blocks[:phase])[:w]
        write_line(line)
        phase = (phase + 1) % L
        time.sleep(delay)


def pattern_scanlines(w: int, delay: float, ascii_only: bool):
    phase = 0
    chars = " .:-=+*#%@" if ascii_only else "░▒▓█"
    denom = max(1, len(chars) - 1)
    while True:
        s = []
        for x in range(w):
            v = (x * 3 + phase) % (denom * 6)
            idx = min(denom, v // 6)
            s.append(chars[idx])
        write_line("".join(s))
        phase += 1
        time.sleep(delay)


def pattern_mosaic(w: int, delay: float, ascii_only: bool):
    phase = 0
    random.seed(1)
    tiles = ["#", "+", "*", "=", "@", "%", "&"] if ascii_only else [
        "▀", "▄", "█", "▌", "▐", "▖", "▗", "▘", "▙", "▚", "▛", "▜", "▝", "▞", "▟"
    ]
    cols = ["red", "grn", "ylw", "blu", "mag", "cyn"]
    while True:
        s = []
        for x in range(w):
            r = (x // 4 + phase) % 19
            ch = tiles[(r * r + x + phase) % len(tiles)]
            c = cols[(x // 10 + (phase // 2)) % len(cols)]
            s.append(FG[c] + ch + RST)
        write_line("".join(s))
        phase += 1
        time.sleep(delay)


def pattern_c64(w: int, delay: float, ascii_only: bool):
    """Retro-ish 'LOADING / data transfer' colour cycle bars.

    Vibe goals:
      - Thick horizontal bands with a cycling palette
      - A moving 'transfer head' that brightens a segment
      - Occasional title strip to sell the loader feel

    Output is row-by-row so it scrolls.
    """

    block = ASCII_FULL if ascii_only else UNICODE_FULL

    bar_rows = [
        (0, 8),
        (2, 8),
        (4, 8),
        (6, 8),
    ]

    phase = 0
    head = 0

    title = "  *** COMMODORE 64 ***   LOADING  "
    title = (title + " " * w)[:w]

    while True:
        if phase % 12 == 0:
            write_line(BG["bblu"] + FG["bwht"] + title + RST)

        for (off, _) in bar_rows:
            s = []
            for x in range(w):
                band = (x // 4 + (phase + off)) % len(C64_CYCLE_BG)
                bg = C64_CYCLE_BG[band]

                dist = (x - head) % w
                is_head = dist < 6
                is_tail = 6 <= dist < 10

                fg = "blk" if bg not in ("blk", "bblk") else "bwht"
                if is_head:
                    bg = "bwht"
                    fg = "blk"
                elif is_tail:
                    bg = "bylw"
                    fg = "blk"

                s.append(BG[bg] + FG[fg] + block + RST)

            write_line("".join(s))

        phase += 1
        head = (head + 2) % w
        time.sleep(delay)


def pattern_raster_bars(w: int, delay: float, ascii_only: bool):
    """Thin rolling raster bars (demoscene-ish).

    Uses multiple colour stripes per line, with a sinusoidal roll so the bands appear
    to move vertically as the terminal scrolls.
    """

    block = "=" if ascii_only else "▀"
    phase = 0.0

    # Narrower, punchier subset for that classic raster look
    palette = [
        "bblu", "blu", "bcyn", "cyn", "bgrn", "grn", "bylw", "ylw", "bred", "red", "bmag", "mag"
    ]

    while True:
        # Choose which palette slice is "in phase" for this row
        # so the colour sequence appears to roll.
        roll = int((math.sin(phase) * 0.5 + 0.5) * (len(palette) - 1))
        s = []
        for x in range(w):
            # Thin stripes across X, but phase-shifted each row
            stripe = (x // 2 + roll + int(phase * 6)) % len(palette)
            bg = palette[stripe]
            # occasional highlight spark
            fg = "bwht" if ((x + int(phase * 10)) % 16 == 0) else "blk"
            s.append(BG[bg] + FG[fg] + block + RST)
        write_line("".join(s))
        phase += 0.12
        time.sleep(delay)


def pattern_progress_loader(w: int, delay: float, ascii_only: bool):
    """Chunky progress bar with cycling fill + bouncing head.

    Designed to feel like a C64 tape/disk loader: a frame, a fill that advances,
    and a cycling colour treatment across the filled area.
    """

    # Inner width for the bar, leaving room for a tiny label
    label = "LOADING"
    inner = max(10, w - (len(label) + 6))

    left = "[" if ascii_only else "▕"
    right = "]" if ascii_only else "▏"
    empty_ch = "." if ascii_only else " "
    fill_ch = "#" if ascii_only else "█"

    phase = 0
    pos = 0
    dirn = 1

    # A classic-ish cycling ramp
    ramp = ["bblu", "blu", "bcyn", "cyn", "bgrn", "grn", "bylw", "ylw", "bred", "red", "bmag", "mag"]

    while True:
        fill = (phase // 2) % (inner + 1)

        # bouncing head over the fill zone
        pos += dirn
        if pos >= inner - 1:
            dirn = -1
        elif pos <= 0:
            dirn = 1

        bar = []
        for i in range(inner):
            if i < fill:
                bg = ramp[(i + phase) % len(ramp)]
                # head highlight (only if within filled section)
                if abs(i - pos) <= 1:
                    bar.append(BG["bwht"] + FG["blk"] + fill_ch + RST)
                else:
                    bar.append(BG[bg] + FG["blk"] + fill_ch + RST)
            else:
                bar.append(FG["bblk"] + empty_ch + RST)

        pct = int((fill / inner) * 100)
        line = f" {label} {left}" + "".join(bar) + f"{right} {pct:3d}%"
        # Hard clamp to w (ANSI makes this imperfect, but we cap to spec)
        write_line((line + " " * w)[:w])

        phase += 1
        time.sleep(delay)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern", choices=["c64", "chevrons", "scanlines", "mosaic"], help="which pattern")
    ap.add_argument("--delay", type=float, default=0.03, help="seconds between frames")
    ap.add_argument("--ascii", action="store_true", help="force ASCII-only")
    args = ap.parse_args()

    w = clamp_width(term_width(80))

    sys.stdout.write(HIDE)
    sys.stdout.flush()
    try:
        if args.pattern == "c64":
            pattern_c64(w, args.delay, args.ascii)
        elif args.pattern == "chevrons":
            pattern_chevrons(w, args.delay, args.ascii)
        elif args.pattern == "scanlines":
            pattern_scanlines(w, args.delay, args.ascii)
        elif args.pattern == "mosaic":
            pattern_mosaic(w, args.delay, args.ascii)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RST + SHOW)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
