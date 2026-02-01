# Roadmap: Rounds 3–10 (2026)

This spec consolidates the outstanding development rounds outlined in `docs/ROADMAP.md` and gives owners clear deliverables, reference specs, and status indicators so contributors can move quickly.

## Round 3 — Wizard Web UI / Notion Blocks + Plugin Dashboard (Svelte + Tailwind)
- **Owner:** Wizard
- **Status:** Design complete, implementation ongoing
- **Deliverables:** Notion block components, webhook status panel, theme system, plugin browser (cards, enable/disable, update checks) and mod overlay controls.
- **References:** `docs/specs/wiki_spec_obsidian.md`, `wizard/docs/INTERACTIVE-CONSOLE.md`, `wizard/ARCHITECTURE.md`
- **Next actions:** Build Svelte components, hook plugin API routes (`wizard/server.py`), wire plugin install/update/uninstall workflows.

## Round 4 — Wizard Web Browser / Dataset Tables + SQLite Binding
- **Owner:** Wizard (Dashboard)
- **Status:** Planning
- **Deliverables:** Sortable/filterable dataset table, chart view, `/api/data/*` endpoints for tables/query/schema/export, spatial tagging filters.
- **References:** `docs/specs/file-parsing-architecture.md`, `specs/grid-spatial-computing.md`
- **Next actions:** Implement FastAPI routes, build Svelte Table + Chart components, add pagination/performance guardrails.

## Round 5 — Wizard Web Browser / Teletext Mode + NES Buttons
- **Owner:** Wizard (Dashboard)
- **Status:** Design phase
- **Deliverables:** Canvas-based teletext renderer, NES-style button kit, input handling (keyboard/mouse), Svelte wrapper, dark-mode palette.
- **References:** `docs/specs/grid-spatial-computing.md`, teletext/VT340 references.
- **Next actions:** Prototype Canvas renderer, finalize NES button recommendation, connect to teletext API endpoints.

## Round 6 — Beacon Portal + Sonic Device Catalog (WiFi + VPN)
- **Owner:** Wizard + Sonic documentation
- **Status:** Specification ready
- **Deliverables:** Beacon portal APIs, device database routes, WireGuard configs, quota throttles, Sonic/Beacon docs (`docs/wiki/BEACON-...`), Sonic DB integration in `wizard/routes/sonic_routes.py`.
- **References:** `sonic/docs/specs/sonic-screwdriver-v1.1.0.md`, `docs/wiki/BEACON-PORTAL-DELIVERY.md`
- **Next actions:** Harden `/api/sonic` DB, add quota enforcement middleware, publish Sonic dataset updates.

## Round 7 — Goblin Dev Server Experiments
- **Owner:** Goblin team
- **Status:** Experimental
- **Deliverables:** Binder compiler service, Screwdriver flash pack, MeshCore device manager; features that graduate to Wizard/Core.
- **Next actions:** Surface stable features to Wizard (binder, device manager), archive experiments once migrated.

## Round 8 — Wizard Plugin Ecosystem + Bolt-On Distribution
- **Owner:** Wizard (and extensions)
- **Status:** Architecture design
- **Deliverables:** Plugin manifest spec, package manager service, distribution repo, UI for install/update/disable, mod overlay loader, permission model, version tracking via `memory/wizard/plugins.db`.
- **References:** `docs/specs/PLUGIN-ARCHITECTURE.md` (forthcoming), `wizard/server.py` plugin routes.
- **Next actions:** Publish manifest spec, implement `PackageManager` service, add plugin registry endpoints, integrate uCODE `PLUGIN` command, document overlay conventions.

## Round 9 — App Typo Editor (Tauri) + Converters
- **Owner:** App team
- **Status:** Early development
- **Deliverables:** Typo editor core, markdown converters (PDF/HTML), typography system, emoji/pixel renderer, uCode runtime embed.
- **References:** `specs/app-file-extensions.md`, `docs/specs/mac-app-roadmap.md`
- **Next actions:** Scaffold Tauri project, implement editor + converter pipeline, connect to runtime APIs.

## Round 10 — Groovebox + Songscribe
- **Owner:** Wizard (audio/creativity)
- **Status:** Planning
- **Deliverables:** Sample library database + waveform generator, Songscribe Markdown music syntax, step sequencer/pattern editor, audio synthesis/export (WAV/MIDI/PDF), Wizard sample APIs.
- **References:** `sonic/docs/specs/sonic-stick-media-addon-brief.md`, future `docs/specs/GROOVEBOX-SONGSCRIBE.md` and Songscribe syntax guide.
- **Next actions:** Finalize Songscribe grammar, implement service + UI (sample browser, pattern editor), expose playback/export endpoints.

## Core TUI Stability & Training

- **Owner:** Core
- **Status:** Active
- **Focus:** Keep Core TUI as the bedrock for future rounds by documenting hot-reload/self-heal habits, locking the new script executor guard and test suite, and maintaining story handler tests/fallbacks.
- **References:** `core/services/hot_reload.py`, `core/services/self_healer.py`, `core/src/executors/script-executor.ts`, `tui/tests/test_form_fields.py`, `tests/test_setup_handler.py`, `tests/test_story_form_handler.py`
- **Next actions:** 
  1. Record how to start/stop the hot reload watcher and interpret self-heal output for Core contributors.  
  2. Keep regression coverage for DateTime approval/override inputs and the script executor guard current.  
  3. Monitor fallback execution so SimpleFallbackFormHandler remains reliable on non-interactive terminals.

---
**Tracking note:** Publish this spec via `/docs/specs/ROUNDS-3-10.md` and keep it updated whenever the referenced rounds advance.
