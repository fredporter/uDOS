# Empire Phase 2 Checklist (Alpha Stabilization v1.0.0)

Goal: stability and UX polish on current scope.

## Scope (current pass)
- Empire internal extension only.
- Non-web stabilization first (web tests deferred by request).
- Compatibility with uDOS core preserved.

## Checklist

API Hardening
- [x] Remove known deprecation warning in API parameter validation
- [x] Add repeatable API smoke script
- [x] Verify smoke script against local API (no-token mode)
- [x] Verify smoke script auth checks in token-protected mode

Stability
- [x] No P0/P1 defects open
- [x] 3 consecutive green smoke runs (Phase 2 smoke)
- [ ] No blocking UI errors on core flows (pending web run)

Operational
- [x] Document smoke command(s)
- [x] Decide handling for generated Phase 1/2 test artifacts in `data/`

## Smoke Commands
- Start API (no-token mode):
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 -m uvicorn empire.api.server:app --host 127.0.0.1 --port 8991`
- Smoke run (no-token mode):
  `cd /Users/fredbook/Code/uDOS/extensions/empire && python3 scripts/smoke/api_smoke.py --base-url http://127.0.0.1:8991`
- Start API (token mode):
  `cd /Users/fredbook/Code/uDOS/extensions/empire && EMPIRE_API_TOKEN=phase2token PYTHONPATH=/Users/fredbook/Code/uDOS python3 -m uvicorn empire.api.server:app --host 127.0.0.1 --port 8991`
- Smoke run (token mode + auth assertions):
  `cd /Users/fredbook/Code/uDOS/extensions/empire && python3 scripts/smoke/api_smoke.py --base-url http://127.0.0.1:8991 --token phase2token --expect-auth`

## Execution Log
- 2026-02-15: Phase 2 commenced with API hardening and smoke automation.
- 2026-02-15 Run #1 (no-token): `api_smoke.py` passed (`health`, `records`, `events`, `tasks`).
- 2026-02-15 Run #2 (token + auth): `api_smoke.py --token phase2token --expect-auth` passed, including `401/403/200` auth checks.
- 2026-02-15 Run #3 (no-token): `api_smoke.py` passed again; Phase 2 smoke target reached (3 consecutive green).
- 2026-02-15 Operational hardening: added one-command runner `scripts/smoke/run_phase2_api_smoke.sh` and validated in no-token and token/auth modes.
- 2026-02-15 Artifact policy: added `.gitignore` rules for generated local test outputs in `data/raw/*.jsonl`, `data/normalized/*.jsonl`, and `data/raw/phase*_fixture.csv`.
