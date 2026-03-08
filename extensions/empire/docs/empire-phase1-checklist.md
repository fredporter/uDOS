# Empire Phase 1 Checklist (Internal Beta v0.0.1)

Goal: establish test baseline and defect inventory.

## Scope
- Internal Empire extension only
- Must remain separate from public uDOS paths
- Compatibility with uDOS core is required

## Checklist

Baseline
- [ ] Confirm Empire extension tree is present and on expected working state
- [x] Verify Empire API start (local)
- [ ] Verify Empire web build/start (local)

Test Matrix
- [x] API: health, auth, list endpoints
- [x] Ingest: file ingest (records.jsonl)
- [x] Normalize: records normalization output
- [x] Storage: DB write + read sanity
- [ ] UI: core routes load, no console errors

Smoke Suite
- [x] Create/confirm smoke run steps (script or documented steps)
- [x] Run smoke suite 3 times
- [x] Record pass/fail outcomes

Defect Triage
- [x] Define severity labels (P0/P1/P2/P3)
- [x] Log and assign all P0/P1
- [x] Daily triage cadence set

Exit Criteria
- [ ] Full test matrix completed end-to-end
- [ ] All P0/P1 defects triaged with owners
- [ ] Clean build + start for API and web

## Execution Log (2026-02-15)

Environment notes
- Web checks intentionally deferred by request.
- `npm install` remains blocked in this sandbox context and was not required for this run.

Run 1 outcomes
- API start: pass (`uvicorn empire.api.server:app` on `127.0.0.1:8991`).
- API endpoints: pass (`/health`, `/records`, `/events`, `/tasks`).
- Auth behavior: running in no-token mode (no `EMPIRE_API_TOKEN` configured), token enforcement not exercised in this pass.
- Ingest: pass (`data/raw/phase1_fixture.csv` -> `data/raw/phase1_records.jsonl`, 2 records).
- Normalize: pass (`data/raw/phase1_records.jsonl` -> `data/normalized/phase1_records.jsonl`, 2 records, persisted).
- Storage sanity: pass (records/events/sources persisted in `data/empire.db`; verified by SQLite queries).

Run 2 outcomes
- Ingest: pass (`data/raw/phase1_fixture.csv` -> `data/raw/phase1_records_run2.jsonl`, 2 records).
- Normalize: pass (`data/raw/phase1_records_run2.jsonl` -> `data/normalized/phase1_records_run2.jsonl`, 2 records, persisted).

Run 3 outcomes
- Ingest: pass (`data/raw/phase1_fixture.csv` -> `data/raw/phase1_records_run3.jsonl`, 2 records).
- Normalize: pass (`data/raw/phase1_records_run3.jsonl` -> `data/normalized/phase1_records_run3.jsonl`, 2 records, persisted).

Auth check outcomes
- Token-protected mode validated with `EMPIRE_API_TOKEN=phase1token`.
- Missing token: `401`.
- Wrong token: `403`.
- Correct token: `200` on `/health`.

Defect triage setup
- Severity model and daily cadence documented in `docs/empire-defect-triage.md`.
- Current status: no P0/P1 defects identified in Phase 1 non-web runs.

Known blockers / follow-up
- Web build/start still pending for Phase 1 completion.
- Extension working tree is currently not clean due to generated Phase 1 data artifacts (`data/raw`, `data/normalized`, and updated `data/empire.db`).
