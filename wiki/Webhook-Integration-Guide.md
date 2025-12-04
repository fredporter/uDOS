# Webhook Integration Guide

## Overview

uDOS v1.2.5 introduces webhook integration for event-driven automation. Connect GitHub, Slack, Notion, and ClickUp to trigger knowledge updates, workflow automation, and real-time notifications.

## Architecture

```
External Platform → Webhook Endpoint → Signature Validation → Event Handler → Workflow Trigger
     (GitHub)         /api/webhooks/      (HMAC-SHA256)      (Platform)      (uDOS Commands)
```

### Components

1. **Webhook Manager** (`core/services/webhook_manager.py`)
   - Registration and storage
   - Signature validation (platform-specific)
   - Event routing
   - Trigger tracking

2. **Platform Handlers**
   - `github_webhook_handler.py` - Push/PR/Release events
   - `platform_webhook_handlers.py` - Slack/Notion/ClickUp

3. **API Endpoints** (`extensions/api/server.py`)
   - `POST /api/webhooks/register` - Register new webhook
   - `GET /api/webhooks/list` - List webhooks
   - `DELETE /api/webhooks/delete/<id>` - Remove webhook
   - `POST /api/webhooks/receive/<platform>` - Receive events
   - `POST /api/webhooks/test/<id>` - Test webhook

4. **Dashboard Widget** (`extensions/core/dashboard/widgets/webhook-widget.js`)
   - Visual webhook management
   - Test interface
   - Event logs

## Platform Setup

### GitHub

**1. Register Webhook**

```bash
curl -X POST http://localhost:5000/api/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "github",
    "events": ["push", "pull_request", "release"],
    "actions": [
      {
        "event": "push",
        "workflow": "knowledge-quality-scan",
        "args": {}
      }
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "webhook": {
    "id": "wh_a1b2c3d4e5f6g7h8",
    "platform": "github",
    "url": "http://localhost:5000/api/webhooks/receive/github",
    "secret": "your-webhook-secret-here",
    "events": ["push", "pull_request", "release"],
    "created": "2025-12-03T12:00:00"
  }
}
```

**2. Configure GitHub Repository**

Go to: `Settings` → `Webhooks` → `Add webhook`

- **Payload URL**: `http://your-server:5000/api/webhooks/receive/github`
- **Content type**: `application/json`
- **Secret**: (use secret from response)
- **Events**: Select individual events
  - ☑ Pushes
  - ☑ Pull requests
  - ☑ Releases

**3. Supported Events**

| Event | Trigger | Workflow |
|-------|---------|----------|
| `push` | Main branch push with knowledge/ changes | `knowledge-quality-scan` |
| `pull_request` | PR opened with knowledge mention | `knowledge-gap-analysis` |
| `release` | Release published | `CHANGELOG UPDATE` |
| `issues` | Issue with `knowledge-gap` label | Notification |

---

### Slack

**1. Register Webhook**

```bash
curl -X POST http://localhost:5000/api/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "slack",
    "events": ["message", "slash_command"],
    "actions": []
  }'
```

**2. Configure Slack App**

Create Slack App at https://api.slack.com/apps

**Slash Commands:**
- `/udos <command>` - Execute any uDOS command
- `/knowledge <query>` - Search knowledge bank
- `/map <action>` - Map commands

**Event Subscriptions:**
- Request URL: `http://your-server:5000/api/webhooks/receive/slack`
- Subscribe to bot events:
  - `message.channels`
  - `app_mention`

**3. Signing Secret**

- Copy signing secret from Slack app settings
- Use when registering webhook (not shown in example)

---

### Notion

**1. Register Webhook**

```bash
curl -X POST http://localhost:5000/api/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "notion",
    "events": ["page", "database"],
    "actions": [
      {
        "event": "page",
        "workflow": "notion-sync",
        "args": {}
      }
    ]
  }'
```

**2. Configure Notion Integration**

- Create internal integration at https://www.notion.so/my-integrations
- Add integration to your workspace
- Share specific pages/databases with integration

**3. Webhook Setup**

Notion doesn't have built-in webhooks. Use:
- **Zapier/Make** to trigger webhook URL
- **Notion API polling** (custom script)
- **Database automation** (future Notion feature)

---

### ClickUp

**1. Register Webhook**

```bash
curl -X POST http://localhost:5000/api/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "clickup",
    "events": ["taskCreated", "taskUpdated", "taskCommentPosted"],
    "actions": []
  }'
```

**2. Configure ClickUp Workspace**

Go to: `Workspace Settings` → `Integrations` → `Webhooks`

- **Endpoint**: `http://your-server:5000/api/webhooks/receive/clickup`
- **Events**:
  - ☑ Task Created
  - ☑ Task Updated
  - ☑ Task Comment Posted
- **Filters**: Add tag filter for "knowledge" tasks

**3. Special Features**

- **@udos mentions** in comments trigger ASSIST command
- Tasks with "knowledge" in name sync to uDOS

---

## Dashboard Usage

### Access Dashboard

1. Start API server:
   ```bash
   python extensions/api/server.py
   ```

2. Open dashboard:
   ```
   http://localhost:5000
   ```

3. Add webhook widget:
   - Click **➕ Add Widget**
   - Select **🪝 Webhook Manager**
   - Widget shows live webhook status

### Webhook Widget Features

- **📊 Stats**: Total webhooks, active count, trigger count
- **➕ Register**: Quick webhook registration form
- **🧪 Test**: Send test events to webhooks
- **🗑️ Delete**: Remove webhooks
- **🔄 Refresh**: Update webhook list

---

## Testing Webhooks

### Manual Test via API

```bash
# Test specific webhook
curl -X POST http://localhost:5000/api/webhooks/test/wh_abc123 \
  -H "Content-Type: application/json" \
  -d '{
    "event": "push",
    "test_data": {
      "ref": "refs/heads/main",
      "commits": [{
        "modified": ["knowledge/water/boiling.md"]
      }]
    }
  }'
```

### GitHub Test Event

In GitHub repo settings → Webhooks → Recent Deliveries:
- Click **Redeliver** to resend event

### Webhook Logs

View logs in:
- **Dashboard**: Webhook widget shows event history
- **API Logs**: `sandbox/logs/api_server.log`
- **System Logs**: `memory/logs/system.log`

---

## Security

### Signature Validation

All webhooks use HMAC-SHA256 signature validation:

**GitHub**: `X-Hub-Signature-256: sha256=<hash>`
**Slack**: `X-Slack-Signature: v0=<hash>` (with timestamp)
**Notion**: `X-Notion-Signature: <hash>`
**ClickUp**: `X-ClickUp-Signature: <hash>`

### Secret Management

**⚠️ Never commit webhook secrets to git!**

Store secrets in:
- **Environment variables**: `WEBHOOK_SECRET_GITHUB=...`
- **Config file**: `memory/system/webhooks.json` (gitignored)
- **Vault service**: HashiCorp Vault, AWS Secrets Manager

### IP Allowlisting

For production deployments:

```python
# Add to server.py before webhook endpoint
ALLOWED_IPS = {
    'github': ['192.30.252.0/22', '185.199.108.0/22'],
    'slack': ['54.224.0.0/12', '54.144.0.0/14'],
}

@app.before_request
def check_webhook_ip():
    if request.path.startswith('/api/webhooks/receive/'):
        platform = request.path.split('/')[-1]
        if request.remote_addr not in ALLOWED_IPS.get(platform, []):
            abort(403)
```

---

## Workflow Integration

### Auto-Trigger Workflows

**GitHub push to knowledge/**:
```yaml
Event: push
Condition: knowledge/ files modified
Workflow: knowledge-quality-scan
```

**PR with knowledge changes**:
```yaml
Event: pull_request
Condition: "knowledge" in PR title
Workflow: knowledge-gap-analysis
```

**Slack /knowledge command**:
```yaml
Event: slash_command
Command: /knowledge water purification
Workflow: knowledge-search
```

### Custom Actions

Create custom event → workflow mappings:

```bash
curl -X POST http://localhost:5000/api/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "github",
    "events": ["push"],
    "actions": [
      {
        "event": "push",
        "workflow": "batch-regen",
        "args": {"category": "water"}
      },
      {
        "event": "push",
        "workflow": "xref-validation",
        "args": {}
      }
    ]
  }'
```

---

## Troubleshooting

### Webhook Not Receiving Events

**Check API server is running:**
```bash
curl http://localhost:5000/api/health
```

**Verify webhook registered:**
```bash
curl http://localhost:5000/api/webhooks/list
```

**Check platform webhook settings:**
- GitHub: Settings → Webhooks → Recent Deliveries
- Slack: App settings → Event Subscriptions → Request Log

### Signature Validation Failures

**Common causes:**
- Wrong secret (check `webhooks.json`)
- Clock skew (Slack requires ±5 min)
- Payload encoding (use raw bytes, not JSON string)

**Debug mode:**
```python
# Add to webhook_receive() endpoint
api_logger.debug(f'Signature header: {signature}')
api_logger.debug(f'Computed signature: {computed_sig}')
api_logger.debug(f'Payload: {payload}')
```

### Workflow Not Triggering

**Check workflow exists:**
```bash
ls memory/workflows/*.upy
```

**Test workflow manually:**
```bash
./start_udos.sh
> WORKFLOW RUN knowledge-quality-scan
```

**Check event → action mapping:**
```bash
curl http://localhost:5000/api/webhooks/test/wh_abc123 \
  -H "Content-Type: application/json" \
  -d '{"event": "push"}'
```

---

## API Reference

### Register Webhook

```
POST /api/webhooks/register
Content-Type: application/json

{
  "platform": "github|slack|notion|clickup",
  "events": ["event1", "event2"],
  "actions": [
    {"event": "event1", "workflow": "workflow-name", "args": {}}
  ]
}

Response:
{
  "status": "success",
  "webhook": {
    "id": "wh_...",
    "platform": "...",
    "url": "...",
    "secret": "...",
    "created": "..."
  }
}
```

### List Webhooks

```
GET /api/webhooks/list?platform=github

Response:
{
  "status": "success",
  "count": 3,
  "webhooks": [...]
}
```

### Delete Webhook

```
DELETE /api/webhooks/delete/<webhook_id>

Response:
{
  "status": "success",
  "message": "Webhook deleted"
}
```

### Receive Webhook Event

```
POST /api/webhooks/receive/<platform>
Headers:
  X-Hub-Signature-256: sha256=... (GitHub)
  X-Slack-Signature: v0=...       (Slack)

Body: Platform-specific JSON

Response:
{
  "status": "success",
  "platform": "...",
  "event": "...",
  "actions_triggered": 2,
  "results": [...]
}
```

### Test Webhook

```
POST /api/webhooks/test/<webhook_id>
{
  "event": "push",
  "test_data": {...}
}

Response:
{
  "status": "success",
  "webhook_id": "...",
  "event": "...",
  "actions_found": 1,
  "actions": [...]
}
```

---

## Next Steps

1. **Set up GitHub webhook** for knowledge repo
2. **Create Slack app** for team integration
3. **Configure dashboard widget** for monitoring
4. **Test webhook flows** end-to-end
5. **Document custom workflows** specific to your use case

For more information:
- API Documentation: `wiki/Developers-Guide.md`
- Workflow System: `memory/workflows/README.md`
- Knowledge Quality: `dev/sessions/v1.2.11-complete.md`
