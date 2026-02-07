"""
Health training log helpers
===========================

Provides helpers for reading the Self-Healer + Hot Reload summaries written to
`memory/logs/health-training.log` so automation and startup scripts can decide when
to rerun diagnostics.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from core.services.logging_api import get_logger, get_repo_root

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


def append_training_entry(entry: Dict[str, Any]) -> None:
    """Append a structured entry to the health-training log."""
    log_path = get_health_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    try:
        with open(log_path, "a") as log_file:
            log_file.write(json.dumps(entry) + "\n")
    except Exception as exc:
        logger.warning(f"[HealthLog] Failed to append entry: {exc}")


def _extract_result_field(result: Any, field: str) -> Any:
    """Helper to read a field from InstallResult or dict-like payloads."""
    if hasattr(result, field):
        return getattr(result, field)
    if isinstance(result, dict):
        return result.get(field)
    return None


def log_plugin_install_event(
    plugin_name: str,
    source: str,
    result: Any,
    manifest: Optional[Dict[str, Any]] = None,
    validation: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record plugin install attempts in the health-training log."""
    payload = {
        "event": "plugin_install",
        "plugin": plugin_name,
        "source": source,
        "result": {
            "success": _extract_result_field(result, "success"),
            "action": _extract_result_field(result, "action"),
            "message": _extract_result_field(result, "message"),
            "error": _extract_result_field(result, "error"),
        },
        "manifest": manifest or {},
        "validation": validation or {},
        "metadata": metadata or {},
    }
    append_training_entry(payload)


def read_last_todo_reminder() -> Optional[Dict[str, Any]]:
    """Return the most recent todo reminder entry stored in the health log."""
    log_path = get_health_log_path()
    if not log_path.exists():
        return None
    try:
        with open(log_path, "r") as log_file:
            lines = [line.strip() for line in log_file if line.strip()]
    except Exception as exc:
        logger.warning(f"[HealthLog] Could not read reminders: {exc}")
        return None

    for line in reversed(lines):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("event") == "todo_reminder":
            return payload
    return None
