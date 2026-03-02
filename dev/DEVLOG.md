# DEVLOG.md — Dev Mode Extension Log

Last Updated: 2026-03-02
Project: uDOS v1.5 Dev Mode Extension
Status: Active

---

## Purpose

This log tracks implementation progress, key decisions, and verification work for the v1.5 Dev Mode extension and related pre-release basework.

---

## Entries

### 2026-03-02: Dev Extension Runtime Rebaseline

**Status:** Completed

**Changes:**
- Reframed `/dev` as the Dev Mode extension framework root with a real manifest at [`/Users/fredbook/Code/uDOS/dev/extension.json`](/Users/fredbook/Code/uDOS/dev/extension.json)
- Added a centralized Wizard-side Dev extension service in [`/Users/fredbook/Code/uDOS/wizard/services/dev_extension_service.py`](/Users/fredbook/Code/uDOS/wizard/services/dev_extension_service.py)
- Removed active Goblin/server assumptions from the Dev Mode command/runtime path
- Updated Wizard Dev GUI and policy docs to match the explicit TUI/Dev tooling model

**Testing:**
- `uv run python -m compileall core/commands/dev_mode_handler.py wizard/services/dev_mode_service.py wizard/services/dev_extension_service.py wizard/routes/dev_routes.py`
- `npm run build` in `wizard/dashboard`

**Next Steps:**
- Consolidate remaining direct dev/library/GitHub flows behind the Dev extension service
- Remove broad legacy Goblin references outside the active runtime path

### 2026-03-02: Library Operator Workflow Hardening

**Status:** Completed

**Changes:**
- Added repo URL normalization/validation and install-wizard flow in [`/Users/fredbook/Code/uDOS/wizard/routes/library_routes.py`](/Users/fredbook/Code/uDOS/wizard/routes/library_routes.py)
- Extended container discovery so cloned repos under `library/containers` can be launched directly
- Added Thin GUI readiness polling and per-row dependency install actions in [`/Users/fredbook/Code/uDOS/wizard/dashboard/src/routes/Library.svelte`](/Users/fredbook/Code/uDOS/wizard/dashboard/src/routes/Library.svelte)
- Replaced raw inventory JSON rendering with a structured dependency operator surface

**Testing:**
- `uv run python -m pytest -q wizard/tests/library_routes_crud_versioning_test.py`
- `npm run build` in `wizard/dashboard`

**Next Steps:**
- Add launch-health/status drilldown for newly installed containers
- Add dependency remediation guidance when package-manager installation is unavailable on the host OS

### 2026-03-03: Creator Profile Acceptance Pass Started

**Status:** In Progress

**Changes:**
- Added initial creator-profile blocker matrix at [`/Users/fredbook/Code/uDOS/docs/decisions/v1-5-creator-blocker-matrix.md`](/Users/fredbook/Code/uDOS/docs/decisions/v1-5-creator-blocker-matrix.md)
- Mapped the current blocked areas: transcription, score export, sound-library health, creator install verification, and queue/health evidence
- Linked the creator acceptance pass back into the canonical roadmap

**Testing:**
- Documentation/planning pass only

**Next Steps:**
- Replace transcription scaffolds with explicit job-backed runtime behavior
- Add creator-profile verification and acceptance tests

---

End of Log
