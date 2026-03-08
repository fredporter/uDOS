# Empire Migration Closeout Note v1.5.2

Date: 2026-03-07

Empire migration is closed for the v1.5.2 internal-extension round.

## Final state

- Empire is an internal uDOS extension.
- Empire is disabled by default and activated explicitly through Wizard Extensions.
- Wizard-owned routes and services are the canonical runtime surface.
- HubSpot, Gmail, and Places connector lanes resolve through the Wizard-owned Empire service layer.
- The duplicate nested extension tree has been removed.
- The standalone `extensions/empire/web` app remains in-repo as a legacy reference surface and is not the supported runtime UI.

## Verified evidence

- `wizard/tests/empire_routes_test.py`: pass
- `core/tests/release_profile_service_test.py`: pass
- `extensions/empire/tests/test_storage_schema_migration.py`: pass
- `extensions/empire/scripts/smoke/integration_preflight.py --db data/empire.db --strict`: pass
- `extensions/empire/scripts/smoke/integration_no_live_smoke.py`: pass
- `extensions/empire/scripts/smoke/db_backup_restore_sanity.py --db data/empire.db`: pass
- Wizard dashboard build: pass

## Dev environment note

Local strict preflight is now satisfied using the repo-supported mock connector configuration seeded by `extensions/empire/scripts/setup/ci_seed_mock_secrets.sh`.

## Closeout decision

Empire and Wizard can now be treated as stable internal extension infrastructure for follow-on v1.5.2 work. Remaining work in this repo should be feature development, real provider credential rollout, or commercial product integration, not migration cleanup.
