# v1.3.2 Dev Plan (No Dates) — ✅ COMPLETE

**Source of truth:** `docs/ROADMAP-TODO.md` (Spec-Aligned section)

## Scope
- Implement v1.3 contracts (Vault, Theme Pack, Engine-Agnostic World) and ship the spec-aligned runtime + tooling.
- Progress spatial runtime (UGRID + gameplay anchors + world lenses).
- Align TUI, uCODE, and Vibe CLI workflow.
- Add Wizard AI modes and theme validation + previews.

## Priorities (Ordered)

### P0 — Contract Foundation (Core/Docs)
**Dependencies:** none
**Owner:** Core
**Status:** ✅ Complete
**Breakdown:**
- Vault Contract validation in core runtime + docs cross-links
- Theme Pack Contract validation in core tooling
- Engine-Agnostic World Contract enforcement (LocId invariants)

### P0 — UGRID Core (Core)
**Dependencies:** Fractal grid + universe mapping complete
**Owner:** Core
**Status:** ✅ Complete
**Breakdown:**
- Grid canvas primitives + overlays
- LocId overlay rendering + deterministic tests
- Map block runtime hooks

### P0 — Gameplay Anchors (Core/Sonic)
**Dependencies:** UGRID Core, Engine-Agnostic World Contract
**Owner:** Core, Sonic
**Status:** ✅ Complete
**Breakdown:**
- Anchor registry runtime interfaces
- Validation rules for anchor data
- Adapter surface for Sonic/TUI access

### P1 — World Lenses (Core/Extensions)
**Dependencies:** UGRID Core
**Owner:** Core
**Status:** ✅ Complete
**Breakdown:**
- Godot 2D/2.5D adapter MVP
- O3DE prototype adapter
- Minimal integration test harness

### P1 — uCODE Prompt Spec (Core/TUI)
**Dependencies:** none
**Owner:** Core
**Status:** ✅ Complete
**Breakdown:**
- OK/: commands
- Slash routing
- Dynamic autocomplete
- Shared parser updates

### P1 — TUI ↔ Vibe Integration (Core/Extensions)
**Dependencies:** uCODE Prompt Spec, ENV boundary contract
**Owner:** Core
**Status:** ✅ Complete
**Breakdown:**
- Shared IO boundary
- Keystore access rules
- Runtime router wiring

### P1 — Vibe CLI Workflow Alignment (Core)
**Dependencies:** TUI ↔ Vibe Integration
**Owner:** Core
**Status:** ✅ Complete
**Breakdown:**
- Map recommended flows to uCODE commands
- Close routing gaps
- UX notes in roadmap

### P1 — Vibe capabilities track (Core)
**Dependencies:** TUI ↔ Vibe Integration
**Owner:** Core
**Status:** ✅ Complete
**Breakdown:**
- Natural language routing
- Code assistance
- Code analysis surfaces

### P1 — Wizard AI Modes (Wizard)
**Dependencies:** AI-MODES spec
**Owner:** Wizard
**Status:** ✅ Complete
**Breakdown:**
- Mode contract (conversation/creative)
- Local model defaults
- `/api/ai/complete` policy enforcement

### P1 — Theme Validation Tooling (Wizard/Extensions)
**Dependencies:** Theme Pack Contract
**Owner:** Wizard
**Status:** ✅ Complete
**Breakdown:**
- Pack validator
- CLI/endpoint integration
- Failure reporting

### P2 — Theme Packs + Previews (Wizard/App)
**Dependencies:** Theme Validation Tooling
**Owner:** Wizard, App
**Status:** ✅ Complete
**Breakdown:**
- NES/teletext/C64/medium packs
- Export tests
- Preview endpoints for app + dashboard

## Execution Notes
- App and Groovebox were rolled into v1.3.7 and completed.
- Keep contract changes in lockstep with `docs/specs/` and `docs/*-Contract.md`.
