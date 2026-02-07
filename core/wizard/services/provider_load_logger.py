"""Helper for recording provider load and throttle events."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from core.services.logging_api import get_repo_root, get_logger

logger = get_logger("wizard", category="provider-load", name="provider-load")


def _ensure_log_path() -> Path:
    repo = get_repo_root()
    log_dir = repo / "memory" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "provider-load.log"


def log_provider_event(
    provider: str,
    event_type: str,
    details: Optional[Dict] = None,
    extra: Optional[str] = None,
) -> None:
    """Append a provider load event to provider-load.log."""
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "provider": provider,
        "event": event_type,
        "details": details or {},
    }
    if extra:
        payload["extra"] = extra
    try:
        log_path = _ensure_log_path()
        with open(log_path, "a") as handle:
            handle.write(json.dumps(payload) + "\n")
        logger.debug("[ProviderLoad] %s %s", provider, event_type)
    except Exception as exc:
        logger.warning("[ProviderLoad] Failed to log event: %s", exc)


def read_recent_provider_events(limit: int = 10) -> List[Dict]:
    """Return the most recent provider load entries."""
    log_path = _ensure_log_path()
    if not log_path.exists():
        return []

    try:
        with open(log_path, "r") as handle:
            lines = [line.strip() for line in handle if line.strip()]
        recent = lines[-limit:]
        return [json.loads(line) for line in recent]
    except Exception as exc:
        logger.warning("[ProviderLoad] Failed to read events: %s", exc)
        return []


def log_throttle_event(provider: str, endpoint: str, limit: int, usage: int) -> None:
    """Log a throttle/limiting action for gating automation."""
    log_provider_event(
        provider,
        "throttle",
        {
            "endpoint": endpoint,
            "limit": limit,
            "usage": usage,
        },
    )
