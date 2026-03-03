"""Wizard logging API wrapper (v1.3)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from core.services import logging_api as core_logging
from core.services.logging_api import LOG_SCHEMA_ID
from core.services.logging_api import LOG_RUNTIME_VERSION
from core.services.logging_api import LogConfig
from core.services.logging_api import Logger
from core.services.logging_api import get_log_manager
from core.services.logging_api import get_log_stats as core_get_log_stats
from core.services.logging_api import get_logging_health as core_get_logging_health
from core.services.logging_api import get_logs_root as core_get_logs_root
from core.services.logging_api import new_corr_id


def get_logger(
    component: str,
    category: str = "general",
    name: Optional[str] = None,
    ctx: Optional[Dict[str, Any]] = None,
    corr_id: Optional[str] = None,
) -> Logger:
    """Wizard-biased logger wrapper for v1.3 logging."""
    return core_logging.get_logger(
        component=component,
        category=category,
        name=name,
        ctx=ctx,
        corr_id=corr_id,
        default_component="wizard",
    )


def get_logs_root() -> Path:
    """Return memory/logs/udos root."""
    return core_get_logs_root()


def get_log_stats() -> Dict[str, Any]:
    """Basic stats for v1.5 JSONL logs."""
    return core_get_log_stats(get_logs_root())


def get_logging_health() -> Dict[str, Any]:
    health = core_get_logging_health()
    health["schema"] = LOG_SCHEMA_ID
    health["runtime_version"] = LOG_RUNTIME_VERSION
    return health
