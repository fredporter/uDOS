# v1.5 Demo Certification

Updated: 2026-03-04
Status: Certified

This document records the release-demo certification pass for the canonical
v1.5 `ucode` pack.

## Runtime Contract Used

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python
```

The direct `python3` entrypoint is not the release contract for this pack. The
certification pass was executed on the shared `uv` + `/.venv` runtime required
by v1.5.

## Certified Demo Set

| Demo | Profiles | Script | Artifact | Result |
| --- | --- | --- | --- | --- |
| `00-setup-and-status` | `core`, `home`, `creator`, `gaming`, `dev` | `scripts/run_demo_00_setup_and_status.py` | `.artifacts/release-demos/demo-00-setup-and-status.json` | Certified |
| `01-local-assist-and-knowledge` | `core`, `home`, `dev` | `scripts/run_demo_01_local_assist_and_knowledge.py` | `.artifacts/release-demos/demo-01-local-assist-and-knowledge.json` | Certified |
| `02-workflow-and-task-planning` | `core`, `creator`, `dev` | `scripts/run_demo_02_workflow_and_task_planning.py` | `.artifacts/release-demos/demo-02-workflow-and-task-planning.json` | Certified |
| `03-managed-scheduler-and-budget` | `home`, `creator`, `dev` | `scripts/run_demo_03_managed_scheduler_and_budget.py` | `.artifacts/release-demos/demo-03-managed-scheduler-and-budget.json` | Certified |
| `04-self-hosted-dev-mode` | `dev` | `scripts/run_demo_04_self_hosted_dev_mode.py` | `.artifacts/release-demos/demo-04-self-hosted-dev-mode.json` | Certified |

## Release Findings

- demo `00` confirmed local runtime readiness and matching managed-operations payloads across operator-visible status surfaces
- demo `01` confirmed local assist remained the first lane, persisted conversation state, and carried active governance context into the prompt contract
- demo `02` confirmed the canonical workflow runtime produced approval-gated progress and runtime-owned artifacts
- demo `03` confirmed budget-gated defer behavior and prompt/scheduler parity on the quota-blocked provider contract
- demo `04` confirmed the self-hosted `@dev` lane can plan, sync, schedule, run, and update task state through runtime-owned surfaces

## Profile Coverage

Verified healthy through the current release-profile registry:

- `core`
- `home`
- `creator`
- `gaming`
- `dev`

Current install-state truth from `memory/ucode/release-profiles.json`:

- installed and enabled: `core`, `home`, `creator`, `gaming`, `dev`

Final profile signoff is now tracked in
`docs/specs/V1-5-STABLE-SIGNOFF.md`.

## Validation Commands

Demo execution:

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_00_setup_and_status.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_01_local_assist_and_knowledge.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_02_workflow_and_task_planning.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_03_managed_scheduler_and_budget.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_04_self_hosted_dev_mode.py
```

Focused regression coverage:

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_pack_test.py \
  core/tests/ucode_release_demo_scripts_test.py \
  core/tests/dev_mode_handler_test.py \
  wizard/tests/managed_operations_runtime_contract_test.py \
  wizard/tests/logic_assist_service_test.py \
  wizard/tests/provider_health_routes_test.py \
  wizard/tests/self_heal_routes_recovery_test.py \
  wizard/tests/ucode_ok_mode_utils_test.py \
  wizard/tests/ucode_ok_routes_test.py \
  wizard/tests/cloud_provider_executor_test.py \
  wizard/tests/task_scheduler_windows_test.py \
  wizard/tests/maintenance_job_test.py \
  wizard/tests/ops_routes_test.py \
  wizard/tests/workflow_routes_test.py \
  dev/goblin/tests/test_dev_ops_routes.py
```

Profile verification:

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python - <<'PY'
from pathlib import Path
from core.services.release_profile_service import ReleaseProfileService

service = ReleaseProfileService(Path.cwd())
for profile in service.list_profiles():
    print(profile["profile_id"], service.verify_profile(profile["profile_id"])["healthy"])
PY
```

## Final Lane Entry

The demo pack remains the certified runtime proof set for v1.5. The freeze
summary is published and the release metadata is now cut to `stable`.
