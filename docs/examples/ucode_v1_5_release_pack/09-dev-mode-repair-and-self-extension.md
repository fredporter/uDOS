# Demo 09: Dev Mode Repair and Self-Extension

## Goal

Prove v1.5 can repair and extend itself from Dev Mode using runtime-owned tools and cloud-code-agent lane planning under Wizard policy.

## Target Profiles

- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_09_dev_mode_repair_and_self_extension.py
ucode DEV PLAN
ucode REPAIR --dry-run
ucode REPAIR --config
ucode DEV EXTENSION SCAFFOLD demo.teletext.pack
ucode DEV EXTENSION ENABLE demo.teletext.pack
ucode DEV CLOUD PLAN --policy-gated
```

## Expected Output

- Dev Mode planning summary reports healthy contributor/runtime handoff
- repair sequence emits check, plan, and action records
- extension scaffold and activation records are attached to runtime report
- cloud-code-agent lane remains explicit, policy-gated, and non-default

## Expected Artifacts

- `.artifacts/release-demos/demo-09-dev-mode-repair-and-self-extension.json`

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_09_dev_mode_repair_and_self_extension.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_pack_test.py \
  core/tests/ucode_release_demo_scripts_test.py
```
