# Vault/Memory Contract (v1)

## Decision

uDOS uses a strict split between distributable markdown templates and runtime local state.

## Responsibilities

### `vault/` (repo root)

Use for distributable markdown scaffold only.

- Tracked in git
- Empty framework shape for new users
- No personal notes or synced account exports

### `core/framework/seed/vault/`

Use for canonical starter markdown seed content.

- Tracked in git
- Installed into `memory/vault/` by `bin/install-seed.py` / `REPAIR --seed`
- Versioned alongside framework seed bank files

### `memory/`

Use for local runtime state only.

- Not tracked in git
- User vault data: `memory/vault/`
- Runtime logs: `memory/logs/`
- Private credentials/tokens: `memory/private/` and `memory/bank/private/`
- Runtime databases/cache/wizard state: `memory/**`

## Consolidation Rules

1. Markdown intended for distribution belongs in `core/framework/seed/vault/` and mirrored scaffold docs in `vault/`.
2. User-generated markdown belongs in `memory/vault/`.
3. Runtime operational artifacts (logs, db, cache, secrets) stay in `memory/` and never move into `vault/`.
4. If a folder under `memory/` is needed only at runtime, keep it local and gitignored.

## Outcome

- `/vault` stays clean for publishing/distribution.
- `/memory` remains operational runtime state.
- Seed content has one canonical source under `core/framework/seed/`.
