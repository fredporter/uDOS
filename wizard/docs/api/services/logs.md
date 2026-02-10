# Logs Service

Endpoints for log collection and retrieval.

## Routes

- `POST /api/logs/toast`
  - Record a toast notification log entry.
  - Payload: `{ "severity": "info|success|warning|error", "title": "string", "message": "string", "meta": { ... } }`

- `GET /api/logs/stream?component=wizard&name=wizard-server&limit=200`
  - SSE tail of v1.3 JSONL logs under `memory/logs/udos/<component>/`.
  - Emits `event: log` with JSONL entries and periodic `event: ping`.

- `GET /api/monitoring/logs`
  - List log files in `memory/logs`.

- `GET /api/monitoring/logs/{log_name}?lines=200`
  - Tail a log file (last `lines`).

- `GET /api/monitoring/logs/stats`
  - Log file counts and sizes by category.
