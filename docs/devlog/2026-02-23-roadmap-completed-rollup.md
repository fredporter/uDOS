# 2026-02-23 Roadmap Completed Items Rollup

## Purpose

Move completed roadmap items out of `docs/roadmap.md` so the roadmap remains active-only, with a single evidence-backed completion record.

## Completed Items Moved From Roadmap

### Cycle D (completed)

- Replaced `datetime.utcnow()` usage with timezone-aware UTC patterns across Core/Wizard.
- Removed return-style pytest warnings in `tests/integration/test_phase_ab.py`.
- Kept warning budgets visible in CI profile outputs.
- Completed MCP + FastAPI hardening track for `wizard/tests/test_mcp_server.py`.
- Completed full-post-fix validation sweep and CI/docs matrix parity work.

### Pre-v1.5 Critical Juncture (completed subset)

- Command contract/dispatch/alias convergence to one canonical path.
- Core networking hard-gated to Wizard-local loopback boundaries.
- WEB/HOME routing moved to Wizard-proxy shim behavior.
- Launch/session wrappers unified across Windows/Linux adapters.
- Canonical launch/session lifecycle contract enforced (`memory/wizard/launch/*.json`).
- Packaging metadata/version/offline-assets consolidated behind shared manifest + adapters.
- Hardcoded/fallback build version sources removed.
- Dead/forked legacy server/service pathways removed after parity checks.
- API/MCP/Sonic canonical runtime entrypoints collapsed to single modular surfaces.
- CI guardrails added for command parity and non-loopback literal network target rejection.

### Sonic Pending Round (completed subset)

- Consolidated Sonic GPU matrix logic to canonical `wizard/services/sonic_profile_matrix.py` and adopted in device/profile services.

### Quality Gate and Focus (completed subset)

- Enforced uv-based Python checks/tests.
- Kept inline type-ignore/noqa suppressions out of warning-cleanup work.
- Closed Cycle D execution focus items.

## Test Evidence

### Full-suite and warning evidence

- `docs/roadmap.md` Cycle D status record (captured before move) recorded:
  - `1966 passed, 3 skipped, 0 warnings` (post-fix clean-room run).
- Earlier triage baseline in `docs/.compost/historic/2026-03-03-devlog-interim-plans-and-progress/2026-02-23-roadmap-full-sweep-triage.md`:
  - `1946 passed, 5 failed, 3 skipped, 2 warnings`.
- Delta shows closure of previously triaged failure/warning buckets.

### MCP/FastAPI hardening evidence

- `docs/devlog/2026-02-23-mcp-fastapi-validation-map.md`:
  - Full 17-test contract map for `wizard/tests/test_mcp_server.py`.
  - Targeted run recorded as `17/17` passing.

### Startup/installer and packaging convergence evidence

- `docs/devlog/2026-02-23-installer-startup-entrypoint-cleanup.md`:
  - Startup and cross-installer dispatch contract cleanup.
  - Validation commands and targeted tests listed.
- Packaging adapter and manifest work is further detailed across:
  - `docs/devlog/2026-02-22-packaging-manifest-foundation.md`
  - `docs/devlog/2026-02-22-packaging-manifest-installer-wiring.md`
  - `docs/devlog/2026-02-22-packaging-manifest-windows-wiring.md`

## Notes

- This rollup is the canonical completion record for items removed from the active roadmap on 2026-02-23.
- Active and pending work remains in `docs/roadmap.md`.
