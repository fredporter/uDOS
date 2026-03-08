# Empire Live Data Connect Playbook (Phase 5)

Purpose
- Controlled live-data connection for launch, with rollback safety.

Prerequisites
- Phase 4 checklist complete.
- Secrets configured in `config/empire_secrets.json`.
- Backup drill validated.
- Empire enabled through Wizard Extensions.

Cutover sequence
1. Freeze code and config for release candidate.
2. Run launch gate:
   `cd /Users/fredbook/Code/uDOS/extensions/empire && scripts/smoke/phase5_launch_gate.sh`
3. Verify integration credentials:
   - `hubspot_private_app_token`
   - `google_gmail_credentials_path`
   - `google_gmail_token_path`
   - `google_places_api_key`
4. Start API and verify token-auth health.
5. Enable one pilot org and run limited sync:
   - HubSpot: contacts+companies with small page/limit
   - Gmail: max small batch query
   - Places: constrained query/radius
6. Validate data quality in DB (`records`, `events`, `sources`) and UI read paths.
7. Expand from pilot org to full launch scope.
8. Record execution using `docs/empire-pilot-runsheet-template.md`.

Rollback triggers
- Any P0/P1 defect.
- Data integrity mismatch.
- Sustained API failures.

Rollback steps
1. Stop API and integration jobs.
2. Restore latest validated DB backup (see `docs/empire-restore-drill.md`).
3. Restart API and rerun smoke checks.
4. Re-open rollout only after defect triage closeout.

Phase 5 completion note
- This repository run completes the launch package and gate automation.
- Actual provider live-data cutover uses production credentials during rollout window.
