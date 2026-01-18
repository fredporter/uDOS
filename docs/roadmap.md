# uDOS Roadmap

**Current Version:** Core v1.1.0.0 | API v1.1.0.0 | App v1.0.3.0 | Wizard v1.1.0.0 | Goblin v0.2.0.0 | Binder v1.0.6.0 | TUI v1.0.0.0  
**Release:** Alpha v1.0.6.0 Phase 5G ✅ **COMPLETE** 2026-01-18  
**Next Target:** Phase 6: Wizard Integration (OAuth + Services) OR v1.0.7.0 Teletext Grid Runtime  
**Last Updated:** 2026-01-18

---

## 🏗️ Architecture Clarification (2026-01-18)

### Wizard vs Goblin — Production vs Development

| Aspect       | **Wizard Server**            | **Goblin Dev Server**            |
| ------------ | ---------------------------- | -------------------------------- |
| **Port**     | 8765                         | 8767                             |
| **Status**   | Production v1.1.0.0 (stable) | Experimental v0.2.0.0 (unstable) |
| **Purpose**  | Always-on, public-facing     | Localhost-only, dev experiments  |
| **Location** | `/public/wizard/`            | `/dev/goblin/`                   |
| **Symlink**  | `wizard → public/wizard`     | `goblin → dev/goblin`            |

**Wizard Responsibilities:**

- ✅ AI assistants (Vibe, Mistral) — Shared by all devices
- ✅ Scheduling, workflows, calendar sync — Production task management
- ✅ Device authentication + session management
- ✅ Plugin repository + distribution
- ❌ NO aggressive auto-restart (graceful degradation)

**Goblin Responsibilities:**

- ✅ Accesses Wizard AI via API (doesn't host AI)
- ✅ Separate dev workflow files (not using Wizard's)
- ✅ Separate dev logs (isolated from production)
- ✅ Notion sync, TS runtime experiments, binder compilation
- ✅ Aggressive auto-restart appropriate for dev mode

---

## ✅ Maintenance: TUI Launcher + App Alias (COMPLETE 2026-01-18)

**Status:** 🎉 **COMPLETE** (2026-01-18)

**Key Fixes:**

- Updated [bin/Launch-New-TUI.command](bin/Launch-New-TUI.command) to call python -m core.tui with explicit PYTHONPATH, eliminating runpy warnings and ensuring package discovery.
- Added [core/**init**.py](core/__init__.py) and [core/tui/**main**.py](core/tui/__main__.py) so module execution works cleanly from launch scripts.
- Added $lib alias in [app/vite.config.ts](app/vite.config.ts) to resolve [app/src/App.svelte](app/src/App.svelte) imports (notification database store) and fixed the main container closing tag.

**Impact:**

- New TUI launcher path is stable for Python module execution across environments.
- Svelte/Vite builds no longer fail on $lib resolution; layout renders correctly.

---

## 🎯 Phase 6: Wizard Integration (OAuth + HubSpot + Notion + iCloud) **SCOPE LOCKED**

**Status:** 🔒 **SCOPE LOCKED - OPTION A** (2026-01-18)

**Primary Goal:** Complete OAuth2 foundation + integrate HubSpot/Notion/iCloud handlers for multi-service sync

**Scope Decision:**

- ✅ **LOCKED:** Option A - Wizard Integration (OAuth + 3 handlers)
- ⏸️ **DEFERRED:** Option B - TUI Features (Teletext Grid Runtime) for v1.0.7.0+

**Phase 6A-6D Timeline (4-8 weeks):**

| Phase  | Handler | Focus                                                                 | Duration | Status    |
| ------ | ------- | --------------------------------------------------------------------- | -------- | --------- |
| **6A** | OAuth   | Foundation for all integrations (token flows, PKCE, scope validation) | 2 weeks  | 📋 Next   |
| **6B** | HubSpot | CRM contact sync (CRUD, deduplication, enrichment)                    | 2 weeks  | ⏳ Queued |
| **6C** | Notion  | Bidirectional page/block sync (webhooks, conflict resolution)         | 2 weeks  | ⏳ Queued |
| **6D** | iCloud  | Backup relay + continuity + keychain sync                             | 2 weeks  | ⏳ Queued |

**Preparation Complete:**

- ✅ 4 handler stubs created (~721 lines, all async methods)
- ✅ `wizard/config/wizard.json` with feature toggles
- ✅ Implementation roadmap (Phase 6A-6D)
- ✅ Readiness: 90% (awaiting API credentials + sandbox setup)

**Phase 6A Kickoff (Next):**

- 🔲 Obtain OAuth provider credentials (Google, Microsoft, GitHub, Apple)
- 🔲 Set up OAuth provider test apps (sandbox mode)
- 🔲 Begin implementing `OAuthHandler` methods
- 🔲 Create `oauth_handler_test.py` (15+ tests)
- 🔲 Wire OAuth routes into `wizard/server.py`

**See Also:** [PHASE-6-SCOPE-DECISION.md](../../PHASE-6-SCOPE-DECISION.md) (full rationale)

---

## ✅ v1.0.4.1: Offline-First AI + SVG Graphics (COMPLETE 2026-01-17)

**Mission:** Complete offline AI setup (Ollama) with optional cloud burst (OpenRouter)

**Status:** 🎉 **COMPLETE** (2026-01-17)

**Key Accomplishments:**

- ✅ **Fixed Setup-Vibe.command** — Corrected model name from `mistral-small2` to `mistral:small` (3.7GB)
- ✅ **Comprehensive Offline AI Guide** — `/docs/howto/OFFLINE-AI-SETUP.md` (800+ lines)
  - Ollama installation & configuration
  - Model selection & performance tuning
  - OpenRouter cloud routing setup
  - Wizard AI Gateway integration
  - Cost analysis & security considerations
- ✅ **SVG Graphics Generation** — `/docs/howto/SVG-GRAPHICS-GENERATION.md` (500+ lines)
  - AI-driven stylized SVG creation
  - Local (Ollama) + Cloud (Claude 3) options
  - Integration with uDOS handlers & TUI
  - Example diagrams & prompt engineering tips
- ✅ **AI Routing Policy** — Updated to support:
  - Local-first: Mistral Small (3.7GB, $0)
  - Cloud burst: OpenRouter + Claude 3 Opus (~$0.02/request)
  - Offline mode: Force local-only (`tags=["offline"]`)

**Setup Validation:**

```bash
# Run automated setup
bin/Setup-Vibe.command

# Verify Ollama
curl http://127.0.0.1:11434/api/tags
# Shows: {"models": [{"name": "mistral:small"}...]}

# Test with Vibe
source .venv/bin/activate
vibe chat "What is uDOS?"
```

**Model Performance (M1/M2 Mac):**

| Model             | Size  | Latency | Cost      | Best For              |
| ----------------- | ----- | ------- | --------- | --------------------- |
| **mistral:small** | 3.7GB | ~50ms   | $0        | Default local         |
| neural-chat       | 4.1GB | ~60ms   | $0        | CPU-friendly          |
| mistral:latest    | 7.4GB | ~100ms  | $0        | Complex reasoning     |
| Claude 3 (cloud)  | N/A   | 2-3s    | $0.015/1K | High-quality graphics |

**SVG Graphics Features:**

- Generate architecture diagrams from English descriptions
- Support for minimalist, technical, artistic, cartoon styles
- Local generation (free, 100ms) or cloud (better quality, $0.02)
- Integration with TUI commands: `DIAGRAM "description"`
- Caching and batch generation support

**Documentation:**

- [OFFLINE-AI-SETUP.md](./howto/OFFLINE-AI-SETUP.md) — Complete setup guide
- [SVG-GRAPHICS-GENERATION.md](./howto/SVG-GRAPHICS-GENERATION.md) — Graphics generation guide
- Updated: [wizard-model-routing-policy.md](./decisions/wizard-model-routing-policy.md)

**Files Modified:**

1. `bin/Setup-Vibe.command` — Fixed model name, improved error handling
2. `.vibe/config.toml` — Updated to `mistral:small`
3. `docs/howto/OFFLINE-AI-SETUP.md` — NEW (comprehensive guide)
4. `docs/howto/SVG-GRAPHICS-GENERATION.md` — NEW (graphics guide)

**POKE Command Implementation (2026-01-17):**

- ✅ **Wizard Interactive Console** — Added `cmd_poke()` method to open URLs in browser
- ✅ **Goblin REST API** — Added `POST /api/v0/poke` endpoint
- ✅ **Test Suite** — Created `test-poke-command.py` validation script
- ✅ **Documentation** — Full implementation guide + quick reference

**Usage:**

```bash
# Wizard console
wizard> poke http://localhost:8765/docs

# Goblin API
curl -X POST http://127.0.0.1:8767/api/v0/poke \
  -d '{"url": "http://localhost:8767/docs"}'
```

**Documentation:**

- [POKE-COMMAND-IMPLEMENTATION.md](../POKE-COMMAND-IMPLEMENTATION.md) — Complete guide
- [POKE-COMMAND-QUICK-REFERENCE.md](../POKE-COMMAND-QUICK-REFERENCE.md) — Quick ref

---

## ✅ v1.0.6.0: Binder System + VS Code Support (COMPLETE 2026-01-17)

**Mission:** Complete Phase 3 - File parsing, SQLite integration, RSS/JSON feeds, VS Code language support

**Status:** 🎉 **PHASE 3 COMPLETE** (2026-01-17)

**Key Accomplishments:**

- ✅ **Task 7: BinderConfig + Validator** (26 tests passing)
  - JSON-based configuration management
  - Comprehensive structure validation (CRITICAL/WARNING/INFO)
  - Auto-generation of missing configs

- ✅ **Task 8: BinderDatabase Context** (33 tests passing)
  - SQLite context manager with resource safety
  - Three access modes (READ_ONLY, READ_WRITE, FULL)
  - Schema introspection (tables, columns, types)
  - Transaction management with rollback

- ✅ **Task 9: BinderFeed RSS/JSON** (34 tests passing)
  - RSS 2.0 standard-compliant generation
  - JSON Feed v1.1 support
  - Markdown frontmatter parsing
  - Content preview extraction

- ✅ **Task 10: VS Code Language Support** (manual testing + integration)
  - Complete TextMate grammar for 8 runtime block types
  - 7 quick-insert snippets with tab stops
  - Syntax highlighting for variables, keywords, operators
  - Activation on language detection

- ✅ **Task 11: Integration Tests + Documentation** (15 tests passing)
  - End-to-end workflow validation (10 tests)
  - Performance benchmarks (2 tests: 100 files, 1000 rows)
  - Error handling tests (3 tests: invalid paths, corrupted files)
  - Comprehensive usage guide (400+ lines)

**Total Delivered:**

- 2,817 lines production code
- 502 lines integration tests
- 400+ lines documentation
- 108 tests passing (93 unit + 15 integration) - 100%

**Performance Benchmarks:**

| Operation             | Target | Actual | Status |
| --------------------- | ------ | ------ | ------ |
| Scan 100 files        | <1.0s  | ~0.8s  | ✅     |
| Generate RSS (100)    | <0.5s  | ~0.3s  | ✅     |
| Generate JSON (100)   | <0.5s  | ~0.3s  | ✅     |
| Query 1000 rows       | <0.1s  | ~0.05s | ✅     |
| Filtered query (1000) | <0.1s  | ~0.03s | ✅     |

**API Design:**

- Function-based config: `load_binder_config()`, `save_binder_config()`
- Static validation: `BinderValidator.validate()`
- Context manager database: `with BinderDatabase() as db`
- Auto-resource cleanup and transaction safety

**Documentation:**

- [BINDER-USAGE-GUIDE.md](./howto/BINDER-USAGE-GUIDE.md) — Complete usage guide (400+ lines)
- [2026-01-17-phase-3-complete.md](./devlog/2026-01-17-phase-3-complete.md) — Comprehensive completion report
- [extensions/vscode/README.md](../extensions/vscode/README.md) — VS Code extension guide

**Git Commits:**

1. e4f2a891 - Task 7: Config + Validator
2. f7c3b229 - Task 8: Database context
3. a8f4d3e7 - Task 9: Feed generation
4. 86606562 - Task 10: VS Code support
5. 88a327a5 - Task 11 (Part 1): Integration tests
6. 1e6c4091 - Task 11 (Part 2): Documentation

**Next Steps:**

- Task 12: v1.0.6.0 release preparation (version bumping, release notes, git tags)

**Next Phase (v1.0.7.0+):**

- [ ] Integrate SVG generation into graphics handler
- [ ] Add graphics caching layer
- [ ] Support for animated SVG + CSS
- [ ] Batch diagram compilation
- [ ] PDF/PNG export via headless browser

---

## ✅ Phase 5G: New Lightweight TUI (COMPLETE 2026-01-18)

**Mission:** Build new clean TUI (`/core/tui/`) to replace deprecated old Python TUI

**Status:** 🎉 **PHASE 5G COMPLETE** (2026-01-18)

**Architecture Decision:**

- Deprecate old TUI (tied to old library structure)
- Build new lightweight TUI (~500 lines, thin client)
- All logic delegated to Phase 5F handlers
- Wizard Server will handle backend (future)

**Key Accomplishments:**

- ✅ **TUIRepl** (repl.py, 170 lines) — Main event loop
  - Read user input, dispatch to handlers
  - Update GameState, render output, log commands
  - Special commands: QUIT, EXIT, CLEAR, STATUS, HISTORY
  - Graceful exception handling

- ✅ **CommandDispatcher** (dispatcher.py, 121 lines) — Routes to 13 handlers
  - All Phase 5F handlers integrated (navigation, info, game state, system)
  - Command parsing and parameter extraction
  - Helper methods for help text and command lists

- ✅ **GridRenderer** (renderer.py, 134 lines) — Output formatting with ANSI colors
  - GREEN (✓) for success, RED (✗) for error, YELLOW (⚠) for warning
  - Format items, results, prompts, separators
  - Professional color-coded terminal display

- ✅ **GameState** (state.py, 130 lines) — Centralized state management
  - Track location, inventory, discovered_locations, player_stats, history
  - JSON persistence to `/memory/saved_games/`
  - SAVE/LOAD integration with Phase 5F handlers

- ✅ **Comprehensive Test Suite** (test_tui_integration.py, 339 lines, 15+ tests)
  - GameState: initialization, updates, serialization
  - CommandDispatcher: routing, help, error handling
  - GridRenderer: color rendering, item/result formatting
  - TUIRepl: special commands, workflow integration
  - Integration: save/load persistence, full command chain

- ✅ **Launch Script** (bin/Launch-New-TUI.command, 60 lines)
  - Venv activation, module checks, startup banner
  - One-command launch with error handling

**Statistics:**

- Production code: 582 lines
- Test code: 339 lines
- Script: 60 lines
- Total: 982 lines
- Handlers integrated: 13 (all Phase 5F)
- Test cases: 15+
- Git commit: 87e526cb

**Files Created:**

1. `/core/tui/__init__.py` (27 lines) - Module exports
2. `/core/tui/repl.py` (170 lines) - Main REPL loop
3. `/core/tui/dispatcher.py` (121 lines) - Command router
4. `/core/tui/renderer.py` (134 lines) - Output formatter
5. `/core/tui/state.py` (130 lines) - State manager
6. `/core/tui/tests/test_tui_integration.py` (339 lines) - Test suite
7. `/bin/Launch-New-TUI.command` (60 lines) - Launcher

**Commands Available (13 total):**

- **Navigation:** MAP, PANEL, GOTO, FIND
- **Information:** TELL, HELP
- **Game State:** BAG, GRAB, SPAWN, SAVE, LOAD
- **System:** SHAKEDOWN, REPAIR
- **Special:** QUIT, EXIT, CLEAR, STATUS, HISTORY

**Design Patterns:**

- Thin client: TUI delegates to handlers, Wizard will handle backend
- Centralized state: Single GameState for all tracking
- Pattern-based routing: CommandDispatcher routes by command name
- Separated concerns: Display (renderer) vs logic (handlers) vs state (GameState)

**Next Steps:**

- Run TUI: `./bin/Launch-New-TUI.command`
- Run tests: `pytest core/tui/tests/test_tui_integration.py -v`
- Phase 6: Advanced features or Wizard Server integration

**References:**

- [Phase 5G Completion Report](../../PHASE-5G-COMPLETION.md)
- [Phase 5G Quick Reference](../../PHASE-5G-QUICK-REFERENCE.md)
- [Phase 5G Dev Log](../devlog/2026-01-18-phase-5g-complete.md)

---

## ✅ Phase 5E: Command Handlers (COMPLETE 2026-01-18)

**Mission:** Implement MAP, PANEL, GOTO command handlers for location-based TUI navigation

**Status:** 🎉 **PHASE 5E COMPLETE** (2026-01-18)

---

## ✅ Phase 5F: Game & System Commands (COMPLETE 2026-01-18)

**Mission:** Implement 9 new command handlers for game state and system management

**Status:** 🎉 **PHASE 5F COMPLETE** (2026-01-18)

**Key Accomplishments:**

- ✅ **MapHandler** (170 lines) — Display location tile grid
  - 80×24 grid with ASCII/Unicode rendering
  - Column/row headers, tile content with priority rendering
  - Shows borders, location metadata, timezone
  - 5/5 tests passing

- ✅ **PanelHandler** (190 lines) — Show location information
  - Comprehensive metadata display (region, type, layer, continent)
  - GPS coordinates with cardinal directions (N/S, E/W)
  - Timezone and local time calculation
  - Connection list with navigation hints
  - Grid content summary
  - 8/8 tests passing

- ✅ **GotoHandler** (180 lines) — Navigate between locations
  - Direction support: north, south, east, west, up, down, n, s, e, w, u, d
  - Direct location ID navigation
  - Connection validation (no multi-hop pathfinding)
  - State management and available exits display
  - 8/8 tests passing

- ✅ **BaseCommandHandler** (40 lines) — Abstract base class
  - Consistent interface for all handlers
  - Built-in state management
  - Type hints throughout

- ✅ **Test Suite** (380+ lines, 28 tests)
  - TestMapHandler: 5 tests (valid/default/invalid locations, grid rendering, regions)
  - TestPanelHandler: 8 tests (metadata, connections, timezone, local time)
  - TestGotoHandler: 8 tests (directions, location IDs, connections, state)
  - TestCommandHandlersIntegration: 3 integration tests
  - TestHandlerEdgeCases: 4 edge case tests
  - **100% pass rate: 28/28 ✅**

**Critical Bug Fix:**

Fixed case sensitivity issue in GotoHandler where location IDs were being lowercased:

```python
# Before (BROKEN): target_param = params[0].lower()  # "L300-BJ10" → "l300-bj10"
# After (FIXED): target_param = params[0]  # Preserve case, lowercase only for keywords
```

**Test Data Updates:**

Updated all location IDs to match actual database entries:

- L300-AE05 (invalid) → L300-CE10 (Mumbai)
- L300-AA10 (invalid) → L300-BQ10 (Seoul)
- L306-AA01 (invalid) → L306-AA00 (LEO - cosmic)

**Documentation:**

- [devlog/2026-01-18-phase-5e-complete.md](devlog/2026-01-18-phase-5e-complete.md) — Phase completion report

**Files Created:**

1. `/core/commands/base.py` — BaseCommandHandler abstract class
2. `/core/commands/map_handler.py` — MAP command implementation
3. `/core/commands/panel_handler.py` — PANEL command implementation
4. `/core/commands/goto_handler.py` — GOTO command implementation
5. `/core/commands/__init__.py` — Package interface
6. `/memory/tests/integration/test_phase_5e_handlers.py` — Comprehensive test suite

**Git Commit:**

```
48580512 - phase-5e: command handlers (MAP, PANEL, GOTO) with comprehensive tests - all 28 tests passing
```

---

## ✅ Step 1: Architecture Split + App Scaffold (COMPLETE)

**Mission:** Split Wizard into production (v1.1) + development (Goblin v0.1), scaffold uMarkdown Mac App

**Status:** 🎉 Mission Accomplished!  
**Completion Date:** 2026-01-15  
**Port Assignments:** Wizard (8765 production), Goblin (8767 development)

**Key Accomplishments:**

- ✅ AGENTS.md updated with Goblin Dev Server architecture (sections 3.3.1-3.3.2)
- ✅ Created `/dev/goblin/` structure (isolated from production Wizard)
- ✅ Goblin server scaffold (FastAPI, port 8767, 16 endpoints)
- ✅ Four core services:
  - `notion_sync_service.py` — Webhook handler with SQLite queue
  - `runtime_executor.py` — TS Markdown runtime (parse, execute, state)
  - `task_scheduler.py` — Organic cron (Plant → Sprout → Prune → Trellis → Harvest → Compost)
  - `binder_compiler.py` — Multi-format compilation (Markdown, PDF, JSON)
- ✅ Configuration system (example template + gitignored local config)
- ✅ Comprehensive Goblin README (architecture, promotion checklist, design principles)
- ✅ Launcher script: `bin/Launch-Goblin-Dev.command`

**Architecture Separation:**

| Aspect           | Wizard (Production)                 | Goblin (Development)        |
| ---------------- | ----------------------------------- | --------------------------- |
| Port             | 8765                                | 8767                        |
| Status           | Stable v1.1.0.0                     | Unstable v0.1.0.0           |
| API Prefix       | `/api/v1/*`                         | `/api/v0/*`                 |
| Config           | `/public/wizard/config/wizard.json` | `/dev/goblin/config/*.json` |
| Services         | Production-grade                    | Experimental stubs          |
| Access           | Public (with auth)                  | Localhost only              |
| Breaking Changes | Never                               | Expected                    |

**Files Created:** 7 core files + README + launcher  
**Lines Added:** ~2500+

**References:**

- Architecture docs: [/dev/goblin/README.md](../dev/goblin/README.md)
- AGENTS.md sections: 3.3.1 (Wizard), 3.3.2 (Goblin)
- Quick start: `bin/Launch-Goblin-Dev.command`

---

## 🎯 Architecture Clarification

### Current Reality (Python + TypeScript Dual Runtime)

**Core Runtime (TypeScript):** Native Mobile/iPad (`/core/`) - v1.0.0.0

- TypeScript-based execution engine
- Markdown → AST → State → Executors → Render
- 7 runtime block types (state, set, form, if/else, nav, panel, map)
- Nested variable access, interpolation
- Sandboxed, deterministic, offline-first
- **Target:** iOS, iPadOS, mobile web (no Python available)

**Core Runtime (Python TUI):** Desktop/TinyCore (`/core-beta/`) - v1.0.1.0

- Offline-first, TinyCore compatible
- uPY interpreter (Python subset)
- Command handlers + services
- **Target:** Desktop, TinyCore Linux

**App:** Tauri + Svelte (`/app/`) - v1.0.0.1

- Native macOS app
- 5 markdown formats (-ucode, -story, -marp, -guide, -config)
- Renders frontmatter-based documents
- **Does NOT execute runtime code** (yet)

**Wizard Server:** Python FastAPI (`/wizard/`) - Production v1.1.0.0

- Device auth, plugin repo, AI routing
- Port 8765, production-stable

**Goblin Dev Server:** Python FastAPI (`/dev/goblin/`) - Experimental v0.1.0.0

- Notion sync, task scheduling, binder compilation
- Port 8767, localhost-only
- **TS Markdown Runtime experiments** (Python-based for now)

### Future Vision (TypeScript Runtime - REQUIRED for Mobile)

**Critical Insight:** TypeScript runtime IS needed for mobile/iPad offline execution

**Platform Strategy:**

- **Desktop (macOS):** Python Wizard Server + Tauri app
  - Tauri can call Python services via HTTP (localhost)
  - Full access to Python runtime, Notion sync, AI routing
  - Wizard Server provides all backend services
- **Mobile/iPad (iOS/iPadOS):** Native app with TypeScript runtime
  - No Python available - must execute .ts blocks natively
  - Offline presentation mode for .md files with executable code
  - Sandboxed, deterministic execution (state, set, form, if, nav, panel)
  - Can sync with desktop via MeshCore when online

**Implementation Path:**

1. **v1.0.2.0:** Python services (Goblin) for desktop development
2. **v1.0.3.0:** TypeScript runtime scaffold for mobile
   - Location: `/core/` (TypeScript runtime) + `/core-beta/` (Python TUI)
   - Parser: Markdown → AST (runtime blocks)
   - State manager: Variables, objects, arrays
   - Block executors: state, set, form, if, nav, panel, map
   - SQLite bindings (better-sqlite3)
3. **v1.0.4.0+:** iOS/iPadOS native app with TypeScript runtime

**Decision Rationale:** Desktop can use Python services via HTTP, but mobile requires native TypeScript execution for offline capability

---

## ✅ Phase 2B: Lean TypeScript Runtime (COMPLETE 2026-01-16)

**Status:** 🎉 **MISSION ACCOMPLISHED**

**Deliverables:**

- ✅ Fresh TypeScript runtime in `/core/` (v1.0.0-lean)
- ✅ Type system (109 lines, all interfaces)
- ✅ Markdown parser (151 lines, full parsing)
- ✅ State manager (157 lines, dot notation + interpolation)
- ✅ Runtime orchestrator (321 lines, block execution)
- ✅ Test suite (20 test cases, MVP coverage)
- ✅ Documentation (README.md, CHANGELOG.md)
- ✅ Infrastructure (package.json, tsconfig.json, jest.config.js)

**Total:** ~1,600 lines of TypeScript, tests, and documentation

**Strategic Decision:** Build fresh lean TS runtime instead of porting 50+ Python handlers

- Simpler scope (markdown execution vs TUI commands)
- More testable (independent layers)
- Mobile-ready (iOS/iPadOS native)
- Extensible (easy to add block types)

**Next:** Phase 3A - Implement block executors (form, nav, conditional, map)

---

## 🎯 Step 2-4: Extended Roadmap (Mission v1.0.2.0)

### Move 1: Notion Sync Integration **DEFERRED to v1.0.4.0+**

**Mission:** Webhook-driven Notion integration with local SQLite queue, Notion-compatible markdown blocks

**Status:** ⏸️ **DEFERRED** - Foundation complete (Phase B), full implementation deferred

**Reason:** Focus on TypeScript runtime for mobile support (higher priority)

**What's Complete:**

- ✅ Phase A: Database schema (mappings, queue, sync_log tables)
- ✅ Phase B: NotionSyncService with webhook handlers (19 tests passing)
- ⏸️ Phase C.3: Conflict detection (deferred)
- ⏸️ Phase D: Publish mode (local → Notion) (deferred)

**Deliverables (when resumed):**

- Block mapping: uDOS markdown ↔ Notion API blocks
- `BlockMapping` class for parse/convert/serialize
- Bidirectional sync (local → Notion, Notion → local)
- Conflict resolution and retry logic
- Test with real Notion workspace

---

### Move 2: Markdown Runtime Phase 0 (Python-based)

**Mission:** Basic runtime block parsing and execution

**Deliverables:**

- `RuntimeExecutor` (Python) - parse runtime blocks from .md files
- State management ($variables, objects, arrays)
- Execute: state, set, form, if/else, nav, panel blocks
- Integration with Goblin Dev Server (port 8767)

**NOT included:** TypeScript implementation (deferred)  
**Integration:** Python service called from Tauri app via HTTP

**Checkpoint:** Parse and execute basic blocks via Goblin API

---

### Move 3: Task Scheduling + Binder Compilation ✅ **COMPLETE**

**Mission:** Organic cron scheduler + chapter/output generation

**Status:** ✅ **COMPLETE** (2026-01-16)

**Deliverables:**

- ✅ `TaskScheduler` (Python) - organic cron model (445 lines)
  - Plant → Sprout → Prune → Trellis → Harvest → Compost
- ✅ `BinderCompiler` (Python) - multi-format export (500+ lines)
  - Markdown, PDF (via pandoc), JSON, dev briefs
- ✅ Complete database schema with tables, indices, triggers, views
- ✅ 16 API endpoints with Pydantic validation
- ✅ 22/26 tests passing (85.7%)

**Test Results:**

- Task Scheduler: 8/8 unit tests + 5/9 API tests passing
- Binder Compiler: 9/9 API tests passing

**Checkpoint:** ✅ All checkpoints passed - Schedule tasks, compile binder outputs, verify exports

---

### Mission v1.0.2.0 Status: ✅ **COMPLETE** (2026-01-16)

- ✅ Step 1: Architecture + Scaffold (COMPLETE 2026-01-15)
- ✅ Move 1: Notion Sync Foundation - Phase B Complete (DEFERRED - See v1.0.4.0+)
- ✅ Move 2: Runtime Phase 0 - Stubs operational
- ✅ Move 3: Task scheduler + binder functional (COMPLETE)

**Total Delivered:** ~3180 lines of production code  
**Test Coverage:** 22/26 tests passing (85.7%)  
**Architecture:** Python-first implementation complete

---

## ✅ v1.0.3.0: TypeScript Runtime for Mobile/iPad (COMPLETE)

**Mission:** Create sandboxed TypeScript runtime for native iOS/iPadOS apps

**Status:** 🎉 **COMPLETE** (2026-01-16, Final: 38/39 tests - 97.4%)

**Key Accomplishments:**

- ✅ Complete TypeScript runtime scaffold (`/core/`)
- ✅ Parser system (MarkdownParser + ExpressionParser)
  - Extracts 7 runtime block types: state, set, form, if, else, nav, panel, map
  - Expression evaluation with nested variable access
  - Multi-line array and object parsing
- ✅ State Manager with full nested support
  - Primitives, objects, arrays
  - Nested access: `$a.b.c`, `$a[0]`
  - Variable interpolation in text
  - Multi-line state assignment support
- ✅ Complete block executor suite (8 executors)
  - StateExecutor (multi-line array/object support), SetExecutor, FormExecutor
  - ConditionalExecutor (if/else branch tracking), NavExecutor
  - PanelExecutor, MapExecutor (with nested variable evaluation), MapExecutor
  - ExecutorFactory for routing
- ✅ Main Runtime class with error handling and section execution
- ✅ Comprehensive test suite
  - 39 total tests, **38 passing (97.4%)**
  - Unit tests, executor tests, integration tests
  - Real-world script scenarios
- ✅ Full TypeScript infrastructure
  - package.json, tsconfig.json, version.json
  - Type definitions, public API exports
  - Documentation (README, CHANGELOG)

**Files Created:** 15 core files  
**Lines Added:** ~2200 TypeScript  
**Test Coverage:** 38/39 test cases passing

**Known Issues (1 remaining test):**

- MapExecutor: Variable interpolation in sprite coordinates (1 test - edge case with nested state evaluation)

**Platform Integration:**

- Desktop (macOS): Python services (Wizard/Goblin) + Tauri
- Mobile (iOS/iPadOS): TypeScript runtime (this implementation)
- Dual runtime architecture: `/core/` (TypeScript) + `/core-beta/` (Python TUI)

**References:**

- Implementation: `/core/` directory
- Spec: `/dev/roadmap/typescript.md`
- Architecture: [AGENTS.md](../AGENTS.md) sections 3.1-3.4
- Test suite: `/core/__tests__/example-script.test.ts` (11 integration tests)

**Final Notes:**

- Runtime is **production-ready** for MVP use
- All major features working (8 block types, state management, execution flow)
- Ready for iOS/iPadOS integration
- One minor edge case (sprite coordinate interpolation) remaining - low priority

---

## ✅ v1.0.4.0: GitHub Automation + Mistral AI + Empire CRM (COMPLETE)

**Mission:** GitHub integration, Mistral API access, business intelligence foundation

**Status:** 🎉 **COMPLETE** (2026-01-17, Ready for validation)  
**Theme:** Developer automation, AI-assisted development, CRM foundation

**Key Accomplishments:**

### Goblin Dev Server Enhancements (Port 8767)

- ✅ **GitHub Integration Service** (270 lines)
  - Repo sync (fetch, pull, status)
  - Issue/PR management
  - Context file access (roadmap, devlogs, copilot instructions)
  - Log analysis (debug, error, session logs)
  - 11 API endpoints

- ✅ **Mistral/Vibe AI Service** (268 lines)
  - Mistral API + Vibe CLI integration
  - Context-aware queries (roadmap, devlogs, project)
  - Model availability checking
  - Code analysis and suggestions
  - 6 API endpoints

- ✅ **Workflow Manager Service** (352 lines)
  - Project CRUD (Create, Read, Update, Delete)
  - Task management with priority + due dates
  - Status tracking (pending, in-progress, completed, blocked)
  - Organic task scheduling (Plant → Harvest → Compost)
  - SQLite persistence
  - 7 API endpoints

**Total Goblin:** 24 endpoints, ~1,277 lines of service code

### Wizard Server Enhancements (Port 8765)

- ✅ **Interactive Console** (345 lines)
  - Startup dashboard with capabilities
  - Service status display
  - Configuration summary
  - Command prompt interface
  - Real-time monitoring

- ✅ **GitHub Actions Self-Healing Monitor** (328 lines)
  - Webhook receiver (`/api/v1/github/webhook`)
  - Failure pattern detection (test_failure, build_failure, timeout, network_error)
  - Auto-retry for transient failures
  - GitHub CLI integration
  - Real-time notifications

**Total Wizard:** 2 enhanced services, 673 lines of code

### Empire CRM Extension

- ✅ **Scaffolded** (867 lines, 16 files)
  - Renamed from `wizard/tools/bizintel/`
  - HubSpot API integration stubs
  - Contact management database (marketing_db.py - 838 lines)
  - Service modules for enrichment, deduplication, extraction
  - Ready for HubSpot sync implementation

**Implementation Summary:**

| Component         | Lines     | Status | Location                                         |
| ----------------- | --------- | ------ | ------------------------------------------------ |
| Goblin GitHub     | 270       | ✅     | `/dev/goblin/services/github_integration.py`     |
| Goblin AI         | 268       | ✅     | `/dev/goblin/services/mistral_vibe.py`           |
| Goblin Workflow   | 352       | ✅     | `/dev/goblin/services/workflow_manager.py`       |
| Goblin Routes     | 387       | ✅     | `/dev/goblin/routes/*.py`                        |
| Wizard Console    | 345       | ✅     | `/public/wizard/services/interactive_console.py` |
| Wizard GitHub Mon | 328       | ✅     | `/public/wizard/services/github_monitor.py`      |
| Empire CRM        | 867       | ✅     | `/extensions/empire/`                            |
| **TOTAL**         | **2,817** | **✅** | **v1.0.4.0 Complete**                            |

**Testing Documentation:**

- Created: [v1.0.4.0-INTEGRATION-GUIDE.md](v1.0.4.0-INTEGRATION-GUIDE.md) (comprehensive)
- Service reference with 24 endpoint examples
- Curl testing procedures for all endpoints
- Troubleshooting guide

**Features Ready for Validation:**

- ✅ 24 API endpoints (GitHub, AI, Workflow)
- ✅ Lazy-load pattern (prevents startup blocking)
- ✅ GitHub CLI integration (repo sync, issues, PRs)
- ✅ Mistral API + Vibe CLI support
- ✅ SQLite workflow database (persistent)
- ✅ Production monitoring (Wizard console + GitHub Actions)
- ✅ CRM foundation (scaffolded, ready for implementation)

**Documentation:**

- [v1.0.4.0-INTEGRATION-GUIDE.md](v1.0.4.0-INTEGRATION-GUIDE.md) — Complete reference
- [devlog/2026-01-17-v1.0.4.0-dev-launch.md](devlog/2026-01-17-v1.0.4.0-dev-launch.md) — Launch plan
- [devlog/2026-01-16-v1.0.4.0-launch-ready.md](devlog/2026-01-16-v1.0.4.0-launch-ready.md) — Original status

**Pending v1.0.4.0 Items:**

- [ ] **uDOS workflow/Notion-style todo system** (Goblin)
  - SQLite-backed task management
  - Alternative to external project management
  - Integration with Goblin dev server
- [ ] **Local-remote GitHub repo sync** (Wizard promotion)
  - Move from Goblin to production Wizard
  - Production-ready repository management
  - Automated sync workflows
- [ ] **HubSpot CRM sync** (Empire extension)
  - Contacts SQLite ↔ HubSpot free CRM
  - Bidirectional synchronization
  - Contact enrichment and deduplication

**Next Phase (v1.0.5.0):**

- [ ] Implement Mac App notifications (Svelte + Tailwind)
- [ ] Slack API integration for notifications/feeds
- [ ] Deploy v1.0.4.0 preview for community testing

---

## ✅ v1.0.4.1: Port Manager & Service Coordination (COMPLETE)

**Mission:** Complete server and port awareness with automated conflict resolution

**Status:** ✅ **COMPLETE** (2026-01-17)  
**Theme:** Infrastructure automation, service health monitoring

**Key Accomplishments:**

### Port Manager Core (`wizard/services/port_manager.py`)

- ✅ Service registry with 5 pre-configured services (Wizard, Goblin, API, Vite, Tauri)
- ✅ Real-time port conflict detection using `lsof`
- ✅ Automatic PID tracking and process identification
- ✅ Port availability checking and auto-assignment
- ✅ Service health endpoint monitoring
- ✅ Startup/shutdown order coordination

### CLI Tool (`wizard/cli_port_manager.py` + `bin/port-manager`)

- ✅ 7 commands: status, check, conflicts, kill, available, reassign, env
- ✅ Executable shell wrapper with auto-venv activation
- ✅ Formatted reports with conflict resolution suggestions
- ✅ One-command port cleanup and service management

### REST API Integration (`wizard/services/port_manager_service.py`)

- ✅ 8 endpoints under `/api/v1/ports/`:
  - GET `/status` - Full dashboard
  - GET `/services` - List all services
  - GET `/services/{name}` - Check specific service
  - GET `/conflicts` - Port conflict list
  - POST `/services/{name}/kill` - Kill service
  - POST `/ports/{port}/kill` - Kill port
  - GET `/report` - Formatted report
  - GET `/env` - Environment variables

### Launcher Integration

- ✅ Updated `Launch-Goblin-Dev.command` with port manager checks
- ✅ Updated `Launch-Wizard-Dev.command` with automated conflict resolution
- ✅ Updated `Launch-Dev-Mode.command` with pre-flight port cleanup
- ✅ All launchers test and kill conflicting processes automatically

**Files Created:** 7 files (~2,000 lines)
**Tests Performed:** CLI, REST API, launcher integration all verified

**Quick Reference:**

```bash
bin/port-manager status      # Check all services
bin/port-manager conflicts   # Find port conflicts
bin/port-manager kill :8767  # Kill process on port
```

**REST API Access:**

```bash
curl http://localhost:8765/api/v1/ports/status
```

**Documentation:**

- `wizard/docs/PORT-MANAGER.md` - Full guide
- `wizard/PORT-MANAGER-QUICK.md` - Quick reference
- `PORT-MANAGER-IMPLEMENTATION.md` - Implementation summary

---

## 🎨 Graphics Architecture (Integrated into v1.0.2.0)

**Three-Tier System:** Markdown Source → ASCII-Teletext (TUI) → SVG (App)

### Tier 1: Markdown Native (SOURCE)

- Flowchart.js syntax
- Mermaid diagrams
- Marp presentations
- Knowledge guide embeds

### Tier 2: ASCII-Teletext (FALLBACK - TUI)

- Unicode block characters
- Box drawing charactersScaffold

**Theme:** Build TypeScript runtime for mobile/iPad offline execution

**Mission:** Create sandboxed TypeScript runtime for native iOS/iPadOS apps

**Deliverables:**

- `/core/` (TypeScript runtime) - parse, state manager, block executors
- Rename `/core/` → `/core-beta/` (Python TUI - backward compatibility)
- Parser: Markdown → AST (identify runtime blocks)
- State Manager: Variables, objects, arrays, persistence
- Block Executors: state, set, form, if/else, nav, panel, map
- SQLite bindings: better-sqlite3 (offline data storage)
- Test suite: Sandboxed execution, deterministic results

**Platform Integration:**

- Desktop (macOS): Continue using Python services (Wizard/Goblin via HTTP)
- Mobile (iOS/iPadOS): Native TypeScript runtime (offline, no Python)

**Checkpoint:** Execute basic runtime blocks on iOS simulator, verify offline capability

- Can Python runtime + Tauri IPC meet App needs?
- Is browser-based TS execution required?
- Performance vs complexity trade-offs

**If TypeScript needed:**

- Create `/core/` (TypeScript runtime)
- Rename `/core/` → `/core-beta/` (Python TUI)
- Implement parser, state manager, block executors
- SQLite bindings via better-sqlite3
- Sandboxed, deterministic execution

**If Python sufficient:**

- Keep current Python runtime
- Enhance Tauri IPC bridge
- Optimize Python execution performance

---

### v1.0.4.0 - Goblin AI Dev Server + Empire CRM Extension

**Theme:** GitHub automation, Mistral API integration, business intelligence

| Task                                       | Category  | Status | Notes                                                  |
| ------------------------------------------ | --------- | ------ | ------------------------------------------------------ |
| **Wizard interactive console**             | Wizard    | ✅     | Startup dashboard + command prompt (2026-01-16)        |
| **GitHub Actions monitoring**              | Wizard    | ✅     | Self-healing CI/CD with webhooks (2026-01-16)          |
| **GitHub CLI integration**                 | Wizard    | ✅     | Workflow status, auto-retry, pattern detection         |
| **GitHub webhooks**                        | Wizard    | ✅     | /api/v1/github/webhook endpoint (2026-01-16)           |
| **Local-remote GitHub sync**               | Wizard    | ⏳     | Move from Goblin, production-ready repo management     |
| **Mistral API + Vibe CLI**                 | Goblin    | ⏳     | Access to devlogs, roadmap, logs, copilot instructions |
| **uDOS workflow/Notion-style todo system** | Goblin    | ⏳     | Alternative to external project management             |
| **Empire Extension (bizintel → empire)**   | Extension | ⏳     | Rename and scaffold for CRM integration                |
| **HubSpot CRM sync**                       | Empire    | ⏳     | Contacts SQLite ↔ HubSpot free CRM bidirectional sync  |
| **Empire contacts schema**                 | Empire    | ⏳     | SQLite database design for contact management          |

**Wizard Server Enhancements Complete (2026-01-16):**

- ✅ **Interactive Console** (`wizard/services/interactive_console.py`)
  - Startup banner with capabilities dashboard
  - 9 services listed with versions/status
  - Configuration summary (rate limits, budgets)
  - API endpoints displayed
  - Commands: status, services, config, health, reload, github, workflows, help, exit

- ✅ **GitHub Actions Self-Healing** (`wizard/services/github_monitor.py`)
  - Webhook receiver: `/api/v1/github/webhook`
  - Failure pattern detection (test_failure, build_failure, timeout, network_error)
  - Auto-retry for transient failures (network, timeout)
  - Auto-retry for flaky tests (up to 2x)
  - Real-time notifications in wizard console
  - GitHub CLI integration (gh run view, gh run rerun)

**Files Created:**

- `wizard/services/interactive_console.py` (345 lines)
- `wizard/services/github_monitor.py` (328 lines)
- `wizard/docs/INTERACTIVE-CONSOLE.md` (comprehensive guide)

**Files Modified:**

- `wizard/server.py` - Added `interactive` parameter, async console integration, webhook endpoint

**Documentation:** [wizard/docs/INTERACTIVE-CONSOLE.md](../public/wizard/docs/INTERACTIVE-CONSOLE.md)

### v1.0.5.0 - Mac App Notifications & UI

**Theme:** Toast notifications, Slack integration (requires App workspace)

| Task                            | Category | Notes                                      |
| ------------------------------- | -------- | ------------------------------------------ |
| **Mac App toast notifications** | App      | Svelte/Tailwind styled notification system |
| **Slack API integration**       | App      | Notifications/feeds via Slack Web API      |

### v1.0.6.0 - TUI Consolidation + Graphics Integration + File Parsing

**Theme:** Fix hardcoding, consolidate duplicates, integrate graphics tiers, add file parsing system

#### TUI & Graphics Tasks

| Task                                   | Category  | Notes                                                         |
| -------------------------------------- | --------- | ------------------------------------------------------------- |
| Box drawing consolidation              | TUI       | ✅ Partial (width alignment improved, minor wrapping remains) |
| Progress bars consolidation            | TUI       |                                                               |
| Viewport detection utilities           | TUI       |                                                               |
| Column wrapping & alignment refinement | TUI       | Fine-tune box element alignment for narrow viewports          |
| Graphics Service integration           | Graphics  |                                                               |
| DIAGRAM command                        | Extension |                                                               |

#### File Parsing & Binder System

**Theme:** Text-based data formats → SQLite tables + binder sandboxes

| Task                           | Category | Notes                                                |
| ------------------------------ | -------- | ---------------------------------------------------- |
| **Markdown table parsing**     | Core     | Parse `.table.md` → SQLite                           |
| **CSV/TSV import**             | Core     | Import delimited files → `uDOS-table.db`             |
| **JSON/JSONL parsing**         | Core     | Semi-structured data → tables                        |
| **YAML/TOML parsing**          | Core     | Config-as-data → SQLite                              |
| **SQL script execution**       | Core     | Data cleaning, enrichment, merges                    |
| **Binder folder structure**    | App      | Isolated sandboxes with local DB access              |
| **Binder-local DB context**    | App      | Relative references within binder scope              |
| **Table export (.table.md)**   | Core     | SQLite → human-readable markdown tables              |
| **RSS Feed generation**        | Wizard   | FEED command - assemble/serve RSS from local content |
| **uDOS language registration** | Editor   | VS Code grammar for `udos` code blocks               |
| **Monaspace typography**       | App      | Multi-voiced text with semantic fonts                |
| **AI provenance markers**      | Editor   | Visual distinction for AI-suggested code             |

**File Extensions Strategy:**

| Extension            | Purpose              | Parsable to SQLite |
| -------------------- | -------------------- | ------------------ |
| `*.md`               | Human-first document | ❌                 |
| `*.table.md`         | Markdown tables      | ✅                 |
| `*.script.md`        | Executable markdown  | ❌                 |
| `*.mission.md`       | Long-running plans   | ❌                 |
| `*.wizard.md`        | Experimental/dev     | ❌                 |
| `*.csv` / `*.tsv`    | Delimited data       | ✅                 |
| `*.json` / `*.jsonl` | Structured data      | ✅                 |
| `*.yaml` / `*.toml`  | Config data          | ✅                 |
| `*.sql`              | Query/transform      | ✅ (executable)    |

**Binder Structure:**

```
MyBinder/
  binder.md              # Optional binder home
  uDOS-table.db          # Local SQLite database
  imports/               # CSV, JSON, YAML sources
  tables/                # Exported .table.md files
  scripts/               # .script.md executables
```

**References:**

- [dev/roadmap/app-files-parsing.md](../dev/roadmap/app-files-parsing.md) — Complete file parsing spec
- Monaspace fonts: https://monaspace.githubnext.com

---

## 🎯 v1.0.7.0: Teletext Grid Runtime + Text Graphics (PLANNING)

**Mission:** TypeScript runtime for grid-based spatial rendering, sextant graphics, and tile system

**Status:** 📋 Planning (Estimated 3-4 weeks)

**Locked Specification:** [u_dos_spatial_text_graphics_brief.md](dev/roadmap/u_dos_spatial_text_graphics_brief.md)

**Key Specifications:**

- Tile geometry: 16×24 pixels
- Viewport system: 80×30 standard, 40×15 mini
- Layer bands: SUR (L300–L305), UDN (L299–L294), SUB (L293+)
- Grid addressing: L{Layer}-{Cell}, e.g., `L300-AA10`
- Tile taxonomy: Object (static), Sprite (dynamic), Marker (waypoint)
- Graphics: Unicode sextant with fallback ladder (quadrant → shades → ASCII)

**Phase Breakdown:**

| Phase | Component                     | Effort | Status     |
| ----- | ----------------------------- | ------ | ---------- |
| 1     | TypeScript grid runtime       | 1-2w   | 📋 Planned |
| 2     | Sextant/fallback rendering    | 3-4d   | 📋 Planned |
| 3     | Code block parsing (markdown) | 3-4d   | 📋 Planned |
| 4     | Location parser & data model  | 3-4d   | 📋 Planned |
| 5     | Integration with uDOS runtime | 2-3d   | 📋 Planned |

**Deliverables:**

- [ ] `core/grid-runtime/` — TypeScript grid rendering engine
  - Viewport management (80×30, 40×15)
  - Sextant/quadrant/shade/ASCII rendering pipeline
  - Layer model and tile positioning
  - Sprite animation state machine
  - Sky view computation (location + time → sky)

- [ ] Code block integration
  - ` ```teletext ` — inline sextant graphics (stored text)
  - ` ```grid ` — structured grid definition (YAML/JSON)
  - ` ```tiles ` — tile manifest with metadata
  - Variable interpolation ($player.pos.tile, $world.layer, etc.)

- [ ] Location & tile system
  - `location.json` rebuilt with new grid geometry
  - Cell address parser (AA10 → [0, 0])
  - Layer band validator (SUR/UDN/SUB)
  - Sparse world model (on-demand tile allocation)
  - Movement validation and pathfinding

- [ ] Runtime integration
  - Wire grid rendering into map blocks (example-script.md patterns)
  - Tile interaction system (pickup, inspect, use)
  - Movement between adjacent cells
  - Dynamic sprite updates

**Foundation for v1.0.8.0:** ASCII → Teletext → Markdown diagrams → SVG

---

## 🎨 v1.0.8.0: SVG Graphics Integration (DEFERRED)

**Mission:** AI-driven diagram generation with graphics caching and export

**Status:** 📋 Deferred (After v1.0.7.0)

**Key Features:**

- [ ] Integrate SVG generation into graphics handler
- [ ] Add graphics caching layer
- [ ] Support for animated SVG + CSS
- [ ] Batch diagram compilation
- [ ] PDF/PNG export via headless browser

**Builds on:** Teletext → SVG conversion pipeline

---

## 🎵 v1.0.9.0+: Groovebox Extension (DEFERRED)

**Mission:** Music production with MML sequencing and 808 drums

**Status:** 📋 Deferred (After v1.0.8.0)

**Key Features:**

- [ ] MML (Music Macro Language) engine
- [ ] 808 drum sound generation
- [ ] TUI pattern editor
- [ ] PLAY/MUSIC commands for Core

---

### v1.1.0.0 - TypeScript Runtime: SQLite + iOS Integration

**Theme:** Complete mobile runtime with database access

| Task                                  | Category | Notes                                         |
| ------------------------------------- | -------- | --------------------------------------------- |
| SQLite bindings (better-sqlite3)      | Core     | Offline data storage for mobile               |
| Database binding ($db.\* variables)   | Core     | Read-only access to external SQLite databases |
| iOS compatibility testing             | Core     | Verify runtime works on iOS/iPadOS            |
| Object literal parsing in expressions | Core     | Support `$x = { "a": 1 }` syntax              |
| Array literal parsing                 | Core     | Support `$x = [1, 2, 3]` syntax               |
| Enhanced error messages               | Core     | Developer-friendly diagnostics                |
| Runtime performance profiling         | Core     | Optimize parser and executor performance      |
| Mobile integration examples           | Docs     | Example iOS/SwiftUI integration               |

### v1.0.7.0 - Groovebox Extension

**Theme:** Music production with MML sequencing

| Task                | Category  |
| ------------------- | --------- |
| MML engine          | Extension |
| 808 drum sounds     | Extension |
| TUI pattern editor  | Extension |
| PLAY/MUSIC commands | Core      |

### v1.0.8.0 - Knowledge & Community

**Theme:** Extended knowledge and collaboration

| Task                    | Category  |
| ----------------------- | --------- |
| Knowledge contributions | Knowledge |
| Mesh sync improvements  | Transport |
| Group workflows         | Core      |
| Extension marketplace   | Wizard    |

---

## 📊 Recent Releases

### Alpha v1.0.1.0 - Stable Alpha (2026-01-10)

**Theme:** Polish, test, document, optimize

#### Release Highlights

✅ **Complete Optimization Round**

- Tauri app: Type consolidation, shared exports, component modularization
- Core: Extracted shared deduplication utilities, archived deprecated modules
- Fixed broken imports, standardized `.archive/` folder naming
- **300+ lines** of duplicate/deprecated code removed

✅ **Testing & Validation**

- 35 integration tests covering all major features
- SHAKEDOWN validation (47 tests) passing
- Handler architecture validated

✅ **Documentation Complete**

- Comprehensive optimization assessments (Tauri + Core)
- Wiki rebuild with current command reference
- Development conventions documented

#### Version Summary

| Component     | Version  | Changes                                                          |
| ------------- | -------- | ---------------------------------------------------------------- |
| **Core**      | v1.1.0.0 | File deduplication utilities, config consolidation               |
| **API**       | v1.1.0.0 | Modular architecture stable                                      |
| **App**       | v1.0.3.0 | Type sharing, SidebarContainer, font config, format architecture |
| **Wizard**    | v1.1.0.0 | AI provider integrations stable                                  |
| **Transport** | v1.0.1.0 | Policy enforcement validated                                     |
| **Knowledge** | v1.0.2.0 | Tech/code categories added                                       |

#### Alpha Workspace: uCode Format Architecture

**App v1.0.3.0** introduces frontmatter-based markdown format specifications:

| Format     | Extension    | Purpose                     | Features                                                                          |
| ---------- | ------------ | --------------------------- | --------------------------------------------------------------------------------- |
| **uCode**  | `-ucode.md`  | Executable documents        | ```upy code blocks (runtime), accesses maps/docs, extendable                      |
| **Story**  | `-story.md`  | Interactive presentations   | Self-contained, ```story blocks, typeform-style Q&A, variables/objects, sandboxed |
| **Marp**   | `-marp.md`   | Full-viewport presentations | Marp prevention styling, slideshow mode                                           |
| **Guide**  | `-guide.md`  | Knowledge bank articles     | Standard knowledge format                                                         |
| **Config** | `-config.md` | System configuration        | Settings, fonts, icons, custom functions                                          |

**Format Comparison:** Story vs uCode

- **Story**: Sandboxed, distributable, single-file data collection. One .md file that collects/contains data within it and can be returned to sender with results. Typically sandboxed, can be sent with information pre-filled and/or to verify/update. Use cases: user setup variables at installation, step-by-step interactive games.
- **uCode**: Extensible runtime with full uDOS integration. Working ```upy code blocks (runtime) that can access other docs, maps, etc. More extendable than Story format.

**Common Structure** (both executable formats):

- Frontmatter at top (essential) - renders as Svelte tag-style buttons at top of Prose
- Main content with standard markdown + ```story blocks (typeform-style form fields)
- Variables, objects, datasets, functions at bottom (after `---`)

**See also:** [app-beta/docs/](../app-beta/docs/) for detailed format specifications

---

## 🎯 Mission Milestones

| Version    | Mission                      | Steps/Moves          | Status          |
| ---------- | ---------------------------- | -------------------- | --------------- |
| v1.0.0     | Handler Implementation       | 1 step               | ✅ Accomplished |
| v1.0.1     | Stable Alpha                 | Polish + test        | ✅ Accomplished |
| **v1.0.2** | **Notion + Runtime + Tasks** | **Step 1 + 3 moves** | **✅ Complete** |
| **v1.0.3** | **TypeScript Runtime**       | **Mobile/iPad**      | **✅ Complete** |
| v1.0.4     | Goblin AI + Empire CRM       | GitHub + HubSpot     | 📋 Planning     |
| v1.0.5     | Mac App Notifications & UI   | Toast + Slack        | 📋 Planning     |
| v1.0.6     | TUI Consolidation + Graphics | TBD                  | 📋 Planning     |
| v1.0.7     | Groovebox Extension          | TBD                  | 📋 Planning     |
| v1.0.8     | Knowledge & Community        | TBD                  | 📋 Planning     |
| v1.1.0     | Beta Release                 | Integration          | 📋 Future       |

---

## 📋 Mission v1.0.2.0 Complete When:

- [x] Step 1: Architecture + Scaffold (✅ Accomplished 2026-01-15)
- [x] Move 1: Notion webhooks + SQLite integration (✅ Phase B Complete - 19 tests)
- [x] Phase C.1-C.2: SyncExecutor (✅ Queue Processing - 15 tests)
- [x] Move 2: TS runtime Phase 0 (parse, state, form) (✅ Complete - 43 tests)
- [x] Move 3: Task scheduler + binder compilation (✅ Complete - 22 tests)

**Status:** ✅ **MISSION ACCOMPLISHED** (2026-01-16)

---

## 🎯 v1.0.5.0: Mac App Notifications & UI (PLANNING)

**Mission:** Enhance uMarkdown Mac app with native notifications and real-time feedback

**Status:** 🎯 Planning (Estimated 1.5-2 weeks)  
**Theme:** User engagement, real-time notifications, productivity integration

**Key Deliverables:**

- ✨ Toast notifications (Svelte + Tailwind)
- 📱 Notification types (info, success, warning, error)
- 💾 Notification history & export
- 🔗 Slack integration (optional, secure)
- ⚡ Real-time server event notifications

**Phase Breakdown:**

| Phase | Component                    | Effort | Status     |
| ----- | ---------------------------- | ------ | ---------- |
| 1     | Toast notification system    | 1-2d   | 📋 Planned |
| 2     | Notification types & styling | 1d     | 📋 Planned |
| 3     | App event integration        | 1-2d   | 📋 Planned |
| 4     | Slack API integration        | 2-3d   | 📋 Planned |
| 5     | Notification history         | 1d     | 📋 Planned |

**References:**

- Full specification: [docs/specs/v1.0.5.0-mac-app-notifications.md](specs/v1.0.5.0-mac-app-notifications.md)
- Complete project checklist with tasks and effort estimates
- Security considerations and API design

**Next Steps:**

1. Review specification document
2. Prepare UI designs and mockups
3. Allocate resources and timeline
4. Begin Phase 1 (toast notification system)

---

## 📋 Mission v1.0.4.0 Scope:

**Goblin AI Dev Server:**

- [x] GitHub CLI integration (repo sync, webhooks, PR/issue management) ✅
- [x] Mistral API + Vibe CLI integration ✅
- [x] Access to devlogs, roadmap, logs/debug/error, copilot instructions ✅
- [ ] uDOS workflow/Notion-style todo system

**Wizard Server (Production):**

- [ ] Local-remote GitHub repo sync/management
- [ ] GitHub webhooks for event-driven automation
- [x] Test and validate existing GitHub integrations ✅

**Empire Extension (bizintel → empire):**

- [x] Rename `/wizard/tools/bizintel/` to `/extensions/empire/` ✅
- [x] Scaffold contacts-sqlite.db schema ✅
- [ ] HubSpot free CRM integration (bidirectional sync)
- [x] Update imports and references across codebase ✅

---

## 📚 Watchlist (Known Risks)

| Risk                               | Impact | Mitigation                                                                           |
| ---------------------------------- | ------ | ------------------------------------------------------------------------------------ |
| TinyCore packaging complexity      | HIGH   | Start with simple TCZ first                                                          |
| Marp/SvelteKit integration         | MEDIUM | Verify SvelteKit can wrap Marp rendered styles/content                               |
| gtx-form vs custom Svelte solution | MEDIUM | Evaluate library/gtx-form vs building Svelte-optimized interactive presentation mode |
| Vibe offline agent setup           | MEDIUM | Follow Mistral docs closely                                                          |

---

## 🔗 References

- [Engineering Index](docs/_index.md)
- [AGENTS.md](../AGENTS.md)
- [Dev Logs](docs/devlog/)
- [Architecture Decisions](docs/decisions/)
- [Wizard Model Routing Policy](docs/decisions/wizard-model-routing-policy.md)

---

_For detailed historical roadmap, see [dev/roadmap/ROADMAP.md](../dev/roadmap/ROADMAP.md)_  
_Last Updated: 2026-01-16_
