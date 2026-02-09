# Roadmap Checklist (Active)

Last updated: 2026-02-09

## P0 — Wizard/Vibe Refactor
- [x] Add MCP server tests to verify stdio tool wrapping + tool index parsing.
- [x] Bootstrap Vibe integration (embed) and minimal uCODE command exposure.
- [x] Enforce Dev mode gate (admin-only + `/dev/` presence) and document policy contract.

## P0 — Consolidation & Verification
- [x] Implement Logging API v1.3 endpoints per `docs/LOGGING-API-v1.3.md`.
- [x] Add integration checks for MCP gateway + Wizard health/tool list.

## P1 — Platform & Extensions
- [x] Reintroduce Empire business features on new extension spine.

## P2 — Code Quality (Pre-v1.4)
- [x] Review long route factory functions for modularization.
- [x] Consider splitting nested route handlers into separate modules.

## Notes
- This checklist mirrors `docs/ROADMAP-STATUS.md` and should be kept in sync.
- All items complete as of v1.3.9 (2026-02-09).
