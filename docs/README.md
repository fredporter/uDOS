# uDOS Documentation Index

**Last Updated:** 2026-01-30  
**Version:** v1.0.7.1 (Spatial Filesystem + Wiki Standardization)

---

## 📚 Documentation Structure

### Primary References

| Document                                                      | Purpose                                                    |
| ------------------------------------------------------------- | ---------------------------------------------------------- |
| [AGENTS.md](../AGENTS.md)                                     | How work is done in uDOS (architecture, policies, tooling) |
| [uCODE.md](uCODE.md)                                          | **NEW**: Unified Terminal TUI (main entry point)           |
| [ROADMAP.md](ROADMAP.md)                                      | Development streams (formerly development-streams.md)     |
| [Spatial Filesystem](specs/SPATIAL-FILESYSTEM.md)            | Grid-integrated filesystem with RBAC & tagging            |
| [Wiki Frontmatter Standard](WIKI-FRONTMATTER-GUIDE.md)       | **NEW**: Obsidian-compatible YAML frontmatter reference   |
| [Frontmatter Standardization Summary](FRONTMATTER-STANDARDIZATION-SUMMARY.md) | **COMPLETE**: All 247 docs standardized (wiki, knowledge, candidates) |
| [Release Readiness Checklist](RELEASE-READINESS-CHECKLIST.md) | v1.1.0 release gates & timeline                           |
| [README.md](README.md)                                        | This file                                                  |

---

## 🚀 Getting Started

### Quick Start with uCODE

```bash
python uDOS.py          # Launch unified TUI
```

Then:

```
STATUS                  # Check what's installed
WIZARD start            # Start Wizard server (if available)
PLUGIN list             # List extensions (if available)
WORKSPACE INFO          # Show spatial filesystem & access levels
HELP                    # Show all commands
```

See [uCODE.md](uCODE.md) and [uCODE-QUICK-REFERENCE.md](uCODE-QUICK-REFERENCE.md).

---

## 🗂️ Spatial Filesystem (v1.0.7.1)

**Feature:** Grid-integrated filesystem with role-based access, location tagging, and content discovery.

### Quick Links

- [SPATIAL-FILESYSTEM.md](specs/SPATIAL-FILESYSTEM.md) — Full architecture & API
- [SPATIAL-FILESYSTEM-QUICK-REF.md](SPATIAL-FILESYSTEM-QUICK-REF.md) — Commands & examples
- `core/services/spatial_filesystem.py` — Implementation
- `core/commands/spatial_filesystem_handler.py` — TUI handler

### Key Commands

```
WORKSPACE list @sandbox              # List files in workspace
LOCATION tag @sandbox/story.md L300-AB15   # Tag file with grid location
TAG find forest adventure            # Find files by tags
BINDER open @sandbox/my-project      # Open multi-chapter project
```

### Workspaces

| Workspace  | Path            | Access |
|------------|-----------------|--------|
| @sandbox   | memory/sandbox  | User   |
| @bank      | memory/bank     | User   |
| @shared    | memory/shared   | User   |
| @wizard    | memory/wizard   | Admin  |
| @knowledge | /knowledge      | Admin  |
| @dev       | /dev            | Admin  |

---

## 📖 Wiki Standardization (Obsidian-Compatible)

**Feature:** All documentation uses standardized YAML frontmatter for stable identifiers, categorization, and discovery.

### Quick Links

- [wiki_spec_obsidian.md](specs/wiki_spec_obsidian.md) — Full specification
- [WIKI-FRONTMATTER-GUIDE.md](WIKI-FRONTMATTER-GUIDE.md) — Migration guide & UID generation
- [docs/wiki/](wiki/) — Core architecture docs (ALPINE-CORE, BEACON-*, WIZARD-*)
- [knowledge/](../knowledge/) — Knowledge bank (survival guides, skills)

### Frontmatter Fields

```yaml
---
uid: udos-wiki-20260130120000-L300AB00       # Stable, immutable identifier
title: Document Title                         # Human-readable title (may change)
tags: [wiki, category, subcategory]          # Categorization & discovery
status: living                                 # living | draft | frozen | deprecated
updated: 2026-01-30                          # Last semantic update
---
```

### Standard Tags

- `wiki` — All wiki documents
- `spec` — Specifications
- `guide` — How-to guides
- `knowledge` — Knowledge bank
- `architecture` — System design
- `networking` — Network protocols
- Hierarchical: `knowledge/fire/safety`, `spec/architecture/etc.`

---

## 🔍 System Validation & Reset

### SHAKEDOWN & DESTROY Commands

- [SHAKEDOWN-DESTROY-UPDATES.md](SHAKEDOWN-DESTROY-UPDATES.md) — Full documentation of v1.1.0 updates
- [SHAKEDOWN-DESTROY-QUICK-REFERENCE.md](SHAKEDOWN-DESTROY-QUICK-REFERENCE.md) — Command reference guide
- [test_shakedown_destroy_v1_1_0.py](../core/tests/test_shakedown_destroy_v1_1_0.py) — Comprehensive test suite

**Quick Commands:**
```bash
SHAKEDOWN                    # Validate system
SHAKEDOWN --fresh            # Validate fresh install
SHAKEDOWN --destroy-verify   # Verify DESTROY is ready
DESTROY                      # Show cleanup options
DESTROY --help               # Show help
DESTROY --wipe-user          # Clear user data
DESTROY --compost            # Archive memory
DESTROY --reset-all --confirm # Factory reset
```

---

## 📋 Specifications (`/docs/specs/`)

### Wiki & Documentation

- [wiki_spec_obsidian.md](specs/wiki_spec_obsidian.md) — Obsidian-compatible Markdown with YAML frontmatter
- [SPATIAL-FILESYSTEM.md](specs/SPATIAL-FILESYSTEM.md) — Grid-integrated filesystem architecture

### Core Runtime

- [TypeScript Markdown Runtime](specs/typescript-markdown-runtime.md) — State, blocks, execution model
- [Grid & Spatial Computing](specs/grid-spatial-computing.md) — Fractal addressing, layers, viewports, tiles
- [File Parsing Architecture](specs/file-parsing-architecture.md) — CSV, JSON, YAML, SQL, Markdown tables
- [Core Runtime Status](specs/core-runtime-status.md) — Command set, runtime state, gaps

### Wizard Server

- [Workflow Management](specs/workflow-management.md) — Projects, organic cron, provider rotation, binders

### App

- [Mac App Roadmap](specs/mac-app-roadmap.md) — Typo editor, converters, uCode, Marp, forms
- [App File Extensions](specs/app-file-extensions.md) — File types, syntax highlighting, predictive coding

---

## 📝 Examples (`/docs/examples/`)

### Runtime Examples

- [Complete Example Script](examples/example-script.md) — All TS Markdown features demonstrated
- [SQLite Database Examples](examples/example-sqlite-db.md) — Schema, seeds, edges for runtime
- [Grid Runtime Examples](examples/grid-runtime-examples.md) — Teletext, sprites, viewports, animation

---

## 🗓️ Development Logs (`/docs/devlog/`)

Chronological development notes organized by month (YYYY-MM.md format).

**Recent:**

- 2026-01-22: Dev Mode Migration
- 2026-01-22: Goblin-Wizard Migration
- 2026-01-22: Wizard Dashboard Integration

---

## 🎯 Engineering Spine

### Core Documents (Root)

1. [AGENTS.md](../AGENTS.md) — Primary operational reference
2. [INSTALLATION.md](../INSTALLATION.md) — Setup instructions
3. [QUICKSTART.md](../QUICKSTART.md) — Getting started guide

### Architecture & Decisions

- [Development Streams](development-streams.md) — Feature planning
- Private submodule decisions in `/dev/docs/`

### Wizard↔Core Integration

- Alpine-style packaging: plugins and tools are distributed via Wizard-managed `apk` or plugin bundles.
- Distribution: Wizard handles packaging, publishing, and quota-aware updates; Core remains offline-first.
- Plugin registry: Wizard exposes an extensions repository; Core installs/activates via handlers.
- Local library management: public definitions in `/library/`, promoted from `/dev/library/` after validation.
- Versioning: all components use `python -m core.version`; never hardcode versions.

### Component-Specific Docs

- **Core:** `/core/docs/` — TUI, handlers, services
- **Wizard:** `/wizard/docs/` — Server architecture, APIs
- **Goblin:** `/dev/goblin/docs/` — Experimental features
- **App:** `/app/docs/` — Tauri app, UI components (public scaffold)

---

## 🔍 Quick Reference

### For Users

- [QUICKSTART.md](../QUICKSTART.md) — Get started with uDOS
- [INSTALLATION.md](../INSTALLATION.md) — Install and configure

### For Developers

- [AGENTS.md](../AGENTS.md) — Development philosophy and boundaries
- [Development Streams](development-streams.md) — What's being built
- [Specifications](specs/) — Technical details
- [Examples](examples/) — Reference implementations

### For Contributors

- Component instructions:
  - [Core Instructions](../.github/instructions/core.instructions.md)
  - [Wizard Instructions](../.github/instructions/wizard.instructions.md)
  - [App Instructions](../.github/instructions/app.instructions.md)
  - [Extensions Instructions](../.github/instructions/extensions.instructions.md)

---

## 📊 Version Information

| Component | Version  | Status       |
| --------- | -------- | ------------ |
| Core      | v1.1.1.1 | Dev          |
| API       | v1.0.1.0 | Alpha        |
| Wizard    | v1.1.0.2 | Alpha        |
| Goblin    | v0.2.0.0 | Experimental |
| App       | v1.0.6.1 | Alpha        |
| TUI       | v1.0.0.0 | Stable       |

---

## 🗂️ Archive Policy

- **Active docs** — Live in `/docs/`
- **Component docs** — Live in component folders
- **Drafts** — Live in `.dev/` (gitignored)
- **Archive** — Moved to `.archive/YYYY-MM-DD/` or component `.archive/`

**Promotion timeline:** Useful drafts are promoted to `/docs/` after ~2 weeks of validation.

---

## 🚀 Next Steps

1. Review [Development Streams](development-streams.md) for roadmap
2. Check [Specifications](specs/) for technical details
3. Explore [Examples](examples/) for implementation patterns
4. Read [AGENTS.md](../AGENTS.md) for development guidelines

---

**Status:** Active Index  
**Maintained by:** uDOS Engineering  
**Next Review:** 2026-02-01
