# Empire Operator Guide (Phase 5)

Empire is an internal uDOS extension. Enable it through Wizard Extensions before using Empire routes or operational flows.

Runbook
- Start API:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 -m uvicorn empire.api.server:app --host 127.0.0.1 --port 8991`
- API smoke:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && scripts/smoke/run_phase2_api_smoke.sh`
- Integration preflight:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/integration_preflight.py --db data/empire.db --strict`
- Launch gate:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && scripts/smoke/phase5_launch_gate.sh`

Secret management
- Set HubSpot token:
  `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_hubspot_token.py --token '<value>'`
- Set Gmail credentials path:
  `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_google_gmail_credentials_path.py --path '/abs/path/credentials.json'`
- Set Gmail token path:
  `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_google_gmail_token_path.py --path '/abs/path/token.json'`
- Set Places API key:
  `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_google_places_api_key.py --api-key '<value>'`

Incident response
- Follow `docs/empire-monitoring-checklist.md` for alert triage.
- Follow `docs/empire-restore-drill.md` for restore rollback.
