# Core Runtime Status (2026-01-24)

This is a snapshot of Core command coverage and runtime integration.

## Python Command Set (Dispatcher)

Commands routed by `core/tui/dispatcher.py`:

- Navigation: MAP, PANEL, GOTO, FIND
- Information: TELL, HELP
- Game State: BAG, GRAB, SPAWN, SAVE, LOAD
- System: SHAKEDOWN, REPAIR, PATTERN, DEV MODE
- NPC & Dialogue: NPC, TALK, REPLY
- Wizard Management: CONFIG, PROVIDER
- Binder: BINDER
- Runtime: RUN
- Data: DATASET

## TS Runtime State

- Node runner: `core/runtime/ts_runner.js`
- Core service: `core/services/ts_runtime_service.py`
- TUI entry: `RUN <file> [section_id]` and `RUN PARSE <file>`
- Execution requires a compiled TS runtime at `core/grid-runtime/dist/index.js`
- Build helper: `core/tools/build_ts_runtime.sh`

## Binder + Datasets

- Binder compile/chapters in Core (SQLite-backed)
- Dataset manager and regen tools (80x30 grid)
- Unified locations dataset built via `python -m core.tools.dataset_builder`

## TUI Output Toolkit

- OutputToolkit used across handlers for ASCII banners/tables/checklists
- Renderer supports output for success/warning/error

## Gaps / Next Improvements

- Expand TS runtime coverage and tests in Core
- Harden map/grid rendering and performance
- Complete file parsing integrations (CSV/JSON/YAML/SQL)
- Replace any remaining ad-hoc output with OutputToolkit where needed
- Add tests for dataset validation and binder compile paths
