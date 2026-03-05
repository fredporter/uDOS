# Demo 02: Workflow and Task Planning

## Goal

Create and run a canonical workflow through the shipped `WORKFLOW` surface, then inspect status and deliverable artifacts.

## Target Profiles

- `core`
- `creator`
- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_02_workflow_and_task_planning.py
ucode WORKFLOW LIST TEMPLATES
ucode WORKFLOW NEW WRITING-article release-pack-001 goal="Write v1.5 release note" audience=operators tone=plain word_limit=600
ucode WORKFLOW RUN release-pack-001
ucode WORKFLOW STATUS release-pack-001
ucode WORKFLOW APPROVE release-pack-001
ucode WORKFLOW STATUS release-pack-001
ucode UCODE DELIVERABLE VALIDATE WORKFLOW @memory/vault/workflows/release-pack-001/workflow.json
```

## Expected Output

- workflow template list includes `WRITING-article`
- workflow creation writes a runtime-owned workflow directory
- `WORKFLOW RUN` advances the first phase and may pause in approval state
- `WORKFLOW STATUS` reports current phase, state, and next action
- deliverable validation confirms the workflow spec remains on the canonical contract

## Expected Artifacts

- `.artifacts/release-demos/demo-02-workflow-and-task-planning.json`
- `memory/vault/workflows/release-pack-001/workflow.json`
- `memory/vault/workflows/release-pack-001/state.json`
- at least one phase artifact such as `01-outline.md`

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_02_workflow_and_task_planning.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_scripts_test.py \
  core/tests/workflow_scheduler_test.py \
  core/tests/ulogic_deliverables_test.py \
  wizard/tests/workflow_routes_test.py
```
