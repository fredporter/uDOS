# uDOS Roadmap (Canonical)

Last updated: 2026-02-20 (v1.4.7 Stable Release planning)

This file is the single canonical roadmap for uDOS. Legacy detail lives in [docs/devlog/ROADMAP-LEGACY.md](devlog/ROADMAP-LEGACY.md).

---

## Status Summary

- Core concept: uDOS is a local Obsidian companion runtime focused on `@workspace`/`@binder` organization, fractal/layered filesystem structures, knowledge-tree navigation, and digital-garden workflows.
- Milestones v1.3.0 to v1.3.7: complete (archived records exist).
- Current focus: v1.4.3 released (2026-02-17). v1.4.4 dev cycle 2026-03-01 to 2026-03-31 (core hardening, gameplay lenses, TUI genres, command dispatch). v1.4.5 dev cycle 2026-04-01 to 2026-04-30 (Wizard stabilization, GitHub Pages publishing). v1.4.6 dev cycle 2026-05-01 to 2026-05-31 (packaging, local libraries, Docker hardening). **v1.4.7 Stable Release planned 2026-06-01 to 2026-06-30 (consolidation, command audit, version unification)**. Groovebox v1.4+ (Songscribe parser pipeline) deferred.
- Version alignment: v1.4.3 released; v1.4.4-6 dev cycles run in parallel; **v1.4.7 is first fully-integrated Stable Release (no multi-version support, all installations upgrade to v1.4.7)**.
- Outstanding (active): v1.4.4 includes core hardening, gameplay lenses (5 implementations), TUI genres (4 types), three-stage command dispatch. v1.4.5 includes Wizard stabilization, GUI browser/file picker, GitHub Pages + Jekyll publishing (no monorepo). v1.4.6 includes distribution packaging (4 variants), local library system (versioning, updates), Docker hardening, standalone Sonic. **v1.4.7 consolidates all work into Stable Release: audits all 40+ commands, modernizes REPAIR/SETUP, removes all backwards-compat shims, unifies versions, publishes comprehensive release notes and command reference.** Groovebox v1.4+ pipeline remains deferred.
- Consolidated release notes: [docs/releases/v1.4.3-release-notes.md](releases/v1.4.3-release-notes.md).
- Dev mode policy: `/dev/` public submodule required and admin-only; see [DEV-MODE-POLICY.md](DEV-MODE-POLICY.md).
- Core/Wizard boundary: `core` is the base runtime; `wizard` is the brand for connected services. Core can run without Wizard (limited). Wizard cannot run without Core.
- Python environment boundary (2026-02-15): Core Python is stdlib-only and must run without a venv; Wizard owns third-party Python in `/venv`; `/dev` piggybacks Wizard venv; Core TS runtime remains optional/lightweight.
- Policy source for env split: [u_dos_python_environments_dev_brief.md](decisions/u_dos_python_environments_dev_brief.md).
- Policy source for VM/control-plane + remote access topology: [u_dos_vm_and_remote_desktop_architecture_apple_silicon_dedicated_nodes.md](decisions/u_dos_vm_and_remote_desktop_architecture_apple_silicon_dedicated_nodes.md).
- Policy source for Alpine thin GUI runtime standard: [u_dos_alpine_thin_gui_runtime_spec_chromium_kiosk_standard.md](decisions/u_dos_alpine_thin_gui_runtime_spec_chromium_kiosk_standard.md).
- Policy source for Sonic DB GPU/Thin-UI launch profiles: [sonic_db_spec_stub_gpu_profiles_thin_ui_launch_profiles.md](decisions/sonic_db_spec_stub_gpu_profiles_thin_ui_launch_profiles.md).
- v1.3.16 release gate checklist: [v1.3.16-release-checklist.md](releases/v1.3.16-release-checklist.md).
- Logging API v1.3: implemented and tested. See [LOGGING-API-v1.3.md](LOGGING-API-v1.3.md).
- Empire: tracked in the Empire section below.

## Recent Progress

- Completed Wizard service split with MCP gateway integration.
- Full vibe-cli integration with uCODE TUI complete.
- Vibe embed and minimal uCODE surface implemented.
- Dev mode gate enforcement finalized.
- Logging API v1.3 implemented and tested (2026-02-08).
- Empire business features split to dedicated Empire scope.
- Migrated legacy bank paths to `memory/system/` and `memory/vault/`.
- Implemented plugin packaging flow (`PLUGIN pack`) aligned to `distribution/plugins`.
- Implemented grid runtime distance calculation, sky view placeholder rendering, and character pixel mapping.
- Wired Talk handler to shared GameState (player id/stats/inventory).
- Documented binder `media/` folder support for non-uDOS-standard files.
- Scaffolded Empire private extension spine with minimal entrypoint and docs.
- Refactored Wizard server wiring into services (auth, logging, stats, scheduler, plugin repo, web proxy, webhooks).
- Completed integration sweep: removed duplicated Wizard route registrations and dropped legacy compatibility wrappers (`create_sonic_routes`, `RebootAliasHandler`).
- Bumped versions: `uDOS` to v1.3.9, `Wizard` to v1.1.2.
- Completed v1.3.16 core command contract cutover (`HEALTH`, `VERIFY`, `DRAW PAT`, `RUN DATA`) with no-shims removal of `SHAKEDOWN`/`PATTERN`/`DATASET`/`INTEGRATION`/`PROVIDER`.
- Added CI policy guardrails for command contract parity, core no-network imports, stdlib boundary, and TS dependency policy.
- Added Wizard venv lifecycle commands (`ucli wizard install`, `ucli wizard doctor`) and pinned Wizard deps at `wizard/requirements.txt`.
- Added architecture decision docs for Apple Silicon VM/remote-desktop topology, Alpine Chromium kiosk thin-GUI runtime standard, and Sonic DB-driven GPU/UI launch profiles.
- Scaffolded gameplay hooks (`PLAY` command + persistent XP/HP/Gold + progression gates) and initial TOYBOX profiles (`hethack`, `elite`) with Wizard container route exposure.
- Replaced TOYBOX launch stubs with PTY-based upstream adapter services (`hethack`, `elite`) and wired event-driven gate/stat updates via Core gameplay tick ingestion.
- Added TOYBOX container expansion (`rpgbbs`, `crawler3d`), standardized gameplay progress fields (`level`, `achievement_level`, `location.grid/z`, metrics), and `PLAY` command conditional/token unlock flow.
- Added `RULE` command scaffold for gameplay IF/THEN automations that evaluate normalized TOYBOX state and trigger gameplay actions/tokens.
- Published TOYBOX variable comparison spec: `docs/specs/TOYBOX-CONTAINER-VARIABLE-COMPARISON-v1.3.md`.
- Added gameplay tutorial/template assets (wireframe demo + historical era variants) and seeded `gameplay-wireframe-demo-script.md` into framework system seeds.
- Added v1.3.22 world-lens MVP bootstrap: `PLAY LENS` status/toggle command surface + single-region 3D lens readiness service behind feature flag.
- Hardened v1.3.22 single-region vertical slice contract checks (allowed place set, LocId/PlaceRef parse validation, slice connectivity validation against seed data).
- Added v1.3.22 parity + ownership guard tests: same quest/place MAP event flow now verified across 2D map lane and adapter lane, with adapter payload attempts blocked from overriding core-owned identity/permissions/gates.
- Started v1.3.23 Round A with mission objective registry + `HEALTH CHECK release-gates` status surface (text/json payload contract).
- Added v1.3.23 TOYBOX adapter lifecycle hardening in PTY runtime (`state`, retries/backoff, health probe/status fields) with dedicated lifecycle tests.
- Added v1.3.23 deterministic gameplay replay harness (`core/services/gameplay_replay_service.py`) with checksum/report artifacts and unknown-event isolation tests.
- Added v1.3.23 CI guardrails/scripts (`check_v1_3_23_contract_drift.py`, `check_v1_3_23_debug_round_a.py`) and Debug Round A triage artifact output.
- Started v1.3.24 Round B by expanding cross-lens parity coverage to multi-step quest-chain state and reward invariants (`core/tests/v1_3_24_parity_reward_invariants_test.py`).
- Added v1.3.24 world-state migration smoke coverage for gameplay/map runtime legacy snapshots + CI smoke entrypoint (`check_v1_3_24_world_state_migration_smoke.py`).
- Added v1.3.24 benchmark history snapshots + regression-delta evaluator/alerts with CI gate (`check_v1_3_24_benchmark_history.py`).
- Added v1.3.24 command capability matrix negative-path tests for role denials, blocked flows, and deterministic syntax/unknown-subcommand errors.
- Completed v1.3.24 Debug Round B hygiene gate: duplicate/legacy-marker baselines cleared and unused private-function annotations emitted via triage artifact.

---

## v1.3.x Pre-3D Bridge (to v1.3.22)

Goal: finish pre-3D foundations inside v1.3.x before enabling engine-backed 3D world rendering.

Integration policy for gameplay rounds:
- [ ] No-fork runtime policy: consume third-party game runtimes as upstream dependencies (pin versions, patch via adapters/wrappers only).
- [ ] Keep uDOS identity/state in Core contracts; do not let external runtimes become system-of-record.
- [ ] 2026 redraw policy: replace/augment presentation via uDOS rendering layers (TUI/grid/web/3D lens), not by rewriting upstream game logic.
- [ ] Naming policy: gameplay runtime containers are `TOYBOX` containers (toybox profiles managed by Wizard).

### v1.3.17 (Complete/Active)
- [x] Sonic cutover to native UEFI contracts (Ventoy removed).
- [x] Core/Wizard command contract cleanup and no-shim enforcement.
- [x] Core/Wizard runtime boundary policy locked (Core stdlib-only Python, Wizard venv-owned deps).

### v1.3.18 (Planned) -- Spatial Contract Hardening
- [x] Lock LocId v1.3 extension with optional vertical axis: `L###-CC##[-Zz]`.
- [x] Keep backward compatibility for existing `L###-CC##` records (`z=0` implied).
- [x] Update parser/validation/tests + renderer schema acceptance for z-aware LocIds.
- [x] Publish migration notes for `grid_locations` and `places` frontmatter.

Reference:
- [v1.3.18-spatial-locid-z-migration-notes.md](releases/v1.3.18-spatial-locid-z-migration-notes.md)

### v1.3.19 (Planned) -- Seed Data Depth Pass
- [x] Add tracked default spatial place seed catalog + CI seed-catalog validation + optional `place_seed_features` persistence scaffold.
- [x] Add deterministic adjacency inference during seed ingestion for places missing explicit links (same anchor/space/layer).
- [x] Add tracked `locations-seed.default.json` gameplay-ready overlay contract and merge it into spatial seed ingest with CI validation.
- [x] Expand `locations-seed.json` from locator-only entries to gameplay-ready tiles/links.
- [x] Add deterministic adjacency/connectivity for region traversal and map overlays.
- [x] Introduce elevation-aware seed fields (`z`, `z_min`, `z_max`, stairs/ramps/portals metadata).
- [x] Add gameplay seed primitives per place/chunk:
  - quest hooks (`quest_ids`, trigger conditions)
  - encounter slots (`npc_spawn`, `hazards`, `loot_tables`)
  - interaction points (`doors`, `terminals`, `craft nodes`, `checkpoints`)

Reference:
- [v1.3.19-seed-depth-foundation.md](releases/v1.3.19-seed-depth-foundation.md)

### v1.3.20 (Planned) -- Grid Runtime Readiness
- [x] Add z-aware map overlays and viewport rules (focus plane + nearby z layers).
- [x] Add schedule/calendar/todo cross-link support to spatial places for workflow overlays.
- [x] Define chunking contract (2D grid chunks now, 3D chunk shape reserved).
- [x] Gameplay Dev Round A (Dungeon Lens: `hethack` integration):
  - containerize public-domain dungeon runtime as a Wizard-managed `TOYBOX` profile
  - run upstream runtime unmodified via adapter boundary (no source fork)
  - reskin terminal/UI surfaces to uDOS visual contract (theme tokens, panels, command affordances)
  - 2026 redraw scope: uDOS-owned renderer for dungeon map/HUD while preserving upstream simulation logic
  - SUB-first dungeon traversal profile (rooms/corridors/doors/traps/loot)
  - turn/tick-compatible event hooks for combat + inventory + quest triggers
  - canonical mapping: `EARTH:SUB:*` PlaceRefs + depth tags to dungeon runtime surfaces
- [x] Add gameplay loop integration in Core map runtime:
  - movement + traversal rules (terrain cost, blocked edges, portal transitions)
  - event dispatch from map actions (`ENTER`, `INSPECT`, `INTERACT`, `COMPLETE`)
  - deterministic tick/update contract for NPC and world-state refresh in TUI lens

Reference:
- [v1.3.20-CHUNKING-CONTRACT.md](specs/v1.3.20-CHUNKING-CONTRACT.md)

### v1.3.21 (Planned) -- 3D Adapter Readiness Gate
- [x] Finalize engine-agnostic world contract (identity, chunks, events, permissions).
- [x] Add compatibility test matrix for dual lenses (TUI map lens + external engine lens).
- [x] Benchmark budgets for seed load, chunk resolve latency, and map render throughput.
- [x] Freeze pre-3D acceptance checklist as release gate for v1.3.22.
- [x] Gameplay Dev Round B (Galaxy Lens: `elite` integration):
  - containerize public-domain galaxy runtime as a Wizard-managed `TOYBOX` profile
  - run upstream runtime unmodified via adapter boundary (no source fork)
  - reskin cockpit/terminal surfaces to uDOS UI contract (grid overlays, status panels, workflow hooks)
  - 2026 redraw scope: uDOS-owned galaxy HUD/nav overlays while preserving upstream simulation logic
  - SUR/ORB/STELLAR travel profile (system map, route graph, station/port nodes)
  - economy/comms/mission hook scaffolds bound to canonical PlaceRefs
  - canonical mapping: `CATALOG:*`, `BODY:*`, and high-band LocIds for galaxy runtime surfaces
- [x] Gameplay parity gate before 3D integration:
  - same quest chain playable in 2D/TUI and adapter harness
  - same NPC state transitions and rewards across both lenses
  - same calendar/todo/workflow side-effects from gameplay events
- [x] Interactive progression requirement (hard gate):
  - complete dungeon level 32 and retrieve the Amulet of Yendor in the `hethack` lens
  - persist gate state in core progression flags (e.g. `gameplay_gates.dungeon_l32_amulet=true`)
  - `UNLOCK/PROCEED/NEXT STEP` actions remain blocked until this gate is satisfied
  - once satisfied, unlock the next integration sequence (galaxy/`elite` round and v1.3.22 preflight)

Reference:
- [v1.3.21-WORLD-ADAPTER-CONTRACT.md](specs/v1.3.21-WORLD-ADAPTER-CONTRACT.md)
- [v1.3.21-DUAL-LENS-COMPAT-MATRIX.md](specs/v1.3.21-DUAL-LENS-COMPAT-MATRIX.md)
- [v1.3.21-ADAPTER-READINESS-CHECKLIST.md](specs/v1.3.21-ADAPTER-READINESS-CHECKLIST.md)
- [v1.3.21-CAPABILITY-BENCHMARK-MISSIONS.md](specs/v1.3.21-CAPABILITY-BENCHMARK-MISSIONS.md)

### v1.3.22 (Planned) -- 3D-World Integration MVP
- [x] Enable first 3D world lens integration behind feature flag.
- [x] Start with single-region vertical slice using canonical LocId/Place contracts.
- [x] Require parity: same quest/place/events playable in 2D grid and 3D lens.
- [x] Keep uDOS as system-of-record; adapters render only (no identity ownership in engine).

### v1.3.23 (Planned) -- Core Stabilization Round A
- [x] Mission objective registry + status endpoint for release gates.
- [x] Stabilize adapter lifecycle management (launch/stop/status retries and health probes).
- [x] Add deterministic replay harness for gameplay event streams.
- [x] Add CI guardrails for contract drift across map/gameplay/toybox surfaces.
- [x] Debug Round A:
  - [x] hardcoded path scan baseline clean
  - [x] deprecated/depreciated marker baseline clean
  - [x] duplicate function scanner baseline clean
  - [x] unused private-function report triaged

Reference:
- [v1.3.23-MISSION-OBJECTIVE-REGISTRY-CONTRACT.md](specs/v1.3.23-MISSION-OBJECTIVE-REGISTRY-CONTRACT.md)
- [v1.3.23-ADAPTER-LIFECYCLE-AND-REPLAY-CONTRACT.md](specs/v1.3.23-ADAPTER-LIFECYCLE-AND-REPLAY-CONTRACT.md)
- [v1.3.23-CONTRACT-DRIFT-CI-GUARDRAILS.md](specs/v1.3.23-CONTRACT-DRIFT-CI-GUARDRAILS.md)
- [v1.3.23-STABILIZATION-ROUND-A-CHECKLIST.md](specs/v1.3.23-STABILIZATION-ROUND-A-CHECKLIST.md)

### v1.3.24 (Planned) -- Core Stabilization Round B
- [x] Expand cross-lens parity suite to include quest chain state and reward invariants.
- [x] Add world-state migration smoke tests for backward-compatible persistence.
- [x] Add benchmark history snapshots and regression-delta alerts.
- [x] Harden command capability matrix with negative-path tests.
- [x] Debug Round B:
  - [x] remove flagged duplicate functions
  - [x] remove or annotate unused private functions
  - [x] resolve legacy/deprecated markers still in active code paths

Reference:
- [v1.3.24-ROUND-B-PARITY-AND-MIGRATION-CHECKLIST.md](specs/v1.3.24-ROUND-B-PARITY-AND-MIGRATION-CHECKLIST.md)

### v1.3.25 (Complete) -- Core Stabilization Round C
- [x] Freeze v1.3.x contract set before v1.4 branch cut.
- [x] Add long-run soak test for event ingestion + map tick loops.
- [x] Add release checklist automation for mission objectives + benchmark budgets.
- [x] Verify no hardcoded local machine paths remain in runtime code.
- [x] Debug Round C:
  - [x] dead-code cleanup sweep (python + ts)
  - [x] duplicate logic consolidation in command/service layers
  - [x] benchmark regression drill (simulate failure, verify gate blocks release)

Reference:
- [v1.3.25-CONTRACT-FREEZE-AND-RELEASE-CHECKLIST.md](specs/v1.3.25-CONTRACT-FREEZE-AND-RELEASE-CHECKLIST.md)

### v1.3.26 (Complete) -- Core Stabilization Final Gate
- [x] Final stabilization pass for command/runtime surfaces (no contract regressions).
- [x] Final capability matrix sign-off for Core, Wizard, and TOYBOX lanes.
- [x] Final benchmark sign-off against mission objective thresholds.
- [x] Publish core stabilization release notes and v1.4 readiness memo.
- [x] Debug Round Final:
  - [x] hardcoding check passes
  - [x] deprecated/depreciated code marker check passes
  - [x] duplicate function check passes
  - [x] unused-function report reviewed and approved

Reference:
- [v1.3.26-FINAL-GATE-READINESS-CHECKLIST.md](specs/v1.3.26-FINAL-GATE-READINESS-CHECKLIST.md)
- [v1.3.26-CORE-STABILIZATION-RELEASE-NOTES.md](specs/v1.3.26-CORE-STABILIZATION-RELEASE-NOTES.md)
- [v1.4.0-READINESS-MEMO.md](specs/v1.4.0-READINESS-MEMO.md)
- [v1.4.0-KICKOFF-CHECKLIST.md](specs/v1.4.0-KICKOFF-CHECKLIST.md)

---

## Active Checklist (Merged)

Last updated: 2026-02-17

### P0 -- Wizard/Vibe Refactor
- [x] Add MCP server tests to verify stdio tool wrapping and tool index parsing.
- [x] Bootstrap Vibe integration (embed) and minimal uCODE command exposure.
- [x] Enforce Dev mode gate (admin-only and `/dev/` presence) and document policy contract.

### P0 -- Consolidation and Verification
- [x] Implement Logging API v1.3 endpoints per [LOGGING-API-v1.3.md](LOGGING-API-v1.3.md).
- [x] Add integration checks for MCP gateway and Wizard health/tool list.

### P0 -- Runtime Boundary Enforcement (Core/Wizard Venv Split)
- [x] Add CI guardrail to block non-stdlib imports under `core/py`.
- [x] Add CI guardrail to flag heavy Core TS dependency growth.
- [x] Enforce launcher capability checks:
  - [x] `udos wizard ...` and `udos dev ...` fail with install guidance if `/venv` is missing.
  - [x] `udos ts ...` reports missing Node and falls back to Core mode when possible.
- [x] Ensure Wizard dependency pinning policy is enforced (`requirements.txt`/lockfile committed and used by install path).
- [x] Add/verify `udos wizard install` and `udos wizard doctor` for venv lifecycle checks.

### P0 -- TUI Parity and Advanced I/O Hardening (Active)
- [x] Next-round handoff prep note created: [2026-02-17-next-dev-round-prep.md](releases/2026-02-17-next-dev-round-prep.md).
- [x] Next-round execution note deployed: [2026-02-17-next-dev-round-execution.md](releases/2026-02-17-next-dev-round-execution.md).
- [x] Single-writer stdout lock deployed across prompt/menu/renderer/uCLI interactive paths.
- [x] Full-screen/raw menu defaults removed; inline-first mode is now default with explicit opt-in toggles.
- [x] `GRID WORKFLOW` sample payload + command docs/examples added (`memory/system/grid-workflow-sample.json`).
- [x] Canonical `80x30` parity fixtures added for GRID calendar/schedule/workflow panels.
- [ ] Consolidate interactive surfaces (menus, story forms, confirmations, selectors) onto one inline-first I/O layer with consistent rendering rules.
- [x] Remove mixed full-screen/raw-mode defaults from core command flows; allow full-screen mode only as explicit opt-in.
- [x] Add explicit prompt lifecycle contract:
  - [x] input phase (exclusive stdin ownership)
  - [x] render phase (exclusive stdout ownership)
  - [x] background phase (no direct stdout writes; queue to renderer)
- [ ] Implement output arbitration to prevent interleaving between:
  - [ ] startup banners/progress
  - [ ] status bar redraws
  - [ ] command output payloads
  - [ ] toolbar/suggestion refresh
- [ ] Standardize terminal control sequences:
  - [ ] no cursor-home on menu/screen restore
  - [ ] line-clear via ANSI-safe primitives
  - [ ] width-safe handling for block glyphs and emoji
- [ ] Add advanced I/O compatibility test matrix:
  - [ ] iTerm2 (macOS), Terminal.app (macOS), VS Code integrated terminal, Linux PTY
  - [ ] arrow keys/history/completion parity in advanced and fallback prompt modes
  - [ ] no-output-corruption regression snapshots for startup + HELP + STORY flows
- [ ] Add CI gate for TUI parity:
  - [ ] fail on detected output interleaving/misalignment regressions
  - [ ] fail on reintroduction of deprecated compatibility shims

### P1 -- Platform and Extensions
- [x] Reintroduce Empire business features on new extension spine.
- [ ] uCLI map layer rendering extension:
  - [ ] Add layered map renderer contract in uCLI (`base terrain`, `objects/sprites`, `overlays`, `workflow/task markers`).
  - [ ] Add deterministic z-layer view controls and legend rendering for LocId + PlaceRef surfaces.
  - [ ] Align `MAP`, `GRID MAP`, and `PLAY MAP` outputs to a shared map-panel schema.
  - [ ] Add markdown diagram export path for map layers (`DRAW --md MAP`, `GRID MAP --format md` parity target).
  - [ ] Add parity tests for canonical `80x30` and adaptive viewport map outputs.

### P2 -- Code Quality (Pre-v1.4)
- [x] Review long route factory functions for modularization.
- [x] Consider splitting nested route handlers into separate modules.

---

## Core Roadmap (uDOS)

### v1.4.x -- Repo Restructure and Containerisation (Completed in v1.4.3)

Reference:
- [v1.4.3 consolidated release notes](releases/v1.4.3-release-notes.md)
- [v1.4.0-KICKOFF-CHECKLIST.md](specs/v1.4.0-KICKOFF-CHECKLIST.md)
- [v1.4.0-EXECUTION-ORDER.md](specs/v1.4.0-EXECUTION-ORDER.md)
- [v1.4.0-DOCKER-AUTOMATION-CAPABILITY-SPEC.md](specs/v1.4.0-DOCKER-AUTOMATION-CAPABILITY-SPEC.md)

#### P0 -- Repo Restructure (Complete)
- [x] Root cleanup: removed ephemeral debug/fix files.
- [x] Wizard consolidation: merged `api/wizard/`, `mcp/wizard/`, `core/wizard/` into `wizard/`.
- [x] Removed compatibility shims (`services/` to direct `core.services` imports).
- [x] Workspace filesystem contract aligned:
  - `vault/` kept as distributable template scaffold
  - `core/framework/seed/vault/` is canonical starter seed source
  - `memory/vault/` remains runtime user vault (gitignored)
- [x] Added `memory/inbox/` and `memory/submissions/` workspaces.
- [x] Fixed vault path references in binder manager, compiler, server.
- [x] Moved `vendor/emoji/` to `fonts/emoji/`.
- [x] Removed stub dirs: `commands/`, `input/`, `tui/`, `tauri-ui/`, `vault-md/`, `web-portal/`.
- [x] Distribution consolidation: merged `wizard/distribution/` into `distribution/`.
- [x] Library cleanup: removed empty `library/containers/`, `library/packages/`.
- [x] Docker compose updated: snap-on-off profiles (wizard, ollama, scheduler, home-assistant, groovebox).
- [x] App separation: ObsidianCompanion moved out of uDOS monorepo to private pre-release repo `fredporter/oc-app`.

#### P0 -- Workspace Filesystem (@workspace)
- [x] Scaffold all workspace dirs under `memory/`.
- [x] Wire `@workspace` syntax in Core TUI (canonical `PLACE` + `BINDER` command surfaces).
- [x] Implement workspace switching in file pickers and readers.
- [x] Update Wizard routes to use workspace-aware vault paths.

#### P0 -- Python Runtime Boundary (Core/Wizard/Dev)
- [x] Keep `core/py` strictly stdlib-only and venv-independent.
- [x] Keep Wizard Python dependencies isolated to `/venv`.
- [x] Keep `/dev` tooling on Wizard venv only (no separate default dev venv).
- [x] Add boundary tests for `core` (system Python), `wizard/dev` (venv required), and `ts` (Node capability-gated).

#### P1 -- Containerisation
- [x] Sonic Screwdriver Dockerfile (ISO/USB builder).
- [x] Songscribe/Groovebox Dockerfile.
- [x] Verify all `docker compose --profile` combinations work.
- [x] Library manager: `LIBRARY sync`, `LIBRARY status`, and `LIBRARY info` commands.

#### P2 -- Code Quality and Modularization
- [ ] Review long route factory functions for modularization opportunities:
  - [x] `wizard/routes/ucode_routes.py` (modularized from ~1059 -> ~263 lines; split into `ucode_meta_routes.py`, `ucode_ok_routes.py`, `ucode_user_routes.py`, `ucode_dispatch_routes.py`, `ucode_setup_story_utils.py`, `ucode_dispatch_utils.py`, `ucode_ok_execution.py`, `ucode_ok_mode_utils.py`, `ucode_ok_dispatch_core.py`, `ucode_ok_stream_dispatch.py`, `ucode_route_utils.py`, `ucode_stream_utils.py`, `ucode_command_utils.py`)
  - [x] `wizard/routes/config_routes.py` (now split into core routes + `config_routes_helpers.py` + `config_admin_routes.py` + `config_ssh_routes.py`; compatibility wrappers removed)
  - [x] `wizard/routes/provider_routes.py` (now split: route + `ollama_route_utils.py`)
  - [x] `wizard/routes/setup_routes.py` (phase modularization complete; core endpoints moved to `setup_core_routes.py`, helpers moved to `setup_route_utils.py`, `/story/*` moved to `setup_story_routes.py`, `/profile/*` + `/installation/*` moved to `setup_profile_routes.py`, `/locations/*` + timezone endpoint moved to `setup_location_routes.py`, `/wizard/*` moved to `setup_wizard_routes.py`, `/paths*` moved to `setup_path_routes.py`)
  - [x] `core/commands/destroy_handler.py` (now split: handler + `destroy_handler_helpers.py`)
  - [x] `core/commands/setup_handler.py` (now split: handler + `setup_handler_helpers.py`)
- [x] Consider splitting nested route handlers into separate modules.

### v1.4.4 -- Core Hardening, Demo Scripts & Educational Distribution

**Goal:** Stabilize core internals via comprehensive modularization audit, expand TypeScript runtime feature coverage with demo scripts, and create executable educational assets for community learning.

**Timeline:** 2026-03-01 to 2026-03-31 (planned)

#### P0 -- Core Module Audit & Hardening

- [ ] **Modularization Compliance Check**
  - [ ] Audit `core/commands/` for nested functions exceeding 150 lines; extract helpers where applicable.
  - [ ] Audit `core/services/` for single-responsibility violations; document public/private contract boundaries.
  - [ ] Audit `core/parsers/` for grammar/tokenizer/AST separation clarity; consolidate related parsing logic.
  - [ ] Audit `core/runtime/` for runtime lifecycle phases; extract phase-specific logic into stage handlers.
  - [ ] Generate modularization compliance report with remediation checklist.

- [ ] **Dependency Integrity Audit**
  - [ ] Verify Core Python remains stdlib-only (no indirect `wizard/Wizard` imports).
  - [ ] Verify Core TypeScript has no Node.js-only dependencies (browser-compatible runtime check).
  - [ ] Audit circular dependency chains in `core/services/` and confirm acyclic DAG.
  - [ ] Enforce no `sys.path` manipulation in Core (direct imports only).
  - [ ] Document boundary test suite coverage for Core/Wizard separation.

- [ ] **Error Handling Hardening**
  - [ ] Expand error contract compliance in command handlers (validate all error types map to schema).
  - [ ] Add recovery-path test harness for common failure modes (missing config, invalid state, timeout).
  - [ ] Audit logging levels and ensure no sensitive data in `DEBUG` logs.
  - [ ] Create `ERROR-HANDLING-v1.4.4.md` contract spec.

#### P1 -- Gameplay Integration, Theming Architecture & Input Dispatch

**Gameplay Hardening + Lenses:**

- [ ] **TOYBOX Container Integration Hardening**
  - [ ] Audit PTY lifecycle in `core/services/gameplay_service.py` (startup/shutdown contract).
  - [ ] Verify game state mutations are atomic and replayed deterministically.
  - [ ] Add recovery paths for game container crashes (graceful degradation, state restore).
  - [ ] Expand `core/commands/play_handler.py` with `--debug` flag for adapter diagnostics.
  - [ ] Create `core/tests/v1_4_4_gameplay_adapter_lifecycle_test.py` for container lifecycle tests.

- [ ] **PLAY Command Integration Expansion**
  - [ ] Wire `PLAY @profile/nethack` profile selection with canonical profile loader.
  - [ ] Wire `PLAY @profile/elite` 3D flight sim variant with viewport adapter.
  - [ ] Wire `PLAY @profile/rpgbbs` classic BBS-style MUD variant.
  - [ ] Wire `PLAY @profile/crawler3d` procedural dungeon crawler variant.
  - [ ] Implement profile startup sequence with title screens, character creation, intro flow.
  - [ ] Add `PLAY --list-profiles` to enumerate available variants.
  - [ ] Add `PLAY --info <profile>` to show profile metadata (description, requirements, save format).

- [ ] **Game Lens Scaffolding**
  - [ ] Create lens interface contract: input (game state), output (rendered view), event routing.
  - [ ] Scaffold `core/lenses/nethack_lens.py` — translates nethack map to uDOS grid + TUI render.
  - [ ] Scaffold `core/lenses/elite_lens.py` — 3D flight corridor view (procedural ASCII art).
  - [ ] Scaffold `core/lenses/rpgbbs_lens.py` — terminal BBS-style UI preservation + wrapping.
  - [ ] Scaffold `core/lenses/simple_ascii_lens.py` — fallback viewport for all game types (generic grid).
  - [ ] Implement lens switching via `PLAY LENS <name>` command (e.g., `PLAY LENS nethack`, `PLAY LENS ascii`).
  - [ ] Add lens feature tests: viewport rendering, input translation, output consistency.
  - [ ] Create `docs/specs/GAMEPLAY-LENS-ARCHITECTURE-v1.4.4.md` with contract + examples.

**Theming Architecture Refactor:**

- [ ] **Separate TUI GENRE from Wizard GUI Themes**
  - [ ] Rename `/themes/` → `/themes/genre/` with TUI-specific color schemes + ASCII conventions.
  - [ ] Create genre types: `retro` (C64, Teletext), `neon` (cyberpunk, neon), `minimal` (zen, monochrome), `dungeon` (fantasy, nethack-like).
  - [ ] Add genre error/system message styles (colored stack traces, status indicators, warning boxes).
  - [ ] Move Wizard web GUI themes (HTML/CSS) to `wizard/web/themes/` (separate from Core).
  - [ ] Create genre applicator: `core/services/tui_genre_manager.py` with genre manifest loading.
  - [ ] Wire genre selection in `core/config/` (config.json: `"tui_genre": "retro"`).
  - [ ] Add genre export for error renders: colored error frames, styled logging output.
  - [ ] Create `docs/specs/TUI-GENRE-ARCHITECTURE-v1.4.4.md` with genre contract + customization guide.

**uCLI VIBE Integration Hardening:**

- [ ] **Input Dispatch Chain Optimization**
  - [ ] Implement three-stage dispatch: (1) uCODE command matching, (2) shell/bash passthrough, (3) VIBE/OK fallback.
  - [ ] Stage 1: Tokenize input, match against canonical command registry (`HELP`, `HEALTH`, `PLACE`, `DRAW`, `RUN`, `PLAY`, `RULE`, `LIBRARY`, `BINDER`, `VERIFY`).
  - [ ] Stage 2: If no uCODE match, check if input is valid shell syntax (bash/sh safety checks).
  - [ ] Stage 3: If neither Stage 1 nor 2 match, route to Wizard VIBE/OK service for AI handling.
  - [ ] Add early-exit optimization: Stage 1 match confidence >95% short-circuits Stages 2+3.
  - [ ] Create `core/services/command_dispatch_service.py` with three-stage dispatcher.
  - [ ] Wire dispatcher in `bin/ucli` at REPL input phase.
  - [ ] Add dispatch diagnostics: `ucli --dispatch-debug "input"` shows dispatch chain reasoning.
  - [ ] Create `docs/specs/uCLI-COMMAND-DISPATCH-v1.4.4.md` with routing contract + examples.

- [ ] **VIBE Integration Testing**
  - [ ] Create `core/tests/v1_4_4_command_dispatch_chain_test.py` with dispatch scenarios.
  - [ ] Add tests for dispatch ambiguity (e.g., `PLAY` vs. `play` case sensitivity, abbreviation handling).
  - [ ] Add tests for fallback routing (e.g., `UNKNOWN_CMD` → Wizard → appropriate error or AI response).
  - [ ] Add tests for shell passthrough safety (reject attempts to break out, exfiltrate data).
  - [ ] Verify dispatch latency: uCODE dispatch <10ms, shell validation <50ms, VIBE lookup <500ms.

#### P1b -- TypeScript Runtime Demo Scripts & Feature Showcase

- [ ] **TS Runtime Feature Completion**
  - [ ] Verify all TUI rendering features are represented in demo suite (boxes, grids, tables, ansi colors, progress bars).
  - [ ] Verify command parsing features covered (subcommand dispatch, flag parsing, help generation).
  - [ ] Verify AST/parser features covered (markdown tokenization, schema validation, template processing).
  - [ ] Verify grid runtime features covered (spatial queries, viewport calculations, place/location resolution).
  - [ ] Audit TypeScript `core/src/` for untested public methods; target 85% coverage.

- [ ] **Demo Script Suite**
  - [ ] Create `core/examples/demo-tui-rendering.ts` — showcase all TUI atoms (box, grid, table, progress, color palette) + genre variations.
  - [ ] Create `core/examples/demo-command-parsing.ts` — showcase CLI argument parsing, subcommands, help text generation.
  - [ ] Create `core/examples/demo-markdown-ast.ts` — showcase Markdown tokenization, AST generation, frontmatter extraction.
  - [ ] Create `core/examples/demo-grid-runtime.ts` — showcase spatial API, place resolution, viewport calculations, pathfinding stubs.
  - [ ] Create `core/examples/demo-template-engine.ts` — showcase variable substitution, conditionals, loops in templates.
  - [ ] Create `core/examples/demo-schema-validation.ts` — showcase JSON/YAML schema validation with error reporting.
  - [ ] Create `core/examples/demo-gameplay-lens.ts` — showcase lens interface, game state rendering, input translation.
  - [ ] Compile demo scripts via `tsc` and create executable `bin/demo-*` entry points.

- [ ] **Documentation & Inline Help**
  - [ ] Add JSDoc comments to all demo entry functions.
  - [ ] Create `core/examples/README.md` with feature matrix and demo invocation instructions.
  - [ ] Add `--help` and `--demo-mode` flags to each demo script for interactive exploration.
  - [ ] Add `demo-gameplay-lens.ts` to education materials (showcase game variant rendering).

#### P2 -- Stdlib Core Python Command Test Suite & Display Showcase

- [ ] **Command Handler Test Coverage**
  - [ ] Create `core/tests/v1_4_4_stdlib_command_integration_test.py` covering command lifecycle.
  - [ ] Add tests for all P0 commands: `HELP`, `HEALTH`, `VERIFY`, `PLACE`, `BINDER`, `DRAW`, `RUN`, `PLAY`, `RULE`, `LIBRARY`.
  - [ ] Add negative-path tests for invalid subcommands, missing args, state violations.
  - [ ] Add integration tests for command chaining and state persistence across commands.
  - [ ] Verify error messages match contract spec schema.
  - [ ] Add gameplay tests: `PLAY --status`, profile selection, lens switching, game state mutations.
  - [ ] Target 90%+ coverage for command handlers.

- [ ] **TUI Display Test & Render Script**
  - [ ] Create `core/tests/v1_4_4_display_render_test.py` — comprehensive TUI render coverage.
  - [ ] Add render tests for all TUI widgets (panels, tables, grids, status bars, progress).
  - [ ] Add multi-width viewport tests (40x12, 80x24, 120x40) with ANSI code validation.
  - [ ] Create `core/scripts/display-showcase.md` — Markdown document with all rendered outputs embedded.
  - [ ] Add script to auto-generate ASCII art snapshots and embed in showcase via `![char](data:text/plain;base64,...)`.
  - [ ] Create `bin/display-showcase` executable wrapper (Python entry point).

- [ ] **Educational Demo Distribution**
  - [ ] Create `bin/ucli-education-mode` flag for interactive guided tours of Core features.
  - [ ] Scaffold `distribution/education/` directory structure with:
    - [ ] `getting-started-cli.md` — learn `HELP`, `HEALTH`, `VERIFY` flow.
    - [ ] `learning-workspaces.md` — learn `PLACE`, `BINDER`, `@workspace` syntax.
    - [ ] `learning-grid-and-map.md` — learn `DRAW`, `PLAY LENS`, grid spatial logic.
    - [ ] `learning-commands-and-flow.md` — learn `RUN`, `RULE`, replay and replay verification.
    - [ ] `learning-styling-and-theming.md` — learn theme packs, TUI customization, rendering layers.
  - [ ] Create `distribution/education/demo-scripts/` with runnable examples:
    - [ ] `00-hello-udos.sh` — minimal "Hello uDOS" TUI render.
    - [ ] `01-workspace-tour.sh` — interactive `@workspace` navigation.
    - [ ] `02-grid-explorer.sh` — spatial grid demo with playable character.
    - [ ] `03-command-matrix.sh` — exhaustive command invocation matrix with timing.
    - [ ] `04-theme-viewer.sh` — theme pack gallery with live render comparison.
    - [ ] `05-gameplay-replay.sh` — recorded gameplay session with deterministic replay.
  - [ ] Add `.gitkeep` + distribution metadata in `distribution/education/MANIFEST.md`.

#### P3 -- Integration & QA Gate

- [ ] **Integration Smoke**
  - [ ] Run modularization compliance report and remediation checklist.
  - [ ] Run Core/Wizard boundary test suite and confirm all 0 violations.
  - [ ] Run TS demo suite compiled artifacts and verify all bins are executable.
  - [ ] Run Python command test suite and verify 90%+ coverage + all P0 commands pass.
  - [ ] Run display showcase script and verify no render errors.
  - [ ] Run education suite demo scripts and verify all complete successfully.

- [ ] **Release Gate**
  - [ ] Update `core/version.py` to v1.4.4.
  - [ ] Update `wizard/version.json` to match uDOS major.minor (v1.4.4).
  - [ ] Publish `v1.4.4-release-checklist.md` in `docs/releases/`.
  - [ ] Publish `CORE-HARDENING-AUDIT-v1.4.4.md` in `docs/specs/` with full compliance matrix.
  - [ ] Update `STATUS.md` with v1.4.4 completion date and next focus (Groovebox v1.4+ or v1.5 features).
  - [ ] Tag release: `git tag -a v1.4.4 -m "Core hardening, demo scripts, educational distribution"`.

---

#### Reference Artifacts

- **Modularization Audit:** [CORE-MODULARIZATION-AUDIT-v1.4.4.md](specs/CORE-MODULARIZATION-AUDIT-v1.4.4.md)
- **Error Handling Contract:** [ERROR-HANDLING-v1.4.4.md](specs/ERROR-HANDLING-v1.4.4.md)
- **Gameplay Lens Architecture:** [GAMEPLAY-LENS-ARCHITECTURE-v1.4.4.md](specs/GAMEPLAY-LENS-ARCHITECTURE-v1.4.4.md) (to be created)
- **TUI Genre Architecture:** [TUI-GENRE-ARCHITECTURE-v1.4.4.md](specs/TUI-GENRE-ARCHITECTURE-v1.4.4.md) (to be created)
- **uCLI Command Dispatch:** [uCLI-COMMAND-DISPATCH-v1.4.4.md](specs/uCLI-COMMAND-DISPATCH-v1.4.4.md) (to be created)
- **TypeScript Demo Suite:** `core/examples/demo-*.ts` (to be created)
- **Python Command Tests:** `core/tests/v1_4_4_stdlib_command_integration_test.py`
- **Display Render Tests:** `core/tests/v1_4_4_display_render_test.py`
- **Gameplay Adapter Tests:** `core/tests/v1_4_4_gameplay_adapter_lifecycle_test.py` (to be created)
- **Command Dispatch Tests:** `core/tests/v1_4_4_command_dispatch_chain_test.py` (to be created)
- **Display Showcase:** `core/scripts/display-showcase.md` + `bin/display-showcase`
- **Education Pack:** `distribution/education/` with guides, demo scripts, resources

---

## Wizard Roadmap

**Component:** `wizard/` | **Current:** v1.4.3 (stable release) | **Status:** Active Development

### v1.3.15 -- Publish Spec Refactor (Planned)

#### P0 -- Must Have
- [x] Define and approve Wizard web publish contract for monorepo/module model.
- [x] Implement provider capability registry for publish routes.
- [x] Add canonical publish API surface and dashboard publish views.
- [x] Enforce module-aware publish gating (`/dev`, `sonic`, `groovebox`, external app adapters).
- [x] Add release-gate tests for publish lifecycle + manifest integrity.

Reference: [WIZARD-WEB-PUBLISH-SPEC-v1.3.15.md](specs/WIZARD-WEB-PUBLISH-SPEC-v1.3.15.md)

### v1.4.x (Completed in v1.4.3)

#### P0 -- Must Have
- [x] Library manager completion: full CRUD, versioning, dependency resolution.
- [x] Web proxy implementation: reverse proxy for container-hosted services.
- [x] Workspace routing: `@workspace` syntax for routing requests to named contexts.
- [x] MCP gateway hardening: auth, rate limiting, tool registration protocol.
- [x] Unified config layer: single config source of truth across `wizard/`.

#### P1 -- Should Have
- [x] Container orchestration: compose-based multi-container lifecycle management.
- [x] Plugin marketplace: discovery, install, update flow via plugin registry.
- [x] Provider health checks: automated provider availability monitoring.
- [x] Extension hot-reload: live reload for wizard extensions without restart.
- [x] Dashboard WebSocket events: real-time status push to web-admin.

#### P2 -- Nice to Have
- [x] Self-heal route expansion: broader automated recovery strategies.
- [x] Diagram generation service: server-side diagram rendering pipeline.
- [x] Songscribe route integration: bridge groovebox transport into Wizard API.
- [x] GitHub integration polish: PR and issue automation helpers.
- [x] GitHub Actions publish sync (from OC-app) when moving beyond direct push.

### v1.4.5 -- Wizard Stabilization & GitHub Pages Web Publishing

**Goal:** Stabilize Wizard server (fix instabilities, improve GUI reliability), refine browser refinement and file picker, establish user-controlled web publishing pathway via GitHub Pages + Jekyll (replacing monorepo), and improve GitHub Actions automation for vault sync.

**Timeline:** 2026-04-01 to 2026-04-30 (planned)

**Monorepo Deprecation:** Replace central uDOS monorepo concept with decentralized user-owned GitHub Pages hosting. Each user publishes to their own GitHub repo and custom domain. No central publish infrastructure.

#### P0 -- Wizard Stabilization & Bug Fixes

- [ ] **Critical Stability Fixes**
  - [ ] Audit and fix Wizard server startup crashes (`wizard/server.py` init sequence).
  - [ ] Fix memory leaks in long-running Wizard processes (WebSocket handlers, background tasks).
  - [ ] Audit active error codes and resolve common exceptions in routes.
  - [ ] Add comprehensive Wizard health check (`WIZARD health`, `WIZARD status`).
  - [ ] Verify venv lifecycle management (create, activate, cleanup without orphaned processes).

- [ ] **Wizard Venv Operations**
  - [ ] Implement `WIZARD venv create --python 3.11` (create isolated Wizard venv).
  - [ ] Implement `WIZARD venv activate` (switch active Wizard Python environment).
  - [ ] Implement `WIZARD venv doctor` (diagnose venv issues, missing packages).
  - [ ] Implement `WIZARD venv reset` (clean reinstall of all dependencies).
  - [ ] Wire venv selection in dashboard settings (`#/settings/python-environment`).
  - [ ] Add dependency pinning checks (`requirements.txt` version locks, security vulnerability scans).

- [ ] **GUI Browser & File Picker Restoration**
  - [ ] Audit existing file picker code (`wizard/web/components/FilePicker.svelte` or equivalent).
  - [ ] Fix broken file picker (currently non-functional per user report).
  - [ ] Restore file picker in all browse modal contexts (import, export, config file edit).
  - [ ] **Enhance with Collapsible Tailwind Styles:**
    - [ ] Collapse/expand folder trees with smooth animations (Tailwind `transition`).
    - [ ] Context menu (right-click) for copy path, open in terminal, trash file.
    - [ ] Drag-and-drop to reorder or move files.
    - [ ] Search/filter within file browser (`cmd+f` or persistent search box).
    - [ ] Recent files sidebar + frequent locations (Desktop, Downloads, vault).
    - [ ] Breadcrumb navigation at top of picker.
  - [ ] **File Browser Refinement:**
    - [ ] Sort by name, date modified, size (toggle buttons).
    - [ ] File type icons (markdown, folder, image, code, etc.).
    - [ ] Preview pane (show file contents for markdown, image thumbs).
    - [ ] Multi-select + bulk operations (copy, move, delete selected).
    - [ ] Keyboard shortcuts (arrow keys, enter to select, esc to cancel).

#### P1 -- GitHub Pages Web Publishing & Monorepo Replacement

- [ ] **GitHub Setup & Config**
  - [ ] Implement `WIZARD github setup` interactive flow (username → repo → domain).
  - [ ] Store GitHub PAT securely in `wizard/secrets/` (encrypted config).
  - [ ] Validate GitHub repo access on setup (test push to throwaway branch).
  - [ ] Add GitHub setup panel in dashboard (`#/publish/github`).
  - [ ] Wire uCLI commands: `WIZARD github setup`, `WIZARD github status`, `WIZARD github validate`.

- [ ] **Jekyll Site Template & Content Staging**
  - [ ] Create `distribution/jekyll-site-template/` with minimal Jekyll setup.
  - [ ] Include `.github/workflows/build.yml` for automated Jekyll build + GitHub Pages deploy.
  - [ ] Create Jekyll layouts: `default.html`, `vault.html`, `binder.html`, `page.html`.
  - [ ] Create Jekyll includes: `nav.html`, `toc.html`, `footer.html`, `search-box.html`.
  - [ ] Implement vault → Jekyll markdown conversion (frontmatter extraction, image rewriting, link conversion).
  - [ ] Implement search index generation (JSON index for client-side search).

- [ ] **Publish Pipeline**
  - [ ] Implement `PUBLISH --github` command (soft sync: stage → commit → push).
  - [ ] Implement `PUBLISH --github --hard` (full reset, re-upload all content).
  - [ ] Implement `PUBLISH --github --export` (export to local Jekyll dir without push).
  - [ ] Implement soft sync latency targets: <30 seconds for typical vault (50-100 files).
  - [ ] Add sync progress tracking and cancellation support.

- [ ] **GitHub Actions Integration**
  - [ ] Verify Jekyll build via GitHub Actions (`ruby/setup-ruby`, `jekyll build`, `actions/deploy-pages`).
  - [ ] Add GitHub Pages deployment automation (main branch → published site).
  - [ ] Add build status monitoring and error reporting in dashboard.
  - [ ] Implement rollback mechanism if build fails (revert last good commit).
  - [ ] Add custom domain support (CNAME setup guide in setup flow).

- [ ] **Wizard Dashboard Publishing Panel**
  - [ ] Create publish status panel (`#/publish`) showing GitHub repo, Pages URL, last sync time.
  - [ ] Create sync history panel with audit trail (timestamps, item counts, status).
  - [ ] Wire `[🔄 Sync Now]`, `[⚙ Settings]`, `[View Log]` buttons.
  - [ ] Real-time status updates via WebSocket (sync in progress, build running).

- [ ] **Monorepo Deprecation & Migration**
  - [ ] Mark existing monorepo publish routes as deprecated (show warning in UI).
  - [ ] Implement `PUBLISH --export-legacy` for exiting monorepo users.
  - [ ] Create migration guide: monorepo → GitHub Pages workflow.
  - [ ] Document rollback path if user wants to revert to monorepo (remains available but hidden).

#### P2 -- GUI Enhancement & Library Sheets

- [ ] **Wizard GUI Font & Icon Library Reference Sheets**
  - [ ] Create interactive font picker in dashboard (`#/settings/fonts`).
  - [ ] Create emoji/icon picker with searchable library (Discord emoji, Unicode, FontAwesome icons).
  - [ ] Wire selected fonts into TUI rendering (`core` uses selected font when available).
  - [ ] Export font config as YAML (user can share/version control theme).
  - [ ] Embed reference sheet in Wizard GUI as collapsible panel.

- [ ] **Editable Config Sheets**
  - [ ] Create config editor UI (`#/config/advanced`) for manual JSON/YAML editing.
  - [ ] Support live validation (schema checking, error highlighting in editor).
  - [ ] Add undo/redo history for config changes.
  - [ ] Add import/export for config files (backup/restore, share with team).
  - [ ] Warn users of breaking changes in config schema (version migration prompts).

- [ ] **Publishing Config Panel**
  - [ ] Create editable Jekyll config panel (`#/publish/config/jekyll`).
  - [ ] Allow custom `_config.yml` editing (theme, plugins, site title/tagline).
  - [ ] Provide theme preview (render sample page with selected theme).
  - [ ] Support custom CSS/JS injection (for advanced theme customization).

#### P3 -- Testing & Documentation

- [ ] **E2E Testing**
  - [ ] Test GitHub setup flow: full interactive walkthrough.
  - [ ] Test publish pipeline: stage → commit → push → build → pages.
  - [ ] Test large vault sync: performance with 500+, 1000+ files.
  - [ ] Test jekyll build errors and rollback mechanism.
  - [ ] Test custom domain configuration (CNAME + DNS).

- [ ] **Documentation**
  - [ ] Write user guide: "Publishing Your Vault to GitHub Pages" (step-by-step with screenshots).
  - [ ] Write troubleshooting guide: common errors, resolution steps.
  - [ ] Write migration guide: "Moving from uDOS Monorepo to GitHub Pages".
  - [ ] Write Jekyll theme customization guide (CSS, layouts, plugins).
  - [ ] Create video tutorial (5-10 min walkthrough of full publish flow).

- [ ] **Wizard Stability Testing**
  - [ ] Stress test long-running Wizard processes (24hr uptime, memory stability).
  - [ ] Test venv isolation and cleanup (no orphaned Python processes).
  - [ ] Test browser file picker: multi-select, drag-drop, search, keyboard shortcuts.
  - [ ] Verify GUI responsiveness with large vaults (100k+ files in file picker).

---

### v1.4.6 -- Packaging, Local Libraries & Distribution Hardening

**Goal:** Establish comprehensive packaging and distribution system for uDOS, including standalone Sonic ISO distribution, local library management with versioning and updates, hardened Docker container lifecycle, and integrated Wizard/Sonic deployment.

**Timeline:** 2026-05-01 to 2026-05-31 (planned)

**Key Focus:** uDOS shifts from monorepo to consumable distribution packages with local library ecosystem; Sonic becomes standalone bootable artifact; container system gains health, recovery, and auto-update mechanisms.

#### P0 -- Packaging & Distribution Infrastructure

- [ ] **uDOS Package Definition**
  - [ ] Define release package structure: Core + optional Wizard + optional Sonic + optional modules.
  - [ ] Document package variants:
    - `udos-core-slim`: Core runtime only (no Wizard, no containers) for lightweight local use.
    - `udos-wizard-full`: Core + Wizard + Docker compose setup (all services).
    - `udos-sonic-iso`: Standalone ISO for USB/boot (no Wizard, minimal Core).
    - `udos-dev-complete`: Core + Wizard + Sonic + /dev module (for developers).
  - [ ] Create release manifest schema (checksums, metadata, signatures, component versions).
  - [ ] Implement semantic versioning enforcement (MAJOR.MINOR.PATCH.RELEASE_TYPE).

- [ ] **Build & Release Automation**
  - [ ] Create `bin/build-release.py` script that orchestrates full package build.
  - [ ] Implement artifact signing (GPG keys for release artifacts).
  - [ ] Create GitHub Actions workflow: `release-build.yml` (on tag: build all variants, upload to releases).
  - [ ] Automate checksum generation and provenance logging (SBOM, build reproducibility).
  - [ ] Wire changelog generation from git commits (conventional commit parsing).

- [ ] **Distribution Channels**
  - [ ] Release artifacts on GitHub Releases (direct download, versioned).
  - [ ] Create package registry schema (`releases/package-registry.json`).
  - [ ] Document installation pathways: direct download, package managers (brew, apt, choco), Docker image.
  - [ ] Create installation guide: `INSTALLATION-v1.4.6.md` (multiple OS/arch combinations).

#### P1 -- Local Library System & Package Management

- [ ] **Library Manager Enhancement**
  - [ ] Expand library manager to support versioned packages (semver constraints: `~1.4.5`, `^1.4.0`, `>=1.4.0`).
  - [ ] Implement `LIBRARY search <name>` (search local + remote registries).
  - [ ] Implement `LIBRARY install <name>@<version>` (pin specific version).
  - [ ] Implement `LIBRARY update <name>` (upgrade to latest compatible).
  - [ ] Implement `LIBRARY update --all` (recursive dependency resolution, safety checks).
  - [ ] Add dependency conflict detection and resolution (warn on circular deps, version mismatches).

- [ ] **Local Library Index & Catalog**
  - [ ] Create `distribution/local-library-catalog.json` (all available local packages).
  - [ ] Include metadata: name, version, description, dependencies, size, checksum, install path.
  - [ ] Add library installation hooks (setup scripts, permission fixes, symlink creation).
  - [ ] Support library namespacing: `@author/library-name` for organization (similar to npm).

- [ ] **Library Update Pipeline**
  - [ ] Implement soft update checks (background service checks for newer versions).
  - [ ] Create `LIBRARY check-updates` command (list available updates).
  - [ ] Implement automatic dependency updates (opt-in via config: `"auto_update": "minor"`).
  - [ ] Add update notifications in Wizard GUI (badge on `#/library` panel showing available updates).
  - [ ] Implement rollback mechanism: `LIBRARY rollback <name> --to <version>`.

- [ ] **Library Sharing & Distribution**
  - [ ] Enable library export as distributable archives: `LIBRARY pack <name> > lib.udos-package`.
  - [ ] Support local installation from archive: `LIBRARY install ./lib.udos-package`.
  - [ ] Enable GitHub-based library registry (users publish libraries to `fredbook/udos-library-registry`).
  - [ ] Wire GitHub sync in Wizard: `LIBRARY sync` pulls latest registry from GitHub.

#### P2 -- Docker Container Hardening & Lifecycle

- [ ] **Container Health & Monitoring**
  - [ ] Implement health checks for all containers in `docker-compose.yml`.
  - [ ] Add liveness probes (containers auto-restart if unhealthy, with backoff).
  - [ ] Add readiness probes (services only marked ready when dependencies (DB, cache) available).
  - [ ] Create `DOCKER health` command: show status of all running containers.
  - [ ] Wire container health to Wizard dashboard (`#/system/docker-health`).

- [ ] **Container Lifecycle Management**
  - [ ] Implement graceful shutdown hooks (send SIGTERM, wait 30s before SIGKILL).
  - [ ] Implement startup order enforcement (dependencies boot first via `depends_on` + health checks).
  - [ ] Create `DOCKER start`, `DOCKER stop`, `DOCKER restart` commands.
  - [ ] Implement `DOCKER logs <service>` tail command (stream service logs in real-time).
  - [ ] Add container resource limits (memory, CPU) to prevent runaway processes.

- [ ] **Network & Storage Hardening**
  - [ ] Isolate containers to custom Docker network (default bridge too permissive).
  - [ ] Implement service-to-service auth (API keys, TLS cert pinning for inter-service calls).
  - [ ] Harden volume mounts (read-only where possible, explicit UID/GID ownership).
  - [ ] Implement data backup mechanism: `DOCKER backup` (export volumes to archive).
  - [ ] Implement data restore: `DOCKER restore <backup-archive>`.

- [ ] **Container Image Security**
  - [ ] Scan Docker images for vulnerabilities at build time (Trivy, Grype, or similar).
  - [ ] Use minimal base images (Alpine where possible, distroless for prod workloads).
  - [ ] Enforce image signing (sign and verify images in `docker-compose.yml`).
  - [ ] Document base image versions and CVE patching process.

#### P3 -- Sonic Standalone Integration & Distribution

- [ ] **Standalone Sonic Distribution**
  - [ ] Build Sonic as bootable ISO (UEFI + MBR fallback) without Wizard dependency.
  - [ ] Verify Sonic boots on USB without full uDOS installation (minimal Core + TUI).
  - [ ] Create Sonic installer script: `sonic-install.sh` (download ISO, write to USB, verify checksum).
  - [ ] Document supported hardware (CPU, RAM, storage, GPU, network requirements).
  - [ ] Test on 5+ diverse hardware targets (laptops, desktops, VMs, ARM boards).

- [ ] **Wizard ↔ Sonic Integration**
  - [ ] Enable Wizard to orchestrate Sonic builds (trigger build from `#/system/sonic`).
  - [ ] Wire build progress reporting to Wizard (live log stream during build).
  - [ ] Implement Sonic boot management: Wizard can create/delete VM boot profiles pointing to ISO.
  - [ ] Add Sonic → Wizard communication bridge (booted Sonic detects Wizard on network, auto-registers).
  - [ ] Create "uDOS Duo" mode: run Sonic on separate machine, connect to Wizard host via SSH.

- [ ] **Sonic Package Updates**
  - [ ] Implement Sonic image versioning (ISO tagged with release version).
  - [ ] Create Sonic update mechanism: `sonic update` checks for new ISO, downloads if available.
  - [ ] Verify ISO integrity (checksum check + GPG signature verification).
  - [ ] Support incremental updates (delta-sync only changed files, not full 1GB+ ISO).

#### P4 -- Testing & Documentation

- [ ] **Distribution Testing**
  - [ ] E2E test all package variants installation (core-slim, wizard-full, sonic-iso, dev-complete).
  - [ ] Test installation on Linux (Ubuntu 20.04, 22.04), macOS (12, 13), Windows (WSL2).
  - [ ] Test upgrades: v1.4.3 → v1.4.6 on all platforms.
  - [ ] Verify no data loss during upgrade (vault and memory preserved).

- [ ] **Library System Testing**
  - [ ] Test library install/update/rollback workflows.
  - [ ] Test dependency resolution (circular deps, version mismatches, missing transitive deps).
  - [ ] Test library sharing (export, import from archive, GitHub registry sync).
  - [ ] Load test library manager (1000+ libraries, metadata parsing performance).

- [ ] **Container System Testing**
  - [ ] Stress test Docker health checks (simulate failures, verify recovery).
  - [ ] Test container startup order (verify all services healthy before marked ready).
  - [ ] Test data backup/restore (full round-trip with large volumes).
  - [ ] Test image security scanning (verify CVE detection, alert blocking).

- [ ] **Sonic Testing**
  - [ ] Boot Sonic on 5+ diverse hardware targets (verify driver detection, network, storage).
  - [ ] Test Sonic → Wizard bridge (auto-registration, SSH tunnel, command execution).
  - [ ] Test ISO update cycle (download, verify, write, reboot).
  - [ ] Test Sonic in VM (VirtualBox, QEMU, Hyper-V).

- [ ] **Documentation**
  - [ ] Create `INSTALLATION-v1.4.6.md`: installation guide for all variants and platforms.
  - [ ] Create `LIBRARY-MANAGEMENT.md`: library browser, install, update, share workflows.
  - [ ] Create `DOCKER-OPERATIONS.md`: container health, logs, backup/restore, troubleshooting.
  - [ ] Create `SONIC-STANDALONE.md`: Sonic boot, setup, updates, Wizard bridge.
  - [ ] Create `PACKAGING-INTERNALS.md`: release process, package structure, artifact signing.

**Reference Artifacts:**
- [PACKAGING-DISTRIBUTION-ARCHITECTURE-v1.4.6.md](specs/PACKAGING-DISTRIBUTION-ARCHITECTURE-v1.4.6.md): Complete packaging system, library catalog, Docker hardening, Sonic integration

---

### v1.4.7 -- Stable Release (Consolidation & Command Audit)

**Goal:** Consolidate v1.4.4 through v1.4.6 work into a single Stable Release, audit and modernize complete command set (legacy concepts preserved but updated), ensure REPAIR/SETUP commands handle all scenarios, eliminate all backwards-compatibility shims, and establish version unification (all installations run v1.4.7 Stable).

**Timeline:** 2026-06-01 to 2026-06-30 (planned)

**Key Focus:** uDOS v1.4.7 is the **first fully-integrated stable release** combining Core hardening, Gameplay lenses, TUI genres, Command dispatch, GitHub Pages publishing, Local libraries, and Docker hardening. No legacy shims, no dual versions, one modern coherent platform.

#### P0 -- Release Consolidation & Version Unification

- [ ] **Consolidate GitHub Releases**
  - [ ] Merge v1.4.4, v1.4.5, v1.4.6 release notes into single v1.4.7 comprehensive release.
  - [ ] Create consolidated `v1.4.7-release-notes.md` (features, breaking changes, migration guide).
  - [ ] Identify and document all breaking changes and deprecations since v1.3.x.
  - [ ] Create migration guide: v1.3.x → v1.4.7 (covers all variant upgrades).

- [ ] **Version Unification**
  - [ ] Enforce version consistency across all components:
    - `uDOS.py`, `version.json` → v1.4.7
    - `wizard/version.json` → v1.4.7
    - `wizard/requirements.txt` → pin versions aligned to v1.4.7
    - Docker image tags → v1.4.7
    - Sonic ISO → v1.4.7
  - [ ] Establish version policy: **no multi-version installations supported; all installations must upgrade to v1.4.7**.
  - [ ] Create deprecation timeline: v1.3.x support ends 2026-09-30, v1.4.0-6 support ends 2026-12-31.
  - [ ] Wire auto-update checks into Core and Wizard (badge notifications, migration warnings).

- [ ] **Legacy Shim Removal & Cleanup**
  - [ ] Audit codebase for any remaining backwards-compatibility shims or legacy aliases.
  - [ ] Remove deprecated command aliases (`core`→`tui`, `server`→`wizard`, `command`→`cmd` already removed).
  - [ ] Remove any feature flags for v1.3.x backwards compat.
  - [ ] Remove stub/placeholder code (mark any TODOs as v1.5+ future work).
  - [ ] Document what was removed and why (changelog for developers).

#### P1 -- Command Audit & Modernization

**Complete Command Set (44+ commands across Core + Wizard):**

- [ ] **Core Commands Audit (18 P0 + Extensions)**
  - Core P0 (Legacy → Modern v1.4.7):
    - `HEALTH` (offline stdlib checks, enhanced diagnostics)
    - `VERIFY` (TS runtime verification, gameplay state validation)
    - `DRAW` (grid rendering, viewport, ASCII art, themes - now includes GENRE support)
    - `PLACE` (workspace/binder navigation, @workspace syntax - enhanced with file picker)
    - `BINDER` (content organization, TOC generation - integrated with libraries)
    - `RUN` (command composition, script execution - enhanced with three-stage dispatch)
    - `PLAY` (gameplay, TOYBOX profiles, lenses - now supports 5 lenses + GENRE themes)
    - `RULE` (conditional automation, gates, progression - expanded for complex workflows)
    - `LIBRARY` (package management - now with versioning, updates, GitHub registry)

  - Spatial/Navigation (v1.3.18+):
    - `GRID` (spatial queries, distance, adjacency, z-aware maps)
    - `MAP` (world visualization, layers, viewport, landmarks)
    - `GOTO` (fast travel, waypoints, region traversal)
    - `FIND` (search locations, entities, content - semantic search support)

  - User State & Progression:
    - `HOME` (personal workspace root, settings, preferences)
    - `WORKSPACE` (active workspace management, context switching)
    - `STORY` (narrative progression, quest chains, achievements)

  - Content Management:
    - `READ` (markdown parsing, metadata extraction, frontmatter)
    - `EXPORT` (PDF export, document generation, publishing)
    - `FILE` (filesystem operations, vault management, media handling)
    - `TALK` (NPC interaction, dialogue, narrative events)
    - `NPC` (entity management, spawning, character state)

  - Interaction & Gameplay:
    - `ANCHOR` (world objects, placement, persistence)
    - `SPAWN` (entity creation, respawn logic, pools)
    - `GHOST` (debug/observation mode, entity tracking)
    - `GRAB`/`BAG` (inventory, item management, container logic)

  - System & Utility:
    - `HELP` (command documentation, interactiveMenu, examples)
    - `LOGS` (log streaming, filtering, debugging)
    - `CONFIG` (configuration editing, validation, schema)
    - `HOTKEY` (keyboard shortcuts, macros, key bindings)
    - `UID`/`TOKEN` (ID generation, authentication tokens)

  - Administrative:
    - `REPAIR` (modernized for v1.4.7: system recovery, health check, venv reset)
    - `SETUP` (v1.4.7 interactive setup: user identity, providers, GitHub config)
    - `DESTROY` (reset/factory reset - DANGEROUS, requires confirmations)
    - `MAINTENANCE` (scheduled tasks, cleanup, optimization)
    - `MIGRATE` (data migration between versions, schema updates)

- [ ] **Wizard Ecosystem Commands (20+)**
  - Provider/Integration:
    - `WIZARD PROV <provider>` (manage providers: GitHub, OpenAI, etc.)
    - `WIZARD INTEG <integration>` (configure integrations: webhooks, soft sync)
    - `WIZARD CHECK` (full network/provider shakedown)

  - GitHub/Publishing:
    - `WIZARD github setup` (GitHub Pages setup, repo auth, PAT storage)
    - `WIZARD github status` (show current GitHub config and sync status)
    - `WIZARD github validate` (test GitHub access/connectivity)

  - Service Management:
    - `WIZARD venv create/activate/doctor/reset` (Python environment management)
    - `WIZARD docker start/stop/restart/health/logs/backup/restore` (container ops)

  - Library/Package:
    - `LIBRARY search/info/list/install/update/uninstall/rollback/pack` (package management)
    - `LIBRARY sync` (GitHub registry refresh)

  - Sonic:
    - `SONIC build` (build ISO + artifact signing)
    - `SONIC boot` (manage boot profiles)
    - `SONIC update` (check/apply ISO updates)

  - Publishing:
    - `PUBLISH --github` (soft sync to GitHub Pages)
    - `PUBLISH --github --hard` (full reset + re-upload)
    - `PUBLISH --config` (edit publishing configuration)

  - Misc:
    - `WIZARD install` (dependency installation)
    - `WIZARD doctor` (diagnostic checks)
    - `WIZARD status` (service status overview)

- [ ] **Command Verification Tests**
  - [ ] Verify all 40+ commands execute without errors.
  - [ ] Verify all commands display correct help text (no orphaned docs).
  - [ ] Verify command aliases resolve correctly (no broken shortcuts).
  - [ ] Verify error handling for invalid subcommands (no confusing messages).
  - [ ] Verify command dispatch chain works: uCODE → Shell → VIBE (with confidence scoring).
  - [ ] Test backwards-incompatible changes (removed commands show explicit errors, not silent failures).

#### P2 -- REPAIR & SETUP Command Hardening

- [ ] **REPAIR Command Modernization (v1.4.7)**
  - [ ] `REPAIR` (default) - comprehensive health check for v1.4.7 stack
    - Verify Core Python env (stdlib-only, no venv contamination)
    - Verify Wizard venv health (requirements.txt consistent)
    - Check Docker daemon (if installed) + container health
    - Verify vault/memory structure (no orphaned v1.3.x folders)
    - Check GitHub Pages config (if publishing enabled)
    - Verify local libraries consistency (catalog.json, lock.json)
    - Report findings with recovery suggestions (no auto-fix unless confirmed)

  - [ ] `REPAIR --full` - comprehensive system recovery
    - Run all checks above
    - Auto-fix: orphaned processes, stale locks, temp files
    - Auto-reset: Wizard venv (reinstall from requirements.txt)
    - Auto-clean: Docker images older than v1.4.6
    - Preserve user data (vault, binders, configs)
    - Generate repair report (what was fixed, warnings, next steps)

  - [ ] `REPAIR --pull` - git pull + install dependencies
    - Check for uncommitted changes (warn or stash with permission)
    - Pull latest from canonical branch (main, not dev)
    - Reinstall dependencies: core (none), Wizard (pip install -r wizard/requirements.txt)

  - [ ] `REPAIR --confirm` - skip all confirmations (for automated recovery scripts)

  - [ ] `REPAIR --health-only` - lightweight check (no fixes, just diagnostics)

  - [ ] REPAIR logging & audit trail
    - Log all repair actions to `memory/system/repair-audit.log`
    - Include timestamps, actions taken, success/failure status
    - Make logs queryable via `LOGS REPAIR` command

- [ ] **SETUP Command Modernization (v1.4.7)**
  - [ ] `SETUP` (interactive story-based setup)
    - Collect user identity (name, DOB, role, location, timezone, OS type)
    - Allow optional password setup (User/Admin roles)
    - Offer GitHub Pages publishing setup (optional, can skip)
    - Offer Wizard service setup (optional, can skip)
    - Generate `.env` file with local settings
    - Test connectivity (GitHub, Wizard server if enabled)

  - [ ] `SETUP --resume` - resume incomplete setup

  - [ ] `SETUP --check` - validate current setup (no changes)

  - [ ] `SETUP --reset` - clear all setup, start over (requires confirmation)

  - [ ] `SETUP --export` - export settings as config file (for backup/migration)

  - [ ] `SETUP --import <file>` - import settings from config file

  - [ ] SETUP validation & error handling
    - Validate all inputs (username format, timezone validity, etc.)
    - Test GitHub PAT validity if provided
    - Check port availability for Wizard server
    - Provide clear error messages for all failures
    - Suggest recovery actions (e.g., "GitHub PAT expired, re-enter at Step 3")

#### P3 -- Release Documentation & Migration

- [ ] **Create Comprehensive v1.4.7 Release Notes**
  - [ ] Executive summary (major features, highlights, why upgrade)
  - [ ] Feature matrix (40+ commands with descriptions + examples)
  - [ ] Breaking changes list (removed commands, changed behaviors, config updates)
  - [ ] Installation guide (all variants: core-slim, wizard-full, sonic-iso, dev-complete)
  - [ ] Upgrade guide (v1.3.x → v1.4.7 step-by-step)
  - [ ] Configuration migration (old configs → v1.4.7 schema, auto-migration script)
  - [ ] Troubleshooting guide (common issues, recovery steps)
  - [ ] Command reference (all 40+ commands with syntax, examples, error codes)

- [ ] **Create Command Reference Sheets**
  - [ ] Cheat sheet: 1-page quickstart (10 most common commands)
  - [ ] Full command matrix: all 40+ commands organized by category
  - [ ] Interactive `HELP` system updates (searchable, examples inline)
  - [ ] Generate command reference as HTML/PDF for offline access

- [ ] **Migration & Upgrade Testing**
  - [ ] Test upgrade paths:
    - v1.3.x (any point) → v1.4.7
    - v1.4.0 → v1.4.7
    - v1.4.3 → v1.4.7 (direct supported upgrade)
    - All variant combinations
  - [ ] Verify data preservation: vault, binders, workspace state, game progress
  - [ ] Verify config migration: old configs auto-converted to v1.4.7 schema
  - [ ] Verify automated recovery: REPAIR --full resolves any post-upgrade issues

#### P4 -- QA & Release Gate

- [ ] **Comprehensive Testing Suite**
  - [ ] Unit tests for all commands (40+ handlers)
  - [ ] Integration tests: command chains, state persistence
  - [ ] E2E tests: full workflows (setup → workspace → gameplay → publish)
  - [ ] Backwards compat tests: verify removed commands return explicit errors
  - [ ] Performance tests: command latency, memory under load, Docker stability
  - [ ] Security tests: no credential leakage, proper RBAC, safe file operations

- [ ] **Release Gate Checklist**
  - [ ] All 40+ commands verified working
  - [ ] REPAIR/SETUP command validated for v1.4.7
  - [ ] Zero known critical bugs in main features
  - [ ] 100% test coverage for command dispatch
  - [ ] All documentation updated and reviewed
  - [ ] Release artifacts signed (GPG)
  - [ ] GitHub release published with consolidated notes
  - [ ] Version unified across all components

- [ ] **Post-Release Support Plan**
  - [ ] Publish v1.4.7 Stable as recommended minimum version
  - [ ] Auto-update notifications for v1.3.x and v1.4.0-6 users
  - [ ] Create support pathways: docs + FAQ + community issues
  - [ ] Monitor first-week bug reports, patch as needed
  - [ ] Begin v1.5.0 planning once v1.4.7 stabilizes

**Reference Artifacts:**
- Command contract: [UCLI-COMMAND-CONTRACT-v1.3.md](specs/UCLI-COMMAND-CONTRACT-v1.3.md) (to be updated to v1.4.7)
- Release notes: [docs/releases/v1.4.7-release-notes.md](releases/v1.4.7-release-notes.md) ✅ Created
- Command reference: `docs/v1.4.7-COMMAND-REFERENCE.md` (to be created)

---

### v1.5.0 (Aspirational)
- [ ] Multi-tenant workspace isolation (separate storage per workspace user).
- [ ] Distributed wizard nodes (cluster mode, load balancing).
- [ ] Audit log and compliance layer (activity tracking, permission controls).
- [ ] Third-party publishing integrations (Medium, Dev.to, Notion export).

---

## Groovebox Roadmap

**Component:** `groovebox/` | **Current:** v1.4.3 (deferred items from v1.4.0 stream) | **Status:** Deferred to v1.4+

### v1.4 stream (Deferred → v1.4+)

Groovebox P0 pipeline was deferred from the v1.4.0 implementation stream to keep release scope focused on Core containerization and library management. The Songscribe Dockerfile and Groovebox smoke gate were completed in the v1.4 stream and consolidated in v1.4.3; the full parser/synthesis pipeline moves to v1.4+.

### v1.4+ -- Songscribe Pipeline

#### P0 -- Must Have
- [ ] Songscribe parser: tokenizer and AST for `.songscribe` markdown grammar.
- [ ] Audio synthesis pipeline: render AST nodes to audio buffers.
- [ ] MIDI export: generate Standard MIDI files from Songscribe AST.
- [ ] WAV export: PCM render pipeline with configurable sample rate/depth.
- [ ] Transport layer for Wizard: stdio/WebSocket bridge to wizard server.

#### P1 -- Should Have
- [ ] Sample library manager: download, index, tag, and resolve samples.
- [ ] Live preview transport: real-time audio playback during editing.
- [ ] Instrument definitions: built-in synth patches and drum kits.
- [ ] Songscribe CLI: `udos songscribe render <file>` command.
- [ ] Tempo and time signature handling: BPM, meter changes in AST.

#### P2 -- Nice to Have
- [ ] MP3/OGG export: compressed format output via ffmpeg.
- [ ] Effect chain DSL: reverb, delay, EQ as Songscribe directives.
- [ ] Pattern sequencer: loop and arrangement blocks in grammar.
- [ ] Web preview widget: embeddable player for wizard dashboard.
- [ ] MIDI input capture: record from MIDI controller to Songscribe.

---

## Sonic Roadmap

**Scope:** Standalone USB builder, device database, and uDOS compatibility.

### Now (v1.3.0)
- [x] Document standalone contract and decoupleable packaging.
- [x] Specify Ventoy-free partition layout.
- [x] Add Windows 10 install/WTG modes.
- [x] Define uDOS TUI minimal image target.
- [x] Expand device database schema (windows/media flags).

### Next (v1.2.x)
- [x] Implement custom partitioning scripts.
- [x] Create bootloader profiles and reboot routing.
- [x] Add uDOS Windows launcher and mode selector.
- [x] Establish dataset validation and build scripts.

### Later (v1.3+)
- [x] Device profile auto-detection and recommendations.
- [x] Media console workflows (Kodi + WantMyMTV).
- [x] Windows gaming profile automation.
- [x] Public standalone releases and install guide.

### v1.3.17 Status (2026-02-15)
- [x] Ventoy removed from active Sonic pipeline and contracts.
- [x] Native UEFI fields adopted (`uefi_native`, `ESP`) across Sonic datasets/API/docs.
- [x] Legacy Ventoy scripts/config physically removed from Sonic submodule.
- [x] Sonic standalone release artifacts/checksums/signing flow finalized.
- [x] Wizard GUI Sonic entry points fully implemented end-to-end.

Reference decisions:
- [u_dos_alpine_thin_gui_runtime_spec_chromium_kiosk_standard.md](decisions/u_dos_alpine_thin_gui_runtime_spec_chromium_kiosk_standard.md)
- [sonic_db_spec_stub_gpu_profiles_thin_ui_launch_profiles.md](decisions/sonic_db_spec_stub_gpu_profiles_thin_ui_launch_profiles.md)

---

## Empire Roadmap

Versioning target:
- Beta: v0.0.1 (current)
- Alpha: v1.0.0 (target)

### Phase 1: Internal Beta (v0.0.1)
- Full test matrix run (API, ingest, normalize, UI).
- Smoke suite for API, ingest, normalize, and UI.
- Bug triage labels and daily triage routine.

### Phase 2: Alpha Stabilization
- Fix P0/P1 from beta.
- Svelte UI stabilization: loading/error/empty states and responsiveness.
- Pipeline reliability improvements (ingest to normalize to store).

### Phase 3: Integrations Test Round (No Live Data)
- Test harness for each integration with mock/sandbox data.
- Config validation and error surfaces.
- E2E test script: import to normalize to API to UI.

### Phase 4: Pre-Alpha Hardening
- Performance pass (response times, batch ingest).
- DB backup/restore sanity check.
- Security checklist (secrets, tokens, rate limits).

### Phase 5: Live Data Connect and Launch (Alpha v1.0.0)
- Live data connectivity playbook.
- Monitoring checklist and rollback plan.
- Release notes and operator guide.

---

## Obsidian Companion (External)

- Ownership moved to private pre-release repo: `fredporter/oc-app`.
- App-specific roadmap/TODOs now live in `oc-app` issues and milestones.
- uDOS monorepo is under development and does not ship `/app`.

### uDOS-side TODOs (Integration Only)
- [x] Define Wizard web view host contract for external app content.
- [x] Define rendering API contract (HTML/asset handoff, cache behavior, versioning).
- [x] Define auth/session boundary between Wizard and external Obsidian Companion flows.
- [x] Add compatibility tests for Wizard rendering integration points.
- Draft contract: [OBSIDIAN-COMPANION-INTEGRATION-CONTRACT.md](specs/OBSIDIAN-COMPANION-INTEGRATION-CONTRACT.md).

### Migrated TODOs (Now in `oc-app`)
- `app/Sources/Automation/TaskScheduler.swift`: launchd generation/unload/execute TODOs.
- App product milestones previously tracked in this file now tracked in `oc-app`.
