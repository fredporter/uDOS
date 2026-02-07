# uDOS Block System — Obsidian-Aligned Architecture

**Version:** v1.3  
**Updated:** 2026-02-05  
**Status:** Active (local-first blocks)

---

## Philosophy

uDOS blocks are **Obsidian-compatible Markdown** with runtime execution capabilities. Unlike proprietary cloud blocks (which require API sync), uDOS blocks are:

- ✅ **Local-first** — Pure Markdown files
- ✅ **Obsidian-readable** — Standard frontmatter + code blocks
- ✅ **Executable** — Runtime blocks for automation
- ✅ **Searchable** — Full-text search, tags, links
- ✅ **Portable** — No vendor lock-in

---

## Block Types

### Standard Markdown Blocks (Obsidian-compatible)

These work in both Obsidian and uDOS:

```markdown
# Heading 1
## Heading 2
### Heading 3

**bold** *italic* `code`

> Blockquote

- Bullet list
- Item 2

1. Numbered list
2. Item 2

---

[[wiki-link]]
[markdown link](path.md)

![[embed.png]]

#tag #another-tag

```python
code block
```
```

### Runtime Blocks (uDOS-specific)

Execute in uDOS, render as code blocks in Obsidian:

````markdown
```state
{
  "counter": 0,
  "active": true
}
```

```set
variable_name = "value"
```

```form
name: text
message: message
submit: "Send"
```

```if
condition: user.logged_in
show: dashboard.md
else: login.md
```

```nav
- Home: index.md
- About: about.md
```

```panel
title: "Stats"
data: metrics.json
```

```map
location: EARTH:SUR:L305-DA11
zoom: 12
```
````

**Obsidian view:** Code blocks with syntax highlighting  
**uDOS view:** Executed runtime components

---

## Grid Layouts

uDOS has a native grid system (80×30 TUI, scalable for GUI):

### Grid Canvas Modes
- **dashboard** — Widget panels
- **calendar** — Time-based views
- **schedule** — Task timelines
- **table** — Tabular data
- **map** — Spatial navigation

### Grid Types (core/src/grid/)
```typescript
interface GridCanvasSpec {
  width: number    // Default: 80
  height: number   // Default: 30
  columns: number  // Layout columns
  title?: string
  mode?: GridMode
}
```

---

## Column Formats

### Multi-column Markdown

Using Obsidian's CSS snippets + uDOS runtime:

```markdown
---
layout: columns
columns: 2
---

::column-1::
# Left Column
Content here

::column-2::
# Right Column
More content
```

### uDOS Grid Layout

```markdown
---
grid:
  mode: dashboard
  columns: 3
  panels:
    - type: stats
      col: 1
    - type: calendar
      col: 2
    - type: tasks
      col: 3
---
```

---

## Frontmatter (YAML)

Obsidian-compatible frontmatter with uDOS extensions:

```yaml
---
# Standard Obsidian
title: "My Note"
tags: [project, urgent]
aliases: [alt-name]
created: 2026-02-05
modified: 2026-02-05

# uDOS Runtime
runtime: true
executor: python
state:
  counter: 0
  status: active

# uDOS Spatial
places: ["EARTH:SUR:L305-DA11"]
grid_locations: ["DA11"]

# uDOS Grid
grid:
  mode: dashboard
  columns: 2
---
```

**Obsidian:** Renders standard fields, ignores uDOS-specific  
**uDOS:** Processes all fields including runtime directives

---

## Tagging Strategy

### Obsidian Tags
```markdown
#project/active
#type/script
#priority/high
#status/draft
```

**Features:**
- Searchable in Obsidian tag pane
- Nested tags (`project/active`)
- Click to navigate
- Tag graph visualization

### uDOS Tags
```markdown
---
tags:
  - runtime
  - executable
  - automation
runtime_tags:
  - scheduled
  - background
---
```

**Features:**
- Parsed by uDOS runtime
- Filter in CLI: `LIST --tags runtime`
- Trigger automation workflows
- Index for fast lookup

---

## Linking & References

### Wiki Links (Both)
```markdown
[[Other Note]]
[[folder/note|Display Text]]
[[note#heading]]
```

Works in Obsidian graph view AND uDOS navigation.

### Obsidian Links
```markdown
![[embed-note.md]]
![[image.png|200]]
![[audio.mp3]]
```

**Obsidian:** Renders embedded content  
**uDOS:** Includes in execution context

### uDOS Links
```markdown
[script:run-backup](scripts/backup.script.md)
[location:DA11](EARTH:SUR:L305-DA11)
[runtime:state](state.json)
```

Custom protocols for uDOS actions.

---

## Search Features

### Obsidian Search
- Full-text search (Cmd+Shift+F)
- Regex support
- Search in properties
- File/folder filters
- Tag search

### uDOS Search
```bash
# CLI
SEARCH "query" --tags automation
SEARCH "^# Heading" --regex
GREP pattern --files *.script.md

# Runtime API
search(query, filters)
find_tagged(tags)
locate(spatial_ref)
```

---

## Wiki Features

### Obsidian Wiki Features
- **Backlinks** — See what links to current note
- **Graph View** — Visualize connections
- **Outlinks** — Links from current note
- **Unlinked Mentions** — Find potential connections
- **Daily Notes** — Template-based
- **Templates** — Insert reusable content

### uDOS Wiki Features
- **Spatial Index** — Location-based navigation
- **Runtime Execution** — Scripts as wiki pages
- **State Management** — Stateful wiki pages
- **Automation** — Scheduled wiki updates
- **Version Control** — Git-based history
- **Offline-First** — No internet required

---

## Block Structure Comparison

| Feature | Legacy Cloud Blocks | uDOS Blocks |
|---------|--------------|-------------|
| Format | Proprietary JSON | Markdown + YAML |
| Storage | Cloud database | Local files |
| Editing | Web/app only | Any text editor |
| Sync | Required | Not needed |
| Offline | Limited | Full |
| Search | Database query | Full-text + grep |
| Version Control | Limited | Git-native |
| Linking | Internal only | Files + URLs + protocols |
| Execution | No | Yes (runtime blocks) |
| Obsidian Compatible | No | Yes |

---

## Migration from Legacy Cloud Blocks

If you have old cloud block data:

1. **Export to Markdown** from your previous system
2. **Convert block types:**
  - Task → `- [ ] task`
  - Heading → `# Heading`
  - Paragraph → Plain text
  - Code → ` ```lang\ncode\n``` `
  - Bullet → `- item`
3. **Add frontmatter:**
  ```yaml
  ---
  title: "From Legacy Export"
  source: legacy
  migrated: 2026-02-05
  ---
  ```
4. **Open in Obsidian** — Works immediately
5. **Execute in uDOS** — Add runtime blocks as needed

---

## Best Practices

### For Obsidian Compatibility
- Use standard Markdown syntax
- Keep frontmatter YAML valid
- Use `[[wiki-links]]` for internal refs
- Tag consistently
- Template daily notes

### For uDOS Features
- Add `runtime: true` to executable notes
- Use runtime blocks for automation
- Leverage spatial indexing
- Version control with Git
- Keep scripts in `/scripts/`

### For Both
- Use clear naming conventions
- Organize with folders + tags
- Link liberally
- Keep files under 1MB
- UTF-8 encoding always

---

## Implementation Status

### ✅ Implemented (v1.3)
- Grid canvas system
- Runtime blocks (state, set, form, if, nav, panel, map)
- Frontmatter parsing
- Spatial indexing
- Markdown → HTML rendering
- Tag indexing

### 🚧 In Progress
- Column layout renderer
- Advanced grid layouts
- Obsidian plugin integration
- Live reload

### 📋 Planned
- Visual grid editor
- Block templates library
- Enhanced linking protocols
- Performance optimizations

---

## Technical Reference

### Core Grid System
- `core/src/grid/` — Grid layout engine
- `core/src/grid/types.ts` — Type definitions
- `core/src/grid/layouts/` — Layout renderers
- `core/src/spatial/grid_canvas.ts` — Canvas interface

### Runtime Blocks
- `core/src/executors/` — Block executors
- `core/src/types.ts` — RuntimeBlock types

### Documentation
- `docs/specs/07-grid-canvas-rendering.md`
- `docs/RUNTIME-INTERFACE-SPEC.md`

---

## Summary

**uDOS blocks = Obsidian-compatible Markdown + Runtime execution**

- Read/write in Obsidian
- Execute in uDOS
- Version with Git
- No sync needed
- Fully offline
- Open format

**This is the v1.3 block system.**

---

_Last updated: 2026-02-05_
