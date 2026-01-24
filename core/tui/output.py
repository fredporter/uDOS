"""
Output Toolkit for Core TUI

Provides consistent ASCII formatting for banners, alerts, checklists,
tables, and sectioned output.
"""

from typing import Iterable, List, Sequence, Tuple


class OutputToolkit:
    """Helpers for consistent CLI output formatting."""

    @staticmethod
    def banner(title: str, width: int = 60, pad: str = "=") -> str:
        line = pad * width
        title_line = f"{title}"
        return "\n".join([line, title_line, line])

    @staticmethod
    def alert(message: str, level: str = "info") -> str:
        prefix = {"info": "INFO", "warn": "WARN", "error": "ERROR"}.get(level, "INFO")
        return f"[{prefix}] {message}"

    @staticmethod
    def checklist(items: Sequence[Tuple[str, bool]]) -> str:
        lines = []
        for label, ok in items:
            status = "[x]" if ok else "[ ]"
            lines.append(f"{status} {label}")
        return "\n".join(lines)

    @staticmethod
    def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))

        def fmt_row(row_vals):
            return " | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row_vals))

        sep = "-+-".join("-" * w for w in widths)
        output = [fmt_row(headers), sep]
        output.extend(fmt_row(row) for row in rows)
        return "\n".join(output)

    @staticmethod
    def section(title: str, body: str) -> str:
        return f"{title}\n" + "-" * len(title) + "\n" + body

    @staticmethod
    def progress_bar(current: int, total: int, width: int = 24) -> str:
        if total <= 0:
            return "[?]"
        filled = int((current / total) * width)
        return "[" + "#" * filled + "-" * (width - filled) + f"] {current}/{total}"

    @staticmethod
    def map_view(location) -> str:
        from core.services.map_renderer import MapRenderer

        renderer = MapRenderer()
        return renderer.render(location)
