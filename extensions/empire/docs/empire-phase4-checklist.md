# Empire Phase 4 Checklist (Pre-Alpha Hardening)

Goal: performance and resilience hardening before live data.

## Scope
- Empire internal extension only.
- Hardening includes non-web checks plus web build validation.

## Checklist

Performance
- [x] API baseline script added
- [x] API baseline executed and recorded
- [x] Performance budget thresholds agreed for alpha gate

Resilience
- [x] DB backup/restore sanity script added
- [x] DB backup/restore sanity executed and recorded
- [x] Restore drill documented for operations handoff

Security
- [x] Secret files and local credential artifacts ignored in git
- [x] Integration preflight strict mode passing (from Phase 3)
- [x] Token rotation workflow smoke-tested and documented

Exit Criteria
- [x] Regression suite green (non-web + web)
- [x] No P0/P1; max 3 P2 with documented workaround
- [x] Go/No-Go RC sign-off

## Commands
- Start API for perf baseline:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 -m uvicorn empire.api.server:app --host 127.0.0.1 --port 8991`
- Run perf baseline:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/api_perf_baseline.py --base-url http://127.0.0.1:8991 --iterations 25`
- Run DB backup/restore sanity:
  `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/db_backup_restore_sanity.py --db data/empire.db`
- Run web build regression:
  `cd /Users/fredbook/Code/uDOS/extensions/empire/web && npm install && npm run build`

## Execution Log
- 2026-02-15: Phase 4 started; hardening scripts added.
- 2026-02-15 API perf baseline (`n=25`): `health avg=2.05ms p95=1.97ms max=13.12ms`; `records avg=2.05ms p95=2.21ms max=2.85ms`; `events avg=2.23ms p95=2.69ms max=2.71ms`; `tasks avg=2.02ms p95=2.30ms max=2.50ms`.
- 2026-02-15 DB backup/restore sanity: backup created at `data/backups/empire-20260215T023518Z.db`, restore validated at `data/restore-check/restore-20260215T023518Z.db`, `integrity_check=ok`, counts matched source (`records=2`, `events=135`, `sources=1`, `tasks=0`, `companies=0`, `contact_companies=0`).
- 2026-02-15 Token rotation smoke: `POST /auth/rotate` returned `200`, issued replacement token length `43`.
- 2026-02-15 API perf baseline rerun (`n=25`, token mode): `health avg=2.13ms p95=2.07ms max=15.25ms`; `records avg=2.01ms p95=2.44ms max=2.52ms`; `events avg=2.22ms p95=2.56ms max=2.63ms`; `tasks avg=2.02ms p95=2.42ms max=2.63ms`.
- 2026-02-15 Performance budget documented in `docs/empire-performance-budget.md`.
- 2026-02-15 Restore drill documented in `docs/empire-restore-drill.md`.
- 2026-02-15 Regression suite green:
  - `scripts/smoke/run_phase2_api_smoke.sh` passed twice (auth-aware mode).
  - `scripts/smoke/integration_preflight.py --strict` passed (`PASS=11 WARN=0 FAIL=0`).
  - `scripts/smoke/integration_no_live_smoke.py` passed (HubSpot/Gmail/Places mocked flows).
  - `scripts/smoke/db_backup_restore_sanity.py` passed.
  - `web` build passed (`npm install`, `npm run build`).
- 2026-02-15 Defect posture: P0=0, P1=0, P2=0 open for Phase 4 gate; `npm audit --omit=dev` reports `0` runtime vulnerabilities.
- 2026-02-15 RC decision: GO for Alpha hardening completion (Phase 4), with live-data rollout controlled in Phase 5.
