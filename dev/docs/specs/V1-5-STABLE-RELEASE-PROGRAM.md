# v1.5 Stable Release Program

Updated: 2026-03-04
Status: Active
Scope: contributor execution plan for v1.5 stable release

## Purpose

This document turns the remaining v1.5 work into one release program.

uDOS already has most required subsystem pieces. The remaining work is to
integrate them, certify them, and demonstrate them through canonical `ucode`
surfaces.

## Stable Release Goals

v1.5 stable must prove:

- `ucode` is the standard operator entry point
- Core remains deterministic and offline-capable
- Wizard remains the only networked provider and web layer
- `@dev` can develop uDOS through canonical planning, task, workflow, and
  scheduling surfaces
- the local conversation engine is reliable before cloud escalation
- provider rotation, budget control, and scheduling act as one managed system
- certified profiles have install, verify, repair, rollback, and demo evidence

## Program Phases

### Phase 1 — Self-Hosted `@dev`

Objective: prove uDOS can be developed from the `@dev` workspace without
leaving the v1.5 contract.

Required outcomes:

- tracked contributor planning files can be edited from Dev Mode
- planning and execution route back through runtime-owned `core/` and `wizard/`
  services
- contributors can inspect task, workflow, and scheduling state through
  canonical surfaces
- no contributor-only execution loop becomes the real runtime

Acceptance evidence:

- one end-to-end contributor walkthrough
- one regression test or focused verification command per touched runtime path
- one demo script or transcript in the release pack

### Phase 2 — Local Assist Reliability

Objective: make the local conversation engine dependable enough to be the
default development and operator assistant.

Required outcomes:

- GPT4All readiness is visible and testable
- the uDOS OK context bundle is loaded into assist requests
- offline-first behavior is preserved when local assist is ready
- cloud escalation only happens when local readiness, policy, or budget requires
  it

Acceptance evidence:

- status/readiness proof for the local model path
- focused validation of context injection and fallback behavior
- one demo showing local assist with uDOS-aware context

### Phase 3 — Managed Budget, Rotation, and Scheduling

Objective: certify the integrated managed-operations path.

Required outcomes:

- provider fallback chain behavior is explicit
- quota and budget state is operator-visible
- defer and retry behavior is deterministic for supported reasons
- scheduled work and prompt-driven work honor the same policy and budget rules

Acceptance evidence:

- one managed-operations checklist with defer/retry examples
- focused validation of failover and budget exhaustion behavior
- one demo showing queued work, deferral, retry, and budget state

### Phase 4 — Demo `ucode` Pack

Objective: ship a small demo set that proves integrated capability.

Canonical demo set:

1. `00-setup-and-status`
2. `01-local-assist-and-knowledge`
3. `02-workflow-and-task-planning`
4. `03-managed-scheduler-and-budget`
5. `04-self-hosted-dev-mode`

Each demo must include:

- checked-in script or command transcript
- expected artifacts or output
- target release profile
- validation command or test reference

## Certified Profile Signoff

The stable release cannot close until `core`, `home`, `creator`, `gaming`, and
`dev` each have:

- install evidence
- verify evidence
- repair evidence
- rollback or recovery evidence where applicable
- demo coverage or explicit non-applicability

## Blocking Risks

The current release blockers are:

- version truth drift between public docs and runtime metadata
- partial offline-assist and knowledge-bank evidence
- missing integrated evidence across provider fallback, budgets, and scheduling
- missing self-hosting proof from the `@dev` workspace
- missing release-grade demo scripts bound to certified profiles

## Canonical Tracking

Use these files together:

- `dev/ops/tasks.md`
- `dev/ops/tasks.json`
- `dev/ops/DEVLOG.md`
- `dev/docs/roadmap/ROADMAP.md`
- `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md`
- `docs/specs/PACKAGING-RELEASE-CONTRACT-v1.5.md`

This document is the contributor execution brief for the final v1.5 release
program. It does not replace runtime or public operator docs.
