"""
Monitoring & Alerting Manager

Provides health checks, alerts, rate limit tracking, cost monitoring,
and comprehensive audit logging for Wizard Server operations.
"""

import json
import time
import asyncio
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from core.services.health_training import read_last_summary
from wizard.services.logging_api import get_logger
from wizard.services.notification_history_service import NotificationHistoryService
import os
from wizard.services.plugin_registry import get_registry

logger = get_logger("wizard", category="monitoring", name="monitoring")


class HealthStatus(Enum):
    """Health check status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Alert types"""

    HEALTH_CHECK = "health_check"
    RATE_LIMIT = "rate_limit"
    COST_BUDGET = "cost_budget"
    SYNC_FAILURE = "sync_failure"
    API_ERROR = "api_error"
    SYSTEM_ERROR = "system_error"


@dataclass
class HealthCheck:
    """Health check result"""

    service: str
    status: str  # HealthStatus value
    response_time_ms: float
    timestamp: str
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Alert:
    """Alert notification"""

    id: str
    type: str  # AlertType value
    severity: str  # AlertSeverity value
    message: str
    timestamp: str
    service: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    acknowledged: bool = False
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class RateLimitStatus:
    """Rate limit tracking"""

    service: str
    limit: int
    remaining: int
    reset_at: str
    usage_percent: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CostMetrics:
    """Cost tracking metrics"""

    service: str
    cost_today: float
    cost_month: float
    budget_daily: float
    budget_monthly: float
    usage_percent_daily: float
    usage_percent_monthly: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AuditLogEntry:
    """Audit log entry"""

    id: str
    timestamp: str
    operation: str
    service: str
    user: str
    success: bool
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class MonitoringManager:
    """Manage monitoring, alerts, and health checks"""

    def __init__(
        self,
        data_dir: Path = None,
        check_interval: int = 60,
        alert_callbacks: Optional[List[Callable]] = None,
    ):
        """
        Initialize monitoring manager.

        Args:
            data_dir: Directory for monitoring data
            check_interval: Health check interval in seconds
            alert_callbacks: Optional callback functions for alerts
        """
        self.data_dir = data_dir or Path("memory/logs/monitoring")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.check_interval = check_interval
        self.alert_callbacks = alert_callbacks or []

        # State tracking
        self.health_checks: Dict[str, HealthCheck] = {}
        self.alerts: List[Alert] = []
        self.rate_limits: Dict[str, RateLimitStatus] = {}
        self.cost_metrics: Dict[str, CostMetrics] = {}
        self.audit_entries: List[AuditLogEntry] = []

        # Alert history
        self.alert_counts = defaultdict(int)
        self.last_alert_time = defaultdict(float)

        # Cost tracking
        self.cost_history: Dict[str, List[float]] = defaultdict(list)

        # Load persisted data
        self._load_state()

        logger.info("[WIZ] MonitoringManager initialized")

    def log_training_summary(self) -> Dict[str, Any]:
        """Emit health summary into logging_api and notify automation."""
        summary = self.get_health_summary()
        health_log = read_last_summary() or {}
        payload = {
            "summary": summary,
            "health_log": health_log,
            "alerts": [alert.to_dict() for alert in self.alerts],
            "rate_limits": {k: v.to_dict() for k, v in self.rate_limits.items()},
            "cost_metrics": {k: v.to_dict() for k, v in self.cost_metrics.items()},
        }
        summary_logger = get_logger("wizard", category="monitoring-summary", name="monitoring")
        summary_logger.info("Health training summary", ctx={"payload": payload})
        self._notify_on_drift(health_log, summary)
        return payload

    def _notify_on_drift(
        self, health_log: Dict[str, Any], summary: Dict[str, Any]
    ) -> None:
        """Notify history service when issues remain."""
        remaining = health_log.get("self_heal", {}).get("remaining", 0)
        if remaining > 0:
            notif = NotificationHistoryService()
            message = (
                f"Self-Heal drift detected: {remaining} issue(s) remain (status {summary.get('status')})"
            )
            try:
                asyncio.run(
                    notif.save_notification(
                        "warning",
                        "Self-Heal training alert",
                        message,
                        duration_ms=8000,
                        sticky=True,
                    )
                )
            except RuntimeError:
                # Already running loop; skip notification
                pass
    # -------------------------------------------------------------------------
    # Health Checks
    # -------------------------------------------------------------------------

    def check_health(self, service: str, check_func: Callable) -> HealthCheck:
        """
        Run health check for service.

        Args:
            service: Service name
            check_func: Function that returns (status, message, metadata)

        Returns:
            HealthCheck result
        """
        start_time = time.time()

        try:
            status, message, metadata = check_func()
            response_time = (time.time() - start_time) * 1000

            health = HealthCheck(
                service=service,
                status=status.value if isinstance(status, HealthStatus) else status,
                response_time_ms=round(response_time, 2),
                timestamp=datetime.now().isoformat(),
                message=message,
                metadata=metadata,
            )

            self.health_checks[service] = health

            # Create alert if unhealthy
            if health.status == HealthStatus.UNHEALTHY.value:
                self.create_alert(
                    type=AlertType.HEALTH_CHECK,
                    severity=AlertSeverity.ERROR,
                    message=f"{service} is unhealthy: {message}",
                    service=service,
                )

            logger.info(
                f"[WIZ] Health check: {service} = {health.status} ({response_time:.2f}ms)"
            )
            return health
        except Exception as exc:
            response_time = (time.time() - start_time) * 1000
            health = HealthCheck(
                service=service,
                status=HealthStatus.UNHEALTHY.value,
                response_time_ms=round(response_time, 2),
                timestamp=datetime.now().isoformat(),
                message=str(exc),
                metadata=None,
            )
            self.health_checks[service] = health
            self.create_alert(
                type=AlertType.HEALTH_CHECK,
                severity=AlertSeverity.ERROR,
                message=f"{service} check failed: {exc}",
                service=service,
            )
            logger.error(
                f"[WIZ] Health check failed: {service} ({response_time:.2f}ms) {exc}"
            )
            return health

    def check_wizard_core(self) -> HealthCheck:
        """Check Wizard core health endpoint."""
        base_url = (os.environ.get("WIZARD_BASE_URL") or "http://localhost:8765").rstrip("/")

        def check():
            try:
                resp = requests.get(f"{base_url}/health", timeout=2)
                if resp.status_code == 200:
                    return HealthStatus.HEALTHY, "Wizard healthy", {"status_code": resp.status_code}
                if resp.status_code < 500:
                    return HealthStatus.DEGRADED, f"HTTP {resp.status_code}", {"status_code": resp.status_code}
                return HealthStatus.UNHEALTHY, f"HTTP {resp.status_code}", {"status_code": resp.status_code}
            except requests.RequestException as exc:
                return HealthStatus.UNHEALTHY, str(exc), None

        return self.check_health("wizard_core", check)

    def check_goblin(self) -> HealthCheck:
        """Check Goblin dev server health."""
        host = os.environ.get("GOBLIN_HOST", "127.0.0.1").strip()
        port = os.environ.get("GOBLIN_PORT", "8767").strip()
        url = f"http://{host}:{port}/health"

        def check():
            try:
                resp = requests.get(url, timeout=2)
                if resp.status_code == 200:
                    return HealthStatus.HEALTHY, "Goblin healthy", {"status_code": resp.status_code}
                if resp.status_code < 500:
                    return HealthStatus.DEGRADED, f"HTTP {resp.status_code}", {"status_code": resp.status_code}
                return HealthStatus.UNHEALTHY, f"HTTP {resp.status_code}", {"status_code": resp.status_code}
            except requests.RequestException as exc:
                return HealthStatus.UNHEALTHY, str(exc), None

        return self.check_health("goblin", check)

    def check_plugin_registry(self) -> HealthCheck:
        """Check plugin registry availability."""
        def check():
            try:
                registry = get_registry()
                if not registry.base_dir.exists():
                    return HealthStatus.DEGRADED, "Plugin registry base dir missing", {"base_dir": str(registry.base_dir)}
                data = registry.build_registry(refresh=False, include_manifests=False)
                count = len(data or {})
                if count == 0:
                    return HealthStatus.DEGRADED, "No plugins registered", {"count": 0}
                return HealthStatus.HEALTHY, f"{count} plugins", {"count": count}
            except Exception as exc:
                return HealthStatus.UNHEALTHY, str(exc), None

        return self.check_health("plugin_registry", check)

    def run_default_checks(self) -> Dict[str, HealthCheck]:
        """Run core Wizard health checks."""
        results = {
            "wizard_core": self.check_wizard_core(),
            "goblin": self.check_goblin(),
            "plugin_registry": self.check_plugin_registry(),
        }
        return results

    def check_wizard_server(
        self, host: str = "127.0.0.1", port: int = 8765
    ) -> HealthCheck:
        """Check Wizard Server health"""

        def check():
            try:
                response = requests.get(f"http://{host}:{port}/health", timeout=2)
                if response.status_code == 200:
                    return HealthStatus.HEALTHY, "Server responding", {"port": port}
                else:
                    return HealthStatus.DEGRADED, f"Status {response.status_code}", None
            except requests.RequestException as e:
                return HealthStatus.UNHEALTHY, str(e), None

        return self.check_health("wizard_server", check)

    def check_ollama(self, endpoint: str = "http://127.0.0.1:11434") -> HealthCheck:
        """Check Ollama health"""

        def check():
            try:
                response = requests.get(f"{endpoint}/api/tags", timeout=2)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return (
                        HealthStatus.HEALTHY,
                        f"{len(models)} models available",
                        {"models": len(models)},
                    )
                else:
                    return HealthStatus.DEGRADED, f"Status {response.status_code}", None
            except requests.RequestException as e:
                return HealthStatus.UNHEALTHY, str(e), None

        return self.check_health("ollama", check)

    def check_github_api(self, token: Optional[str] = None) -> HealthCheck:
        """Check GitHub API health"""

        def check():
            try:
                headers = {"Authorization": f"token {token}"} if token else {}
                response = requests.get(
                    "https://api.github.com/rate_limit", headers=headers, timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    remaining = data["rate"]["remaining"]
                    limit = data["rate"]["limit"]
                    return (
                        HealthStatus.HEALTHY,
                        f"{remaining}/{limit} requests remaining",
                        {"remaining": remaining, "limit": limit},
                    )
                else:
                    return HealthStatus.DEGRADED, f"Status {response.status_code}", None
            except requests.RequestException as e:
                return HealthStatus.UNHEALTHY, str(e), None

        return self.check_health("github_api", check)

    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        if not self.health_checks:
            return {
                "status": "unknown",
                "services": 0,
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
            }

        statuses = [h.status for h in self.health_checks.values()]

        summary = {
            "status": "healthy",
            "services": len(statuses),
            "healthy": statuses.count(HealthStatus.HEALTHY.value),
            "degraded": statuses.count(HealthStatus.DEGRADED.value),
            "unhealthy": statuses.count(HealthStatus.UNHEALTHY.value),
            "checks": {
                name: check.to_dict() for name, check in self.health_checks.items()
            },
        }

        # Overall status
        if summary["unhealthy"] > 0:
            summary["status"] = "unhealthy"
        elif summary["degraded"] > 0:
            summary["status"] = "degraded"

        return summary

    # -------------------------------------------------------------------------
    # Alerts
    # -------------------------------------------------------------------------

    def create_alert(
        self,
        type: AlertType,
        severity: AlertSeverity,
        message: str,
        service: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        suppress_duplicates: bool = True,
        suppress_window: int = 300,  # 5 minutes
    ) -> Alert:
        """
        Create alert.

        Args:
            type: Alert type
            severity: Alert severity
            message: Alert message
            service: Service name
            metadata: Additional metadata
            suppress_duplicates: Suppress duplicate alerts
            suppress_window: Window for duplicate suppression (seconds)

        Returns:
            Created alert
        """
        # Check for duplicate suppression
        if suppress_duplicates:
            alert_key = f"{type.value}:{service}:{message}"
            last_time = self.last_alert_time.get(alert_key, 0)

            if time.time() - last_time < suppress_window:
                logger.debug(f"[WIZ] Suppressing duplicate alert: {message}")
                return None

            self.last_alert_time[alert_key] = time.time()

        # Create alert
        alert_id = f"alert-{int(time.time() * 1000)}"
        alert = Alert(
            id=alert_id,
            type=type.value,
            severity=severity.value,
            message=message,
            timestamp=datetime.now().isoformat(),
            service=service,
            metadata=metadata,
        )

        self.alerts.append(alert)
        self.alert_counts[type.value] += 1

        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"[WIZ] Alert callback failed: {e}")

        logger.warning(f"[WIZ] Alert: [{severity.value.upper()}] {message}")

        # Save state
        self._save_alerts()

        return alert

    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        type: Optional[AlertType] = None,
        service: Optional[str] = None,
        unacknowledged_only: bool = False,
        limit: int = 100,
    ) -> List[Alert]:
        """Get alerts with optional filtering"""
        filtered = self.alerts

        if severity:
            filtered = [a for a in filtered if a.severity == severity.value]

        if type:
            filtered = [a for a in filtered if a.type == type.value]

        if service:
            filtered = [a for a in filtered if a.service == service]

        if unacknowledged_only:
            filtered = [a for a in filtered if not a.acknowledged]

        # Sort by timestamp descending
        filtered.sort(key=lambda a: a.timestamp, reverse=True)

        return filtered[:limit]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                self._save_alerts()
                logger.info(f"[WIZ] Alert acknowledged: {alert_id}")
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.acknowledged = True
                self._save_alerts()
                logger.info(f"[WIZ] Alert resolved: {alert_id}")
                return True
        return False

    # -------------------------------------------------------------------------
    # Rate Limit Tracking
    # -------------------------------------------------------------------------

    def track_rate_limit(
        self,
        service: str,
        limit: int,
        remaining: int,
        reset_at: datetime,
        warn_threshold: float = 0.2,  # Warn at 20% remaining
    ) -> RateLimitStatus:
        """
        Track rate limit for service.

        Args:
            service: Service name
            limit: Total rate limit
            remaining: Remaining requests
            reset_at: Reset timestamp
            warn_threshold: Warning threshold (0.0-1.0)

        Returns:
            Rate limit status
        """
        usage_percent = ((limit - remaining) / limit) * 100 if limit > 0 else 0

        status = RateLimitStatus(
            service=service,
            limit=limit,
            remaining=remaining,
            reset_at=reset_at.isoformat(),
            usage_percent=round(usage_percent, 2),
            timestamp=datetime.now().isoformat(),
        )

        self.rate_limits[service] = status

        # Create alert if threshold exceeded
        if remaining / limit <= warn_threshold:
            self.create_alert(
                type=AlertType.RATE_LIMIT,
                severity=(
                    AlertSeverity.WARNING if remaining > 0 else AlertSeverity.ERROR
                ),
                message=f"{service} rate limit: {remaining}/{limit} remaining ({usage_percent:.1f}% used)",
                service=service,
                metadata={"remaining": remaining, "limit": limit},
            )

        logger.info(
            f"[WIZ] Rate limit: {service} = {remaining}/{limit} ({usage_percent:.1f}%)"
        )

        return status

    def get_rate_limit_status(
        self, service: Optional[str] = None
    ) -> Dict[str, RateLimitStatus]:
        """Get rate limit status"""
        if service:
            return {service: self.rate_limits.get(service)}
        return self.rate_limits

    # -------------------------------------------------------------------------
    # Cost Monitoring
    # -------------------------------------------------------------------------

    def track_cost(
        self,
        service: str,
        cost: float,
        budget_daily: float,
        budget_monthly: float,
        warn_threshold: float = 0.8,  # Warn at 80% of budget
    ) -> CostMetrics:
        """
        Track service costs.

        Args:
            service: Service name
            cost: Cost to add
            budget_daily: Daily budget
            budget_monthly: Monthly budget
            warn_threshold: Warning threshold (0.0-1.0)

        Returns:
            Cost metrics
        """
        # Add to history
        self.cost_history[service].append(cost)

        # Calculate totals
        today = datetime.now().date()
        month_start = datetime(today.year, today.month, 1).date()

        cost_today = sum(self.cost_history[service])  # Simplified for now
        cost_month = cost_today  # Simplified for now

        usage_daily = (cost_today / budget_daily) * 100 if budget_daily > 0 else 0
        usage_monthly = (cost_month / budget_monthly) * 100 if budget_monthly > 0 else 0

        metrics = CostMetrics(
            service=service,
            cost_today=round(cost_today, 2),
            cost_month=round(cost_month, 2),
            budget_daily=budget_daily,
            budget_monthly=budget_monthly,
            usage_percent_daily=round(usage_daily, 2),
            usage_percent_monthly=round(usage_monthly, 2),
            timestamp=datetime.now().isoformat(),
        )

        self.cost_metrics[service] = metrics

        # Create alerts
        if usage_daily >= warn_threshold * 100:
            self.create_alert(
                type=AlertType.COST_BUDGET,
                severity=(
                    AlertSeverity.WARNING if usage_daily < 100 else AlertSeverity.ERROR
                ),
                message=f"{service} daily cost: ${cost_today:.2f}/${budget_daily:.2f} ({usage_daily:.1f}%)",
                service=service,
                metadata={"cost": cost_today, "budget": budget_daily},
            )

        if usage_monthly >= warn_threshold * 100:
            self.create_alert(
                type=AlertType.COST_BUDGET,
                severity=(
                    AlertSeverity.WARNING
                    if usage_monthly < 100
                    else AlertSeverity.ERROR
                ),
                message=f"{service} monthly cost: ${cost_month:.2f}/${budget_monthly:.2f} ({usage_monthly:.1f}%)",
                service=service,
                metadata={"cost": cost_month, "budget": budget_monthly},
            )

        logger.info(
            f"[WIZ] Cost tracking: {service} = ${cost_today:.2f} today, ${cost_month:.2f} this month"
        )

        return metrics

    def get_cost_summary(self, service: Optional[str] = None) -> Dict[str, CostMetrics]:
        """Get cost summary"""
        if service:
            return {service: self.cost_metrics.get(service)}
        return self.cost_metrics

    # -------------------------------------------------------------------------
    # Audit Logging
    # -------------------------------------------------------------------------

    def audit_log(
        self,
        operation: str,
        service: str,
        user: str = "system",
        success: bool = True,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> AuditLogEntry:
        """
        Create audit log entry.

        Args:
            operation: Operation name
            service: Service name
            user: User performing operation
            success: Whether operation succeeded
            duration_ms: Operation duration
            metadata: Additional metadata
            error: Error message if failed

        Returns:
            Audit log entry
        """
        entry = AuditLogEntry(
            id=f"audit-{int(time.time() * 1000)}",
            timestamp=datetime.now().isoformat(),
            operation=operation,
            service=service,
            user=user,
            success=success,
            duration_ms=duration_ms,
            metadata=metadata,
            error=error,
        )

        self.audit_entries.append(entry)

        # Log to file
        log_level = logger.info if success else logger.error
        log_level(
            f"[AUDIT] {operation} on {service} by {user}: {'success' if success else 'failed'}"
        )

        # Save periodically
        if len(self.audit_entries) % 100 == 0:
            self._save_audit_log()

        return entry

    def get_audit_log(
        self,
        operation: Optional[str] = None,
        service: Optional[str] = None,
        user: Optional[str] = None,
        success_only: Optional[bool] = None,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """Get audit log entries with optional filtering"""
        filtered = self.audit_entries

        if operation:
            filtered = [e for e in filtered if e.operation == operation]

        if service:
            filtered = [e for e in filtered if e.service == service]

        if user:
            filtered = [e for e in filtered if e.user == user]

        if success_only is not None:
            filtered = [e for e in filtered if e.success == success_only]

        # Sort by timestamp descending
        filtered.sort(key=lambda e: e.timestamp, reverse=True)

        return filtered[:limit]

    # -------------------------------------------------------------------------
    # State Persistence
    # -------------------------------------------------------------------------

    def _save_alerts(self):
        """Save alerts to disk"""
        alerts_file = self.data_dir / "alerts.json"
        with open(alerts_file, "w") as f:
            json.dump([a.to_dict() for a in self.alerts], f, indent=2)

    def _save_audit_log(self):
        """Save audit log to disk"""
        # Save to dated file
        today = datetime.now().strftime("%Y-%m-%d")
        audit_file = self.data_dir / f"audit-{today}.json"

        with open(audit_file, "w") as f:
            json.dump([e.to_dict() for e in self.audit_entries], f, indent=2)

    def _load_state(self):
        """Load persisted state"""
        # Load alerts
        alerts_file = self.data_dir / "alerts.json"
        if alerts_file.exists():
            try:
                with open(alerts_file) as f:
                    data = json.load(f)
                    self.alerts = [Alert(**a) for a in data]
                logger.info(f"[WIZ] Loaded {len(self.alerts)} alerts")
            except Exception as e:
                logger.error(f"[WIZ] Failed to load alerts: {e}")

    def export_state(self, filepath: Path):
        """Export monitoring state"""
        state = {
            "health_checks": {k: v.to_dict() for k, v in self.health_checks.items()},
            "alerts": [a.to_dict() for a in self.alerts],
            "rate_limits": {k: v.to_dict() for k, v in self.rate_limits.items()},
            "cost_metrics": {k: v.to_dict() for k, v in self.cost_metrics.items()},
            "audit_log": [
                e.to_dict() for e in self.audit_entries[-1000:]
            ],  # Last 1000 entries
            "exported_at": datetime.now().isoformat(),
        }

        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"[WIZ] Monitoring state exported to {filepath}")
