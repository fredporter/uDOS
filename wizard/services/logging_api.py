"""Wizard logging API wrapper (v1.3)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from wizard.services.path_utils import get_logs_dir

from core.services import logging_api as core_logging
from core.services.logging_api import (  # noqa: F401
    LOG_SCHEMA_ID,
    LogConfig,
    Logger,
    get_log_manager,
    new_corr_id,
)


def get_logger(
    component: str,
    category: str = "general",
    name: Optional[str] = None,
    ctx: Optional[Dict[str, Any]] = None,
    corr_id: Optional[str] = None,
) -> Logger:
    """Wizard-biased logger wrapper for v1.3 logging."""
    known_components = {"core", "wizard", "script", "goblin", "extension"}
    if component not in known_components and category == "general" and name is None:
        category = component
        component = "wizard"
    return core_logging.get_logger(
        component=component,
        category=category,
        name=name,
        ctx=ctx,
        corr_id=corr_id,
    )


def get_logs_root() -> Path:
    """Return memory/logs/udos root."""
    root = get_logs_dir() / "udos"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_log_stats() -> Dict[str, Any]:
    """Basic stats for v1.3 JSONL logs."""
    root = get_logs_root()
    stats: Dict[str, Any] = {
        "total_files": 0,
        "total_size_mb": 0,
        "by_component": {},
    }

    for path in root.rglob("*.jsonl"):
        stats["total_files"] += 1
        size_bytes = path.stat().st_size
        stats["total_size_mb"] += size_bytes / (1024 * 1024)
        component = path.parent.name
        if component not in stats["by_component"]:
            stats["by_component"][component] = {"count": 0, "size_mb": 0}
        stats["by_component"][component]["count"] += 1
        stats["by_component"][component]["size_mb"] += size_bytes / (1024 * 1024)

    stats["total_size_mb"] = round(stats["total_size_mb"], 2)
    for comp in stats["by_component"].values():
        comp["size_mb"] = round(comp["size_mb"], 2)

    return stats
