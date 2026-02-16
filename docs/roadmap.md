# uDOS Roadmap (Canonical)

Last updated: 2026-02-15

This file is the single canonical roadmap for uDOS. Legacy detail lives in [docs/devlog/ROADMAP-LEGACY.md](devlog/ROADMAP-LEGACY.md).

---

## Status Summary

- Core concept: uDOS is a local Obsidian companion runtime focused on `@workspace`/`@binder` organization, fractal/layered filesystem structures, knowledge-tree navigation, and digital-garden workflows.
- Milestones v1.3.0 to v1.3.7: complete (archived records exist).
- Current focus: v1.3.23 Core Stabilization Round A as the final quality ramp into v1.4.0.
- Outstanding (active): v1.4.0 platform/containerization and Wizard publish roadmap items remain open; v1.3.16 command/boundary refactor is complete.
- Dev mode policy: `/dev/` public submodule required and admin-only; see [DEV-MODE-POLICY.md](DEV-MODE-POLICY.md).
- Core/Wizard boundary: `core` is the base runtime; `wizard` is the brand for connected services. Core can run without Wizard (limited). Wizard cannot run without Core.
- Python environment boundary (2026-02-15): Core Python is stdlib-only and must run without a venv; Wizard owns third-party Python in `/wizard/.venv`; `/dev` piggybacks Wizard venv; Core TS runtime remains optional/lightweight.
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
- Scaffolded gameplay hooks (`GPLAY` command + persistent XP/HP/Gold + progression gates) and initial TOYBOX profiles (`hethack`, `elite`) with Wizard container route exposure.
- Replaced TOYBOX launch stubs with PTY-based upstream adapter services (`hethack`, `elite`) and wired event-driven gate/stat updates via Core gameplay tick ingestion.
- Added TOYBOX container expansion (`rpgbbs`, `crawler3d`), standardized gameplay progress fields (`level`, `achievement_level`, `location.grid/z`, metrics), and `PLAY` command conditional/token unlock flow.
- Added `RULE` command scaffold for gameplay IF/THEN automations that evaluate normalized TOYBOX state and trigger gameplay actions/tokens.
- Published TOYBOX variable comparison spec: `docs/specs/TOYBOX-CONTAINER-VARIABLE-COMPARISON-v1.3.md`.
- Added gameplay tutorial/template assets (wireframe demo + historical era variants) and seeded `gameplay-wireframe-demo-script.md` into framework system seeds.
- Added v1.3.22 world-lens MVP bootstrap: `GPLAY LENS` status/toggle command surface + single-region 3D lens readiness service behind feature flag.
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

Last updated: 2026-02-15

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
  - [x] `udos wizard ...` and `udos dev ...` fail with install guidance if `/wizard/.venv` is missing.
  - [x] `udos ts ...` reports missing Node and falls back to Core mode when possible.
- [x] Ensure Wizard dependency pinning policy is enforced (`requirements.txt`/lockfile committed and used by install path).
- [x] Add/verify `udos wizard install` and `udos wizard doctor` for venv lifecycle checks.

### P1 -- Platform and Extensions
- [x] Reintroduce Empire business features on new extension spine.

### P2 -- Code Quality (Pre-v1.4)
- [x] Review long route factory functions for modularization.
- [x] Consider splitting nested route handlers into separate modules.

---

## Core Roadmap (uDOS)

### v1.4.0 -- Repo Restructure and Containerisation

Reference:
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
- [x] Keep Wizard Python dependencies isolated to `/wizard/.venv`.
- [x] Keep `/dev` tooling on Wizard venv only (no separate default dev venv).
- [x] Add boundary tests for `core` (system Python), `wizard/dev` (venv required), and `ts` (Node capability-gated).

#### P1 -- Containerisation
- [x] Sonic Screwdriver Dockerfile (ISO/USB builder).
- [x] Songscribe/Groovebox Dockerfile.
- [x] Verify all `docker compose --profile` combinations work.
- [ ] Library manager: `LIBRARY sync` and `LIBRARY status` commands.

#### P2 -- Code Quality and Modularization
- [ ] Review long route factory functions for modularization opportunities:
  - [x] `wizard/routes/ucode_routes.py` (modularized from ~1059 -> ~263 lines; split into `ucode_meta_routes.py`, `ucode_ok_routes.py`, `ucode_user_routes.py`, `ucode_dispatch_routes.py`, `ucode_setup_story_utils.py`, `ucode_dispatch_utils.py`, `ucode_ok_execution.py`, `ucode_ok_mode_utils.py`, `ucode_ok_dispatch_core.py`, `ucode_ok_stream_dispatch.py`, `ucode_route_utils.py`, `ucode_stream_utils.py`, `ucode_command_utils.py`)
  - [x] `wizard/routes/config_routes.py` (now split into core routes + `config_routes_helpers.py` + `config_admin_routes.py` + `config_ssh_routes.py`; compatibility wrappers removed)
  - [x] `wizard/routes/provider_routes.py` (now split: route + `ollama_route_utils.py`)
  - [x] `wizard/routes/setup_routes.py` (phase modularization complete; core endpoints moved to `setup_core_routes.py`, helpers moved to `setup_route_utils.py`, `/story/*` moved to `setup_story_routes.py`, `/profile/*` + `/installation/*` moved to `setup_profile_routes.py`, `/locations/*` + timezone endpoint moved to `setup_location_routes.py`, `/wizard/*` moved to `setup_wizard_routes.py`, `/paths*` moved to `setup_path_routes.py`)
  - [x] `core/commands/destroy_handler.py` (now split: handler + `destroy_handler_helpers.py`)
  - [x] `core/commands/setup_handler.py` (now split: handler + `setup_handler_helpers.py`)
- [x] Consider splitting nested route handlers into separate modules.

---

## Wizard Roadmap

**Component:** `wizard/` | **Current:** v1.3.12 | **Status:** Active Development

### v1.3.15 -- Publish Spec Refactor (Planned)

#### P0 -- Must Have
- [ ] Define and approve Wizard web publish contract for monorepo/module model.
- [ ] Implement provider capability registry for publish routes.
- [ ] Add canonical publish API surface and dashboard publish views.
- [ ] Enforce module-aware publish gating (`/dev`, `sonic`, `groovebox`, external app adapters).
- [ ] Add release-gate tests for publish lifecycle + manifest integrity.

Reference: [WIZARD-WEB-PUBLISH-SPEC-v1.3.15.md](specs/WIZARD-WEB-PUBLISH-SPEC-v1.3.15.md)

### v1.4.0

#### P0 -- Must Have
- [ ] Library manager completion: full CRUD, versioning, dependency resolution.
- [ ] Web proxy implementation: reverse proxy for container-hosted services.
- [ ] Workspace routing: `@workspace` syntax for routing requests to named contexts.
- [ ] MCP gateway hardening: auth, rate limiting, tool registration protocol.
- [ ] Unified config layer: single config source of truth across `wizard/`.

#### P1 -- Should Have
- [ ] Container orchestration: compose-based multi-container lifecycle management.
- [ ] Plugin marketplace: discovery, install, update flow via plugin registry.
- [ ] Provider health checks: automated provider availability monitoring.
- [ ] Extension hot-reload: live reload for wizard extensions without restart.
- [ ] Dashboard WebSocket events: real-time status push to web-admin.

#### P2 -- Nice to Have
- [ ] Self-heal route expansion: broader automated recovery strategies.
- [ ] Diagram generation service: server-side diagram rendering pipeline.
- [ ] Songscribe route integration: bridge groovebox transport into Wizard API.
- [ ] GitHub integration polish: PR and issue automation helpers.
- [ ] GitHub Actions publish sync (from OC-app) when moving beyond direct push.

### v1.5.0 (Planned)
- [ ] Multi-tenant workspace isolation.
- [ ] Distributed wizard nodes (cluster mode).
- [ ] Audit log and compliance layer.

---

## Groovebox Roadmap

**Component:** `groovebox/` | **Current:** v1.3.12 | **Status:** Early Development

### v1.4.0

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
- [ ] Public standalone releases and install guide.

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
