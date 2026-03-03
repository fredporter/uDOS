# v1.5 Logic Input Handler Decision

Status: Active  
Last updated: 2026-03-03

## Decision

uDOS v1.5 adopts one **smart, offline-first logic input handler** for the standard
`ucode` runtime.

This handler is part of the v1.5 runtime refactor. It is not an optional helper
layer and it is not a second command system.

The logic input handler must:
- sit inside the standard `ucode` shell flow
- prefer deterministic local parsing before any model-assisted interpretation
- hand off cleanly to command execution, workflow launch, or operator guidance
- remain file-backed and auditable
- align with the TUI element and output contracts

## Purpose

The v1.5 runtime needs one standard path for turning user input into action.

That path must support:
- explicit `ucode` commands
- natural-language intent that should become commands or workflow actions
- workflow launch and continuation
- knowledge-gathering prompts that should resolve into local librarian actions
- local-first operation without requiring network access

## Product Rule

The logic input handler is part of the standard user runtime.

- `ucode` owns the shell and input path
- the logic input handler owns intent parsing and routing
- the workflow manager owns workflow/task orchestration once a workflow action is selected
- Wizard may observe or orchestrate through control-plane APIs, but it must not define a second user input contract
- Dev extension tooling may use separate contributor-only helpers, but those helpers must not redefine the main user input path

## Input Classes

The handler must normalize the standard runtime into a small set of classes:

1. command input
   - explicit `ucode` commands
   - direct deterministic dispatch

2. workflow input
   - workflow creation, launch, continuation, approval, escalation
   - normalized into workflow manager actions

3. logic/library input
   - gather, summarize, classify, duplicate, enrich, or route local Markdown knowledge
   - normalized into file-backed librarian actions

4. operator guidance input
   - ambiguous natural-language prompts that need plan/guidance output before execution
   - normalized into deterministic operator planning rather than opaque model action

## Design Rules

### 1. `ucode`-first

The handler must never behave like a separate assistant shell.

All action paths resolve back into:
- command dispatch
- workflow manager actions
- local operator guidance
- file-backed knowledge actions

### 2. Offline first

Intent parsing must work without network access.

Allowed baseline techniques:
- exact command matching
- structured prefixes
- deterministic pattern libraries
- typed slot extraction
- file-backed rule libraries

Model assistance may exist later, but only as an advisor and never as the only route to understanding input.

### 3. File-backed state

The handler must resolve actions against the same file-backed runtime contract used by offline logic and workflows:
- `project.json`
- `agents.md`
- `tasks.json`
- `completed.json`
- markdown workflow/mission/runbook files

### 4. Visible routing

The runtime must be able to explain what happened to the input:
- command matched
- workflow action selected
- knowledge action selected
- operator guidance path selected

Routing must be visible in logs and render events.

### 5. One shell contract

The logic input handler must align with the v1.5 `ucode` TUI refactor:
- standardized selectors
- standardized dialogs
- standardized input widgets
- standardized event/output contracts

It must not introduce custom ad hoc widgets or hidden parser branches that bypass the shared TUI element library.

## Boundaries

### Core owns

- input normalization rules
- deterministic intent parsing
- command/workflow/knowledge/operator routing
- local rule and slot extraction logic
- file-backed action preparation

### Workflow manager owns

- workflow/task lifecycle after workflow routing
- run state
- approvals
- escalation
- artifact tracking

### Wizard owns

- control-plane APIs
- managed scheduling/orchestration surfaces
- optional GUI views of workflow or queue state

## v1.5 Refactor Implications

The release must treat this as a standardization milestone, not a patch:

- replace scattered parser behavior with one canonical logic input contract
- document the routing classes used by the runtime
- align TUI shell, logic input handler, and workflow manager handoff
- keep Dev extension contributor tooling outside the main user input contract

## Related Documents

- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/decisions/v1-5-offline-assist.md`
- `docs/decisions/v1-5-workflow.md`
- `docs/roadmap.md`
