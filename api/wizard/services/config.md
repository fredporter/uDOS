# Service: wizard.config

## Purpose
Read or update Wizard server configuration.

## Requests

- Method: `GET`
- Path: `/api/config`

- Method: `PATCH`
- Path: `/api/config`
- Body:

```json
{
  "updates": {
    "ai_gateway_enabled": true,
    "plugin_auto_update": false
  }
}
```

## Response (example)

```json
{
  "status": "ok",
  "config": {
    "ai_gateway_enabled": true,
    "plugin_auto_update": false
  }
}
```

## MCP Tool Mapping

- Tool: `wizard.config.get`
- Tool: `wizard.config.set`

