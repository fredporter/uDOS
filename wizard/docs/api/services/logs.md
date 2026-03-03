# Logs Service

Endpoints for log collection and retrieval.

## Routes

- `GET /api/logs/status`
  - Return central log contract health and tree stats.
  - Response includes:
    - `health.schema`, `health.runtime_version`, `health.level`, `health.dest`, `health.format`
    - `health.redact`, `health.payloads`, `health.ring_entries`, `health.ring_size`
    - `stats.total_files`, `stats.total_size_mb`, `stats.latest_file`, `stats.by_component`

- `POST /api/logs/toast`
  - Record a toast notification log entry.
  - Payload: `{ "severity": "info|success|warning|error", "title": "string", "message": "string", "meta": { ... } }`

- `GET /api/logs/stream?component=wizard&name=wizard-server&limit=200`
  - SSE tail of v1.5 JSONL logs under `memory/logs/udos/<component>/`.
  - Emits `event: log` with JSONL entries and periodic `event: ping`.

- `GET /api/monitoring/logs`
  - List log files in `memory/logs`.

- `GET /api/monitoring/logs/{log_name}?lines=200`
  - Tail a log file (last `lines`).

- `GET /api/monitoring/logs/stats`
  - Log file counts and sizes by category.
