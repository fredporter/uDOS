# OK UI Data Model

Contract for the OK (local Vibe) UI surface.

## Data Sources

- `GET /api/ai/health`
- `GET /api/ai/config`
- `GET /api/ai/context`
- `POST /api/ai/analyze-logs`
- `GET /api/ai/suggest-next`

## UI Model

```json
{
  "status": "ok|error",
  "vibe_cli_installed": true,
  "default_model": "devstral-small",
  "context": {
    "files": 0,
    "total_chars": 0
  },
  "last_analysis": {
    "log_type": "error",
    "summary": "string"
  }
}
```

## UI Notes

- The UI should label this as **OK (Local Vibe)**.
- Use `include_context=true` for OK queries by default.
