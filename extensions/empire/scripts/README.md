# Empire Scripts

Empire is an internal uDOS extension. These scripts are not the primary runtime surface.

Canonical runtime entrypoints:

- Wizard Extensions activation state
- Wizard Empire routes
- Wizard-owned Empire services in `/Users/fredbook/Code/uDOS/wizard/services`

Use the scripts here for operator setup, smoke checks, and manual support flows unless a script is explicitly promoted into the Wizard-owned runtime.

Structure:

- `email/` legacy/support email processing utilities
- `ingest/` manual intake and staging helpers
- `integrations/` manual connector wrappers
- `ops/` operator health and monitoring helpers
- `process/` legacy/support normalization utilities
- `setup/` secret and credential bootstrap helpers
- `smoke/` repeatable local smoke and launch-gate checks

High-value commands:

- `python scripts/ingest/run_ingest.py <input.csv> --out data/raw/records.jsonl`
- `scripts/smoke/run_phase2_api_smoke.sh`
- `EMPIRE_API_TOKEN=phase2token scripts/smoke/run_phase2_api_smoke.sh`
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/integration_preflight.py --db data/empire.db`
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/integration_no_live_smoke.py`
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/api_perf_baseline.py --base-url http://127.0.0.1:8991 --iterations 25`
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/db_backup_restore_sanity.py --db data/empire.db`
- `scripts/smoke/phase5_launch_gate.sh`
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/ops/monitor_runtime.py --db data/empire.db --samples 30 --interval-s 2`
- `scripts/setup/ci_seed_mock_secrets.sh`
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_google_places_api_key.py --api-key '<value>'`

Script classification and remaining migration work are tracked in `/Users/fredbook/Code/uDOS/extensions/empire/docs/EMPIRE-MIGRATION-CLOSEOUT-CHECKLIST.md`.
