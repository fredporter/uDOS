# Empire Dev Deploy Plan v1.5.2

Status date: 2026-03-07

This plan turns the Empire migration and activation work into an execution sequence that can be deployed and closed.

## Objective

Ship Empire as a stable internal uDOS extension with:

- explicit Wizard activation
- Wizard-owned runtime entrypoints
- HubSpot/Gmail/Places connector flows routed through Wizard services
- a reduced, classified script surface
- operator docs that match the current repo layout

## Scope

In scope:

- Empire extension runtime and Wizard integration
- operator setup and smoke scripts
- doc and runbook correction for the internal extension model
- migration of remaining supported manual workflows behind clear contracts

Out of scope:

- Android or macOS commercial app repos
- `uHOME-server`
- Sonic repo extraction work

## Deployment phases

### Phase 1: Runtime truth

- [x] Remove duplicate nested Empire tree
- [x] Remove runtime references to the nested tree
- [x] Make Empire disabled by default
- [x] Gate protected Empire routes behind Wizard activation
- [x] Ensure HubSpot sync resolves through Wizard-owned services

Exit gate:

- Empire status reports only the internal extension contract
- route tests and release profile tests pass

### Phase 2: Script surface reduction

- [x] Audit all remaining scripts
- [x] Classify scripts as operator, smoke, wrapper, or keep/retire decision
- [x] Add contract headers or README notes to remaining wrapper scripts
- [x] Decide whether `scripts/email/*` remains supported
- [x] Decide whether `scripts/process/refresh_overview.py` remains supported

Exit gate:

- no unsupported script is implied to be canonical runtime
- wrapper scripts clearly point back to Wizard services/routes

### Phase 3: Operator doc correction

- [x] Replace stale `/Users/fredbook/Code/uDOS/empire` paths with `extensions/empire`
- [x] Update historical phase checklists where they are still used operationally
- [x] Update operator guide and live-connect playbook to the internal extension contract
- [x] Remove all remaining “private submodule” language

Exit gate:

- operator docs no longer describe the old layout
- live runbooks can be executed against the current repo without path edits

### Phase 4: Runtime polish

- [x] Audit Wizard UI copy for Empire disabled-state consistency
- [x] Add one migration regression test proving Empire status exposes no nested-tree fields
- [x] Decide whether the legacy web app remains supported or archived
- [x] Replace any remaining script-first fallback messaging in UI with Wizard-first guidance

Exit gate:

- UI state, API state, and docs all describe the same activation model

### Phase 5: Closeout

- [x] Run Empire route and release profile test suite
- [x] Run the Empire smoke subset still classified as supported
- [x] Write final Empire migration closeout note
- [x] Mark the migration checklist complete

Exit gate:

- Empire can be treated as stable internal extension infrastructure for v1.5.2 follow-on work

## Working order

1. Clean Phase 3 operator docs and runbooks.
2. Lock Phase 4 regressions and UI consistency.
3. Run Phase 5 verification and write the closeout note.

## Required evidence

- Passing:
  - `uv run python -m pytest /Users/fredbook/Code/uDOS/wizard/tests/empire_routes_test.py /Users/fredbook/Code/uDOS/core/tests/release_profile_service_test.py`
- Passing:
  - `PYTHONPATH=/Users/fredbook/Code/uDOS/extensions /Users/fredbook/Code/uDOS/.venv/bin/python -m pytest /Users/fredbook/Code/uDOS/extensions/empire/tests/test_storage_schema_migration.py`
- Updated docs:
  - `extensions/empire/docs/EMPIRE-MIGRATION-CLOSEOUT-CHECKLIST.md`
  - `extensions/empire/docs/ARCHITECTURE.md`
  - `extensions/empire/scripts/README.md`
- No runtime references to:
  - `extensions/empire/empire`
  - “private submodule” contract language in active operator docs

## Current verification state

- `wizard/tests/empire_routes_test.py`: pass
- `core/tests/release_profile_service_test.py`: pass
- `extensions/empire/tests/test_storage_schema_migration.py`: pass
- `scripts/smoke/integration_preflight.py --db data/empire.db --strict`: pass
- `scripts/smoke/integration_no_live_smoke.py`: pass
- `scripts/smoke/db_backup_restore_sanity.py --db data/empire.db`: pass
- local mock connector configuration seeded with `scripts/setup/ci_seed_mock_secrets.sh`

Plan status: complete for the v1.5.2 internal-extension migration round.
