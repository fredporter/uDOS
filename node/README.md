# Node Container Compose

This compose file demonstrates how the `node/` deliverable hosts the Wizard services plus renderer, AI router, and SvelteKit admin (`web-admin/`). It mounts the shared `vault/` and `themes/` directories so each lane can read the Markdown vault, render via the theme packs, and expose static sites through the portal-static service.

## New services

- **`vibe-cli`**: Runs the Mistral Vibe CLI (`mistral-vibe`) so the local AI lane and mission scheduler can propose edits, patch bundles, and contributions via `wizard/extensions/assistant/vibe_cli_service.py`.
- **`mission-scheduler`**: Watches `vault/contributions/pending`, triggers `/api/renderer/render`, and writes run reports/logs into `vault/06_RUNS` and `vault/07_LOGS` so contributions drive the static export pipeline and mission metadata the Svelte components consume.

## Mission workflow

1. Vibe CLI accepts AI prompts or mission triggers and surfaces tasks/patch bundles to the contributions folder.
2. The mission scheduler apprentices through the contribution queue, posts render jobs to `/api/renderer/render`, and records mission/job metadata under `vault/06_RUNS`.
3. After each render, the scheduler pulls place metadata from `/api/renderer/places` and seeds the spatial SQLite (`vault/.udos/state.db` or `vault/05_DATA/sqlite/udos.db`) with anchors, locations, and file tags so the spatial APIs stay current.
4. The renderer service turns Markdown into `_site/<theme>` outputs, while the `/api/renderer/*` endpoints publish the metadata consumed by `web-admin` theme pickers and wizard portal UIs.
