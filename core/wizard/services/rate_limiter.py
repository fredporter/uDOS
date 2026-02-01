"""Rate limiting helpers for Wizard API endpoints."""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict

from core.services.logging_service import get_logger
from wizard.services.provider_load_logger import log_throttle_event

logger = get_logger("wizard-rate-limiter", source="wizard")


@dataclass
class _EndpointState:
    limit: int
    window_secs: int
    count: int = 0
    start: datetime = field(default_factory=datetime.utcnow)

    def increment(self) -> int:
        now = datetime.utcnow()
        if (now - self.start).total_seconds() >= self.window_secs:
            self.start = now
            self.count = 0
        self.count += 1
        return self.count


class RateLimiter:
    def __init__(self, default_limit: int = 10, default_window: int = 60):
        self.default_limit = default_limit
        self.default_window = default_window
        self._states: Dict[str, _EndpointState] = {}
        self._lock = threading.Lock()

    def allow(self, endpoint: str, provider: str = "wizard-api") -> bool:
        """Return True when the endpoint is allowed, False when throttled."""
        with self._lock:
            if endpoint not in self._states:
                self._states[endpoint] = _EndpointState(self.default_limit, self.default_window)
            state = self._states[endpoint]
            usage = state.increment()
            if usage > state.limit:
                log_throttle_event(provider, endpoint, limit=state.limit, usage=usage)
                logger.warning(
                    "[RateLimiter] Throttled %s (%s/%s calls in %ss)",
                    endpoint,
                    usage,
                    state.limit,
                    state.window_secs,
                )
                return False
            return True


rate_limiter = RateLimiter()
