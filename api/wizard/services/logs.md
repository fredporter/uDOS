# Logs Service

Endpoints for log collection and retrieval.

## Routes

- `POST /api/logs/toast`
  - Record a toast notification log entry.
  - Payload: `{ "severity": "info|success|warning|error", "title": "string", "message": "string", "meta": { ... } }`

- `GET /api/monitoring/logs`
  - List log files in `memory/logs`.

- `GET /api/monitoring/logs/{log_name}?lines=200`
  - Tail a log file (last `lines`).

- `GET /api/monitoring/logs/stats`
  - Log file counts and sizes by category.
