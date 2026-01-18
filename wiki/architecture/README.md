# uDOS Architecture Documentation

System architecture specifications and design documents.

## Contents

| Document | Description |
|----------|-------------|
| [DATABASE-ARCHITECTURE.md](DATABASE-ARCHITECTURE.md) | SQLite database ecosystem (5 databases) |
| [FILESYSTEM-ARCHITECTURE.md](FILESYSTEM-ARCHITECTURE.md) | Directory structure and paths |
| [LAYER-ARCHITECTURE.md](LAYER-ARCHITECTURE.md) | Map layers and coordinate system |
| [KNOWLEDGE-LINKING-SYSTEM.md](KNOWLEDGE-LINKING-SYSTEM.md) | Knowledge-geography TILE linking |
| [UDOS-MD-TEMPLATE-SPEC.md](UDOS-MD-TEMPLATE-SPEC.md) | .udos.md template format |
| [UDOS-MD-FORMAT.md](UDOS-MD-FORMAT.md) | Markdown formatting conventions |

## Quick Reference

### Database Locations

| Database | Path | Purpose |
|----------|------|---------|
| `knowledge.db` | `memory/bank/` | Knowledge index |
| `core.db` | `memory/bank/` | Scripts library |
| `contacts.db` | `memory/bank/user/` | BizIntel contacts |
| `devices.db` | `memory/bank/wizard/` | Device registry |
| `scripts.db` | `memory/bank/wizard/` | Wizard scripts |

### Layer System

| Layer Range | Name | Content |
|-------------|------|---------|
| 0-99 | Planet Core | Geology, internals |
| 100-199 | Surface | Geography, roads, buildings |
| 200-399 | Bio Layer | Plants, animals, weather |
| 400-599 | Human | Communities, culture |
| 600-699 | Tech | Networks, devices |
| 700-799 | Future | Planning, projections |
| 800-899 | Celestial | Space, stars, orbits |

---

Part of uDOS v1.0.1.0 documentation
