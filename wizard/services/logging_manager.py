"""
Logging Manager for Wizard Server

Centralized logging for Wizard and its services with:
- Flat directory structure (memory/logs/)
- Category-based filenames (prefix-date.log)
- Automatic daily rotation
- Location privacy masking

Usage:
    from wizard.services.logging_manager import get_logger

    logger = get_logger('ai-gateway')
    logger.info('[WIZARD] Processing AI request')
"""

import logging
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any


class FlatFileHandler(logging.FileHandler):
    """Custom file handler with flat directory structure and daily rotation."""

    def __init__(self, category: str, log_dir: Path, date_format: str = "%Y-%m-%d"):
        """Initialize handler with category-based filename."""
        self.category = category
        self.log_dir = Path(log_dir)
        self.date_format = date_format
        self.current_date = None

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize with current filename
        filename = self._get_current_filename()
        super().__init__(filename, mode="a", encoding="utf-8")

    def _get_current_filename(self) -> str:
        """Get current log filename based on category and date."""
        date_str = datetime.now().strftime(self.date_format)
        self.current_date = date_str
        return str(self.log_dir / f"{self.category}-{date_str}.log")

    def emit(self, record: logging.LogRecord):
        """Emit log record, rotating file if date changed."""
        current_date = datetime.now().strftime(self.date_format)
        if current_date != self.current_date:
            # Date changed, rotate to new file
            self.close()
            self.baseFilename = self._get_current_filename()
            self.stream = self._open()

        super().emit(record)


class CategoryFormatter(logging.Formatter):
    """Formatter that adds category to log record."""

    def __init__(self, category: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category

    def format(self, record: logging.LogRecord) -> str:
        record.category = self.category
        return super().format(record)


class ContextFilter(logging.Filter):
    """Filter that injects context into log records."""

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.context = context or {}

    def filter(self, record: logging.LogRecord) -> bool:
        if self.context:
            record.context = self.context
        if not hasattr(record, "source"):
            record.source = self.context.get("source", "wizard")
        return True


class LoggingManager:
    """Central logging manager for Wizard services."""

    # Log retention policies (in days)
    RETENTION_POLICIES = {
        "ai-gateway": 30,
        "api-server": 30,
        "device-auth": 30,
        "policy-enforcer": 30,
        "model-router": 30,
        "cost-tracking": 30,
        "error": 90,
        "debug": 7,
        "audit": 90,
    }

    def __init__(self, log_dir: Optional[str] = None):
        """Initialize logging manager."""
        if log_dir is None:
            # Use memory/logs/ directory (anchor to repo root)
            repo_root = Path(__file__).parent.parent.parent.resolve()
            log_dir = str(repo_root / "memory" / "logs")
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.loggers: Dict[str, logging.Logger] = {}

    def get_logger(
        self,
        category: str,
        level: int = logging.INFO,
        source: Optional[str] = None,
    ) -> logging.Logger:
        """Get or create logger for category."""
        cache_key = f"{category}:{source or 'wizard'}"

        if cache_key in self.loggers:
            return self.loggers[cache_key]

        # Create new logger
        logger = logging.Logger(category, level=level)

        # Add context filter
        ctx = {"source": source or "wizard"}
        context_filter = ContextFilter(ctx)
        logger.addFilter(context_filter)

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

    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about current logs."""
        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "by_category": {},
        }

        for log_file in self.log_dir.glob("*.log"):
            stats["total_files"] += 1
            size_bytes = log_file.stat().st_size
            stats["total_size_mb"] += size_bytes / (1024 * 1024)

            category = log_file.stem.split("-")[0]
            if category not in stats["by_category"]:
                stats["by_category"][category] = {"count": 0, "size_mb": 0}
            stats["by_category"][category]["count"] += 1
            stats["by_category"][category]["size_mb"] += size_bytes / (1024 * 1024)

        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        for cat_stats in stats["by_category"].values():
            cat_stats["size_mb"] = round(cat_stats["size_mb"], 2)

        return stats


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
        category: Log category (e.g., 'ai-gateway', 'api-server')
        source: Log source identifier (wizard by default)
        **kwargs: Additional arguments

    Returns:
        Configured logger

    Example:
        logger = get_logger('ai-gateway')
        logger.info('[WIZARD] Processing AI request')
    """
    manager = get_logging_manager()
    return manager.get_logger(category, source=source, **kwargs)
