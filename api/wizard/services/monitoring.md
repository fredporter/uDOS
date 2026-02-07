# Monitoring Service

Lightweight monitoring + diagnostics for Wizard.

## Routes

- `GET /api/monitoring/summary`
  - Health summary from MonitoringManager.

- `GET /api/monitoring/diagnostics`
  - Bundled diagnostics (health summary + system info + log stats).

- `GET /api/monitoring/alerts`
  - List alerts (filters: `severity`, `type`, `service`, `unacknowledged_only`, `limit`).

- `POST /api/monitoring/alerts/{alert_id}/ack`
- `POST /api/monitoring/alerts/{alert_id}/resolve`
