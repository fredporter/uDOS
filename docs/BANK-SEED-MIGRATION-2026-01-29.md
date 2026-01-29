# Framework Seed Data Migration Summary

**Date:** 2026-01-29  
**Action:** Migrate rich seed data from `.archive` → `core/framework/seed/bank/`

---

## ✅ Completed Migrations

### 1. Graphics Seed Data (464KB)

**Source:** `core/.archive/data/themes/`, `core/.archive/data/diagrams/`  
**Destination:** `core/framework/seed/bank/graphics/`

**Contents:**
- **Themes** (4 files)
  - `_schema.json` — Theme variable definitions (4.4KB)
  - `_index.json` — Theme catalog (310B)
  - `default.json` — Base theme (1.2KB)
  - `templates/` — Custom theme templates

- **Diagrams** (catalog + templates)
  - `catalog.json` — Full diagram registry (5.6KB)
  - `README.md` — Documentation (5.9KB)
  - `ascii/` — 25 ASCII art templates
  - `teletext/` — 4 teletext palettes (classic, earth, terminal, amber)
  - `svg/` — 3 SVG styles (technical, simple, detailed)
  - `sequence/` — 5 sequence diagram templates
  - `flow/` — 5 flowchart templates
  - `blocks/`, `plain/`, `templates/` — Supporting assets
