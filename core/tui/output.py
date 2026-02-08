"""
Output Toolkit for Core TUI

Provides consistent ASCII formatting for banners, alerts, checklists,
tables, and sectioned output.
"""

from typing import Iterable, List, Sequence, Tuple

from core.utils.text_width import display_width, pad_to_width, truncate_to_width
from core.services.viewport_service import ViewportService


class OutputToolkit:
    """Helpers for consistent CLI output formatting."""

    @staticmethod
    def banner(title: str, width: int = 60, pad: str = "=") -> str:
        line = pad * width
        title_line = f"{title}"
        output = "\n".join([line, title_line, line])
        return OutputToolkit._clamp(output)

    @staticmethod
    def alert(message: str, level: str = "info") -> str:
        prefix = {"info": "INFO", "warn": "WARN", "error": "ERROR"}.get(level, "INFO")
        return OutputToolkit._clamp(f"[{prefix}] {message}")

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
            return OutputToolkit._clamp("[?]")
        filled = int((current / total) * width)
        return OutputToolkit._clamp("[" + "#" * filled + "-" * (width - filled) + f"] {current}/{total}")

    @staticmethod
    def map_view(location) -> str:
        from core.services.map_renderer import MapRenderer

        renderer = MapRenderer()
        return OutputToolkit._clamp(renderer.render(location))

    @staticmethod
    def _clamp(text: str) -> str:
        width = ViewportService().get_cols()
        lines = (text or "").splitlines()
        clamped = [truncate_to_width(line, width) for line in lines]
        output = "\n".join(clamped)
        if text.endswith("\n"):
            output += "\n"
        return output
