"""
Unified Logging Manager for Core

Centralized logging for Core TUI with:
- Flat directory structure (memory/logs/)
- Category-based filenames (prefix-date.log)
- Automatic daily rotation
- Transport tagging ([LOCAL], [MESH], [BT-PRIV], etc.)
- Location privacy masking

Usage:
    from core.services.logging_manager import get_logger

    logger = get_logger('command-pattern')
    logger.info('[LOCAL] Pattern command executed')

Author: uDOS Core Team
Version: Core v1.2.0
Date: 2026-01-24
"""

import logging
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


# Project root detection
def get_repo_root() -> Path:
    """Get repository root from current file location."""
    current = Path(__file__).resolve()
    # core/services/logging_manager.py -> go up to repo root
    return current.parent.parent.parent


class FlatFileHandler(logging.FileHandler):
    """Custom file handler with flat directory structure and daily rotation."""

    def __init__(self, category: str, log_dir: Path, mode: str = "a"):
        """
        Initialize handler with category-based filename.

        Args:
            category: Log category (e.g., 'command-pattern', 'system-startup')
            log_dir: Base log directory
            mode: File mode (default: append)
        """
        self.category = category
        self.log_dir = log_dir
        self.current_date = datetime.now().date()

        # Build filename: category-YYYY-MM-DD.log
        filename = self._build_filename()
        filepath = log_dir / filename

        super().__init__(str(filepath), mode=mode)

    def _build_filename(self) -> str:
        """Build filename with current date."""
        date_str = self.current_date.strftime("%Y-%m-%d")
        return f"{self.category}-{date_str}.log"

    def emit(self, record):
        """Emit a record, rotating file if date changed."""
        now_date = datetime.now().date()
        if now_date != self.current_date:
            # Date changed - rotate to new file
            self.close()
            self.current_date = now_date
            filename = self._build_filename()
            filepath = self.log_dir / filename
            self.baseFilename = str(filepath)
            self.stream = self._open()

        super().emit(record)


class CategoryFormatter(logging.Formatter):
    """Formatter that adds category to log record."""

    def __init__(self, category: str, fmt: str, datefmt: str = None):
        """
        Initialize formatter with category.

        Args:
            category: Log category
            fmt: Log format string
            datefmt: Date format string
        """
        super().__init__(fmt, datefmt)
        self.category = category

    def format(self, record):
        """Format record with category."""
        record.category = self.category
        return super().format(record)


class ContextFilter(logging.Filter):
    """Filter that injects context into log records."""

    def __init__(self, context: Optional[Dict] = None):
        """
        Initialize filter with context dict.

        Args:
            context: Context dictionary (user, session, source, etc.)
        """
        super().__init__()
        self.context = context or {}

    def filter(self, record):
        """Add context to record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


class LocationMaskingFilter(logging.Filter):
    """Filter to mask precise location data for privacy."""

    # Patterns to mask (coordinate-like data)
    COORDINATE_PATTERN = re.compile(
        r"-?\d{1,3}\.\d{4,}"  # Latitude/longitude-like numbers
    )

    def filter(self, record):
        """Mask location data in message."""
        if hasattr(record, "msg"):
            msg = str(record.msg)
            # Replace precise coordinates with masked version
            msg = self.COORDINATE_PATTERN.sub("[COORDS]", msg)
            record.msg = msg
        return True


class LoggingManager:
    """Central logging manager for Core TUI."""

    def __init__(self, log_dir: Optional[str] = None):
        """Initialize logging manager."""
        if log_dir is None:
            # Allow override via env; otherwise anchor to repo root
            env_log_dir = os.environ.get("UDOS_LOG_DIR")
            if env_log_dir:
                log_dir = env_log_dir
            else:
                log_dir = str(get_repo_root() / "memory" / "logs")

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.loggers: Dict[str, logging.Logger] = {}

    def get_logger(
        self,
        category: str,
        level: int = logging.INFO,
        source: Optional[str] = None,
    ) -> logging.Logger:
        """Get or create logger for category.

        Args:
            category: Log category (e.g., 'command-pattern', 'system-startup')
            level: Logging level (DEBUG, INFO, WARN, ERROR, CRITICAL)
            source: Log source identifier (tui, tauri, api, system)

        Returns:
            Configured logger instance

        Example:
            logger = get_logger('command-pattern', source='tui')
            logger.info('[LOCAL] Pattern displayed')
        """
        cache_key = f"{category}:{source or 'core'}"

        if cache_key in self.loggers:
            return self.loggers[cache_key]

        # Create new logger
        logger = logging.Logger(category, level=level)

        # Add context filter
        ctx = {"source": source or "core"}
        context_filter = ContextFilter(ctx)
        logger.addFilter(context_filter)

        # Add location masking filter for privacy
        location_filter = LocationMaskingFilter()
        logger.addFilter(location_filter)

        # Add flat file handler
        handler = FlatFileHandler(category, self.log_dir)

        # Set formatter
        fmt = "[%(asctime)s] [%(levelname)s] [%(category)s]"
        if source:
            fmt += f" [{source}]"
        fmt += " %(message)s"
        formatter = CategoryFormatter(category, fmt, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        # Cache logger
        self.loggers[cache_key] = logger

        return logger


# Global instance
_logging_manager: Optional[LoggingManager] = None


def get_logging_manager() -> LoggingManager:
    """Get global logging manager instance."""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager


def get_logger(category: str, source: Optional[str] = None, **kwargs) -> logging.Logger:
    """Convenience function to get logger.

    Args:
        category: Log category (e.g., 'command-pattern', 'system-startup')
        source: Log source identifier (core by default)
        **kwargs: Additional arguments

    Returns:
        Configured logger

    Example:
        logger = get_logger('command-pattern')
        logger.info('[LOCAL] Pattern command executed')
    """
    manager = get_logging_manager()
    return manager.get_logger(category, source=source, **kwargs)


# Transport tag constants for logging
class LogTags:
    """Standard logging tags for transport identification."""

    LOCAL = "[LOCAL]"  # Local device operation
    MESH = "[MESH]"  # MeshCore P2P
    BT_PRIV = "[BT-PRIV]"  # Bluetooth Private (paired devices)
    BT_PUB = "[BT-PUB]"  # Bluetooth Public (beacons only - NO DATA)
    NFC = "[NFC]"  # NFC contact
    QR = "[QR]"  # QR relay
    AUD = "[AUD]"  # Audio transport
    WIZ = "[WIZ]"  # Wizard Server operation
    GMAIL = "[GMAIL]"  # Gmail relay (Wizard only)
