# uDOS Roadmap (Canonical)

Last updated: 2026-02-15

This file is the single canonical roadmap for uDOS. Legacy detail lives in [docs/devlog/ROADMAP-LEGACY.md](devlog/ROADMAP-LEGACY.md).

---

## Status Summary

- Core concept: uDOS is a local Obsidian companion runtime focused on `@workspace`/`@binder` organization, fractal/layered filesystem structures, knowledge-tree navigation, and digital-garden workflows.
- Milestones v1.3.0 to v1.3.7: complete (archived records exist).
- Current focus: stabilization and polish for v1.4.0 release.
- Outstanding (active): none; all P0 items complete as of 2026-02-09.
- Dev mode policy: `/dev/` public submodule required and admin-only; see [DEV-MODE-POLICY.md](DEV-MODE-POLICY.md).
- Core/Wizard boundary: `core` is the base runtime; `wizard` is the brand for connected services. Core can run without Wizard (limited). Wizard cannot run without Core.
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

### P1 -- Platform and Extensions
- [x] Reintroduce Empire business features on new extension spine.

### P2 -- Code Quality (Pre-v1.4)
- [x] Review long route factory functions for modularization.
- [x] Consider splitting nested route handlers into separate modules.

---

## Core Roadmap (uDOS)

### v1.4.0 -- Repo Restructure and Containerisation

#### P0 -- Repo Restructure (Complete)
- [x] Root cleanup: removed ephemeral debug/fix files.
- [x] Wizard consolidation: merged `api/wizard/`, `mcp/wizard/`, `core/wizard/` into `wizard/`.
- [x] Removed compatibility shims (`services/` to direct `core.services` imports).
- [x] Workspace filesystem: deprecated root `vault/` in favor of `memory/vault/`.
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
- [x] Wire `@workspace` syntax in Core TUI (WORKSPACE, TAG, LOCATION, BINDER commands).
- [x] Implement workspace switching in file pickers and readers.
- [x] Update Wizard routes to use workspace-aware vault paths.

#### P1 -- Containerisation
- [ ] Sonic Screwdriver Dockerfile (ISO/USB builder).
- [ ] Songscribe/Groovebox Dockerfile.
- [ ] Verify all `docker compose --profile` combinations work.
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
- Document standalone contract and decoupleable packaging.
- Specify Ventoy-free partition layout.
- Add Windows 10 install/WTG modes.
- Define uDOS TUI minimal image target.
- Expand device database schema (windows/media flags).

### Next (v1.2.x)
- Implement custom partitioning scripts.
- Create bootloader profiles and reboot routing.
- Add uDOS Windows launcher and mode selector.
- Establish dataset validation and build scripts.

### Later (v1.3+)
- Device profile auto-detection and recommendations.
- Media console workflows (Kodi + WantMyMTV).
- Windows gaming profile automation.
- Public standalone releases and install guide.

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
- [ ] Define Wizard web view host contract for external app content.
- [ ] Define rendering API contract (HTML/asset handoff, cache behavior, versioning).
- [ ] Define auth/session boundary between Wizard and external Obsidian Companion flows.
- [ ] Add compatibility tests for Wizard rendering integration points.
- Draft contract: [OBSIDIAN-COMPANION-INTEGRATION-CONTRACT.md](specs/OBSIDIAN-COMPANION-INTEGRATION-CONTRACT.md).

### Migrated TODOs (Now in `oc-app`)
- `app/Sources/Automation/TaskScheduler.swift`: launchd generation/unload/execute TODOs.
- App product milestones previously tracked in this file now tracked in `oc-app`.
