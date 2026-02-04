# Contributions Contract

Per `docs/uDOS-v1-3.md` sections 3 and 7, contributions flow as patch bundles and are always reviewed before touching the vault.

## Principles
- Contributions are never applied automatically; they land in a queue for review (Wizard portal / SvelteKit control plane).
- Vault Markdown remains the source of truth; contributions modify Markdown files via deterministic patches.
- WordPress and other public lanes never become sources of truth—they only consume published snapshots and emit new bundles for review.

## Patch bundle format
A bundle may include:
- Metadata (contributor identity, timestamp, mission/job ID, target vault path)
- File diffs (unified patches or JSON patch lists)
- Optional task updates (line numbers, status changes)
- Optional theme metadata when a published snapshot references a new pack

Control surfaces (`wizard/`, `web-admin/`, `Vibe CLI`) must verify signatures, check permission levels, and log every bundle before applying changes.

## Storage
- Bundles are catalogued via the SQLite state in the vault (`.udos/state.db` or `05_DATA/sqlite/udos.db`).
- Audit logs and run reports reference bundle IDs (`vault/07_LOGS/` or `vault/06_RUNS/`).
