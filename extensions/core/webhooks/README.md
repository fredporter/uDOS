# uDOS Webhook Integration System

**Version:** 1.2.10
**Status:** Active
**Category:** Core Extension

## Overview

Unified webhook processing system for external platform events with REST API, client library, and platform integration helpers.

### Supported Platforms

- **GitHub** - Push, pull requests, issues, releases
- **Slack** - Messages, reactions, mentions, commands
- **Notion** - Page updates, database changes
- **ClickUp** - Tasks, comments, status updates

## Components

### Event Processor (`event_processor.py`)
Normalizes platform-specific webhook payloads into unified format.

- 19 event type mappings across 4 platforms
- Automatic field extraction
- Statistics tracking
- Error handling

### Event Router (`event_router.py`)
Routes events to handlers based on patterns with priority ordering.

- Regex pattern matching
- Priority-based execution (0-100)
- Async handler support
- uCODE script integration
- Event history (1,000 events default)

### API Server (`api_server.py`)
REST API for webhook management and event querying.

- **14 endpoints** (4 webhook receivers + 10 management)
- Platform-specific signature verification
- CORS support
- Rate limiting
- Health checks

### Client Library (`client.py`)
Python client for webhook API with sync/async support.

- Typed dataclasses (Event, Route, Stats)
- 10 sync methods (requests)
- 10 async methods (aiohttp)
- Context manager support

### Platform Integrations (`integrations/`)
Setup helpers for configuring webhooks on external platforms.

- **GitHub:** API webhook creation, setup guides
- **Slack:** App manifest generation, event subscriptions
- **Notion:** Integration setup, beta API support
- **ClickUp:** Webhook management, event filtering

## Installation

### Dependencies

```bash
pip install flask flask-cors aiohttp hypercorn requests pytest-asyncio
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Environment Variables

```bash
# Webhook secrets for signature verification
GITHUB_WEBHOOK_SECRET=your_github_secret
SLACK_SIGNING_SECRET=your_slack_secret
NOTION_WEBHOOK_SECRET=your_notion_secret
CLICKUP_WEBHOOK_SECRET=your_clickup_secret

# API tokens for platform integration
GITHUB_TOKEN=your_github_pat
CLICKUP_API_TOKEN=your_clickup_token
NOTION_INTEGRATION_TOKEN=your_notion_token
```

## Quick Start

### 1. Start API Server

```python
from extensions.core.webhooks.api_server import create_server

server = create_server(host='0.0.0.0', port=5050)
server.run()
```

### 2. Register Event Handler

```python
from extensions.core.webhooks import EventRouter

router = EventRouter()

async def handle_push(event):
    print(f"📦 {event['source']['sender']} pushed to {event['source']['repository']}")
    return {'success': True}

router.register_route(
    name='github_push_handler',
    pattern={'event_type': 'code.pushed'},
    handler=handle_push,
    priority=50
)
```

### 3. Setup Platform Webhook

```python
from extensions.core.webhooks.integrations import GitHubIntegration
import os

integration = GitHubIntegration('https://your-server.com')

webhook = integration.create_webhook(
    owner='fredporter',
    repo='uDOS',
    token=os.getenv('GITHUB_TOKEN'),
    events=['push', 'pull_request']
)
```

### 4. Query Events

```python
from extensions.core.webhooks.client import WebhookClient

client = WebhookClient('http://localhost:5050')
events = client.get_events(platform='github', limit=10)

for event in events:
    print(f"{event['event_type']}: {event['payload']['title']}")
```

## API Reference

### Webhook Receivers

- `POST /webhooks/github` - GitHub events
- `POST /webhooks/slack` - Slack events
- `POST /webhooks/notion` - Notion events
- `POST /webhooks/clickup` - ClickUp events

### Event Management

- `GET /api/events?limit={n}&platform={platform}` - Query history
- `GET /api/events/{event_id}` - Get specific event

### Route Management

- `GET /api/routes` - List routes
- `GET /api/routes/{name}` - Get route
- `POST /api/routes/{name}/enable` - Enable route
- `POST /api/routes/{name}/disable` - Disable route
- `DELETE /api/routes/{name}` - Remove route

### System

- `GET /api/stats` - Statistics
- `POST /api/stats/reset` - Reset stats
- `GET /api/health` - Health check

## Event Format

All events normalized to:

```json
{
  "event_id": "uuid",
  "platform": "github|slack|notion|clickup",
  "event_type": "normalized.type",
  "timestamp": "ISO-8601",
  "source": {
    "platform": "github",
    "repository": "owner/repo",
    "sender": "username"
  },
  "payload": {
    "title": "Event title",
    "description": "Details",
    "url": "https://...",
    "state": "open|closed",
    "author": "username"
  },
  "raw": {}
}
```

## Event Types

### GitHub
- `code.pushed` - Code pushed
- `code.pull_request.opened` - PR opened
- `code.pull_request.closed` - PR closed
- `issue.created` - Issue created
- `issue.closed` - Issue closed
- `release.published` - Release published

### Slack
- `message.posted` - Message sent
- `message.reacted` - Reaction added
- `message.mentioned` - Bot mentioned
- `command.invoked` - Slash command

### Notion
- `page.updated` - Page modified
- `page.created` - Page created
- `database.item.created` - DB row added
- `database.item.updated` - DB row updated

### ClickUp
- `task.created` - Task created
- `task.updated` - Task modified
- `task.status.changed` - Status changed
- `task.comment.posted` - Comment added

## Configuration

Edit `config.json`:

```json
{
  "webhook_system": {
    "platforms": {
      "github": {
        "enabled": true,
        "events": ["push", "pull_request"],
        "filters": {
          "repositories": ["owner/repo"],
          "exclude_bots": true
        }
      }
    },
    "routing": {
      "max_history": 1000,
      "retry_failed": true,
      "max_retries": 3,
      "script_timeout": 30
    },
    "security": {
      "verify_signatures": true,
      "rate_limit": {
        "enabled": true,
        "max_requests": 100,
        "window_seconds": 60
      }
    }
  }
}
```

## Testing

```bash
# Run all webhook tests
pytest memory/tests/test_event_processing.py -v

# Test specific platform
pytest memory/tests/test_event_processing.py::TestEventProcessor::test_github_push_event -v
```

## Security

- **Signature Verification:** HMAC SHA-256 for all platforms
- **API Authentication:** Bearer token support
- **Rate Limiting:** Configurable requests/minute
- **CORS:** Configurable origins
- **IP Filtering:** Allowlist support

## Performance

- Event processing: ~0.1ms
- Route matching: ~0.05ms
- Max history: 1,000 events (configurable)
- Rate limit: 100 req/min (configurable)

## Production Deployment

### Using Hypercorn (ASGI)

```bash
# Production server with 4 workers
hypercorn extensions.core.webhooks.api_server:app \
    --bind 0.0.0.0:5090 \
    --workers 4 \
    --access-logfile - \
    --error-logfile -
```

### Using Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY extensions/core/webhooks/ extensions/core/webhooks/
COPY core/ core/

EXPOSE 5090

CMD ["hypercorn", "extensions.core.webhooks.api_server:app", \
     "--bind", "0.0.0.0:5090", \
     "--workers", "4"]
```

```bash
# Build and run
docker build -t udos-webhooks .
docker run -p 5090:5090 --env-file .env udos-webhooks
```

### Using systemd

```ini
# /etc/systemd/system/udos-webhooks.service
[Unit]
Description=uDOS Webhook API Server
After=network.target

[Service]
Type=simple
User=udos
WorkingDirectory=/opt/udos
Environment="PATH=/opt/udos/.venv/bin"
EnvironmentFile=/opt/udos/.env
ExecStart=/opt/udos/.venv/bin/hypercorn \
    extensions.core.webhooks.api_server:app \
    --bind 0.0.0.0:5090 \
    --workers 4

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl enable udos-webhooks
sudo systemctl start udos-webhooks
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/udos-webhooks
server {
    listen 443 ssl http2;
    server_name webhooks.your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    location / {
        proxy_pass http://127.0.0.1:5090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### Health Checks

```bash
# Check API health
curl http://localhost:5090/api/health

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2025-12-06T12:00:00Z",
#   "version": "1.2.10",
#   "routes_registered": 5,
#   "events_processed": 1234
# }
```

### Statistics

```python
from extensions.core.webhooks.client import WebhookClient

client = WebhookClient()
stats = client.get_stats()

print(f"Total events: {stats.total_events}")
print(f"Active routes: {stats.active_routes}")
print(f"Errors: {stats.processing_errors}")
```

### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('extensions.core.webhooks')
logger.setLevel(logging.DEBUG)
```

## Documentation

- **Full Guide:** `wiki/Webhook-Integration.md`
- **API Tests:** `memory/tests/test_webhook_api.py`
- **Simulator Tests:** `memory/tests/test_webhook_simulator.py`
- **Examples:** `memory/ucode/examples/webhooks/`
- **Integration Helpers:** `extensions/core/webhooks/integrations/`

## License

MIT License - See LICENSE.txt

## Credits

uDOS Development Team

---

**Last Updated:** December 6, 2025
**Version:** 1.2.10 (Complete)
**Components:** 8 (Processor, Router, API, Client, Integrations, Simulator, Test Panel, Config)
**Tests:** 49/49 passing
**Endpoints:** 14 (4 webhook + 10 management)
**Platforms:** 4 (GitHub, Slack, Notion, ClickUp)
