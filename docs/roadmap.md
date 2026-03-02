# uDOS Roadmap (Canonical)

Last updated: 2026-03-03

This roadmap tracks active execution and planned development.

## v1.5 Rebaseline (Active)

Status on March 2, 2026:
- the earlier v1.5 GA claim dated February 26, 2026 is now treated as stale
- v1.5 has been reopened as an active rebaseline release
- `ucode` is the primary entry point for standard users
- the v1.5 `ucode` TUI is the standard interactive experience
- `vibe` is being restricted to Dev Mode only
- Mistral-backed contributor flows are being restricted to Dev Mode operations
- certified release profiles now define supported install lanes: `core`, `home`, `creator`, `gaming`, `dev`

### Active Foundation Work

- `UCODE PROFILE` command family added as the release-control surface
- `UCODE OPERATOR` command family added as the deterministic local helper surface
- `UCODE EXTENSION`, `UCODE PACKAGE`, and `UCODE REPAIR STATUS` added for profile-aware operations
- non-Dev TUI fallback now routes to local operator planning instead of defaulting to `vibe`/provider routing
- certified profile manifest introduced at `distribution/profiles/certified-profiles.json`

### Pre-1.5 Progress Snapshot

Completed basework as of March 2, 2026:
- Dev Mode is now an explicit certified profile and activated extension surface
- `/dev` is being re-established as the Dev Mode extension framework and governance root
- active standard runtime no longer treats `vibe` as a normal-user surface
- Sonic verification now covers manifest structure, dataset contracts, media provenance, and signed release bundles
- Wizard Sonic GUI now exposes release-signing alerts, dataset-contract state, historical build readiness, and shareable operator views
- Library operator workflow now supports repo validation, clone-to-launch install flow, Thin GUI launch, and structured dependency inventory
- certified-profile policy now gates extension behavior and installer/profile summaries

### Remaining Release Tasks

Priority lanes to close before v1.5 release:
- Creator profile completion:
  Songscribe transcription GA, score export, sound-library management, queue/health visibility
- Gameplay profile completion:
  integrated mission/progression packaging, educational mapping, gaming-profile verification
- Dev extension consolidation:
  route remaining GitHub/library contributor workflows through the Dev Mode extension service
- Packaging and repair closure:
  profile drift detection, rollback/patch validation, package-group install evidence across supported profiles
- Documentation and operator runbooks:
  remove stale legacy terminology and complete profile-specific recovery/troubleshooting docs
- `ucode` TUI refactor:
  align the standard TUI with the v1.5 teletext-safe `ucode` direction, shared primitives, and backend event-contract model
- Full specs shakedown and demo pass:
  run a pre-release feature check against the active specs catalog, implement missing pieces, harden weak paths, and capture end-to-end demo evidence for v1.5 signoff

Documentation closure status:
- active-tree runtime/operator docs cleanup is complete for the v1.5 pre-release surface
- remaining documentation work is limited to low-priority historical terminology cleanup, release-evidence updates, and keeping new docs aligned to the `ucode`-first runtime rule

### Full Specs Shakedown and Demo Pass

Pre-release rule:
- every active feature family represented in `docs/specs/` must have a recorded shakedown/demo outcome before v1.5 release
- use `docs/specs/README.md` as the active spec catalog and `docs/roadmap.md` as the release tracking surface
- where a spec is historical or draft-only, record that status explicitly and do not treat it as a silent pass

Execution model:
- `checking`
  - inventory active canonical specs from `docs/specs/README.md`
  - map each spec to an executable feature area, command surface, route set, or operator workflow
  - identify missing implementation, stale docs, broken examples, and unverified runtime paths
  - produce a demo checklist with expected inputs, outputs, and evidence paths
- `implementing`
  - close any spec-to-runtime gaps discovered during checking
  - fix broken command paths, routes, file layouts, operator flows, or example assets needed for demoable behavior
  - update specs/how-to docs where the implementation truth has shifted
- `hardening`
  - run end-to-end shakedown tests and manual demo passes across core, Wizard, and extension lanes
  - verify error handling, offline behavior, profile gating, packaging assumptions, and recovery paths
  - capture evidence in devlog, release notes, or dedicated acceptance docs
- `extending`
  - add follow-on coverage where a spec is valid but under-demonstrated for v1.5
  - expand examples, sample binders, demo datasets, and operator walkthroughs for post-GA depth without blocking the main release

Minimum v1.5 shakedown coverage:
- command/runtime specs:
  `UCODE-COMMAND-CONTRACT`, `RUNTIME-INTERFACE-SPEC`, `PORT-REGISTRY`, `GHOST-MODE-POLICY`
- workflow/task specs:
  `WORKFLOW-SCHEDULER-v1.5`, `OFFLINE-ASSIST-STANDARD-v1.5`, task ingestion/import specs, formatting spec, Obsidian-facing specs
- profile and extension specs:
  Dev Mode, gameplay lens, 3D world extension lane, plugin manifest, packaging/runtime contracts that remain active for release
- operator proof:
  at least one full demo per certified profile lane where applicable: `core`, `home`, `creator`, `gaming`, `dev`

Release evidence required:
- one consolidated shakedown checklist linked from the roadmap
- implementation fixes landed for any failed critical checks
- hardening notes showing what passed, what is deferred, and what is extension-only
- a final demo/readiness summary before v1.5 freeze

### Decision Coverage For v1.5 Pre-Release

All active files under `docs/decisions/` must be accounted for in the v1.5 pre-release through one of these actions:
- `checking`
- `implementing`
- `hardening`
- `extending`
- `archived/monitor-only`

#### Rebaseline and release truth

- `docs/decisions/v1-5-rebaseline.md`
  - status: active source of truth
  - release action: `hardening`
  - scope: keep roadmap, profile policy, runtime entrypoint rules, and Dev Mode provider boundaries aligned to the rebaseline

- `docs/decisions/v1-5-creator-blocker-matrix.md`
  - status: active release gate
  - release action: `checking` -> `implementing` -> `hardening`
  - scope: creator profile blockers, evidence capture, signoff

#### Workflow and Wizard orchestration

- `docs/decisions/v1-5-workflow.md`
  - status: active source of truth
  - release action: `implementing` -> `hardening` -> `extending`
  - scope: core workflow scheduler, Wizard follow-on integration, extension workflow lanes

- `docs/decisions/v1-5-offline-assist.md`
  - status: active source of truth
  - release action: `checking` -> `implementing` -> `hardening`
  - scope: offline assist standard, `ucode`-first execution loops, file-backed project/task state, and promotion path from the `udos_ulogic_pack` reference scaffold into canonical runtime contracts

- `docs/decisions/v1-5-wizard-PLAN.md`
  - status: superseded redirect stub
  - release action: `archived/monitor-only`
  - scope: keep as redirect only; do not implement from this file

- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
  - status: active boundary map
  - release action: `checking` -> `hardening`
  - scope: enforce Wizard API/MCP/service ownership during v1.5 pre-release work

- `docs/decisions/MCP-API.md`
  - status: active implementation reference
  - release action: `hardening` -> `extending`
  - scope: MCP bridge stability, tool registration, command-routing integrity

#### `ucode` TUI and terminal runtime

- `docs/decisions/v1-5-ucode-tui-spec.md`
  - status: active source of truth
  - release action: `implementing` -> `hardening`
  - scope: `ucode`-first TUI behavior, shared primitives, output-contract alignment, paste/resize safety, teletext-safe layout consistency, and separation from Dev Mode contributor flows

- `docs/decisions/udos-protocol-v1.md`
  - status: active supporting protocol
  - release action: `hardening`
  - scope: TUI/backend structured message protocol stability

- `docs/decisions/udos-reference-implementation.md`
  - status: active supporting reference
  - release action: `implementing` -> `extending`
  - scope: reference implementation shape for the TUI frontend/backend split

- `docs/decisions/udos-teletext-theme.md`
  - status: active supporting theme reference
  - release action: `hardening`
  - scope: teletext-style visual rules and fixed-width layout consistency

#### Core architecture and runtime contracts

- `docs/decisions/UDOS-PYTHON-CORE-STDLIB-PROFILE.md`
  - status: active boundary contract
  - release action: `checking` -> `hardening`
  - scope: preserve stdlib-only core and prevent Wizard/network leakage into core

- `docs/decisions/UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF.md`
  - status: active implementation constraint
  - release action: `checking` -> `hardening`
  - scope: environment model, Wizard venv ownership, Dev Mode alignment

- `docs/decisions/VAULT-MEMORY-CONTRACT.md`
  - status: active source of truth
  - release action: `checking` -> `hardening`
  - scope: tracked scaffold vs local runtime state split, seed installation, memory layout

- `docs/decisions/data-layer-architecture.md`
  - status: proposed architecture still relevant
  - release action: `checking` -> `implementing`
  - scope: data placement cleanup, SQL/JSON/Python parity, local/runtime layout decisions

- `docs/decisions/LOGGING-API-v1.3.md`
  - status: active but draft-like
  - release action: `hardening`
  - scope: unified logging behavior, low-overhead logging, centralised log layout

- `docs/decisions/formatting-spec-v1-4.md`
  - status: redirect stub to canonical spec
  - release action: `checking` complete, now `hardening`
  - scope: active formatting rules now live in `docs/specs/FORMATTING-SPEC-v1.4.md`

- `docs/decisions/OK-update-v1-4-6.md`
  - status: redirect stub to canonical governance decision
  - release action: `hardening`
  - scope: active governance rules now live in `docs/decisions/OK-GOVERNANCE-POLICY.md`

- `docs/decisions/OK-GOVERNANCE-POLICY.md`
  - status: active governance source of truth
  - release action: `hardening`
  - scope: terminology policy, AGENTS authority, boundary rules, and OK Agent behavior constraints

#### Platform and deployment lanes

- `docs/decisions/alpine-linux-spec.md`
  - status: active platform direction
  - release action: `checking` -> `hardening`
  - scope: Alpine deployment assumptions, plugin/package model, OS-aware behavior

- `docs/decisions/UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md`
  - status: active platform/runtime direction
  - release action: `checking` -> `extending`
  - scope: thin GUI runtime expectations and compatibility with current release profiles

- `docs/decisions/UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md`
  - status: active but likely non-blocking for GA
  - release action: `monitor-only` / `extending`
  - scope: keep aligned, but do not let it block v1.5 unless a release path depends on it

#### Obsidian, home, and media lanes

- `docs/decisions/OBSIDIAN-INTEGRATION.md`
  - status: active user model reference
  - release action: `checking` -> `hardening`
  - scope: shared-vault model, open-box editing, Obsidian compatibility

- `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
  - status: planned v1.5 stable lane
  - release action: `implementing` -> `hardening`
  - scope: Home Assistant discovery/command bridge and Wizard contract

- `docs/decisions/uHOME-spec.md`
  - status: active home profile lane
  - release action: `implementing` -> `hardening`
  - scope: uHOME packaging, DVR/ad-filtered stack, Sonic-installed home profile behavior

- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`
  - status: active Sonic contract
  - release action: `hardening`
  - scope: Sonic DB schema and launch-profile consistency for v1.5 media/profile readiness

#### Historical architecture snapshots

- `docs/decisions/uDOS-v1-3.md`
  - status: historical architecture snapshot
  - release action: `archived/monitor-only`
  - scope: retain for context only; do not treat as current release truth

### Workflow Scheduler Split

Core workflow scheduler lane:
- completed on March 3, 2026:
  - added `core/workflows/` deterministic workflow runtime
  - added `WORKFLOW` command family: `LIST`, `NEW`, `RUN`, `STATUS`, `APPROVE`, `ESCALATE`
  - added markdown workflow template parsing, phase execution, approval checkpoints, and provider-tier escalation
  - added workflow artifact/state output under `memory/vault/workflows/<workflow-id>/`
  - wired creative-pack templates/prompts into the core execution path
  - updated command contract and operator docs for `WORKFLOW`
  - added targeted test coverage for workflow parser, scheduler, handler, and command-surface parity
- current core workflow lane status:
  - deterministic local workflow execution is now live
  - markdown-first workflow artifacts are now a real runtime surface, not only a design brief
  - local execution remains available without network/provider access
- canonical docs for this lane:
  - `docs/decisions/v1-5-workflow.md`
  - `docs/specs/WORKFLOW-SCHEDULER-v1.5.md`
  - `docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md`
- remaining core workflow tasks:
  - expand template coverage beyond the current creative-pack set
  - add stronger variable validation and richer phase contract parsing
  - connect real provider backends behind the current deterministic mock provider path
  - add packaging-stage execution contracts after text-first workflow stages are stable

Wizard workflow integration lane:
- completed on March 3, 2026:
  - added canonical Wizard operations routes under `/api/ops/*`
  - built and verified `web-admin` as the hosted operator control plane served from `/admin`
  - added managed deploy mode with SQLite local fallback and Postgres-backed Wizard store support for managed environments
  - added Wizard migrations, managed bootstrap tooling, and cron job entrypoints for due-task execution, health snapshots, and maintenance
  - added markdown-first task and workflow import so Obsidian-style task files can create jobs directly inside the Wizard control plane
  - added managed environment contract docs plus one canonical pytest runner and Python artifact cleanup scripts
  - added workflow-aware queue execution so `workflow_phase` jobs advance real core workflow state instead of acting as placeholder tasks
  - added off-peak window handling, daily provider-budget controls, defer tracking, and per-reason retry/backoff policy for managed scheduling
  - added deferred queue preview and retry controls, inline alert actions, automation heartbeat visibility, and maintenance policy controls in `/admin`
  - added maintenance automation with preview/live passes, per-reason windows, queue-pressure recovery, and Wizard host timezone metadata for operator scheduling decisions
  - added project and calendar planning views on `/admin`, with server-local scheduling timestamps carried through the operator surface
- current Wizard workflow lane status:
  - the managed Wizard control plane is now live and verified end to end at `/admin`
  - markdown-first tasks, prompts, and workflow templates can be expanded into scheduled work without requiring network access just to define the workflow
  - scheduling policy is now operator-visible, previewable, and adjustable from the canonical ops surface
- connect workflow execution windows, provider budget planning, research/import jobs, and contact-linked tasks
- expose workflow orchestration through Wizard APIs and MCP after the core lane is stable
- keep Wizard scheduling and GUI work tracked separately from the core implementation path
- canonical docs for this lane:
  - `docs/roadmap.md`
  - `docs/decisions/v1-5-workflow.md`
- roadmap note:
  - Wizard work should continue building on the core workflow artifact/state contract instead of introducing a parallel workflow runtime
  - next work in this lane should favor richer project/calendar views and contact-linked operator workflows over adding another scheduler surface

### Offline Assist Standard Lane

Offline assist lane:
- completed on March 3, 2026:
  - promoted the v1.5 offline assist decision into the canonical spec at `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md`
  - grounded that spec in the base reference scaffold under `docs/examples/udos_ulogic_pack/`
  - aligned roadmap and specs coverage so the offline assist lane is part of v1.5 release tracking instead of a detached decision note
- current offline assist lane status:
  - the canonical contract now exists for an offline-first assist runtime that is `ucode`-first, file-backed, and deterministic by default
  - the example scaffold is the current implementation reference for parser, planner, executor, verifier, gameplay, and state-store shape
- remaining offline assist tasks:
  - promote stable pieces of the `udos_ulogic_pack` scaffold into `core/` without violating the stdlib-only boundary
  - align workflow, task, and mission contracts so markdown-first editing remains the source surface for offline assist operations
  - connect the offline assist runtime to canonical `ucode` dispatch and local workflow execution without adding a parallel command system
- canonical docs for this lane:
  - `docs/decisions/v1-5-offline-assist.md`
  - `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md`
  - `docs/examples/udos_ulogic_pack/README.md`

Extension workflow lane:
- Empire: email import to tasks, contact linking, contact store repair/debug, scraping, and knowledge expansion jobs
- Typo: integrated file picker, template browser, markdown formatting tools, and workflow/task expansion helpers
- creative pack templates: keep extending template coverage for writing, image, video, music, and packaging workflows

### `ucode` TUI Refactor Lane

Current source of truth:
- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/decisions/udos-protocol-v1.md`
- `docs/decisions/udos-reference-implementation.md`
- `docs/decisions/udos-teletext-theme.md`

Pre-release work:
- `checking`
  - inventory the current `ucode` terminal path against the v1.5 TUI decision
  - identify selector/input inconsistencies, layout drift, unsafe paste handling, backend text paths that bypass the output contract, and any drift that still treats `vibe` or Mistral contributor flows as the standard runtime
- `implementing`
  - refactor the standard TUI toward shared primitives, teletext-safe layout, and structured render events
  - align runtime entry behavior so `ucode` remains the default interactive path and Dev Mode Mistral operations stay separate
- `hardening`
  - shakedown paste safety, resize behavior, slow-output handling, narrow-terminal fallback, and at least one end-to-end workflow/task flow
- `extending`
  - add richer teletext blocks, improved pickers, and post-release polish without blocking signoff

### Documentation Consolidation Lane

Completed on March 3, 2026:
- promoted the active workflow decision into:
  - a stable spec in `docs/specs/WORKFLOW-SCHEDULER-v1.5.md`
  - an operator guide in `docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md`
- converted the older workflow plan file into an archive redirect
- added `docs/specs/DOCUMENTATION-CANONICAL-MAP.md` to record canonical doc ownership and cleanup targets
- merged Wizard plan milestones into the roadmap and converted duplicate plan/spec workflow docs into redirect stubs
- completed a second-pass docs audit for duplication, verbosity, and likely `.compost` candidates
- promoted `docs/decisions/formatting-spec-v1-4.md` into the canonical spec `docs/specs/FORMATTING-SPEC-v1.4.md`
- renamed the legacy task-ingestion spec filename to `docs/specs/TASK-JSON-FORMAT-OK-MODEL-INGESTION.md`
- split `docs/specs/typescript-markdown-runtime.md` into the active contract `docs/specs/TYPESCRIPT-MARKDOWN-RUNTIME-CONTRACT.md` plus archived detail
- split `docs/specs/PACKAGING-DISTRIBUTION-ARCHITECTURE-v1.4.6.md` into the active contract `docs/specs/PACKAGING-RELEASE-CONTRACT-v1.5.md` plus archived detail
- merged `docs/MANAGED-OPERATIONS.md` into `docs/howto/MANAGED-WIZARD-OPERATIONS.md`
- bulk-archived unreferenced devlogs out of the active `docs/devlog/` surface
- split `docs/decisions/OK-update-v1-4-6.md` into the active decision `docs/decisions/OK-GOVERNANCE-POLICY.md` plus redirect stub
- split `docs/specs/Spatial-Grid-COMPLETE.md` into the active contract `docs/specs/SPATIAL-GRID-CONTRACT.md` plus redirect stub
- split `docs/howto/TOOLS-REFERENCE.md` into a short tools index plus focused category pages
- reduced `docs/howto/OFFLINE-ASSITANT-SETUP.md` into a front-door guide plus quickstart/reference companions
- reduced `docs/howto/SVG-GRAPHICS-GENERATION.md` into a front-door guide plus quickstart/reference companions
- reduced `docs/howto/WIZARD-PLUGIN-SYSTEM.md` into a front-door guide plus quickstart/reference companions
- reduced `docs/ARCHITECTURE.md` into an overview plus detailed integration reference
- reduced `docs/howto/BINDER-USAGE-GUIDE.md` into a front-door guide plus binder quickstart
- reduced `docs/examples/example-sqlite.db.md` into a front-door example plus focused companion examples
- reduced `docs/specs/UCODE-COMMAND-DISPATCH-v1.4.4.md` to a redirect stub plus `docs/specs/UCODE-DISPATCH-CONTRACT.md`
- aligned the active runtime docs to the v1.5 rule that `ucode` TUI is the standard experience and `vibe`/Mistral contributor flows are Dev Mode only
- rewrote TUI-adjacent docs around the v1.5 `ucode` TUI source of truth and added a dedicated TUI refactor lane to the roadmap
- updated operator-facing install, setup, migration, selector, Ghost Mode, and MCP docs to remove `vibe`-first runtime guidance
- completed the active-tree documentation cleanup pass for core operator/runtime docs and the main docs entry surfaces

Remaining:
- complete low-priority terminology cleanup in historical or low-traffic active docs as time permits
- keep future docs aligned to the `ucode`-first runtime rule and Dev Mode boundary

### Workflow Rebaseline Notes

Carry-forward direction from the workflow brief and current implementation:
- markdown-first remains the canonical authoring model
- human checkpoints remain required between major phases unless explicitly relaxed later
- paced execution windows remain part of the active design, but only the core workflow artifact/state layer is implemented today
- provider rotation is currently deterministic and scaffolded; budget-aware Wizard orchestration remains a follow-on lane
- workflow implementation is now split deliberately:
  - core owns deterministic parsing, state, artifacts, local execution, and command surface
  - Wizard owns future scheduler windows, GUI, MCP/API orchestration, and budget-aware execution
  - extensions own domain-specific workflow enrichment such as contacts, email intake, research, and formatting

### Creator Acceptance Pass

The creator-profile acceptance pass started on March 3, 2026.

Current tracking document:
- [`docs/decisions/v1-5-creator-blocker-matrix.md`](/Users/fredbook/Code/uDOS/docs/decisions/v1-5-creator-blocker-matrix.md)

Current result:
- creator profile remains blocked by transcription scaffolding, score export closure, sound-library health verification, and end-to-end install/verify evidence

### Next Release Sequence

1. Close the Dev extension consolidation and documentation cleanup lane.
2. Run the full specs `checking` pass and build the v1.5 shakedown/demo checklist from `docs/specs/README.md`.
3. Expand the core workflow lane with more templates and stronger phase contracts.
4. Start Wizard workflow integration against the new core workflow artifact/state model.
5. Finish creator-profile blocker matrix and acceptance tests.
6. Finish gameplay/gaming profile packaging and verification.
7. Complete the specs shakedown `implementing` and `hardening` passes, then run the full certified-profile release readiness sweep.
8. Freeze docs, installers, operator runbooks, and demo evidence for v1.5 signoff.

### Immediate Exit Criteria

- `ucode` remains the sole primary interaction surface for normal runtime
- profile install/enable/verify flows work from the TUI
- standard runtime no longer depends on `vibe`
- release/governance docs stop claiming a completed v1.5 GA state

---

## Scope Notes

- macOS Swift thin UI source is not part of this repository and is maintained as an independent commercial companion application.
- Alpine-core thin UI remained conceptual and was not developed as an active implementation lane in this repository.
- Sonic work was tracked as a dedicated pending-round stream — completed 2026-02-23 (I6 schema contract parity + alias retirement, GA3 uHOME packaging). 55 sonic tests passing at v1.5 GA.

Previous roadmap snapshot is archived at:
- `/.compost/2026-02-22/archive/docs/roadmap-pre-cycle-d-2026-02-22.md`

---

## Architecture Convergence Sprint (2026-02-26) ✅

**Primary Focus:** Pre-release parallel-stack cleanup and service consolidation.
See full details: `docs/decisions/ARCHITECTURE-DEFERRED-MILESTONES.md`

### Completed
- ✅ Entry point & call graph audit — 6 entry points mapped, 8 parallel-stack problems (P1–P8) identified
- ✅ P2: Removed dead `wizard.json` read from `UnifiedConfigLoader`
- ✅ P4: `get_ok_local_status()` delegates to the shared provider-status handler — single OK provider status path
- ✅ P5: Lazy imports in `core/tui/ucode.py` — eliminates Core→Wizard circular import
- ✅ P6: `/api/self-heal/status` wired to `collect_self_heal_summary()` via `run_in_executor`
- ✅ P7: `admin_secret_contract.py` → `secret_vault.py` — naming collision resolved
- ✅ P1: `GET /health` and `GET /api/dashboard/health` merged via `health_probe()` in `wizard/version_utils.py` + `dashboard_summary_routes.py`
- ✅ P3: Notification history unified — `NotificationHistoryProtocol` in core; `NotificationHistoryAdapter` registered in `CoreProviderRegistry` at Wizard startup; core writes to SQLite backend when Wizard is running, falls back to JSONL offline

### Key Commits
| Commit | Description |
|---|---|
| `a03facd` | Dead routes wired in wizard/server.py |
| `b85406c` | Duplicate method defs + unused imports removed |
| `07ce276` | P4/P6/P7 convergence |
| `6c4c953` | P2 dead config read + deferred milestones doc |
| `4e05561` | P5 circular import fix |
| `007b042` | P1 + P3 health consolidation + notification history |

---

## v1.4.6 Development Release (Upcoming)

**Primary Focus:** Environment configuration consolidation, testing phase verification, config alignment

### Completed Features
- ✅ Centralized `UnifiedConfigLoader` for all config sources (.env → TOML → JSON)
- ✅ Centralized shared provider-status handler for Ollama/Mistral status checking
- ✅ Centralized `PermissionHandler` created + critical class definition bug fixed
- ⏳ Partial TUI migration to config loader (7 os.getenv() → get_config())
- ⏳ Wizard provider routes migrated to the shared provider-status handler
- ✅ Unit tests for all 3 central handlers (113/113 passing)
- ✅ `admin_secret_contract.py` (SecureVault interface for cloud API keys)

### Planned Features
- Complete config loader migration (100+ remaining `os.getenv()` calls)
- Path constants handler (`core/services/paths.py`)
- Documentation: ENV-STRUCTURE spec completion

### Exit Criteria
- [x] Config loader implementation complete with type-safe accessors
- [x] **FIX:** PermissionHandler class definition (critical bug — resolved)
- [x] **CREATE:** Unit tests for 3 central handlers — **113/113 passing**
- [x] All TUI/Wizard/core `os.getenv()` calls centralized — **100% complete** (3 remaining are in test migration demos only)
- [x] Path constants handler created (`core/services/paths.py`)
- [x] User data paths aligned — wizard routes + user_service both use `get_user_manager()` → `memory/bank/private/users.json`
- [x] Secrets location documented with path constants (`paths.py`: get_vault_root, get_vault_md_root, get_private_memory_dir)
- [x] Profile matrix tests pass — 16/16 passing
- [x] `admin_secret_contract.py` created — unblocks 11 provider-status handler cloud tests
- [x] Devlog: v1.4.6 completion summary — `docs/devlog/2026-02-24-v1.4.6-complete.md`

---

## v1.4.7 Development Release (Upcoming)

**Primary Focus:** Remaining v1.5 blockers, stability improvements, final pre-release polish

### Completed Features
- ✅ Sonic schema parity (SQL/JSON/Python) — 3/3 tests passing, contract validator in place
- ✅ Cloud provider expansion — `cloud_provider_executor.py` fallback chain (Mistral→OpenRouter→OpenAI→Anthropic→Gemini), 12 tests
- ✅ Ollama tier baselines — `ollama_tier_service.py` with explicit tier1/tier2/tier3 definitions, 22 tests
- ✅ Wizard secret sync drift repair — fixed `collect_admin_secret_contract` isolation, all 9 sync tests passing
- ✅ Sonic uHOME bundle contract — 21/21 tests passing
- ✅ uHOME HA bridge fully wired — real tuner/DVR/ad-processing/playback handlers, 32 integration tests

### Exit Criteria
- [x] Wizard secret store sync contract fully implemented — drift detection + repair tested
- [x] Sonic schema drift eliminated across all layers — 3/3 contract tests pass
- [x] Cloud provider fallback chain deterministic and tested — all 5 providers + 12 executor tests
- [x] Ollama tier-aware pulling stabilized — tier1/2/3 baselines + detect_missing_models
- [x] uHOME HA bridge routes live with integration tests — **32/32 passing** (tuner, DVR, ad-processing, playback)
- [x] Extended integration test coverage — 56 new tests this milestone (executor×12, tier×22, HA bridge×32 – net +22 with overlap reduction)
- [x] Devlog: v1.4.7 completion summary — `docs/devlog/2026-02-24-v1.4.7-complete.md`

---

## Flexible Development Buffer (Optional Enhancements)

**Placeholder rounds for additional development if needed** — no committed features.

If the v1.4.6 and v1.4.7 timelines accelerate, we can add:
- Additional cloud providers
- Extended Wizard dashboard consolidation
- 3DWORLD extension packaging
- Stub remediation (Git actions, plugin stubs, dataset parsing)
- Docs normalization work

Or slot this time for burn-in, stabilization, and user validation before RC phase.

---

## v1.5 Complete Tested Working Release ✅ (Superseded snapshot from 2026-02-26)

This section is retained as historical evidence only. It is no longer the active release truth for the repository after the March 2, 2026 rebaseline.

**Primary Focus:** Release candidate hardening → General Availability

### Release Scope (All v1.4.6 + v1.4.7 Features Plus)
- Offline/online parity validation
- Capability-tier installer gates with deterministic fallback
- Full cloud provider support matrix
- Ollama baseline with self-heal diagnostics
- Wizard config/secret sync contract verified
- Sonic drift cleanup complete
- uHOME + Home Assistant bridge live
- Sonic Screwdriver uHOME standalone packaging
- Wizard networking + beacon services stabilized

### Milestone Exit Criteria
- [x] RC1 burn-in cycle: multi-day reliability run completed
- [x] Extended integration test suite: core/wizard/full profiles passing — **2280/6 skipped** (2026-02-26)
- [x] GA1: Release-candidate burn-in cycle (multi-day reliability run + failure triage)
- [x] GA2: Post-RC stabilization sweep and doc finalization
- [x] GA3: Release readiness validation (operator runbooks tested end-to-end)
- [x] GA4: Final security audit and dependency scan — `.env` not in git, CI gate active, secrets.tomb in place
- [x] All freeze-blocker lanes closed and evidence captured
- [x] Operator readiness confirmed: deployment guides, troubleshooting, recovery paths documented

### v1.5 Launch Readiness Checklist
- [x] Documentation: Full operator runbooks for all deployment tiers
- [x] Minimum spec verified: Linux/macOS/Windows 10+ with explicit offline paths
- [x] Provider fallback tested under network failures, rate limits, auth errors
- [x] Ollama baseline proven stable across tier2/tier3 hardware profiles
- [x] Sonic Screwdriver uHOME installer tested on compatible hardware
- [x] Wizard networking beacon services stable under degraded conditions
- [x] Support: Known issues list with workarounds and tracking issues filed for v1.5.x patches — `docs/known-issues.md`

---

## v1.5.1+ Patch Stream (After v1.5 GA)

Will include:
- Security fixes and dependency updates
- Stability improvements from post-GA feedback
- Non-blocking feature enhancements
- Performance optimizations

---

---

## Cycle D Completion Summary

All work from Cycle D has been completed and moved into v1.4.6 and v1.4.7 milestones above.

For detailed completion evidence and status, see:
- `docs/devlog/2026-02-23-roadmap-completed-rollup.md` - Comprehensive completion summary
- `docs/devlog/2026-02-24-testing-phase-verification.md` - Testing phase validation
- `docs/devlog/2026-02-24-env-alignment-audit.md` - Configuration system audit

### Completed Cycle D Tracks
- ✅ Minimum spec parity validation
- ✅ Installer capability gates (I1, I2)
- ✅ Cloud provider schema and fallback chain (I3)
- ✅ Ollama baseline tier pulls and self-heal (I4)
- ✅ Wizard config/secret sync drift repair (I5)
- ✅ Sonic schema contract cleanup (I6)
- ✅ RC1 validation sweep (I7)
- ✅ GA1: Release-candidate burn-in cycle
- ✅ GA2: uHOME + Home Assistant bridge
- ✅ GA3: Sonic uHOME packaging

All evidence captured in devlog/ directory.

---

## Quality Gate Rules

- [x] Runtime logs remain under memory/logs and test artifacts remain under .artifacts paths.
- [x] All v1.4.6 and v1.4.7 development work captured with evidence in `docs/devlog/`
- [x] v1.5 release readiness validated through full test matrix before GA — **2280 passed** (2026-02-26)
- [x] Known issues and patch assignments prepared for v1.5.1+ stream before launch — `docs/known-issues.md`
