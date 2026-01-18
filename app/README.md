# uMarkdown Mac App

**Native macOS Markdown Editor & Organiser**

Version: **v1.0.0.0** (Alpha)  
Platform: **macOS** (future: iOS/iPadOS)  
Framework: **Tauri + Svelte + Tailwind**

---

## Overview

uMarkdown is a clean, native macOS markdown editor with Notion-style organisation. This is the production-ready native macOS implementation.

### Core Features

- **Typo-first authoring** — Clean markdown editing with live preview
- **Notion-style binder** — Organize documents in a tree-like hierarchy (folders, collections, databases, views)
- **Tasks & scheduling** — Built-in task management with local SQLite storage
- **Tables mode** — Import/export data, manage Notion mappings, audit sync operations
- **Notion integration** — Optional publish-mode sync (local → Notion)

### Architecture

- **Frontend:** Svelte + Tailwind CSS (type-safe, responsive)
- **Backend:** Rust (Tauri)
- **Storage:** SQLite (local-first, portable)
- **Platform:** macOS native (future mobile support)

---

## Development

### Prerequisites

- Node.js >= 18.0
- Rust toolchain (for Tauri)
- macOS 10.13+

### Setup

```bash
cd app
npm install
```

### Run Dev

```bash
npm run tauri:dev
```

This launches:

- Vite dev server on port 1420
- Tauri app window

### Build

```bash
npm run tauri:build
```

Produces `app/src-tauri/target/release/umarkdown.app`

---

## Project Structure

```
app/
├── src/
│   ├── App.svelte              # Root component
│   ├── main.ts                 # Entry point
│   └── components/
│       ├── BinderNav.svelte    # Sidebar tree navigation
│       ├── MarkdownEditor.svelte
│       └── Preview.svelte       # Live preview
├── src-tauri/                  # Rust/Tauri backend
│   ├── src/main.rs
│   └── tauri.conf.json
├── tailwind.config.js
├── postcss.config.js
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## UI Components

### BinderNav

Tree-based navigation for organizing:

- Documents (files)
- Collections (virtual folders)
- Databases (tasks, content)
- Views (saved searches/filters)

### MarkdownEditor

Full-featured markdown editor with:

- Syntax highlighting
- Toolbar for formatting (B, I, code, links)
- Live updates

### Preview

Renders markdown to styled HTML with support for:

- Headings, lists, tables
- Code blocks with syntax highlighting
- Embeds (images, videos, external content)

---

## Configuration

### Theme

Set via Tailwind config in `tailwind.config.js`:

- Colors: uDOS brand purple, grays
- Typography: Inter (sans), JetBrains Mono (mono)
- Spacing: Safe area insets for macOS notch

### Tauri Config

`src-tauri/tauri.conf.json`:

- Window size, position, decorations
- Permissions (file system, clipboard, etc.)
- Security settings

---

## Roadmap

### v1.0.0.0 (Current)

- [x] Tauri scaffold + Svelte setup
- [x] Binder tree UI
- [x] Markdown editor + preview
- [x] Tailwind styling

### v1.0.1.0 (Phase 2)

- [ ] File system integration (open/save)
- [ ] Local SQLite database setup
- [ ] Task database UI
- [ ] Tables mode (import/export)

### v1.0.2.0 (Phase 3)

- [ ] Notion integration (webhook receiver)
- [ ] TS runtime execution (blocks)
- [ ] Task scheduling (organic cron)
- [ ] Binder compilation (outputs)

### v1.1.0.0 (Phase 4)

- [ ] iOS/iPadOS support
- [ ] Cloud sync (encrypted)
- [ ] Advanced Notion features
- [ ] Extensions API

---

## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/)
- [Svelte extension](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode)
- [Tauri extension](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode)
- [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)

---

## Commands

```bash
# Development
npm run dev           # Vite dev server only
npm run tauri:dev    # Full Tauri dev mode

# Production
npm run build        # Build frontend + Rust
npm run tauri:build  # Full production build

# Testing
npm test            # Run tests (when added)

# Tauri-specific
npm run tauri       # Run Tauri CLI directly
```

---

## References

- [Tauri Documentation](https://tauri.app/develop/)
- [Svelte Documentation](https://svelte.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**Status:** Alpha v1.0.0.0  
**Last Updated:** 2026-01-15

- [ ] Native macOS UI

### v1.1.0.0 (Next)

- [ ] uCode format support
- [ ] Story format support
- [ ] Marp format support
- [ ] Full format architecture

### v2.0.0.0 (Future)

- [ ] iOS/iPadOS support
- [ ] iCloud sync
- [ ] Handoff support

---

## Relationship to Other Apps

| App                      | Purpose                     | Status   |
| ------------------------ | --------------------------- | -------- |
| **uMarkdown** (this)     | Native macOS production app | v1.0.0.0 |
| **uCode App** (app-beta) | Cross-platform prototype    | v1.0.2.4 |

---

_Last Updated: 2026-01-15_
