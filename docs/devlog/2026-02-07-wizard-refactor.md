# Wizard Server Refactor + Version Bump

**Date:** 2026-02-07  
**Status:** ✅ Complete  
**Impact:** Medium — Wizard server wiring cleanup + version bump

---

## Summary

Completed the Wizard server refactor by extracting non‑wiring logic into services and helpers. Updated version metadata and added a Wizard changelog entry.

---

## Work Completed

- Extracted Wizard server logic into services:
  - Auth/session handling
  - Log reading
  - System stats collection
  - Web proxy service wrapper
  - Plugin repository service
  - Scheduler runner
  - Webhook utilities
  - Fallback dashboard HTML
  - Environment loader
  - Wizard config model
- Wired `wizard/server.py` to the new services.
- Bumped versions:
  - `uDOS` → `v1.3.9`
  - `Wizard` → `v1.1.2`
- Added Wizard changelog entry at `dev/roadmap/CHANGELOG-wizard.md`.

---

## Next Steps

1. Continue MCP gateway extraction and tool surface definition.
2. Bootstrap Vibe TUI replacement and uCODE command exposure.
3. Enforce Dev mode gate (admin‑only + `/dev/` presence) and document policy contract.
