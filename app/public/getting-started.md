---
title: Getting Started with Markdown
type: guide
tags: [welcome, tutorial, getting-started]
status: published
created: 2026-01-15
modified: 2026-01-15
---

# Welcome to Markdown

**Markdown** is your local-first macOS markdown editor with Notion-style organization, powerful formatting, and optional sync capabilities.

## Core Features

### 🎨 Three Independent Font Controls

- **Heading Font** — for h1-h6 elements
- **Body Font** — for paragraphs and lists
- **Code Font** — for code blocks and inline code

Access font preferences via **⌘,** or menu: **Markdown → Settings...**

### 📝 Typo-First Editing

Clean, distraction-free markdown editing with live preview. Toggle between edit and view modes with the bottom toolbar button.

### 📊 Tables Mode (Coming Soon)

Your data control plane for:

- Import/export (JSON, CSV, XLSX, MD tables)
- Data formatting and cleanup
- Notion sync management
- Database views and queries

### 🗂️ Notion-Style Organization

Organize documents with:

- **Binders** — virtual grouping
- **Folders** — filesystem roots
- **Databases** — structured data (tasks, projects)
- **Views** — saved database perspectives

## Document Formats

Markdown supports multiple frontmatter-based formats:

### 📄 Guide Format (`-guide.md`)

Standard knowledge articles (like this one):

```yaml
---
title: My Guide
type: guide
tags: [topic1, topic2]
---
```

### 💻 uCode Format (`-ucode.md`)

Executable documents with runtime blocks:

```yaml
---
title: My Workflow
type: ucode
runtime: true
---
```

uCode blocks can:

- Access other docs and maps
- Execute uPY code (restricted Python subset)
- Integrate with uDOS Core

### 📖 Story Format (`-story.md`)

Interactive presentations (typeform-style):

```yaml
---
title: User Onboarding
type: story
sandbox: true
---
```

Story blocks are:

- Self-contained and distributable
- Sandboxed for safety
- Perfect for forms and surveys

### 🎬 Marp Format (`-marp.md`)

Full-viewport presentations:

```yaml
---
marp: true
theme: default
---
```

### ⚙️ Config Format (`-config.md`)

System configuration:

```yaml
---
type: config
scope: workspace
---
```

## Keyboard Shortcuts

| Shortcut | Action                |
| -------- | --------------------- |
| ⌘O       | Open file             |
| ⌘⇧S      | Save As               |
| ⌘S       | Save (when file open) |
| ⌘B       | Toggle sidebar        |
| ⌘,       | Settings              |
| ⌘+       | Zoom in               |
| ⌘-       | Zoom out              |
| ⌘F       | Fullscreen            |

## Tasks & Scheduling

Tasks are stored as database rows with:

- Title, status, priority
- Due dates and recurrence
- Assignee and tags
- Linked items (projects, notes)

Task execution targets:

- **local** — Mac app
- **udos** — Core TUI runtime
- **wizard** — Always-on server
- **mesh** — P2P network

## Notion Sync (Coming Soon)

### Sync Modes

**Publish Mode** (default)

- Local SQLite is source of truth
- Push changes to Notion on demand
- Deterministic and safe

**Limited Live** (future)

- Allow text updates within blocks
- Disable arbitrary reordering
- Fallback to rebuild on conflicts

### Conflict Resolution

When conflicts detected:

1. **Keep Local** — overwrite remote
2. **Keep Remote** — pull changes
3. **Duplicate** — create local copy

### What Syncs

- ✅ Pages and properties
- ✅ Database rows
- ✅ Task status updates
- ✅ Managed block regions

### What Doesn't Sync

- ❌ Arbitrary filesystem folders
- ❌ Local-only databases
- ❌ Job execution history
- ❌ System configuration

## Getting Help

### Documentation

- [Architecture Overview](../docs/_index.md)
- [Roadmap](../docs/roadmap.md)
- [Notion Specs](../dev/roadmap/notion-specs.md)

### Quick Tips

1. **Start Simple** — Use this as a plain markdown editor first
2. **Organize Later** — Add binders and databases as you need them
3. **Stay Local** — All features work offline by default
4. **Sync Optionally** — Enable Notion sync only when ready

---

**Next Steps:**

1. Open a new file (⌘O) or start typing
2. Explore font preferences (⌘,)
3. Try different document formats
4. Check out the Notion view for organization

Happy writing! 📝
