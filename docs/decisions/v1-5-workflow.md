# v1.5 Workflow Scheduler Decision

Status: Active  
Last updated: 2026-03-03

## Decision

uDOS v1.5 adopts a **deterministic, markdown-first workflow scheduler**.

The workflow system is designed for:
- scheduled orchestration
- structured delegation
- controlled iteration
- deterministic progression

It is not designed as opaque autonomous production.

## Current Status

### Core lane completed on 2026-03-03

- `core/workflows/` now exists as the deterministic workflow runtime
- `WORKFLOW` command family is live:
  - `LIST`
  - `NEW`
  - `RUN`
  - `STATUS`
  - `APPROVE`
  - `ESCALATE`
- workflow templates are parsed from markdown
- phase execution, approval checkpoints, and provider-tier escalation are implemented
- workflow artifacts now write to `memory/vault/workflows/<workflow-id>/`
- creative-pack templates and prompts are connected to the core execution path
- command contract, user docs, and targeted tests were updated with the new surface

### Wizard lane not yet merged

- GUI task/calendar/project views
- budget-aware scheduled execution windows
- MCP/API orchestration for workflows
- research/import/contact-linked workflow surfaces

### Extension lane not yet merged

- Empire email/contact/scraping workflows
- Typo integrated file picker, formatting, and template/workflow editing tools
- expanded creative/template library coverage

## Ownership Split

- Core owns deterministic markdown-first workflow parsing, state, artifacts, local execution, and command surface.
- Wizard owns future control-plane orchestration, scheduled execution windows, GUI, and MCP/API surfaces.
- Extensions own domain-specific workflow enrichment and editing tools.

## Design Rules

### 1. Markdown first

Workflows emit structured markdown artifacts as the canonical source of truth.

### 2. Human checkpoints

Major phases pause for review unless explicitly configured otherwise.

### 3. Deterministic contracts

Each phase has explicit inputs, outputs, tier rules, and state transitions.

### 4. Visible provider rotation

Provider escalation must be visible in workflow state and artifacts.

### 5. Slow is stable

The system may intentionally defer execution to scheduled windows rather than completing in one burst.

## Core Architecture

### Runtime modules

Core workflow runtime lives under:

```text
core/workflows/
```

Primary responsibilities:
- parse workflow templates
- manage workflow state machine
- execute phases deterministically
- track approvals and escalations
- write artifacts and state into the vault
- expose the workflow surface through `WORKFLOW`

### Canonical artifact path

Workflow artifacts live at:

```text
memory/vault/workflows/<workflow-id>/
```

Typical contents:

```text
workflow.md
workflow.json
state.json
01-outline.md
02-draft.md
meta/<phase>.json
```

### Workflow template model

Workflow templates are markdown contracts. They define:
- goal
- constraints
- phases
- outputs

Operators are expected to edit constraints and rerun through explicit commands rather than through hidden runtime mutation.

### Phase model

Each phase has:
- input artifact references
- adapter type
- prompt name
- output artifact paths
- approval requirement
- provider hint
- budget cap

### Provider tier model

Tier model for workflow execution:

- `tier1_local`
  - local-first, low cost, drafting/formatting
- `tier2_cloud`
  - balanced cost/quality, structural reasoning
- `tier3_high`
  - limited high-cost refinement or complex synthesis

Escalation rule:
- try lower tier first
- validate output
- escalate only when required and visible in state

## Scheduling Model

The workflow scheduler is a **paced execution system**.

It is intended to support:
- scheduled execution windows
- cooldown periods
- retry and escalation logic
- multi-phase workflows that can run over hours or days

The current merged core lane implements:
- workflow state
- next-run timestamps
- approval and escalation flow

The full budget-aware execution window planner remains Wizard-owned follow-on work.

## Packaging Rule

Packaging is a final-stage workflow concern.

Allowed examples:
- markdown to PDF
- markdown to PPTX
- script to MP4
- score to MIDI

Packaging must not replace structured intermediate artifacts. Text-first and contract-first stages come first.

## Music Rule

If music workflows are used, they must remain structure-first:

1. concept and structure
2. chord/rhythm map
3. score generation
4. audio rendering
5. packaging

Audio must not be the first artifact.

## Explicitly Deferred to Wizard

These are part of the v1.5 roadmap, but not part of the merged core scheduler implementation:

- Notion-like task list and calendar views
- workflow-aware GUI dashboards
- provider budget windows
- off-peak execution planning
- MCP/API workflow orchestration
- research/import/contact-linked workflow control surfaces

Wizard work must build on the core workflow artifact/state contract and must not introduce a second workflow runtime.

## Explicitly Deferred to Extensions

These remain separate active lanes:

- Empire email import to tasks
- contact linking and contact-store repair/debug
- scraping and knowledge expansion workflows
- Typo template browsing, markdown formatting, and workflow editing helpers
- broader template-library growth across writing, image, video, music, and packaging

## Command Surface

Current core command surface:

```text
WORKFLOW LIST [TEMPLATES|RUNS]
WORKFLOW NEW <template> <workflow_id> [key=value ...]
WORKFLOW RUN <workflow_id>
WORKFLOW STATUS <workflow_id>
WORKFLOW APPROVE <workflow_id>
WORKFLOW ESCALATE <workflow_id>
```

## Success Criteria

This decision is considered successfully implemented at the core layer when:
- a workflow can execute across multiple phases with persisted state
- every phase emits structured artifacts
- approvals can pause progression
- provider escalation is deterministic and visible
- local execution works without requiring network/provider access

This decision is considered fully realized for v1.5 only when the Wizard and extension lanes build on this core foundation without creating parallel workflow systems.
