# Mission Scheduler & Vibe CLI Integration

This document explains how the new `mission-scheduler` container in `node/docker-compose.yml` collaborates with the Vibe CLI, contributions, and renderer API so the static exports and Svelte UI modules stay in sync.

1. **Vibe CLI** (see `node/vibe-cli/README.md`)
   - Runs Mistral's `vibe` binary and shares the Vault (`/workspace/vault`) so it can read/write the same `.env`, mission reports, and story outputs that Core/Wizard already uses.
   - Contributions proposed by Vibe land as JSON patch bundles under `vault/contributions/pending`, matching the format from `docs/Contributions-Contract.md`.
   - When Vibe needs a mission update, it calls `wizard/extensions/assistant/vibe_cli_service.py`, which is aware of the `/api/renderer/*` renderer endpoints and can signal the scheduler.

2. **Mission Scheduler** (`node/mission-scheduler/runner.py`)
   - Watches `vault/contributions/pending`, posts render jobs to `/api/renderer/render`, and records mission/job metadata under `vault/06_RUNS` plus `vault/07_LOGS`.
   - After each render it re-indexes tasks from the vault Markdown via `state.db` (matching `node/mission-scheduler/task_indexer.py`) so `/api/renderer/missions` can report task counts and the UI can feed calendars/agenda layouts.
   - Processed contributions are moved to `vault/contributions/processed`, keeping live queues clean.

3. **Renderer API**
   - `/api/renderer/themes` and `/api/renderer/missions` publish metadata about available themes, missions, and `_site/<theme>` outputs so the SvelteKit control plane can render the same lists seen by the static portal.
   - When `mission-scheduler` posts to `/api/renderer/render`, Wizard logs the job ID and mission so mission history surfaces in the UI.

4. **Positioning in the new architecture**
   - `node/docker-compose.yml` now wires `vibe-cli`, `mission-scheduler`, `renderer`, `portal-static`, and `web-admin` together, ensuring contributions + AI routing drive the static export lane without manual intervention.
   - The rendered `_site/<theme>` data is served by `portal-static` and is described by the contracts in `docs/Theme-Pack-Contract.md`, `docs/Universal-Components-Contract.md`, and `docs/CSS-Tokens.md`.

This pipeline keeps missions deterministic, contributions auditable, and the control plane aware of the latest exports while respecting the `.env` + Wizard keystore boundaries.
