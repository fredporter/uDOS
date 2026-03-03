# v1.5 Workflow Manager Decision

Status: Active  
Last updated: 2026-03-03

## Decision

uDOS v1.5 adopts one **standardized workflow manager contract** across core,
Wizard, and offline logic surfaces.

The workflow manager is the single orchestration boundary for:
- workflow lifecycle
- task linkage
- approvals
- escalation
- artifact tracking
- run state

This is part of the v1.5 runtime refactor and must not split into separate
component-specific workflow runtimes.

## Purpose

The repository already contains:
- the `WORKFLOW` command family
- markdown workflow contracts
- offline logic scaffolding
- Wizard orchestration surfaces

v1.5 needs these to resolve into one workflow manager contract rather than a set
of related but drifting lanes.

## Product Rule

There is one workflow model for active v1.5 runtime behavior.

- Core owns the canonical workflow state and artifact model
- Wizard may orchestrate, schedule, or visualize that model
- offline logic may launch or advance workflows through that model
- TUI surfaces must present that model through the standardized `ucode` runtime

No surface may introduce a parallel task/workflow engine with different state
semantics for active v1.5 work.

## Canonical Contract

The workflow manager must unify:
- workflow definitions
- workflow run state
- task relationships
- approval checkpoints
- escalation markers
- artifact outputs
- queue/schedule metadata where applicable

The contract should remain file-backed and operator-readable.

Minimum state surfaces:
- markdown workflow templates
- workflow artifact folders
- `tasks.json`
- `completed.json`
- related project/agent policy files where the run requires them

## Ownership Split

### Core owns

- workflow parsing
- workflow run state
- approval and escalation semantics
- artifact production contract
- deterministic local execution
- the `WORKFLOW` command family

### Wizard owns

- queue windows
- managed scheduling
- GUI/API/MCP exposure
- budget/control-plane policy

Wizard must build on the core workflow manager contract, not redefine it.

### Offline logic owns

- intent-to-workflow handoff
- workflow launch preparation
- workflow-aware knowledge/runbook generation

Offline logic must treat the workflow manager as the execution boundary once a
workflow action is selected.

## Design Rules

### 1. Markdown first

Workflow definitions and artifacts remain markdown-first and operator-readable.

### 2. File-backed truth

Workflow/task state must stay compatible with the same file-backed librarian
model used by offline logic.

### 3. Shared artifact semantics

Every surface must agree on:
- where artifacts live
- what run state means
- what approval means
- what escalation means
- how completion evidence is recorded

### 4. Cross-component compatibility

The workflow manager must align with the v1.5 standard template/runbook shape so
core, Wizard, Sonic, `uHOME`, and logic packs can share one operational structure.

### 5. TUI alignment

The workflow manager must fit the v1.5 `ucode` TUI refactor:
- standardized shell entry
- standardized dialogs/selectors
- standardized progress/log blocks
- standardized event/output contracts

## v1.5 Refactor Implications

The release must:
- standardize the workflow manager contract across runtime/control-plane surfaces
- document the handoff from logic input handler to workflow manager
- ensure the TUI refactor presents workflow actions through the new standard element set
- keep Dev extension tooling contributor-only and outside the normal-user workflow contract

## Related Documents

- `docs/decisions/v1-5-workflow.md`
- `docs/decisions/v1-5-logic-input-handler.md`
- `docs/decisions/v1-5-offline-assist.md`
- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/roadmap.md`
