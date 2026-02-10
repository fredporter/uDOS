# Service: wizard.dev

## Purpose
Toggle developer mode (Goblin dev services) and expose status/logs.

## Endpoints (current)

- `GET /api/dev/health`
- `GET /api/dev/status`
- `POST /api/dev/activate`
- `POST /api/dev/deactivate`
- `POST /api/dev/restart`
- `POST /api/dev/clear`
- `GET /api/dev/logs?lines=50`

## Response (example)

```json
{
  "status": "success",
  "active": true,
  "goblin_endpoint": "http://127.0.0.1:8767",
  "goblin_pid": 12345,
  "services": {
    "goblin": true
  }
}
```

## MCP Tool Mapping

- `wizard.dev.health`
- `wizard.dev.status`
- `wizard.dev.activate`
- `wizard.dev.deactivate`
- `wizard.dev.restart`
- `wizard.dev.clear`
- `wizard.dev.logs`

