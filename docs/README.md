# uDOS Documentation Index

**Last Updated:** 2026-01-24  
**Version:** v1.0.7

---

## 📚 Documentation Structure

### Primary References

| Document                                      | Purpose                                                    |
| --------------------------------------------- | ---------------------------------------------------------- |
| [AGENTS.md](../AGENTS.md)                     | How work is done in uDOS (architecture, policies, tooling) |
| [Development Streams](development-streams.md) | Active development planning across all components          |
| [README.md](README.md)                        | This file                                                  |

---

## 📋 Specifications (`/docs/specs/`)

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
