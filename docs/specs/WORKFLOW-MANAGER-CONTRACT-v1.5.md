# Workflow Manager Contract v1.5

Status: Active
Last updated: 2026-03-03

## Purpose

This spec defines the canonical v1.5 workflow manager contract across core,
Wizard, and offline logic surfaces.

It standardizes one workflow/task orchestration boundary for:
- workflow definitions
- run state
- approvals
- escalation
- task linkage
- artifact tracking
- operator-readable evidence

## Scope

### In scope

- Markdown workflow templates
- file-backed workflow state
- task and completion linkage
- workflow approval and escalation semantics
- workflow artifact layout
- handoff from the logic input handler
- Wizard orchestration built on the same core contract

### Out of scope

- component-specific parallel workflow engines
- GUI-only workflow semantics
- provider-specific runtime truth
- hidden execution state that bypasses file-backed artifacts

## Product Rule

There is one active v1.5 workflow model.

- core owns canonical workflow parsing, run state, and artifact semantics
- Wizard may schedule, visualize, or expose that model
- the logic input handler may launch or advance workflows through that model
- the standard `ucode` TUI must present that model through the refactored shell

No active surface may define a conflicting workflow lifecycle for v1.5.

## Canonical Runtime Shape

The workflow manager contract must unify:
- workflow markdown templates
- workflow artifact folders
- `tasks.json`
- `completed.json`
- project and role policy inputs where required

Minimum runtime surfaces:
- workflow specification
- workflow state
- phase state
- approval markers
- escalation markers
- artifact references
- task linkage

## Workflow Handoff Contract

The standard handoff path is:

```text
logic input handler
-> workflow intent frame
-> workflow manager action
-> workflow state transition
-> artifact + task/completion updates
-> structured TUI/Wizard output
```

Required workflow actions:
- `workflow.new`
- `workflow.run`
- `workflow.resume`
- `workflow.status`
- `workflow.approve`
- `workflow.escalate`
- `workflow.list`

## Canonical State Rules

The workflow manager must keep these semantics stable across core and Wizard:

### Workflow status

- `ready`
- `awaiting_approval`
- `waiting`
- `completed`
- `failed`

### Phase status

- `pending`
- `ready`
- `running`
- `pending_approval`
- `completed`
- `failed`

### Approval

Approval means:
- a declared gate was reached
- evidence exists for the completed phase
- the next phase is blocked until an explicit approval action occurs

### Escalation

Escalation means:
- the current path cannot proceed within the current tier, policy, or constraints
- the state transition is recorded explicitly
- the operator can inspect the reason and next allowed path

## Artifact Contract

Every workflow run must remain operator-readable and file-backed.

Expected run folder shape:

```text
memory/vault/workflows/<workflow-id>/
  workflow.md
  workflow.json
  state.json
  meta/<phase>.json
  outputs/
```

The workflow manager must also keep task/completion linkage coherent with:
- `tasks.json`
- `completed.json`

## Cross-Component Compatibility Rule

Workflow artifacts, templates, and state must align with the shared v1.5
Markdown runbook/template structure so:
- core runtime flows
- Wizard control-plane flows
- Sonic operations
- `uHOME` operations
- offline logic packs

all share one recognizable operational shape.

## Integration Anchors

Current repository anchors for this spec:
- `core/workflows/contracts.py`
- `core/workflows/parser.py`
- `core/workflows/scheduler.py`
- `core/commands/workflow_handler.py`
- `wizard/routes/workflow_routes.py`
- `docs/examples/udos_ulogic_pack/core/ulogic/library/workflows/WORKFLOW-template.md`

## Required v1.5 Standardization Steps

Before freeze, v1.5 must:
- standardize the workflow handoff from the logic input handler
- standardize shared artifact semantics across core and Wizard
- align task/completion updates with workflow state transitions
- align runbook and workflow templates with the shared Markdown template standard
- ensure TUI dialogs, selectors, logs, and status blocks present one workflow model

## Related Documents

- `docs/decisions/v1-5-workflow-manager.md`
- `docs/decisions/v1-5-workflow.md`
- `docs/specs/WORKFLOW-SCHEDULER-v1.5.md`
- `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md`
- `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`
