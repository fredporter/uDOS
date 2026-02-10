# Providers UI Data Model

Contract for the Providers dashboard (AI + local).

## Data Sources

- `GET /api/providers/list`
- `GET /api/providers/{provider_id}/status`
- `GET /api/providers/{provider_id}/config`
- `GET /api/providers/models/available`
- `GET /api/providers/models/installed`
- `GET /api/providers/models/pull/status`
- `GET /api/providers/dashboard`

## UI Model

```json
{
  "providers": [
    {
      "id": "mistral",
      "name": "Mistral AI",
      "type": "api_key",
      "enabled": true,
      "status": {
        "configured": true,
        "available": true
      },
      "config": {
        "config_file": "path",
        "config_key": "MISTRAL_API_KEY",
        "exists": true,
        "keys": []
      }
    }
  ],
  "models": {
    "available": [],
    "installed": [],
    "pull_status": {}
  },
  "quotas": {
    "updated_at": "timestamp",
    "providers": {},
    "totals": {}
  }
}
```

## UI Notes

- Use `providers/dashboard` as the primary load for the Providers screen.
- Merge model lists with provider status for UI badges.
