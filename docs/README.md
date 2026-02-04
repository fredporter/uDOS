# uDOS Documentation — Developer Reference

**Last Updated:** February 3, 2026
**Version:** v1.0.7

> 🎯 **For users?** Go to [/wiki/START-HERE.md](../wiki/START-HERE.md)
> 🚀 **For getting started?** Read [/QUICKSTART.md](../QUICKSTART.md)
> 📝 **For contributing?** See [/wiki/CONTRIBUTING.md](../wiki/CONTRIBUTING.md)

---

## 🎯 Core References (Start Here)

| Document | Purpose |
|----------|---------|
| [/AGENTS.md](../AGENTS.md) | How work is organized (boundaries, policies, tools) |
| [/QUICKSTART.md](../QUICKSTART.md) | Install & run uDOS (5 min) |
| [/INSTALLATION.md](../INSTALLATION.md) | Detailed setup for all platforms |
| [ROADMAP-TODO.md](ROADMAP-TODO.md) | Current development roadmap |
| [specs/uCODE.md](specs/uCODE.md) | Unified Terminal TUI (main entry) |

---

## 🚀 Quick Start

```bash
python uDOS.py          # Launch unified TUI
```

Then run:
```
HELP                    # Show all commands
STATUS                  # Check installed components
```

See [specs/uCODE.md](specs/uCODE.md) for all commands.

---

## 📚 Specifications & Architecture

### Core Systems

- **[specs/uCODE.md](specs/uCODE.md)** — Terminal TUI & commands
- **[specs/SPATIAL-FILESYSTEM.md](specs/SPATIAL-FILESYSTEM.md)** — Grid filesystem with RBAC
- **[specs/grid-spatial-computing.md](specs/grid-spatial-computing.md)** — Fractal addressing & layers
- **[specs/LAYER-ARCHITECTURE.md](specs/LAYER-ARCHITECTURE.md)** — Layer system (000-799)
- **[specs/database-architecture.md](specs/DATABASE-ARCHITECTURE.md)** — SQLite ecosystem

### Document & Data

- **[specs/typescript-markdown-runtime.md](specs/typescript-markdown-runtime.md)** — Executable Markdown
- **[specs/file-parsing-architecture.md](specs/file-parsing-architecture.md)** — CSV, JSON, YAML, SQL parsing
- **[specs/wiki_spec_obsidian.md](specs/wiki_spec_obsidian.md)** — Obsidian-compatible YAML frontmatter
- **[v1-3/docs/07-grid-canvas-rendering.md](v1-3/docs/07-grid-canvas-rendering.md)** — 80×30 grid canvas rendering spec for CLI, Vibe, logs
- **[v1-3 UNIVERSE.md](v1-3 UNIVERSE.md)** — v1.3 Fractal Grid & universe mapping + location standards

### Contracts & Shared Guidance

- **[Vault-Contract.md](Vault-Contract.md)** — Vault-as-truth, export conventions, SQLite state expectations
- **[Theme-Pack-Contract.md](Theme-Pack-Contract.md)** — Theme structure, slots, metadata, exports
- **[Universal-Components-Contract.md](Universal-Components-Contract.md)** — Slot/data/CSS token alignment for static + Svelte UI lanes
- **[CSS-Tokens.md](CSS-Tokens.md)** — Shared typography, spacing, color, and elevation tokens
- **[Contributions-Contract.md](Contributions-Contract.md)** — Patch bundle format and review workflow
- **[AI-Policy-Contract.md](AI-Policy-Contract.md)** — Local vs online model governance and logging
- **[Mission-Job-Schema.md](Mission-Job-Schema.md)** — Mission/job fields, artifacts, and storage paths
- **[TUI-Vibe-Integration.md](TUI-Vibe-Integration.md)** — `.env` + Wizard keystore boundary and Vibe CLI IO hooks
- **[wizard/docs/renderer-ui-standards.md](../wizard/docs/renderer-ui-standards.md)** — Wizard renderer + Svelte module expectations
- **[Mission-Scheduler-Integration.md](Mission-Scheduler-Integration.md)** — How Vibe CLI + mission scheduler trigger renderer/export jobs

### Features

- **[specs/workflow-management.md](specs/workflow-management.md)** — Projects, tasks, automation
- **[specs/TUI-FORM-SYSTEM.md](specs/TUI-FORM-SYSTEM.md)** — Form builder & validation
- **[specs/INTERACTIVE-MENUS-IMPLEMENTATION.md](specs/INTERACTIVE-MENUS-IMPLEMENTATION.md)** — Menu system

### Deployment

- **[specs/app-file-extensions.md](specs/app-file-extensions.md)** — File types & syntax highlighting
- **[specs/mac-app-roadmap.md](specs/mac-app-roadmap.md)** — macOS Tauri app

---

## 🔧 How-To Guides

- **[howto/alpine-install.md](howto/alpine-install.md)** — Install on Alpine Linux
- **[howto/renderer-indexer-runbook.md](howto/renderer-indexer-runbook.md)** — Renderer + task indexer runbook
- **[howto/SEED-INSTALLATION-GUIDE.md](howto/SEED-INSTALLATION-GUIDE.md)** — SEED protocol setup
- **[howto/goblin-wizard-migration-checklist.md](howto/goblin-wizard-migration-checklist.md)** — Migration guide

---

## 🎵 Feature Guides

- **[features/TUI-ENHANCEMENT-ROADMAP.md](features/TUI-ENHANCEMENT-ROADMAP.md)** — TUI improvements
- **[features/config-import-export.md](features/config-import-export.md)** — Configuration system

---

## 📊 Status & Examples

### Reference & Examples

- **[examples/example-script.md](examples/example-script.md)** — Markdown runtime demo
- **[examples/grid-runtime-examples.md](examples/grid-runtime-examples.md)** — Grid system examples
- **[examples/INTERACTIVE-MENU-DEMO.md](examples/INTERACTIVE-MENU-DEMO.md)** — Menu system examples

### Decision Records

- **[decisions/ADR-0003-alpine-linux-migration.md](decisions/ADR-0003-alpine-linux-migration.md)** — Alpine migration
- **[decisions/ADR-0004-data-layer-architecture.md](decisions/ADR-0004-data-layer-architecture.md)** — Data architecture
- **[decisions/ADR-006-UDOS-ROOT-ENVIRONMENT-VARIABLE.md](decisions/ADR-006-UDOS-ROOT-ENVIRONMENT-VARIABLE.md)** — Root variable

---

## 📁 Archived Documentation

Old development notes, assessments, and historical planning are in **[.archive/](.archive/README.md)**.

Do NOT use for current development. Use for:
- ✅ Historical context
- ✅ Understanding evolution
- ✅ Reference old approaches

---

## 🗂️ Documentation Structure

```
/docs                               # Developer reference
├── README.md                       # This file
├── ROADMAP-TODO.md                 # Current work
├── specs/                          # Architecture specs
├── howto/                          # How-to guides
├── features/                       # Feature planning
├── examples/                       # Code examples
├── decisions/                      # Decision records
└── archive/                        # Old docs

/wiki                               # User guide (public)
├── README.md                       # Index
├── START-HERE.md                   # Beginner guide
├── ARCHITECTURE.md                 # System design
├── CONFIGURATION.md                # Setup
├── quick-refs/                     # Quick lookups
└── [Feature guides]

/root
├── README.md                       # Project overview
├── QUICKSTART.md                   # Get started
├── INSTALLATION.md                 # Install
├── AGENTS.md                       # How work is organized
└── [Release notes]
```

---

## 🎯 By Role

### 👤 **User/Administrator**
1. [/QUICKSTART.md](../QUICKSTART.md) — Get it running
2. [/INSTALLATION.md](../INSTALLATION.md) — Full setup
3. [/wiki/START-HERE.md](../wiki/START-HERE.md) — Beginner guide
4. [/wiki/CONFIGURATION.md](../wiki/CONFIGURATION.md) — Configure system

### 🛠️ **Developer/Contributor**
1. [/QUICKSTART.md](../QUICKSTART.md) — Get it running
2. [/AGENTS.md](../AGENTS.md) — Development guidelines
3. [specs/uCODE.md](specs/uCODE.md) — Main entry point
4. [/wiki/CONTRIBUTING.md](../wiki/CONTRIBUTING.md) — How to contribute
5. Pick specs/features relevant to your work

### 📦 **Component-Specific**

- **Core (TUI):** [/core/README.md](../core/README.md)
- **Wizard (Server):** [/wizard/README.md](../wizard/README.md)
- **Groovebox (Music):** [/groovebox/README.md](../groovebox/README.md)
- **App (UI):** [/app/docs/README.md](../app/docs/README.md) (if exists)

---

## ❓ Documentation Standards

All docs should be:
- **Current** — Dated & version-noted
- **Navigable** — Links between related docs
- **Scannable** — Clear headers & bullets
- **Beginner-friendly** — Explain jargon
- **Focused** — One main topic

---

## 🔗 Navigation

- **Home:** [/README.md](../README.md)
- **Wiki:** [/wiki/README.md](../wiki/README.md)
- **Quick Start:** [/QUICKSTART.md](../QUICKSTART.md)
- **Contributing:** [/wiki/CONTRIBUTING.md](../wiki/CONTRIBUTING.md)
- **Archive:** [.archive/README.md](.archive/README.md)

---

**Status:** Active Developer Reference
**Version:** v1.0.7
**Updated:** February 2, 2026
**Maintained by:** uDOS Engineering
