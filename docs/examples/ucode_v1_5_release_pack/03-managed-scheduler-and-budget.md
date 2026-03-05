# Demo 03: Managed Scheduler and Budget

## Goal

Show queued work, provider failover readiness, budget gating, defer/retry behavior, and the shared managed-operations contract across prompt-driven and scheduled paths.

## Target Profiles

- `home`
- `creator`
- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_03_managed_scheduler_and_budget.py
curl -s http://127.0.0.1:8000/api/ucode/logic/status
curl -s http://127.0.0.1:8000/api/ops/config/status
curl -s http://127.0.0.1:8000/api/ops/planning/jobs
curl -s -X POST http://127.0.0.1:8000/api/ops/planning/jobs \
  -H 'Content-Type: application/json' \
  -d '{"name":"Quota gated release task","schedule":"daily","provider":"openai","requires_network":true,"resource_cost":1,"budget_units":1}'
curl -s http://127.0.0.1:8000/api/ops/planning/overview
curl -s http://127.0.0.1:8000/api/ops/planning/deferred/preview?reason=api_budget_exhausted
curl -s -X POST http://127.0.0.1:8000/api/ops/planning/deferred/retry?reason=network_unavailable\&limit=5
```

## Expected Output

- `logic/status` and ops status surfaces report the same provider readiness and blocked-by-quota state
- ops runtime reports `managed_operations`, `scheduler_budget`, and defer reasons
- queued work can move into a deferred state with `api_budget_exhausted` or `network_unavailable`
- retry surfaces clear defer metadata only for the selected retry path

## Expected Artifacts

- `.artifacts/release-demos/demo-03-managed-scheduler-and-budget.json`
- queue and task-run rows reflecting pending, deferred, retried, or completed work

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_03_managed_scheduler_and_budget.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_scripts_test.py \
  wizard/tests/managed_operations_runtime_contract_test.py \
  wizard/tests/cloud_provider_executor_test.py \
  wizard/tests/task_scheduler_windows_test.py \
  wizard/tests/maintenance_job_test.py \
  wizard/tests/ops_routes_test.py \
  wizard/tests/ucode_ok_routes_test.py
```
