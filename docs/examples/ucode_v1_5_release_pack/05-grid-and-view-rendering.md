# Demo 05: Grid and View Rendering Matrix

## Goal

Prove v1.5 TUI rendering parity across text, columns, ASCII, teletext, calendar, task, and block/grid/container views with deterministic fixed-width behavior.

## Target Profiles

- `core`
- `creator`
- `gaming`
- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_05_grid_and_view_rendering.py
ucode VIEW TEXT --demo
ucode VIEW COLUMNS --demo
ucode VIEW ASCII --demo
ucode VIEW TELETEXT --demo
ucode VIEW CALENDAR --demo
ucode VIEW TASK --demo
ucode VIEW GRID --demo
ucode VIEW CONTAINER --demo
```

## Expected Output

- renderer reports all required view kinds as available
- text and column layouts remain fixed-width and aligned
- ASCII and teletext view payloads include fallback-safe frame contracts
- calendar/task/grid/container contracts include stable panel metadata
- rendering matrix includes at least one canonical event sample per view kind

## Expected Artifacts

- `.artifacts/release-demos/demo-05-grid-and-view-rendering.json`

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_05_grid_and_view_rendering.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_pack_test.py \
  core/tests/ucode_release_demo_scripts_test.py
```
