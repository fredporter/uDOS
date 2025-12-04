# Webhook Analytics Guide (v1.2.6)

## Overview

v1.2.6 adds comprehensive analytics and event history tracking to the webhook system introduced in v1.2.5. Every webhook event is now automatically logged to a SQLite database, enabling:

- **Event History** - Browse all webhook events with filtering
- **Performance Analytics** - Track success rates and response times
- **Platform Metrics** - Monitor usage across GitHub, Slack, Notion, ClickUp
- **Event Replay** - Re-execute webhook events for debugging
- **Error Tracking** - View recent failures and error trends

## Architecture

### Event Storage (`webhook_event_store.py`)

SQLite-based persistence layer that records every webhook event with:

- **Event Metadata**: ID, webhook_id, platform, event_type, timestamp
- **Execution Data**: Payload, headers, execution_time_ms
- **Response Data**: Status (success/error), response_data, error message
- **Analytics**: Indexes for fast querying by platform, event type, date

**Database Schema:**
```sql
CREATE TABLE webhook_events (
    id TEXT PRIMARY KEY,              -- evt_abc123
    webhook_id TEXT NOT NULL,          -- wh_def456
    platform TEXT NOT NULL,            -- github, slack, notion, clickup
    event_type TEXT NOT NULL,          -- push, pull_request, message, etc.
    payload TEXT NOT NULL,             -- JSON payload
    headers TEXT,                      -- Request headers JSON
    response_status TEXT NOT NULL,     -- success | error
    response_data TEXT,                -- Response JSON
    execution_time_ms REAL NOT NULL,   -- Execution duration
    error TEXT,                        -- Error message if failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_webhook_id ON webhook_events(webhook_id);
CREATE INDEX idx_platform ON webhook_events(platform);
CREATE INDEX idx_created_at ON webhook_events(created_at);
CREATE INDEX idx_event_type ON webhook_events(event_type);
```

### Event Logging Integration

The `webhook_receive` endpoint automatically logs events:

```python
@app.route('/api/webhooks/receive/<platform>', methods=['POST'])
def webhook_receive(platform):
    start_time = time.time()
    event_store = get_event_store()

    try:
        # Process webhook...

        # Record successful event
        execution_time_ms = (time.time() - start_time) * 1000
        event_id = event_store.record_event(
            webhook_id=webhook.id,
            platform=platform,
            event_type=event_type,
            payload=data,
            headers=dict(request.headers),
            response_status="success",
            response_data=response_data,
            execution_time_ms=execution_time_ms
        )

        return jsonify({...., "event_id": event_id})

    except Exception as e:
        # Record failed event
        event_store.record_event(..., error=str(e))
```

## API Endpoints

### 1. List Events

Get paginated event history with optional filtering.

**Request:**
```http
GET /api/webhooks/events?platform=github&limit=50&offset=0&webhook_id=wh_abc123&event_type=push
```

**Parameters:**
- `platform` (optional) - Filter by platform (github, slack, notion, clickup)
- `webhook_id` (optional) - Filter by webhook ID
- `event_type` (optional) - Filter by event type
- `limit` (default: 50) - Max events to return
- `offset` (default: 0) - Pagination offset

**Response:**
```json
{
  "status": "success",
  "events": [
    {
      "id": "evt_abc123",
      "webhook_id": "wh_def456",
      "platform": "github",
      "event_type": "push",
      "payload": {...},
      "headers": {...},
      "response_status": "success",
      "response_data": {...},
      "execution_time_ms": 45.23,
      "error": null,
      "created_at": "2025-12-04T10:30:00Z"
    }
  ],
  "count": 1,
  "limit": 50,
  "offset": 0
}
```

### 2. Get Event Details

Retrieve full details for a specific event.

**Request:**
```http
GET /api/webhooks/events/evt_abc123
```

**Response:**
```json
{
  "status": "success",
  "event": {
    "id": "evt_abc123",
    "webhook_id": "wh_def456",
    "platform": "github",
    "event_type": "push",
    "payload": {
      "ref": "refs/heads/main",
      "repository": {"name": "my-repo"},
      "commits": [...]
    },
    "headers": {
      "X-Hub-Signature-256": "sha256=...",
      "Content-Type": "application/json"
    },
    "response_status": "success",
    "response_data": {
      "status": "success",
      "actions_triggered": 2,
      "results": [...]
    },
    "execution_time_ms": 45.23,
    "error": null,
    "created_at": "2025-12-04T10:30:00Z"
  }
}
```

### 3. Get Analytics

Retrieve aggregated metrics for a time period.

**Request:**
```http
GET /api/webhooks/analytics?days=7
```

**Parameters:**
- `days` (default: 7) - Number of days to analyze

**Response:**
```json
{
  "status": "success",
  "analytics": {
    "total_events": 127,
    "successful_events": 121,
    "failed_events": 6,
    "success_rate": 95.3,
    "avg_execution_time": 42.5,
    "platforms": {
      "github": 85,
      "slack": 30,
      "notion": 12
    },
    "event_types": {
      "push": 60,
      "pull_request": 25,
      "message": 30,
      "page_created": 12
    },
    "period_start": "2025-11-27T00:00:00Z",
    "period_end": "2025-12-04T23:59:59Z"
  },
  "period_days": 7
}
```

### 4. Replay Event

Re-execute a webhook event using its original payload.

**Request:**
```http
POST /api/webhooks/events/evt_abc123/replay
```

**Response:**
```json
{
  "status": "success",
  "event_id": "evt_abc123",
  "original_event": {
    "id": "evt_abc123",
    "webhook_id": "wh_def456",
    "platform": "github",
    "event_type": "push",
    "created_at": "2025-12-04T10:30:00Z"
  },
  "actions_triggered": 2,
  "results": [
    {
      "action": "workflow",
      "workflow": "deploy.upy",
      "status": "triggered"
    },
    {
      "action": "command",
      "command": "NOTIFY 'Deployment started'",
      "status": "triggered"
    }
  ]
}
```

### 5. Delete Event

Remove an event from history.

**Request:**
```http
DELETE /api/webhooks/events/evt_abc123
```

**Response:**
```json
{
  "status": "success",
  "message": "Event evt_abc123 deleted"
}
```

## Analytics Dashboard Widget

The analytics widget provides real-time visualization of webhook metrics.

### Setup

1. **Include JavaScript and CSS:**
```html
<link rel="stylesheet" href="/widgets/analytics-widget.css">
<script src="/widgets/analytics-widget.js"></script>
```

2. **Create Widget Container:**
```html
<div id="analytics-container"></div>
```

3. **Initialize Widget:**
```javascript
const analyticsWidget = new AnalyticsWidget('analytics-container', {
    apiBaseUrl: 'http://localhost:5001/api',
    refreshInterval: 30000,  // 30 seconds
    days: 7                   // Last 7 days
});

// Make available globally for event handlers
window.analyticsWidget = analyticsWidget;
```

### Features

**Metrics Cards:**
- Total Events - Count of all webhook events
- Success Rate - Percentage of successful executions
- Avg Response Time - Mean execution duration in milliseconds
- Failed Events - Count of errors

**Charts:**
- Events Over Time - Timeline visualization
- Platform Distribution - Pie chart showing event counts per platform

**Recent Events:**
- List of latest webhook events
- Status indicators (✓ success, ✗ error)
- Execution time for each event
- View/Replay actions

**Recent Errors:**
- Latest failed webhook events
- Error messages
- Quick access to event details

### Customization

**Period Selector:**
```javascript
// Change analytics period
document.getElementById('analytics-period').value = '30';  // 30 days
widget.config.days = 30;
widget.loadAnalytics();
```

**Refresh Interval:**
```javascript
// Update every 60 seconds
widget.config.refreshInterval = 60000;
widget.stopAutoRefresh();
widget.startAutoRefresh();
```

**Styling:**
```css
/* Customize colors */
.analytics-widget {
    background: #1a1a1a;
    color: #fff;
}

.metric-value {
    color: #4CAF50;  /* Green for metrics */
}
```

## Event Replay System

Event replay allows re-executing webhook events for debugging and testing.

### Use Cases

1. **Debugging** - Replay failed events to diagnose issues
2. **Testing** - Verify workflow changes with historical events
3. **Recovery** - Re-process events that failed due to temporary issues
4. **Validation** - Test webhook handlers with real payloads

### How It Works

1. Event is retrieved from database with original payload
2. Webhook configuration is fetched
3. Actions are re-executed (workflows, commands)
4. New event is NOT created (replay doesn't log)

**Example:**
```bash
# Replay event via API
curl -X POST http://localhost:5001/api/webhooks/events/evt_abc123/replay

# Via dashboard widget
// Click "Replay" button on event item
window.analyticsWidget.replayEvent('evt_abc123');
```

## Data Retention

The event store includes automatic cleanup for old events.

### Cleanup Policy

- **Default Retention**: 90 days
- **Automatic Cleanup**: Runs on store initialization
- **Manual Cleanup**: Call `cleanup_old_events(days=90)`

**Example:**
```python
from core.services.webhook_event_store import get_event_store

event_store = get_event_store()

# Clean events older than 30 days
deleted_count = event_store.cleanup_old_events(days=30)
print(f"Deleted {deleted_count} old events")
```

### Database Size Management

Monitor database size:
```bash
# Check database file size
ls -lh memory/system/webhook_events.db

# Count total events
sqlite3 memory/system/webhook_events.db "SELECT COUNT(*) FROM webhook_events;"

# Count events by platform
sqlite3 memory/system/webhook_events.db "
  SELECT platform, COUNT(*)
  FROM webhook_events
  GROUP BY platform;"
```

## Performance Considerations

### Indexes

All queries use database indexes for performance:
- `idx_webhook_id` - Fast lookup by webhook
- `idx_platform` - Filter by platform
- `idx_created_at` - Time range queries
- `idx_event_type` - Filter by event type

### Thread Safety

Event store uses locking for thread-safe operations:
```python
with self.lock:
    # Database operations are thread-safe
    event_id = self.record_event(...)
```

### Bulk Operations

For high-volume scenarios, batch operations can be optimized:
```python
# Record multiple events efficiently
with event_store._get_connection() as conn:
    cursor = conn.cursor()
    for event_data in events:
        cursor.execute('INSERT INTO webhook_events ...', event_data)
    conn.commit()
```

## Testing

Run the analytics test suite:

```bash
# Start API server
python extensions/api/server.py

# Run tests in another terminal
python dev/scripts/test_webhook_analytics.py
```

**Test Coverage:**
1. ✓ Event logging during webhook processing
2. ✓ Multiple events across platforms
3. ✓ List events with filtering
4. ✓ Get event details
5. ✓ Analytics metrics calculation
6. ✓ Event replay functionality
7. ✓ Event deletion
8. ✓ Cleanup and teardown

## Troubleshooting

### Events Not Being Logged

**Symptom**: Webhooks work but no events appear in history.

**Solution**:
```python
# Check event store initialization
from core.services.webhook_event_store import get_event_store
store = get_event_store()
print(store.db_path)  # Should be memory/system/webhook_events.db

# Verify database exists
import os
print(os.path.exists('memory/system/webhook_events.db'))
```

### Analytics Show Zero Events

**Symptom**: Analytics endpoint returns zero events despite logged events.

**Solution**:
```python
# Check date range
from datetime import datetime, timedelta
recent = datetime.now() - timedelta(days=7)

# List events manually
events = store.list_events(limit=10)
print(f"Total events: {len(events)}")
```

### High Database Size

**Symptom**: `webhook_events.db` grows too large.

**Solution**:
```bash
# Run cleanup
python -c "
from core.services.webhook_event_store import get_event_store
store = get_event_store()
deleted = store.cleanup_old_events(days=30)
print(f'Deleted {deleted} events')
"

# Vacuum database to reclaim space
sqlite3 memory/system/webhook_events.db "VACUUM;"
```

## Integration Examples

### Custom Analytics Dashboard

```javascript
// Fetch and display custom metrics
async function showCustomMetrics() {
    const res = await fetch('http://localhost:5001/api/webhooks/analytics?days=30');
    const data = await res.json();

    const analytics = data.analytics;

    console.log(`Success Rate: ${analytics.success_rate}%`);
    console.log(`Avg Response: ${analytics.avg_execution_time}ms`);

    // Show platform breakdown
    Object.entries(analytics.platforms).forEach(([platform, count]) => {
        console.log(`${platform}: ${count} events`);
    });
}
```

### Monitoring Alerts

```python
# Alert on low success rate
from core.services.webhook_event_store import get_event_store

store = get_event_store()
analytics = store.get_analytics(days=1)

if analytics['success_rate'] < 95:
    print(f"⚠️  WARNING: Success rate dropped to {analytics['success_rate']}%")
    print(f"   Failed events: {analytics['failed_events']}")
```

### Event Export

```python
# Export events to JSON
import json

events = store.list_events(limit=1000)
with open('webhook_events_export.json', 'w') as f:
    json.dump(events, f, indent=2)
```

## Next Steps

With v1.2.6 analytics in place, consider:

1. **v1.2.7** - Cloud sync for webhook events (multi-node deployments)
2. **Alerting** - Slack/email notifications for webhook failures
3. **Advanced Charts** - Integration with Chart.js for better visualizations
4. **Event Filtering** - More sophisticated query capabilities
5. **Webhook Templates** - Pre-configured webhooks for common scenarios

---

**Version**: 1.2.6
**Last Updated**: December 4, 2025
**Related**: [Webhook Integration Guide](Webhook-Integration-Guide.md), [API Reference](Command-Reference.md)
