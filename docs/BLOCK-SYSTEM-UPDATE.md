# Block System Update — Obsidian-Aligned v1.3

**Date:** 2026-02-05  
**Changes:** Removed cloud sync dependencies, aligned block system with Obsidian + uDOS runtime

---

## What Changed

### ✅ Kept: Block Concept
The idea of structured content blocks is valuable and remains in uDOS. However, we've pivoted from:
- ❌ **Proprietary cloud blocks** (vendor-locked, API-synced, JSON format)
- ✅ **uDOS blocks** (Markdown, Obsidian-compatible, runtime-enabled)

### 🗑️ Removed: Legacy Sync Infrastructure
- Legacy cloud API integration code
- Webhook handlers for external sync events
- Block mapper for proprietary JSON formats
- Legacy dashboard sync components

### 🎯 New Focus: Obsidian + uDOS Features

**Obsidian Features (v1.3 Priority):**
1. **Tagging** — `#tag` syntax, nested tags, tag search
2. **Frontmatter** — YAML metadata, properties panel
3. **Searchable** — Full-text + grep + regex
4. **Linkable** — `[[wiki-links]]`, backlinks, graph view
5. **Offline** — No cloud, no sync, just files
6. **Wiki** — Daily notes, templates, aliases

**uDOS Features (v1.3 Additions):**
1. **Runtime Blocks** — Executable code blocks (state, form, if, nav, panel, map)
2. **Grid Layouts** — 80×30 TUI grids, scalable for GUI
3. **Column Formats** — Multi-column Markdown layouts
4. **Spatial Index** — Location-based navigation
5. **Automation** — Script execution from Markdown
6. **State Management** — Stateful wiki pages

---

## Block System v1.3

### Standard Blocks (Obsidian-compatible)
All standard Markdown works in both:
- Headings (`#`, `##`, `###`)
- Lists (bullet, numbered, task)
- Links (`[[wiki]]`, `[md](link)`)
- Embeds (`![[file]]`)
- Code blocks with syntax highlighting
- Tables, blockquotes, dividers

### Runtime Blocks (uDOS-specific)
Execute in uDOS, display as code in Obsidian:
```state, set, form, if, nav, panel, map```

### Grid Layouts (uDOS-specific)
Native grid system for dashboards, calendars, tables, maps:
- `core/src/grid/` — Grid engine
- `core/src/grid/layouts/` — Layout renderers
- Modes: dashboard, calendar, schedule, table, map

---

## Implementation

### Core System (TypeScript)
- ✅ Grid canvas (`core/src/grid/`)
- ✅ Runtime blocks (`core/src/executors/`)
- ✅ Spatial indexing (`core/src/spatial/`)
- ✅ Frontmatter parsing
- ✅ Tag indexing

### Documentation
- ✅ [docs/BLOCK-SYSTEM-V1.3.md](BLOCK-SYSTEM-V1.3.md) — Full spec
- ✅ [docs/OBSIDIAN-INTEGRATION.md](OBSIDIAN-INTEGRATION.md) — Integration guide
- ✅ Technical refs in `core/src/grid/` and `docs/specs/`

---

## Migration Path

### From Legacy Cloud Blocks → uDOS Blocks

1. **Export to Markdown** from your previous system
2. **Convert block types:**
   - Task → Markdown `- [ ] task`
   - Heading → Markdown `# Heading`
   - Code → Markdown ` ```lang` `
   - Bullets → Markdown `- item`
3. **Add frontmatter:**
   ```yaml
   ---
   title: "From Legacy Export"
   tags: [migrated]
   source: legacy
   ---
   ```
4. **Open in Obsidian** — Works immediately
5. **Add runtime blocks in uDOS** — As needed for automation

---

## Architecture Benefits

### Before (Cloud Sync)
- Required cloud API connection
- Proprietary block format
- Sync conflicts
- Vendor lock-in
- Online-only features

### After (Obsidian-Aligned)
- Local files only
- Standard Markdown
- No sync needed
- Open format
- Fully offline

---

## What's Still Called "Block"

1. **Runtime Blocks** — uDOS execution units (state, form, etc.)
2. **Grid Blocks** — Layout components (panels, widgets)
3. **Markdown Blocks** — Standard content sections (headings, paragraphs, lists)

All are Markdown-based, Obsidian-readable, and locally stored.

---

## Dashboard Updates

### Removed Components
- Legacy sync UI and webhook components archived

### Kept Components
- `mappingStore.ts` — Updated with legacy comments (handles imported data)
- Other Wizard UI components remain

---

## Next Steps

1. **Enhanced Grid Layouts** — More layout modes, visual editor
2. **Column Format Renderer** — Multi-column Markdown
3. **Obsidian Plugin** — Bidirectional integration
4. **Block Templates** — Library of common runtime blocks
5. **Performance** — Optimize large vault indexing

---

## Key Takeaway

> **uDOS blocks ≠ Notion blocks**
>
> uDOS blocks are Obsidian-compatible Markdown with optional runtime execution.  
> No sync. No API. Just files.

This is the v1.3 block philosophy.

---

_Updated: 2026-02-05_  
_See: [BLOCK-SYSTEM-V1.3.md](BLOCK-SYSTEM-V1.3.md) for full specification_
