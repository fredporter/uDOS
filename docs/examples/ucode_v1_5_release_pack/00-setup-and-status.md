# Demo 00: Setup and Status

## Goal

Show that a v1.5 profile is installed, the runtime is healthy, and the operator-visible status surfaces agree on local assist, workflow, and managed-operations readiness.

## Target Profiles

- `core`
- `home`
- `creator`
- `gaming`
- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_00_setup_and_status.py
ucode UCODE PROFILE LIST
ucode UCODE PROFILE SHOW core
ucode UCODE OPERATOR STATUS
ucode WORKFLOW LIST TEMPLATES
curl -s http://127.0.0.1:8000/api/ucode/logic/status
curl -s http://127.0.0.1:8000/api/ops/config/status
curl -s http://127.0.0.1:8000/api/ops/planning/jobs
```

## Expected Output

- profile list includes the target release profile
- operator status reports a ready local runtime or a clear local issue
- workflow templates are listed from the canonical workflow runtime
- `logic/status` returns local runtime metadata plus network readiness
- `ops/config/status` returns `managed_operations`
- `ops/planning/jobs` returns scheduler settings, queue state, and managed-operations runtime data

## Expected Artifacts

- `.artifacts/release-demos/demo-00-setup-and-status.json`

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_00_setup_and_status.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_pack_test.py \
  core/tests/ucode_release_demo_scripts_test.py
```
