# Mission / Job Schema

Expands on the Milestones and runtime split from `docs/uDOS-v1-3.md` sections 7, 9, and 10. Missions define long-running programmes; jobs are their runnable units.

## Mission definition
- `id`: UUID
- `name`: human-readable goal
- `description`: mission intent and constraints
- `cadence`: daily/weekly/nightly/scheduled
- `targets`: list of folders, notes, feeds
- `capabilities`: `offline-only`, `online-allowed`, `ai-router` etc.
- `outputs`: report directories (`vault/06_RUNS/`), log targets (`vault/07_LOGS/`), patch bundles

## Job schema
- `job_id`, `mission_id`
- `runner`: e.g., `Vibe CLI`, `wizard-core`, `renderer`
- `status`: `pending`, `running`, `completed`, `failed`
- `tasks`: sequence of deterministic actions (parse → render → diff → export)
- `ai_model`: optional pointer to local or online model, with policy justification
- `artifacts`: references to `_site/`, patch bundles, logs, sqlite snapshots

## Storage
- Jobs, runs, and provenance live in the vault SQLite (`.udos/state.db` or `05_DATA/sqlite/udos.db`).
- Run reports should be emitted into `vault/06_RUNS/<mission-id>/`.
- Logs go to `vault/07_LOGS/<mission-id>/` with traceable timestamps.
