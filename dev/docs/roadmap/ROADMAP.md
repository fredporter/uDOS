# Contributor Roadmap

Updated: 2026-03-04

This is the canonical roadmap page for the v1.5 `@dev` workspace.

## Current Priorities

1. The tracked v1.5 repo backlog is closed.
2. v1.5.0 release metadata is now stable.

## Tracking Sources

- Active tasks: `dev/ops/tasks.md`
- Machine task state: `dev/ops/tasks.json`
- Completed milestones: `dev/ops/completed.json`
- Contributor log: `dev/ops/DEVLOG.md`
- Contributor decisions: `dev/docs/decisions/`

Root `docs/roadmap.md` is a redirect only.

## Provisioning Round

The v1.5 `@dev` provisioning round is complete:

- contributor operations state is canonical under `dev/ops/`
- contributor docs and decisions are canonical under `dev/docs/`
- Goblin is the tracked overlay lane under `dev/goblin/`
- the Wizard Dev Mode GUI now exposes nested tracked-browser navigation, preview, and safe text editing support through `/api/dev/ops/files`, `/api/dev/ops/read`, and `/api/dev/ops/write`
- the tracked editor round is complete, including validation for JSON, TOML, YAML, Python, shell syntax, and Markdown fence balance
- the Goblin overlay drain is complete for contributor scaffold and policy assertions; remaining Dev-mode branches in `wizard/tests` are runtime-owned
- format-aware helpers are complete for the tracked editor lane, with backend-owned format, normalize, or cleanup actions surfaced per file type

## Release Integration Program

The release-integration phases are closed except for the final freeze brief. The
remaining repo backlog is now mostly documentation cleanup plus a small number
of explicitly open subsystem lanes.

### Phase 1 — Self-Hosting Contributor Loop

Status: Completed

Goal: operate uDOS development from `@dev` using standard runtime surfaces.

- wire the `@dev` workspace to canonical `ucode` planning, workflow, and scheduling flows instead of contributor-only side paths
- prove Dev Mode can browse, edit, format, and save tracked contributor files while the actual execution path still runs through runtime-owned `core/` and `wizard/` services
- add explicit release evidence showing a contributor can open `@dev`, update tracked plans/tasks, schedule work, and execute or inspect it without leaving the v1.5 contract

### Phase 2 — Local Assist Reliability

Status: Completed

Goal: make the local conversation engine dependable enough to serve as the default development/operator assistant.

- keep GPT4All as the local assist baseline and Wizard as the only network escalation layer
- validate the OK context bundle, local model bootstrap, readiness reporting, cache behavior, and fallback boundaries
- define release evidence for "offline ready", "context loaded", and "cloud escalation only when policy or readiness requires it"

### Phase 3 — Budget, Rotation, and Scheduling Closure

Status: Completed

Goal: unify provider failover, budget control, and queue execution into one stable managed contract.

- certify the handoff between `wizard/services/cloud_provider_executor.py`, `wizard/services/quota_tracker.py`, `wizard/services/logic_assist_service.py`, and `wizard/services/task_scheduler.py`
- verify defer/retry behavior for `network_unavailable`, `api_budget_exhausted`, workflow wait states, and retry-safe maintenance policies
- make budget/failover state visible in release evidence, not only in service internals

### Phase 4 — Demo `ucode` Pack

Status: Completed

Goal: ship v1.5 as a demonstrated system, not just a tested codebase.

Recommended demo set:

1. `00-setup-and-status`: boot, profile list, operator status, and release/readiness baseline
2. `01-local-assist-and-knowledge`: run local assist, capture/import knowledge, and show offline-first behavior
3. `02-workflow-and-task-planning`: create, inspect, and run a workflow with task/state output
4. `03-managed-scheduler-and-budget`: queue managed work, show defer/retry/failover behavior, and surface budget state
5. `04-self-hosted-dev-mode`: operate from `@dev`, update tracked planning files, and route execution back through canonical runtime surfaces

Each demo should have:

- a checked-in script or command transcript
- expected artifacts/output
- the profile(s) it is valid for
- a validation command or test proving it still works

### Phase 5 — Certified Profiles And Freeze

Status: Completed

Goal: convert the integrated system into a stable release.

- close install, verify, repair, and rollback evidence for `core`, `home`, `creator`, `gaming`, and `dev`
- align release/version truth so public docs, runtime metadata, and packaging all describe the same active v1.5 state
- publish one final readiness summary that names the exact demo pack, profile evidence, and local-assist/budget/scheduler signoff used for stable release
- release metadata cutover from `beta` to `stable` is complete
