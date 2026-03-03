# uDOS Roadmap (Canonical)

Last updated: 2026-03-03
Release baseline: v1.5 rebaseline
Status: Active

This roadmap tracks the active v1.5 release work. Historical milestone notes belong in `docs/devlog/` or `.compost`, not in the active execution plan.

## Release Truth

- `ucode` is the primary user entry point.
- The v1.5 `ucode` TUI is the standard interactive runtime.
- Wizard remains the browser, API, and managed operations layer subordinate to `ucode`.
- `vibe` is restricted to Dev Mode contributor flows.
- Certified release profiles remain:
  - `core`
  - `home`
  - `creator`
  - `gaming`
  - `dev`

## Current Implementation Snapshot

Implemented and available in the repository on 2026-03-03:

- core `WORKFLOW` runtime is live under `core/workflows/`
- `WORKFLOW LIST|NEW|RUN|STATUS|APPROVE|ESCALATE` is implemented and tested
- `UCODE PROFILE`, `UCODE OPERATOR`, `UCODE EXTENSION`, `UCODE PACKAGE`, and `UCODE REPAIR STATUS` are implemented in the core command surface
- certified profile manifest exists at `distribution/profiles/certified-profiles.json`
- workflow templates and reference scaffolds exist under `docs/examples/udos_creative_pack/` and `docs/examples/udos_ulogic_pack/`
- Wizard already has active managed operations, queue execution, markdown job import, and `/admin` operator work that should now be tracked as follow-on integration rounds rather than as speculative design
- Sonic runtime defaults now resolve through the shared Typo workspace for build profile, boot route, and media launcher
- `uHOME` runtime defaults now resolve through the shared Typo workspace for ad processing, presentation mode, node role, and playback target selection
- Wizard dashboard surfaces now expose Sonic and `uHOME` runtime defaults as one shared editable control surface
- the shared container catalog now anchors extension and library execution metadata across core, Wizard, Sonic, `uHOME`, and bundled extensions
- Empire has a first-class Wizard extension surface and dashboard route rather than remaining a placeholder lane

Still open for v1.5 release closure:

- full specs shakedown against the active catalog in `docs/specs/README.md`
- offline assist promotion from reference scaffold into canonical core runtime pieces
- Wizard workflow orchestration completion against the core workflow state/artifact contract
- creator and gaming profile acceptance evidence
- TUI hardening and release evidence capture
- remaining doc/example drift cleanup around the `ucode`-first runtime rule
- Sonic dashboard follow-through beyond runtime defaults, especially end-to-end build/install evidence capture against the new shared workspace contract
- `uHOME` runtime follow-through beyond the current scaffolded presentation/playback layer, especially TV-node polish and standalone packaging validation
- final release pass across Wizard, Empire, Groovebox, and core to close remaining spec-to-runtime evidence gaps

## Pre-v1.5 Completion Rollup

Completed ahead of v1.5 freeze:

- Sonic decision and install docs consolidated onto the v1.5 canonical spec path
- shared Typo workspace established as the seeded/default/user Markdown source for Sonic, `uHOME`, Wizard, and shared extension metadata
- field-level dashboard editing added for shared runtime defaults without introducing a second settings system
- shared container execution and library metadata normalized through the central catalog instead of per-surface manifest drift
- `uHOME` HA bridge moved from stub dispatch to real tuner, DVR, ad-processing, and playback handlers
- `uHOME` presentation runtime scaffold added through Wizard platform routes and dashboard surface
- Empire promoted to an active extension/dashboard lane instead of a deferred placeholder

Remaining before release freeze:

- capture Sonic install, verify, rollback, and standalone evidence against the refactored contract
- turn the `uHOME` scaffold into a fuller standalone lane with tighter TV-node and packaging validation
- close creator, gaming, and Groovebox acceptance evidence in the same release accounting pass
- finish the Round 1 and Round 4 doc drift cleanup so only active canonical v1.5 surfaces remain prominent

## Roadmap Rounds

### Round 1: Spec and Command Surface Shakedown

Goal:
- make the shipped command/runtime surface the baseline for the rest of v1.5 work

Scope:
- verify every active spec in `docs/specs/README.md` maps to a real command, runtime module, Wizard route, or explicit deferred lane
- build one consolidated shakedown checklist for release evidence
- resolve active docs/examples drift around `WORKFLOW`, `UCODE PROFILE`, and `UCODE OPERATOR`
- remove stale tracker language that still claims the repo is in the v1.4.6 stabilization phase

Tracking surface:
- `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md`

Exit criteria:
- one current roadmap-driven shakedown checklist exists
- root tracking docs reflect v1.5 rebaseline instead of v1.4.6 stabilization
- high-traffic command docs match the implemented command surface

Decision coverage:
- `docs/decisions/v1-5-rebaseline.md`
- `docs/decisions/OK-GOVERNANCE-POLICY.md`
- `docs/decisions/formatting-spec-v1-4.md`
- `docs/decisions/OK-update-v1-4-6.md`
- `docs/decisions/UDOS-PYTHON-CORE-STDLIB-PROFILE.md`
- `docs/decisions/UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF.md`
- `docs/decisions/VAULT-MEMORY-CONTRACT.md`

### Round 2: Core Workflow and Offline Assist Hardening

Goal:
- harden the deterministic local runtime that already exists and close the gap between the reference scaffolds and canonical core surfaces

Scope:
- expand `WORKFLOW` template coverage beyond the current creative-pack set
- tighten variable validation, richer phase contract parsing, and packaging-stage follow-through
- promote stable `udos_ulogic_pack` pieces into canonical core-owned runtime modules without breaking the stdlib-only boundary
- align workflow, task, mission, and vault state contracts so markdown-first editing remains the authoritative operator surface
- keep offline assist `ucode`-first and file-backed rather than introducing a second command system

Exit criteria:
- core workflow runtime remains deterministic and local-first with stronger contract validation
- offline assist has at least one promoted canonical core slice beyond the example scaffold
- workflow and offline assist docs point to one current implementation path

Decision coverage:
- `docs/decisions/v1-5-workflow.md`
- `docs/decisions/v1-5-offline-assist.md`
- `docs/decisions/data-layer-architecture.md`
- `docs/decisions/LOGGING-API-v1.3.md`
- `docs/decisions/OBSIDIAN-INTEGRATION.md`

### Round 3: Wizard Orchestration Integration

Goal:
- complete the managed Wizard follow-on layer using the core workflow contracts that already ship

Scope:
- connect workflow execution windows, provider-budget planning, queue policy, and project/calendar planning to real core workflow state
- expose workflow orchestration through stable Wizard APIs and MCP bridges
- keep Wizard ownership limited to control-plane scheduling, managed operations, GUI, API, and network-aware integrations
- continue home-lane bridge work where it depends on the Wizard service boundary

Exit criteria:
- Wizard workflow operations build on `core/workflows/` state and artifacts rather than a parallel scheduler
- managed ops, API, and queue surfaces remain consistent with the core workflow contract
- service ownership remains aligned to the Wizard split map

Decision coverage:
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
- `docs/decisions/MCP-API.md`
- `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
- `docs/decisions/uHOME-spec.md`
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`

Canonical spec companion:
- `docs/specs/UHOME-v1.5.md`

### Round 4: Profile Acceptance and Packaging Closure

Goal:
- close release blockers per certified profile and capture install, verify, and recovery evidence

Scope:
- complete creator blockers: transcription closure, score export, sound-library management, queue and health visibility
- complete gaming profile packaging and verification against the active gameplay/profile specs
- finish package-group install evidence, drift detection, rollback checks, and repair validation across supported profiles
- verify platform-specific expectations for Alpine and thin-GUI follow-on lanes without letting non-blocking variants stall GA

Exit criteria:
- creator, home, gaming, core, and dev profiles each have clear acceptance status
- package, repair, and rollback evidence exists across supported install lanes
- any deferred platform lanes are explicitly marked as post-release or monitor-only

Decision coverage:
- `docs/decisions/v1-5-creator-blocker-matrix.md`
- `docs/decisions/alpine-linux-spec.md`
- `docs/decisions/UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md`
- `docs/decisions/UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md`

### Round 5: TUI Hardening and Release Freeze

Goal:
- harden the standard `ucode` TUI path, capture demo evidence, and freeze the release surface

Scope:
- audit the current terminal path against the v1.5 TUI decision
- fix selector/input drift, paste handling, resize handling, slow output behavior, and teletext-safe layout consistency
- keep Dev Mode contributor flows separate from the standard runtime
- finish the final shakedown/demo pass and produce the readiness summary for freeze

Exit criteria:
- standard runtime defaults to the `ucode` TUI path
- Dev Mode-only `vibe` operations stay outside the normal-user path
- final release evidence links back to the shakedown checklist and profile acceptance results

Decision coverage:
- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/decisions/udos-protocol-v1.md`
- `docs/decisions/udos-reference-implementation.md`
- `docs/decisions/udos-teletext-theme.md`

## Decision-to-Round Summary

### Active implementation and hardening

- Round 1:
  - `v1-5-rebaseline`
  - `OK-GOVERNANCE-POLICY`
  - `UDOS-PYTHON-CORE-STDLIB-PROFILE`
  - `UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF`
  - `VAULT-MEMORY-CONTRACT`
- Round 2:
  - `v1-5-workflow`
  - `v1-5-offline-assist`
  - `data-layer-architecture`
  - `LOGGING-API-v1.3`
  - `OBSIDIAN-INTEGRATION`
- Round 3:
  - `WIZARD-SERVICE-SPLIT-MAP`
  - `MCP-API`
  - `HOME-ASSISTANT-BRIDGE`
  - `uHOME-spec`
  - `SONIC-DB-SPEC-GPU-PROFILES`
  - `UHOME-v1.5`
- Round 4:
  - `v1-5-creator-blocker-matrix`
  - `alpine-linux-spec`
  - `UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC`
  - `UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE`
- Round 5:
  - `v1-5-ucode-tui-spec`
  - `udos-protocol-v1`
  - `udos-reference-implementation`
  - `udos-teletext-theme`

### Redirect, historical, or monitor-only

- `docs/decisions/v1-5-wizard-PLAN.md`
  - redirect stub only
- `docs/decisions/formatting-spec-v1-4.md`
  - redirect to canonical spec
- `docs/decisions/OK-update-v1-4-6.md`
  - redirect to canonical governance decision
- `docs/decisions/uDOS-v1-3.md`
  - historical snapshot only

## Immediate Next Sequence

1. Finish Round 1 shakedown accounting and keep the root tracker files aligned to the v1.5 rebaseline.
2. Use the Round 1 checklist to drive Round 2 core workflow and offline assist hardening.
3. Continue Round 3 Wizard orchestration only on top of the existing core workflow artifact and state model.
4. Close Round 4 certified-profile acceptance evidence for `creator`, `gaming`, `home`, `core`, and `dev`.
5. Run Round 5 TUI hardening and freeze with one final readiness summary.

## Non-Blocking Notes

- `vibe` remains present in the repository because Dev Mode still uses it, but it is not the standard runtime lane for v1.5.
- Alpine thin-GUI and VM remote desktop remain valid tracked decisions, but they should not block the main v1.5 release unless a certified install lane depends on them.
- Historical milestone summaries should stay in `docs/devlog/` and `.compost` instead of growing this file again.
