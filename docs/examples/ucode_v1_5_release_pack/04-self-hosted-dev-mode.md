# Demo 04: Self-Hosted Dev Mode

## Goal

Operate uDOS from the `@dev` lane using canonical planning, workflow sync, scheduler registration, and task-state updates rather than ad hoc contributor flows.

## Target Profiles

- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_04_self_hosted_dev_mode.py
ucode DEV PLAN
ucode DEV SYNC release-program.json
ucode DEV SCHEDULE release-demo.json release-program.json
ucode DEV RUN release-program.json
ucode DEV TASK release-program.json phase-1 completed
ucode WORKFLOW LIST
ucode WORKFLOW STATUS <runtime-workflow-id>
```

The same sequence may be executed from the Dev Mode GUI through the tracked `@dev` handoff panel.

## Expected Output

- `DEV PLAN` reports tracked contributor state and runtime handoff options
- `DEV SYNC` promotes a tracked workflow plan into a runtime-managed project
- `DEV SCHEDULE` registers a tracked scheduler template against that runtime project
- `DEV RUN` starts the synced runtime workflow
- `DEV TASK` updates task state through the canonical runtime path

## Expected Artifacts

- `.artifacts/release-demos/demo-04-self-hosted-dev-mode.json`
- runtime workflow project state linked to the tracked `dev/ops/workflows/` source
- scheduler task rows linked to the synced workflow project
- updated contributor/runtime handoff records in Dev Mode status output

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_04_self_hosted_dev_mode.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_scripts_test.py \
  core/tests/dev_mode_handler_test.py \
  dev/goblin/tests/test_dev_ops_routes.py
```
