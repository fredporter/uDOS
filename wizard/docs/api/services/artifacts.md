# Artifacts Service

Wizard-local artifact storage (installers, builds, backups).

## Routes

- `GET /api/artifacts`
  - List artifacts (optional `kind`).

- `GET /api/artifacts/summary`
  - Summary counts and sizes for artifacts UI.

- `POST /api/artifacts/add`
  - Add an artifact from a repo-local file path.

- `DELETE /api/artifacts/{artifact_id}`
  - Delete an artifact by id.
