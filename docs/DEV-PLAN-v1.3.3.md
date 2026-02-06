# v1.3.3 Dev Plan (No Dates) — Rolled Forward

**Source of truth:** `docs/ROADMAP-TODO.md` (v1.3.3 Extension & Container Refactor)

## Scope
- Harden extension/container architecture for distributed, modular runtime.
- Stabilize Sonic as TUI entry point and plugin ecosystem.
- Confirm Groovebox/Songscribe stack readiness in library container layout.
- Advance Home Assistant container refactor integration.

## Priorities (Ordered)

### P0 — Extension & Container Infrastructure (Core/Extensions)
**Dependencies:** v1.3.2 complete
**Owner:** Core
**Status:** ✅ Complete
**Breakdown:**
- Audit container manifests and registry expectations across `library/*`.
- Verify plugin loader compatibility (Wizard + Core).
- Ensure container metadata aligns with `docs/PLUGIN-MANIFEST-SPEC.md`.

### P0 — Sonic → TUI Entry Point (Core/Sonic)
**Dependencies:** Extension/container infra
**Owner:** Core, Sonic
**Status:** ✅ Complete
**Breakdown:**
- Validate Sonic CLI scaffolding as primary TUI entry (commands, device catalog).
- Verify device database sync + USB flashing abstraction.
- Confirm plugin catalog wiring and registry health.

### P1 — Groovebox → Songscribe Stack (Library)
**Dependencies:** Extension/container infra
**Owner:** Wizard, Library
**Status:** Rolled to v1.3.4
**Breakdown:**
- Confirm module separation (synthesis engine vs UI).
- Validate plugin API for sample libraries + effects chains.
- Verify songscribe Markdown grammar + converters remain stable.

### P1 — Home Assistant Container Refactor (Library)
**Dependencies:** Extension/container infra
**Owner:** Wizard, Library
**Status:** Rolled to v1.3.4
**Breakdown:**
- Validate container-based deployment + uDOS config binding.
- Confirm REST/WebSocket gateway wiring to Wizard services.
- Verify device discovery + automation templates for Beacon/Sonic.

## Execution Notes
- App + Groovebox feature work rolled into v1.3.7 and completed.
- Keep container contracts aligned with `docs/PLUGIN-MANIFEST-SPEC.md` and `docs/ARCHITECTURE-v1.3.md`.
- Generated `manifest.json` files are unsigned placeholders; signing still required for distribution.
