"""
Unified Logging System - Integration across Core, Wizard, Goblin, Extensions

This module provides a unified logging interface that integrates logs from:
- Core TUI (command execution, handlers, state)
- Wizard Server (AI routing, APIs, services)
- Goblin Dev Server (experimental features)
- Extensions (plugins, transport, API)

All logs are aggregated into a single view for debugging and monitoring.

Usage:
    from core.services.unified_logging import UnifiedLogger, LogContext
    
    unified = UnifiedLogger()
    
    # Log from Core
    unified.log_core('command-dispatch', 'Dispatching MAP command', level='INFO')
    
    # Log from Wizard (called from wizard services)
    unified.log_wizard('ai-routing', 'Escalated to OpenRouter', model='claude-3.5')
    
    # Log from Goblin
    unified.log_goblin('notion-sync', 'Synced 5 pages', pages_count=5)
    
    # View unified log
    unified.view_last(50)  # Last 50 entries across all systems

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-28
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum


class LogSource(Enum):
    """Log source identifiers."""
    CORE = "CORE"
    WIZARD = "WIZARD"
    GOBLIN = "GOBLIN"
    EXTENSION = "EXTENSION"
    UNIFIED = "UNIFIED"


class LogLevel(Enum):
    """Log levels (matches Python logging)."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogContext:
    """Structured log context across all systems."""
    
    def __init__(
        self,
        source: LogSource,
        category: str,
        message: str,
        level: LogLevel = LogLevel.INFO,
        **metadata
    ):
        """Initialize log context.
        
        Args:
            source: Log source (CORE, WIZARD, GOBLIN, EXTENSION)
            category: Log category (e.g., 'command-dispatch', 'ai-routing')
            message: Log message
            level: Log level
            **metadata: Additional structured data
        """
        self.timestamp = datetime.now()
        self.source = source
        self.category = category
        self.message = message
        self.level = level
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source.value,
            "category": self.category,
            "message": self.message,
            "level": self.level.value,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())
    
    def __str__(self) -> str:
        """Pretty string representation."""
        meta_str = " | ".join(f"{k}={v}" for k, v in self.metadata.items())
        if meta_str:
            meta_str = f" | {meta_str}"
        return f"[{self.timestamp.strftime('%H:%M:%S')}] [{self.source.value}] [{self.level.value}] {self.category}: {self.message}{meta_str}"


class UnifiedLogger:
    """Central unified logging for all uDOS systems."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize unified logger.
        
        Args:
            log_dir: Log directory (default: memory/logs)
        """
        if log_dir is None:
            from core.services.logging_manager import get_repo_root
            log_dir = Path(get_repo_root()) / "memory" / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.entries: list[LogContext] = []
        
        # Setup Python loggers for each source
        self.loggers = {
            source: self._setup_logger(source)
            for source in LogSource
        }
    
    def _setup_logger(self, source: LogSource) -> logging.Logger:
        """Setup Python logger for source."""
        logger_name = f"unified.{source.value.lower()}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # File handler
        handler = logging.FileHandler(
            self.log_dir / f"unified-{source.value.lower()}-{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(category)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log(self, context: LogContext) -> None:
        """Log a structured context entry.
        
        Args:
            context: LogContext instance
        """
        self.entries.append(context)
        
        # Also write to Python logger
        logger = self.loggers[context.source]
        log_level = getattr(logging, context.level.value)
        extra = {"category": context.category}
        logger.log(log_level, context.message, extra=extra)
    
    # Convenience methods for each source
    
    def log_core(
        self,
        category: str,
        message: str,
        level: LogLevel = LogLevel.INFO,
        **metadata
    ) -> None:
        """Log from Core TUI."""
        context = LogContext(LogSource.CORE, category, message, level, **metadata)
        self.log(context)
    
    def log_wizard(
        self,
        category: str,
        message: str,
        level: LogLevel = LogLevel.INFO,
        **metadata
    ) -> None:
        """Log from Wizard Server."""
        context = LogContext(LogSource.WIZARD, category, message, level, **metadata)
        self.log(context)
    
    def log_goblin(
        self,
        category: str,
        message: str,
        level: LogLevel = LogLevel.INFO,
        **metadata
    ) -> None:
        """Log from Goblin Dev Server."""
        context = LogContext(LogSource.GOBLIN, category, message, level, **metadata)
        self.log(context)
    
    def log_extension(
        self,
        category: str,
        message: str,
        level: LogLevel = LogLevel.INFO,
        **metadata
    ) -> None:
        """Log from Extensions."""
        context = LogContext(LogSource.EXTENSION, category, message, level, **metadata)
        self.log(context)
    
    # Querying
    
    def filter(
        self,
        source: Optional[LogSource] = None,
        category: Optional[str] = None,
        level: Optional[LogLevel] = None,
        limit: int = 100
    ) -> list[LogContext]:
        """Filter log entries.
        
        Args:
            source: Filter by source (optional)
            category: Filter by category (optional)
            level: Filter by level (optional)
            limit: Max results
        
        Returns:
            List of matching entries (most recent first)
        """
        results = []
        for entry in reversed(self.entries):
            if source and entry.source != source:
                continue
            if category and entry.category != category:
                continue
            if level and entry.level != level:
                continue
            results.append(entry)
            if len(results) >= limit:
                break
        return results
    
    def view_last(self, count: int = 50, source: Optional[LogSource] = None) -> str:
        """View last N entries.
        
        Args:
            count: Number of entries to show
            source: Optional source filter
        
        Returns:
            Formatted string for display
        """
        entries = self.filter(source=source, limit=count)
        if not entries:
            return "[No log entries]"
        
        lines = ["═" * 80, "UNIFIED LOG VIEW", "═" * 80]
        for entry in reversed(entries):
            lines.append(str(entry))
        lines.append("═" * 80)
        return "\n".join(lines)
    
    def stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        by_source = {}
        by_level = {}
        
        for entry in self.entries:
            source = entry.source.value
            level = entry.level.value
            by_source[source] = by_source.get(source, 0) + 1
            by_level[level] = by_level.get(level, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "by_source": by_source,
            "by_level": by_level,
            "uptime": (datetime.now() - self.entries[0].timestamp).total_seconds() if self.entries else 0
        }
    
    def save_summary(self, filepath: Optional[Path] = None) -> Path:
        """Save log summary to file.
        
        Args:
            filepath: Optional custom filepath
        
        Returns:
            Path to saved file
        """
        if filepath is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            filepath = self.log_dir / f"unified-summary-{date_str}.json"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats(),
            "entries": [e.to_dict() for e in self.entries[-1000:]],  # Last 1000
        }
        
        with open(filepath, "w") as f:
            json.dump(summary, f, indent=2)
        
        return filepath


# Global unified logger instance
_unified_logger: Optional[UnifiedLogger] = None


def get_unified_logger() -> UnifiedLogger:
    """Get global unified logger instance."""
    global _unified_logger
    if _unified_logger is None:
        _unified_logger = UnifiedLogger()
    return _unified_logger
