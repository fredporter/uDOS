# Workflow Scheduler Spec v1.5

Status: Active  
Last updated: 2026-03-03

## Purpose

This spec defines the canonical v1.5 workflow scheduler contract for the current core implementation.

It covers:
- workflow template structure
- workflow runtime state
- artifact layout
- phase execution model
- provider tier model
- command surface expectations

It does not define the future Wizard GUI or control-plane scheduling APIs. Those remain roadmap work built on top of this core contract.

## Scope

### In scope

- deterministic core workflow execution
- markdown-first workflow templates
- persisted workflow state
- approval checkpoints
- provider-tier escalation
- artifact generation under `memory/vault/workflows/`
- `WORKFLOW` ucode commands

### Out of scope

- Wizard GUI task/calendar/project views
- Wizard budget-window orchestration
- Wizard MCP/API workflow control plane
- Empire and Typo workflow enrichment features

## Canonical Locations

### Template source

Workflow templates currently ship from:

```text
core/framework/seed/bank/templates/workflows/
```

Prompt templates currently ship from:

```text
docs/examples/udos_creative_pack/core/creative/
```

### Runtime source

Core workflow runtime lives in:

```text
core/workflows/
```

### Artifact output

Workflow artifacts are written to:

```text
memory/vault/workflows/<workflow-id>/
```

## Workflow Template Contract

Workflow templates are markdown files with these required sections:

```markdown
# WORKFLOW: <template-id>

## Goal
<text>

## Constraints
- Key: Value

## Phases
1. Label (adapter/prompt -> output-path.md)

## Outputs
- output-path.md
```

### Required rules

- The title line must start with `# WORKFLOW:`
- `Goal` must be present
- `Phases` must contain one or more numbered phase lines
- Each phase line must follow:
  - `<index>. <label> (<adapter>/<prompt> -> <output>)`
- `Outputs` should list the expected artifact paths

### Current parser behavior

The current parser extracts:
- `template_id`
- `project`
- `goal`
- `purpose`
- `inputs`
- `constraints`
- `phases`
- `outputs`

The current parser normalizes phase names from labels into lowercase underscore identifiers.
If a `## Project` section is present, that value becomes the first-class workflow project. Otherwise the parser falls back to `Inputs -> Project`, then to a `project` constraint, then to `workflow_id`.

## Workflow Runtime Contract

### Workflow spec

A workflow spec contains:
- `workflow_id`
- `template_id`
- `project`
- `goal`
- `purpose`
- `inputs`
- `constraints`
- `phases`
- `outputs`
- `created_at_iso`
- `source_path`

### Phase spec

Each phase contains:
- `name`
- `adapter`
- `prompt_name`
- `outputs`
- `inputs`
- `requires_user_approval`
- `provider_hint`
- `budget`

### Workflow state

Runtime state contains:
- `workflow_id`
- `status`
- `current_phase_index`
- `total_cost_usd`
- `total_tokens`
- `created_at`
- `updated_at`
- `next_run_at`
- `phases`

### Phase state

Each phase state contains:
- `name`
- `status`
- `tier`
- `retries_used`
- `escalations_used`
- `provider_id`
- `last_error`
- `last_run_at`
- `approved_at`
- `next_run_at`
- `cost_usd`
- `tokens`

## Status Model

### Workflow status values

Current workflow status values:
- `ready`
- `awaiting_approval`
- `waiting`
- `completed`

### Phase status values

Current phase status values:
- `pending`
- `ready`
- `pending_approval`
- `completed`
- `failed`

## Artifact Contract

Each workflow directory may contain:

```text
workflow.md
workflow.json
state.json
meta/<phase>.json
<phase outputs...>
```

### Required files

- `workflow.md`
  - rendered markdown template used to create the run
- `workflow.json`
  - serialized workflow spec
- `state.json`
  - serialized workflow runtime state

### Phase metadata

Each executed phase writes:

```text
meta/<phase>.json
```

The metadata includes:
- phase name
- provider id
- tier
- success/failure
- validation errors
- cost
- token usage

## Execution Model

### Phase execution order

- phases execute in declared order
- only the current phase may run
- completed phases do not rerun automatically

### Approval gate

If `requires_user_approval` is true:
- successful execution moves the phase to `pending_approval`
- workflow status becomes `awaiting_approval`
- next phase does not start until `WORKFLOW APPROVE`

### Escalation gate

If an operator calls `WORKFLOW ESCALATE`:
- current phase tier moves upward through:
  - `tier1_local`
  - `tier2_cloud`
  - `tier3_high`
- escalation count increments
- workflow returns to `ready`

## Provider Tier Model

Current tier model:

- `tier1_local`
  - local-first drafting and formatting
- `tier2_cloud`
  - balanced hosted refinement
- `tier3_high`
  - expensive/high-end pass

### Current implementation note

The current core implementation uses a deterministic mock provider backend for execution scaffolding.

This means:
- workflow execution is testable and local
- provider contracts are in place
- real provider routing remains follow-on work

## Command Surface

Current command surface:

```text
WORKFLOW LIST [TEMPLATES|RUNS]
WORKFLOW NEW <template> <workflow_id> [key=value ...]
WORKFLOW RUN <workflow_id>
WORKFLOW STATUS <workflow_id>
WORKFLOW APPROVE <workflow_id>
WORKFLOW ESCALATE <workflow_id>
```

### Behavioral expectations

- `WORKFLOW LIST TEMPLATES` lists available workflow templates
- `WORKFLOW LIST RUNS` lists created workflow runs
- `WORKFLOW NEW` renders a template into a workflow run directory
- `WORKFLOW RUN` executes the current phase only
- `WORKFLOW STATUS` reports current phase, status, window, and budget summary
- `WORKFLOW APPROVE` advances an approval-gated workflow
- `WORKFLOW ESCALATE` promotes the current phase to the next tier

## Relationship to Other Docs

- Architecture decision:
  - `docs/decisions/v1-5-workflow.md`
- Roadmap and progress:
  - `docs/roadmap.md`
- Operator usage:
  - `docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md`
- Example templates:
  - `docs/examples/udos_creative_pack/`
