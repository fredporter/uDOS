# 3DWORLD Extension Spec v1.5.0 (Draft)

Superseded for extension boundary authority by:
- `docs/specs/3DWORLD-EXTENSION-CONTRACT-v1.5.md`

Status: Draft for Cycle D
Owner: Core + Extensions + Wizard
Last Updated: 2026-02-22

## 1. Scope

This specification defines how 3DWORLD is packaged and integrated as an optional heavy extension.

Normative goals:
- preserve canonical uDOS gameplay semantics
- support renderer/client adapters without gameplay forking
- provide deterministic mapping for LENS, SKIN, GRID, and Z-axis semantics

## 2. Packaging Requirements

3DWORLD MUST be shipped at `/extensions/3dworld/`.

3DWORLD MUST include:
- `manifest.json`
- `container.json`
- extension service entrypoint(s)
- contract/schema definitions for gameplay-to-3D mapping

3DWORLD SHOULD follow the same containerized extension policy model as `/extensions/groovebox/`.

3DWORLD MUST be optional; core gameplay MUST remain available when 3DWORLD is not installed or disabled.

## 3. Canonical Ownership

uDOS core is canonical for:
- IDs, anchors, and location identity
- gameplay state progression
- LENS and SKIN semantic state
- GRID coordinate semantics, including z-axis meaning
- permissions and policy gates

3DWORLD is canonical only for:
- scene construction and rendering
- client input/output adaptation
- non-authoritative render caches and perf telemetry

3DWORLD MUST NOT mint canonical gameplay IDs or persistence records outside core contracts.

## 4. Mapping Contract

Required mapping keys:
- `lens_state`
- `skin_state`
- `grid_location` (`x`, `y`, `z`, anchor metadata)
- `gameplay_context` (active objectives/events)

Normative mapping behavior:
- LENS MUST control camera/discovery behavior.
- SKIN MUST control material/theme and visual layer representation.
- GRID LOCATION MUST anchor entities/chunks/regions in world space.
- Z-axis MUST map to deterministic elevation/progression semantics.

At v1.5, z-axis MAY render as lightweight elevation hints, but semantics MUST be preserved.

## 5. Adapter Model

Adapter targets (phased):
- desktop client (phase 1)
- VR client (phase 2)
- uHOME-compatible game-console UX (phase 2)

Each adapter MUST consume the same normalized mapping contract.

Adapter-specific rendering details MUST remain isolated from canonical gameplay state.

## 6. Runtime and Failure Semantics

When 3DWORLD is unavailable:
- core gameplay MUST continue without hard failure
- adapter requests MUST return explicit unavailable/degraded status
- no canonical gameplay mutations may be dropped silently

When 3DWORLD is enabled:
- mapping must be deterministic for identical gameplay snapshots
- unsupported adapter capabilities MUST degrade gracefully

## 7. Test Requirements

Minimum test set:
- mapping determinism tests for LENS/SKIN/GRID/Z inputs
- enable/disable lifecycle tests (no gameplay regression)
- contract validation tests for mapping schema
- adapter smoke tests for desktop, and stubs for VR/uHOME adapters until full implementation

## 8. Non-Goals (v1.5)

- mandatory VR support
- engine-specific gameplay authority
- photoreal rendering baselines that block low-resource devices

## 9. Open Decisions

- final adapter protocol shape (sync snapshot vs event-stream hybrid)
- asset bundle distribution path for large world packs
- multiplayer/shared-world transport requirements in relation to MeshCore and Wizard networking tracks
