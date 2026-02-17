"""
Lightweight TUI UI elements (no external deps).

Provides:
- Spinner: animated progress indicator with elapsed time
- ProgressBar: simple text progress bar
- Table: aligned text table formatter
"""

from __future__ import annotations

import sys
import time
import threading
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from core.utils.text_width import display_width, pad_to_width, truncate_to_width
from core.services.viewport_service import ViewportService


@dataclass
class Spinner:
    """Lightweight spinner for blocking operations."""

    label: str = "Working"
    frames: Sequence[str] | None = None
    interval: float = 0.1
    show_elapsed: bool = True

    def __post_init__(self) -> None:
        if not self.frames:
            self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._start = 0.0
        self._running = False
        self._idx = 0

    def start(self) -> None:
        self._start = time.time()
        self._running = True

    def tick(self) -> None:
        if not self._running:
            return
        frame = self.frames[self._idx % len(self.frames)]
        elapsed = int(time.time() - self._start) if self.show_elapsed else None
        if elapsed is None:
            text = f"{self.label} {frame}"
        else:
            text = f"{self.label} {frame} {elapsed}s"
        # Clear the full terminal row first so stale suffix characters from
        # prior longer frames cannot bleed into subsequent output.
        sys.stdout.write("\r\033[2K" + text)
        sys.stdout.flush()
        self._idx += 1

    def stop(self, success_text: str | None = None) -> None:
        if not self._running:
            return
        elapsed = time.time() - self._start
        sys.stdout.write("\r\033[2K")
        sys.stdout.flush()
        self._running = False
        if success_text:
            sys.stdout.write(f"{success_text} ({elapsed:0.1f}s)\n")
            sys.stdout.flush()

    def start_background(self, stop_event: threading.Event) -> threading.Thread:
        """Start spinner ticks in a background thread until stop_event is set."""
        self.start()

        def _spin() -> None:
            while not stop_event.is_set():
                self.tick()
                time.sleep(self.interval)

        thread = threading.Thread(target=_spin, daemon=True)
        thread.start()
        return thread


@dataclass
class ProgressBar:
    """Simple text progress bar."""

    total: int
    width: int = 24
    fill: str = "█"
    empty: str = "░"

    def render(self, current: int, label: str | None = None) -> str:
        if self.total <= 0:
            return f"{label + ' ' if label else ''}[{self.empty * self.width}] 0%"
        ratio = max(0.0, min(1.0, current / self.total))
        filled = int(self.width * ratio)
        bar = self.fill * filled + self.empty * (self.width - filled)
        percent = int(ratio * 100)
        prefix = f"{label} " if label else ""
        return f"{prefix}[{bar}] {percent}%"


def format_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    """Format a simple left-aligned table."""
    rows_list: List[List[str]] = [list(map(str, headers))]
    for row in rows:
        rows_list.append([str(cell) for cell in row])

    col_widths = [0] * len(rows_list[0])
    for row in rows_list:
        for idx, cell in enumerate(row):
            col_widths[idx] = max(col_widths[idx], display_width(cell))

    def fmt_row(row: Sequence[str]) -> str:
        return " | ".join(pad_to_width(cell, col_widths[i]) for i, cell in enumerate(row))

    header_line = fmt_row(rows_list[0])
    divider = "-+-".join("-" * w for w in col_widths)
    data_lines = [fmt_row(row) for row in rows_list[1:]]

    width = ViewportService().get_cols()
    lines = [header_line, divider] + data_lines
    clamped = [truncate_to_width(line, width) for line in lines]
    return "\n".join(clamped)
