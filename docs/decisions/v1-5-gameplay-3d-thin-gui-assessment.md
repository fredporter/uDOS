# v1.5 Gameplay, 3D, and Thin GUI Assessment

Status: pre-release assessment  
Updated: 2026-03-05

## Scope

This assessment covers current v1.5 state for:

- gameplay command/runtime surfaces (`PLAY`, `RULE`, lens/profile progression)
- 3D world direction and implementation status
- z-index/z-layer and lens mapping surfaces
- Thin GUI runtime readiness for production use

## Evidence Reviewed

- Gameplay commands/services:
  - `core/commands/play_handler.py`
  - `core/commands/gameplay_handler.py`
  - `core/services/gameplay_service.py`
  - `core/services/lens_service.py`
  - `core/services/world_lens_service.py`
- 3D and gameplay docs/specs:
  - `docs/features/3D-WORLD.md`
  - `docs/specs/3DWORLD-EXTENSION-SPEC-v1.5.0.md`
  - `docs/specs/TOYBOX-GAMEPLAY-SCAFFOLD-v1.3.md`
  - `docs/specs/GAMEPLAY-LENS-ARCHITECTURE-v1.4.4.md`
  - `docs/specs/GAMEPLAY-LENS-SKIN-PROGRESSION-v1.4.8.md`
  - `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md`
- Thin GUI:
  - `extensions/thin-gui/*`
  - `wizard/services/thin_gui_contract.py`
  - `wizard/services/launch_orchestrator.py`
  - `wizard/services/uhome_presentation_service.py`
  - `wizard/routes/platform_routes.py`
  - `wizard/dashboard/src/routes/ThinGui.svelte`

## Current State

### Gameplay + lens core

State: implemented and test-covered.

- `PLAY` is unified through `PlayHandler`, delegating gameplay subcommands to `GameplayHandler`.
- progression state, gates, play options, lens score/checkpoints, and token unlock rules are persisted in `gameplay_state.json` and exercised by tests.
- world-lens readiness is feature-flagged and bounded to a single-region contract via `WorldLensService`.

Validation snapshot:

- `core/tests/gameplay_service_test.py` passed
- `core/tests/v1_4_4_lens_gameplay_test.py` passed

### 3D world lane

State: deferred for v1.5 mainline, scaffold-only.

- docs explicitly mark 3D world as planned/draft/deferred.
- no `extensions/3dworld/` package currently exists.
- current 3D-related runtime is limited to `crawler3d` lens/profile scaffolding and adapter hooks.

### z-index/z-layer and lens mapping

State: partially consolidated.

- core supports gameplay `z` in location/progression structures and world-lens slice checks.
- docs and examples cover both spatial z semantics and theme/lens mapping.
- terminology is split across "z-layer", "z-index", and "map-level/lens" docs, which is functional but fragmented.

### Thin GUI

State: functional contract layer, not production-complete kiosk runtime.

Implemented:

- launch-intent/session contract is in place (`thin_gui_contract.py`).
- launch session list/get/stream routes exist.
- extension package `extensions/thin-gui` builds and type-checks.
- dashboard has a Thin GUI route and popup helper.

Not yet production-complete:

- current dashboard Thin GUI route is an iframe wrapper, not a hardened kiosk shell.
- no full evidence in this lane of compositor/session hardening (Wayland/Cage/Chromium orchestration) in the same contract path.
- no single production readiness checklist/signoff document tied to Thin GUI route behavior, recovery behavior, and security posture.

Validation snapshot:

- `wizard/tests/launch_orchestrator_test.py` passed
- `wizard/tests/uhome_presentation_service_test.py` passed
- `extensions/thin-gui` TypeScript lint/build check passed (`tsc --noEmit`)

## Overlap and Drift

### Documentation overlap

There is material overlap across:

- gameplay scaffold (`TOYBOX-GAMEPLAY-SCAFFOLD-v1.3`)
- lens architecture (`GAMEPLAY-LENS-ARCHITECTURE-v1.4.4`)
- lens+skin progression contract (`GAMEPLAY-LENS-SKIN-PROGRESSION-v1.4.8`)
- 3D planning/spec docs (`3D-WORLD`, `3DWORLD-EXTENSION-SPEC-v1.5.0`)

This causes repeated command examples and mixed maturity levels (implemented, partial, deferred) in adjacent docs.

### Command-surface overlap

`PLAY` semantics are split between:

- progression/runtime command concerns (`GameplayHandler`)
- play-option orchestration concerns (`PlayHandler`)

This is intentional in code but not consistently represented as one canonical command contract document.

## Consolidation Decision (Recommended)

Yes: combine into a clear **Core + 3D Extension** model.

### Core ownership (keep in core)

- canonical gameplay state (`xp/hp/gold/level/achievements/metrics`)
- gates, unlock tokens, progression contract
- TOYBOX profile state and permission gating
- lens policy/readiness contract and map/z semantics
- command contract for `PLAY`, `RULE`, `SKIN`, `MODE`

### 3D extension ownership (move/contain in extension)

- 3D scene rendering pipeline
- 3D camera/presentation adapters
- heavy asset/runtime dependencies
- optional VR/uHOME visual adapter surfaces
- non-authoritative render caches and perf telemetry

### Boundary rule

3D extension consumes normalized core snapshots/events and returns interaction events. It must not own canonical gameplay persistence.

## Release Readiness Verdict

### Gameplay/lens stack

Verdict: release-ready for v1.5 baseline (current scope).

### 3D world

Verdict: not baseline-ready as an extension package for v1.5 stable (still deferred/scaffold).

### Thin GUI

Verdict: pre-production.

- ready as a shared launch/session contract and dashboard integration layer
- not yet evidenced as a hardened, end-to-end production kiosk runtime in this repo's current signoff surfaces

## Pre-release Actions

1. Publish one canonical gameplay command contract page that supersedes duplicated command examples in older gameplay/lens specs.
2. Keep 3D lane explicitly optional/deferred in release signoff until `extensions/3dworld/` exists with manifest/container/contracts/tests.
3. Add Thin GUI production checklist/signoff evidence (security, recovery, kiosk lifecycle, offline behavior, session continuity).
4. Normalize terminology in docs: use one canonical definition set for `z`, `z-layer` (spatial), `z-index` (renderer ordering), and `lens` (gameplay/presentation semantics).
