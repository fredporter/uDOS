# uDOS Development Streams (2026-01-24)

**Version:** v1.0.7.0 Planning  
**Last Updated:** 2026-01-24  
**Status:** Active Roadmap

---

## 📋 Executive Summary

This document consolidates all active development streams across Core, Wizard, Goblin, and App workspaces based on recent roadmap analysis.

---

## 🎯 Development Streams

### Stream 1: Core Runtime (TypeScript Markdown + Grid)

**Owner:** Core (`/core/`)  
**Status:** v1.0.7.0 — Active build  
**Timeline:** 4-6 weeks

**Components:**

1. **TypeScript Markdown Runtime**
   - State management (`$variables`)
   - Runtime blocks: `state`, `set`, `form`, `if/else`, `nav`, `panel`, `map`
   - Variable interpolation in Markdown text
   - SQLite DB binding (read-only)
   - Core execution via Node runner (parse + execute)
   - Deterministic execution model

2. **Grid Runtime + Spatial Computing**
   - Fractal addressing (L###-Cell pattern)
   - Layer bands (SUR/UDN/SUB)
   - Viewport rendering (80x30 canonical, 40x15 mini)
   - Tile system (16×24 pixels, 5-bit palette)
   - Sextant/quadrant/ASCII fallback rendering
   - Sprite animation support

3. **File Parsing System**
   - Markdown table parser (`.table.md`)
   - CSV/TSV importer
   - JSON/JSONL parser
   - YAML/TOML config parser
   - SQL executor
   - RSS feed generation

4. **Binder + Dataset Operations (Core)**
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
- ✅ Binder compiler moved to Core
- ✅ Dataset manager + regen tools
- ✅ Output toolkit (ASCII-first)
- 🔲 Core runtime implementation (full TS runtime support)
- 🔲 Grid viewport renderer (beyond base map render)
- 🔲 File parser integration (CSV/JSON/YAML/SQL)

**References:**

- [TypeScript Markdown Runtime Spec](specs/typescript-markdown-runtime.md)
- [Grid & Spatial Computing Spec](specs/grid-spatial-computing.md)
- [File Parsing Architecture](specs/file-parsing-architecture.md)
- [Example Scripts](examples/)

---

### Stream 2: Wizard Server (Production Services)

**Owner:** Wizard (`/wizard/`)  
**Status:** v1.1.0.0 — Stable, Phase 6 Planning  
**Timeline:** 4-8 weeks (Phase 6A-6D)

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

**References:**

- [Workflow Management Spec](specs/workflow-management.md)
- [OAuth Integration Plan](/dev/docs/roadmap.md#phase-6)

---

### Stream 3: Goblin Dev Server (Experimental)

**Owner:** Goblin (`/dev/goblin/`)  
**Status:** v0.2.0.0 — Experimental  
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

### Stream 4: App Development (Tauri + Future Native)

**Owner:** App (`/app/`)  
**Status:** v1.0.3.0 — Active Development  
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
   - Public scaffold with private submodule at /app/src
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

---

## 📊 Feature Matrix

| Feature             | Core | Wizard | Goblin | App   |
| ------------------- | ---- | ------ | ------ | ----- |
| TS Markdown Runtime | ✅   | —      | —      | ✅    |
| Grid/Spatial System | ✅   | —      | —      | ✅    |
| File Parsing        | ✅   | ✅ API | —      | ✅ UI |
| OAuth Integration   | —    | ✅     | —      | —     |
| Workflow Management | —    | ✅     | 🧪     | —     |
| Binder Compilation  | —    | ✅     | 🧪     | —     |
| Device Provisioning | —    | —      | 🧪     | —     |
| MeshCore Manager    | —    | —      | 🧪     | —     |
| Typography System   | —    | —      | —      | ✅    |
| Converters          | —    | —      | —      | ✅    |

Legend: ✅ Primary, 🧪 Experimental, — Not applicable

---

## 🗓️ Milestone Timeline

### Q1 2026 (Jan-Mar)

**January:**

- ✅ Wizard/Goblin dashboard integration (COMPLETE 2026-01-24)
- ✅ Goblin feature cleanup (COMPLETE 2026-01-24)
- 🔲 Specs consolidation (IN PROGRESS 2026-01-24)

**February:**

- 🔲 Core: TS Markdown Runtime (Weeks 1-4)
- 🔲 Core: Grid Runtime Phase 1 (Weeks 3-6)
- 🔲 Wizard: OAuth Foundation (Phase 6A, Weeks 1-2)
- 🔲 Wizard: HubSpot Integration (Phase 6B, Weeks 3-4)

**March:**

- 🔲 Core: File Parsing System
- 🔲 Wizard: Notion Integration (Phase 6C)
- 🔲 Wizard: iCloud Relay (Phase 6D)
- 🔲 App: Typo Editor Foundation

### Q2 2026 (Apr-Jun)

- 🔲 App: Converter Pipeline
- 🔲 App: Monaspace Typography
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

## 🎯 Next Actions (2026-01-24)

1. ✅ Create development streams document
2. ✅ Move specs to `/docs/specs/`
3. ✅ Move examples to `/docs/examples/`
4. 🔲 Update `/dev/docs/roadmap.md` with stream references
5. 🔲 Archive processed roadmap files to `.archive/2026-01-24/`
6. 🔲 Create implementation tickets for v1.0.7.0

---

**Status:** Active Planning Document  
**Maintained by:** uDOS Engineering Team  
**Next Review:** 2026-02-01
