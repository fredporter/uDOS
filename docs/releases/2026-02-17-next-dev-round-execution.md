# Next Dev Round Execution (2026-02-17)

Round status: active (deployed)

This document promotes the prep artifact into an execution contract for the active round:
- Prep source: `docs/releases/2026-02-17-next-dev-round-prep.md`
- Canonical roadmap: `docs/roadmap.md`

## Round Objective

Ship stable uCLI interactive rendering with panel parity across task/schedule/workflow and map-layer readiness.

## Deployment Actions (Completed)

- [x] Round activated from prep to execution.
- [x] Roadmap now points to this execution artifact for active tracking.
- [x] Execution gate checklist captured below for this round.

## Active Execution Checklist

- [x] Lock single-writer stdout behavior in interactive flows (`HELP`, menus, setup/story forms, status lines).
- [x] Remove/disable remaining full-screen menu paths from default command flows (inline-first behavior).
- [x] Add explicit prompt lifecycle contract (`input`/`render`/`background`) in the uCLI REPL loop and spinner paths.
- [x] Add/expand regression tests for output interleaving (startup + HELP + command output).
- [x] Add `GRID workflow` command docs/examples and sample input payloads under `memory/system/`.
- [x] Add parity fixtures for task/schedule/workflow outputs in canonical `80x30`.
- [x] Start uCLI map-layer extension implementation:
  - [x] layer stack (`terrain`, `objects/sprites`, `overlays`, `workflow markers`)
  - [x] z-range controls and legend parity
  - [ ] unified schema for `MAP`, `GRID MAP`, `PLAY MAP` (schema types done; command routing unification is next)
- [ ] Wire markdown export parity for map/task/schedule/workflow diagrams.
- [ ] Close remaining v1.4.0 open items in roadmap (library manager + modularization residue checks if still open).

## Validation Gates

- [x] TS build passes (`npm --prefix core run build`) — 17/17 TS tests pass
- [x] Grid runtime tests pass (including panel parity) — 7/7 Python parity tests pass
- [ ] Python command compile checks pass for updated handlers/tests
- [x] No new compatibility shims introduced
- [ ] Roadmap checkboxes and release note delta updated at end of round
