# Demo 08: Seed Library Generation

## Goal

Verify v1.5 seed library generation/indexing for diagrams, themes, and templates used by TUI rendering and workflow onboarding.

## Target Profiles

- `core`
- `creator`
- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_08_seed_library_generation.py
ucode SEED LIST --bank graphics
ucode SEED INDEX --bank graphics
ucode SEED INDEX --bank templates
ucode STATUS --seed-health
```

## Expected Output

- seed-bank roots are discovered from canonical repo paths
- diagram/theme/template seed counts are reported
- deterministic index payload is generated for release audit
- seed categories include teletext/ascii/block/flow and starter templates

## Expected Artifacts

- `.artifacts/release-demos/demo-08-seed-library-generation.json`

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_08_seed_library_generation.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_pack_test.py \
  core/tests/ucode_release_demo_scripts_test.py
```
