# v1.5.1 TUI Operational Closeout

Status: active patch-stream decision  
Updated: 2026-03-07  
Scope: Bubble Tea `ucode` TUI operational completion required before v1.5.2 and v1.5.3 dependent work

## Purpose

Close the gap between the current v1.5 Bubble Tea shell and a release-quality
operator surface.

The TUI is no longer allowed to be judged only by:
- successful startup
- command dispatch
- renderer correctness
- demo-pack compatibility

For v1.5.1, the TUI must become an operational launcher with truthful menu
semantics and stable result presentation.

## Why This Matters

v1.5.2 and v1.5.3 both assume a reliable local shell/controller surface:

- [v1-5-2-EMPIRE-SERVER.md](./v1-5-2-EMPIRE-SERVER.md)
  pushes provider-heavy workflows into Wizard/Empire and leaves clients as thin,
  local-first shells, editors, and approval/monitor surfaces.
- [v1-5-3-UHOME-KIOSK.md](./v1-5-3-UHOME-KIOSK.md)
  depends on a controller-friendly launcher shell, status panels, and Thin-GUI
  route entry points.

That means v1.5.1 must finish the shell boundary before the Android side
project can depend on the same assumptions.

## Problem Statement

The v1.5 Bubble Tea shell previously had four classes of defects:

1. Dispatch defects
   Plain core commands such as `BINDER`, `PLAY`, `WIZARD`, and `CONFIG` could
   fall through to guidance text instead of executing the command surface.

2. Manifest defects
   Home menu entries pointed to unsupported or invalid commands such as
   `BINDER CREATE @binder/new-mission` and `BINDER OPEN @binder`, creating the
   appearance of a richer product than the runtime actually implemented.

3. Presentation defects
   Runner output could be hidden behind trailing progress packets, making valid
   command results appear to be log-only transport noise.

4. Product-surface defects
   Several menu items were informational placeholders rather than complete
   creation/edit flows.

The first three are patch defects and belong in v1.5.1.
The fourth is a mix of patch completion and deferred workflow implementation.

## v1.5.1 Decision

For v1.5.1:

- the Bubble Tea shell is a truthful operational surface, not a speculative UX
- every built-in home menu item must be one of:
  - a stable inspect/status command
  - a stable launch/open route
  - a stable read/list flow
  - a fully implemented create/edit flow
- no built-in menu item may point at an unimplemented or invalid command
- runner summaries must prioritize user-meaningful result panels over protocol
  transport events
- structured command results with no explicit text output must still render a
  useful summary block

## Required v1.5.1 Outcomes

### A. Truthful Menu Surface

Built-in menu entries must match the real runtime.

Allowed:
- list templates
- inspect profiles
- inspect repair/runtime/wizard/dev status
- open GUI routes
- run known-safe health/verify/status commands

Not allowed:
- fictional binder creation shortcuts
- invalid workspace aliases
- editor labels that only read static templates
- destructive or blocking paths disguised as stable launcher items

### B. Stable Result Visibility

The runner must show result panels by default.

Required behavior:
- `OUTPUT` remains visible after command completion
- `RESULT SUMMARY` appears when handlers return structured data without text
- `PROGRESS` and `RULE` packets do not dominate the visible summary lane

### C. Operational Classification

Every home item must be classified into one of four groups:

1. Inspect
   Status, verification, listing, repair/readiness, profile visibility.

2. Launch
   Thin-GUI routes, Wizard routes, local overlays, kiosk/controller surfaces.

3. Read
   Docs, templates, binder inventories, workflow inventories.

4. Act
   Real workflow execution, creation, editing, or server-control actions.

If an item is not a true `Act` flow, its label must not imply creation or edit
ownership.

### D. Blocked Workflow Inventory

v1.5.1 must explicitly identify which desired menu actions remain unfinished and
why.

At minimum this inventory includes:
- mission/new binder creation
- binder resume/open workflow beyond raw listing
- script editor flow
- inline setup/config editing inside Bubble Tea
- non-blocking operational controls for Wizard/dev/server actions

These are valid backlog items, but they must be named as backlog, not shipped as
fake-complete launcher entries.

## Relationship To v1.5.2 Empire Server

The Empire/Wizard split increases the importance of the shell as:
- a local monitor
- a route launcher
- a review/approval console
- a stable fallback UI when provider logic lives elsewhere

Therefore v1.5.1 must guarantee:
- route truthfulness
- stable job/result rendering
- clear separation between inspect vs act flows
- safe command surfaces for later Android thin-client parity

## Relationship To v1.5.3 uHOME Kiosk

The Android kiosk lane needs:
- a launcher model
- stable status panels
- Thin-GUI route launch semantics
- controller-safe view hierarchy

v1.5.1 is not required to build the Android app in this repo, but it is
required to define and stabilize the launcher behavior the Android app will
mirror.

## Explicit Non-Goals For v1.5.1

The following do not need to be completed in this patch stream:

- Empire provider pipelines
- Android app implementation
- full kiosk/controller UX
- all future binder authoring flows
- full local rich-text/script editing

Those belong to v1.5.2+, v1.5.3+, or later workflow-specific milestones.

## Acceptance Criteria

v1.5.1 closeout is complete only when:

1. every built-in home menu entry dispatches a real supported command or route
2. every built-in home menu label truthfully describes the underlying action
3. runner detail panels keep result output visible after completion
4. structured no-text results still render human-usable summaries
5. stale repo-root/runtime path drift is eliminated from the launcher baseline
6. the unfinished create/edit workflows are documented as deferred work rather
   than shipped as misleading launcher actions
7. public status docs stop claiming backlog closure without the v1.5.1 TUI patch
   scope being acknowledged

## Release Gate

v1.5.2 and v1.5.3 dependent shell/controller work must not assume:
- complete creation/edit workflows
- stable launcher parity
- accurate route semantics

until this v1.5.1 closeout decision and the associated checklist are satisfied.
