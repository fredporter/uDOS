# Empire Phase 3 Checklist (Integrations, No Live Data)

Goal: all integrations active, configurable, and passing tests without live data.

## Scope
- Integrations: HubSpot, Gmail, Google Places.
- No external live data writes.
- Validation via config/dependency preflight and local normalization path.

## Checklist

Preflight
- [x] Integration preflight script exists
- [x] DB schema readiness validated
- [x] HubSpot token configured (`hubspot_private_app_token`)
- [x] Gmail credentials path configured (`google_gmail_credentials_path`)
- [x] Gmail token path configured (`google_gmail_token_path`)
- [x] Google Places API key configured (`google_places_api_key`)

Execution
- [x] Preflight run executed (non-strict)
- [x] Preflight run executed in strict mode
- [x] Preflight run executed in strict mode with zero WARN/FAIL
- [x] Integration sync smoke commands validated in no-live-data/sandbox mode

Exit Criteria
- [x] HubSpot preflight PASS (config + import + normalization)
- [x] Gmail preflight PASS (config + import + normalization)
- [x] Places preflight PASS (config + import + normalization)
- [x] No FAIL and no WARN in strict preflight

## Commands
- Non-strict preflight:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/integration_preflight.py --db data/empire.db`
- Strict preflight:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/integration_preflight.py --db data/empire.db --strict`
- Mocked integration sync smoke (no live APIs):
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/integration_no_live_smoke.py`
- Configure HubSpot token:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_hubspot_token.py --token '<value>'`
- Configure Gmail credentials path:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_google_gmail_credentials_path.py --path '/absolute/path/credentials.json'`
- Configure Gmail token path:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_google_gmail_token_path.py --path '/absolute/path/token.json'`
- Configure Places API key:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_google_places_api_key.py --api-key '<value>'`

## Execution Log
- 2026-02-15: Phase 3 preparation started with integration preflight harness.
- 2026-02-15 Non-strict preflight: `PASS=7 WARN=4 FAIL=0`.
- 2026-02-15 Strict preflight: failed as expected (`exit_code=1`) due to 4 WARN (missing HubSpot token, Gmail credentials path, Gmail token path, Places API key).
- 2026-02-15 Mocked no-live sync smoke: passed for HubSpot (`contacts=1, companies=1`), Gmail (`contacts=2`), and Places (`records=1`) against temp DB.
- 2026-02-15 Configuration set for no-live Phase 3 validation using placeholder values/paths.
- 2026-02-15 Strict preflight rerun: `PASS=11 WARN=0 FAIL=0`.
