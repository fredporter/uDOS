"""
Rate Limiter Service
====================

Granular rate limiting for Wizard Server endpoints.
Supports per-device, per-endpoint, and tiered limits.

Rate Limit Tiers:
  - Standard: General API endpoints
  - Expensive: AI/LLM calls (token cost)
  - Heavy: File downloads, web proxy
  - Light: Health checks, status

Alpha v1.0.0.19
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from enum import Enum


class RateLimitTier(Enum):
    """Rate limit tier categories."""

    LIGHT = "light"  # Health, status, ping
    STANDARD = "standard"  # Normal API calls
    HEAVY = "heavy"  # Downloads, large fetches
    EXPENSIVE = "expensive"  # AI/LLM API calls


@dataclass
class TierLimits:
    """Rate limits for a tier."""

    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    cooldown_seconds: float = 1.0  # Minimum time between requests


# Default tier configurations
DEFAULT_TIER_LIMITS: Dict[RateLimitTier, TierLimits] = {
    RateLimitTier.LIGHT: TierLimits(
        requests_per_minute=120,
        requests_per_hour=3600,
        requests_per_day=50000,
        cooldown_seconds=0.1,
    ),
    RateLimitTier.STANDARD: TierLimits(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
        cooldown_seconds=0.5,
    ),
    RateLimitTier.HEAVY: TierLimits(
        requests_per_minute=10,
        requests_per_hour=100,
        requests_per_day=500,
        cooldown_seconds=2.0,
    ),
    RateLimitTier.EXPENSIVE: TierLimits(
        requests_per_minute=5,
        requests_per_hour=50,
        requests_per_day=200,
        cooldown_seconds=5.0,
    ),
}

# Endpoint to tier mapping
ENDPOINT_TIERS: Dict[str, RateLimitTier] = {
    # Light tier (high throughput)
    "/health": RateLimitTier.LIGHT,
    "/api/v1/status": RateLimitTier.LIGHT,
    "/api/v1/ping": RateLimitTier.LIGHT,
    "/api/v1/index": RateLimitTier.LIGHT,
    "/": RateLimitTier.LIGHT,
    "/assets": RateLimitTier.LIGHT,
    # Standard tier
    "/api/v1/plugin/list": RateLimitTier.STANDARD,
    "/api/v1/plugin/{id}": RateLimitTier.STANDARD,
    "/api/v1/plugin/search": RateLimitTier.STANDARD,
    # Heavy tier (bandwidth intensive)
    "/api/v1/plugin/{id}/download": RateLimitTier.HEAVY,
    "/api/v1/web/fetch": RateLimitTier.HEAVY,
    "/api/v1/web/scrape": RateLimitTier.HEAVY,
    "/api/v1/image/convert": RateLimitTier.HEAVY,
    # Expensive tier (cost incurring)
    "/api/v1/ai/complete": RateLimitTier.EXPENSIVE,
    "/api/v1/ai/chat": RateLimitTier.EXPENSIVE,
    "/api/v1/ai/embed": RateLimitTier.EXPENSIVE,
    "/api/v1/gmail/send": RateLimitTier.EXPENSIVE,
}


@dataclass
class RequestRecord:
    """Record of a single request."""

    timestamp: float
    endpoint: str
    tier: RateLimitTier
    device_id: str
    allowed: bool


@dataclass
class DeviceRateLimitState:
    """Rate limit state for a device."""

    device_id: str
    tier_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    last_requests: Dict[str, float] = field(default_factory=dict)
    blocked_until: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        # Initialize counters for each tier
        for tier in RateLimitTier:
            self.tier_counts[tier.value] = {
                "minute": 0,
                "hour": 0,
                "day": 0,
                "window_start_minute": time.time(),
                "window_start_hour": time.time(),
                "window_start_day": time.time(),
            }
            self.last_requests[tier.value] = 0
            self.blocked_until[tier.value] = 0


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    tier: RateLimitTier
    reason: Optional[str] = None
    retry_after_seconds: Optional[float] = None
    current_counts: Optional[Dict[str, int]] = None
    limits: Optional[Dict[str, int]] = None


class RateLimiter:
    """
    Granular rate limiter for Wizard Server.

    Features:
    - Per-device tracking
    - Per-endpoint tier classification
    - Sliding window counters
    - Cooldown enforcement
    - Block/unblock management
    """

    def __init__(
        self,
        tier_limits: Dict[RateLimitTier, TierLimits] = None,
        endpoint_tiers: Dict[str, RateLimitTier] = None,
    ):
        """
        Initialize rate limiter.

        Args:
            tier_limits: Custom tier configurations
            endpoint_tiers: Custom endpoint-to-tier mapping
        """
        self.tier_limits = tier_limits or DEFAULT_TIER_LIMITS
        self.endpoint_tiers = endpoint_tiers or ENDPOINT_TIERS
        self.device_states: Dict[str, DeviceRateLimitState] = {}
        self.request_log: list[RequestRecord] = []
        self.log_max_size = 10000

    def get_tier_for_endpoint(self, endpoint: str) -> RateLimitTier:
        """
        Get rate limit tier for an endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Applicable rate limit tier
        """
        # Exact match
        if endpoint in self.endpoint_tiers:
            return self.endpoint_tiers[endpoint]

        # Pattern match (e.g., /api/v1/plugin/{id} matches /api/v1/plugin/micro)
        for pattern, tier in self.endpoint_tiers.items():
            if "{" in pattern:
                # Simple pattern matching
                pattern_parts = pattern.split("/")
                endpoint_parts = endpoint.split("/")

                if len(pattern_parts) == len(endpoint_parts):
                    match = True
                    for p, e in zip(pattern_parts, endpoint_parts):
                        if p.startswith("{") and p.endswith("}"):
                            continue  # Wildcard
                        if p != e:
                            match = False
                            break
                    if match:
                        return tier

        # Default to standard
        return RateLimitTier.STANDARD

    def get_device_state(self, device_id: str) -> DeviceRateLimitState:
        """Get or create device state."""
        if device_id not in self.device_states:
            self.device_states[device_id] = DeviceRateLimitState(device_id=device_id)
        return self.device_states[device_id]

    def _reset_windows(self, state: DeviceRateLimitState, tier: RateLimitTier):
        """Reset expired time windows."""
        now = time.time()
        counts = state.tier_counts[tier.value]

        # Reset minute window (60 seconds)
        if now - counts["window_start_minute"] >= 60:
            counts["minute"] = 0
            counts["window_start_minute"] = now

        # Reset hour window (3600 seconds)
        if now - counts["window_start_hour"] >= 3600:
            counts["hour"] = 0
            counts["window_start_hour"] = now

        # Reset day window (86400 seconds)
        if now - counts["window_start_day"] >= 86400:
            counts["day"] = 0
            counts["window_start_day"] = now

    def check(self, device_id: str, endpoint: str) -> RateLimitResult:
        """
        Check if request should be allowed.

        Args:
            device_id: Device making the request
            endpoint: API endpoint being accessed

        Returns:
            RateLimitResult with decision and details
        """
        tier = self.get_tier_for_endpoint(endpoint)
        limits = self.tier_limits[tier]
        state = self.get_device_state(device_id)
        now = time.time()

        # Reset expired windows
        self._reset_windows(state, tier)

        counts = state.tier_counts[tier.value]

        # Check if device is blocked
        if state.blocked_until[tier.value] > now:
            retry_after = state.blocked_until[tier.value] - now
            return RateLimitResult(
                allowed=False,
                tier=tier,
                reason=f"Device blocked for {tier.value} tier",
                retry_after_seconds=retry_after,
                current_counts={
                    "minute": counts["minute"],
                    "hour": counts["hour"],
                    "day": counts["day"],
                },
                limits={
                    "minute": limits.requests_per_minute,
                    "hour": limits.requests_per_hour,
                    "day": limits.requests_per_day,
                },
            )

        # Check cooldown
        last_request = state.last_requests[tier.value]
        if now - last_request < limits.cooldown_seconds:
            retry_after = limits.cooldown_seconds - (now - last_request)
            return RateLimitResult(
                allowed=False,
                tier=tier,
                reason=f"Cooldown active ({limits.cooldown_seconds}s between requests)",
                retry_after_seconds=retry_after,
            )

        # Check minute limit
        if counts["minute"] >= limits.requests_per_minute:
            retry_after = 60 - (now - counts["window_start_minute"])
            return RateLimitResult(
                allowed=False,
                tier=tier,
                reason=f"Minute limit exceeded ({limits.requests_per_minute}/min)",
                retry_after_seconds=max(0, retry_after),
                current_counts={"minute": counts["minute"]},
                limits={"minute": limits.requests_per_minute},
            )

        # Check hour limit
        if counts["hour"] >= limits.requests_per_hour:
            retry_after = 3600 - (now - counts["window_start_hour"])
            return RateLimitResult(
                allowed=False,
                tier=tier,
                reason=f"Hour limit exceeded ({limits.requests_per_hour}/hr)",
                retry_after_seconds=max(0, retry_after),
                current_counts={"hour": counts["hour"]},
                limits={"hour": limits.requests_per_hour},
            )

        # Check day limit
        if counts["day"] >= limits.requests_per_day:
            retry_after = 86400 - (now - counts["window_start_day"])
            return RateLimitResult(
                allowed=False,
                tier=tier,
                reason=f"Daily limit exceeded ({limits.requests_per_day}/day)",
                retry_after_seconds=max(0, retry_after),
                current_counts={"day": counts["day"]},
                limits={"day": limits.requests_per_day},
            )

        # Request allowed
        return RateLimitResult(
            allowed=True,
            tier=tier,
            current_counts={
                "minute": counts["minute"],
                "hour": counts["hour"],
                "day": counts["day"],
            },
            limits={
                "minute": limits.requests_per_minute,
                "hour": limits.requests_per_hour,
                "day": limits.requests_per_day,
            },
        )

    def record(self, device_id: str, endpoint: str, allowed: bool = True):
        """
        Record a request (call after allowing).

        Args:
            device_id: Device making the request
            endpoint: API endpoint accessed
            allowed: Whether request was allowed
        """
        tier = self.get_tier_for_endpoint(endpoint)
        state = self.get_device_state(device_id)
        now = time.time()

        if allowed:
            # Update counters
            counts = state.tier_counts[tier.value]
            counts["minute"] += 1
            counts["hour"] += 1
            counts["day"] += 1
            state.last_requests[tier.value] = now

        # Log request
        record = RequestRecord(
            timestamp=now,
            endpoint=endpoint,
            tier=tier,
            device_id=device_id,
            allowed=allowed,
        )
        self.request_log.append(record)

        # Trim log if too large
        if len(self.request_log) > self.log_max_size:
            self.request_log = self.request_log[-self.log_max_size // 2 :]

    def block_device(
        self, device_id: str, tier: RateLimitTier, duration_seconds: float
    ):
        """
        Block a device for a specific tier.

        Args:
            device_id: Device to block
            tier: Tier to block
            duration_seconds: Block duration
        """
        state = self.get_device_state(device_id)
        state.blocked_until[tier.value] = time.time() + duration_seconds

    def unblock_device(self, device_id: str, tier: RateLimitTier = None):
        """
        Unblock a device.

        Args:
            device_id: Device to unblock
            tier: Specific tier to unblock (None = all tiers)
        """
        state = self.get_device_state(device_id)

        if tier:
            state.blocked_until[tier.value] = 0
        else:
            for t in RateLimitTier:
                state.blocked_until[t.value] = 0

    def get_device_stats(self, device_id: str) -> Dict[str, Any]:
        """
        Get rate limit statistics for a device.

        Args:
            device_id: Device to query

        Returns:
            Statistics dictionary
        """
        state = self.get_device_state(device_id)
        now = time.time()

        stats = {
            "device_id": device_id,
            "tiers": {},
        }

        for tier in RateLimitTier:
            limits = self.tier_limits[tier]
            counts = state.tier_counts[tier.value]
            blocked_until = state.blocked_until[tier.value]

            stats["tiers"][tier.value] = {
                "counts": {
                    "minute": counts["minute"],
                    "hour": counts["hour"],
                    "day": counts["day"],
                },
                "limits": {
                    "minute": limits.requests_per_minute,
                    "hour": limits.requests_per_hour,
                    "day": limits.requests_per_day,
                },
                "remaining": {
                    "minute": max(0, limits.requests_per_minute - counts["minute"]),
                    "hour": max(0, limits.requests_per_hour - counts["hour"]),
                    "day": max(0, limits.requests_per_day - counts["day"]),
                },
                "blocked": blocked_until > now,
                "blocked_seconds_remaining": (
                    max(0, blocked_until - now) if blocked_until > now else 0
                ),
            }

        return stats

    def get_global_stats(self) -> Dict[str, Any]:
        """Get global rate limiter statistics."""
        now = time.time()

        # Count recent requests
        minute_ago = now - 60
        hour_ago = now - 3600

        recent_minute = sum(1 for r in self.request_log if r.timestamp >= minute_ago)
        recent_hour = sum(1 for r in self.request_log if r.timestamp >= hour_ago)
        blocked_minute = sum(
            1 for r in self.request_log if r.timestamp >= minute_ago and not r.allowed
        )

        # Tier breakdown
        tier_breakdown = defaultdict(int)
        for r in self.request_log:
            if r.timestamp >= minute_ago:
                tier_breakdown[r.tier.value] += 1

        return {
            "active_devices": len(self.device_states),
            "requests_last_minute": recent_minute,
            "requests_last_hour": recent_hour,
            "blocked_last_minute": blocked_minute,
            "tier_breakdown": dict(tier_breakdown),
            "log_size": len(self.request_log),
        }


# Singleton instance for server use
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# FastAPI middleware integration
def create_rate_limit_middleware(rate_limiter: RateLimiter = None):
    """
    Create FastAPI middleware for rate limiting.

    Usage:
        app.middleware("http")(create_rate_limit_middleware())
    """
    limiter = rate_limiter or get_rate_limiter()

    async def rate_limit_middleware(request, call_next):
        # Extract device ID from auth header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            device_id = token.split(":")[0] if ":" in token else token[:16]
        else:
            device_id = request.client.host if request.client else "anonymous"

        endpoint = request.url.path

        # Check rate limit
        result = limiter.check(device_id, endpoint)

        if not result.allowed:
            # Return 429 Too Many Requests
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": result.reason,
                    "tier": result.tier.value,
                    "retry_after_seconds": result.retry_after_seconds,
                },
                headers={
                    "Retry-After": str(int(result.retry_after_seconds or 60)),
                    "X-RateLimit-Tier": result.tier.value,
                },
            )

        # Record the request and proceed
        response = await call_next(request)
        limiter.record(device_id, endpoint, allowed=True)

        # Add rate limit headers
        if result.limits:
            response.headers["X-RateLimit-Limit-Minute"] = str(
                result.limits.get("minute", 0)
            )
            response.headers["X-RateLimit-Remaining-Minute"] = str(
                max(
                    0,
                    result.limits.get("minute", 0)
                    - result.current_counts.get("minute", 0)
                    - 1,
                )
            )
            response.headers["X-RateLimit-Tier"] = result.tier.value

        return response

    return rate_limit_middleware


__all__ = [
    "RateLimiter",
    "RateLimitResult",
    "RateLimitTier",
    "TierLimits",
    "get_rate_limiter",
    "create_rate_limit_middleware",
    "DEFAULT_TIER_LIMITS",
    "ENDPOINT_TIERS",
]
