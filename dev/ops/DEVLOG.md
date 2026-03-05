# DEVLOG.md — uDOS Development Log

Last Updated: 2026-03-04
Version: v1.5 rebaseline
Status: Active

---

## Purpose

This log tracks root-level milestone changes and release-tracking updates for the active repository state.

---

## Entries

### 2026-03-04: Phase 1 Self-Hosted `@dev` Runtime Handoff

**Status:** Completed

**Changes:**
- added one runtime-backed planning summary for Dev Mode so tracked contributor files now show their handoff into workflow and scheduler ownership instead of remaining a file browser only
- added workflow-plan sync from `dev/ops/workflows/` into the Wizard workflow manager, allowing tracked contributor plans to become runtime-managed task projects without inventing a parallel contributor executor
- exposed the same handoff through the standard `DEV` command surface with `DEV PLAN` and `DEV SYNC <workflow_plan>`

**Implementation truth captured:**
- `wizard/services/dev_mode_service.py` now reports tracked task-ledger summary, contributor workflow plans, scheduler templates, runtime workflow dashboard state, scheduler queue state, and can sync a contributor workflow plan into a runtime project
- `wizard/routes/dev_routes.py` now exposes `/api/dev/ops/planning` and `/api/dev/ops/workflows/sync` as the canonical Dev Mode planning handoff routes
- `wizard/dashboard/src/routes/DevMode.svelte` now surfaces the runtime planning handoff and allows workflow-plan sync from the Dev Mode GUI while `core/commands/dev_mode_handler.py` exposes the same path through `DEV PLAN` and `DEV SYNC`

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/dev_mode_handler_test.py dev/goblin/tests/test_dev_ops_routes.py`
- `npm run test -- DevMode.test.ts`

### 2026-03-04: v1.5 Stable Release Program Reframe

**Status:** Completed

**Changes:**
- reframed the active contributor roadmap from subsystem completion into release integration, certification, and demo-pack execution
- promoted the remaining release blockers into explicit tracked missions for self-hosting, local assist reliability, managed budget/rotation closure, demo `ucode` coverage, and final profile signoff
- added one contributor-facing stable release program document so roadmap, machine task state, and release sequencing stay aligned

**Implementation truth captured:**
- `dev/ops/tasks.md` now treats self-hosted `@dev`, local assist reliability, managed provider-budget scheduling closure, the demo pack, and stable signoff as the active Round 5 lanes
- `dev/ops/tasks.json` now mirrors those lanes as active missions instead of leaving machine-readable state on already-completed contributor consolidation work only
- `dev/docs/roadmap/ROADMAP.md` and `dev/docs/specs/V1-5-STABLE-RELEASE-PROGRAM.md` now define the phased path from current runtime consolidation into v1.5 stable release evidence

**Validation:**
- contributor planning/docs sync only; no runtime test command was required for this tracker update

### 2026-03-04: v1.5 Task And Workflow Format Helpers

**Status:** Completed

**Changes:**
- added one core-owned JSON formatter for contributor task ledgers, completed-milestone ledgers, workflow plans, and runtime workflow specs instead of leaving each surface to guess at formatting
- exposed the helper contract through `UCODE FORMAT`, the task/workflow Wizard APIs, and the `@dev` tracked editor metadata
- updated Goblin and core coverage so format-helper routing, write behavior, and task/workflow profile detection stay under regression protection

**Implementation truth captured:**
- `core/ulogic/format_helpers.py` now owns task/workflow profile detection, canonical key ordering, and helper-shape validation
- `core/commands/ucode_handler.py` and `core/tui/protocol_bridge.py` now expose and render the shared `UCODE FORMAT` helper contract
- `wizard/routes/task_routes.py`, `wizard/routes/workflow_routes.py`, and `wizard/services/dev_mode_service.py` now reuse the same formatter for API and `@dev` edit flows

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ulogic_format_helpers_test.py core/tests/ucode_min_spec_command_test.py core/tests/tui_protocol_bridge_test.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest wizard/tests/test_setup_and_tasks_api.py wizard/tests/workflow_routes_test.py dev/goblin/tests/test_dev_ops_routes.py dev/goblin/tests/test_dev_workspace_contract.py`

### 2026-03-04: Goblin Drain And Format Helper Closure

**Status:** Completed

**Changes:**
- completed the contributor overlay drain by moving the remaining scaffold and profile-policy assertions into Goblin and documenting the runtime-owned boundary left in Wizard
- finished the tracked editor helper contract so file types now advertise backend-owned format, normalize, or cleanup actions that match actual behavior
- updated the contributor roadmap and completion state to treat Goblin drain and format helpers as closed lanes

**Implementation truth captured:**
- `dev/goblin/tests/` now carries the contributor scaffold route, launcher workspace-selection, profile-gate, and tracked editor overlay assertions
- `wizard/services/dev_mode_service.py` now reports helper action modes and labels that distinguish formatting from normalization or whitespace cleanup
- `wizard/dashboard/src/routes/DevMode.svelte` surfaces those helper labels directly instead of assuming every normalize action is formatting

**Validation:**
- `npm run test -- DevMode.test.ts`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest dev/goblin/tests/test_dev_ops_routes.py dev/goblin/tests/test_dev_scaffold_platform_routes.py dev/goblin/tests/test_dev_extension_profile_gate.py dev/goblin/tests/test_udos_launcher_dev_workspace.py wizard/tests/udos_launcher_service_test.py`

**Next steps:**
1. move to the remaining release-evidence and certified-profile signoff lanes from the closed contributor baseline
2. expand Goblin fixtures only where new experimental overlays need tracked scenarios or test-vault payloads

### 2026-03-04: Contributor Scaffold Contract Alignment

**Status:** Completed

**Changes:**
- aligned the platform-facing contributor scaffold route to the canonical `DevExtensionService` framework contract instead of a partial hardcoded checklist
- expanded Goblin scaffold coverage to prove both complete and incomplete `@dev` payloads report the full required-file truth
- removed the remaining drift risk between Dev Mode framework policy and platform scaffold status output

**Implementation truth captured:**
- `wizard/routes/platform_routes.py` now sources `/api/platform/dev/scaffold` from `wizard.services.dev_extension_service`
- `dev/goblin/tests/test_dev_scaffold_platform_routes.py` now validates the full required-file set, tracked sync paths, and missing-file reporting
- the contributor scaffold now has one authoritative required-file contract across Wizard services and Goblin overlay checks

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest dev/goblin/tests/test_dev_scaffold_platform_routes.py`

**Next steps:**
1. keep any future scaffold status fields derived from `DevExtensionService` rather than route-local checklists
2. continue the remaining roadmap lanes from the now-complete contributor scaffold baseline

### 2026-03-04: Goblin Overlay Audit Boundary

**Status:** Completed

**Changes:**
- audited the remaining Dev-related Wizard tests after the latest Goblin drain
- confirmed the launcher workspace-selection and certified-profile Dev extension gate cases are the active contributor-overlay assertions now carried by Goblin
- documented that runtime dispatch/router tests which only branch on Dev Mode state stay in `wizard/tests` because they validate the primary runtime contract

**Implementation truth captured:**
- `wizard/tests/udos_launcher_service_test.py` now keeps the runtime-owned core workspace launch expectation
- `dev/goblin/tests/test_udos_launcher_dev_workspace.py` and `dev/goblin/tests/test_dev_extension_profile_gate.py` carry the contributor overlay policy checks
- `dev/goblin/tests/README.md` now states the boundary so future drain passes do not move runtime-owned dispatch coverage by mistake

**Validation:**
- audit only; no additional commands beyond the focused lane validation already captured for the moved tests

**Next steps:**
1. continue searching for contributor scaffold and policy assertions near release/profile wiring, not runtime dispatch code
2. keep future Goblin drains coupled to explicit boundary notes when a neighboring Wizard test remains runtime-owned

### 2026-03-04: `@dev` Format-Aware Save Helpers And Goblin Profile-Gate Drain

**Status:** Completed

**Changes:**
- added format-aware helper metadata to tracked file reads so the Dev Mode editor can describe validation and formatting actions per file type
- extended the tracked save route with an optional normalize-on-save path, letting contributors format and persist structured payloads in one guarded action
- moved the certified-profile Dev extension gate coverage out of `wizard/tests` and into Goblin as contributor overlay policy evidence

**Implementation truth captured:**
- `wizard/services/dev_mode_service.py` now returns per-file helper metadata and can persist formatted output through the same guarded `/api/dev/ops/write` contract
- `wizard/dashboard/src/routes/DevMode.svelte` now surfaces helper-aware copy plus a dedicated save-formatted action for editable tracked files
- `dev/goblin/tests/test_dev_extension_profile_gate.py` now carries the `@dev` extension profile-policy assertions while runtime-owned extension behavior remains under Wizard ownership

**Validation:**
- `npm run test -- DevMode.test.ts`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest dev/goblin/tests/test_dev_ops_routes.py dev/goblin/tests/test_dev_extension_profile_gate.py`

**Next steps:**
1. keep draining contributor-policy and scaffold-only assertions from `wizard/tests` where Wizard runtime ownership is not under test
2. consider broader helper actions only where they stay backend-authoritative and do not duplicate format logic in the GUI

### 2026-03-04: `@dev` Tracked Editor Round Closure

**Status:** Completed

**Changes:**
- consolidated the tracked-file upgrade lane into one guarded save path covering preview, nested navigation, editing, and validation
- extended backend validation beyond JSON into TOML, YAML, Python syntax, shell syntax, and Markdown fenced-code balance
- expanded Goblin contract coverage so the tracked write route now rejects malformed payloads across the remaining practical editable formats

**Implementation truth captured:**
- `wizard/services/dev_mode_service.py` is now the single authority for tracked write validation across `dev/ops`, `dev/docs`, and `dev/goblin`
- `/api/dev/ops/write` now rejects malformed JSON, TOML, YAML, Python, shell, and broken Markdown fence content before any write happens
- the Dev Mode GUI remains thin and surfaces backend validation detail instead of owning separate parser logic

**Validation:**
- `npm run test -- DevMode.test.ts`
- `python3 -m py_compile wizard/services/dev_mode_service.py wizard/routes/dev_routes.py dev/goblin/tests/test_dev_ops_routes.py`
- focused lane result: UI tests passed, Python syntax validation passed

**Next steps:**
1. add optional format/normalize actions for validated structured files where it improves contributor throughput
2. continue the Goblin overlay drain and broader release-evidence work from the canonical `@dev` baseline

### 2026-03-04: `@dev` JSON Edit Guardrails

**Status:** Completed

**Changes:**
- added JSON validation at the tracked-file write boundary so malformed `project.json`, `tasks.json`, `.code-workspace`, and similar payloads are rejected before save
- updated the Dev Mode save flow to surface structured backend validation details instead of only showing generic HTTP failure text
- extended Goblin route coverage and the dashboard UI test to cover invalid JSON save attempts

**Implementation truth captured:**
- `wizard/services/dev_mode_service.py` now validates JSON-like tracked files with `json.loads` before writing to disk
- `wizard/dashboard/src/routes/DevMode.svelte` now reads structured error payloads from `/api/dev/ops/write` and displays the validation message directly
- the tracked editing lane now has one authoritative backend guardrail rather than relying on UI-only assumptions

**Validation:**
- `npm run test -- DevMode.test.ts`
- `python3 -m py_compile wizard/services/dev_mode_service.py wizard/routes/dev_routes.py dev/goblin/tests/test_dev_ops_routes.py`
- focused lane result: UI tests passed, Python syntax validation passed

**Next steps:**
1. extend structured guardrails to other machine-readable file types where validation is cheap and authoritative
2. consider a small pre-save format/normalize action for JSON-like tracked files if the edit loop starts getting noisy

### 2026-03-04: `@dev` Nested Tracked Browser Navigation

**Status:** Completed

**Changes:**
- extended the Dev Mode tracked browser from first-level listings to nested directory navigation within `ops`, `docs`, and `goblin`
- added per-area `root` and `up` navigation controls so deeper tracked files can be reached without leaving the Dev Mode screen
- updated the dashboard route test so it proves nested navigation into `ops/templates/` before returning to root and reopening a tracked file

**Implementation truth captured:**
- the existing `/api/dev/ops/files?area=...&path=...` contract is now used as the canonical nested browser mechanism instead of inventing new backend surfaces
- `wizard/dashboard/src/routes/DevMode.svelte` now tracks current relative path per browser area and reloads only within the allowed `@dev` roots
- tracked editing still stays bounded to the same safe `ops|docs|goblin` roots and file types

**Validation:**
- `npm run test -- DevMode.test.ts`
- `python3 -m py_compile wizard/services/dev_mode_service.py wizard/routes/dev_routes.py dev/goblin/tests/test_dev_ops_routes.py`
- focused lane result: UI test passed, Python syntax validation passed

**Next steps:**
1. add structured-edit guardrails for JSON and other machine-readable tracked files before save
2. consider lightweight breadcrumbs or area-local history if deeper navigation starts getting heavy

### 2026-03-04: `@dev` Tracked File Editing

**Status:** Completed

**Changes:**
- added a safe tracked-file write path in the Dev Mode service and routes so the GUI can save text changes inside `dev/ops`, `dev/docs`, and `dev/goblin`
- upgraded the Dev Mode preview panel into an editable tracked-file surface with save-state feedback instead of read-only preview
- extended the Goblin route contract coverage to prove tracked text writes round-trip through the `/api/dev/ops/write` endpoint

**Implementation truth captured:**
- `wizard/services/dev_mode_service.py` now enforces tracked-root boundaries, text-only editing, and a size limit for Dev Mode writes
- `wizard/routes/dev_routes.py` now exposes `/api/dev/ops/write` as the canonical save endpoint for tracked contributor payloads
- `wizard/dashboard/src/routes/DevMode.svelte` now lets operators preview, edit, and save tracked text files without leaving the `@dev` screen

**Validation:**
- `npm run test -- DevMode.test.ts`
- `python3 -m py_compile wizard/services/dev_mode_service.py wizard/routes/dev_routes.py dev/goblin/tests/test_dev_ops_routes.py`
- focused lane result: UI test passed, Python syntax validation passed

**Next steps:**
1. extend the tracked browser from first-level listings to directory navigation within `ops`, `docs`, and `goblin`
2. add lightweight guardrails for structured edits such as JSON validation before save where that adds real value

### 2026-03-04: `@dev` Provisioning Round Closure And Goblin Overlay Drain

**Status:** Completed

**Changes:**
- removed the remaining contributor compatibility tracker files from repo root and `dev/`, leaving `dev/ops`, `dev/docs`, and `dev/goblin` as the only active contributor roots
- added clickable tracked-file preview in the Dev Mode GUI on top of `/api/dev/ops/read`, extending the browser support already exposed by `/api/dev/ops/files`
- moved more contributor-overlay coverage into Goblin, including Dev scaffold status, extension hot-reload, and launcher workspace-selection checks, while leaving runtime-owned coverage in `wizard/tests`
- updated the contributor roadmap, completion state, and Goblin docs to treat the provisioning round as closed and the overlay-drain lane as the next tracked task

**Implementation truth captured:**
- `wizard/dashboard/src/routes/DevMode.svelte` now previews tracked files from the canonical `@dev` payload instead of showing a list only
- `dev/goblin/tests/` is now the home for `@dev` browser/read contracts, contributor scaffold route checks, extension overlay checks, and launcher workspace-selection coverage
- `wizard/tests/` keeps the runtime-owned launcher/session behavior while Goblin carries the contributor overlay assertions

**Validation:**
- `npm run test -- DevMode.test.ts`
- `python3 -m py_compile dev/goblin/tests/test_dev_ops_routes.py dev/goblin/tests/test_dev_extension_hot_reload_routes.py dev/goblin/tests/test_dev_scaffold_platform_routes.py dev/goblin/tests/test_udos_launcher_dev_workspace.py wizard/tests/udos_launcher_service_test.py`
- focused lane result: UI test passed, Python syntax validation passed for the touched files

**Next steps:**
1. continue draining remaining contributor-overlay checks from `wizard/tests` where the behavior is about the scaffold rather than Wizard runtime ownership
2. extend the Dev Mode file browser from preview into safe tracked-file editing flows for `dev/ops`, `dev/docs`, and Goblin fixtures

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
- removed the remaining active local-runtime adapter bootstrap from the TUI provider registration path and updated Wizard page routing to use the v1.5 logic endpoints instead of `/api/ai/*`

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
- rewrote `wizard/check_provider_setup.py` around the v1.5 `logic_assist` plus `github` setup model instead of the retired local-runtime installer and model-pull flow
- moved the Wizard interactive console from older local-runtime helper wording to `logic`/GPT4All plus Wizard-network status and request handling
- replaced the old local-runtime-backed `VibeService` implementation with a local GPT4All contributor helper that reads the shared logic-assist profile
- updated the seeded provider setup flags and provider-registry metadata so the helper layer stops resurfacing the retired local-model runtime

**Next steps:**
1. continue through the remaining deeper compatibility modules such as `ok_gateway`, `ucode` local-mode helpers, and provider health/admin surfaces
2. fold the same cleaned helper/runtime contract into the deeper `ucode` v1.5 TUI refactor

### 2026-03-04: v1.5 Documentation Contraction And Legacy How-To Cleanup

**Status:** Completed

**Changes:**
- moved retired offline `OK` setup/front-door docs and the old Wizard `OK` UI contract doc out of the active tree into `docs/.compost/historic/2026-03-04-retired-offline-ok-docs/`
- rewrote the remaining active graphics and workspace-transfer guides to point directly at the v1.5 installation, Dev extension, and logic-assist contract instead of the retired local-runtime path
- updated active setup/help surfaces so `SETUP DEV`, local logic-assist tooling, and open-box portability are the current guidance rather than `SETUP VIBE` or legacy offline-assistant loops

**Next steps:**
1. continue removing lower-priority historical provider/runtime helpers that still mention the retired local runtime or `assistant_keys.json`
2. carry the tightened active docs set into the deeper `ucode` v1.5 TUI refactor so help and runtime behavior stay aligned

### 2026-03-04: v1.5 Logic Assist Surface Cleanup

**Status:** Completed

**Changes:**
- added a dedicated `core/services/logic_assist_setup.py` installer/manager for the GPT4All local runtime and contributor tooling path
- upgraded live `SETUP`, self-heal, repair, and command-metadata surfaces to describe the v1.5 logic-assist contract instead of sending users toward the retired local runtime or legacy `OK` labels
- moved the Config dashboard’s self-heal and local-model panels onto the GPT4All status/setup contract so active Wizard UI paths stop depending on retired local-runtime flows
- normalized active Wizard config/setup status payloads and the live `ucode.py` assist route/output path so `LOGIC` and `/api/ucode/logic/*` are the visible contract in the current TUI lane

**Next steps:**
1. carry the same v1.5 logic-assist contract into the deeper `ucode` TUI element and flow-state refactor
2. retire lower-priority historical and compatibility surfaces that still mention the retired local runtime or older `OK` terminology outside the active runtime path

### 2026-03-03: v1.5 Logic Assist Runtime Promotion

**Status:** Completed

**Changes:**
- replaced the active Wizard assist/runtime surface with the v1.5 logic-assist contract instead of keeping the old `OK` + local-runtime route family as the primary path
- seeded a shared Markdown-backed `logic-assist` settings contract in the Typo workspace and started using it as the active provider/budget profile source
- upgraded the Wizard secret-store payload metadata and active `.env` guidance to the v1.5 GPT4All plus Wizard-network model
- moved the dashboard console and setup page onto `/api/logic` and `/api/ucode/logic` so the planned `ucode` TUI refactor can build on the new contract directly

**Implementation truth captured:**
- `wizard/services/logic_assist_service.py`, `wizard/services/local_model_gpt4all.py`, and `wizard/services/logic_assist_profile.py` now define the active local-assist, network-budget, and Markdown-profile runtime
- `wizard/routes/ai_routes.py`, `wizard/server.py`, `wizard/routes/ucode_routes.py`, and the dashboard console/setup surfaces now use the v1.5 logic-assist endpoints and status model
- the shared Typo workspace now seeds `settings/logic-assist.md` and `instructions/logic-assist.md` as the active operator-editable config/instruction contract
- active command-prompt and coding-assist helpers now speak `LOGIC`/GPT4All semantics rather than `OK`/older local-runtime framing

**Next steps:**
1. continue removing remaining legacy `OK`/local-runtime management surfaces such as self-heal and older config panels that are outside the primary runtime path
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

### 2026-03-04: Phase 1 Self-Hosted @dev Loop Closure

**Status:** Completed

**Changes:**
- closed the self-hosted `@dev` loop by extending the runtime planning handoff into executable controls instead of summary-only visibility
- added Wizard route/service coverage for scheduler-template registration, workflow-plan run/start, and runtime task-status updates against synced `@dev` workflow plans
- exposed the same actions through standard `DEV` commands so the contributor loop stays inside canonical `ucode`/Wizard boundaries
- extended the Dev Mode dashboard handoff panel so contributors can sync plans, register scheduler templates, run workflow tasks, and update runtime task state from the tracked `@dev` lane

**Implementation truth captured:**
- tracked workflow plans under `dev/ops/workflows/` now promote into runtime-owned workflow projects and can be run from both Dev Mode and `DEV RUN <workflow_plan>`
- tracked scheduler templates under `dev/ops/scheduler/` can now register runtime scheduler tasks tied to synced `@dev` workflow projects through both Dev Mode and `DEV SCHEDULE <template> <workflow_plan>`
- runtime task state for synced `@dev` projects is now operable through both the Dev Mode planning panel and `DEV TASK <workflow_plan> <task_id> <status>`
- the scheduler now recognizes `dev_scheduler:*` task kinds and starts the linked runtime workflow project instead of storing dead metadata

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/dev_mode_handler_test.py dev/goblin/tests/test_dev_ops_routes.py`
- `npm run test -- DevMode.test.ts`
- focused lane result: 30 tests passed

**Next steps:**
1. start Phase 2 by hardening the local conversation engine defaults, knowledge bundle, and offline assist reliability evidence
2. use the closed `@dev` loop as the execution lane for the remaining v1.5 stable work instead of adding more ad hoc contributor flows

### 2026-03-04: Phase 2 Local Assist Reliability Slice 1

**Status:** In Progress

**Changes:**
- strengthened the local logic-assist runtime so requests now assemble a stable effective prompt from the OK profile, workspace-aware context bundle, and recent conversation turns
- added persisted conversation carry-over for repeated local assist requests so `@dev` and other workspaces can keep short operational context without inventing a separate chat store
- enforced offline-required behavior when the local runtime is unavailable and added explicit local-to-network fallback when local generation fails but policy allows Wizard escalation
- fixed the provider status surface so `gpt4all` local runtime status is served consistently through `/api/providers/{provider_id}/status`

**Implementation truth captured:**
- `wizard/services/ok_context_store.py` now builds workspace-aware context bundles and hashes them so assist calls can bind to concrete uDOS/`ucode` guidance inputs
- `wizard/services/logic_assist_service.py` now records conversation events, reuses recent turns, includes context metadata in routing, and avoids stale cache keys that ignored the effective prompt contract
- offline-required requests now fail fast on missing local readiness instead of silently drifting to network behavior
- local generation failure now falls back to Wizard network execution only when policy allows it, and the returned route records that fallback reason

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest wizard/tests/logic_assist_service_test.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest wizard/tests/logic_assist_service_test.py wizard/tests/provider_health_routes_test.py wizard/tests/ucode_ok_mode_utils_test.py`
- `python3 -m compileall wizard/services/logic_assist_service.py wizard/services/ok_context_store.py wizard/routes/provider_routes.py wizard/tests/logic_assist_service_test.py`
- focused lane result: 10 tests passed

**Next steps:**
1. expose conversation/context readiness more clearly in operator-facing Wizard and `ucode` status surfaces
2. tighten local model bootstrap defaults and install-state evidence so the offline path is dependable without manual recovery
3. add proof that the local assist output stays aligned to active uDOS and `ucode` standards in the planned demo pack and release evidence

### 2026-03-04: Phase 2 Local Assist Reliability Slice 2

**Status:** In Progress

**Changes:**
- promoted the new local assist reliability details into the standard `ucode`/Wizard status helpers instead of leaving them buried inside the raw service payload
- extended local logic status to report context hash, context file count, stored conversation count, and cache entry count alongside the existing readiness/model fields
- kept the provider health surface aligned by preserving the `gpt4all` local-runtime status contract through the generic provider status route

**Implementation truth captured:**
- `wizard/services/logic_assist_service.py` now reports context, conversation-store, and cache metrics in `get_status()`
- `wizard/routes/ucode_ok_mode_utils.py` and `wizard/routes/ucode_logic_mode_utils.py` now carry those metrics into the operator-facing logic status payloads
- `/api/ucode/logic/status` now exposes the same reliability metadata used by the local assist runtime, so the operator can see whether context and conversation state are actually present

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest wizard/tests/logic_assist_service_test.py wizard/tests/ucode_ok_mode_utils_test.py wizard/tests/ucode_ok_routes_test.py wizard/tests/provider_health_routes_test.py`
- `python3 -m compileall wizard/routes/ucode_ok_mode_utils.py wizard/routes/ucode_logic_mode_utils.py wizard/tests/ucode_ok_mode_utils_test.py wizard/tests/ucode_ok_routes_test.py`
- focused lane result: 14 tests passed

**Next steps:**
1. tighten GPT4All bootstrap/install-state evidence so the local lane is dependable after setup and repair, not just observable
2. add release proof that local assist output stays aligned to active uDOS governance and `ucode` standards under `@dev` and core workspaces

### 2026-03-04: Phase 2 Local Assist Reliability Slice 3

**Status:** In Progress

**Changes:**
- aligned GPT4All bootstrap/install-state reporting across the local runtime, setup helper, provider health surface, and self-heal routes
- extended the local runtime status to report model directory, guidance file path, and guidance presence in addition to package/model readiness
- updated logic-assist setup so it returns structured install-state evidence after preparing the model directory and guidance file
- updated self-heal recovery/status output so operator guidance now points to the concrete model and guidance paths instead of only generic failure messages

**Implementation truth captured:**
- `wizard/services/local_model_gpt4all.py` now reports `model_dir`, `guidance_path`, and `guidance_present` as part of the canonical GPT4All status payload
- `core/services/logic_assist_setup.py` now exposes `inspect_logic_assist_setup()` and returns a structured `status` block from setup runs
- `wizard/routes/self_heal_routes.py` now includes the same GPT4All bootstrap evidence in model-asset checks, next-step guidance, and setup completion output

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/logic_assist_setup_test.py core/tests/self_healer_boundary_test.py wizard/tests/self_heal_routes_recovery_test.py wizard/tests/provider_health_routes_test.py wizard/tests/logic_assist_service_test.py`
- `python3 -m compileall core/services/logic_assist_setup.py wizard/services/local_model_gpt4all.py wizard/routes/self_heal_routes.py core/tests/logic_assist_setup_test.py`
- focused lane result: 15 tests passed

**Next steps:**
1. add release-proof tests that the local assist output stays aligned to active uDOS governance and `ucode` standards under both `core` and `@dev`
2. then move that proof into the demo `ucode` pack so Phase 2 can close on behavior evidence instead of infrastructure evidence alone

### 2026-03-04: Phase 2 Local Assist Reliability Closure

**Status:** Completed

**Changes:**
- closed the local assist reliability lane with behavior-level proof instead of stopping at health/readiness reporting
- updated the local prompt contract so condensed governance excerpts from the active context bundle are included in the local assist system prompt
- added focused tests proving the local assist sees root governance plus `core` constraints under `core`, and root governance plus `@dev`/ops rules under `@dev`

**Implementation truth captured:**
- the local GPT4All lane now receives active governance content, not just context hashes and file names
- the `core` prompt path now carries root branding and architecture constraints together with core-specific runtime restrictions
- the `@dev` prompt path now carries root governance plus contributor/runtime-boundary rules for the self-hosted dev lane

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest wizard/tests/logic_assist_service_test.py wizard/tests/ucode_ok_mode_utils_test.py wizard/tests/ucode_ok_routes_test.py wizard/tests/provider_health_routes_test.py`
- `python3 -m compileall wizard/services/logic_assist_service.py wizard/tests/logic_assist_service_test.py`
- focused lane result: 16 tests passed

**Next steps:**
1. move to Phase 3 and certify provider rotation, budget policy, and task-scheduler handoff as one managed contract
2. start building the demo `ucode` pack against the now-closed self-hosted and local-assist lanes

### 2026-03-04: Phase 3 Managed Budget, Rotation, and Scheduler Slice 1

**Status:** In Progress

**Changes:**
- started the integrated managed-operations closure pass by sharing quota truth between cloud-provider failover and queued task execution
- made cloud fallback planning operator-visible with per-provider readiness, quota eligibility, and detailed failover attempt reporting
- tightened scheduler gating so queued work now honors mapped provider quota before execution and preserves defer semantics for budget exhaustion and workflow wait states
- fixed two scheduler contract bugs uncovered by the new slice: queued task rows were dropping `provider`, and scheduler settings normalization was silently rewriting `off_peak_start_hour=0` back to the default window

**Implementation truth captured:**
- `wizard/services/cloud_provider_executor.py` now exposes a quota-aware execution plan and detailed failover report instead of only a coarse ready/not-ready result
- `wizard/services/task_scheduler.py` now carries provider identity through queue reads, applies quota checks during budget gating, and correctly preserves midnight-based off-peak windows
- `wizard/routes/ops_routes.py` now exposes the same managed-operations contract in runtime/config payloads, including cloud execution readiness, quota status, scheduler budget, and defer-reason state
- the managed queue path now has focused proof for quota-blocked network tasks, workflow-phase deferral, retry-safe deferred work, and ops-facing scheduler status/config surfaces

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest wizard/tests/cloud_provider_executor_test.py wizard/tests/task_scheduler_windows_test.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest wizard/tests/maintenance_job_test.py wizard/tests/ops_routes_test.py`
- `python3 -m compileall wizard/services/cloud_provider_executor.py wizard/services/task_scheduler.py wizard/tests/cloud_provider_executor_test.py wizard/tests/task_scheduler_windows_test.py wizard/tests/maintenance_job_test.py wizard/tests/ops_routes_test.py`
- focused lane result: 27 tests passed

**Next steps:**
1. add one end-to-end release proof that scheduled work and prompt-driven cloud work report the same provider/budget contract
2. then decide whether Phase 3 can close or still needs a dedicated demo `ucode` proof surface before signoff

### 2026-03-04: Phase 3 Managed Budget, Rotation, and Scheduler Slice 2

**Status:** In Progress

**Changes:**
- extended the prompt-driven `logic` status helpers so they stop dropping quota-aware planner fields such as blocked providers, quota-ready providers, provider readiness details, and estimated token planning
- added one shared-contract proof that the same quota-blocked provider state appears in both the prompt-driven `logic/status` surface and the queued-work ops runtime/config payloads
- kept the proof narrow by reusing the existing status routes instead of inventing a new release-only status endpoint

**Implementation truth captured:**
- `wizard/routes/ucode_logic_mode_utils.py` now preserves the quota-aware planner metadata already produced by the underlying logic-assist/network status
- `wizard/tests/ucode_ok_routes_test.py` now proves the prompt-driven `logic/status` surface carries blocked-provider, quota-ready, and provider-detail data through to the uCODE route payload
- `wizard/tests/ops_routes_test.py` now proves the ops planning/config runtime surfaces carry the same managed-operations contract for queued work

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest wizard/tests/ucode_ok_routes_test.py wizard/tests/ops_routes_test.py wizard/tests/cloud_provider_executor_test.py wizard/tests/task_scheduler_windows_test.py wizard/tests/maintenance_job_test.py`
- `python3 -m compileall wizard/routes/ucode_logic_mode_utils.py wizard/tests/ucode_ok_routes_test.py wizard/tests/ops_routes_test.py`
- focused lane result: 32 tests passed

**Next steps:**
1. decide whether to close Phase 3 now or require one demo `ucode` script as the final operator-visible proof before closure
2. if Phase 3 stays open, the next concrete move is to start the demo pack and use the managed budget/scheduler lane as demo `03`

### 2026-03-04: Phase 3 Managed Budget, Rotation, and Scheduler Closure

**Status:** Completed

**Changes:**
- closed the managed-operations lane with a stricter runtime proof through the real mounted route stack instead of stopping at helper-level status assertions
- added one integrated test that mounts both `/api/ucode` and `/api/ops` and proves prompt-driven logic status and queued-work ops status surfaces report the same quota-blocked provider contract
- carried the managed budget/scheduler contract forward into the release demo pack as canonical demo `03`

**Implementation truth captured:**
- `wizard/tests/managed_operations_runtime_contract_test.py` now proves `/api/ucode/logic/status`, `/api/ops/planning/jobs`, and `/api/ops/config/status` agree on blocked providers, quota-ready providers, primary provider, and quota status under one shared runtime contract
- the Phase 3 lane now has service, route, and mounted-runtime evidence instead of component-level proof only
- the managed budget/scheduler closure is now treated as release-ready input to the demo pack rather than an open integration lane

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest wizard/tests/managed_operations_runtime_contract_test.py wizard/tests/ucode_ok_routes_test.py wizard/tests/ops_routes_test.py wizard/tests/cloud_provider_executor_test.py wizard/tests/task_scheduler_windows_test.py wizard/tests/maintenance_job_test.py`
- `python3 -m compileall wizard/tests/managed_operations_runtime_contract_test.py`
- focused lane result: 33 tests passed

**Next steps:**
1. start the extensive demo pack round with the five checked-in release demos as the working baseline
2. tighten each demo against certified profile evidence until the pack is runnable release proof instead of script scaffolding alone

### 2026-03-04: Phase 4 Demo Pack Slice 1

**Status:** In Progress

**Changes:**
- created the canonical v1.5 release demo pack under `docs/examples/ucode_v1_5_release_pack/`
- added the five roadmap-defined demos covering setup/status, local assist/knowledge, workflow/task planning, managed scheduler/budget, and self-hosted `@dev`
- added one structural validation test so the release pack cannot silently lose a demo file or required sections

**Implementation truth captured:**
- `docs/examples/ucode_v1_5_release_pack/README.md` now defines the demo index, profile matrix, and validation entrypoints for the pack
- each checked-in demo now includes goal, target profiles, transcript, expected output/artifacts, and validation references
- `core/tests/ucode_release_demo_pack_test.py` now guards the pack inventory and required demo sections

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ucode_release_demo_pack_test.py wizard/tests/managed_operations_runtime_contract_test.py`
- `python3 -m compileall core/tests/ucode_release_demo_pack_test.py`
- focused lane result: 4 tests passed

**Next steps:**
1. turn the checked-in demo transcripts into profile-certified release evidence by executing and tightening them one by one
2. start with demo `00` and demo `03`, because they anchor setup truth and managed-operations truth for the rest of the pack

### 2026-03-04: Phase 4 Demo Pack Slice 2

**Status:** In Progress

**Changes:**
- turned the first two release demos into runnable Python artifacts instead of leaving them as transcript-only Markdown
- added a shared demo runtime harness that mounts the real `/api/ucode` and `/api/ops` routes against controlled release-demo state under `.artifacts/release-demos/`
- wired demo `00` and demo `03` to emit checked JSON reports and added focused tests that prove those reports carry the expected setup/managed-operations contract

**Implementation truth captured:**
- `docs/examples/ucode_v1_5_release_pack/scripts/demo_runtime.py` now provides the shared release-demo app/runtime harness, including controlled cloud/quota state and isolated runtime roots
- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_00_setup_and_status.py` now generates a setup/status report covering `logic/status`, ops config, ops jobs, and releases overview
- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_03_managed_scheduler_and_budget.py` now drives a real scheduler defer path and captures the matching `logic`/ops managed-operations surfaces in one report
- `core/tests/ucode_release_demo_scripts_test.py` now verifies the runnable demo reports for demos `00` and `03`

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ucode_release_demo_pack_test.py core/tests/ucode_release_demo_scripts_test.py wizard/tests/managed_operations_runtime_contract_test.py`
- `python3 -m compileall docs/examples/ucode_v1_5_release_pack/scripts core/tests/ucode_release_demo_scripts_test.py`
- focused lane result: 6 tests passed

**Next steps:**
1. add runnable demo scripts for `01-local-assist-and-knowledge`, `02-workflow-and-task-planning`, and `04-self-hosted-dev-mode`
2. then start tightening the whole pack against certified profile evidence instead of demo-operator scaffolding alone

### 2026-03-04: Phase 4 Demo Pack Slice 3

**Status:** In Progress

**Changes:**
- completed the coding round for the release demo pack by adding runnable scripts for demos `01`, `02`, and `04`
- extended the focused demo-script test suite so all five canonical demos now produce checked reports
- updated the pack docs so every canonical demo lists its runnable script entrypoint

**Implementation truth captured:**
- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_01_local_assist_and_knowledge.py` now records offline local-assist status, response routing, and conversation persistence evidence
- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_02_workflow_and_task_planning.py` now records workflow creation, phase execution, approval handoff, and artifact creation under an isolated workflow root
- `docs/examples/ucode_v1_5_release_pack/scripts/run_demo_04_self_hosted_dev_mode.py` now records the self-hosted `@dev` loop through planning summary, workflow sync, scheduler registration, workflow run, and runtime task-state update
- `core/tests/ucode_release_demo_scripts_test.py` now covers all five runnable demo reports

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ucode_release_demo_pack_test.py core/tests/ucode_release_demo_scripts_test.py`
- `python3 -m compileall docs/examples/ucode_v1_5_release_pack/scripts core/tests/ucode_release_demo_scripts_test.py`
- focused lane result: 8 tests passed

**Next steps:**
1. move from demo coding into demo certification by running these scripts against the real target profiles and tightening any profile-specific gaps
2. start recording certified profile evidence for `core`, `home`, `creator`, `gaming`, and `dev` against the runnable pack

### 2026-03-04: Phase 4 Demo Certification And Final Lane Entry

**Status:** Completed

**Changes:**
- certified all five runnable release demos against the canonical `uv` + `/.venv` runtime and recorded their generated reports under `.artifacts/release-demos/`
- fixed two release-grade issues found during certification: the demo CLI entrypoints now bootstrap the repo root correctly, and the self-hosted `@dev` handoff now normalizes repo-root paths before computing tracked workflow-plan paths
- moved the release program into the final signoff lane with checked-in certification docs/JSON, updated public status, and aligned root runtime metadata to `v1.5.0` beta instead of the stale `v1.4.0` stable record

**Implementation truth captured:**
- `docs/examples/ucode_v1_5_release_pack/CERTIFICATION.md` and `docs/examples/ucode_v1_5_release_pack/certification.json` now bind the five canonical demos to their target profiles, generated artifacts, focused validation commands, and profile-coverage truth
- `core/tests/ucode_release_demo_pack_test.py` and `core/tests/ucode_release_demo_scripts_test.py` now guard both the certification inventory and direct CLI execution of all five demo scripts
- `wizard/services/dev_mode_service.py` now resolves the repo root on construction so isolated runtime roots and tracked `@dev` workflow-plan paths remain consistent during sync and scheduler registration

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_00_setup_and_status.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_01_local_assist_and_knowledge.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_02_workflow_and_task_planning.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_03_managed_scheduler_and_budget.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_04_self_hosted_dev_mode.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ucode_release_demo_pack_test.py core/tests/ucode_release_demo_scripts_test.py core/tests/dev_mode_handler_test.py wizard/tests/managed_operations_runtime_contract_test.py wizard/tests/logic_assist_service_test.py wizard/tests/provider_health_routes_test.py wizard/tests/self_heal_routes_recovery_test.py wizard/tests/ucode_ok_mode_utils_test.py wizard/tests/ucode_ok_routes_test.py wizard/tests/cloud_provider_executor_test.py wizard/tests/task_scheduler_windows_test.py wizard/tests/maintenance_job_test.py wizard/tests/ops_routes_test.py wizard/tests/workflow_routes_test.py dev/goblin/tests/test_dev_ops_routes.py`

**Next steps:**
1. persist install-state evidence for `creator`, `gaming`, and `dev` through the certified profile flow instead of verify-only status
2. record repair and rollback evidence for `core`, `home`, `creator`, `gaming`, and `dev`
3. publish the final freeze summary naming the exact demos, profile evidence, local assist baseline, and managed-operations proof used for stable release

### 2026-03-04: Final Lane Profile Signoff Closure

**Status:** Completed

**Changes:**
- persisted install-state for `creator`, `gaming`, and `dev` through the canonical release-profile CLI so all five certified profiles are now installed and enabled in `memory/ucode/release-profiles.json`
- added one checked-in stable-signoff matrix in Markdown and JSON that records install, verify, repair, and rollback-or-recovery evidence per certified profile
- strengthened the core evidence surface with explicit optional-profile disable/enable recovery tests and a guard test that the stable-signoff artifact matches the current persisted profile state

**Implementation truth captured:**
- `docs/specs/V1-5-STABLE-SIGNOFF.md` and `docs/specs/V1-5-STABLE-SIGNOFF.json` now tie the final-lane evidence to the certified profile registry, current install state, demo coverage, shared repair contract, and home rollback-token evidence
- `memory/ucode/release-profiles.json` now records `core`, `home`, `creator`, `gaming`, and `dev` as both installed and enabled
- `core/tests/release_profile_service_test.py`, `core/tests/ucode_min_spec_command_test.py`, and `core/tests/v1_5_stable_signoff_test.py` now cover recovery semantics, mandatory-profile guardrails, and signoff/state alignment

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m core.services.release_profile_cli install --repo-root /Users/fredbook/Code/uDOS --profiles creator,gaming,dev`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/release_profile_service_test.py core/tests/ucode_min_spec_command_test.py core/tests/v1_5_stable_signoff_test.py core/tests/sonic_uhome_bundle_test.py`

**Next steps:**
1. publish the final freeze summary and release-readiness brief
2. decide when to flip `version.json` from `beta` to `stable` for the release cut

### 2026-03-04: Repo Backlog Closure And Freeze Summary

**Status:** Completed

**Changes:**
- closed the remaining v1.5 repo backlog lanes by promoting the deterministic offline runtime primitives from the `udos_ulogic_pack` reference scaffold into `core/ulogic/`
- implemented the Sonic seeded-catalog submission and contributor approval flow across the core service, `SONIC SUBMISSION` command surface, and Wizard review routes
- aligned the shipped command/example docs to the certified release pack, profile maintenance surfaces, Sonic review flow, and canonical `uv` + `/.venv` runtime
- published the final freeze summary naming the exact demos, profiles, local assist baseline, managed-operations proof, home-lane bridge evidence, and the remaining cut decision boundary

**Implementation truth captured:**
- `core/ulogic/action_graph.py`, `core/ulogic/runtime.py`, `core/ulogic/state_store.py`, `core/ulogic/artifact_store.py`, and `core/ulogic/script_sandbox.py` now hold the promoted deterministic offline runtime primitives guarded by `core/tests/ulogic_runtime_test.py`
- `core/services/sonic_device_service.py`, `core/commands/sonic_handler.py`, and `wizard/routes/sonic_plugin_routes.py` now implement local Sonic submission queueing plus contributor approve/reject review with coverage in `core/tests/sonic_device_service_test.py`, `core/tests/test_sonic_handler.py`, and `wizard/tests/sonic_submission_routes_test.py`
- `docs/specs/V1-5-FREEZE-SUMMARY.md` and `docs/specs/V1-5-FREEZE-SUMMARY.json` are now the canonical freeze-readiness brief for the stable cut decision

**Validation:**
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ulogic_runtime_test.py core/tests/ulogic_parser_test.py core/tests/ulogic_deliverables_test.py`
- `UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/sonic_device_service_test.py core/tests/test_sonic_handler.py wizard/tests/sonic_submission_routes_test.py wizard/tests/sonic_plugin_alias_routes_test.py`
- `python3 -m compileall core/ulogic core/services/sonic_device_service.py core/commands/sonic_handler.py wizard/routes/sonic_plugin_routes.py wizard/tests/sonic_submission_routes_test.py`

**Next steps:**
1. decide when to flip `version.json` from `beta` to `stable`
2. cut the release when that metadata transition is approved

### 2026-03-04: Stable Metadata Cutover

**Status:** Completed

**Changes:**
- updated canonical release metadata from `beta` to `stable`
- aligned public status, freeze summary, stable-signoff artifacts, and release-pack certification notes to the stable release truth

**Implementation truth captured:**
- `version.json` now reports `v1.5.0` on the `stable` channel
- `docs/STATUS.md`, `docs/specs/V1-5-FREEZE-SUMMARY.md`, `docs/specs/V1-5-STABLE-SIGNOFF.md`, and the release-pack certification artifacts now match the stable cut

**Validation:**
- `python3 -m json.tool version.json >/dev/null`
- `python3 -m json.tool docs/specs/V1-5-FREEZE-SUMMARY.json >/dev/null`
- `python3 -m json.tool docs/specs/V1-5-STABLE-SIGNOFF.json >/dev/null`

**Next steps:**
1. publish or tag the release if distribution metadata also needs a cut

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
