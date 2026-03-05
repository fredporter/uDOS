# 3DWORLD Extension Contract v1.5

Status: canonical extension contract  
Updated: 2026-03-05

## Purpose

Define the v1.5 3D world integration as an extension-owned lane with dedicated runtime/server semantics.

## Boundary

Core owns:

- canonical gameplay/progression state
- lens and skin semantics
- map identity and z/elevation semantics

3DWORLD extension owns:

- 3D render pipeline
- advanced GUI surfaces
- optional dedicated gameplay/toybox node runtime
- extension-local scene caching and adapter services

No canonical gameplay persistence may move into the extension.

## Packaging

3DWORLD extension path:

- `extensions/3dworld/`

Required scaffold:

- `extension.json`
- extension contracts under `extensions/3dworld/contracts/`
- dedicated runtime/server entrypoint (separate from core TUI loop)

## Integration Contract

Input from core:

- normalized gameplay snapshot
- active lens/skin
- spatial location (`x`, `y`, `z`) and anchors
- policy/gating context

Output to core:

- interaction events
- objective/telemetry updates
- optional render/session diagnostics

## Lens + Skin Integration

3DWORLD must use the same lens/skin vocabulary contract as core gameplay surfaces.

For crawler 3D demo lane:

- gameplay profile: `crawler3d`
- lens id: `crawler3d`
- recommended skins from `core/config/lens_skin_game_catalog_v1_5.json`
- skin insertion path remains `SKIN SCAFFOLD` + `SKIN INSERT`

## Runtime Model

This lane is advanced GUI and must remain separate:

- separate extension process/service
- optional separate toybox node deployment
- explicit degradation when extension is unavailable

Core gameplay must continue when 3DWORLD is disabled/unavailable.

## Related

- `docs/specs/GAMEPLAY-COMMAND-CONTRACT-v1.5.md`
- `docs/features/3D-WORLD.md`
- `extensions/3dworld/`
