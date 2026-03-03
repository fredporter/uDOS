# Datasets Service

Read-only dataset inspection plus bounded export and parse surfaces.

## Routes

- `GET /api/data/tables`
  - List tables and metadata.

- `GET /api/data/summary`
  - Summary counts for datasets UI.

- `GET /api/data/schema`
  - Full dataset schema.

- `GET /api/data/tables/{table_name}`
  - Fetch rows with pagination/filtering.

- `GET /api/data/query`
  - Query table with filters, selected columns.

- `POST /api/data/export/{table}`
  - Export table data (server-side).

- `POST /api/data/parse/{table}`
  - Import/parse handoff for dataset-specific processing lanes.
