"""Helpers for guarding Wizard API calls with the shared rate limiter."""

import os
from typing import Dict, Optional, Any

from core.services.provider_registry import (
    get_provider,
    ProviderType,
    ProviderNotAvailableError,
)

_DEVICE_ID = f"core-cli-{os.getpid()}"


def _get_rate_limiter() -> Optional[Any]:
    try:
        return get_provider(ProviderType.RATE_LIMITER)
    except ProviderNotAvailableError:
        return None


def _get_load_logger() -> Optional[Any]:
    try:
        return get_provider(ProviderType.PROVIDER_LOAD_LOGGER)
    except ProviderNotAvailableError:
        return None


def _log_throttle(endpoint: str, result: Optional[Any]) -> None:
    if not result:
        return
    logger = _get_load_logger()
    if not logger:
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
    if callable(logger):
        logger("wizard-api", "throttle", reason, source="rate-limiter", metadata=metadata)


def guard_wizard_endpoint(endpoint: str) -> Optional[Dict[str, Any]]:
    """Guard a Wizard endpoint; return an error payload on throttling."""
    limiter = _get_rate_limiter()
    if not limiter:
        return None
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
