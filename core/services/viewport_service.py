"""
Viewport Service

Measures and persists the terminal viewport size for TUI rendering.
Values are stored in .env and cached per session to avoid mid-session drift.
"""

import os
import sys
import shutil
from datetime import datetime
from typing import Optional, Tuple, Dict

from core.services.logging_api import get_logger
from core.services.config_sync_service import ConfigSyncManager


class ViewportService:
    """Measure and cache terminal viewport dimensions."""

    ENV_COLS = "UDOS_VIEWPORT_COLS"
    ENV_ROWS = "UDOS_VIEWPORT_ROWS"
    ENV_UPDATED_AT = "UDOS_VIEWPORT_UPDATED_AT"
    ENV_SOURCE = "UDOS_VIEWPORT_SOURCE"

    DEFAULT_COLS = 80
    DEFAULT_ROWS = 24

    _cached_cols: Optional[int] = None
    _cached_rows: Optional[int] = None
    _cached_updated_at: Optional[str] = None
    _cached_source: Optional[str] = None

    def __init__(self):
        self.logger = get_logger("core", category="viewport-service", name="viewport")
        self._sync = ConfigSyncManager()

    def _measure_terminal(self) -> Tuple[int, int]:
        """Measure current terminal size with safe fallbacks."""
        fallback = (self.DEFAULT_COLS, self.DEFAULT_ROWS)
        try:
            if sys.stdout and sys.stdout.isatty():
                size = os.get_terminal_size(sys.stdout.fileno())
                return max(20, size.columns), max(10, size.lines)
        except Exception:
            pass
        try:
            size = shutil.get_terminal_size(fallback=fallback)
            return max(20, size.columns), max(10, size.lines)
        except Exception:
            return self.DEFAULT_COLS, self.DEFAULT_ROWS

    def _load_cached(self) -> None:
        """Load cached viewport from env or .env file."""
        if self._cached_cols and self._cached_rows:
            return

        cols = os.environ.get(self.ENV_COLS)
        rows = os.environ.get(self.ENV_ROWS)
        updated = os.environ.get(self.ENV_UPDATED_AT)
        source = os.environ.get(self.ENV_SOURCE)

        if not cols or not rows:
            env = self._sync.load_env_dict()
            cols = cols or env.get(self.ENV_COLS)
            rows = rows or env.get(self.ENV_ROWS)
            updated = updated or env.get(self.ENV_UPDATED_AT)
            source = source or env.get(self.ENV_SOURCE)

        try:
            self._cached_cols = int(cols) if cols else None
            self._cached_rows = int(rows) if rows else None
        except Exception:
            self._cached_cols = None
            self._cached_rows = None

        self._cached_updated_at = updated
        self._cached_source = source

    def get_size(self) -> Tuple[int, int]:
        """Return cached viewport size (or defaults if missing)."""
        self._load_cached()
        cols = self._cached_cols or self.DEFAULT_COLS
        rows = self._cached_rows or self.DEFAULT_ROWS
        return cols, rows

    def get_cols(self) -> int:
        return self.get_size()[0]

    def get_rows(self) -> int:
        return self.get_size()[1]

    def refresh(self, source: str = "manual") -> Dict[str, str]:
        """Measure viewport and persist to .env."""
        cols, rows = self._measure_terminal()
        updated_at = datetime.utcnow().isoformat() + "Z"
        updates = {
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
        os.environ[self.ENV_COLS] = str(cols)
        os.environ[self.ENV_ROWS] = str(rows)
        os.environ[self.ENV_UPDATED_AT] = updated_at
        os.environ[self.ENV_SOURCE] = source

        return {
            "cols": str(cols),
            "rows": str(rows),
            "updated_at": updated_at,
            "source": source,
            "status": "success" if ok else "warning",
            "message": message if not ok else "Viewport refreshed",
        }
