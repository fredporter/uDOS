"""
uDOS v1.2.0 - API Monitor Service

Comprehensive API usage monitoring with:
- Rate limiting (requests per second/minute/hour/day)
- Cost tracking (per request, per session, per day)
- Budget alerts (80% warning, 100% blocking)
- Usage statistics (requests, tokens, errors)
- Live stats display
- Persistent storage (survives restarts)

Version: 1.2.0 (Task 5 - API Monitoring)
Author: uDOS Development Team
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass, asdict


@dataclass
class APIRequest:
    """Record of a single API request."""
    timestamp: float
    api_type: str  # 'gemini', 'banana', 'other'
    operation: str  # 'DO', 'GUIDE', 'SVG', etc.
    tokens_input: int = 0
    tokens_output: int = 0
    cost: float = 0.0
    duration_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    priority: str = 'normal'  # 'critical', 'high', 'normal', 'low'


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_second: float = 2.0
    requests_per_minute: int = 60
    requests_per_hour: int = 1440
    requests_per_day: int = 10000

    # Burst allowance (can exceed limit briefly)
    allow_burst: bool = True
    burst_size: int = 5
    burst_window_seconds: float = 1.0


@dataclass
class BudgetConfig:
    """Budget configuration and tracking."""
    daily_budget_usd: float = 1.0
    hourly_budget_usd: float = 0.1
    warn_at_percent: int = 80
    block_at_percent: int = 100

    # Priority-based budget allocation
    critical_reserve_percent: int = 20  # Reserve 20% for critical requests
    high_reserve_percent: int = 30      # Reserve 30% for high priority


class APIMonitor:
    """
    Monitor and control API usage with rate limiting and cost tracking.

    Features:
    - Rate limiting (configurable per second/minute/hour/day)
    - Cost tracking with budget enforcement
    - Priority queue support
    - Usage statistics
    - Persistent storage
    """

    def __init__(self,
                 rate_config: Optional[RateLimitConfig] = None,
                 budget_config: Optional[BudgetConfig] = None,
                 storage_path: Optional[Path] = None):
        """
        Initialize API monitor.

        Args:
            rate_config: Rate limiting configuration
            budget_config: Budget configuration
            storage_path: Path for persistent storage
        """
        self.rate_config = rate_config or RateLimitConfig()
        self.budget_config = budget_config or BudgetConfig()
        from core.utils.paths import PATHS
        self.storage_path = storage_path or (PATHS.MEMORY_SYSTEM / "api_monitor.json")

        # Request tracking (in-memory, fast access)
        self.recent_requests: deque = deque(maxlen=10000)  # Last 10K requests

        # Time-based request tracking for rate limiting
        self.requests_last_second: deque = deque(maxlen=100)
        self.requests_last_minute: deque = deque(maxlen=1000)
        self.requests_last_hour: deque = deque(maxlen=5000)
        self.requests_last_day: deque = deque(maxlen=50000)

        # Statistics
        self.stats = {
            'session_start': time.time(),
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_cost': 0.0,
            'total_tokens_input': 0,
            'total_tokens_output': 0,
            'total_duration_ms': 0.0,
            'by_api_type': {},
            'by_operation': {},
            'by_priority': {
                'critical': {'count': 0, 'cost': 0.0},
                'high': {'count': 0, 'cost': 0.0},
                'normal': {'count': 0, 'cost': 0.0},
                'low': {'count': 0, 'cost': 0.0}
            }
        }

        # Budget tracking
        self.budget_usage = {
            'today': {
                'date': datetime.now().date().isoformat(),
                'cost': 0.0,
                'requests': 0
            },
            'current_hour': {
                'hour': datetime.now().hour,
                'cost': 0.0,
                'requests': 0
            }
        }

        # Alerts
        self.alerts: List[Dict] = []

        # Load persistent data if exists
        self._load_state()

    # ========== Rate Limiting ==========

    def check_rate_limit(self, priority: str = 'normal') -> Tuple[bool, Optional[str]]:
        """
        Check if request can proceed based on rate limits.

        Args:
            priority: Request priority ('critical', 'high', 'normal', 'low')

        Returns:
            (allowed: bool, reason: Optional[str])
        """
        now = time.time()

        # Clean old requests from tracking
        self._clean_request_tracking(now)

        # Critical requests bypass rate limits
        if priority == 'critical':
            return True, None

        # Check per-second limit
        requests_this_second = len([
            ts for ts in self.requests_last_second
            if now - ts < 1.0
        ])

        if requests_this_second >= self.rate_config.requests_per_second:
            # Check if burst allowed
            if self.rate_config.allow_burst and priority in ['high', 'normal']:
                if requests_this_second < self.rate_config.requests_per_second + self.rate_config.burst_size:
                    return True, None  # Allow burst

            wait_time = 1.0 - (now - min(self.requests_last_second))
            return False, f"Rate limit: {self.rate_config.requests_per_second} req/sec (wait {wait_time:.1f}s)"

        # Check per-minute limit
        if len(self.requests_last_minute) >= self.rate_config.requests_per_minute:
            return False, f"Rate limit: {self.rate_config.requests_per_minute} req/min"

        # Check per-hour limit
        if len(self.requests_last_hour) >= self.rate_config.requests_per_hour:
            return False, f"Rate limit: {self.rate_config.requests_per_hour} req/hour"

        # Check per-day limit
        if len(self.requests_last_day) >= self.rate_config.requests_per_day:
            return False, f"Rate limit: {self.rate_config.requests_per_day} req/day"

        return True, None

    def _clean_request_tracking(self, now: float) -> None:
        """Remove old requests from tracking queues."""
        # Clean per-second tracking (keep last 1 second)
        while self.requests_last_second and now - self.requests_last_second[0] > 1.0:
            self.requests_last_second.popleft()

        # Clean per-minute tracking (keep last 60 seconds)
        while self.requests_last_minute and now - self.requests_last_minute[0] > 60.0:
            self.requests_last_minute.popleft()

        # Clean per-hour tracking (keep last 3600 seconds)
        while self.requests_last_hour and now - self.requests_last_hour[0] > 3600.0:
            self.requests_last_hour.popleft()

        # Clean per-day tracking (keep last 86400 seconds)
        while self.requests_last_day and now - self.requests_last_day[0] > 86400.0:
            self.requests_last_day.popleft()

    # ========== Budget Enforcement ==========

    def check_budget(self, estimated_cost: float, priority: str = 'normal') -> Tuple[bool, Optional[str]]:
        """
        Check if request fits within budget.

        Args:
            estimated_cost: Estimated cost in USD
            priority: Request priority

        Returns:
            (allowed: bool, reason: Optional[str])
        """
        # Update budget tracking (reset if new day/hour)
        self._update_budget_tracking()

        # Critical requests bypass budget (but track cost)
        if priority == 'critical':
            return True, None

        # Check daily budget
        daily_used = self.budget_usage['today']['cost']
        daily_limit = self.budget_config.daily_budget_usd

        # Reserve budget for higher priorities
        if priority == 'low':
            # Low priority can only use unreserved budget
            reserved = daily_limit * (self.budget_config.critical_reserve_percent +
                                     self.budget_config.high_reserve_percent) / 100
            available = daily_limit - reserved - daily_used
        elif priority == 'normal':
            # Normal priority can use all but critical reserve
            reserved = daily_limit * self.budget_config.critical_reserve_percent / 100
            available = daily_limit - reserved - daily_used
        else:  # high priority
            # High priority can use full budget
            available = daily_limit - daily_used

        if daily_used + estimated_cost > daily_limit:
            return False, f"Daily budget exceeded: ${daily_used:.4f} / ${daily_limit:.2f}"

        if estimated_cost > available:
            return False, f"Insufficient budget for priority '{priority}': ${available:.4f} available"

        # Check hourly budget
        hourly_used = self.budget_usage['current_hour']['cost']
        hourly_limit = self.budget_config.hourly_budget_usd

        if hourly_used + estimated_cost > hourly_limit:
            return False, f"Hourly budget exceeded: ${hourly_used:.4f} / ${hourly_limit:.2f}"

        # Check if at warning threshold
        daily_percent = (daily_used / daily_limit * 100) if daily_limit > 0 else 0
        if daily_percent >= self.budget_config.warn_at_percent:
            # Allow but warn
            self._add_alert('warning', f"Budget at {daily_percent:.0f}% (${daily_used:.4f} / ${daily_limit:.2f})")

        return True, None

    def _update_budget_tracking(self) -> None:
        """Update budget tracking, reset if new day/hour."""
        now = datetime.now()
        today = now.date().isoformat()
        current_hour = now.hour

        # Reset daily budget if new day
        if self.budget_usage['today']['date'] != today:
            self.budget_usage['today'] = {
                'date': today,
                'cost': 0.0,
                'requests': 0
            }

        # Reset hourly budget if new hour
        if self.budget_usage['current_hour']['hour'] != current_hour:
            self.budget_usage['current_hour'] = {
                'hour': current_hour,
                'cost': 0.0,
                'requests': 0
            }

    # ========== Request Tracking ==========

    def record_request(self, request: APIRequest) -> None:
        """
        Record an API request.

        Args:
            request: APIRequest object with details
        """
        now = time.time()

        # Add to tracking queues
        self.requests_last_second.append(now)
        self.requests_last_minute.append(now)
        self.requests_last_hour.append(now)
        self.requests_last_day.append(now)

        # Add to recent requests
        self.recent_requests.append(request)

        # Update statistics
        self.stats['total_requests'] += 1
        if request.success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1

        self.stats['total_cost'] += request.cost
        self.stats['total_tokens_input'] += request.tokens_input
        self.stats['total_tokens_output'] += request.tokens_output
        self.stats['total_duration_ms'] += request.duration_ms

        # Track by API type
        if request.api_type not in self.stats['by_api_type']:
            self.stats['by_api_type'][request.api_type] = {
                'count': 0, 'cost': 0.0, 'tokens': 0
            }
        self.stats['by_api_type'][request.api_type]['count'] += 1
        self.stats['by_api_type'][request.api_type]['cost'] += request.cost
        self.stats['by_api_type'][request.api_type]['tokens'] += (request.tokens_input + request.tokens_output)

        # Track by operation
        if request.operation not in self.stats['by_operation']:
            self.stats['by_operation'][request.operation] = {
                'count': 0, 'cost': 0.0
            }
        self.stats['by_operation'][request.operation]['count'] += 1
        self.stats['by_operation'][request.operation]['cost'] += request.cost

        # Track by priority
        self.stats['by_priority'][request.priority]['count'] += 1
        self.stats['by_priority'][request.priority]['cost'] += request.cost

        # Update budget usage
        self.budget_usage['today']['cost'] += request.cost
        self.budget_usage['today']['requests'] += 1
        self.budget_usage['current_hour']['cost'] += request.cost
        self.budget_usage['current_hour']['requests'] += 1

        # Persist state periodically (every 10 requests)
        if self.stats['total_requests'] % 10 == 0:
            self._save_state()

    # ========== Statistics ==========

    def get_stats(self) -> Dict:
        """Get current statistics."""
        uptime = time.time() - self.stats['session_start']

        return {
            'uptime_seconds': uptime,
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': (self.stats['successful_requests'] / self.stats['total_requests'] * 100)
                           if self.stats['total_requests'] > 0 else 0,
            'total_cost': self.stats['total_cost'],
            'avg_cost_per_request': (self.stats['total_cost'] / self.stats['total_requests'])
                                   if self.stats['total_requests'] > 0 else 0,
            'total_tokens': self.stats['total_tokens_input'] + self.stats['total_tokens_output'],
            'tokens_input': self.stats['total_tokens_input'],
            'tokens_output': self.stats['total_tokens_output'],
            'avg_duration_ms': (self.stats['total_duration_ms'] / self.stats['total_requests'])
                              if self.stats['total_requests'] > 0 else 0,
            'by_api_type': self.stats['by_api_type'],
            'by_operation': self.stats['by_operation'],
            'by_priority': self.stats['by_priority'],
            'rate_limits': {
                'per_second': f"{len(self.requests_last_second)} / {self.rate_config.requests_per_second}",
                'per_minute': f"{len(self.requests_last_minute)} / {self.rate_config.requests_per_minute}",
                'per_hour': f"{len(self.requests_last_hour)} / {self.rate_config.requests_per_hour}",
                'per_day': f"{len(self.requests_last_day)} / {self.rate_config.requests_per_day}"
            },
            'budget': {
                'daily_limit': self.budget_config.daily_budget_usd,
                'daily_used': self.budget_usage['today']['cost'],
                'daily_remaining': self.budget_config.daily_budget_usd - self.budget_usage['today']['cost'],
                'daily_percent': (self.budget_usage['today']['cost'] / self.budget_config.daily_budget_usd * 100)
                                if self.budget_config.daily_budget_usd > 0 else 0,
                'hourly_limit': self.budget_config.hourly_budget_usd,
                'hourly_used': self.budget_usage['current_hour']['cost'],
                'hourly_remaining': self.budget_config.hourly_budget_usd - self.budget_usage['current_hour']['cost']
            },
            'alerts': self.alerts[-10:]  # Last 10 alerts
        }

    def get_live_stats(self) -> str:
        """Get formatted live statistics for display."""
        stats = self.get_stats()

        uptime_hours = stats['uptime_seconds'] / 3600
        uptime_str = f"{uptime_hours:.1f}h" if uptime_hours >= 1 else f"{stats['uptime_seconds']:.0f}s"

        return f"""📊 API Monitor - Live Stats

Session: {uptime_str} | Requests: {stats['total_requests']} | Success: {stats['success_rate']:.0f}%

Rate Limits:
  Per Second: {stats['rate_limits']['per_second']}
  Per Minute: {stats['rate_limits']['per_minute']}
  Per Hour: {stats['rate_limits']['per_hour']}
  Per Day: {stats['rate_limits']['per_day']}

Budget (Daily):
  Used: ${stats['budget']['daily_used']:.4f} / ${stats['budget']['daily_limit']:.2f} ({stats['budget']['daily_percent']:.0f}%)
  Remaining: ${stats['budget']['daily_remaining']:.4f}

Budget (Hourly):
  Used: ${stats['budget']['hourly_used']:.4f} / ${stats['budget']['hourly_limit']:.2f}
  Remaining: ${stats['budget']['hourly_remaining']:.4f}

Costs:
  Total: ${stats['total_cost']:.4f}
  Avg per Request: ${stats['avg_cost_per_request']:.6f}

Tokens:
  Input: {stats['tokens_input']:,}
  Output: {stats['tokens_output']:,}
  Total: {stats['total_tokens']:,}

Performance:
  Avg Duration: {stats['avg_duration_ms']:.0f}ms
"""

    # ========== Alerts ==========

    def _add_alert(self, level: str, message: str) -> None:
        """
        Add an alert.

        Args:
            level: Alert level ('info', 'warning', 'error')
            message: Alert message
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.alerts.append(alert)

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

    def get_alerts(self, level: Optional[str] = None) -> List[Dict]:
        """
        Get alerts, optionally filtered by level.

        Args:
            level: Optional level filter

        Returns:
            List of alert dictionaries
        """
        if level:
            return [a for a in self.alerts if a['level'] == level]
        return self.alerts

    # ========== Persistence ==========

    def _save_state(self) -> None:
        """Save state to disk."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            state = {
                'stats': self.stats,
                'budget_usage': self.budget_usage,
                'alerts': self.alerts,
                'last_saved': datetime.now().isoformat()
            }

            with open(self.storage_path, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            # Don't crash if save fails
            pass

    def _load_state(self) -> None:
        """Load state from disk."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    state = json.load(f)

                # Restore statistics
                if 'stats' in state:
                    self.stats.update(state['stats'])
                    # Reset session start to now
                    self.stats['session_start'] = time.time()

                # Restore budget usage (check if still same day/hour)
                if 'budget_usage' in state:
                    self._restore_budget_usage(state['budget_usage'])

                # Restore alerts
                if 'alerts' in state:
                    self.alerts = state['alerts']
        except Exception as e:
            # Start fresh if load fails
            pass

    def _restore_budget_usage(self, saved_budget: Dict) -> None:
        """Restore budget usage if still same day/hour."""
        now = datetime.now()
        today = now.date().isoformat()
        current_hour = now.hour

        # Restore daily budget if same day
        if saved_budget.get('today', {}).get('date') == today:
            self.budget_usage['today'] = saved_budget['today']

        # Restore hourly budget if same hour
        if saved_budget.get('current_hour', {}).get('hour') == current_hour:
            self.budget_usage['current_hour'] = saved_budget['current_hour']


# ========== Global Instance ==========

_monitor_instance: Optional[APIMonitor] = None


def get_api_monitor(
    rate_config: Optional[RateLimitConfig] = None,
    budget_config: Optional[BudgetConfig] = None
) -> APIMonitor:
    """
    Get or create global API monitor instance.

    Args:
        rate_config: Optional rate limit configuration
        budget_config: Optional budget configuration

    Returns:
        APIMonitor instance
    """
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = APIMonitor(
            rate_config=rate_config,
            budget_config=budget_config
        )
    return _monitor_instance


def reset_monitor() -> None:
    """Reset global monitor instance (useful for testing)."""
    global _monitor_instance
    _monitor_instance = None
