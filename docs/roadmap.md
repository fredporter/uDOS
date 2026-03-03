# uDOS Roadmap (Canonical)

Last updated: 2026-03-04
Release baseline: v1.5 rebaseline
Status: Active

This roadmap tracks the active v1.5 release work. Historical milestone notes belong in `docs/devlog/` or `.compost`, not in the active execution plan.

## Release Truth

- `ucode` is the primary user entry point.
- The v1.5 `ucode` TUI is the standard interactive runtime and requires a full refactor rather than incremental patching.
- uDOS v1.5 is offline-first, local-first, and file-backed by default.
- uDOS v1.5 is a logic-assisted knowledge gatherer and local librarian before it is a networked assistant surface.
- Wizard remains the browser, API, and managed operations layer subordinate to `ucode`.
- `vibe` is restricted to Dev Mode contributor flows.
- global seed banks ship as distributable, read-only Markdown/data scaffolds and may only be edited by contributors through the Dev extension lane.
- user knowledge lives in local writable trees that can supplement seeded global banks without mutating distributable source material.
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
- the offline logic scaffold already documents deterministic project/task/agent/completion contracts under `docs/decisions/v1-5-offline-assist.md` and `docs/examples/udos_ulogic_pack/`
- the final v1.5 logic-assist deployment shape is now captured in `docs/decisions/v1-5-logic-assist-final-spec.md`, with the delivery framework staged under `docs/examples/udos_v1_5_deliverables/`
- the active Wizard/runtime assist lane now runs on the v1.5 contract: GPT4All local advisory status, Wizard network routing/budget control, Markdown-backed `logic-assist` settings, and upgraded secret-store metadata
- setup, self-heal, and Config dashboard surfaces now align to the same GPT4All plus Markdown-config contract so the upcoming `ucode` v1.5 TUI refactor lands on one runtime doctrine
- the live `ucode.py` assist path now follows that same contract: `LOGIC` is the surfaced contributor command lane, Wizard cloud review uses `/api/ucode/logic/*`, and the setup/config drift cleanup for the active path is complete
- retired offline `OK` setup/how-to assets were moved out of the active docs tree into `docs/.compost/`, and the remaining active setup/graphics/transfer docs now point directly at the v1.5 installation and logic-assist contract
- remaining helper surfaces such as the Wizard interactive console, provider setup checker, and Vibe contributor helper now use the v1.5 logic-assist contract directly instead of teaching Ollama install/pull or `assistant_keys.json`-based setup paths
- the deeper `core/tui/ucode.py` contributor route now matches that contract internally too: the live TUI router accepts `LOGIC` only, active helper methods use `logic_*` naming, and the page routing/status path no longer points at the old `/api/ai/*` lane
- the standard shell now routes through the canonical `core/ulogic` input contract: `ucode.py` compiles deterministic command/workflow/knowledge/guidance frames and hands them off to the real `UCODE`, `WORKFLOW`, `BINDER`, and operator surfaces instead of falling straight into contributor fallback
- high-traffic command docs now match that shell contract, including `UCODE TEMPLATE`, `UCODE RESEARCH|ENRICH|GENERATE`, `WORKFLOW IMPORT RESEARCH`, `BINDER IMPORT-RESEARCH`, housekeeping scopes, and open-box `DESTROY`/`RESTORE` guidance
- the v1.5 TUI shell renderer now standardizes routed success output through shared panels for route metadata, workflow state, operator guidance, and knowledge artifacts
- a dedicated Bubble Tea + Lip Gloss frontend now exists under `tui/`, with `core/tui/protocol_bridge.py` providing the structured JSONL backend contract for the Go shell
- Wizard workflow create/list/detail/run/status/dashboard routes now use the core workflow scheduler/runtime contract instead of presenting a separate local-only workflow state model
- Wizard already has active managed operations, queue execution, markdown job import, and `/admin` operator work that should now be tracked as follow-on integration rounds rather than as speculative design
- the managed ops surface is now grouped into v1.5 route families: `/api/ops/session`, `/api/ops/switchboard`, `/api/ops/planning/*`, `/api/ops/automation/*`, `/api/ops/alerts*`, `/api/ops/config/*`, `/api/ops/releases/*`, and `/api/ops/logs/*`
- `/admin` now consumes those v1.5 ops surfaces directly, including role-aware switchboard data for operator versus admin visibility
- shared runtime root resolution is being tightened around the canonical path service and `UDOS_ROOT`, with active logging/monitoring state normalized under `memory/logs`
- Python runtime operation is standardized on `uv` plus `/.venv` across launchers, workspace config, repair status, and root pytest wrappers
- the Python runtime contract now resolves repo root through the canonical path service rather than direct module-relative ancestry inside the active runtime-status surface
- `UCODE RESEARCH|ENRICH|GENERATE` and `UCODE DELIVERABLE VALIDATE` now run through canonical core-owned `uLogic` services and persist Markdown artifacts into the local knowledge tree
- persisted research artifacts now import directly into workflow and binder flows, with `.compost` snapshots covering processed files and overwritten knowledge copies
- health-managed housekeeping now understands `repo`, `vault`, `knowledge`, and `dev` scopes, with Markdown-first cleanup rules and elastic `.compost` pruning
- active runtime persistence and scheduler surfaces now standardize on UTC/GMT timestamps, leaving local timezone conversion to UI and command rendering layers
- shared render helpers now convert UTC/GMT timestamps into local timezone output only at setup, ops, and TUI presentation boundaries instead of inside persistence services
- dashboard and monitoring route payloads now expose shared UTC-to-local server-time metadata instead of formatting local time ad hoc
- beacon, settings metadata, and older service API surfaces are now being normalized onto the same UTC persistence and render-time-only local conversion contract
- legacy management and export surfaces such as `port_manager`, renderer metadata, and config export routes are being pulled onto the same UTC contract instead of mixing local naive datetimes with serialized state
- the central logging system now runs on one shared `udos-log-v1.5` JSONL contract with shared health/stats visibility for core and Wizard
- open-box release evidence now includes focused restore proof for `memory/` plus Sonic local user overlay persistence across backup/restore and seed-catalog rebuild
- Sonic runtime defaults now resolve through the shared Typo workspace for build profile, boot route, and media launcher
- `uHOME` runtime defaults now resolve through the shared Typo workspace for ad processing, presentation mode, node role, and playback target selection
- Wizard dashboard surfaces now expose Sonic and `uHOME` runtime defaults as one shared editable control surface
- the shared container catalog now anchors extension and library execution metadata across core, Wizard, Sonic, `uHOME`, and bundled extensions
- Empire has a first-class Wizard extension surface with dashboard, import review, document detail, template editing, connector jobs, and webhook tooling rather than remaining a placeholder lane

Still open for v1.5 release closure:

- promote uDOS as an offline-first librarian/runtime truth across roadmap, examples, and acceptance evidence
- establish one canonical global knowledge-bank contract: distributed seed, read-only for users, contributor-editable only through the Dev extension lane
- establish one canonical user knowledge-tree contract for local gathering, duplication, editing, enhancement, and runbook execution
- standardize Markdown templates/runbooks so core, Wizard, Sonic, `uHOME`, and offline logic packs use the same open-box workflow structure
- define Sonic Device DB as a distributed seeded global catalog with user submissions and contributor approval flow rather than an end-user editable runtime database
- full specs shakedown against the active catalog in `docs/specs/README.md`
- offline assist promotion from reference scaffold into canonical core runtime pieces
- deploy the final logic-assist standard into runtime and packaging terms: GPT4All local assist, Wizard network budget control, deterministic `uLogic` authority, and advanced workflow/template utilities
- remove the remaining active `OK`/Ollama command, route, and setup surfaces so the planned `ucode` v1.5 TUI refactor lands on one logic-assist contract
- standardize research, enrich, and generate flows as one deterministic Markdown-first pipeline for ingestion, vault enhancement, and artifact production
- finish evidence and presentation hardening for the now-integrated smart logic input handler and workflow-manager handoff inside the refactored TUI
- creator and gaming profile acceptance evidence
- TUI hardening and release evidence capture
- Go frontend build and smoke validation on a machine with Go 1.22+ so the new `udos-tui` binary can be treated as release-ready rather than source-only
- remaining doc/example drift cleanup around the `ucode`-first runtime rule, especially lower-priority compatibility helpers and historical provider docs
- reduce duplicated and overly verbose active docs/specs so v1.5 operators see one short canonical path per surface rather than parallel how-to variants
- Sonic dashboard follow-through beyond runtime defaults, especially end-to-end build/install evidence capture against the new shared workspace contract
- `uHOME` runtime follow-through beyond the current scaffolded presentation/playback layer, especially TV-node polish and standalone packaging validation
- final release pass across Wizard, Groovebox, and core to close remaining spec-to-runtime evidence gaps
- promote the completed research/deliverable command slice into wider workflow and TUI consumption so it becomes standard operator flow rather than a standalone capability
- complete the remaining historical datetime cleanup outside the active UTC-critical runtime surfaces so the broader codebase follows the same contract
- keep any remaining local timezone formatting confined to UI/render layers and out of file persistence, state comparison, and scheduler logic
- continue retiring naive timestamp writes from lower-priority side-state services so historical helpers follow the same UTC contract over time
- continue retiring remaining legacy timestamp/log handling so every active surface uses the same v1.5 central logging and UTC runtime contract

## Pre-v1.5 Completion Rollup

Completed ahead of v1.5 freeze:

- Sonic decision and install docs consolidated onto the v1.5 canonical spec path
- Python runtime consolidated onto one `uv` + `/.venv` contract with root pytest wrappers and `UCODE REPAIR STATUS` verification
- shared Typo workspace established as the seeded/default/user Markdown source for Sonic, `uHOME`, Wizard, and shared extension metadata
- field-level dashboard editing added for shared runtime defaults without introducing a second settings system
- shared container execution and library metadata normalized through the central catalog instead of per-surface manifest drift
- `uHOME` HA bridge moved from stub dispatch to real tuner, DVR, ad-processing, and playback handlers
- `uHOME` presentation runtime scaffold added through Wizard platform routes and dashboard surface
- Empire promoted to an active extension/dashboard lane with integrated import, template, connector, and webhook review instead of a deferred placeholder

Remaining before release freeze:

- capture Sonic install, verify, rollback, and standalone evidence against the refactored contract
- turn the `uHOME` scaffold into a fuller standalone lane with tighter TV-node and packaging validation
- close creator, gaming, and Groovebox acceptance evidence in the same release accounting pass
- finish the Round 1 and Round 4 doc drift cleanup so only active canonical v1.5 surfaces remain prominent

## Roadmap Rounds

### Round 1: Spec and Command Surface Shakedown

Goal:
- make the shipped offline-first command/runtime surface the baseline for the rest of v1.5 work

Scope:
- verify every active spec in `docs/specs/README.md` maps to a real command, runtime module, Wizard route, or explicit deferred lane
- build one consolidated shakedown checklist for release evidence
- confirm the product truth across active docs: offline-first, local librarian, `ucode`-first, Dev extension-gated contributor tooling
- identify every seeded/distributed/read-only global bank versus every writable user-local tree
- resolve active docs/examples drift around `WORKFLOW`, `UCODE PROFILE`, and `UCODE OPERATOR`
- remove stale tracker language that still claims the repo is in the v1.4.6 stabilization phase

Tracking surface:
- `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md`

Exit criteria:
- one current roadmap-driven shakedown checklist exists
- root tracking docs reflect v1.5 rebaseline instead of v1.4.6 stabilization
- high-traffic command docs match the implemented command surface
- active docs consistently describe the global-seed/local-user split and the Dev extension contributor boundary

Decision coverage:
- `docs/decisions/v1-5-rebaseline.md`
- `docs/decisions/v1-5-offline-assist.md`
- `docs/decisions/v1-5-logic-assist-final-spec.md`
- `docs/decisions/OK-GOVERNANCE-POLICY.md`
- `docs/decisions/formatting-spec-v1-4.md`
- `docs/decisions/OK-update-v1-4-6.md`
- `docs/decisions/UDOS-PYTHON-CORE-STDLIB-PROFILE.md`
- `docs/decisions/UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF.md`
- `docs/decisions/VAULT-MEMORY-CONTRACT.md`

### Round 2: Offline Logic and Knowledge Foundations

Goal:
- harden the deterministic offline logic/runtime spine and establish the librarian data foundations for v1.5

Scope:
- promote stable `udos_ulogic_pack` pieces into canonical core-owned runtime modules without breaking the stdlib-only boundary
- align the promoted logic runtime to the final v1.5 deployment doctrine: deterministic `uLogic` authority, GPT4All local assist as advisory-only offline cognition, and Wizard as the only online routing/budget layer
- define the smart logic input handler contract for offline-first intent parsing, slot filling, command routing, and workflow handoff
- standardize the file-backed contract for `project.json`, `agents.md`, `tasks.json`, `completed.json`, mission markdown, and workflow markdown
- provision the global knowledge-bank as distributed seed content that is readable by all users, duplicable into local trees, and contributor-editable only through the Dev extension lane
- provision the user knowledge-tree as the writable local branch for gathering, enriching, and organizing user-specific Markdown knowledge
- define the process/template pack for capturing, enhancing, and reusing Markdown library content across user topics
- incorporate the research/enrich/generate contract so autonomous research, ingestion, enrichment, and template-driven output all land on the same vault-first pipeline
- use `docs/examples/udos_v1_5_deliverables/` as the deployment/reference framework for project, task, workflow, budget, provider, and migration artifacts rather than inventing a second v1.5 scaffold
- keep offline assist `ucode`-first, deterministic, and file-backed rather than introducing a second command system

Exit criteria:
- at least one canonical `core/ulogic` slice is promoted from the example scaffold
- the smart logic input handler is documented as one standard contract rather than scattered parser behavior
- the final logic-assist stack is deployment-ready on paper: GPT4All local assist, Wizard budget control, deterministic `uLogic` authority, and deliverable schemas/templates all point to one framework
- the knowledge-bank and user knowledge-tree contracts are documented and tied to seed/runtime paths
- open-box Markdown templates exist for browse, duplicate, and local edit workflows
- offline logic, templates, and knowledge docs point to one current implementation path
- the `ucode` research implementation round is complete: deliverable validation is enforced in workflow and binder/project write paths, and `UCODE RESEARCH|ENRICH|GENERATE|DELIVERABLE VALIDATE` persist and inspect canonical Markdown/user artifacts
- workflow and binder flows can now ingest persisted research notes directly, and research artifact cleanup routes through the same `TIDY`/`CLEAN` and `.compost` lifecycle as the rest of the file-backed runtime
- periodic housekeeping now factors in Dev Mode hygiene and user-vault Markdown safety instead of treating cleanup as one blind repo operation
- setup, ops, and TUI approval/prediction surfaces now render local time through shared UTC-to-local helpers while active Wizard/core state services persist UTC only
- Wizard and `ucode` console routing now expose the v1.5 logic-assist lane directly (`/api/logic`, `/api/ucode/logic`) instead of the old `OK` local-assist route family, and the shared template workspace now seeds the active `logic-assist.md` provider/budget contract

Decision coverage:
- `docs/decisions/v1-5-offline-assist.md`
- `docs/decisions/v1-5-logic-assist-final-spec.md`
- `docs/decisions/v1-5-research-enrich-generate.md`
- `docs/decisions/v1-5-logic-input-handler.md`
- `docs/decisions/v1-5-workflow.md`
- `docs/decisions/data-layer-architecture.md`
- `docs/decisions/LOGGING-API-v1.3.md`
- `docs/decisions/OBSIDIAN-INTEGRATION.md`
- `docs/decisions/VAULT-MEMORY-CONTRACT.md`

Reference scaffold:
- `docs/examples/udos_ulogic_pack/`
- `docs/examples/udos_v1_5_deliverables/`

Spec anchors:
- `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md`
- `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md`
- `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`

### Round 3: Template and Cross-Component Standardization

Goal:
- make every major v1.5 surface use the same Markdown-first template, runbook, and workflow structure

Scope:
- define the canonical cross-component template/runbook format for uDOS operations
- align core, Wizard, Sonic, `uHOME`, and offline logic examples onto one Markdown workflow/process structure
- ensure global seed content is open-box, browsable, duplicable, and locally editable for user operations
- standardize ingest, enrich, and generate artifacts so research outputs, summaries, guides, and publish targets all derive from Markdown-canonical vault content
- standardize metadata, sections, and evidence expectations for runbooks, templates, seed docs, and workflow artifacts
- make sure all shipped examples behave as reference packs, not parallel runtime contracts

Exit criteria:
- all active uDOS components use one recognizable workflow/template shape
- users can browse distributed seeds, duplicate them, and edit local copies without crossing contributor-only boundaries
- examples/docs no longer drift by component family

Decision coverage:
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`
- `docs/decisions/uHOME-spec.md`
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
- `docs/decisions/MCP-API.md`
- `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
- `docs/decisions/v1-5-research-enrich-generate.md`

Checkpoint focus:
- global knowledge-bank templates
- user knowledge-tree process templates
- Sonic Device DB seed/submission/approval workflow
- cross-component compatible runbook templates

Spec anchors:
- `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`
- `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md`

### Round 4: Wizard, Sonic, and Seeded Catalog Integration

Goal:
- connect the control-plane surfaces and seeded catalogs to the offline-first core contracts without breaking the local-first rule

Scope:
- connect workflow execution windows, provider-budget planning, queue policy, and project/calendar planning to real core workflow state
- standardize the workflow manager boundary so core, Wizard, and logic surfaces refer to one workflow/task orchestration model
- expose workflow orchestration through stable Wizard APIs and MCP bridges
- connect Wizard budget control and online escalation to the final logic-assist deployment contract instead of ad hoc provider routing
- treat Sonic Device DB as a seeded distributed global catalog with local user submissions and contributor approval paths
- keep Wizard ownership limited to control-plane scheduling, managed operations, GUI, API, and network-aware integrations
- continue home-lane bridge work where it depends on the Wizard service boundary

Exit criteria:
- Wizard orchestration builds on the same file-backed workflow and template contracts as core
- one standardized workflow manager contract exists across core/runtime/control-plane surfaces
- Wizard is the only online routing and budget-control layer described by the v1.5 logic-assist standard
- Sonic global catalog and submission flow are documented against the contributor approval model
- service ownership remains aligned to the Wizard split map

Decision coverage:
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
- `docs/decisions/MCP-API.md`
- `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
- `docs/decisions/uHOME-spec.md`
- `docs/decisions/v1-5-logic-assist-final-spec.md`
- `docs/decisions/v1-5-workflow-manager.md`
- `docs/decisions/v1-5-creator-blocker-matrix.md`
- `docs/decisions/alpine-linux-spec.md`
- `docs/decisions/UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md`
- `docs/decisions/UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md`

Spec anchors:
- `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md`
- `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`

### Round 5: TUI, Logic Standardization, and Release Freeze

Goal:
- complete the `ucode` TUI refactor, standardize the new element library and logic-facing runtime contract, then freeze the release surface

Scope:
- audit the current terminal path against the v1.5 TUI decision
- complete the `ucode` TUI refactor as the standard user runtime shell
- standardize the new TUI element library: selectors, input controls, dialogs, lists, logs, blocks, and layout primitives
- align TUI primitives, selectors, input flows, and backend event contracts to one standard
- incorporate the offline logic runtime expectations into the same standardization pass so `ucode`, workflow, logic packs, and the v1.5 deliverables framework share one operator-facing structure
- ensure research/enrich/generate outputs follow the same TUI-facing workflow and artifact structure rather than introducing a second operator experience
- keep the now-integrated smart logic input handler visible in the standard shell flow, with route events and predictable command/workflow/knowledge handoff
- fix selector/input drift, paste handling, resize handling, slow output behavior, and teletext-safe layout consistency
- keep Dev Mode contributor flows separate from the standard runtime
- finish the final shakedown/demo pass and produce the readiness summary for freeze

Exit criteria:
- standard runtime defaults to the `ucode` TUI path
- the complete TUI refactor is in place with one standardized element library
- the smart logic input handler is part of the standard runtime contract and is active inside `core/tui/ucode.py`
- the workflow manager surface matches the same standardized runtime and template model through the TUI shell handoff
- the dedicated Go shell speaks the same event contract through `core/tui/protocol_bridge.py` and can replace the direct Python shell once built in the target environment
- TUI/input/output standardization steps are complete and reflected in current docs/examples
- offline logic packs and workflow packs align to the same operator-facing structure
- Dev Mode-only `vibe` operations stay outside the normal-user path
- final release evidence links back to the shakedown checklist and profile acceptance results

Decision coverage:
- `docs/decisions/v1-5-offline-assist.md`
- `docs/decisions/v1-5-logic-assist-final-spec.md`
- `docs/decisions/v1-5-research-enrich-generate.md`
- `docs/decisions/v1-5-logic-input-handler.md`
- `docs/decisions/v1-5-workflow-manager.md`
- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/decisions/udos-protocol-v1.md`
- `docs/decisions/udos-reference-implementation.md`
- `docs/decisions/udos-teletext-theme.md`

Spec anchors:
- `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md`
- `docs/examples/udos_v1_5_deliverables/docs/specs/udos-v1.5.md`
- `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md`
- `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`
- `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md`

## Decision-to-Round Summary

### Active implementation and hardening

- Round 1:
  - `v1-5-rebaseline`
  - `OK-GOVERNANCE-POLICY`
  - `UDOS-PYTHON-CORE-STDLIB-PROFILE`
  - `UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF`
  - `VAULT-MEMORY-CONTRACT`
- Round 2:
  - `v1-5-offline-assist`
  - `v1-5-logic-input-handler`
  - `v1-5-workflow`
  - `data-layer-architecture`
  - `LOGGING-API-v1.3`
  - `OBSIDIAN-INTEGRATION`
  - `VAULT-MEMORY-CONTRACT`
- Round 3:
  - `SONIC-DB-SPEC-GPU-PROFILES`
  - `uHOME-spec`
  - `WIZARD-SERVICE-SPLIT-MAP`
  - `MCP-API`
  - `HOME-ASSISTANT-BRIDGE`
- Round 4:
  - `v1-5-workflow-manager`
  - `v1-5-creator-blocker-matrix`
  - `alpine-linux-spec`
  - `UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC`
  - `UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE`
- Round 5:
  - `v1-5-offline-assist`
  - `v1-5-logic-input-handler`
  - `v1-5-workflow-manager`
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
2. Use the Round 1 checklist to drive Round 2 offline logic and knowledge foundation work from `docs/examples/udos_ulogic_pack/`.
3. Complete Round 3 template/runbook standardization so all active components share one Markdown-first structure.
4. Continue Round 4 Wizard, Sonic, and seeded catalog integration only on top of the existing core workflow/state model.
5. Run Round 5 TUI and logic standardization, then freeze with one final readiness summary.

## Non-Blocking Notes

- `vibe` remains present in the repository because Dev Mode still uses it, but it is not the standard runtime lane for v1.5.
- Alpine thin-GUI and VM remote desktop remain valid tracked decisions, but they should not block the main v1.5 release unless a certified install lane depends on them.
- Historical milestone summaries should stay in `docs/devlog/` and `.compost` instead of growing this file again.
