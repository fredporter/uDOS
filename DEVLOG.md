# DEVLOG.md — uDOS Development Log

Last Updated: 2026-03-04
Version: v1.5 rebaseline
Status: Active

---

## Purpose

This log tracks root-level milestone changes and release-tracking updates for the active repository state.

---

## Entries

### 2026-03-04: Bubble Tea + Lip Gloss v1.5 TUI Frontend

**Status:** Completed

**Changes:**
- added a dedicated Go frontend under `tui/` built on Bubble Tea and Lip Gloss instead of keeping the v1.5 shell as Python-only ad hoc rendering
- added `core/tui/protocol_bridge.py` so the frontend talks to the existing runtime through the v1.5 JSONL protocol and structured event blocks
- wired the standard launcher to prefer the compiled Go frontend when `tui/bin/udos-tui` exists and the session is interactive
- added a build script and dedicated launcher for the Go shell

**Implementation truth captured:**
- the Go shell now owns header/body/footer layout, action selection, command entry, routed block rendering, and teletext-style welcome output
- the Python backend bridge owns deterministic command/workflow/knowledge/operator routing and emits structured `block` and `teletext` events rather than raw terminal text
- the v1.5 frontend/backend split now matches the direction documented in `v1-5-ucode-tui-spec.md` and the Bubble Tea/Lip Gloss brief

**Validation:**
- `python3.12 -m py_compile core/tui/protocol_bridge.py core/tests/tui_protocol_bridge_test.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/tui_protocol_bridge_test.py core/tests/tui_renderer_v15_panels_test.py core/tests/ucode_tui_v15_routing_test.py`
- result: 13 passed

**Limitations:**
- Go frontend compile/runtime validation was not possible in this shell because `go` is not installed

**Next steps:**
1. run `./scripts/build_udos_tui.sh` on a machine with Go 1.22+ and smoke-test `./bin/udos-tui`
2. expand the Go frontend controls from the initial home/command/runner flow into the full selector/dialog/input set described in the teletext brief

### 2026-03-04: Round 5 TUI Panels, Wizard Workflow Contract, And Open-Box Evidence

**Status:** Completed

**Changes:**
- standardized the Round 5 shell renderer around shared boxed-panel primitives for route metadata, workflow state, operator plans, and knowledge artifacts
- finished the Wizard workflow facade so create/list/detail/run/status/dashboard routes now resolve through the core workflow scheduler/runtime contract instead of presenting a parallel local-only workflow model
- reduced duplicate active docs around workspace transfer and Sonic standalone release/install to one short canonical path per surface
- added focused open-box restore evidence proving that a backed-up `memory/` tree restores local Markdown content and the Sonic user overlay after runtime removal/reinstall-style cleanup

**Validation:**
- `python3.12 -m py_compile core/tui/ui_elements.py core/tui/renderer.py wizard/services/workflow_manager.py wizard/routes/workflow_routes.py core/tests/open_box_restore_evidence_test.py wizard/tests/workflow_routes_test.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/tui_renderer_v15_panels_test.py core/tests/ucode_tui_v15_routing_test.py core/tests/open_box_restore_evidence_test.py core/tests/sonic_device_service_test.py wizard/tests/workflow_routes_test.py`
- result: 14 passed

**Next steps:**
1. finish the remaining release-evidence lane for certified profiles and final freeze accounting
2. continue historical provider/doc cleanup where older compatibility surfaces still mention the retired local-model stack

### 2026-03-04: v1.5 `ucode.py` Logic Route Refactor

**Status:** Completed

**Changes:**
- removed the live `ok` prefix from the active `ucode` TUI router so the contributor lane is exposed as `LOGIC` only
- renamed the active local-output, file-action, and fallback helpers inside `core/tui/ucode.py` from `ok_*` to `logic_*`
- removed the remaining active Ollama-adapter bootstrap from the TUI provider registration path and updated Wizard page routing to use the v1.5 logic endpoints instead of `/api/ai/*`

**Next steps:**
1. continue the broader TUI refactor through the element library, input handler, and workflow-state surfaces
2. retire the remaining historical `ok_*` names in lower-priority compatibility modules when those modules are next touched

### 2026-03-04: v1.5 TUI Logic Input Handoff Integration

**Status:** Completed

**Changes:**
- rewired the standard `ucode` shell path to use the promoted `core/ulogic` parser instead of falling straight into ad hoc contributor fallback
- added deterministic TUI routing helpers for workflow, knowledge, and guidance frames so the shell now hands off to the real `WORKFLOW`, `UCODE TEMPLATE|RESEARCH|ENRICH|GENERATE`, and operator surfaces
- kept Dev Mode contributor fallback only for low-confidence guidance prompts, preserving the `/dev` lane without letting it replace the standard runtime contract
- added focused regression coverage for workflow, knowledge browse/duplicate, research routing, standard guidance, and Dev-only fallback behavior

**Implementation truth captured:**
- `core/tui/ucode.py` now compiles one primary `IntentFrame` and routes it through explicit `dispatch.command`, `dispatch.workflow`, `dispatch.knowledge`, or `dispatch.guidance` outcomes
- workflow intents now resolve into canonical `WORKFLOW` commands instead of ad hoc TUI-only execution paths
- knowledge intents now resolve into canonical `UCODE TEMPLATE` and `UCODE RESEARCH|ENRICH|GENERATE` commands, preserving file-backed artifacts and the seed/local split
- standard runtime ambiguous prompts now render deterministic operator guidance, while Dev Mode can still fall back to contributor routing for non-deterministic prompts

**Validation:**
- `python3.12 -m py_compile core/tui/ucode.py core/tests/ucode_tui_v15_routing_test.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ucode_tui_v15_routing_test.py`

**Next steps:**
1. finish the remaining TUI element-library and workflow-state presentation standardization work
2. align help/status render blocks with the same route metadata so workflow and librarian flows present one shell doctrine

### 2026-03-04: v1.5 Command Reference And System Guide Alignment

**Status:** Completed

**Changes:**
- updated the active command reference to document the live v1.5 shell-routing contract instead of leaving the new parser-to-command handoff implicit
- added the standard research/template/workflow-import flows to the command docs so operator-facing examples match the real runtime
- refreshed the system command guide to cover housekeeping scopes, `UCODE REPAIR STATUS`, UTC render boundaries, and open-box restore assumptions

**Implementation truth captured:**
- `docs/howto/UCODE-COMMAND-REFERENCE.md` now documents deterministic command, workflow, knowledge, and guidance routing with real `UCODE TEMPLATE`, `UCODE RESEARCH|ENRICH|GENERATE`, `WORKFLOW IMPORT RESEARCH`, and `BINDER IMPORT-RESEARCH` examples
- `docs/howto/commands/system.md` now describes the active v1.5 system/runtime contract instead of the older narrower system-command surface
- the remaining docs drift is now concentrated in older duplicated and lower-priority compatibility guides rather than the main operator entrypoints

**Next steps:**
1. collapse duplicated long-form specs/how-tos so each active v1.5 surface has one short canonical doc path
2. continue clearing lower-priority historical provider and compatibility docs outside the active runtime path

### 2026-03-04: v1.5 Legacy Helper Surface Refactor

**Status:** Completed

**Changes:**
- rewrote `wizard/check_provider_setup.py` around the v1.5 `logic_assist` plus `github` setup model instead of the retired Ollama installer and model-pull flow
- moved the Wizard interactive console from `ai`/Ollama helper wording to `logic`/GPT4All plus Wizard-network status and request handling
- replaced the old Ollama-backed `VibeService` implementation with a local GPT4All contributor helper that reads the shared logic-assist profile
- updated the seeded provider setup flags and provider-registry metadata so the helper layer stops resurfacing the retired local-model runtime

**Next steps:**
1. continue through the remaining deeper compatibility modules such as `ok_gateway`, `ucode` local-mode helpers, and provider health/admin surfaces
2. fold the same cleaned helper/runtime contract into the deeper `ucode` v1.5 TUI refactor

### 2026-03-04: v1.5 Documentation Contraction And Legacy How-To Cleanup

**Status:** Completed

**Changes:**
- moved retired offline `OK` setup/front-door docs and the old Wizard `OK` UI contract doc out of the active tree into `docs/.compost/historic/2026-03-04-retired-offline-ok-docs/`
- rewrote the remaining active graphics and workspace-transfer guides to point directly at the v1.5 installation, Dev extension, and logic-assist contract instead of the retired Ollama path
- updated active setup/help surfaces so `SETUP DEV`, local logic-assist tooling, and open-box portability are the current guidance rather than `SETUP VIBE` or legacy offline-assistant loops

**Next steps:**
1. continue removing lower-priority historical provider/runtime helpers that still mention Ollama or `assistant_keys.json`
2. carry the tightened active docs set into the deeper `ucode` v1.5 TUI refactor so help and runtime behavior stay aligned

### 2026-03-04: v1.5 Logic Assist Surface Cleanup

**Status:** Completed

**Changes:**
- added a dedicated `core/services/logic_assist_setup.py` installer/manager for the GPT4All local runtime and contributor tooling path
- upgraded live `SETUP`, self-heal, repair, and command-metadata surfaces to describe the v1.5 logic-assist contract instead of sending users toward Ollama or legacy `OK` labels
- moved the Config dashboard’s self-heal and local-model panels onto the GPT4All status/setup contract so active Wizard UI paths stop depending on retired Ollama flows
- normalized active Wizard config/setup status payloads and the live `ucode.py` assist route/output path so `LOGIC` and `/api/ucode/logic/*` are the visible contract in the current TUI lane

**Next steps:**
1. carry the same v1.5 logic-assist contract into the deeper `ucode` TUI element and flow-state refactor
2. retire lower-priority historical and compatibility surfaces that still mention Ollama or older `OK` terminology outside the active runtime path

### 2026-03-03: v1.5 Logic Assist Runtime Promotion

**Status:** Completed

**Changes:**
- replaced the active Wizard assist/runtime surface with the v1.5 logic-assist contract instead of keeping the old `OK` + Ollama route family as the primary path
- seeded a shared Markdown-backed `logic-assist` settings contract in the Typo workspace and started using it as the active provider/budget profile source
- upgraded the Wizard secret-store payload metadata and active `.env` guidance to the v1.5 GPT4All plus Wizard-network model
- moved the dashboard console and setup page onto `/api/logic` and `/api/ucode/logic` so the planned `ucode` TUI refactor can build on the new contract directly

**Implementation truth captured:**
- `wizard/services/logic_assist_service.py`, `wizard/services/local_model_gpt4all.py`, and `wizard/services/logic_assist_profile.py` now define the active local-assist, network-budget, and Markdown-profile runtime
- `wizard/routes/ai_routes.py`, `wizard/server.py`, `wizard/routes/ucode_routes.py`, and the dashboard console/setup surfaces now use the v1.5 logic-assist endpoints and status model
- the shared Typo workspace now seeds `settings/logic-assist.md` and `instructions/logic-assist.md` as the active operator-editable config/instruction contract
- active command-prompt and coding-assist helpers now speak `LOGIC`/GPT4All semantics rather than `OK`/Ollama framing

**Next steps:**
1. continue removing remaining legacy `OK`/Ollama management surfaces such as self-heal and older config panels that are outside the primary runtime path
2. fold the new logic-assist runtime directly into the upcoming `ucode` TUI refactor and standardized flow-state element work

### 2026-03-03: UTC Runtime And Local Render Boundary Extension

**Status:** Completed

**Changes:**
- extended the UTC/GMT contract from the first active runtime services into additional Wizard/core persistence surfaces
- added shared render-only timezone helpers so setup, ops, and TUI forms convert UTC to local display values through one code path
- removed remaining local timestamp persistence from monitoring, feed sync, quota tracking, and Wizard task state helpers

**Implementation truth captured:**
- `wizard/services/monitoring_manager.py`, `wizard/services/feed_sync.py`, `wizard/services/quota_tracker.py`, and `core/services/vibe_wizard_service.py` now persist UTC timestamps instead of local naive datetimes
- setup route timezone defaults, ops server-time metadata, and TUI date/time approval surfaces now render local time from shared UTC helpers at output time
- the UTC regression guard now covers these additional active services so they do not drift back to local persistence logic

**Next steps:**
1. continue the UTC cleanup through lower-priority historical services outside the active v1.5 runtime path
2. keep any new local timezone work inside UI/route render helpers instead of persistence or scheduler code

### 2026-03-03: UTC Secondary Service Sweep And Dashboard Render Alignment

**Status:** Completed

**Changes:**
- extended the shared UTC-to-local presentation helper into dashboard and monitoring route payloads
- aligned the shared TUI datetime-approval widget and fallback timezone detection to the same helper contract
- removed naive timestamp persistence from a second tier of Wizard side-state services including OCR metadata, extension activity, plugin discovery/index state, OAuth token storage, and mesh sync state

**Implementation truth captured:**
- dashboard and monitoring endpoints now publish shared `server_time` metadata rendered from UTC instead of hand-built local strings
- the form-field datetime widget now uses UTC-backed local rendering for current date/time/timezone defaults and clock display
- lower-priority service state files now store UTC timestamps through the same helper contract as the active runtime surfaces

**Next steps:**
1. continue into the remaining legacy routes/services such as beacon, port-manager, and historical integration helpers when they become active work
2. keep expanding the UTC guard lists as older side-state services are normalized

### 2026-03-03: UTC Beacon And Settings Surface Cleanup

**Status:** Completed

**Changes:**
- moved Beacon service persistence and route timestamps onto UTC helpers
- aligned settings metadata, workflow-manager side-state, and older Home Assistant API timestamps to the same UTC contract
- extended the secondary UTC guard coverage to cover these additional routes and services

**Implementation truth captured:**
- Beacon config updates, tunnel heartbeats/stats, cache records, and route responses no longer write naive local timestamps
- settings status, secret metadata, migration markers, and older service API timestamps now serialize UTC timestamps consistently
- route-side status calculations that compare timestamps now parse stored UTC values before computing age

**Next steps:**
1. take a dedicated pass through `wizard/services/port_manager.py` and the remaining legacy-heavy services that still mix local naive datetimes with persistence
2. keep TUI-facing human-readable timestamps routed through shared render helpers instead of inline `strftime` calls where practical

### 2026-03-03: UTC Legacy Management Surface Cleanup

**Status:** Completed

**Changes:**
- normalized the `port_manager` event/resource/operation lifecycle onto UTC-aware timestamps
- replaced older `utcfromtimestamp` and local export timestamp helpers in renderer/config admin routes with the shared UTC helpers
- expanded the UTC regression guard to cover these additional legacy management surfaces

**Implementation truth captured:**
- `wizard/services/port_manager.py` now uses UTC-aware datetimes for persisted events, resource snapshots, managed-process uptime, and background operations
- renderer file metadata and config export listings now derive serialized timestamps from the shared UTC helper path
- the remaining active legacy drift is now concentrated in narrower service families rather than spread across the management layer

**Next steps:**
1. continue through the remaining legacy-heavy services such as `config_routes`, `beacon_routes` adjacent helpers, and any older integration lanes still using `datetime.now()`
2. add targeted tests for `port_manager` serialization if that surface becomes part of the active release proof lane

### 2026-03-03: v1.5 Central Logging Contract Upgrade

**Status:** Completed

**Changes:**
- upgraded the shared logging contract marker to `udos-log-v1.5`
- added shared logging health/stats helpers at the core layer and exposed them through the Wizard wrapper and log routes
- folded another batch of legacy Wizard services onto the same UTC-safe logging and timestamp contract

**Implementation truth captured:**
- core and Wizard now report one `udos-log-v1.5` JSONL logging contract with shared health/stats metadata
- `/api/logs/status` can now report central logging health and log-tree stats without inventing a second route-local model
- config rotation, device auth, URL-to-Markdown, and OK gateway state paths now serialize UTC timestamps instead of naive local values

**Next steps:**
1. continue retiring the remaining legacy timestamp writers in lower-priority Wizard service families
2. expose the new logging health/stats payload in any operator-facing dashboard lane that still only shows raw files

### 2026-03-03: Empire Wizard Refactor Closure

**Status:** Completed

**Changes:**
- completed the active Empire Wizard extension surface with route-backed document review, import job detail, grouped template inventory, connector review, and webhook tooling
- removed the remaining placeholder import/template language from the Empire dashboard and aligned it to the real managed route flow
- expanded Empire template discovery to include mappings, workflows, and general template files under one extension inventory
- closed the current release-tracking gap by updating the roadmap and task tracker to treat Empire as a completed active lane rather than a partial placeholder

**Implementation truth captured:**
- Empire dashboard imports now review real documents and import jobs through `/api/empire`
- Empire templates now expose mapping and workflow inventory from the official extension tree
- Wizard route tests cover template kinds and document detail access in addition to the existing import, sync, and webhook surfaces
- Empire follow-on work now belongs under broader Wizard/workflow release closure instead of module-specific refactor cleanup

**Next steps:**
1. keep Empire aligned with the shared workflow/template standards as Round 4 and Round 5 continue
2. close the remaining Wizard-wide orchestration and release evidence work outside the Empire module itself

### 2026-03-03: Python Runtime Contract Consolidation

**Status:** Completed

**Changes:**
- standardized the active Python runtime direction on `uv` plus `/.venv`
- aligned launcher scripts and workspace settings away from legacy `venv/` references
- added a canonical Python runtime decision/spec pair and a root stdlib smoke lane
- kept pytest execution centralized in root `scripts/` while reinforcing `/dev/` as contributor governance only
- cleaned the remaining active repair/setup/help surfaces so Wizard and core now describe one shared Python runtime model

**Implementation truth captured:**
- `UCODE REPAIR STATUS` now reports Python runtime contract health
- `bin/ucode` no longer auto-installs Wizard extras on normal runtime launch
- root tooling now treats `/.venv` as the canonical local Python environment path
- Wizard repair/bootstrap flows now build and sync the shared `/.venv` via `uv`
- active docs and workspace tooling now point to one `uv`/`/.venv` operating model

**Next steps:**
1. tighten the stdlib boundary audit allowlist as legacy core exceptions are retired
2. keep archive and historical docs from being promoted back into active runtime guidance

### 2026-03-03: v1.5 Roadmap Rebaseline Consolidation

**Status:** Completed

**Changes:**
- rewrote the canonical roadmap around active v1.5 implementation rounds
- converted decision coverage into round-based release sequencing
- updated root tracking files from the stale v1.4.6 stabilization snapshot to the current v1.5 rebaseline
- aligned high-traffic command/example docs with the shipped `WORKFLOW` and `UCODE` command surfaces
- kept historical milestone detail out of the active roadmap and root task tracker

**Implementation truth captured:**
- core `WORKFLOW` runtime is live and tested
- `UCODE PROFILE`, `UCODE OPERATOR`, `UCODE EXTENSION`, `UCODE PACKAGE`, and `UCODE REPAIR STATUS` are live surfaces
- Wizard follow-on work is now tracked as an integration round rather than as speculative pre-implementation planning
- offline assist remains an active v1.5 lane, with the example scaffold treated as the current promotion source rather than as completed core runtime

**Next steps:**
1. complete the Round 1 shakedown checklist across the active specs catalog
2. harden core workflow and offline assist implementation slices
3. continue Wizard orchestration only on top of the canonical core workflow contract

### 2026-03-03: Logic Assist Final Spec Routed Into Deployment Roadmap

**Status:** Completed

**Changes:**
- promoted `docs/decisions/v1-5-logic-assist-final-spec.md` into the active v1.5 roadmap as a deployment-shaping decision rather than leaving it as a standalone note
- tied Round 2, Round 4, and Round 5 to the final logic-assist doctrine: deterministic `uLogic` authority, GPT4All local assist, and Wizard-only online budget control
- designated `docs/examples/udos_v1_5_deliverables/` as the deployment/reference framework for schemas, migration guidance, and v1.5 delivery artifacts

**Implementation truth captured:**
- offline logic promotion is now tracked against the final local-assist and Wizard-escalation contract
- Wizard orchestration is explicitly framed as the sole online routing and budget-control layer for v1.5
- the deliverables pack is now treated as the active framework for v1.5 deployment evidence, not as an orphan example set

**Next steps:**
1. promote the deliverables schemas and migration contract into canonical runtime validation where appropriate
2. align the upcoming TUI and workflow-manager implementation slices to the final logic-assist deployment contract

### 2026-03-03: Research/Enrich/Generate Spec Added To Active Rounds

**Status:** Completed

**Changes:**
- added `docs/decisions/v1-5-research-enrich-generate.md` to the active v1.5 rounds instead of leaving it outside the main release sequencing
- tied Round 2, Round 3, and Round 5 to one vault-first Markdown pipeline for ingestion, enrichment, transformation, and artifact generation
- aligned the roadmap language so non-Markdown formats remain ingestion sources or render targets, not canonical storage

**Implementation truth captured:**
- research and autonomous ingestion are now explicitly part of the offline logic and knowledge-foundation round
- cross-component template standardization now includes research summaries, guides, and generated deliverables
- TUI standardization now explicitly includes research/enrich/generate outputs as part of the one operator-facing flow

**Next steps:**
1. promote the deliverables schemas and migration contract into active upgrade/setup documentation
2. implement canonical runtime validation around the v1.5 deliverables schemas as the next bridge from docs to code

### 2026-03-03: Deliverables Validation And Research Pipeline Promotion

**Status:** Completed

**Changes:**
- promoted the v1.5 deliverables schemas into stdlib-only runtime validators under `core/ulogic/deliverables.py`
- added a deterministic research/enrich/generate pipeline slice under `core/ulogic/research_pipeline.py`
- extended the offline input parser to recognize explicit research and generate intents instead of collapsing everything into one generic knowledge action

**Implementation truth captured:**
- project, task, workflow, and Wizard budget deliverables now have a canonical validation surface in core
- research normalization now produces Markdown-canonical documents with stable ids and frontmatter
- enrichment and artifact generation now have a first deterministic implementation anchor for Round 2

**Next steps:**
1. wire the new deliverables validators into workflow and project runtime boundaries where those artifacts are created or loaded
2. connect the research/enrich/generate pipeline to real command or workflow entrypoints so operator flows can use it directly

### 2026-03-03: uCODE Research Implementation Round Closure

**Status:** Completed

**Changes:**
- wired the v1.5 deliverables validators into workflow creation/load checks and binder/project write paths instead of leaving them as standalone helpers
- extended the `UCODE` command surface with persistent `RESEARCH`, `ENRICH`, `GENERATE`, and `DELIVERABLE VALIDATE` entrypoints, plus `LIST` and `READ` operations for saved research artifacts
- completed the local knowledge-tree persistence path so research outputs are stored under `memory/bank/knowledge/user/` rather than returned as transient-only text

**Implementation truth captured:**
- workflow specs are now checked against the canonical v1.5 deliverables contract before scheduler persistence
- binder `project.json` and `tasks.json` writes now reject invalid payloads instead of silently accepting missing identifiers
- the deterministic research/enrich/generate pipeline is now operator-reachable from `ucode` and produces canonical Markdown artifacts with stable local storage paths

**Validation:**
- `python3.12 -m compileall core/ulogic core/commands/ucode_handler.py core/services/mission_templates.py core/services/vibe_binder_service.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ucode_min_spec_command_test.py core/tests/workflow_scheduler_test.py core/tests/ulogic_deliverables_test.py core/tests/ulogic_parser_test.py core/tests/deliverable_writer_validation_test.py`
- focused lane result: 42 tests passed

**Next steps:**
1. feed persisted research artifacts into `WORKFLOW` and binder flows directly instead of treating them as adjacent notes
2. carry the same deliverable validation pattern into any remaining project/task writers outside the current workflow and binder surfaces

### 2026-03-03: Research Artifact Workflow And Binder Integration

**Status:** Completed

**Changes:**
- added a shared core knowledge-artifact service to own saved research/enrich/generate Markdown files, binder/workflow imports, and `.compost` snapshot handling
- extended `WORKFLOW` with direct research import and `BINDER` with direct persisted research ingestion instead of leaving those notes outside the operator flow
- added direct `UCODE` cleanup hooks for saved research artifacts so the local knowledge tree uses the same `TIDY`/`CLEAN` lifecycle as the rest of the runtime
- promoted the deliverable validation pattern to `completed.json` so the binder file set is checked consistently across project, tasks, and completed outputs

**Implementation truth captured:**
- workflow runs now accept persisted research notes as imported workflow inputs with tracked metadata under workflow artifacts
- binder imports now copy research notes into binder-local research folders and create imported task records with source/snapshot metadata
- processed research files and overwritten local note versions now land in `/.compost/...` instead of being silently replaced or discarded
- research cleanup now routes through the existing maintenance contract rather than creating a second archive/trash path

**Validation:**
- `python3.12 -m compileall core/services/knowledge_artifact_service.py core/services/maintenance_utils.py core/services/mission_templates.py core/services/vibe_binder_service.py core/commands/ucode_handler.py core/commands/workflow_handler.py core/commands/binder_handler.py core/workflows/scheduler.py core/ulogic`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ucode_min_spec_command_test.py core/tests/workflow_scheduler_test.py core/tests/workflow_research_import_test.py core/tests/binder_research_import_test.py core/tests/ulogic_deliverables_test.py core/tests/ulogic_parser_test.py core/tests/deliverable_writer_validation_test.py`
- focused lane result: 45 tests passed

**Next steps:**
1. surface the new workflow/binder research import flows in the TUI help and high-traffic command docs
2. thread imported research artifacts into workflow phase execution and binder summarization beyond simple copy-and-link ingestion

### 2026-03-03: Housekeeping And Open-Box Lifecycle Alignment

**Status:** Completed

**Changes:**
- added scope-aware housekeeping for `repo`, `vault`, `knowledge`, and `dev` instead of treating cleanup as one generic operation
- made vault and knowledge cleanup Markdown-first so unsupported files are moved into `/.compost` while canonical `.md` plus companion/support files remain intact
- added elastic `.compost` pruning that now considers both age and duplicate-version overflow
- aligned the `DESTROY` help/recovery language to the v1.5 open-box rule: runtime can be reinstalled while persisted user data remains recoverable
- exposed the same housekeeping routine to Wizard’s managed scheduler for periodic runs

**Implementation truth captured:**
- `HEALTH CHECK housekeeping --scope ... [--apply]` now previews or applies scoped cleanup
- `TIDY/CLEAN vault|knowledge|dev` now use profile-aware file rules instead of blind directory wiping
- `/dev` housekeeping focuses on contributor work dirs and transient build/cache artifacts, not on runtime ownership
- `/.compost` now prunes older copies once enough newer versions of the same file exist, in addition to normal age-based cleanup

**Validation:**
- `python3.12 -m compileall core/services/maintenance_utils.py core/commands/health_handler.py core/commands/maintenance_handler.py core/commands/destroy_handler_helpers.py wizard/services/task_scheduler.py core/tests/maintenance_housekeeping_test.py core/tests/health_housekeeping_command_test.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/maintenance_housekeeping_test.py core/tests/health_housekeeping_command_test.py core/tests/health_release_gates_command_test.py core/tests/destructive_ops_test.py`
- focused lane result: 11 tests passed

**Next steps:**
1. expose the new housekeeping scopes in the TUI help surfaces and any matching Wizard ops pages
2. capture release evidence that `DESTROY`/`RESTORE` preserves user libraries across runtime reinstall

### 2026-03-03: UTC Runtime Time Contract Alignment

**Status:** Completed

**Changes:**
- expanded the shared time helpers so active runtime code has one UTC/GMT timestamp contract for iso strings, compact stamps, file/day labels, and parsing
- converted the active binder, mission-template, housekeeping, destroy-helper, logging, and Wizard task-scheduler paths away from naive local `datetime.now()` usage
- added a runtime guard test that blocks naive datetime calls in the UTC-critical persistence and scheduler surfaces

**Implementation truth captured:**
- persisted timestamps and scheduler comparisons now use UTC/GMT in the active runtime-critical files
- `.compost` day folders, archive stamps, and backup labels now derive from UTC instead of local wall-clock time
- local timezone handling is now treated as a UI/rendering concern rather than a persistence concern

**Validation:**
- `python3.12 -m compileall core/services/time_utils.py core/services/maintenance_utils.py core/services/knowledge_artifact_service.py core/services/mission_templates.py core/services/vibe_binder_service.py core/services/logging_api.py core/commands/destroy_handler_helpers.py wizard/services/task_scheduler.py core/tests/utc_runtime_contract_test.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/utc_runtime_contract_test.py core/tests/maintenance_housekeeping_test.py core/tests/health_housekeeping_command_test.py core/tests/deliverable_writer_validation_test.py core/tests/workflow_research_import_test.py core/tests/binder_research_import_test.py`
- focused lane result: 11 tests passed

**Next steps:**
1. continue the UTC cleanup through remaining historical Wizard/core services that still persist naive local timestamps
2. standardize explicit local-time rendering helpers in UI-facing routes and TUI surfaces so conversion happens in one presentation layer

### 2026-02-24: AGENTS.md Governance Standardisation (v1.4.6)

**Status:** Completed

**Changes:**
- implemented the OK Agent governance policy
- created root AGENTS governance and subsystem-scoped AGENTS files
- scaffolded governance templates in `/dev`
- updated binder seed templates with AGENTS, DEVLOG, and task tracking files
- created the initial root governance tracker set

### 2026-02-23: Testing Phase Verification

**Status:** Completed

**Changes:**
- verified the core and Wizard test baselines for the then-active stabilization milestone
- recorded milestone readiness in the historical devlog stream

---

End of Log
