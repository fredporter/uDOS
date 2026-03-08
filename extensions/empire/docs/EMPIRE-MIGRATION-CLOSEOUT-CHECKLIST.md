# Empire Migration Closeout Checklist

Status date: 2026-03-07

This checklist closes the transition from legacy Empire script-first operation to the current uDOS-internal, Wizard-activated extension model.

Execution plan: `extensions/empire/docs/EMPIRE-DEV-DEPLOY-PLAN-v1.5.2.md`
Final closeout note: `extensions/empire/docs/EMPIRE-MIGRATION-CLOSEOUT-NOTE-v1.5.2.md`

## Completed

- Removed the duplicate nested extension tree at `extensions/empire/empire`.
- Removed runtime checks that still expected the deleted nested tree.
- Empire activation is now explicit and Wizard-gated.
- HubSpot sync is wired through Wizard-owned Empire services.

## Canonical runtime contract

- Empire is an internal extension inside uDOS.
- Empire is disabled by default and must be enabled from Wizard Extensions.
- Wizard-owned services and routes are the canonical runtime entrypoints.
- `extensions/empire/scripts/*` are support utilities, smoke checks, or operator tools unless explicitly promoted into a Wizard-owned service.

## Script audit

### Keep as setup/operator utilities

- `scripts/setup/ci_seed_mock_secrets.sh`
- `scripts/setup/set_api_token.py`
- `scripts/setup/set_google_gmail_credentials_path.py`
- `scripts/setup/set_google_gmail_token_path.py`
- `scripts/setup/set_google_places_api_key.py`
- `scripts/setup/set_hubspot_token.py`
- `scripts/ops/monitor_runtime.py`

### Keep as smoke and release-gate utilities

- `scripts/smoke/api_perf_baseline.py`
- `scripts/smoke/api_smoke.py`
- `scripts/smoke/db_backup_restore_sanity.py`
- `scripts/smoke/integration_no_live_smoke.py`
- `scripts/smoke/integration_preflight.py`
- `scripts/smoke/phase5_launch_gate.sh`
- `scripts/smoke/run_phase2_api_smoke.sh`

### Keep temporarily as manual wrappers, but treat Wizard services as canonical

- `scripts/integrations/gmail_sync.py`
- `scripts/integrations/hubspot_sync.py`
- `scripts/integrations/places_sync.py`
- `scripts/ingest/run_ingest.py`

Wizard-owned replacements already exist in:

- `wizard/services/empire_sync_service.py`
- `wizard/services/empire_import_service.py`

Decision:

- keep these scripts as manual operator wrappers
- add in-file contract guidance pointing back to Wizard-owned routes/services
- do not expose them as primary runtime entrypoints in docs or UI

### Legacy/support utilities retained, but not supported as canonical runtime entrypoints

- `scripts/email/process_emails.py`
- `scripts/email/receive_emails.py`
- `scripts/process/normalize_records.py`
- `scripts/process/refresh_overview.py`

Decision:

- retain as legacy/operator utilities for manual recovery, migration, and standalone support work
- do not treat them as part of the supported Wizard runtime contract
- if they become product-critical again, promote them through Wizard-owned services/routes instead of expanding direct script usage

## Remaining closeout work

- [x] Replace stale docs that still use `/Users/fredbook/Code/uDOS/empire` with `extensions/empire`.
- [x] Remove stale “private submodule” language from Empire docs and operator notes.
- [x] Decide whether `scripts/process/refresh_overview.py` remains a supported operator utility.
- [x] Decide whether `scripts/email/*` remains part of the supported operational surface.
- [x] Add a short contract note to all remaining manual wrapper scripts saying Wizard routes/services are canonical.
- [x] Confirm Wizard UI copy for Empire uses the same disabled-by-default language everywhere.
- [x] Add one migration test that asserts Empire status does not mention any legacy nested-tree contract.

Checklist status: complete for the v1.5.2 internal-extension migration round.

## Verification notes

- Wizard dashboard build passes. Existing unrelated warning remains in `wizard/dashboard/src/routes/Devices.svelte` for a self-closing `textarea`.
- Empire route and release profile tests pass.
- Legacy DB schema migration for `tasks.review_status` is now covered by a dedicated regression test.
- Supported smoke subset results:
  - `integration_preflight.py --strict`: pass
  - `integration_no_live_smoke.py`: pass
  - `db_backup_restore_sanity.py`: pass
  - mock connector configuration seeded locally with `scripts/setup/ci_seed_mock_secrets.sh`

## Definition of done for Empire migration

- No runtime code references the removed nested Empire tree.
- No operator docs refer to Empire as a private submodule.
- No primary docs or runbooks point at `/Users/fredbook/Code/uDOS/empire`.
- Remaining scripts are explicitly classified as canonical, operator-only, smoke-only, or deprecated.
- HubSpot, Gmail, and Places live connector flows resolve through Wizard-owned services.
- Empire activation and protected-route behavior remain covered by tests.
- The standalone `extensions/empire/web` surface is explicitly marked legacy and is not treated as the supported runtime UI.
