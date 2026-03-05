# Service: wizard.dev

## Purpose
Manage the installed Dev Mode extension lane for the `@dev` workspace and expose contributor status, health, lifecycle, script/test, and GitHub surfaces.

## Endpoints (current)

- `GET /api/dev/health`
- `GET /api/dev/status`
- `GET /api/dev/ops`
- `GET /api/dev/ops/files?area=ops|docs|goblin&path=<relative>`
- `GET /api/dev/ops/read?area=ops|docs|goblin&path=<relative-file>`
- `POST /api/dev/ops/write`
- `POST /api/dev/ops/normalize`
- `POST /api/dev/activate`
- `POST /api/dev/deactivate`
- `POST /api/dev/restart`
- `POST /api/dev/clear`
- `GET /api/dev/logs?lines=50`
- `GET /api/dev/scripts`
- `POST /api/dev/scripts/run`
- `GET /api/dev/tests`
- `POST /api/dev/tests/run`
- `GET /api/dev/github/status`
- `GET /api/dev/github/pat-status`
- `POST /api/dev/github/pat`
- `DELETE /api/dev/github/pat`
- `GET /api/dev/webhook/github-secret-status`
- `POST /api/dev/webhook/github-secret`

## Response (example)

```json
{
  "status": "success",
  "active": true,
  "workspace_alias": "@dev",
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
- `/dev/` must exist and contain the required tracked framework payload.
- `@dev` is the contributor workspace alias for `/dev`.
- Tracked sync content is limited to `/dev` governance files, `dev/docs/`, and `dev/goblin/`.
- Local contributor work areas under `/dev/files`, `/dev/relecs`, `/dev/dev-work`, and `/dev/testing` are valid, but they are not the canonical framework payload.
- Tracked editor reads expose backend-owned helper metadata so file types can advertise format, normalize, or cleanup actions without moving parser logic into the GUI.
- Task ledgers, completed ledgers, and workflow JSON plans/specs now advertise dedicated helper profiles instead of generic JSON-only labels.
- `/api/dev/ops/write` is the canonical tracked save surface and may persist normalized content when `normalize=true` is requested.
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
