# 3DWORLD Extension Architecture (v1.5 Planning)

Canonical extension authority now lives in:
- `docs/specs/3DWORLD-EXTENSION-CONTRACT-v1.5.md`

Status: Planned (pre-v1.5 stable)
Owner: Core + Extensions + Wizard networking
Updated: 2026-02-22

## Purpose

3DWORLD is a heavy rendering and simulation extension that maps canonical uDOS gameplay state into explorable 3D scenes.

Design rule: uDOS remains the source of truth for gameplay semantics. 3D engines are render/execution lenses.

## Why Extension Packaging

3DWORLD has materially different runtime cost (rendering, assets, optional VR), so it should not be bundled into core runtime paths.

Package model:
- Location: `/extensions/3dworld/`
- Pattern: containerized extension, same deployment shape as `/extensions/groovebox/`
- Activation: optional install/enable, not required for baseline uDOS gameplay

## Canonical Boundary

uDOS owns:
- gameplay state and rules
- LENS and SKIN progression semantics
- GRID identity, indexing, and permissions
- coordinate model (`x`, `y`, `z`) and world anchors

3DWORLD owns:
- scene graph construction
- rendering pipeline selection
- client-specific input/output adaptation (desktop, VR, uHOME console)
- asset streaming and visual LOD policy

Engines/clients must not invent canonical IDs or persistence semantics.

## Mapping Contract (Gameplay -> 3D)

Minimum stable mapping:
- `LENS` -> camera mode, discoverability overlays, interaction affordances
- `SKIN` -> material/theme layer bindings for world entities
- `GRID LOCATION` -> world anchor and chunk/region placement
- `Z axis` -> vertical progression/elevation semantics (already present in core calculations)

Initial implementation can keep z-axis mostly logical while producing visual elevation hints.

## Runtime Topology

### Core to Extension Interface

3DWORLD consumes normalized gameplay snapshots/events from uDOS and renders deterministic world states.

Required inputs:
- resolved grid coordinates and anchor IDs
- current LENS/SKIN context
- active gameplay/objective state
- policy constraints (visibility/access/gating)

Expected outputs:
- render state summaries
- interaction events mapped back to canonical gameplay actions
- optional telemetry for perf/diagnostics

### Client Surfaces

Supported client targets (phased):
- desktop viewer
- VR viewer
- uHOME-compatible game-console UX

Client surface differences must stay in adapters; shared world contract remains engine-agnostic.

## Packaging Blueprint

Target file model (initial):
- `/extensions/3dworld/manifest.json`
- `/extensions/3dworld/container.json`
- `/extensions/3dworld/store.py` (or equivalent registry hook)
- `/extensions/3dworld/services/` (renderer and adapter boundaries)
- `/extensions/3dworld/contracts/` (mapping schema and compatibility guards)

Container policy should default to least privilege and explicit runtime dependencies.

## Delivery Phasing

1. Contract-first scaffold
- define canonical gameplay->3D mapping schema
- add extension manifest/container metadata
- add no-op adapter proving load/enable path

2. Minimal world lens
- render grid/anchor placement from real gameplay state
- apply SKIN theming and LENS camera behavior
- keep z-axis as deterministic vertical hints

3. Advanced surfaces
- VR and uHOME controller adaptations
- chunk streaming and richer scene composition
- networking hooks for shared/multi-device world state where required

## Acceptance Signals

- Core gameplay runs without 3DWORLD installed.
- Enabling 3DWORLD does not fork canonical gameplay state.
- LENS/SKIN and GRID/Z mappings are deterministic and testable.
- 3DWORLD can be installed/updated as an extension package independent of core release cadence.

## Non-Goals (v1.5 lane)

- Replacing core gameplay model with engine-specific state
- Shipping photoreal/high-cost rendering as a baseline requirement
- Making VR mandatory for world interaction
