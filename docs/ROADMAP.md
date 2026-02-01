# uDOS Development Rounds → ROADMAP (2026-02-01)

**Version:** v1.1.14 (Target)  
**Last Updated:** 2026-02-01  
**Status:** 🚀 ACCELERATION PLAN ACTIVE — Round 2 expedited at 2x rounds/day

---

## 🎯 ACCELERATION PLAN: v1.1.14 by Sunday, Feb 7, 2026

**Duration:** 6 days (Feb 1-7, 2026)  
**Acceleration:** 2x complete rounds per day = **12 total rounds**  
**Target:** Core v1.1.0 (Day 4) → Wizard v1.1.0 (Day 5) → Release v1.1.14 (Day 7)

### Critical Path

```
Day 1 (Sun) → Rounds 1-2   : Setup + Phase 1B Planning
Day 2 (Mon) → Rounds 3-4   : Phase 1B Executors (state, set, form, if/else, nav, panel, map)
Day 3 (Tue) → Rounds 5-6   : Phase 1C Interpolation + Phase 1D SQLite
Day 4 (Wed) → Rounds 7-8   : Phase 1E Document Runner (Core v1.1.0) + Wizard OAuth Part 1
Day 5 (Thu) → Rounds 9-10  : Wizard OAuth Part 2 + Workflow System (Wizard v1.1.0)
Day 6 (Fri) → Round 11     : Wizard Phase 6B-6C (HubSpot + Notion)
Day 7 (Sat) → Round 12     : Final Hardening + v1.1.14 Release
```

### Resources

- **Daily Sprint Plan:** [memory/logs/daily-sprint-plan-2026-02-01-to-07.md](../../memory/logs/daily-sprint-plan-2026-02-01-to-07.md)
- **Weekly Devlog:** [memory/logs/devlog-2026-W05.md](../../memory/logs/devlog-2026-W05.md)
- **CI/CD Checkpoints:** [memory/logs/ci-integration.json](../../memory/logs/ci-integration.json)
- **Test Health Dashboard:** [memory/tests/health_dashboard.py](../../memory/tests/health_dashboard.py)

**Daily Checkpoints:** Create `memory/logs/daily-2026-02-0X.md` for each day with round status, blockers, and metrics.

---

## 📋 Executive Summary

This document consolidates all active development streams across Core, Wizard, Goblin, and App workspaces based on recent roadmap analysis.

**NEW (2026-02-01):** Shift to **accelerated 2x rounds/day schedule** for v1.1.14 delivery. Core runtime groundwork is stable (Phase 1A complete), so focus is Phase 1B-1E completion in Days 1-4, followed by Wizard Phase 6A-6C in Days 4-6, with final hardening on Day 7. Weekly logs replace monthly; daily cycles replace weekly planning.

---

## 🎯 Development Rounds

### Round 1: Core Runtime (TypeScript Markdown + Grid + Spatial Filesystem + Wiki Standard)

**Owner:** Core (`/core/`)  
**Status:** v1.0.7 — Foundation Complete (Spatial Filesystem + Wiki standardization) → Runtime Implementation Phase  
**Timeline:** 2 weeks remaining (TypeScript runtime core implementation)  
**Action Plan:** [STREAM1-ACTION-PLAN.md](STREAM1-ACTION-PLAN.md) (5 phases, 14-day implementation roadmap)

**Components:**

1. **Spatial Filesystem** ✅ **COMPLETE v1.0.7**
   - Workspace hierarchy (@sandbox, @bank, @shared, @wizard, @knowledge, @dev)
   - Role-based access control (RBAC) — User/Admin/Guest
   - Grid location tagging (L###-Cell → file mapping)
   - Content-tag indexing (metadata discovery)
   - Binder integration (multi-chapter projects)
   - Front-matter standardization (YAML metadata)
   - TUI commands (WORKSPACE, LOCATION, TAG, BINDER)
   - ✅ Implementation complete (core/services/spatial_filesystem.py, 850 lines)
   - ✅ Handler complete (core/commands/spatial_filesystem_handler.py, 400 lines)
   - ✅ Tests complete (32 test cases, all passing)
   - ✅ Documentation complete (docs/specs/SPATIAL-FILESYSTEM.md + quick ref)

2. **Wiki Standardization** ✅ **COMPLETE**
   - Obsidian-compatible YAML frontmatter spec (uid, title, tags, status, updated)
   - All 7 wiki documents updated with frontmatter
   - Knowledge bank README updated (uid + tags)
   - 6 core architecture docs: ALPINE-CORE, BEACON-PORTAL, BEACON-VPN, SONIC-SCREWDRIVER, WIZARD-CORE-STORY, BEACON-QUICK-REF
   - ✅ Spec: [wiki_spec_obsidian.md](specs/wiki_spec_obsidian.md)
   - ✅ Guide: [WIKI-FRONTMATTER-GUIDE.md](WIKI-FRONTMATTER-GUIDE.md) with migration examples
   - ✅ Vault ready for Obsidian import

3. **TypeScript Markdown Runtime** (Next Priority)
   - State management (`$variables`) — **Phase 1A complete** (RuntimeState/StateStore + persistence contracts + regression tests); Phase 1B block executors now next.
   - Runtime blocks: `state`, `set`, `form`, `if/else`, `nav`, `panel`, `map`
   - Variable interpolation in Markdown text
   - SQLite DB binding (read-only)
   - Core execution via Node runner (parse + execute)
   - Deterministic execution model
   - **Integration:** Read location from front-matter, track state spatially

4. **Grid Runtime + Spatial Computing**
   - Fractal addressing (L###-Cell pattern)
   - Layer bands (SUR/UDN/SUB)
   - Viewport rendering (80x30 canonical, 40x15 mini)
   - Tile system (16×24 pixels, 5-bit palette)
   - Sextant/quadrant/ASCII fallback rendering
   - Sprite animation support
   - **Integration:** Render files tagged with location as sprites/markers

5. **File Parsing System**
   - Markdown table parser (`.table.md`)
   - CSV/TSV importer
   - JSON/JSONL parser
   - YAML/TOML config parser
   - SQL executor
   - RSS feed generation
   - **Integration:** Spatial write/tag for parsed files

5. **Binder + Dataset Operations (Core)**
   - Binder compile and chapters (Markdown/JSON/PDF/brief)
   - SQLite-backed binder metadata
   - Dataset validation/build/regen (80x30)
   - Unified locations dataset output

5. **TUI Output Toolkit**
   - ASCII banners, tables, checklists, map render
   - Consistent handler output formatting
   - SmartPrompt and selector framework integration

**Key Deliverables:**

- ✅ Specs moved to `/docs/specs/`
- ✅ Examples moved to `/docs/examples/`
- ✅ Spatial Filesystem implementation complete
- ✅ Wiki standardization complete (247 files, all standardized with unique UIDs)
- ✅ Binder compiler moved to Core
- ✅ Dataset manager + regen tools
- ✅ Output toolkit (ASCII-first)
- 🔲 Core runtime implementation (Phase 1A-1E: State, Blocks, Expressions, DB, Executor)
- 🔲 **Outstanding Phase 1 work:** interpolation layer (`core/src/interpolation/*` + Markdown text renderer), read-only SQLite binding (`core/src/database/sqlite-adapter.ts`), and the Node-based document runner cannot yet execute the parsed Markdown documents. These pieces are still tracked under [STREAM1-ACTION-PLAN.md](STREAM1-ACTION-PLAN.md) before transitioning into Phase 2.
- 🔲 Grid viewport renderer (beyond base map render)
- 🔲 File parser integration (CSV/JSON/YAML/SQL)
- ✅ Phase 1A (state store + persistence API) implemented; Phase 1B (block executors) now next focus.

Recent progress:
- DocumentRunner now wires the Phase 1B `state` and `set` executors end-to-end, backed by the new `memory/tests/phase1b_*` suites (legacy `__tests__` files moved into `memory/tests/legacy`). 
- The TUI startup/self-heal loop now watches `~/memory/tests/` for new or modified scripts, launches `automation.py`, and surfaces the status/log path in the health summary so regressions and prep work are flagged before interpolation/DB phases begin.

**Next Action:**
- See [STREAM1-ACTION-PLAN.md](STREAM1-ACTION-PLAN.md) for 14-day implementation roadmap (TypeScript Markdown Runtime)

**References:**

- [TypeScript Markdown Runtime Spec](specs/typescript-markdown-runtime.md)
- [Grid & Spatial Computing Spec](specs/grid-spatial-computing.md)
- [File Parsing Architecture](specs/file-parsing-architecture.md)
- [Spatial Filesystem Spec](specs/SPATIAL-FILESYSTEM.md)
- [Wiki Frontmatter Guide](WIKI-FRONTMATTER-GUIDE.md)
- [Example Scripts](examples/)

---

### Round 2: Wizard Server (Production Services) — Optimizations & Hardening

**Owner:** Wizard (`/wizard/`)  
**Status:** v1.1.0 — Optimization/hardening sprint, Phase 6 lock-in  
**Timeline:** 4-8 weeks (Phase 6A-6D + follow-up tuning)  
**Focus:** Harden the OAuth/workflow surface, optimize gateway throughput, lock down secrets/authorization, and expand observability so Wizard can safely bridge Core runtime and Sonic plugin automation.  
**Round 2 Plan:** [Wizard Round 2 Optimization & Hardening Plan](WIZARD-ROUND2-PLAN.md) keeps the checklist, metrics, and references in one location and now enumerates the work as **critical daily cycles** (Jan 31–Feb 13) rather than weekly windows so automation knows what to expect each day.

**Components:**

1. **OAuth Foundation (Phase 6A)**
   - Provider integrations (Google, Microsoft, GitHub, Apple)
   - PKCE flow implementation
   - Token management & refresh
   - Scope validation
   - Duration: 2 weeks

2. **Workflow & Project Management**
   - Project/Mission container system
   - Organic cron scheduler
   - Provider rotation (Ollama -> OpenRouter escalation)
   - Daily quota pacing
   - Task graph dependencies
   - Binder compilation uses Core services

3. **Integration Handlers (Phase 6B-6D)**
   - HubSpot CRM sync (Phase 6B, 2 weeks)
   - Notion bidirectional sync (Phase 6C, 2 weeks)
   - iCloud backup relay (Phase 6D, 2 weeks)

4. **File Parsing APIs**
   - `/api/v1/parse/table` — Markdown tables → SQLite
   - `/api/v1/parse/csv` — CSV import
   - `/api/v1/parse/json` — JSON import
   - `/api/v1/parse/yaml` — YAML config
   - `/api/v1/export/table` — SQLite → `.table.md`
   - `/api/v1/execute/sql` — SQL execution
   - `/api/v1/feed/generate` — RSS generation

**Key Deliverables:**

- 🔲 OAuth handler implementation
- 🔲 HubSpot integration
- 🔲 Notion integration
- 🔲 iCloud relay
- 🔲 Workflow management system
- 🔲 File parsing API endpoints
- 🔲 Optimization, reliability, and hardening checklist completed (see Round 2 plan)

**References:**

- [Workflow Management Spec](specs/workflow-management.md)
- [OAuth Integration Plan](/dev/docs/roadmap.md#phase-6)

---

### Round 3: Wizard Web UI — Svelt + Notion Styling + Webhooks

**Owner:** Wizard (`/wizard/dashboard/`)
**Status:** v1.0.0 — Design Complete, Implementation Ready
**Timeline:** 2-3 weeks (component library + Notion webhook wiring)

**Components:**

1. **Svelt Component Library for Notion Blocks**
   - Block rendering components (paragraph, heading, bullet, code, etc.)
   - Interactive form blocks (text, select, checkbox, date)
   - Styled using Tailwind CSS (consistent with dashboard)
   - Real-time preview of Notion block changes
   - Editable inline with validation

2. **Notion Webhook Integration Panel**
   - Visual queue status (pending, processing, completed, failed)
   - Block change history timeline
   - Manual sync trigger with progress indicator
   - Conflict detection & resolution UI
   - Sync statistics dashboard

3. **Tailwind + Svelt Theme System**
   - Notion-inspired color palette (gray, blue, red, yellow)
   - Light/dark mode toggle
   - Responsive grid layouts (mobile → desktop)
   - Typography scale (H1-H6, body, code)
   - Component state styles (hover, active, disabled, error)

4. **Bi-Directional Block Mapper UI**
   - Visual mapping editor (uDOS markdown ↔ Notion blocks)
   - Drag-and-drop property assignment
   - Real-time preview of mapped output
   - Save/load mapping profiles

**Key Deliverables:**

- 🔲 Svelt block components (12+ components)
- 🔲 Notion webhook status panel
- 🔲 Tailwind theme configuration
- 🔲 Block mapper UI with drag-and-drop
- 🔲 Sync history timeline component
- 🔲 Conflict resolution modal
- 🔲 Integration with `notion_routes.py` endpoints
- 🔲 Dark mode toggle persistence

**References:**

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Svelte Component Guide](https://svelte.dev/docs)
- [Notion Block Types](https://developers.notion.com/reference/block)
- [WIKI-FRONTMATTER-GUIDE.md](WIKI-FRONTMATTER-GUIDE.md) (block metadata)

---

### Round 4: Wizard Web Browser — SQLite Dataset Rendering

**Owner:** Wizard (`/wizard/dashboard/`)
**Status:** v1.0.0 — Specification Ready
**Timeline:** 2-3 weeks (table components + data binding)

**Components:**

1. **Interactive Dataset Table Component**
   - Sortable columns (click header to toggle ASC/DESC)
   - Filterable rows (search, column filters)
   - Pagination (configurable page size: 10, 25, 50, 100)
   - Row selection (checkbox for bulk operations)
   - Responsive design (horizontal scroll on mobile)

2. **SQLite Data Binding**
   - `/api/v1/data/tables` — List available tables from memory/wizard/*.db
   - `/api/v1/data/query` — Execute parameterized SQL (SELECT only)
   - `/api/v1/data/schema` — Fetch table schema (columns, types, constraints)
   - `/api/v1/data/export` — Export to CSV, JSON, XLSX
   - Caching layer to avoid repeated queries

3. **Data Visualization Options**
   - Table (default, sortable, filterable)
   - Cards (grid view with custom templates)
   - Timeline (date-based rows)
   - Kanban (group by column, drag-to-update)
   - Chart (bar, line, pie — via Chart.js)

4. **Spatial Filesystem Integration**
   - Render @workspace/@location tagged datasets
   - Location-aware cell highlighting (L###-Cell pattern)
   - Grid overlay for spatial reference
   - Tag-based filtering (show rows matching selected tags)

5. **Tailwind + Svelt Styling**
   - Table header with sort/filter icons
   - Alternating row colors (zebra striping)
   - Hover effects (row highlight, cell expansion)
   - Cell formatting (currency, date, boolean, links)
   - Empty state message (no data)

**Key Deliverables:**

- 🔲 DataTable Svelt component (core sorting/filtering)
- 🔲 DataVisualization wrapper (toggle table → cards → chart)
- 🔲 `/api/v1/data/*` endpoint implementation
- 🔲 ChartJS integration (bar, line, pie, scatter)
- 🔲 CSV/JSON/XLSX export pipeline
- 🔲 Spatial tagging selector (filter by @location/@workspace)
- 🔲 SQL query builder UI (for power users)
- 🔲 Data refresh controls (poll interval, manual refresh)
- 🔲 Performance tests (1M+ row datasets)

**References:**

- [SvelteKit Tutorial](https://learn.svelte.dev/)
- [Tailwind Table Patterns](https://tailwindcss.com/docs/table)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [File Parsing Architecture Spec](specs/file-parsing-architecture.md)
- [Spatial Filesystem Spec](specs/SPATIAL-FILESYSTEM.md)

---

### Round 5: Wizard Web Browser — Teletext Mode Display

**Owner:** Wizard (`/wizard/dashboard/`) + Extensions (`/extensions/api/`)
**Status:** v0.5.0 — Design Phase (Exploring NES Button Integration)
**Timeline:** 3-4 weeks (grid rendering + button styling exploration)

**Components:**

1. **Teletext Grid Renderer**
   - 12×16 character grid (120×240 pixels at 10×15px per char)
   - SIXEL graphics support (VT340 palette: 262,144 colors)
   - Monospace font (Courier, Monaco, or custom bitmap font)
   - No CSS/Tailwind — pure pixel-perfect rendering
   - Color palette: 8-bit ANSI + custom RGB (24-bit)
   - Line drawing characters (box, angles, shading)

2. **Teletext Content Modes**
   - **Text Mode**: ASCII + line drawing (240×240 character viewport)
   - **Graphics Mode**: SIXEL or UDG (user-defined graphics)
   - **Mixed Mode**: Text + inline SIXEL graphics
   - **Cursor**: Blinking block or underline
   - **Scrolling**: Smooth vertical/horizontal scroll

3. **NES-Style Button Exploration** ⚠️ *Design TBD*
   - Question: Use SVG buttons or simulate with ANSI box characters?
   - Option A: SVG overlay on teletext grid (lose authenticity, easy styling)
   - Option B: Teletext-native buttons (text + line-drawing chars, pixel-perfect)
   - Option C: Hybrid (teletext content + NES-styled button bar at bottom)
   - **Recommendation**: Start with Option B (line-drawing chars as button borders)
   - Button styles: Raised (top-left light), sunken (bottom-right dark)
   - Labels: Center-aligned, fixed-width (8-10 chars)
   - States: Normal, hover (inverted), pressed (reversed video)

4. **Input & Interaction**
   - Keyboard navigation (arrow keys, ENTER, ESC, F-keys)
   - Numpad support (0-9 for menu selection)
   - Mouse click detection (map screen coords → grid cell)
   - Terminal resize handling (preserve content, reflow layout)

5. **Wizard Integration Points**
   - `/api/v0/teletext/render` — Render `.tty` or `.ans` file to SIXEL/HTML5 canvas
   - `/api/v0/teletext/input` — Submit user input (key press, mouse click)
   - `/api/v0/teletext/session` — Manage persistent terminal state (session ID, scrollback)
   - Serve retro dashboard: Status, Tasks, Messages, Maps as teletext pages
   - Navigation menu: Teletext-native (nested lists, numbered options)

6. **Implementation Options**
   - **Canvas (HTML5 Canvas API)**: Full control, pixel-perfect, no CSS
   - **SVG**: Scalable, DOM elements, harder for performance
   - **xterm.js**: Full terminal emulator, but heavyweight
   - **Custom WebGL**: Overkill unless 4K rendering needed
   - **Recommendation**: Start with Canvas API (2D context), fallback to SVG

7. **Sveltekit Integration Questions** 🤔
   - Can we bind a Canvas to a Svelt reactive component?
   - How to handle real-time updates (scroll, input)?
   - Mouse/keyboard event delegation (capture in component)?
   - Dark mode support (swap color palette, not CSS)?
   - Printing support (teletext → PDF, preserve layout)?

**Key Deliverables:**

- 🔲 TeletextRenderer class (Canvas-based, 12×16 grid)
- 🔲 SIXEL palette definition (262k colors)
- 🔲 Character bitmap font (10×15px monospace)
- 🔲 Line-drawing character set (box, corners, shading)
- 🔲 NES-button simulator (using teletext chars or SVG overlay — TBD)
- 🔲 Input event handler (keyboard, mouse, numpad)
- 🔲 Svelt component wrapper (TeletextDisplay)
- 🔲 Sveltekit routes for teletext endpoints
- 🔲 Example teletext pages (Status, Tasks, Map)
- 🔲 Dark mode palette (preserve authenticity)
- 🔲 Design doc: "NES Buttons in Teletext Mode" (recommendations)

**Open Questions:**

1. **Button Style**: Use ASCII line-drawing or SVG overlay?
   - Line-drawing (authentic, pixel-perfect, no CSS styling)
   - SVG overlay (easier to style, less authentic, potential z-order issues)
   - Hybrid (content in teletext, buttons in SVG at bottom)?

2. **Sveltekit Binding**: How to manage Canvas state in Svelt reactivity?
   - Use `onMount()` to initialize Canvas context?
   - How to trigger re-renders on model changes?
   - Can we use Svelt stores for teletext state?

3. **Font**: Bitmap or web font?
   - Bitmap (perfect pixels, fixed size, fast rendering)
   - Web font (scalable, supports Unicode, slower)
   - Recommendation: Start with bitmap (10×15px), upgrade to web font later

4. **Color Palette**: Full 262k SIXEL or reduced 256-color ANSI?
   - 262k (authentic VT340, flexible styling)
   - 256-color (smaller, still vibrant, better compatibility)
   - Recommendation: Start with 256-color, upgrade to 262k if needed

5. **Performance**: How to handle large scrollback (1000+ lines)?
   - Canvas render on-demand (only visible viewport)
   - Scrollback storage (circular buffer in memory)
   - Lazy load from database (historical logs)

**References:**

- [VT340 Sixel Graphics](https://en.wikipedia.org/wiki/Sixel)
- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Teletext (Videotext) Standard](https://en.wikipedia.org/wiki/Teletext)
- [HTML5 Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [NES UI Design](https://www.pixelationsgame.com/the-nes-user-interface-operating-system/)
- [Sveltekit Component Binding](https://svelte.dev/docs/component-instance-exports)
- [Grid Computing Spec](specs/grid-spatial-computing.md) (related: spatial addressing)

---

### Round 6: Beacon Portal (WiFi Infrastructure)

**Owner:** Wizard (`/wizard/`) + Extensions  
**Status:** v1.0.0 — Specification Complete, Ready for Integration  
**Timeline:** 2-3 weeks (implementation)

**Components:**

1. **Sonic Screwdriver Device Catalog**
   - Device identification (vendor, model, year, CPU, GPU, TPM, BIOS)
   - Reflashing method recommendations
   - Driver sourcing
   - Hardware compatibility tracking
   - Community contributions

2. **Beacon Portal (WiFi Infrastructure)**
   - WiFi access point configuration (2.4GHz, 5GHz, dual-band)
   - Two modes: Private-Home (WPA3 passphrase) + Public-Secure (registration)
   - Captive portal with offline fallback
   - Device registration + pairing
   - Local plugin caching

3. **VPN Tunnel (WireGuard)**
   - Encrypted gateway between beacon and Wizard
   - ChaCha20-Poly1305 cipher (AEAD)
   - Curve25519 key exchange (post-quantum)
   - Cost-aware escalation (local-first with cloud fallback)
   - Per-device quota enforcement

4. **Device Quota Management**
   - Monthly cloud budget per device ($5–$10 default)
   - Cost tracking per request
   - Quota enforcement before execution
   - Monthly reset + emergency top-up
   - Budget alerts at 80%

**Key Deliverables:**

- ✅ SONIC-SCREWDRIVER.md specification
- ✅ BEACON-PORTAL.md specification
- ✅ BEACON-VPN-TUNNEL.md specification
- ✅ beacon_routes.py (13 API endpoints)
- ✅ beacon_service.py (SQLite backend)
- ✅ BEACON-IMPLEMENTATION.md (integration guide)
- ✅ BEACON-QUICK-REFERENCE.md (user guide)
- 🔲 Wizard server route registration
- 🔲 Hardware setup guides (4 device categories)
- 🔲 WireGuard config generation
- 🔲 Quota enforcement middleware
- 🔲 Integration tests + load testing

**References:**

- [SONIC-SCREWDRIVER.md](wiki/SONIC-SCREWDRIVER.md)
- [BEACON-PORTAL.md](wiki/BEACON-PORTAL.md)
- [BEACON-VPN-TUNNEL.md](wiki/BEACON-VPN-TUNNEL.md)
- [BEACON-IMPLEMENTATION.md](../wizard/docs/BEACON-IMPLEMENTATION.md)
- [BEACON-QUICK-REFERENCE.md](wiki/BEACON-QUICK-REFERENCE.md)

---

### Round 7: Goblin Dev Server (Experimental)

**Owner:** Goblin (`/dev/goblin/`)  
**Status:** v0.2.0 — Experimental  
**Timeline:** Ongoing (feature graduation to Wizard/Core)

**Active Features:**

1. **Binder Compiler**
   - Graduated to Core for production usage
   - Goblin dev routes should call Core binder services

2. **Screwdriver Provisioner**
   - Device flash pack creation
   - SD card image preparation
   - Configuration templates
   - Device registration

3. **MeshCore Manager**
   - P2P mesh network device management
   - Device pairing & discovery
   - Mesh routing configuration
   - Transport policy enforcement

**Graduation Path:**

- Stable features → Wizard Server
- Core runtime features → Core
- Archived experiments → `.archive/`

**Key Deliverables:**

- 🔲 Binder compiler service implementation
- 🔲 Screwdriver flash pack system
- 🔲 MeshCore device manager

---

### Round 8: Wizard Plugin Ecosystem — Modular Distribution & Bolt-Ons

**Owner:** Wizard (`/wizard/`) + Extensions (`/extensions/`)  
**Status:** v0.8.0 — Architecture Design Phase  
**Timeline:** 3-4 weeks (plugin system + distribution library)

**Components:**

1. **Plugin Architecture (Bolt-On Repos)**
   - Plugin manifest spec (YAML/JSON: name, version, dependencies, entry points)
   - Containerized plugin loading (isolate dependencies, sandboxed execution)
   - Mod overlay system (override Core/Wizard behavior without forking)
   - Plugin lifecycle hooks (init, activate, deactivate, uninstall)
   - API surface for plugins (core services, wizard endpoints, UI components)
   - Permission model (filesystem, network, database, UI access control)

2. **Wizard Plugins Management UI**
   - Plugin browser dashboard (`/wizard/dashboard/routes/Plugins.svelte`)
   - Visual plugin cards (name, description, version, author, status)
   - Toggle controls (enable/disable per plugin)
   - Update checker (compare local version vs remote)
   - Install/uninstall with dependency resolution
   - Plugin settings panel (per-plugin configuration)
   - Health status (running, crashed, disabled, outdated)

3. **Distribution & Packaging Library**
   - `PackageManager` service (`/wizard/services/package_manager.py`)
   - Track online repo (GitHub releases, git tags, manifest URLs)
   - Track local cloned version (installed path, commit hash, version)
   - Version comparison (semver-aware: major.minor.patch)
   - Auto-update scheduler (check daily, prompt user, apply updates)
   - Rollback support (revert to previous version on failure)
   - Multi-source registries (GitHub, GitLab, custom CDN)

4. **Bolt-On Repo Structure**
   - Standard plugin template (cookiecutter or scaffold CLI)
   - Plugin metadata file: `plugin.yaml` (name, version, entry, dependencies)
   - Entry point convention: `plugin/__init__.py` (register routes/services)
   - Mod overlay convention: `mods/` directory (overrides for core files)
   - Documentation: `README.md` + `CHANGELOG.md` + `LICENSE`
   - Distribution: GitHub releases with versioned tarballs

5. **Immediate Bolt-On Candidates**
   - **uDOS-sonic** (Sonic Screwdriver device catalog)
   - **Groovebox** (sample library + music scripting)
   - **Beacon Portal** (WiFi + VPN infrastructure)
   - **MeshCore** (P2P mesh networking)
   - **Community Extensions** (user-contributed plugins)

6. **Mod Overlay System**
   - Overlay spec: `mods/core/commands/custom_handler.py` → replaces Core handler
   - Wizard checks `mods/` directory before loading default modules
   - Precedence: Plugin Mods → Local Mods → Core Defaults
   - Conflict detection (multiple plugins overriding same file)
   - Versioning: Tag mod overlays with compatible uDOS versions

**Key Deliverables:**

- 🔲 Plugin manifest spec (`docs/specs/PLUGIN-ARCHITECTURE.md`)
- 🔲 `PackageManager` service implementation
- 🔲 Plugin browser UI (Wizard dashboard)
- 🔲 Install/update/uninstall workflows
- 🔲 Mod overlay loader (check `mods/` before defaults)
- 🔲 Plugin template repository (cookiecutter scaffold)
- 🔲 Bolt-on packaging for uDOS-sonic (first external plugin)
- 🔲 Version tracking database (`memory/wizard/plugins.db`)
- 🔲 Auto-update scheduler with rollback
- 🔲 Permission model enforcement (sandbox plugins)
- 🔲 Integration tests (install, enable, disable, update, uninstall)

**API Endpoints:**

- `/api/v1/plugins/list` — List installed plugins
- `/api/v1/plugins/available` — List available plugins from registry
- `/api/v1/plugins/install` — Install plugin by name/URL
- `/api/v1/plugins/update` — Update plugin to latest version
- `/api/v1/plugins/uninstall` — Remove plugin
- `/api/v1/plugins/toggle` — Enable/disable plugin
- `/api/v1/plugins/config` — Get/set plugin configuration
- `/api/v1/plugins/check-updates` — Check for updates

**References:**

- [Wizard Architecture](../wizard/ARCHITECTURE.md) (services + routes)
- [Extensions API](../extensions/api/) (transport + server_manager)
- [Mod Overlay Pattern](https://flask.palletsprojects.com/en/2.3.x/blueprints/) (Flask blueprints)
- [Semantic Versioning](https://semver.org/) (version comparison)

---

### Round 9: App Development (Tauri + Future Native)

**Owner:** App (`/app/`)  
**Status:** v1.0.3 — Active Development  
**Timeline:** 8-12 weeks

**Components:**

1. **Typo Editor Foundation**
   - Markdown-first editor/reader
   - File browser (iCloud + local)
   - Reading mode (distraction-free)
   - Editing mode (syntax highlighting)
   - Live preview

2. **File Converters**
   - Image → text (OCR)
   - PDF → Markdown
   - HTML → Markdown
   - Text → `.table.md`
   - Markdown → PDF/HTML

3. **Typography & Fonts**
   - Monaspace integration (5 fonts: Argon, Xenon, Krypton, Neon, Radon)
   - Per-block typographic voice
   - Heading vs body font separation
   - macOS system font integration
   - AI provenance visualization (light weight, dashed underline, etc.)

4. **Emoji & Graphics**
   - Noto Emoji rendering
   - GitHub `:emoji:` token support
   - Pixel editor integration
   - Consistent cross-platform rendering

5. **Runtime Features**
   - uCode/uPY templating (safe execution)
   - Marp slide mode
   - Typeform-style forms
   - Sandboxed script execution (Phase 2)

6. **Migration to /app**
   - Public scaffold with private submodule at /app
   - Dev launchers and docs (App Store + Xcode prep)
   - macOS integration stubs (file dialogs, notifications, keychain)

**Key Deliverables:**

- 🔲 Typo editor core
- 🔲 Converter pipeline
- 🔲 Monaspace typography
- 🔲 Emoji system
- 🔲 uCode renderer
- 🔲 Marp/form modes
- 🔲 /app migration and submodule wiring

**References:**

- [Mac App Roadmap](specs/mac-app-roadmap.md)
- [File Extensions & Parsing](specs/app-file-extensions.md)

**Components:**

1. **Sample Library Management**
   - Audio sample database (`memory/groovebox/samples.db`)
   - Sample metadata (name, duration, BPM, key, genre, tags, waveform)
   - Waveform preview generation (PNG thumbnail, 800×100px)
   - Audio file formats (WAV, MP3, FLAC, OGG)
   - Sample packs (collections of related samples)
   - Tagging system (instrument, mood, genre, energy level)
   - Search & filter (by BPM, key, tags, duration)
   - Import/export sample packs (ZIP archive with manifest)

2. **Songscribe — Music Notation in Markdown**
   - Music notation syntax (inspired by ABC notation, adapted for Markdown)
   - Inline notation blocks (triple backticks: ```music)
   - Chord notation (C, Dm, G7, Cmaj7, etc.)
   - Melody notation (C4 D4 E4 F4 G4 A4 B4 C5)
   - Rhythm notation (whole, half, quarter, eighth notes)
   - Time signatures (4/4, 3/4, 6/8)
   - Key signatures (C major, A minor, etc.)
   - Lyrics alignment (sync text with melody)

3. **Music Rendering**
   - **Markdown → Sheet Music**: Render notation blocks as SVG staff notation
   - **Markdown → Audio**: Synthesize MIDI from notation (via FluidSynth or similar)
   - **Markdown → Tablature**: Guitar/bass tabs from notation
   - **Markdown → Chord Charts**: Visual chord diagrams
   - Export formats: PDF, MIDI, MusicXML, Lilypond

4. **Groovebox Integration**
   - Load samples from library into groovebox tracks
   - Step sequencer (16-step, 8 tracks, BPM control)
   - Pattern editor (create loops, save patterns)
   - Song arrangement (sequence patterns into full songs)
   - Real-time playback (via Web Audio API or ALSA)
   - Export to WAV, MP3, or MIDI

5. **Songscribe Markdown Syntax (Draft)**
   ```markdown
   # My Song Title
   
   **Tempo:** 120 BPM  
   **Key:** C Major  
   **Time:** 4/4
   
   ## Verse
   ```music
   | C     | Am    | F     | G     |
   | C4 E4 | G4 A4 | F4 A4 | G4 B4 |
   Lyrics: "This is the first line of my song"
   ```
   
   ## Chorus
   ```music
   | F     | G     | C     | Am    |
   | F4 A4 | G4 B4 | C5 E5 | A4 C5 |
   Lyrics: "This is the chorus line"
   ```
   ```

6. **Wizard Integration**
   - `/api/v1/groovebox/samples` — List samples
   - `/api/v1/groovebox/samples/upload` — Add new sample
   - `/api/v1/groovebox/samples/waveform` — Generate waveform PNG
   - `/api/v1/groovebox/render` — Render songscribe Markdown → audio/sheet
   - `/api/v1/groovebox/export` — Export song as WAV/MIDI
   - `/api/v1/groovebox/patterns` — CRUD for patterns
   - `/api/v1/groovebox/play` — Real-time playback

7. **UI Components (Wizard Dashboard)**
   - Sample browser (grid view, waveform previews, play button)
   - Pattern editor (step sequencer grid, 16×8 matrix)
   - Song arranger (timeline view, drag-and-drop patterns)
   - Songscribe editor (Markdown preview + audio playback)
   - Export modal (format selection, quality settings)

**Key Deliverables:**

- 🔲 Sample database schema + migration
- 🔲 Sample library service (`groovebox/services/sample_manager.py`)
- 🔲 Waveform generator (audio → PNG)
- 🔲 Songscribe parser (Markdown → music AST)
- 🔲 Music renderer (AST → SVG staff notation)
- 🔲 Audio synthesizer (AST → MIDI → WAV)
- 🔲 Step sequencer component (Svelt grid UI)
- 🔲 Pattern storage (SQLite patterns table)
- 🔲 Song arrangement service
- 🔲 Real-time audio playback (Web Audio API)
- 🔲 Export pipeline (WAV, MP3, MIDI, PDF)
- 🔲 Sample browser UI (Wizard dashboard)
- 🔲 Integration with Wizard file picker (import samples)
- 🔲 Documentation: Songscribe syntax guide

**Open Questions:**

1. **Music Notation Standard**: Use ABC notation as-is, or create custom syntax?
   - ABC (established, tool support, learning curve)
   - Custom (Markdown-native, simpler, less tooling)
   - Recommendation: Start with ABC-inspired, simplify for MVP

2. **Audio Synthesis**: Server-side (FluidSynth) or client-side (Web Audio API)?
   - Server-side (better quality, CPU-intensive, latency)
   - Client-side (lower latency, browser support, limited quality)
   - Recommendation: Client-side for preview, server-side for export

3. **Sample Storage**: Store in filesystem or embed in database?
   - Filesystem (better for large files, harder to sync)
   - Database (easier to sync, size limits, slower access)
   - Recommendation: Filesystem with metadata in database

4. **Real-Time Collaboration**: Support multi-user pattern editing?
   - Deferred to later phase (requires WebSocket + conflict resolution)

**References:**

- [ABC Notation Standard](https://abcnotation.com/)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [VexFlow](https://www.vexflow.com/) (music notation rendering in JS)
- [FluidSynth](https://www.fluidsynth.org/) (MIDI synthesizer)
- [MusicXML](https://www.musicxml.com/) (interchange format)

---

## 📊 Feature Matrix

| Feature             | Core | Wizard | Wizard (Beacon)  | Wizard (Web UI) | Wizard (Plugins) | Groovebox | Goblin | App   |
| ------------------- | ---- | ------ | ---------------- | --------------- | ---------------- | --------- | ------ | ----- |
| TS Markdown Runtime | ✅   | —      | —                | —               | —                | —         | —      | ✅    |
| Grid/Spatial System | ✅   | —      | —                | —               | —                | —         | —      | ✅    |
| File Parsing        | ✅   | ✅ API | —                | —               | —                | —         | —      | ✅ UI |
| OAuth Integration   | —    | ✅     | —                | —               | —                | —         | —      | —     |
| Workflow Management | —    | ✅     | —                | —               | —                | —         | 🧪     | —     |
| Binder Compilation  | —    | ✅     | —                | —               | —                | —         | 🧪     | —     |
| Notion Webhooks     | —    | ✅     | —                | ✅ (Round 3)    | —                | —         | —      | —     |
| Svelt Components    | —    | —      | —                | ✅ (Round 3)    | ✅ (Round 8)     | ✅ (R10)  | —      | —     |
| Dataset Tables      | —    | —      | —                | ✅ (Round 4)    | —                | —         | —      | —     |
| SQLite Binding      | —    | ✅ API | —                | ✅ (Round 4)    | —                | ✅ (R10)  | —      | —     |
| Teletext Mode       | —    | —      | —                | ✅ (Round 5)    | —                | —         | —      | —     |
| NES Buttons (R5)    | —    | —      | —                | 🤔 Exploring    | —                | —         | —      | —     |
| Plugin System       | —    | —      | —                | —               | ✅ (Round 8)     | —         | —      | —     |
| Mod Overlays        | —    | —      | —                | —               | ✅ (Round 8)     | —         | —      | —     |
| Package Manager     | —    | ✅     | —                | ✅ UI           | ✅ (Round 8)     | —         | —      | —     |
| Sample Library      | —    | —      | —                | —               | —                | ✅ (R10)  | —      | —     |
| Music Notation      | —    | —      | —                | —               | —                | ✅ (R10)  | —      | —     |
| Step Sequencer      | —    | —      | —                | —               | —                | ✅ (R10)  | —      | —     |
| Audio Synthesis     | —    | —      | —                | —               | —                | ✅ (R10)  | —      | —     |
| Device Provisioning | —    | —      | —                | —               | 🧪 (Plugin)      | —         | 🧪     | —     |
| MeshCore Manager    | —    | —      | —                | —               | 🧪 (Plugin)      | —         | 🧪     | —     |
| Beacon Portal       | —    | —      | ✅ (Round 6)     | —               | 🧪 (Plugin)      | —         | —      | —     |
| Device Quota        | —    | —      | ✅ (Round 6)     | —               | —                | —         | —      | —     |
| VPN Tunneling       | —    | —      | ✅ (Round 6)     | —               | —                | —         | —      | —     |
| Typography System   | —    | —      | —                | —               | —                | —         | —      | ✅    |
| Converters          | —    | —      | —                | —               | —                | —         | —      | ✅    |

Legend: ✅ Primary, 🧪 Experimental, — Not applicable

---

## 🗓️ Milestone Timeline

### Q1 2026 (Jan-Mar)

**January:**

- ✅ Wizard/Goblin dashboard integration (COMPLETE 2026-01-24)
- ✅ Goblin feature cleanup (COMPLETE 2026-01-24)
- ✅ Beacon Portal specification & scaffold (COMPLETE 2026-01-25)
- ✅ Specs consolidation (COMPLETE 2026-01-25)

**February:**

- 🔲 Round 3: Wizard Web UI — Svelt + Notion Styling (Weeks 1-2)
  - Notion block components
  - Webhook status panel
  - Tailwind theme system
- 🔲 Core: TS Markdown Runtime (Weeks 1-4)
- 🔲 Core: Grid Runtime Phase 1 (Weeks 3-6)
- 🔲 Wizard: OAuth Foundation (Phase 6A, Weeks 1-2)

**March:**

- 🔲 Round 4: Wizard Web Browser — Dataset Tables (Weeks 1-2)
  - SQLite data binding
  - Sortable/filterable table component
  - Chart visualization
- 🔲 Round 5: Wizard Web Browser — Teletext Mode (Weeks 3-4)
  - Canvas-based grid renderer
  - NES button exploration
  - Sveltekit component integration
- 🔲 Core: File Parsing System
- 🔲 Wizard: Notion Integration (Phase 6C)
- 🔲 Wizard: iCloud Relay (Phase 6D)
- 🔲 App: Typo Editor Foundation

### Q2 2026 (Apr-Jun)

- 🔲 Round 6: Beacon Portal integration
- 🔲 Round 8: Wizard Plugin Ecosystem (Weeks 1-3)
  - Plugin architecture + manifest spec
  - Package manager service
  - Plugins management UI
  - Mod overlay system
- 🔲 Round 10: Groovebox + Songscribe (Weeks 4-9)
  - Sample library management
  - Music notation parser (Markdown → music)
  - Step sequencer + pattern editor
  - Audio synthesis + export
- 🔲 Round 9: App (Typo Editor + Converters)
- 🔲 Wizard: Workflow Management
- 🔲 Core: Grid Runtime Phase 2 (Animation, Sprites)

---

## 📁 Documentation Organization

### Promoted to `/docs/specs/`

- `typescript-markdown-runtime.md` — TS runtime spec
- `grid-spatial-computing.md` — Spatial addressing & layers
- `file-parsing-architecture.md` — File parsing system
- `workflow-management.md` — Project/workflow system
- `mac-app-roadmap.md` — App development plan
- `app-file-extensions.md` — File type taxonomy

### Moved to `/docs/examples/`

- `example-script.md` — Complete runtime example
- `example-sqlite-db.md` — Database schema examples
- `grid-runtime-examples.md` — Grid rendering examples

### Archived to `.archive/`

- Original roadmap files after promotion

---

## 🎯 Next Actions (2026-01-31)

1. ✅ Document development rounds 3–10 (`docs/specs/ROUNDS-3-10.md`)
2. ✅ Move specs to `/docs/specs/`
3. ✅ Move examples to `/docs/examples/`
4. 🔲 Create Round 3 design spec: `docs/specs/WIZARD-WEB-UI-NOTION.md`
5. 🔲 Create Round 4 design spec: `docs/specs/WIZARD-DATASET-TABLES.md`
6. 🔲 Create Round 5 design doc: `docs/specs/WIZARD-TELETEXT-MODE.md` (with NES button exploration)
7. 🔲 Create Round 8 design spec: `docs/specs/PLUGIN-ARCHITECTURE.md`
8. 🔲 Create Round 10 design spec: `docs/specs/GROOVEBOX-SONGSCRIBE.md`
9. 🔲 Update `/dev/docs/roadmap.md` with new rounds
10. 🔲 Create implementation tickets for Q1 2026 (Rounds 3-5) and Q2 2026 (Rounds 8-10)
11. 🔲 Add regression tests for `DateTimeApproval`/TUI approval flows (`tui/tests/test_form_fields.py`)
12. 🔲 Keep `docs/ROADMAP-TODO.md` synced with roadmap outstanding items

---

**Status:** Active Planning Document (v1.2.0 Roadmap Updated)  
**Maintained by:** uDOS Engineering Team  
**Next Review:** 2026-02-07
**Recent Updates:** Added Rounds 8-10 (Plugin Ecosystem, Groovebox + Songscribe, App Development)
