# Service: wizard.providers

## Purpose
List configured AI providers and basic capabilities.

## UI Contract

See `providers-ui.md` for the dashboard/UI data model.

## Endpoints

- `GET /api/providers`
- `GET /api/providers/list`
- `GET /api/providers/{provider_id}/status`
- `GET /api/providers/{provider_id}/config`
- `POST /api/providers/{provider_id}/enable`
- `POST /api/providers/{provider_id}/disable`
- `GET /api/providers/dashboard`

## Response (example)

```json
{
  "status": "ok",
  "providers": [
    {
      "name": "mistral",
      "enabled": true,
      "capabilities": ["chat", "embeddings"]
    },
    {
      "name": "anthropic",
      "enabled": false,
      "capabilities": ["chat"]
    }
  ]
}
```

## MCP Tool Mapping

- `wizard.providers.list`
- `wizard.providers.status`
- `wizard.providers.config`
- `wizard.providers.enable`
- `wizard.providers.disable`
- `wizard.providers.dashboard`
