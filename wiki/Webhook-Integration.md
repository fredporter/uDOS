# Webhook Integration System

**Version:** 1.2.10
**Status:** Active
**Extension:** `extensions/core/webhooks/`

## Overview

The uDOS Webhook Integration System provides unified event processing for external platforms. It normalizes platform-specific webhook payloads into a consistent format, routes events to handlers, and triggers automated workflows through uCODE scripts.

**Supported Platforms:**
- **GitHub** - Push events, pull requests, issues, releases
- **Slack** - Messages, reactions, mentions, slash commands
- **Notion** - Page updates, database changes
- **ClickUp** - Task updates, comments, status changes

## Architecture

```
┌─────────────┐
│   Platform  │  (GitHub, Slack, Notion, ClickUp)
│   Webhook   │
└──────┬──────┘
       │ POST /webhooks/{platform}
       ▼
┌─────────────────┐
│ Event Processor │  Normalize payload
│  (Platform-     │  • Extract common fields
│   specific)     │  • Map to uDOS event type
└────────┬────────┘  • Generate event ID
         │
         ▼
┌─────────────────┐
│   Event Router  │  Route to handlers
│                 │  • Pattern matching
│                 │  • Priority ordering
└────────┬────────┘  • Async execution
         │
         ├──────────┐──────────┐
         ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌──────────┐
    │Python  │ │uCODE   │ │Extension │
    │Handler │ │Script  │ │Endpoint  │
    └────────┘ └────────┘ └──────────┘
```

## Quick Start

### 1. Enable Webhook Platform

Edit `extensions/core/webhooks/config.json`:

```json
{
  "webhook_system": {
    "platforms": {
      "github": {
        "enabled": true,
        "events": ["push", "pull_request"],
        "filters": {
          "repositories": ["fredporter/uDOS"],
          "exclude_bots": true
        }
      }
    }
  }
}
```

### 2. Set Webhook Secret

Add to `.env`:

```bash
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
```

### 3. Register Event Handler

**Python Handler:**
```python
from extensions.core.webhooks import EventRouter

router = EventRouter()

async def on_code_push(event):
    """Handle GitHub push events."""
    repo = event['source']['repository']
    author = event['payload']['author']
    title = event['payload']['title']

    print(f"📦 {author} pushed to {repo}: {title}")
    return {'notified': True}

# Register handler for push events
router.register_route(
    name='notify_push',
    pattern={'event_type': 'code.pushed'},
    handler=on_code_push,
    priority=50
)
```

**uCODE Script:**
```python
# File: memory/workflows/missions/on_code_push.upy

# Access event data via variables
PRINT "📦 Code pushed to $EVENT.SOURCE.REPOSITORY"
PRINT "Author: $EVENT.PAYLOAD.AUTHOR"
PRINT "Commit: $EVENT.PAYLOAD.TITLE"

# Log to mission system
LOG --mission "code_monitoring" "GitHub push detected"

# Trigger build workflow
IF $EVENT.SOURCE.REPOSITORY == "fredporter/uDOS"
  WORKFLOW run build_and_test.upy
END
```

Register script binding in `config.json`:
```json
{
  "script_bindings": {
    "code.pushed": "memory/workflows/missions/on_code_push.upy"
  }
}
```

## Event Format

All webhook events are normalized to this structure:

```json
{
  "event_id": "unique-uuid",
  "platform": "github|slack|notion|clickup",
  "event_type": "normalized-type",
  "timestamp": "2025-12-06T12:00:00Z",
  "source": {
    "platform": "github",
    "repository": "fredporter/uDOS",
    "sender": "fredporter"
  },
  "payload": {
    "title": "Event title or message",
    "description": "Detailed description",
    "url": "https://github.com/...",
    "state": "open|closed",
    "author": "username"
  },
  "raw": {
    // Original platform payload
  }
}
```

## Event Types

### GitHub Events

| Platform Event | uDOS Event Type | Description |
|----------------|-----------------|-------------|
| `push` | `code.pushed` | Code pushed to repository |
| `pull_request.opened` | `code.pull_request.opened` | PR created |
| `pull_request.closed` | `code.pull_request.closed` | PR merged/closed |
| `issues.opened` | `issue.created` | Issue created |
| `issues.closed` | `issue.closed` | Issue closed |
| `release.published` | `release.published` | Release created |

### Slack Events

| Platform Event | uDOS Event Type | Description |
|----------------|-----------------|-------------|
| `message` | `message.posted` | Message sent |
| `reaction_added` | `message.reacted` | Reaction added |
| `app_mention` | `message.mentioned` | Bot mentioned |
| `slash_command` | `command.invoked` | Slash command used |

### Notion Events

| Platform Event | uDOS Event Type | Description |
|----------------|-----------------|-------------|
| `page.updated` | `page.updated` | Page modified |
| `page.created` | `page.created` | Page created |
| `database.item.created` | `database.item.created` | Database row added |
| `database.item.updated` | `database.item.updated` | Database row updated |

### ClickUp Events

| Platform Event | uDOS Event Type | Description |
|----------------|-----------------|-------------|
| `taskCreated` | `task.created` | Task created |
| `taskUpdated` | `task.updated` | Task modified |
| `taskStatusUpdated` | `task.status.changed` | Status changed |
| `taskCommentPosted` | `task.comment.posted` | Comment added |

## Routing Patterns

Routes match events using patterns:

### Simple Platform Match
```python
pattern = {'platform': 'github'}
# Matches: All GitHub events
```

### Event Type Match
```python
pattern = {'event_type': 'code.pushed'}
# Matches: Only push events
```

### Regex Event Type
```python
pattern = {'event_type': r'code\..*'}
# Matches: code.pushed, code.pull_request.opened, etc.
```

### Source Filter
```python
pattern = {
    'platform': 'github',
    'source': {
        'repository': 'fredporter/uDOS'
    }
}
# Matches: Only events from specific repo
```

### Multiple Event Types
```python
pattern = {
    'event_type': ['code.pushed', 'code.pull_request.opened']
}
# Matches: Push events OR PR opened events
```

## Configuration Reference

### Platform Configuration

```json
{
  "platforms": {
    "github": {
      "enabled": true,
      "webhook_url": "/webhooks/github",
      "secret_env": "GITHUB_WEBHOOK_SECRET",
      "events": ["push", "pull_request", "issues"],
      "filters": {
        "repositories": ["owner/repo"],
        "branches": ["main", "develop"],
        "exclude_bots": true
      }
    }
  }
}
```

### Routing Configuration

```json
{
  "routing": {
    "max_history": 1000,
    "retry_failed": true,
    "max_retries": 3,
    "script_timeout": 30,
    "stop_on_error": false,
    "default_routes": [
      {
        "name": "log_all_events",
        "pattern": {"event_type": ".*"},
        "action": "log",
        "priority": 10,
        "enabled": true
      }
    ]
  }
}
```

### Security Configuration

```json
{
  "security": {
    "verify_signatures": true,
    "allowed_ips": [],
    "rate_limit": {
      "enabled": true,
      "max_requests": 100,
      "window_seconds": 60
    }
  }
}
```

## Usage Examples

### Example 1: Auto-Tag Releases

**Scenario:** Automatically tag GitHub releases in mission system

```python
# File: memory/workflows/missions/tag_releases.upy

IF $EVENT_TYPE == "release.published"
  SET release_name = $EVENT.PAYLOAD.TITLE
  SET repo = $EVENT.SOURCE.REPOSITORY

  PRINT "🚀 New release: $release_name from $repo"

  # Tag in mission system
  MISSION tag --name "release_tracking" \
    --tag "release:$release_name" \
    --tag "repo:$repo"

  # Notify team
  NOTIFY "New release $release_name published!" \
    --channel dashboard
END
```

Register in `config.json`:
```json
{
  "script_bindings": {
    "release.published": "memory/workflows/missions/tag_releases.upy"
  }
}
```

### Example 2: Slack Auto-Response

**Scenario:** Respond to Slack mentions with status

```python
# File: memory/workflows/missions/slack_auto_response.upy

IF $EVENT_TYPE == "message.mentioned"
  SET user = $EVENT.SOURCE.SENDER
  SET text = $EVENT.PAYLOAD.TEXT

  # Check mission status
  SET active_missions = MISSION list --status active --count

  # Generate response
  SET response = "👋 Hi! I have $active_missions active missions."

  # Post to Slack (via API extension)
  API slack post_message \
    --channel $EVENT.PAYLOAD.CHANNEL \
    --text "$response"
END
```

### Example 3: ClickUp Task Sync

**Scenario:** Sync ClickUp tasks to uDOS mission system

```python
# File: memory/workflows/missions/sync_clickup_tasks.upy

IF $EVENT_TYPE == "task.created"
  SET task_title = $EVENT.PAYLOAD.TITLE
  SET task_url = $EVENT.PAYLOAD.URL
  SET assignees = $EVENT.PAYLOAD.ASSIGNEES

  # Create corresponding mission
  MISSION new \
    --name "$task_title" \
    --description "Synced from ClickUp" \
    --metadata "clickup_url:$task_url" \
    --metadata "assignees:$assignees"

  PRINT "✅ Synced ClickUp task: $task_title"
END

IF $EVENT_TYPE == "task.status.changed"
  SET new_status = $EVENT.PAYLOAD.STATUS
  SET task_id = $EVENT.SOURCE.TASK_ID

  # Update mission status
  MISSION update --query "clickup_id:$task_id" \
    --status $new_status

  PRINT "🔄 Updated task status: $new_status"
END
```

## API Reference

### EventProcessor

```python
from extensions.core.webhooks import EventProcessor

processor = EventProcessor()

# Process webhook
event = processor.process('github', raw_payload)

# Get statistics
stats = processor.get_stats()
# {'processed': 42, 'errors': 0, 'by_platform': {'github': 30, 'slack': 12}}
```

### EventRouter

```python
from extensions.core.webhooks import EventRouter

router = EventRouter()

# Register route
async def handler(event):
    print(f"Got event: {event['event_type']}")
    return {'success': True}

router.register_route(
    name='my_handler',
    pattern={'platform': 'github'},
    handler=handler,
    priority=50
)

# Route event
results = await router.route(event)

# Manage routes
router.enable_route('my_handler')
router.disable_route('my_handler')
router.remove_route('my_handler')

# Get history
history = router.get_history(limit=100, event_type='code.pushed')

# Get statistics
stats = router.get_stats()
```

## Testing

### Unit Tests

```bash
# Run all webhook tests
pytest memory/tests/test_event_processing.py -v

# Test specific platform
pytest memory/tests/test_event_processing.py::TestEventProcessor::test_github_push_event -v
```

### Simulate Events

Use the Event Simulator (coming in v1.2.10 Part 3):

```python
from extensions.core.webhooks.simulator import EventSimulator

sim = EventSimulator()

# Simulate GitHub push
event = sim.simulate_github_push(
    repo='fredporter/uDOS',
    author='fredporter',
    message='Add webhook support'
)

# Simulate Slack message
event = sim.simulate_slack_message(
    user='U123',
    text='Hello uDOS!',
    channel='general'
)
```

## Troubleshooting

### Events Not Being Received

1. **Check webhook URL:** Ensure platform webhook is configured correctly
2. **Verify signature:** Check webhook secret in `.env`
3. **Review logs:** `memory/logs/webhook_events.jsonl`
4. **Test endpoint:** Use `curl` to POST test payload

### Handlers Not Executing

1. **Check route pattern:** Ensure pattern matches event type
2. **Verify priority:** Higher priority handlers run first
3. **Check enabled status:** `router.get_route('name').enabled`
4. **Review errors:** `router.get_stats()` shows error counts

### Script Timeout Errors

1. **Increase timeout:** Edit `script_timeout` in config.json
2. **Optimize script:** Reduce complexity or use background tasks
3. **Check dependencies:** Ensure required extensions are loaded

## Security Best Practices

1. **Always verify signatures** - Set `verify_signatures: true`
2. **Use webhook secrets** - Store in `.env`, never commit
3. **Enable rate limiting** - Prevent abuse
4. **Restrict IPs** - Use `allowed_ips` for known sources
5. **Filter events** - Only subscribe to needed event types
6. **Validate payloads** - Check required fields exist
7. **Sanitize data** - Don't trust external input

## Performance

- **Event processing:** ~0.1ms per event (normalization)
- **Route matching:** ~0.05ms per route
- **Handler execution:** Depends on handler complexity
- **Script execution:** 30s default timeout (configurable)
- **Max history:** 1,000 events (configurable)
- **Rate limit:** 100 requests/minute (configurable)

## Roadmap

- **v1.2.10 Part 2:** ✅ REST API Server (COMPLETE)
- **v1.2.10 Part 3:** Event Simulator & Test Panel
- **v1.2.10 Part 4:** Documentation & Examples
- **v1.2.11:** Additional platforms (GitLab, Trello, Jira)
- **v1.2.12:** Webhook templates and marketplace

## REST API Server (v1.2.10)

### Starting the Server

```python
from extensions.core.webhooks.api_server import create_server

# Create and run server
server = create_server(host='0.0.0.0', port=5050)
server.run()

# Or run in debug mode
server.run(debug=True)

# Or run async
import asyncio
asyncio.run(server.run_async())
```

### API Endpoints

**Webhook Receivers:**
- `POST /webhooks/github` - Receive GitHub events
- `POST /webhooks/slack` - Receive Slack events
- `POST /webhooks/notion` - Receive Notion events
- `POST /webhooks/clickup` - Receive ClickUp events

**Event Management:**
- `GET /api/events` - Query event history
  - Params: `limit`, `event_type`, `platform`
- `GET /api/events/{event_id}` - Get specific event

**Route Management:**
- `GET /api/routes` - List all routes
- `GET /api/routes/{name}` - Get route details
- `POST /api/routes/{name}/enable` - Enable route
- `POST /api/routes/{name}/disable` - Disable route
- `DELETE /api/routes/{name}` - Remove route

**System:**
- `GET /api/stats` - Get statistics
- `POST /api/stats/reset` - Reset statistics
- `GET /api/health` - Health check

### Python Client Library

**Synchronous Usage:**
```python
from extensions.core.webhooks.client import WebhookClient

# Create client
client = WebhookClient('http://localhost:5050')

# Query events
events = client.get_events(limit=10, platform='github')
for event in events:
    print(f"{event['event_type']}: {event['payload']['title']}")

# Get specific event
event = client.get_event('event-uuid-here')

# Manage routes
routes = client.get_routes()
route = client.get_route('notify_push')
client.enable_route('notify_push')
client.disable_route('notify_push')
client.delete_route('old_route')

# Get statistics
stats = client.get_stats()
print(f"Total processed: {stats.processor['processed']}")
print(f"API requests: {stats.api['api_requests']}")

# Health check
health = client.health_check()
print(f"Status: {health['status']}")
print(f"Events processed: {health['events_processed']}")
```

**Asynchronous Usage:**
```python
from extensions.core.webhooks.client import WebhookClient

async def main():
    async with WebhookClient('http://localhost:5050') as client:
        # Query events
        events = await client.get_events_async(platform='slack', limit=5)

        # Get routes
        routes = await client.get_routes_async()

        # Manage routes
        await client.enable_route_async('slack_handler')

        # Get stats
        stats = await client.get_stats_async()
        print(f"Routed: {stats.router['global']['routed']}")

import asyncio
asyncio.run(main())
```

**With Authentication:**
```python
# Create client with API key
client = WebhookClient(
    'http://localhost:5050',
    api_key='your-api-key-here'
)

# All requests include Bearer token
events = client.get_events()
```

### Platform Integration Helpers

**GitHub Integration:**
```python
from extensions.core.webhooks.integrations import GitHubIntegration
import os

integration = GitHubIntegration('https://your-server.com')

# Get setup instructions (returns markdown)
instructions = integration.get_setup_instructions('fredporter', 'uDOS')
print(instructions)

# Create webhook via GitHub API
webhook = integration.create_webhook(
    owner='fredporter',
    repo='uDOS',
    token=os.getenv('GITHUB_TOKEN'),
    events=['push', 'pull_request', 'issues']
)
print(f"Webhook created: {webhook['id']}")

# Send test event
success = integration.send_test_event(
    owner='fredporter',
    repo='uDOS',
    token=os.getenv('GITHUB_TOKEN'),
    hook_id=webhook['id']
)
```

**Slack Integration:**
```python
from extensions.core.webhooks.integrations import SlackIntegration
import json

integration = SlackIntegration('https://your-server.com')

# Get app manifest for quick setup
manifest = integration.get_app_manifest(app_name='uDOS Webhook')
print(json.dumps(manifest, indent=2))

# Get setup instructions
instructions = integration.get_setup_instructions('my-workspace')
print(instructions)

# Handle URL verification challenge
challenge_response = integration.verify_url_challenge('challenge-string')
```

**ClickUp Integration:**
```python
from extensions.core.webhooks.integrations import ClickUpIntegration
import os

integration = ClickUpIntegration('https://your-server.com')

# Create webhook
webhook = integration.create_webhook(
    team_id='12345',
    api_token=os.getenv('CLICKUP_API_TOKEN'),
    events=['taskCreated', 'taskUpdated', 'taskStatusUpdated']
)
print(f"Webhook created: {webhook['id']}")

# List webhooks
webhooks = integration.list_webhooks(
    team_id='12345',
    api_token=os.getenv('CLICKUP_API_TOKEN')
)
print(f"Active webhooks: {len(webhooks)}")

# Delete webhook
integration.delete_webhook(
    webhook_id=webhook['id'],
    api_token=os.getenv('CLICKUP_API_TOKEN')
)
```

**Notion Integration:**
```python
from extensions.core.webhooks.integrations import NotionIntegration

integration = NotionIntegration('https://your-server.com')

# Get setup instructions (Notion webhooks are in beta)
instructions = integration.get_setup_instructions()
print(instructions)
```

### API Response Examples

**Event Query Response:**
```json
{
  "total": 5,
  "events": [
    {
      "event_id": "uuid-here",
      "platform": "github",
      "event_type": "code.pushed",
      "timestamp": "2025-12-06T12:00:00Z",
      "source": {
        "platform": "github",
        "repository": "fredporter/uDOS",
        "sender": "fredporter"
      },
      "payload": {
        "title": "Add webhook integration",
        "description": "",
        "url": "https://github.com/...",
        "state": "open",
        "author": "fredporter"
      },
      "routes_matched": 2,
      "routes_succeeded": 2
    }
  ]
}
```

**Route List Response:**
```json
{
  "total": 3,
  "routes": [
    {
      "name": "notify_push",
      "pattern": {
        "event_type": "code.pushed"
      },
      "priority": 50,
      "enabled": true,
      "stats": {
        "matched": 42,
        "executed": 42,
        "errors": 0
      }
    }
  ]
}
```

**Statistics Response:**
```json
{
  "api": {
    "api_requests": 156,
    "webhook_received": 89,
    "api_errors": 2
  },
  "processor": {
    "processed": 89,
    "errors": 0,
    "by_platform": {
      "github": 45,
      "slack": 32,
      "clickup": 12
    }
  },
  "router": {
    "global": {
      "routed": 89,
      "no_match": 3,
      "errors": 1
    },
    "routes": {
      "notify_push": {
        "matched": 45,
        "executed": 45,
        "errors": 0
      }
    },
    "total_routes": 5,
    "enabled_routes": 4
  }
}
```

**Health Check Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-06T14:30:00Z",
  "version": "1.2.10",
  "routes_registered": 5,
  "events_processed": 89
}
```

## Testing & Development

### Event Simulator

Generate realistic webhook payloads for testing without external platforms:

```python
from extensions.core.webhooks.simulator import WebhookSimulator

# Create simulator
simulator = WebhookSimulator()

# Generate GitHub push event
payload = simulator.generate('github', 'push')

# With custom parameters
payload = simulator.generate(
    'github', 'push',
    repo_name='my-repo',
    commit_message='Test commit',
    ref='refs/heads/feature'
)

# Generate with signature
event = simulator.generate_with_signature('github', 'push')
print(f"Payload: {event.payload}")
print(f"Signature: {event.signature}")
print(f"Headers: {event.headers}")

# Send to API
response = requests.post(
    'http://localhost:5090/webhooks/github',
    json=event.payload,
    headers=event.headers
)
```

**Supported Event Types:**

| Platform | Events |
|----------|--------|
| GitHub | `push`, `pull_request`, `issues`, `release` |
| Slack | `message`, `reaction_added`, `app_mention` |
| Notion | `page_created`, `page_updated`, `database_updated` |
| ClickUp | `task_created`, `task_updated`, `task_status_changed` |

**Custom Parameters:**

```python
# GitHub
payload = simulator.generate('github', 'pull_request',
    action='opened',
    pr_number=42,
    pr_title='Amazing Feature',
    user='developer'
)

# Slack
payload = simulator.generate('slack', 'message',
    text='Hello world',
    channel='C12345678',
    user='U87654321'
)

# Notion
payload = simulator.generate('notion', 'page_created',
    title='My Page',
    page_id='custom_id_123'
)

# ClickUp
payload = simulator.generate('clickup', 'task_status_changed',
    old_status='to do',
    new_status='in progress'
)
```

### Interactive Test Panel

Web-based UI for webhook testing (port 5091):

```bash
# Start test panel
python -c "
from extensions.core.webhooks.test_panel import create_test_panel
panel = create_test_panel('http://localhost:5090')
panel.run(port=5091)
"

# Open browser to http://localhost:5091
```

**Test Panel Features:**
- ✅ Generate realistic webhook payloads
- ✅ Send events to API server
- ✅ View event history
- ✅ Inspect active routes
- ✅ Monitor statistics (events, routes, errors)
- ✅ Custom payload parameters
- ✅ Auto-refresh every 5 seconds

**Testing Workflow:**

1. **Start API Server** (port 5090)
   ```bash
   hypercorn extensions.core.webhooks.api_server:app --bind 0.0.0.0:5090
   ```

2. **Start Test Panel** (port 5091)
   ```bash
   python -c "from extensions.core.webhooks.test_panel import create_test_panel; create_test_panel().run()"
   ```

3. **Generate & Send Events**
   - Select platform (GitHub, Slack, Notion, ClickUp)
   - Choose event type
   - Add custom parameters (JSON)
   - Click "Generate Payload"
   - Click "Send to API"

4. **Monitor Results**
   - View event in Recent Events list
   - Check statistics update
   - Inspect route matching
   - Debug any errors

### Unit Tests

Comprehensive test suite (33 tests, 100% passing):

```bash
# Run simulator tests
pytest memory/tests/test_webhook_simulator.py -v

# Run event processing tests
pytest memory/tests/test_event_processing.py -v

# Run all webhook tests
pytest memory/tests/test_webhook*.py -v
```

**Test Coverage:**
- ✅ Payload generation (13 event types)
- ✅ Signature verification (4 platforms)
- ✅ Event normalization
- ✅ Route matching
- ✅ Handler execution
- ✅ Error handling
- ✅ Custom parameters
- ✅ Timestamp validation

### Development Tips

**Debug Mode:**
```python
# Enable Flask debug mode
from extensions.core.webhooks.api_server import create_server
server = create_server()
server.run(debug=True, port=5090)
```

**Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# See detailed event processing
logger = logging.getLogger('extensions.core.webhooks')
logger.setLevel(logging.DEBUG)
```

**Testing Routes:**
```python
# Add test route
from extensions.core.webhooks.client import WebhookClient

client = WebhookClient()
client.add_route(
    route_id='test_route',
    pattern='github.push',
    action='log',
    config={'level': 'debug'}
)

# Simulate event
client.simulate_event('github', 'push', payload={...})

# Check if route matched (view logs)
```

**Performance Testing:**
```bash
# Generate load with simulator
python -c "
from extensions.core.webhooks.simulator import WebhookSimulator
from extensions.core.webhooks.client import WebhookClient
import time

simulator = WebhookSimulator()
client = WebhookClient()

# Send 100 events
for i in range(100):
    event = simulator.generate_with_signature('github', 'push')
    client.simulate_event('github', 'push', payload=event.payload)
    time.sleep(0.1)

# Check stats
stats = client.get_stats()
print(f'Processed: {stats.total_events}')
"
```

## Support

- **Documentation:** This file
- **API Reference:** `extensions/core/webhooks/README.md`
- **Examples:** `memory/workflows/missions/webhook_examples/`
- **Tests:** `memory/tests/test_event_processing.py`, `test_webhook_simulator.py`
- **Issues:** GitHub Issues (fredporter/uDOS)

---

**Last Updated:** December 6, 2025
**Extension Version:** 1.2.10 (Parts 1-3 complete)
**API Server:** ✅ Active (14 endpoints)
**Client Library:** ✅ Available (sync + async)
**Integrations:** ✅ GitHub, Slack, Notion, ClickUp
**Testing:** ✅ Simulator + Test Panel (33 tests passing)
