# Demo 06: Ghost to Wizard Onboarding Mission

## Goal

Certify that v1.5 onboarding is gameplay-first while performing real setup tasks and role progression from Ghost to Wizard.

## Target Profiles

- `core`
- `home`
- `creator`
- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_06_ghost_to_wizard_onboarding.py
ucode ONBOARD START ghost-to-wizard
ucode ONBOARD STATUS
ucode ONBOARD RUN level awakening_chamber
ucode ONBOARD RUN level command_vault
ucode ONBOARD RUN level tui_hall
ucode ONBOARD RUN level workflow_engine
ucode ONBOARD RUN level extension_forge
ucode ONBOARD RUN level research_tower
ucode ONBOARD RUN level surface
```

## Expected Output

- onboarding script source is present and parseable
- level sequence is complete and role promotions are ordered
- setup checkpoints align to actual runtime setup commands
- mission emits structured block events for narration/objective/progress/reward/unlock
- final state is `wizard` with persisted progression record

## Expected Artifacts

- `.artifacts/release-demos/demo-06-ghost-to-wizard-onboarding.json`

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_06_ghost_to_wizard_onboarding.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_pack_test.py \
  core/tests/ucode_release_demo_scripts_test.py
```
