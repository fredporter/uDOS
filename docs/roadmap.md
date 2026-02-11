# uDOS Roadmap (Canonical)

Last updated: 2026-02-11

This file is the single canonical roadmap for uDOS. Legacy detail lives in [docs/devlog/ROADMAP-LEGACY.md](devlog/ROADMAP-LEGACY.md).

---

## Status Summary

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
- Bumped versions: `uDOS` to v1.3.9, `Wizard` to v1.1.2.

---

## Active Checklist (Merged)

Last updated: 2026-02-09

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
- [x] App submodule: archived Tauri v1, promoted ObsidianCompanion to `/app/`.

#### P0 -- Workspace Filesystem (@workspace)
- [x] Scaffold all workspace dirs under `memory/`.
- [ ] Wire `@workspace` syntax in Core TUI (WORKSPACE, TAG, LOCATION, BINDER commands).
- [ ] Implement workspace switching in file pickers and readers.
- [ ] Update Wizard routes to use workspace-aware vault paths.

#### P1 -- Containerisation
- [ ] Sonic Screwdriver Dockerfile (ISO/USB builder).
- [ ] Songscribe/Groovebox Dockerfile.
- [ ] Verify all `docker compose --profile` combinations work.
- [ ] Library manager: `LIBRARY sync` and `LIBRARY status` commands.

#### P2 -- Code Quality and Modularization
- [ ] Review long route factory functions for modularization opportunities:
  - `wizard/routes/ucode_routes.py` (~1200 lines)
  - `wizard/routes/config_routes.py` (~1350 lines)
  - `wizard/routes/provider_routes.py` (~1150 lines)
  - `core/commands/destroy_handler.py` (~1000 lines)
  - `core/commands/setup_handler.py` (~730 lines)
- [ ] Consider splitting nested route handlers into separate modules.

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
- [ ] Web publishing pipeline (moved from OC-app): monorepo deploy path and hosting targets.

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

## App Roadmap

- SwiftUI/Xcode app lives in `/app` (Package.swift, Sources, Resources, Tests).
- Previous Tauri/Svelte app archived at `/app/.archive/2026-02-11-tauri-app`.
- External vault path support.
- Local HTML export only: write `index.html` in the vault/binder folder and `html/` for linked pages.
- Online publishing moved to Wizard roadmap (future dev round).
- Typo editor: in-app quick editing surface.
- Typo upgrades after next testing round (editor UX, file browser, preview).
- Typo integration bridge: Svelte bundle embedded in SwiftUI via WKWebView, JS bridge for file IO and markdown events.
- Tasks index.
- Export UI.

App docs live under [app/docs](../app/docs).
