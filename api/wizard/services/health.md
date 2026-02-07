# Service: wizard.health

## Purpose
Return Wizard server health and basic service status for display in Vibe and companion UI.

## Request

- Method: `GET`
- Path: `/health`

## Response (example)

```json
{
  "status": "ok",
  "timestamp": "2026-02-06T12:34:56Z",
  "services": {
    "wizard": "running",
    "ok_gateway": "enabled",
    "plugins": "enabled"
  },
  "version": "1.3.8"
}
```

## MCP Tool Mapping

- Tool: `wizard.health`
- Input: none
- Output: response JSON

