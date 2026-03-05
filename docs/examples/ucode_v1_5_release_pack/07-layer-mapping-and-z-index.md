# Demo 07: Layer Mapping and Z-Index

## Goal

Validate v1.5 layer-map behavior: spatial z-index semantics, map-level bucket selection, and message-theme mapping remain coherent across dungeon/foundation/galaxy lanes.

## Target Profiles

- `core`
- `creator`
- `gaming`
- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_07_layer_mapping_and_z_index.py
ucode MAP LEVEL SHOW
ucode MAP ZINDEX CHECK
ucode THEME MAP SHOW
ucode VIEW GRID --layer-demo
```

## Expected Output

- z-index policy table is emitted with deterministic bucket mapping
- negative/subterranean z values map to `dungeon` lane
- baseline surface z values map to `foundation` lane
- orbital/high-band z values map to `galaxy` lane
- theme mapping table remains separate from spatial renderer state

## Expected Artifacts

- `.artifacts/release-demos/demo-07-layer-mapping-and-z-index.json`

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_07_layer_mapping_and_z_index.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_pack_test.py \
  core/tests/ucode_release_demo_scripts_test.py
```
