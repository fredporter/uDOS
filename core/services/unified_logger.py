"""
Unified Logging System v1.2.1 - Minimal/Abbreviated Format

Single location for all system-wide logs in memory/logs/ with flat structure.
Minimal format for efficiency, integrated with DEV MODE for debugging uPY scripts.

Log Files:
- system.log      - System startup, shutdown, core operations (abbrev: SYS)
- api.log         - API calls, rate limiting, costs (abbrev: API)
- performance.log - Response times, query rates, metrics (abbrev: PERF)
- debug.log       - DEV MODE debugging, uPY script traces (abbrev: DBG)
- error.log       - All errors, exceptions, failures (abbrev: ERR)
- command.log     - Command execution history (abbrev: CMD)

Format: [TIMESTAMP][CAT][LVL] Message
Example: [2025-12-03 14:23:45][SYS][I] uDOS started
         [2025-12-03 14:23:46][API][D] Gemini call: 0.001s, $0.0001
         [2025-12-03 14:23:47][PERF][I] Query: offline, 0.2s
         [2025-12-03 14:23:48][DBG][D] water_quest.upy:42 - HP=85

Levels (single char):
- D = Debug
- I = Info
- W = Warning
- E = Error
- C = Critical

Version: 1.2.1
Author: uDOS Development Team
Date: 2025-12-03
"""

import logging
from pathlib import Path
from datetime import datetime, UTC
from typing import Optional, Dict, Any
import json


class MinimalFormatter(logging.Formatter):
    """Minimal/abbreviated log formatter."""

    # Category abbreviations
    CATEGORIES = {
        'system': 'SYS',
        'api': 'API',
        'performance': 'PERF',
        'debug': 'DBG',
        'error': 'ERR',
        'command': 'CMD'
    }

    # Level abbreviations
    LEVELS = {
        'DEBUG': 'D',
        'INFO': 'I',
        'WARNING': 'W',
        'ERROR': 'E',
        'CRITICAL': 'C'
    }

    def __init__(self, category: str):
        """Initialize formatter with category.

        Args:
            category: Log category (system, api, performance, etc.)
        """
        super().__init__()
        self.category_abbrev = self.CATEGORIES.get(category, category[:4].upper())

    def format(self, record: logging.LogRecord) -> str:
        """Format log record in minimal style.

        Args:
            record: Log record to format

        Returns:
            Formatted log string
        """
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level_abbrev = self.LEVELS.get(record.levelname, record.levelname[0])
        message = record.getMessage()

        # Add context if available (for debugging)
        if hasattr(record, 'context') and record.context:
            context_str = ' '.join(f"{k}={v}" for k, v in record.context.items())
            message = f"{message} [{context_str}]"

        return f"[{timestamp}][{self.category_abbrev}][{level_abbrev}] {message}"


class UnifiedLogger:
    """Centralized logging system with minimal format."""

    def __init__(self, log_dir: str = "memory/logs"):
        """Initialize unified logger.

        Args:
            log_dir: Base directory for all logs (memory/logs)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.loggers: Dict[str, logging.Logger] = {}

        # Performance tracking (in-memory)
        self.performance_metrics = {
            'total_queries': 0,
            'offline_queries': 0,
            'online_queries': 0,
            'total_cost': 0.0,
            'total_time': 0.0,
            'query_times': []  # Last 100 queries
        }

    def get_logger(self, category: str, level: int = logging.INFO) -> logging.Logger:
        """Get or create logger for category.

        Args:
            category: Log category (system, api, performance, debug, error, command)
            level: Logging level (default: INFO, use DEBUG for dev mode)

        Returns:
            Configured logger instance
        """
        if category in self.loggers:
            return self.loggers[category]

        # Create logger
        logger = logging.getLogger(f"uDOS.{category}")
        logger.setLevel(level)
        logger.propagate = False  # Don't propagate to root

        # Clear any existing handlers
        logger.handlers.clear()

        # Add file handler
        log_file = self.log_dir / f"{category}.log"
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(MinimalFormatter(category))
        logger.addHandler(file_handler)

        # For error logs, also write to error.log
        if category != 'error':
            error_handler = logging.FileHandler(self.log_dir / "error.log", mode='a', encoding='utf-8')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(MinimalFormatter('error'))
            logger.addHandler(error_handler)

        self.loggers[category] = logger
        return logger

    def log_system(self, message: str, level: str = 'info', **context):
        """Log system message.

        Args:
            message: Log message
            level: Log level (debug, info, warning, error, critical)
            **context: Additional context fields
        """
        logger = self.get_logger('system')
        getattr(logger, level)(message, extra={'context': context})

    def log_api(self, service: str, duration: float, cost: float, success: bool = True, **context):
        """Log API call.

        Args:
            service: API service name (gemini, banana, etc.)
            duration: Call duration in seconds
            cost: Call cost in USD
            success: Whether call succeeded
            **context: Additional context
        """
        logger = self.get_logger('api')
        status = 'OK' if success else 'FAIL'
        logger.info(f"{service}: {duration:.3f}s, ${cost:.4f}, {status}", extra={'context': context})

    def log_performance(self, query_type: str, duration: float, offline: bool, **context):
        """Log performance metrics.

        Args:
            query_type: Type of query (generate, guide, svg, etc.)
            duration: Query duration in seconds
            offline: Whether query was handled offline
            **context: Additional context
        """
        logger = self.get_logger('performance')
        mode = 'offline' if offline else 'online'
        logger.info(f"{query_type}: {mode}, {duration:.3f}s", extra={'context': context})

        # Update in-memory metrics
        self.performance_metrics['total_queries'] += 1
        if offline:
            self.performance_metrics['offline_queries'] += 1
        else:
            self.performance_metrics['online_queries'] += 1
        self.performance_metrics['total_time'] += duration

        # Keep last 100 query times
        self.performance_metrics['query_times'].append(duration)
        if len(self.performance_metrics['query_times']) > 100:
            self.performance_metrics['query_times'].pop(0)

    def log_debug(self, message: str, script: Optional[str] = None, line: Optional[int] = None, **context):
        """Log debug message (DEV MODE).

        Args:
            message: Debug message
            script: Script name (for uPY debugging)
            line: Line number (for uPY debugging)
            **context: Additional context (variables, state, etc.)
        """
        logger = self.get_logger('debug', level=logging.DEBUG)
        if script and line:
            logger.debug(f"{script}:{line} - {message}", extra={'context': context})
        else:
            logger.debug(message, extra={'context': context})

    def log_error(self, message: str, exception: Optional[Exception] = None, **context):
        """Log error message.

        Args:
            message: Error message
            exception: Exception object (if any)
            **context: Additional context
        """
        logger = self.get_logger('error')
        if exception:
            logger.error(f"{message}: {type(exception).__name__}: {str(exception)}",
                        extra={'context': context}, exc_info=True)
        else:
            logger.error(message, extra={'context': context})

    def log_command(self, command: str, params: list, result: str, duration: float, **context):
        """Log command execution.

        Args:
            command: Command name
            params: Command parameters
            result: Result status (success, error, etc.)
            duration: Execution duration
            **context: Additional context
        """
        logger = self.get_logger('command')
        params_str = ' '.join(str(p) for p in params) if params else ''
        logger.info(f"{command} {params_str}: {result}, {duration:.3f}s", extra={'context': context})

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics.

        Returns:
            Dictionary with performance metrics
        """
        metrics = self.performance_metrics.copy()

        # Calculate derived metrics
        if metrics['total_queries'] > 0:
            metrics['offline_rate'] = metrics['offline_queries'] / metrics['total_queries']
            metrics['avg_time'] = metrics['total_time'] / metrics['total_queries']
        else:
            metrics['offline_rate'] = 0.0
            metrics['avg_time'] = 0.0

        # Calculate percentiles from last 100 queries
        if metrics['query_times']:
            sorted_times = sorted(metrics['query_times'])
            n = len(sorted_times)
            metrics['p50_time'] = sorted_times[n // 2]
            metrics['p95_time'] = sorted_times[int(n * 0.95)]
            metrics['p99_time'] = sorted_times[int(n * 0.99)]
        else:
            metrics['p50_time'] = 0.0
            metrics['p95_time'] = 0.0
            metrics['p99_time'] = 0.0

        return metrics

    def save_performance_snapshot(self):
        """Save performance metrics snapshot to file."""
        metrics = self.get_performance_metrics()
        metrics['timestamp'] = datetime.now(UTC).isoformat()

        snapshot_file = self.log_dir / f"performance-snapshot-{datetime.now().strftime('%Y%m%d')}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(metrics, f, indent=2)

    def clear_old_logs(self, days: int = 30):
        """Clear log files older than specified days.

        Args:
            days: Number of days to keep (default: 30)
        """
        cutoff = datetime.now(UTC).timestamp() - (days * 24 * 60 * 60)

        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
                self.log_system(f"Deleted old log: {log_file.name}", level='info')


# Singleton instance
_unified_logger = None


def get_unified_logger() -> UnifiedLogger:
    """Get singleton unified logger instance.

    Returns:
        UnifiedLogger instance
    """
    global _unified_logger
    if _unified_logger is None:
        _unified_logger = UnifiedLogger()
    return _unified_logger


# Convenience functions
def log_system(message: str, level: str = 'info', **context):
    """Log system message."""
    get_unified_logger().log_system(message, level, **context)


def log_api(service: str, duration: float, cost: float, success: bool = True, **context):
    """Log API call."""
    get_unified_logger().log_api(service, duration, cost, success, **context)


def log_performance(query_type: str, duration: float, offline: bool, **context):
    """Log performance metrics."""
    get_unified_logger().log_performance(query_type, duration, offline, **context)


def log_debug(message: str, script: Optional[str] = None, line: Optional[int] = None, **context):
    """Log debug message."""
    get_unified_logger().log_debug(message, script, line, **context)


def log_error(message: str, exception: Optional[Exception] = None, **context):
    """Log error message."""
    get_unified_logger().log_error(message, exception, **context)


def log_command(command: str, params: list, result: str, duration: float, **context):
    """Log command execution."""
    get_unified_logger().log_command(command, params, result, duration, **context)
