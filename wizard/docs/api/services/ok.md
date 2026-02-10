# OK Service

Wizard OK Gateway (local Vibe).

## UI Contract

See `ok-ui.md` for the OK (local Vibe) UI data model.

## Defaults

OK model defaults live in `core/config/ok_modes.json` under `modes.ofvibe.default_models` with `core` and `dev` profiles. The UI reads these via `GET /api/ucode/ok/status` (returned as `ok.default_models`).

## Routes

- `GET /api/ai/health`
- `GET /api/ai/config`
- `GET /api/ai/context`
- `GET /api/ai/suggest-next`
- `POST /api/ai/analyze-logs?log_type=error`
- `POST /api/ai/explain-code`
