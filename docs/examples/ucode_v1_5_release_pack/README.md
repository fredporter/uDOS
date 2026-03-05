# ucode v1.5 Release Pack

This pack is the canonical demo set for the v1.5 stable release.

Each demo includes:

- a checked-in command transcript or script
- target release profiles
- expected runtime output or artifacts
- a validation reference

Certification status:

- [v1.5 Demo Certification](CERTIFICATION.md)
- [machine-readable certification](certification.json)

## Demo Set

1. [00-setup-and-status](00-setup-and-status.md)
2. [01-local-assist-and-knowledge](01-local-assist-and-knowledge.md)
3. [02-workflow-and-task-planning](02-workflow-and-task-planning.md)
4. [03-managed-scheduler-and-budget](03-managed-scheduler-and-budget.md)
5. [04-self-hosted-dev-mode](04-self-hosted-dev-mode.md)

## Profile Matrix

| Demo | Target profiles |
| --- | --- |
| `00-setup-and-status` | `core`, `home`, `creator`, `gaming`, `dev` |
| `01-local-assist-and-knowledge` | `core`, `home`, `dev` |
| `02-workflow-and-task-planning` | `core`, `creator`, `dev` |
| `03-managed-scheduler-and-budget` | `home`, `creator`, `dev` |
| `04-self-hosted-dev-mode` | `dev` |

## Pack Validation

Structural validation:

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ucode_release_demo_pack_test.py
```

Runnable demo scripts:

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_00_setup_and_status.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_01_local_assist_and_knowledge.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_02_workflow_and_task_planning.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_03_managed_scheduler_and_budget.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_04_self_hosted_dev_mode.py
```

Focused managed-operations validation:

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  wizard/tests/managed_operations_runtime_contract_test.py \
  wizard/tests/ucode_ok_routes_test.py \
  wizard/tests/ops_routes_test.py \
  wizard/tests/cloud_provider_executor_test.py \
  wizard/tests/task_scheduler_windows_test.py \
  wizard/tests/maintenance_job_test.py
```
