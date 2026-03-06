"""Viewport Service

Measures and persists the terminal viewport size for TUI rendering.
Values are stored in .env and cached per session to avoid mid-session drift.
"""
from __future__ import annotations

from datetime import UTC, datetime
import os
import re
import shutil
import sys

from core.services.config_sync_service import ConfigSyncManager
from core.services.logging_api import get_logger
from core.services.unified_config_loader import get_config_loader


class ViewportService:
    """Measure and cache terminal viewport dimensions."""

    ENV_SIZE = "UDOS_VIEWPORT_SIZE_CH"
    ENV_COLS = "UDOS_VIEWPORT_COLS"
    ENV_ROWS = "UDOS_VIEWPORT_ROWS"
    ENV_UPDATED_AT = "UDOS_VIEWPORT_UPDATED_AT"
    ENV_SOURCE = "UDOS_VIEWPORT_SOURCE"

    DEFAULT_COLS = 80
    DEFAULT_ROWS = 30
    MIN_COLS = 25
    MIN_ROWS = 25

    _cached_cols: int | None = None
    _cached_rows: int | None = None
    _cached_updated_at: str | None = None
    _cached_source: str | None = None

    def __init__(self):
        self.logger = get_logger("core", category="viewport-service", name="viewport")
        self._sync = ConfigSyncManager()

    def _measure_terminal(self) -> tuple[int, int]:
        """Measure current terminal size with safe fallbacks."""
        fallback = (self.DEFAULT_COLS, self.DEFAULT_ROWS)
        try:
            if sys.stdout and sys.stdout.isatty():
                size = os.get_terminal_size(sys.stdout.fileno())
                return max(self.MIN_COLS, size.columns), max(self.MIN_ROWS, size.lines)
        except Exception:
            pass
        try:
            size = shutil.get_terminal_size(fallback=fallback)
            return max(self.MIN_COLS, size.columns), max(self.MIN_ROWS, size.lines)
        except Exception:
            return self.DEFAULT_COLS, self.DEFAULT_ROWS

    def _parse_viewport_size_ch(self, raw: str | None) -> tuple[int, int] | None:
        if not raw:
            return None
        match = re.match(r"^\s*(\d+)\s*x\s*(\d+)\s*$", str(raw), flags=re.IGNORECASE)
        if not match:
            return None
        cols = max(self.MIN_COLS, int(match.group(1)))
        rows = max(self.MIN_ROWS, int(match.group(2)))
        return cols, rows

    def _load_cached(self) -> None:
        """Load cached viewport from env or .env file."""
        if self._cached_cols and self._cached_rows:
            return

        loader = get_config_loader()
        size = loader.get(self.ENV_SIZE)
        cols = loader.get(self.ENV_COLS)
        rows = loader.get(self.ENV_ROWS)
        updated = loader.get(self.ENV_UPDATED_AT)
        source = loader.get(self.ENV_SOURCE)

        explicit = self._parse_viewport_size_ch(size)
        if explicit:
            self._cached_cols, self._cached_rows = explicit
        else:
            try:
                self._cached_cols = int(cols) if cols else None
                self._cached_rows = int(rows) if rows else None
            except Exception:
                self._cached_cols = None
                self._cached_rows = None

        try:
            if self._cached_cols is not None:
                self._cached_cols = max(self.MIN_COLS, self._cached_cols)
            if self._cached_rows is not None:
                self._cached_rows = max(self.MIN_ROWS, self._cached_rows)
        except Exception:
            self._cached_cols, self._cached_rows = None, None

        self._cached_updated_at = updated
        self._cached_source = source

    def get_size(self) -> tuple[int, int]:
        """Return cached viewport size (or defaults if missing)."""
        self._load_cached()
        cols = self._cached_cols or self.DEFAULT_COLS
        rows = self._cached_rows or self.DEFAULT_ROWS
        return cols, rows

    def get_cols(self) -> int:
        return self.get_size()[0]

    def get_rows(self) -> int:
        return self.get_size()[1]

    def refresh(self, source: str = "manual") -> dict[str, str]:
        """Measure viewport and persist to .env."""
        cols, rows = self._measure_terminal()
        size_ch = f"{cols}x{rows}"
        updated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        updates = {
            self.ENV_SIZE: size_ch,
            self.ENV_COLS: str(cols),
            self.ENV_ROWS: str(rows),
            self.ENV_UPDATED_AT: updated_at,
            self.ENV_SOURCE: source,
        }

        ok, message = self._sync.update_env_vars(updates)
        if not ok:
            self.logger.warning(f"[LOCAL] Viewport update failed: {message}")

        # Cache + environment for this process
        self._cached_cols = cols
        self._cached_rows = rows
        self._cached_updated_at = updated_at
        self._cached_source = source

        os.environ[self.ENV_SIZE] = size_ch
        os.environ[self.ENV_COLS] = str(cols)
        os.environ[self.ENV_ROWS] = str(rows)
        os.environ[self.ENV_UPDATED_AT] = updated_at
        os.environ[self.ENV_SOURCE] = source

        return {
            "size_ch": size_ch,
            "cols": str(cols),
            "rows": str(rows),
            "updated_at": updated_at,
            "source": source,
            "status": "success" if ok else "warning",
            "message": message if not ok else "Viewport refreshed",
        }
