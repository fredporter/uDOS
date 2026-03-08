# Empire Architecture

Empire is an internal business extension for uDOS. It depends on Core + Wizard and is activated explicitly through Wizard Extensions.

High-level spine:
- `src/` package root
- `services/` business domain services
- `integrations/` external systems + connectors
- `scripts/` ingest/process/export utilities
- `config/` templates and defaults
- `tests/` validation and regression suites

Runtime expectations:
- Ships inside the uDOS repo under `extensions/empire`.
- Defaults to disabled until explicitly enabled from Wizard Extensions.
- Missing or disabled state should soft-fail with a friendly message.

Initial functional spine:
- Ingestion: raw CSV/JSON/JSONL intake → JSONL staging.
- Normalization: shape raw records to a canonical schema for business workflows.
- Storage: SQLite schema for records, sources, and events (HubSpot-aligned fields).
- API: FastAPI surface for health, records, and events.
- API auth: `EMPIRE_API_TOKEN` bearer auth (private-only).
- Integrations: Gmail API + Google Places (scaffolded).
- CRM sync: HubSpot connector wired through Wizard-owned sync services.
- Email pipeline: receive → categorize → tasks + record updates.
- API ops: `EMPIRE API START|STOP` runs FastAPI on `127.0.0.1:8991`.
- Email validation: rejects malformed/bot addresses, keeps role-based inboxes.
