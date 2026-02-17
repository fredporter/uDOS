"""
Text width helpers for monospaced terminal rendering.

Treats emoji and wide characters as width 2 to avoid unwanted wrapping.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _is_emoji(ch: str) -> bool:
    code = ord(ch)
    # Common emoji blocks
    return (
        0x1F300 <= code <= 0x1F5FF
        or 0x1F600 <= code <= 0x1F64F
        or 0x1F680 <= code <= 0x1F6FF
        or 0x1F700 <= code <= 0x1F77F
        or 0x1F780 <= code <= 0x1F7FF
        or 0x1F800 <= code <= 0x1F8FF
        or 0x1F900 <= code <= 0x1F9FF
        or 0x1FA00 <= code <= 0x1FAFF
        or 0x2600 <= code <= 0x26FF
        or 0x2700 <= code <= 0x27BF
    )


def char_width(ch: str) -> int:
    """Return display width for a single character."""
    if not ch:
        return 0
    if _is_emoji(ch):
        return 2
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes."""
    return _ANSI_RE.sub("", text or "")


def display_width(text: str) -> int:
    """Compute display width of text, counting emoji as width 2."""
    clean = strip_ansi(text)
    return sum(char_width(ch) for ch in clean)


def pad_to_width(text: str, width: int, fill: str = " ") -> str:
    """Pad text on the right to a target display width."""
    current = display_width(text)
    if current >= width:
        return text
    return text + (fill * (width - current))


def truncate_to_width(text: str, width: int, ellipsis: str = "…") -> str:
    """Truncate text to a target display width, appending ellipsis if needed."""
    if width <= 0:
        return ""
    if display_width(text) <= width:
        return text
    ell_w = display_width(ellipsis)
    target = max(0, width - ell_w)
    out = []
    used = 0
    for ch in strip_ansi(text):
        w = char_width(ch)
        if used + w > target:
            break
        out.append(ch)
        used += w
    return "".join(out) + ellipsis


def truncate_ansi_to_width(text: str, width: int, ellipsis: str = "…") -> str:
    """Truncate text to a target display width while preserving ANSI escapes."""
    if width <= 0:
        return ""
    if display_width(text) <= width:
        return text

    ell_w = display_width(ellipsis)
    target = max(0, width - ell_w)
    out = []
    used = 0
    i = 0
    text_len = len(text)
    has_ansi = False

    while i < text_len and used < target:
        ch = text[i]
        if ch == "\x1b":
            # ANSI escape sequence
            has_ansi = True
            seq = [ch]
            i += 1
            while i < text_len:
                seq.append(text[i])
                if text[i].isalpha():
                    i += 1
                    break
                i += 1
            out.append("".join(seq))
            continue

        w = char_width(ch)
        if used + w > target:
            break
        out.append(ch)
        used += w
        i += 1

    result = "".join(out) + ellipsis
    # Reset color if we had ANSI codes to prevent color bleed
    if has_ansi:
        result += "\033[0m"
    return result
