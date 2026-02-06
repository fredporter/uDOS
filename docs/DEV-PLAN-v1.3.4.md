# v1.3.4 Dev Plan (No Dates)

**Source of truth:** `docs/ROADMAP-TODO.md` (v1.3.4 Physical & Distributed Systems)

## Scope
- Execute physical/distributed system deliverables.
- Complete rolled-forward v1.3.3 refactors (Groovebox/Songscribe, Home Assistant).

## Priorities (Ordered)

### P0 — Rolled-Forward Refactors (Library)
**Dependencies:** v1.3.3 P0 complete
**Owner:** Wizard, Library
**Status:** ✅ Complete
**Breakdown:**
- Groovebox → Songscribe refactor: plugin API, converters, grammar stability.
- Home Assistant container refactor: config binding, REST/WS gateway, discovery templates.

### P1 — Alpine Baremetal Concept (distribution/alpine-core)
**Dependencies:** none
**Owner:** Distribution
**Status:** ✅ Complete
**Breakdown:**
- udos-gui launcher + OpenRC services
- Tauri packaging target
- Persistence strategy (UDOS_PERSIST + apkovl)
- Recovery/failure mode handling
- Package list (single source of truth)
- Documentation: `docs/tier2-one-app-gui.md`

### P1 — Windows 10 Entertainment Stack (distribution/windows10-entertainment)
**Dependencies:** none
**Owner:** Distribution, Sonic
**Status:** ✅ Complete
**Breakdown:**
- Partition layout + controller input mapper
- Media/Game mode launchers
- Recovery hooks + LTSC image builder

### P1 — Beacon Portal Infrastructure (wizard/ + library/beacon)
**Dependencies:** none
**Owner:** Wizard, Beacon
**Status:** ✅ Complete
**Breakdown:**
- Router-agnostic config tooling
- Captive portal templates + status page
- Offline fallback messaging

## Execution Notes
- Keep container contracts aligned with `docs/PLUGIN-MANIFEST-SPEC.md`.
- App/Groovebox feature work rolled into v1.3.7 and completed.
