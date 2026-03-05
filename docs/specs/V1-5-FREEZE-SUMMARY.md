# v1.5 Freeze Summary

Updated: 2026-03-04
Status: Stable

This summary is the final v1.5 freeze evidence set for the stable release cut.

## Certified Demo Pack

Canonical pack:

- `docs/examples/ucode_v1_5_release_pack/00-setup-and-status.md`
- `docs/examples/ucode_v1_5_release_pack/01-local-assist-and-knowledge.md`
- `docs/examples/ucode_v1_5_release_pack/02-workflow-and-task-planning.md`
- `docs/examples/ucode_v1_5_release_pack/03-managed-scheduler-and-budget.md`
- `docs/examples/ucode_v1_5_release_pack/04-self-hosted-dev-mode.md`

Runnable entrypoints:

- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_00_setup_and_status.py`
- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_01_local_assist_and_knowledge.py`
- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_02_workflow_and_task_planning.py`
- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_03_managed_scheduler_and_budget.py`
- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_04_self_hosted_dev_mode.py`

Certification source:

- `docs/examples/ucode_v1_5_release_pack/CERTIFICATION.md`
- `docs/examples/ucode_v1_5_release_pack/certification.json`

## Certified Profiles

Certified profile matrix and persisted state:

- `core`
- `home`
- `creator`
- `gaming`
- `dev`

Evidence source:

- `docs/specs/V1-5-STABLE-SIGNOFF.md`
- `docs/specs/V1-5-STABLE-SIGNOFF.json`
- `memory/ucode/release-profiles.json`

## Runtime Baselines

Local assist baseline:

- GPT4All is the designated local OK Model runtime.
- Wizard remains the only network escalation lane.
- Workspace-aware context bundle, conversation carry-over, install-state evidence, and provider-health surfaces are active.

Managed operations baseline:

- quota-aware provider planning
- scheduler budget gating
- provider-preserving queued execution
- mounted-route proof that `/api/ucode/logic/status`, `/api/ops/planning/jobs`, and `/api/ops/config/status` report the same managed contract

Self-hosted contributor baseline:

- Dev Mode and `DEV` commands operate tracked `@dev` planning, workflow sync, scheduler registration, runtime task updates, and workflow execution through canonical runtime-owned services

## Additional Backlog Closure Evidence

Offline runtime promotion:

- `core/ulogic/action_graph.py`
- `core/ulogic/runtime.py`
- `core/ulogic/state_store.py`
- `core/ulogic/artifact_store.py`
- `core/ulogic/script_sandbox.py`
- `core/tests/ulogic_runtime_test.py`

Sonic seeded-catalog contributor review flow:

- `core/services/sonic_device_service.py`
- `core/commands/sonic_handler.py`
- `wizard/routes/sonic_plugin_routes.py`
- `core/tests/sonic_device_service_test.py`
- `core/tests/test_sonic_handler.py`
- `wizard/tests/sonic_submission_routes_test.py`

Wizard-owned home-lane bridge closure:

- `wizard/services/uhome_presentation_service.py`
- `wizard/services/uhome_command_handlers.py`
- `wizard/routes/home_assistant_routes.py`
- `wizard/routes/platform_routes.py`
- `wizard/tests/home_assistant_routes_test.py`
- `wizard/tests/uhome_presentation_service_test.py`

## Canonical Validation

Shared runtime command:

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ulogic_runtime_test.py \
  core/tests/sonic_device_service_test.py \
  core/tests/test_sonic_handler.py \
  wizard/tests/sonic_submission_routes_test.py \
  wizard/tests/sonic_plugin_alias_routes_test.py \
  core/tests/ucode_release_demo_pack_test.py \
  core/tests/ucode_release_demo_scripts_test.py \
  core/tests/v1_5_stable_signoff_test.py
```

## Release Decision Boundary

The v1.5 repo backlog is closed and the release metadata is now cut to `stable`.
