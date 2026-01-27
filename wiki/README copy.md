# uDOS Architecture Standards (v1.0.7.0)

**Last Updated:** 2026-01-24
**Status:** Active Standard
**Scope:** Public reference for system architecture

This directory contains the canonical architecture specifications for uDOS, describing how the system layers, databases, knowledge base, and executable documents work together.

---

## Architecture Documents

### Core Systems

- **[Layer Architecture](LAYER-ARCHITECTURE.md)** (v1.0.0.57) — Fractal grid system, realm layers, coordinate precision
- **[Filesystem Architecture](FILESYSTEM-ARCHITECTURE.md)** (v1.0.0.52) — System vs user data, directory structure, distribution model
- **[Database Architecture](DATABASE-ARCHITECTURE.md)** (v1.0.1.0) — SQLite ecosystem, schema design, cross-linking

### Knowledge & Documents

- **[Knowledge Linking System](KNOWLEDGE-LINKING-SYSTEM.md)** (v1.0.0.53) — Self-indexing documents, frontmatter schema, document lifecycle
- **[uDOS.md Format](UDOS-MD-FORMAT.md)** (v1.0.0.52) — Executable document format, structure, parsing
- **[uDOS.md Template Spec](UDOS-MD-TEMPLATE-SPEC.md)** (v1.0.0.51) — Template system, shortcodes, variable interpolation

---

## Quick Reference

| Document           | Version   | Focus                                           |
| ------------------ | --------- | ----------------------------------------------- |
| Layer Architecture | v1.0.0.57 | Spatial grid, layers 000-799, coordinate system |
| Filesystem         | v1.0.0.52 | Directory layout, data classification           |
| Database           | v1.0.1.0  | Schema, indexing, cross-domain links            |
| Knowledge Linking  | v1.0.0.53 | Frontmatter, document lifecycle, self-indexing  |
| uDOS.md Format     | v1.0.0.52 | Single-file executable documents                |
| Templates          | v1.0.0.51 | Shortcodes, templates, interpolation            |

---

## Design Principles

1. **Offline-First** — All core systems work without internet
2. **Self-Describing** — Documents declare their own relationships via frontmatter
3. **Fractal** — Same patterns repeat at different scales (layers, categories, zoom levels)
4. **Distributed** — System data separate from user data
5. **Versioned** — All components independently versioned

---

## See Also

- [../../AGENTS.md](../../AGENTS.md) — How work is done
- [../../docs/\_index.md](../../docs/_index.md) — Engineering spine
- [../../docs/development-streams.md](../../docs/development-streams.md) — Current priorities
- [../ARCHITECTURE.md](../ARCHITECTURE.md) — Wiki overview

---

**Maintained by:** uDOS Engineering
**License:** See LICENSE.txt
**Repository:** https://github.com/fredporter/uDOS
