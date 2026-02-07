"""
Cost Tracking Service - API Usage & Resource Monitoring
========================================================

Tracks costs for external API usage on the Wizard Server.
Provides budgeting, alerts, and usage reports.

Tracked Resources:
  - AI Providers (OpenAI, Anthropic, local)
  - Web proxy bandwidth
  - Storage usage

Features:
  - Daily/monthly budgets
  - Usage alerts (50%, 75%, 90%, 100%)
  - Cost projection
  - Per-provider breakdown
  - Export to JSON/CSV

Note: WIZARD-ONLY functionality.
"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

from wizard.services.logging_api import get_logger

logger = get_logger("cost-tracking")


class ResourceType(Enum):
    """Types of tracked resources."""

    AI_TOKENS = "ai_tokens"  # LLM API tokens
    AI_REQUESTS = "ai_requests"  # LLM API calls
    WEB_REQUESTS = "web_requests"  # Web proxy requests
    BANDWIDTH_MB = "bandwidth_mb"  # Data transfer
    STORAGE_MB = "storage_mb"  # Cache/storage usage


class Provider(Enum):
    """External service providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    WEB = "web"


@dataclass
class UsageEntry:
    """Single usage entry."""

    timestamp: str
    resource: str
    provider: str
    amount: float
    cost_usd: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Budget:
    """Budget configuration."""

    resource: str
    daily_limit: float
    monthly_limit: float
    alert_thresholds: List[float] = field(default_factory=lambda: [0.5, 0.75, 0.9, 1.0])


@dataclass
class UsageReport:
    """Usage report for a period."""

    start_date: str
    end_date: str
    total_cost_usd: float
    by_provider: Dict[str, float]
    by_resource: Dict[str, float]
    entries_count: int
    over_budget: bool
    budget_usage_percent: float


# Cost rates per provider/resource
COST_RATES = {
    # OpenAI GPT-4 Turbo pricing (per 1K tokens)
    (Provider.OPENAI.value, ResourceType.AI_TOKENS.value): {
        "input": 0.01,
        "output": 0.03,
    },
    # Anthropic Claude 3 pricing (per 1K tokens)
    (Provider.ANTHROPIC.value, ResourceType.AI_TOKENS.value): {
        "input": 0.015,
        "output": 0.075,
    },
    # Local models (electricity estimate)
    (Provider.LOCAL.value, ResourceType.AI_TOKENS.value): {
        "input": 0.0001,
        "output": 0.0002,
    },
    # Web proxy (bandwidth cost estimate)
    (Provider.WEB.value, ResourceType.BANDWIDTH_MB.value): 0.0001,
}

# Default budgets
DEFAULT_BUDGETS = {
    ResourceType.AI_TOKENS.value: Budget(
        resource=ResourceType.AI_TOKENS.value,
        daily_limit=100000,  # tokens
        monthly_limit=2000000,
    ),
    ResourceType.AI_REQUESTS.value: Budget(
        resource=ResourceType.AI_REQUESTS.value,
        daily_limit=100,
        monthly_limit=2000,
    ),
    ResourceType.EMAIL_QUOTA.value: Budget(
        resource=ResourceType.EMAIL_QUOTA.value,
        daily_limit=100,  # Gmail daily limit awareness
        monthly_limit=2000,
    ),
    ResourceType.WEB_REQUESTS.value: Budget(
        resource=ResourceType.WEB_REQUESTS.value,
        daily_limit=500,
        monthly_limit=10000,
    ),
}


class CostTracker:
    """
    Tracks and reports on resource usage and costs.
    """

    # Data storage
    DATA_PATH = (
        Path(__file__).parent.parent.parent / "memory" / "wizard" / "cost_tracking"
    )

    def __init__(self):
        """Initialize cost tracker."""
        self.DATA_PATH.mkdir(parents=True, exist_ok=True)
        self.budgets = self._load_budgets()
        self._alerts_sent: Dict[str, List[float]] = defaultdict(list)

    def _get_usage_file(self, date_obj: date) -> Path:
        """Get usage file for a specific date."""
        return self.DATA_PATH / f"usage-{date_obj.isoformat()}.json"

    def _load_budgets(self) -> Dict[str, Budget]:
        """Load budget configurations."""
        budget_file = self.DATA_PATH / "budgets.json"

        if budget_file.exists():
            try:
                data = json.loads(budget_file.read_text())
                return {k: Budget(**v) for k, v in data.items()}
            except Exception as e:
                logger.error(f"[LOCAL] Failed to load budgets: {e}")

        return DEFAULT_BUDGETS.copy()

    def save_budgets(self):
        """Save budget configurations."""
        budget_file = self.DATA_PATH / "budgets.json"
        data = {k: asdict(v) for k, v in self.budgets.items()}
        budget_file.write_text(json.dumps(data, indent=2))

    def set_budget(self, resource: str, daily_limit: float, monthly_limit: float):
        """Set budget for a resource."""
        self.budgets[resource] = Budget(
            resource=resource,
            daily_limit=daily_limit,
            monthly_limit=monthly_limit,
        )
        self.save_budgets()
        logger.info(
            f"[LOCAL] Budget set for {resource}: {daily_limit}/day, {monthly_limit}/month"
        )

    def record_usage(
        self,
        resource: ResourceType,
        provider: Provider,
        amount: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Record a usage entry.

        Args:
            resource: Type of resource
            provider: Service provider
            amount: Amount used
            metadata: Additional context

        Returns:
            Alert message if threshold crossed, None otherwise
        """
        now = datetime.now()
        cost = self._calculate_cost(provider, resource, amount, metadata)

        entry = UsageEntry(
            timestamp=now.isoformat(),
            resource=resource.value,
            provider=provider.value,
            amount=amount,
            cost_usd=cost,
            metadata=metadata or {},
        )

        # Load and append to today's file
        usage_file = self._get_usage_file(now.date())
        entries = []

        if usage_file.exists():
            try:
                entries = json.loads(usage_file.read_text())
            except Exception:
                entries = []

        entries.append(asdict(entry))
        usage_file.write_text(json.dumps(entries, indent=2))

        # Check budget alerts
        return self._check_alerts(resource.value, now.date())

    def _calculate_cost(
        self,
        provider: Provider,
        resource: ResourceType,
        amount: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate cost for a usage entry."""
        rate_key = (provider.value, resource.value)
        rate = COST_RATES.get(rate_key, 0.0)

        if isinstance(rate, dict):
            # Token pricing with input/output split
            if metadata and "type" in metadata:
                token_type = metadata["type"]
                rate = rate.get(token_type, 0.0)
            else:
                rate = rate.get("output", 0.0)  # Default to output pricing

        # Convert to appropriate units (e.g., per 1K tokens)
        if resource == ResourceType.AI_TOKENS:
            return (amount / 1000) * rate

        return amount * rate

    def _check_alerts(self, resource: str, date_obj: date) -> Optional[str]:
        """Check if usage has crossed alert thresholds."""
        budget = self.budgets.get(resource)
        if not budget:
            return None

        # Get today's usage
        daily_usage = self.get_daily_usage(resource, date_obj)
        daily_percent = (
            daily_usage / budget.daily_limit if budget.daily_limit > 0 else 0
        )

        # Check which thresholds have been crossed
        for threshold in budget.alert_thresholds:
            if daily_percent >= threshold:
                alert_key = f"{resource}:{date_obj}:{threshold}"
                if threshold not in self._alerts_sent[alert_key]:
                    self._alerts_sent[alert_key].append(threshold)
                    percent_str = f"{int(threshold * 100)}%"
                    logger.warning(
                        f"[WIZ] Budget alert: {resource} at {percent_str} of daily limit"
                    )
                    return f"⚠️ BUDGET ALERT: {resource} at {percent_str} of daily limit ({daily_usage:.1f}/{budget.daily_limit})"

        return None

    def get_daily_usage(self, resource: str, date_obj: Optional[date] = None) -> float:
        """Get total usage for a resource on a specific day."""
        date_obj = date_obj or datetime.now().date()
        usage_file = self._get_usage_file(date_obj)

        if not usage_file.exists():
            return 0.0

        try:
            entries = json.loads(usage_file.read_text())
            return sum(e["amount"] for e in entries if e["resource"] == resource)
        except Exception:
            return 0.0

    def get_monthly_usage(self, resource: str, year: int, month: int) -> float:
        """Get total usage for a resource in a specific month."""
        total = 0.0

        # Iterate through all days in the month
        for day in range(1, 32):
            try:
                date_obj = date(year, month, day)
                total += self.get_daily_usage(resource, date_obj)
            except ValueError:
                break  # Invalid date (month ended)

        return total

    def get_daily_cost(self, date_obj: Optional[date] = None) -> float:
        """Get total cost for a day."""
        date_obj = date_obj or datetime.now().date()
        usage_file = self._get_usage_file(date_obj)

        if not usage_file.exists():
            return 0.0

        try:
            entries = json.loads(usage_file.read_text())
            return sum(e["cost_usd"] for e in entries)
        except Exception:
            return 0.0

    def generate_report(self, days: int = 30) -> UsageReport:
        """Generate a usage report for the past N days."""
        end_date = datetime.now().date()
        start_date = date(
            end_date.year,
            end_date.month - (1 if days > 28 else 0),
            1 if days > 28 else end_date.day - days,
        )

        by_provider: Dict[str, float] = defaultdict(float)
        by_resource: Dict[str, float] = defaultdict(float)
        total_cost = 0.0
        total_entries = 0

        # Aggregate data
        current = start_date
        while current <= end_date:
            usage_file = self._get_usage_file(current)
            if usage_file.exists():
                try:
                    entries = json.loads(usage_file.read_text())
                    for entry in entries:
                        by_provider[entry["provider"]] += entry["cost_usd"]
                        by_resource[entry["resource"]] += entry["amount"]
                        total_cost += entry["cost_usd"]
                        total_entries += 1
                except Exception:
                    pass

            # Move to next day
            from datetime import timedelta

            current = current + timedelta(days=1)

        # Calculate budget status
        # Use AI tokens as the primary budget indicator
        token_budget = self.budgets.get(ResourceType.AI_TOKENS.value)
        budget_usage = 0.0
        over_budget = False

        if token_budget:
            monthly_tokens = by_resource.get(ResourceType.AI_TOKENS.value, 0)
            budget_usage = (
                monthly_tokens / token_budget.monthly_limit
                if token_budget.monthly_limit > 0
                else 0
            )
            over_budget = budget_usage > 1.0

        return UsageReport(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            total_cost_usd=total_cost,
            by_provider=dict(by_provider),
            by_resource=dict(by_resource),
            entries_count=total_entries,
            over_budget=over_budget,
            budget_usage_percent=budget_usage * 100,
        )

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for the cost tracking dashboard."""
        today = datetime.now().date()

        data = {
            "today": {
                "date": today.isoformat(),
                "total_cost": self.get_daily_cost(today),
                "by_resource": {},
            },
            "budgets": {},
            "alerts": [],
        }

        # Get usage per resource
        for resource in ResourceType:
            daily = self.get_daily_usage(resource.value, today)
            budget = self.budgets.get(resource.value)

            data["today"]["by_resource"][resource.value] = {
                "usage": daily,
                "limit": budget.daily_limit if budget else 0,
                "percent": (
                    (daily / budget.daily_limit * 100)
                    if budget and budget.daily_limit > 0
                    else 0
                ),
            }

            if budget:
                data["budgets"][resource.value] = {
                    "daily_limit": budget.daily_limit,
                    "monthly_limit": budget.monthly_limit,
                }

        return data

    def export_csv(self, start_date: date, end_date: date, output_path: str) -> bool:
        """Export usage data to CSV."""
        try:
            from datetime import timedelta

            lines = ["timestamp,resource,provider,amount,cost_usd"]

            current = start_date
            while current <= end_date:
                usage_file = self._get_usage_file(current)
                if usage_file.exists():
                    entries = json.loads(usage_file.read_text())
                    for e in entries:
                        lines.append(
                            f"{e['timestamp']},{e['resource']},{e['provider']},{e['amount']},{e['cost_usd']}"
                        )
                current = current + timedelta(days=1)

            Path(output_path).write_text("\n".join(lines))
            return True
        except Exception as e:
            logger.error(f"[LOCAL] CSV export failed: {e}")
            return False


# Singleton instance
_tracker: Optional[CostTracker] = None


def get_tracker() -> CostTracker:
    """Get the cost tracker singleton."""
    global _tracker
    if _tracker is None:
        _tracker = CostTracker()
    return _tracker


if __name__ == "__main__":
    tracker = get_tracker()

    print("Cost Tracking Dashboard")
    print("=" * 40)

    data = tracker.get_dashboard_data()
    print(f"Date: {data['today']['date']}")
    print(f"Today's Cost: ${data['today']['total_cost']:.4f}")
    print()

    print("Resource Usage:")
    for resource, info in data["today"]["by_resource"].items():
        print(
            f"  {resource}: {info['usage']:.1f} / {info['limit']:.0f} ({info['percent']:.1f}%)"
        )
