"""
API Quota Tracker
=================

Tracks API usage, costs, and rate limits across all connected services.
Integrates with workflow system for request prioritization.

Features:
- Per-provider quota tracking
- Daily/monthly budgets with rollover
- Rate limit handling
- Cost estimation
- Dashboard statistics
- Workflow integration for queued requests

Version: 1.0.0
Alpha: v1.0.2.1+
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

from wizard.services.logging_manager import get_logger
from wizard.services.provider_load_logger import log_provider_event

logger = get_logger("quota-tracker")


class APIProvider(Enum):
    """API providers with quotas."""

    # AI Providers
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    MISTRAL = "mistral"
    DEVSTRAL = "devstral"

    # OAuth Providers with APIs
    GOOGLE = "google"
    GITHUB = "github"
    SPOTIFY = "spotify"
    DISCORD = "discord"
    NOTION = "notion"

    # Local/Free
    OFFLINE = "offline"
    VIBE_CLI = "vibe_cli"


class QuotaStatus(Enum):
    """Quota status states."""

    OK = "ok"
    WARNING = "warning"  # >80% used
    CRITICAL = "critical"  # >95% used
    EXCEEDED = "exceeded"
    RATE_LIMITED = "rate_limited"


class RequestPriority(Enum):
    """Priority levels for queued requests."""

    CRITICAL = 1  # Must complete (user-initiated)
    HIGH = 2  # Important (workflow objectives)
    NORMAL = 3  # Standard (background tasks)
    LOW = 4  # Can wait (prefetch, cache)
    BATCH = 5  # Bulk operations (lowest priority)


@dataclass
class ProviderQuota:
    """Quota configuration for a provider."""

    provider: APIProvider

    # Request limits
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    requests_per_month: int = 10000

    # Token/unit limits (for AI providers)
    tokens_per_minute: int = 100000
    tokens_per_day: int = 1000000
    tokens_per_month: int = 10000000

    # Cost limits (USD)
    daily_budget: float = 5.0
    monthly_budget: float = 50.0

    # Cost per unit (for estimation)
    cost_per_1k_tokens_input: float = 0.0
    cost_per_1k_tokens_output: float = 0.0
    cost_per_request: float = 0.0

    # Current usage
    requests_today: int = 0
    requests_this_month: int = 0
    tokens_today: int = 0
    tokens_this_month: int = 0
    cost_today: float = 0.0
    cost_this_month: float = 0.0

    # Rate limiting
    last_request_time: float = 0.0
    requests_this_minute: int = 0
    minute_window_start: float = 0.0

    # Tracking
    last_daily_reset: str = ""
    last_monthly_reset: str = ""
    total_requests: int = 0
    total_cost: float = 0.0

    @property
    def status(self) -> QuotaStatus:
        """Get current quota status."""
        # Check rate limit
        if self.requests_this_minute >= self.requests_per_minute:
            return QuotaStatus.RATE_LIMITED

        # Check daily limits
        daily_request_pct = (self.requests_today / max(self.requests_per_day, 1)) * 100
        daily_cost_pct = (self.cost_today / max(self.daily_budget, 0.01)) * 100

        max_pct = max(daily_request_pct, daily_cost_pct)

        if max_pct >= 100:
            return QuotaStatus.EXCEEDED
        elif max_pct >= 95:
            return QuotaStatus.CRITICAL
        elif max_pct >= 80:
            return QuotaStatus.WARNING
        return QuotaStatus.OK

    @property
    def daily_usage_percent(self) -> float:
        """Get daily usage as percentage."""
        request_pct = (self.requests_today / max(self.requests_per_day, 1)) * 100
        cost_pct = (self.cost_today / max(self.daily_budget, 0.01)) * 100
        return max(request_pct, cost_pct)

    @property
    def monthly_usage_percent(self) -> float:
        """Get monthly usage as percentage."""
        request_pct = (self.requests_this_month / max(self.requests_per_month, 1)) * 100
        cost_pct = (self.cost_this_month / max(self.monthly_budget, 0.01)) * 100
        return max(request_pct, cost_pct)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "requests_per_minute": self.requests_per_minute,
            "requests_per_day": self.requests_per_day,
            "requests_per_month": self.requests_per_month,
            "tokens_per_minute": self.tokens_per_minute,
            "tokens_per_day": self.tokens_per_day,
            "tokens_per_month": self.tokens_per_month,
            "daily_budget": self.daily_budget,
            "monthly_budget": self.monthly_budget,
            "cost_per_1k_tokens_input": self.cost_per_1k_tokens_input,
            "cost_per_1k_tokens_output": self.cost_per_1k_tokens_output,
            "cost_per_request": self.cost_per_request,
            "requests_today": self.requests_today,
            "requests_this_month": self.requests_this_month,
            "tokens_today": self.tokens_today,
            "tokens_this_month": self.tokens_this_month,
            "cost_today": self.cost_today,
            "cost_this_month": self.cost_this_month,
            "last_daily_reset": self.last_daily_reset,
            "last_monthly_reset": self.last_monthly_reset,
            "total_requests": self.total_requests,
            "total_cost": self.total_cost,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderQuota":
        """Create from dictionary."""
        return cls(
            provider=APIProvider(data["provider"]),
            requests_per_minute=data.get("requests_per_minute", 60),
            requests_per_day=data.get("requests_per_day", 1000),
            requests_per_month=data.get("requests_per_month", 10000),
            tokens_per_minute=data.get("tokens_per_minute", 100000),
            tokens_per_day=data.get("tokens_per_day", 1000000),
            tokens_per_month=data.get("tokens_per_month", 10000000),
            daily_budget=data.get("daily_budget", 5.0),
            monthly_budget=data.get("monthly_budget", 50.0),
            cost_per_1k_tokens_input=data.get("cost_per_1k_tokens_input", 0.0),
            cost_per_1k_tokens_output=data.get("cost_per_1k_tokens_output", 0.0),
            cost_per_request=data.get("cost_per_request", 0.0),
            requests_today=data.get("requests_today", 0),
            requests_this_month=data.get("requests_this_month", 0),
            tokens_today=data.get("tokens_today", 0),
            tokens_this_month=data.get("tokens_this_month", 0),
            cost_today=data.get("cost_today", 0.0),
            cost_this_month=data.get("cost_this_month", 0.0),
            last_daily_reset=data.get("last_daily_reset", ""),
            last_monthly_reset=data.get("last_monthly_reset", ""),
            total_requests=data.get("total_requests", 0),
            total_cost=data.get("total_cost", 0.0),
        )


@dataclass
class QueuedRequest:
    """A queued API request."""

    id: str
    provider: APIProvider
    priority: RequestPriority

    # Request details
    endpoint: str = ""
    method: str = "POST"
    payload: Dict[str, Any] = field(default_factory=dict)

    # Estimation
    estimated_tokens: int = 0
    estimated_cost: float = 0.0

    # Workflow integration
    workflow_id: Optional[str] = None
    objective_id: Optional[str] = None

    # Scheduling
    created_at: float = field(default_factory=time.time)
    scheduled_for: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3

    # Result
    status: str = "pending"  # pending, processing, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None


# Default provider configurations
DEFAULT_QUOTAS = {
    APIProvider.GEMINI: {
        "requests_per_minute": 60,
        "requests_per_day": 1500,
        "tokens_per_minute": 60000,
        "daily_budget": 5.0,
        "monthly_budget": 50.0,
        "cost_per_1k_tokens_input": 0.00025,
        "cost_per_1k_tokens_output": 0.001,
    },
    APIProvider.ANTHROPIC: {
        "requests_per_minute": 50,
        "requests_per_day": 1000,
        "tokens_per_minute": 100000,
        "daily_budget": 10.0,
        "monthly_budget": 100.0,
        "cost_per_1k_tokens_input": 0.003,
        "cost_per_1k_tokens_output": 0.015,
    },
    APIProvider.OPENAI: {
        "requests_per_minute": 60,
        "requests_per_day": 1000,
        "tokens_per_minute": 90000,
        "daily_budget": 5.0,
        "monthly_budget": 50.0,
        "cost_per_1k_tokens_input": 0.0005,
        "cost_per_1k_tokens_output": 0.0015,
    },
    APIProvider.MISTRAL: {
        "requests_per_minute": 60,
        "requests_per_day": 2000,
        "tokens_per_minute": 100000,
        "daily_budget": 3.0,
        "monthly_budget": 30.0,
        "cost_per_1k_tokens_input": 0.0002,
        "cost_per_1k_tokens_output": 0.0006,
    },
    APIProvider.GITHUB: {
        "requests_per_minute": 30,
        "requests_per_day": 5000,
        "daily_budget": 0.0,  # Free with OAuth
        "cost_per_request": 0.0,
    },
    APIProvider.SPOTIFY: {
        "requests_per_minute": 100,
        "requests_per_day": 10000,
        "daily_budget": 0.0,
        "cost_per_request": 0.0,
    },
    APIProvider.OFFLINE: {
        "requests_per_minute": 1000,
        "requests_per_day": 100000,
        "daily_budget": 0.0,
        "cost_per_request": 0.0,
    },
}


class QuotaTracker:
    """
    Tracks API quotas and manages request prioritization.
    """

    CONFIG_DIR = Path(__file__).parent.parent / "config"
    DATA_DIR = Path(__file__).parent.parent.parent / "memory" / "logs" / "quotas"

    def __init__(self):
        """Initialize quota tracker."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Provider quotas
        self._quotas: Dict[APIProvider, ProviderQuota] = {}

        # Request queue
        self._queue: List[QueuedRequest] = []

        # Request history (for analytics)
        self._history: List[Dict[str, Any]] = []

        # Load data
        self._load_quotas()
        self._load_queue()

        logger.info(f"[WIZ] QuotaTracker: {len(self._quotas)} providers configured")

    def _load_quotas(self):
        """Load quota configurations and usage."""
        quota_file = self.DATA_DIR / "quotas.json"

        if quota_file.exists():
            try:
                data = json.loads(quota_file.read_text())
                for provider_str, quota_data in data.get("quotas", {}).items():
                    provider = APIProvider(provider_str)
                    self._quotas[provider] = ProviderQuota.from_dict(quota_data)
            except Exception as e:
                logger.error(f"[ERROR] Failed to load quotas: {e}")

        # Initialize missing providers with defaults
        for provider, defaults in DEFAULT_QUOTAS.items():
            if provider not in self._quotas:
                self._quotas[provider] = ProviderQuota(provider=provider, **defaults)

        # Check for date rollovers
        self._check_rollovers()

    def _save_quotas(self):
        """Save quota data."""
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "quotas": {
                provider.value: quota.to_dict()
                for provider, quota in self._quotas.items()
            },
        }

        quota_file = self.DATA_DIR / "quotas.json"
        quota_file.write_text(json.dumps(data, indent=2))

    def _load_queue(self):
        """Load queued requests."""
        queue_file = self.DATA_DIR / "queue.json"

        if queue_file.exists():
            try:
                data = json.loads(queue_file.read_text())
                for req_data in data.get("queue", []):
                    req = QueuedRequest(
                        id=req_data["id"],
                        provider=APIProvider(req_data["provider"]),
                        priority=RequestPriority(req_data["priority"]),
                        endpoint=req_data.get("endpoint", ""),
                        method=req_data.get("method", "POST"),
                        payload=req_data.get("payload", {}),
                        estimated_tokens=req_data.get("estimated_tokens", 0),
                        estimated_cost=req_data.get("estimated_cost", 0.0),
                        workflow_id=req_data.get("workflow_id"),
                        objective_id=req_data.get("objective_id"),
                        created_at=req_data.get("created_at", time.time()),
                        status=req_data.get("status", "pending"),
                    )
                    self._queue.append(req)
            except Exception as e:
                logger.error(f"[ERROR] Failed to load queue: {e}")

    def _save_queue(self):
        """Save queued requests."""
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "queue": [
                {
                    "id": req.id,
                    "provider": req.provider.value,
                    "priority": req.priority.value,
                    "endpoint": req.endpoint,
                    "method": req.method,
                    "payload": req.payload,
                    "estimated_tokens": req.estimated_tokens,
                    "estimated_cost": req.estimated_cost,
                    "workflow_id": req.workflow_id,
                    "objective_id": req.objective_id,
                    "created_at": req.created_at,
                    "status": req.status,
                }
                for req in self._queue
                if req.status == "pending"
            ],
        }

        queue_file = self.DATA_DIR / "queue.json"
        queue_file.write_text(json.dumps(data, indent=2))

    def _check_rollovers(self):
        """Check and apply date rollovers."""
        today = datetime.now().strftime("%Y-%m-%d")
        this_month = datetime.now().strftime("%Y-%m")

        for quota in self._quotas.values():
            # Daily rollover
            if quota.last_daily_reset != today:
                quota.requests_today = 0
                quota.tokens_today = 0
                quota.cost_today = 0.0
                quota.last_daily_reset = today

            # Monthly rollover
            if quota.last_monthly_reset != this_month:
                quota.requests_this_month = 0
                quota.tokens_this_month = 0
                quota.cost_this_month = 0.0
                quota.last_monthly_reset = this_month

        self._save_quotas()

    # === Public API ===

    def can_request(self, provider: APIProvider, estimated_tokens: int = 0) -> bool:
        """
        Check if a request can be made to a provider.

        Args:
            provider: API provider
            estimated_tokens: Estimated token count

        Returns:
            True if request is allowed
        """
        quota = self._quotas.get(provider)
        if not quota:
            return True  # Unknown provider, allow

        # Check rate limit
        now = time.time()
        if now - quota.minute_window_start > 60:
            quota.requests_this_minute = 0
            quota.minute_window_start = now

        if quota.requests_this_minute >= quota.requests_per_minute:
            log_provider_event(
                provider.value,
                QuotaStatus.RATE_LIMITED.value,
                "Requests per minute threshold reached",
                metadata={
                    "requests_this_minute": quota.requests_this_minute,
                    "limit": quota.requests_per_minute,
                },
            )
            return False

        # Check daily limits
        if quota.requests_today >= quota.requests_per_day:
            log_provider_event(
                provider.value,
                QuotaStatus.EXCEEDED.value,
                "Daily requests limit reached",
                metadata={
                    "requests_today": quota.requests_today,
                    "daily_limit": quota.requests_per_day,
                },
            )
            return False

        if quota.tokens_today + estimated_tokens > quota.tokens_per_day:
            log_provider_event(
                provider.value,
                QuotaStatus.CRITICAL.value,
                "Token allowance would be exceeded",
                metadata={
                    "tokens_today": quota.tokens_today,
                    "tokens_limit": quota.tokens_per_day,
                    "estimated_tokens": estimated_tokens,
                },
            )
            return False

        # Estimate cost and check budget
        estimated_cost = self._estimate_cost(provider, estimated_tokens)
        if quota.cost_today + estimated_cost > quota.daily_budget:
            log_provider_event(
                provider.value,
                QuotaStatus.EXCEEDED.value,
                "Daily budget would be exceeded",
                metadata={
                    "cost_today": quota.cost_today,
                    "daily_budget": quota.daily_budget,
                    "estimated_cost": estimated_cost,
                },
            )
            return False

        return True

    def record_request(
        self,
        provider: APIProvider,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost: Optional[float] = None,
        success: bool = True,
        workflow_id: Optional[str] = None,
    ):
        """
        Record a completed API request.

        Args:
            provider: API provider
            tokens_input: Input tokens used
            tokens_output: Output tokens used
            cost: Actual cost (or estimated if None)
            success: Whether request succeeded
            workflow_id: Associated workflow ID
        """
        quota = self._quotas.get(provider)
        if not quota:
            quota = ProviderQuota(provider=provider)
            self._quotas[provider] = quota

        total_tokens = tokens_input + tokens_output

        # Update rate limiting
        now = time.time()
        if now - quota.minute_window_start > 60:
            quota.requests_this_minute = 0
            quota.minute_window_start = now
        quota.requests_this_minute += 1
        quota.last_request_time = now

        # Update counts
        quota.requests_today += 1
        quota.requests_this_month += 1
        quota.total_requests += 1
        quota.tokens_today += total_tokens
        quota.tokens_this_month += total_tokens

        # Calculate cost
        if cost is None:
            cost = self._calculate_cost(provider, tokens_input, tokens_output)

        quota.cost_today += cost
        quota.cost_this_month += cost
        quota.total_cost += cost

        # Record in history
        self._history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "provider": provider.value,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "cost": cost,
                "success": success,
                "workflow_id": workflow_id,
            }
        )

        # Keep history manageable
        if len(self._history) > 1000:
            self._history = self._history[-500:]

        self._save_quotas()

        logger.info(
            f"[WIZ] API request: {provider.value} "
            f"tokens={total_tokens} cost=${cost:.4f}"
        )

    def get_quota_status(self, provider: APIProvider) -> Dict[str, Any]:
        """Get detailed quota status for a provider."""
        quota = self._quotas.get(provider)
        if not quota:
            return {"provider": provider.value, "configured": False}

        return {
            "provider": provider.value,
            "configured": True,
            "status": quota.status.value,
            "daily": {
                "requests": quota.requests_today,
                "limit": quota.requests_per_day,
                "tokens": quota.tokens_today,
                "token_limit": quota.tokens_per_day,
                "cost": round(quota.cost_today, 4),
                "budget": quota.daily_budget,
                "usage_percent": round(quota.daily_usage_percent, 1),
            },
            "monthly": {
                "requests": quota.requests_this_month,
                "limit": quota.requests_per_month,
                "tokens": quota.tokens_this_month,
                "token_limit": quota.tokens_per_month,
                "cost": round(quota.cost_this_month, 4),
                "budget": quota.monthly_budget,
                "usage_percent": round(quota.monthly_usage_percent, 1),
            },
            "totals": {
                "requests": quota.total_requests,
                "cost": round(quota.total_cost, 4),
            },
            "rate_limit": {
                "requests_this_minute": quota.requests_this_minute,
                "limit_per_minute": quota.requests_per_minute,
            },
        }

    def get_all_quotas(self) -> Dict[str, Any]:
        """Get quota status for all providers."""
        result = {
            "updated_at": datetime.now().isoformat(),
            "providers": {},
            "totals": {
                "cost_today": 0.0,
                "cost_this_month": 0.0,
                "requests_today": 0,
                "requests_this_month": 0,
            },
        }

        for provider in APIProvider:
            status = self.get_quota_status(provider)
            if status.get("configured"):
                result["providers"][provider.value] = status
                result["totals"]["cost_today"] += status["daily"]["cost"]
                result["totals"]["cost_this_month"] += status["monthly"]["cost"]
                result["totals"]["requests_today"] += status["daily"]["requests"]
                result["totals"]["requests_this_month"] += status["monthly"]["requests"]

        result["totals"]["cost_today"] = round(result["totals"]["cost_today"], 4)
        result["totals"]["cost_this_month"] = round(
            result["totals"]["cost_this_month"], 4
        )

        return result

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary for dashboard display."""
        all_quotas = self.get_all_quotas()

        # Find providers with issues
        warnings = []
        for provider, status in all_quotas["providers"].items():
            if status["status"] == "exceeded":
                warnings.append(f"⚠️ {provider}: Quota exceeded")
            elif status["status"] == "critical":
                warnings.append(f"🔴 {provider}: >95% quota used")
            elif status["status"] == "warning":
                warnings.append(f"🟡 {provider}: >80% quota used")
            elif status["status"] == "rate_limited":
                warnings.append(f"⏳ {provider}: Rate limited")

        return {
            "cost_today": f"${all_quotas['totals']['cost_today']:.2f}",
            "cost_this_month": f"${all_quotas['totals']['cost_this_month']:.2f}",
            "requests_today": all_quotas["totals"]["requests_today"],
            "active_providers": len(all_quotas["providers"]),
            "warnings": warnings,
            "queue_size": len([r for r in self._queue if r.status == "pending"]),
        }

    # === Queue Management ===

    def queue_request(
        self,
        provider: APIProvider,
        endpoint: str,
        payload: Dict[str, Any],
        priority: RequestPriority = RequestPriority.NORMAL,
        workflow_id: Optional[str] = None,
        objective_id: Optional[str] = None,
        estimated_tokens: int = 0,
    ) -> str:
        """
        Queue an API request for later execution.

        Args:
            provider: API provider
            endpoint: API endpoint
            payload: Request payload
            priority: Request priority
            workflow_id: Associated workflow
            objective_id: Associated objective
            estimated_tokens: Estimated tokens

        Returns:
            Request ID
        """
        import uuid

        request_id = str(uuid.uuid4())[:8]

        request = QueuedRequest(
            id=request_id,
            provider=provider,
            priority=priority,
            endpoint=endpoint,
            payload=payload,
            estimated_tokens=estimated_tokens,
            estimated_cost=self._estimate_cost(provider, estimated_tokens),
            workflow_id=workflow_id,
            objective_id=objective_id,
        )

        self._queue.append(request)
        self._queue.sort(key=lambda r: (r.priority.value, r.created_at))

        self._save_queue()

        logger.info(f"[WIZ] Queued request {request_id} for {provider.value}")

        return request_id

    def get_next_request(self) -> Optional[QueuedRequest]:
        """Get next request from queue that can be executed."""
        for request in self._queue:
            if request.status != "pending":
                continue

            if self.can_request(request.provider, request.estimated_tokens):
                request.status = "processing"
                return request

        return None

    def complete_request(
        self, request_id: str, success: bool, result: Any = None, error: str = None
    ):
        """Mark a queued request as complete."""
        for request in self._queue:
            if request.id == request_id:
                request.status = "completed" if success else "failed"
                request.result = result
                request.error = error

                if not success and request.retry_count < request.max_retries:
                    request.retry_count += 1
                    request.status = "pending"
                    request.scheduled_for = time.time() + (60 * request.retry_count)

                self._save_queue()
                return

    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status."""
        pending = [r for r in self._queue if r.status == "pending"]
        processing = [r for r in self._queue if r.status == "processing"]

        by_priority = defaultdict(int)
        by_provider = defaultdict(int)

        for req in pending:
            by_priority[req.priority.name] += 1
            by_provider[req.provider.value] += 1

        return {
            "pending": len(pending),
            "processing": len(processing),
            "by_priority": dict(by_priority),
            "by_provider": dict(by_provider),
            "estimated_cost": sum(r.estimated_cost for r in pending),
        }

    # === Helper Methods ===

    def _estimate_cost(self, provider: APIProvider, tokens: int) -> float:
        """Estimate cost for a request."""
        quota = self._quotas.get(provider)
        if not quota:
            return 0.0

        # Assume 50/50 input/output split for estimation
        input_tokens = tokens // 2
        output_tokens = tokens - input_tokens

        return self._calculate_cost(provider, input_tokens, output_tokens)

    def _calculate_cost(
        self, provider: APIProvider, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate actual cost."""
        quota = self._quotas.get(provider)
        if not quota:
            return 0.0

        cost = (
            (input_tokens / 1000) * quota.cost_per_1k_tokens_input
            + (output_tokens / 1000) * quota.cost_per_1k_tokens_output
            + quota.cost_per_request
        )

        return cost

    def update_provider_limits(
        self,
        provider: APIProvider,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
        requests_per_day: Optional[int] = None,
    ):
        """Update provider limits."""
        quota = self._quotas.get(provider)
        if not quota:
            return

        if daily_budget is not None:
            quota.daily_budget = daily_budget
        if monthly_budget is not None:
            quota.monthly_budget = monthly_budget
        if requests_per_day is not None:
            quota.requests_per_day = requests_per_day

        self._save_quotas()


# Singleton
_quota_tracker: Optional[QuotaTracker] = None


def get_quota_tracker() -> QuotaTracker:
    """Get or create quota tracker singleton."""
    global _quota_tracker
    if _quota_tracker is None:
        _quota_tracker = QuotaTracker()
    return _quota_tracker


# Convenience functions
def check_quota(provider: str, tokens: int = 0) -> bool:
    """Check if request is allowed."""
    try:
        p = APIProvider(provider)
        return get_quota_tracker().can_request(p, tokens)
    except ValueError:
        return True


def record_usage(
    provider: str, input_tokens: int = 0, output_tokens: int = 0, cost: float = None
):
    """Record API usage."""
    try:
        p = APIProvider(provider)
        get_quota_tracker().record_request(p, input_tokens, output_tokens, cost)
    except ValueError:
        pass


def get_quotas_summary() -> Dict[str, Any]:
    """Get quotas summary for display."""
    return get_quota_tracker().get_dashboard_summary()
