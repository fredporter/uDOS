"""Helpers for guarding Wizard API calls with the shared rate limiter."""

import os
from typing import Dict, Optional, Any

try:
    from wizard.services.rate_limiter import get_rate_limiter
    from wizard.services.rate_limiter import RateLimitResult
except ImportError:  # pragma: no cover - guard for missing wizard server
    get_rate_limiter = None
    RateLimitResult = None

try:
    from wizard.services.provider_load_logger import log_provider_event
except ImportError:
    log_provider_event = None

_DEVICE_ID = f"core-cli-{os.getpid()}"


def _log_throttle(endpoint: str, result: Optional[Any]) -> None:
    if not log_provider_event or not result:
        return
    reason = result.reason or "rate_limit_exceeded"
    metadata = {
        "endpoint": endpoint,
        "counts": getattr(result, "current_counts", {}),
        "limits": getattr(result, "limits", {}),
        "tier": getattr(result, "tier", None).value
        if getattr(result, "tier", None)
        else None,
    }
    log_provider_event("wizard-api", "throttle", reason, source="rate-limiter", metadata=metadata)


def guard_wizard_endpoint(endpoint: str) -> Optional[Dict[str, Any]]:
    """Guard a Wizard endpoint; return an error payload on throttling."""
    if not get_rate_limiter:
        return None
    limiter = get_rate_limiter()
    result = limiter.check(_DEVICE_ID, endpoint)
    if result.allowed:
        limiter.record(_DEVICE_ID, endpoint, allowed=True)
        return None
    _log_throttle(endpoint, result)
    retry_after = int(result.retry_after_seconds or 5)
    reason = result.reason or "rate limit"
    return {
        "status": "throttled",
        "message": f"Rate limit reached for {endpoint} ({reason})",
        "hint": f"Retry after ~{retry_after} seconds.",
        "retry_after_seconds": retry_after,
    }
