# Next Dev Round Prep (2026-02-17)

Status: deployed to active execution via `docs/releases/2026-02-17-next-dev-round-execution.md`.

Scope aligned to the canonical roadmap (`docs/roadmap.md`) after TUI/grid/spec updates.

## Round Objective

Ship stable uCLI interactive rendering with panel parity across task/schedule/workflow and map-layer readiness.

## Priority Tracks

1. TUI parity and advanced I/O hardening (P0)
2. GRID runtime typed panel parity (task/schedule/workflow)
3. uCLI map layer rendering extension
4. v1.4.0 platform/containerization open items

## Execution Checklist

- [ ] Lock single-writer stdout behavior in interactive flows (`HELP`, menus, setup/story forms, status lines).
- [ ] Remove/disable remaining full-screen menu paths from default command flows (inline-first behavior).
- [ ] Add/expand regression tests for output interleaving (startup + HELP + command output).
- [ ] Add `GRID workflow` command docs/examples and sample input payloads under `memory/system/`.
- [ ] Add parity fixtures for task/schedule/workflow outputs in canonical `80x30`.
- [ ] Start uCLI map-layer extension implementation:
  - [ ] layer stack (`terrain`, `objects/sprites`, `overlays`, `workflow markers`)
  - [ ] z-range controls and legend parity
  - [ ] unified schema for `MAP`, `GRID MAP`, `PLAY MAP`
- [ ] Wire markdown export parity for map/task/schedule/workflow diagrams.
- [ ] Close remaining v1.4.0 open items in roadmap (library manager + modularization residue checks if still open).

## Validation Gates

- [ ] TS build passes (`npm --prefix core run build`)
- [ ] Grid runtime tests pass (including panel parity)
- [ ] Python command compile checks pass for updated handlers/tests
- [ ] No new compatibility shims introduced
- [ ] Roadmap checkboxes and release note delta updated at end of round

## Compost / Hygiene Baseline

- Archived stale artifacts to:
  - `/.compost/2026-02-17/archive/20260217-200316/workspace/`
- Archived files:
  - `core/config/ok_modes.invalid-1771318500.json`
  - `wiki/ARCHITECTURE.md.bak`
  - `wiki/README.md.bak`
  - `wiki/STYLE-GUIDE.md.bak`
