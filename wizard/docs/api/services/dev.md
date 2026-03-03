# Service: wizard.dev

## Purpose
Manage the installed Dev Mode extension lane and expose contributor status, health, restart, clear, and log surfaces.

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
  "dev_root": "/repo/dev",
  "framework_ready": true,
  "services": {
    "dev_extension_framework": true,
    "github_service": true
  }
}
```

## Contract Notes

- Dev Mode is a Wizard-gated contributor extension lane.
- `/dev/` must exist and contain the required extension framework files.
- The standard runtime remains `ucode`.
- `vibe` is Dev Mode contributor tooling only and is not a peer default runtime.

## MCP Tool Mapping

- `wizard.dev.health`
- `wizard.dev.status`
- `wizard.dev.activate`
- `wizard.dev.deactivate`
- `wizard.dev.restart`
- `wizard.dev.clear`
- `wizard.dev.logs`
