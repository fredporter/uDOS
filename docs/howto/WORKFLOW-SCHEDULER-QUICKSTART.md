# Workflow Scheduler Quickstart

Updated: 2026-03-03

This guide shows how to use the current core `WORKFLOW` command surface.

## What It Does

The workflow scheduler lets you:
- create a workflow run from a markdown template
- execute one phase at a time
- pause for approval between phases
- escalate provider tier when needed
- inspect artifacts and state in `memory/vault/workflows/`

## Available Commands

```bash
WORKFLOW LIST TEMPLATES
WORKFLOW LIST RUNS
WORKFLOW NEW <template> <workflow_id> [key=value ...]
WORKFLOW RUN <workflow_id>
WORKFLOW STATUS <workflow_id>
WORKFLOW APPROVE <workflow_id>
WORKFLOW ESCALATE <workflow_id>
```

## 1. List Templates

```bash
WORKFLOW LIST TEMPLATES
```

Current templates come from:

```text
core/framework/seed/bank/templates/workflows/
```

## 2. Create a Workflow Run

Example:

```bash
WORKFLOW NEW WRITING-article article-001 goal="Write release note" audience=operators tone=plain word_limit=600
```

This creates:

```text
memory/vault/workflows/article-001/
```

With:
- `workflow.md`
- `workflow.json`
- `state.json`

## 3. Run the Current Phase

```bash
WORKFLOW RUN article-001
```

This executes only the current phase.

If the phase requires approval:
- phase state becomes `pending_approval`
- workflow state becomes `awaiting_approval`

## 4. Check Status

```bash
WORKFLOW STATUS article-001
```

Status output shows:
- workflow status
- current phase
- next window
- budget spent
- token usage
- current tier
- last error, if any

## 5. Approve a Phase

If a phase is waiting for approval:

```bash
WORKFLOW APPROVE article-001
```

This marks the current phase complete and advances the workflow to the next phase.

## 6. Escalate Tier

If you want to move the current phase to a higher provider tier:

```bash
WORKFLOW ESCALATE article-001
```

Current tier order:
- `tier1_local`
- `tier2_cloud`
- `tier3_high`

## 7. Inspect Artifacts

Each workflow run writes to:

```text
memory/vault/workflows/<workflow-id>/
```

Typical files:

```text
workflow.md
workflow.json
state.json
meta/<phase>.json
01-outline.md
02-draft.md
```

## Operator Notes

- The current implementation is deterministic and local-first.
- Real provider-backed execution is not the primary contract yet.
- Wizard GUI, MCP orchestration, and budget-window planning are separate roadmap work.

## Related Docs

- Spec:
  - `docs/specs/WORKFLOW-SCHEDULER-v1.5.md`
- Decision:
  - `docs/decisions/v1-5-workflow.md`
- Roadmap:
  - `docs/roadmap.md`
- Example templates:
  - `core/framework/seed/bank/templates/`
