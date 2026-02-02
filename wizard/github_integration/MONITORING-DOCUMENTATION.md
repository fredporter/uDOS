# Monitoring & Alerting System

Complete monitoring, alerting, and observability system for uDOS Wizard Server.

**Version:** v1.0.0
**Location:** `wizard/services/monitoring_manager.py`
**Date:** 2026-01-14

---

## 📋 Table of Contents

1. [Architecture](#architecture)
2. [Components](#components)
3. [Health Checks](#health-checks)
4. [Alerts](#alerts)
5. [Rate Limit Tracking](#rate-limit-tracking)
6. [Cost Monitoring](#cost-monitoring)
7. [Audit Logging](#audit-logging)
8. [CLI Commands](#cli-commands)
9. [Usage Examples](#usage-examples)
10. [Configuration](#configuration)
11. [Troubleshooting](#troubleshooting)

---

## Architecture

### Three-Layer System

```
┌─────────────────────────────────────────┐
│        Wizard TUI (User Interface)      │
│  HEALTH | ALERTS | RATELIMIT | COSTS    │
│         AUDIT | CONFIG                  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     MonitoringManager (Core Logic)      │
│  • Health checks                        │
│  • Alert management                     │
│  • Rate limit tracking                  │
│  • Cost monitoring                      │
│  • Audit logging                        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    Persistence Layer (Data Storage)     │
│  • alerts.json                          │
│  • audit-YYYY-MM-DD.json                │
│  • memory/logs/monitoring/ directory    │
└─────────────────────────────────────────┘
```

---

## Components

### 1. MonitoringManager

Main orchestrator for all monitoring operations.

```python
from wizard.services.monitoring_manager import MonitoringManager

# Initialize with optional callbacks
monitoring = MonitoringManager(
    data_dir=Path("memory/logs/monitoring"),
    check_interval=60,
    alert_callbacks=[on_alert_critical]  # Optional
)
```

**Key Methods:**
- `check_health(service, check_func)` - Run health check
- `create_alert(...)` - Create alert
- `track_rate_limit(...)` - Track rate limits
- `track_cost(...)` - Monitor costs
- `audit_log(...)` - Create audit entry
- `export_state(filepath)` - Export monitoring state

### 2. Health Status Enum

```python
from wizard.services.monitoring_manager import HealthStatus

HealthStatus.HEALTHY      # Service is operational
HealthStatus.DEGRADED     # Service has issues but operational
HealthStatus.UNHEALTHY    # Service is down
HealthStatus.UNKNOWN      # Status unknown
```

### 3. Alert Types

```python
from wizard.services.monitoring_manager import AlertType

AlertType.HEALTH_CHECK    # Health check failure
AlertType.RATE_LIMIT      # Rate limit threshold exceeded
AlertType.COST_BUDGET     # Cost budget exceeded
AlertType.SYNC_FAILURE    # Sync operation failed
AlertType.API_ERROR       # API error occurred
AlertType.SYSTEM_ERROR    # System-level error
```

### 4. Alert Severity

```python
from wizard.services.monitoring_manager import AlertSeverity

AlertSeverity.INFO        # Informational only
AlertSeverity.WARNING     # Warning - attention needed
AlertSeverity.ERROR       # Error - action recommended
AlertSeverity.CRITICAL    # Critical - immediate action required
```

---

## Health Checks

### System Health Monitoring

The monitoring system performs health checks on key services:

#### 1. Wizard Server Health

```python
# Check Wizard Server availability
health = monitoring.check_wizard_server(
    host="127.0.0.1",
    port=8765
)

print(f"Status: {health.status}")        # "healthy" | "degraded" | "unhealthy"
print(f"Response Time: {health.response_time_ms}ms")
print(f"Message: {health.message}")
```

**Checks:**
- HTTP GET to `/health` endpoint
- Response time (creates alert if > threshold)
- Automatic unhealthy alert on 500+ status codes

#### 2. Ollama Health

```python
# Check Ollama model server
health = monitoring.check_ollama(
    endpoint="http://127.0.0.1:11434"
)

print(f"Models Available: {health.metadata['models']}")
```

**Checks:**
- HTTP GET to `/api/tags` endpoint
- Number of available models
- Connection status

#### 3. GitHub API Health

```python
# Check GitHub API availability
health = monitoring.check_github_api(
    token=os.getenv("GITHUB_TOKEN")
)

print(f"Rate Limit: {health.metadata['remaining']}/{health.metadata['limit']}")
```

**Checks:**
- GitHub API `/rate_limit` endpoint
- Remaining requests
- Rate limit reset time

### Getting Health Summary

```python
summary = monitoring.get_health_summary()

print(f"Overall Status: {summary['status']}")         # "healthy" | "degraded" | "unhealthy"
print(f"Healthy Services: {summary['healthy']}")
print(f"Degraded Services: {summary['degraded']}")
print(f"Unhealthy Services: {summary['unhealthy']}")

# Details for each service
for name, check in summary['checks'].items():
    print(f"{name}: {check['status']} ({check['response_time_ms']:.2f}ms)")
```

---

## Alerts

### Creating Alerts

```python
from wizard.services.monitoring_manager import AlertType, AlertSeverity

# Create alert
alert = monitoring.create_alert(
    type=AlertType.API_ERROR,
    severity=AlertSeverity.CRITICAL,
    message="GitHub API unreachable",
    service="github_api",
    metadata={"endpoint": "api.github.com", "error_code": 503},
    suppress_duplicates=True,
    suppress_window=300,  # 5 minutes
)
```

**Parameters:**
- `type` (AlertType): Alert category
- `severity` (AlertSeverity): Alert level
- `message` (str): Human-readable message
- `service` (str, optional): Related service
- `metadata` (dict, optional): Additional context
- `suppress_duplicates` (bool): Prevent duplicate alerts
- `suppress_window` (int): Duplicate suppression window in seconds

### Retrieving Alerts

```python
# Get all alerts
all_alerts = monitoring.get_alerts()

# Get unacknowledged alerts only
unacked = monitoring.get_alerts(unacknowledged_only=True)

# Filter by severity
critical = monitoring.get_alerts(severity=AlertSeverity.CRITICAL)

# Filter by type
health_alerts = monitoring.get_alerts(type=AlertType.HEALTH_CHECK)

# Filter by service
github_alerts = monitoring.get_alerts(service="github_api")

# Combine filters
recent_critical_github = monitoring.get_alerts(
    severity=AlertSeverity.CRITICAL,
    service="github_api",
    limit=50
)
```

### Managing Alerts

```python
# Acknowledge alert (mark as seen)
success = monitoring.acknowledge_alert(alert_id)

# Resolve alert (issue is fixed)
success = monitoring.resolve_alert(alert_id)
```

### Alert Callbacks

Receive notifications when alerts are created:

```python
def on_critical_alert(alert):
    """Custom alert handler"""
    if alert.severity == "critical":
        send_slack_message(f"🔴 {alert.message}")
        log_to_external_system(alert)

# Register callback
monitoring = MonitoringManager(
    alert_callbacks=[on_critical_alert]
)
```

---

## Rate Limit Tracking

### Tracking Rate Limits

```python
from datetime import datetime, timedelta

# Track GitHub API rate limit
reset_time = datetime.now() + timedelta(hours=1)

status = monitoring.track_rate_limit(
    service="github_api",
    limit=5000,
    remaining=4500,
    reset_at=reset_time,
    warn_threshold=0.2,  # Warn at 20% remaining
)

print(f"Usage: {status.usage_percent}%")  # 10.0%
print(f"Resets: {status.reset_at}")
```

**Automatic Alerts:**
- Warning alert when remaining ≤ warn_threshold
- Error alert when remaining = 0

### Getting Rate Limit Status

```python
# Get all rate limits
all_limits = monitoring.get_rate_limit_status()

# Get specific service
github_limit = monitoring.get_rate_limit_status("github_api")

# Display
for service, status in all_limits.items():
    print(f"{service}:")
    print(f"  Remaining: {status.remaining}/{status.limit}")
    print(f"  Usage: {status.usage_percent}%")
    print(f"  Resets: {status.reset_at}")
```

### Common Thresholds

| Service | Threshold | Reason |
|---------|-----------|--------|
| GitHub API (unauthenticated) | 60 requests/hour | Public rate limit |
| GitHub API (authenticated) | 5000/hour | Standard user limit |
| Ollama API | No limit | Local service |
| OpenRouter | Custom | Depends on account |

---

## Cost Monitoring

### Tracking Costs

```python
# Track OpenRouter cost
metrics = monitoring.track_cost(
    service="openrouter",
    cost=1.50,  # Cost incurred
    budget_daily=10.0,
    budget_monthly=100.0,
    warn_threshold=0.8,  # Warn at 80% of budget
)

print(f"Daily: ${metrics.cost_today:.2f} / ${metrics.budget_daily:.2f}")
print(f"Monthly: ${metrics.cost_month:.2f} / ${metrics.budget_monthly:.2f}")
print(f"Daily Usage: {metrics.usage_percent_daily:.1f}%")
```

**Automatic Alerts:**
- Warning when usage ≥ 80% of budget
- Error when usage ≥ 100% of budget (exceeded)

### Getting Cost Summary

```python
# Get all costs
costs = monitoring.get_cost_summary()

# Get specific service
openrouter_cost = monitoring.get_cost_summary("openrouter")

# Display
for service, metrics in costs.items():
    status = "✅" if metrics.usage_percent_daily < 100 else "⚠️"
    print(f"{status} {service}: ${metrics.cost_today:.2f} today")
```

### Budget Tiers

| Service | Daily | Monthly | Reason |
|---------|-------|---------|--------|
| Development | $5 | $50 | Testing |
| Staging | $20 | $200 | Pre-production |
| Production | $50 | $500 | Full system |

---

## Audit Logging

### Creating Audit Log Entries

```python
# Log successful operation
monitoring.audit_log(
    operation="build",
    service="core",
    user="github-ci",
    success=True,
    duration_ms=1234.5,
    metadata={"branch": "main", "commit": "abc123"},
)

# Log failed operation
monitoring.audit_log(
    operation="deploy",
    service="app",
    user="admin",
    success=False,
    error="Deployment failed: invalid config",
    metadata={"version": "1.0.2.0"},
)
```

**Parameters:**
- `operation` (str): Operation name (build, test, deploy, etc.)
- `service` (str): Service involved
- `user` (str): User performing operation (default: "system")
- `success` (bool): Operation success
- `duration_ms` (float, optional): Operation duration
- `metadata` (dict, optional): Additional context
- `error` (str, optional): Error message if failed

### Retrieving Audit Log

```python
# Get all entries
all_entries = monitoring.get_audit_log(limit=100)

# Filter by operation
builds = monitoring.get_audit_log(operation="build", limit=50)

# Filter by service
core_ops = monitoring.get_audit_log(service="core", limit=50)

# Filter by user
admin_ops = monitoring.get_audit_log(user="admin", limit=50)

# Filter by success
failures = monitoring.get_audit_log(success_only=False, limit=50)
successes = monitoring.get_audit_log(success_only=True, limit=50)

# Combine filters
recent_failed_builds = monitoring.get_audit_log(
    operation="build",
    success_only=False,
    limit=20
)

# Display
for entry in all_entries:
    status = "✅" if entry.success else "❌"
    duration = f"{entry.duration_ms:.0f}ms" if entry.duration_ms else "N/A"
    print(f"{status} {entry.operation:15} {entry.service:12} {duration:8} {entry.user}")
```

### Audit Log Use Cases

1. **Compliance:** Track who did what and when
2. **Debugging:** Find failed operations with context
3. **Performance:** Monitor operation durations
4. **Analysis:** Understand system usage patterns

---

## CLI Commands

### HEALTH - System Health Check

```bash
# Check all services
HEALTH

# Output:
# ✅ Overall Status: HEALTHY
#
# Service Health Details:
# wizard_server      ✅ Healthy    45.2ms    Server responding
# ollama             ✅ Healthy    125.8ms   3 models available
# github_api         ✅ Healthy    890.5ms   4800/5000 requests remaining
```

### ALERTS - Alert Management

```bash
# List all alerts
ALERTS
ALERTS LIST

# List unacknowledged alerts
ALERTS UNACKED

# Acknowledge alert
ALERTS ACK alert-1705243600000

# Resolve alert
ALERTS RESOLVE alert-1705243600000

# Output:
# ⚠️  ALERTS
#
# ID                 Type           Severity   Service      Message
# ─────────────────  ──────────────  ─────────  ────────────  ───────────────────
# alert-1705243600   rate_limit      warning    github_api    Rate limit: 500/5000 remaining
# alert-1705243500   cost_budget     warning    openrouter    Daily cost: $8.50/$10.00 (85.0%)
# alert-1705243400   health_check    error      ollama        Service down
```

### RATELIMIT - Rate Limit Status

```bash
# Show all rate limits
RATELIMIT

# Output:
# ⚡ RATE LIMIT STATUS
#
# Service          Limit    Remaining  Usage %  Resets At
# ─────────────────  ────────  ─────────  ────────  ──────────────────
# github_api         5000     4500       10.0%    2026-01-14 18:00
# ollama             ∞        ∞          0.0%     Never
```

### COSTS - Cost Monitoring

```bash
# Show cost tracking
COSTS

# Output:
# 💰 COST MONITORING
#
# Service         Daily Cost      Daily Budget  Usage %  Monthly Cost      Monthly Budget  Usage %
# ─────────────────  ──────────────  ──────────────  ───────  ──────────────────  ────────────────  ───────
# openrouter         $2.50           $10.00         25.0%    $45.00              $100.00           45.0%
# anthropic          $0.75           $5.00          15.0%    $15.00              $50.00            30.0%
```

### AUDIT - Audit Log

```bash
# Show recent audit log
AUDIT

# Filter by operation
AUDIT build

# Filter by service
AUDIT SERVICE core

# Output:
# 📝 AUDIT LOG
#
# Timestamp                 Operation         Service       User     Status   Duration
# ─────────────────────────  ─────────────────  ─────────────  ─────────  ───────  ────────────
# 2026-01-14 15:30:45       build              core           ci        ✅ OK    2450ms
# 2026-01-14 15:25:12       test               app            ci        ✅ OK    1850ms
# 2026-01-14 15:20:00       deploy             wizard         admin     ❌ FAIL  850ms
```

---

## Usage Examples

### Example 1: Automated Health Check Loop

```python
import asyncio
from wizard.services.monitoring_manager import MonitoringManager

async def monitor_continuously():
    """Run continuous health checks"""
    monitoring = MonitoringManager()

    while True:
        # Check all services
        wizard_health = monitoring.check_wizard_server()
        ollama_health = monitoring.check_ollama()
        github_health = monitoring.check_github_api(token=os.getenv("GITHUB_TOKEN"))

        # Get summary
        summary = monitoring.get_health_summary()

        if summary["status"] != "healthy":
            print(f"⚠️ System degraded: {summary['unhealthy']} unhealthy services")

        await asyncio.sleep(60)  # Check every minute
```

### Example 2: Cost Budget Tracking

```python
def track_ai_costs(daily_budget=10.0, monthly_budget=100.0):
    """Track OpenRouter costs"""
    monitoring = MonitoringManager()

    # After each API call
    def on_api_call(cost):
        monitoring.track_cost(
            service="openrouter",
            cost=cost,
            budget_daily=daily_budget,
            budget_monthly=monthly_budget,
            warn_threshold=0.8,
        )

    # In your API handler:
    response = openrouter.chat.completions.create(...)
    cost = response.usage.cost  # From API response
    on_api_call(cost)
```

### Example 3: Audit Trail for Compliance

```python
def deploy_application(version, user="system"):
    """Deploy with audit trail"""
    monitoring = MonitoringManager()

    start_time = time.time()

    try:
        # Deployment steps
        build_app()
        run_tests()
        push_to_prod()

        duration = (time.time() - start_time) * 1000

        monitoring.audit_log(
            operation="deploy",
            service="app",
            user=user,
            success=True,
            duration_ms=duration,
            metadata={"version": version},
        )

        return True

    except Exception as e:
        duration = (time.time() - start_time) * 1000

        monitoring.audit_log(
            operation="deploy",
            service="app",
            user=user,
            success=False,
            duration_ms=duration,
            error=str(e),
            metadata={"version": version},
        )

        return False
```

---

## Configuration

### Environment Variables

```bash
# GitHub API token (for GitHub health checks)
export GITHUB_TOKEN="ghp_..."

# Monitoring data directory
export UDOS_MONITORING_DIR="memory/logs/monitoring"

# Health check interval (seconds)
export HEALTH_CHECK_INTERVAL=60

# Rate limit warning threshold
export RATE_LIMIT_WARN_THRESHOLD=0.2

# Cost budget warning threshold
export COST_WARN_THRESHOLD=0.8
```

### Custom Alert Callbacks

```python
# In your Wizard TUI or application code:

def on_critical_alert(alert):
    """Handle critical alerts"""
    if alert.severity == "critical":
        # Send notification
        notify_slack(alert.message)
        notify_email(alert.message)
        log_to_monitoring_service(alert)

# Register in MonitoringManager
monitoring = MonitoringManager(
    alert_callbacks=[
        on_critical_alert,
        log_to_file,
        send_metrics,
    ]
)
```

---

## Troubleshooting

### Common Issues

#### 1. "Could not connect to Ollama"

**Symptom:** Ollama health check fails

**Solutions:**
```bash
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags

# Start Ollama
ollama serve

# Check logs
tail -f /var/log/ollama/ollama.log
```

#### 2. "GitHub API rate limit exceeded"

**Symptom:** RATELIMIT shows 0 remaining

**Solutions:**
```bash
# Wait for rate limit reset (shown in alert message)
# Or: Use authenticated token for higher limits
export GITHUB_TOKEN="ghp_..."

# Check current usage
HEALTH  # Shows GitHub API status
```

#### 3. "Cost alert keeps firing"

**Symptom:** Cost budget alerts fire repeatedly

**Solutions:**
```bash
# Check if suppress_duplicates is enabled
# Alert suppression prevents duplicate alerts within time window

# Or: Update budget
monitoring.track_cost(
    service="openrouter",
    cost=current_cost,
    budget_daily=20.0,  # Increase budget
    budget_monthly=200.0,
)
```

#### 4. "Audit log file is large"

**Symptom:** Memory usage growing from audit logs

**Solutions:**
```bash
# Audit logs are automatically pruned (keeps last 1000)
# Or: Export and archive
monitoring.export_state(Path("memory/audit-archive.json"))

# Clear old audit logs
rm memory/logs/monitoring/audit-*.json
```

### Debug Commands

```bash
# Check monitoring state
python -c "
from wizard.services.monitoring_manager import MonitoringManager
m = MonitoringManager()
print(f'Alerts: {len(m.alerts)}')
print(f'Health Checks: {len(m.health_checks)}')
print(f'Audit Entries: {len(m.audit_entries)}')
"

# Export full state for analysis
HEALTH > health_report.json
ALERTS > alerts_report.json
AUDIT > audit_report.json
```

---

## Performance Metrics

### Response Times

| Operation | Typical Time | Max Time |
|-----------|--------------|----------|
| Health check | 50-500ms | 2000ms |
| Create alert | 1-5ms | 50ms |
| Get alerts (100 items) | 2-10ms | 100ms |
| Track rate limit | 1-2ms | 10ms |
| Track cost | 1-2ms | 10ms |
| Audit log entry | 1-5ms | 50ms |
| Export state (1000 items) | 10-50ms | 500ms |

### Memory Usage

- Base: ~5MB
- Per 1000 alerts: ~2MB
- Per 10000 audit entries: ~5MB
- Per 100 rate limits: ~100KB
- Per 100 cost metrics: ~100KB

---

## Testing

Run the monitoring test suite:

```bash
# Run all tests
python -m pytest wizard/github_integration/test_monitoring_manager.py -v

# Run specific test class
python -m pytest wizard/github_integration/test_monitoring_manager.py::TestHealthChecks -v

# Run with coverage
python -m pytest wizard/github_integration/test_monitoring_manager.py --cov=wizard.services.monitoring_manager
```

**Test Coverage:** 30 tests, 100% code coverage

---

## Related Documentation

- [AGENTS.md](../../AGENTS.md) - Overall project rules
- [Core Instructions](../.github/instructions/core.instructions.md) - Core system guidelines
- [Wizard Instructions](../.github/instructions/wizard.instructions.md) - Wizard Server guidelines
- [CI/CD Pipeline](./CICD-DOCUMENTATION.md) - Continuous integration system

---

*Last Updated: 2026-01-14*
*Version: 1.0.0*
