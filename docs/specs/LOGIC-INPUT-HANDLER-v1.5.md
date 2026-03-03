# Logic Input Handler Spec v1.5

Status: Active
Last updated: 2026-03-03

## Purpose

This spec defines the canonical v1.5 logic input handler for the standard
`ucode` TUI runtime.

It standardizes how uDOS turns terminal input into:
- direct command dispatch
- workflow actions
- local librarian actions
- operator guidance output

The handler is part of the v1.5 `ucode` refactor. It is not a separate shell
and it must not create a second command language.

## Scope

### In scope

- offline-first input normalization
- command detection and direct dispatch
- workflow intent routing
- local librarian and knowledge-tree actions
- deterministic operator guidance output
- visible routing events for the TUI
- handoff to the workflow manager and command dispatcher

### Out of scope

- Wizard-specific GUI parsing rules
- Dev extension contributor helpers
- provider-led hidden execution
- ad hoc parser branches outside the shared runtime contract

## Product Rule

The standard v1.5 shell path is:

```text
terminal input
-> logic input handler
-> command dispatch | workflow manager | knowledge action | guidance render
-> file-backed artifacts and logs
```

The handler must remain:
- `ucode`-first
- offline-first
- deterministic by default
- file-backed
- operator-auditable

## Canonical Input Classes

All standard runtime input must normalize into one of these classes:

1. `command`
   - explicit `ucode` command syntax
   - direct deterministic dispatch

2. `workflow`
   - create, run, continue, approve, escalate, inspect
   - routed into the workflow manager contract

3. `knowledge`
   - gather, classify, summarize, duplicate, enrich, file, or browse Markdown knowledge
   - routed into local librarian actions and knowledge-tree operations

4. `guidance`
   - ambiguous requests that require a visible plan or runbook suggestion before action
   - rendered as deterministic operator guidance rather than opaque execution

## Normalized Frame Contract

The handler must compile input into typed frames before execution.

Minimum frame shape:

```json
{
  "input_class": "workflow",
  "intent": "workflow.run",
  "slots": {},
  "confidence": 0.0,
  "source": "deterministic-pattern",
  "requires_confirmation": false
}
```

Required fields:
- `input_class`
- `intent`
- `slots`
- `confidence`
- `source`
- `requires_confirmation`

Optional fields:
- `project`
- `workflow_id`
- `knowledge_path`
- `template_id`
- `notes`

## Routing Outcomes

The handler must emit one explicit routing outcome:
- `dispatch.command`
- `dispatch.workflow`
- `dispatch.knowledge`
- `dispatch.guidance`
- `dispatch.reject`

Each outcome must be visible to:
- runtime logs
- structured TUI events
- later verification or replay

## Knowledge and Librarian Responsibilities

The input handler is the front door for the v1.5 librarian model.

It must support routing into actions such as:
- browse global knowledge-bank content
- duplicate seed material into a local user knowledge-tree
- enhance or classify local Markdown records
- launch a runbook/template workflow against local material
- suggest capture templates for new user topics

The handler must not allow direct mutation of distributed seed banks from the
normal-user path.

## Standard TUI Alignment

The handler must integrate with the v1.5 `ucode` TUI element library.

Required alignment points:
- one standard shell input widget
- one standard confirmation model
- one standard selector/picker model
- one standard render-event contract for routing feedback
- one standard error/help presentation style

The handler must not introduce custom UI logic that bypasses shared TUI
elements.

## File-Backed Runtime Contract

The handler must resolve actions against the standard file-backed runtime:
- `project.json`
- `agents.md`
- `tasks.json`
- `completed.json`
- Markdown runbooks, workflows, missions, and library templates

When knowledge actions are selected, the handler must preserve the seed/local
split:
- global banks remain distributed and read-only for normal users
- user knowledge trees remain local and writable

## Integration Anchors

Current repository anchors for this spec:
- `core/ulogic/parser.py`
- `core/ulogic/contracts.py`
- `core/tui/ucode.py`
- `core/tui/dispatcher.py`
- `core/tui/ui_elements.py`
- `core/services/command_dispatch_service.py`
- `docs/examples/udos_ulogic_pack/core/ulogic/ucode/dispatcher.py`

## Required v1.5 Standardization Steps

Before freeze, v1.5 must:
- replace scattered parser behavior with one canonical input contract
- document supported intents and slot families
- standardize routing events emitted into the TUI
- standardize the handoff into the workflow manager
- standardize the handoff into knowledge-tree and template actions
- prove the same handler works for command, workflow, and librarian flows

## Related Documents

- `docs/decisions/v1-5-logic-input-handler.md`
- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/decisions/v1-5-offline-assist.md`
- `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md`
- `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md`
- `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`
