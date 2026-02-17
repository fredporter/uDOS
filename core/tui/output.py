"""
Output Toolkit for Core TUI

Provides consistent ASCII formatting for banners, alerts, checklists,
tables, and sectioned output.
"""

from typing import Iterable, List, Sequence, Tuple, Optional

from core.utils.text_width import display_width, pad_to_width, truncate_to_width, truncate_ansi_to_width
from core.services.viewport_service import ViewportService
import time


class OutputToolkit:
    """Helpers for consistent CLI output formatting."""

    RESET = "\033[0m"
    INVERT = "\033[7m"
    DIM = "\033[2m"
    SYMBOLS = {
        "info": "•",
        "ok": "✓",
        "warn": "!",
        "error": "✗",
        "progress": "◌",
        "tip": "›",
        "step": "→",
        "milestone": "★",
    }

    @staticmethod
    def banner(title: str, width: Optional[int] = None, pad: str = "=") -> str:
        cols = ViewportService().get_cols()
        w = min(cols, width or cols)
        line = pad * max(1, w)
        title_line = f"{title}"
        output = "\n".join([line, title_line, line])
        return OutputToolkit._clamp(output)

    @staticmethod
    def invert(text: str) -> str:
        return f"{OutputToolkit.INVERT}{text}{OutputToolkit.RESET}"

    @staticmethod
    def faint(text: str) -> str:
        return f"{OutputToolkit.DIM}{text}{OutputToolkit.RESET}"

    @staticmethod
    def rule(char: str = "─", width: Optional[int] = None) -> str:
        cols = ViewportService().get_cols()
        w = min(cols, width or cols)
        return char * max(1, w)

    @staticmethod
    def box(title: str, body: str, width: Optional[int] = None) -> str:
        cols = ViewportService().get_cols()
        w = min(cols, width or cols)
        inner = max(10, w - 4)
        top = f"┌{('─' * (w - 2))}┐"
        head = f"│ {truncate_to_width(title, inner):<{inner}} │"
        mid = f"├{('─' * (w - 2))}┤"
        lines = [top, head, mid]
        for line in (body or "").splitlines():
            lines.append(f"│ {truncate_to_width(line, inner):<{inner}} │")
        lines.append(f"└{('─' * (w - 2))}┘")
        return OutputToolkit._clamp("\n".join(lines))

    @staticmethod
    def invert_section(text: str, width: Optional[int] = None) -> str:
        cols = ViewportService().get_cols()
        w = min(cols, width or cols)
        lines = (text or "").splitlines() or [""]
        out = []
        for line in lines:
            clipped = truncate_to_width(line, w)
            out.append(OutputToolkit.invert(f"{clipped:<{w}}"))
        return OutputToolkit._clamp("\n".join(out))

    @staticmethod
    def columns(left_lines: List[str], right_lines: List[str], gap: int = 2) -> str:
        cols = ViewportService().get_cols()
        left_w = max(12, int(cols * 0.48))
        right_w = max(12, cols - left_w - gap)
        max_len = max(len(left_lines), len(right_lines))
        out = []
        for i in range(max_len):
            left = left_lines[i] if i < len(left_lines) else ""
            right = right_lines[i] if i < len(right_lines) else ""
            out.append(
                f"{pad_to_width(truncate_to_width(left, left_w), left_w)}"
                f"{' ' * gap}"
                f"{truncate_to_width(right, right_w)}"
            )
        return OutputToolkit._clamp("\n".join(out))

    @staticmethod
    def progress_block(current: int, total: int, width: Optional[int] = None, label: Optional[str] = None) -> str:
        cols = ViewportService().get_cols()
        w = min(cols, width or max(20, int(cols * 0.6)))
        w = max(10, w)
        if total <= 0:
            bar = "░" * w
            pct = 0
        else:
            ratio = max(0.0, min(1.0, current / total))
            filled = int(round(ratio * w))
            bar = "█" * filled + "░" * (w - filled)
            pct = int(ratio * 100)
        prefix = f"{label} " if label else ""
        return f"{prefix}[{bar}] {pct}%"

    @staticmethod
    def progress_block_full(current: int, total: int, label: Optional[str] = None) -> str:
        cols = ViewportService().get_cols()
        inner = max(10, cols - 10)
        return OutputToolkit.progress_block(current, total, width=inner, label=label)

    @staticmethod
    def stat_block(label: str, value: str, width: Optional[int] = None, invert: bool = False) -> str:
        cols = ViewportService().get_cols()
        w = min(cols, width or max(18, int(cols * 0.22)))
        w = max(12, w)
        text = f"{label}: {value}"
        line = truncate_to_width(text, w)
        if invert:
            line = OutputToolkit.invert(f"{line:<{w}}")
        return line

    @staticmethod
    def present_frames(frames: Sequence[str], interval: float = 0.8, repeat: int = 1, clear: bool = True) -> None:
        """Present full-screen frames with clears between (presentation-style)."""
        if not frames:
            return
        loops = max(1, int(repeat))
        for _ in range(loops):
            for frame in frames:
                if clear:
                    print("\033[2J\033[H", end="")
                print(frame)
                time.sleep(max(0.0, float(interval)))

    @staticmethod
    def alert(message: str, level: str = "info") -> str:
        prefix = {"info": "INFO", "warn": "WARN", "error": "ERROR"}.get(level, "INFO")
        return OutputToolkit._clamp(f"[{prefix}] {message}")

    @staticmethod
    def line(message: str, level: str = "info", mood: Optional[str] = None) -> str:
        """
        Render a single consistently-prefixed line.

        mood is optional and should be used sparingly for milestone outputs.
        """
        symbol = OutputToolkit.SYMBOLS.get(level, OutputToolkit.SYMBOLS["info"])
        prefix = f"{symbol} "
        if mood:
            prefix = f"{mood} {prefix}"
        return OutputToolkit._clamp(f"{prefix}{message}")

    @staticmethod
    def checklist(items: Sequence[Tuple[str, bool]]) -> str:
        lines = []
        for label, ok in items:
            status = "[x]" if ok else "[ ]"
            lines.append(f"{status} {label}")
        return OutputToolkit._clamp("\n".join(lines))

    @staticmethod
    def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
        widths = [display_width(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], display_width(str(cell)))

        def fmt_row(row_vals):
            return " | ".join(pad_to_width(str(val), widths[i]) for i, val in enumerate(row_vals))

        sep = "-+-".join("-" * w for w in widths)
        output = [fmt_row(headers), sep]
        output.extend(fmt_row(row) for row in rows)
        return OutputToolkit._clamp("\n".join(output))

    @staticmethod
    def section(title: str, body: str) -> str:
        return OutputToolkit._clamp(f"{title}\n" + "-" * len(title) + "\n" + body)

    @staticmethod
    def progress_bar(current: int, total: int, width: int = 24) -> str:
        if total <= 0:
            return OutputToolkit._clamp("Progress: 0/0")
        filled = int((current / total) * width)
        filled = max(0, min(width, filled))
        bar = "█" * filled + "░" * (width - filled)
        return OutputToolkit._clamp(f"Progress: {current}/{total} [{bar}]")

    @staticmethod
    def map_view(location) -> str:
        from core.services.map_renderer import MapRenderer

        renderer = MapRenderer()
        return OutputToolkit._clamp(renderer.render(location))

    @staticmethod
    def _clamp(text: str) -> str:
        width = ViewportService().get_cols()
        lines = (text or "").splitlines()
        clamped = [truncate_ansi_to_width(line, width) for line in lines]
        output = "\n".join(clamped)
        if text.endswith("\n"):
            output += "\n"
        return output
