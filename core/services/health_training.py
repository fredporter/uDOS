"""
Health training log helpers
===========================

Provides helpers for reading the Self-Healer + Hot Reload summaries written to
`memory/logs/health-training.log` so automation and startup scripts can decide when
to rerun diagnostics.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from core.services.logging_service import get_logger, get_repo_root

logger = get_logger("health-training")


def get_health_log_path() -> Path:
    """Return the canonical health training log path."""
    return get_repo_root() / "memory" / "logs" / "health-training.log"


def read_last_summary() -> Optional[Dict[str, Any]]:
    """Return the last health training summary payload."""
    log_path = get_health_log_path()
    if not log_path.exists():
        return None
    try:
        with open(log_path, "r") as log_file:
            lines = [line.strip() for line in log_file if line.strip()]
        if not lines:
            return None
        payload = json.loads(lines[-1])
        return payload
    except Exception as exc:
        logger.warning(f"[HealthLog] Could not read summary: {exc}")
        return None


def needs_self_heal_training(min_remaining: int = 1) -> bool:
    """Return True if the last summary reported >= min_remaining issues."""
    summary = read_last_summary()
    if not summary:
        return False
    remaining = summary.get("self_heal", {}).get("remaining")
    if remaining is None:
        return False
    return remaining >= min_remaining
