# App Subsystem Instructions

> **Scope:** `applyTo: ["app/**"]`

---

## App Architecture

**App** is the uCode Markdown App — a Tauri + Svelte GUI client for uDOS.

### Responsibilities

- Rendering five markdown formats
- Frontmatter-based document presentation
- User interaction and navigation
- Desktop/mobile UI

### Non-Responsibilities

- ❌ Business logic (lives in Core)
- ❌ Long-term state (use Core services)
- ❌ Direct Core modification

---

## Five Markdown Formats

| Format | Extension | Purpose |
|--------|-----------|---------|
| **uCode** | `-ucode.md` | Executable documents with ```upy runtime |
| **Story** | `-story.md` | Interactive presentations, typeform-style Q&A |
| **Marp** | `-marp.md` | Full-viewport slideshow presentations |
| **Guide** | `-guide.md` | Knowledge bank articles |
| **Config** | `-config.md` | System configuration documents |

### Frontmatter Pattern

All formats use YAML frontmatter:

```markdown
---
title: Document Title
format: ucode | story | marp | guide | config
version: 1.0.0
author: Name
tags: [tag1, tag2]
---

# Content...
```

### Story vs uCode

**Story** (Sandboxed)
- Single file contains all data
- Collects variables/objects
- ```story blocks for form fields
- Distributable, can be returned with results
- Use: Setup wizards, games, data collection

**uCode** (Extensible)
- Executes ```upy code blocks
- Accesses external docs/maps/services
- Full uDOS command integration
- Use: Workflows, data processing, integration

---

## Tech Stack

- **Frontend:** Svelte 5
- **Backend:** Rust (Tauri 2.x)
- **Styling:** TailwindCSS
- **Build:** Vite

---

## Type Safety

Use shared type exports from `src/lib/types/`:

```typescript
import type { Document, Frontmatter } from '$lib/types';
```

**NEVER** duplicate type definitions across components.

---

## Component Structure

```
app/
├── src/
│   ├── lib/
│   │   ├── components/      # Reusable UI components
│   │   ├── types/           # Shared TypeScript types
│   │   ├── stores/          # Svelte stores
│   │   └── utils/           # Helper functions
│   ├── routes/              # SvelteKit routes
│   └── app.css              # Global styles
├── src-tauri/               # Rust backend
│   ├── src/
│   └── Cargo.toml
├── static/                  # Static assets
└── version.json             # Version metadata
```

---

## Integration Questions

For v1.0.4.0+ implementation:

1. **Marp wrapper in SvelteKit?**
   - Can we wrap Marp-rendered styles in Svelte components?
   - How to maintain Marp CSS isolation?

2. **gtx-form integration?**
   - Use `library/gtx-form` or build Svelte-native?
   - Typeform-style component requirements?

3. **Story block rendering?**
   - Custom Svelte component architecture?
   - Form validation and state management?

---

## Version Management

Current: App v1.0.3.0

Update via:
```bash
python -m core.version bump app patch
```

---

## Development

```bash
# Install dependencies
cd app
npm install

# Dev mode
npm run tauri:dev

# Build
npm run tauri:build

# Clean
rm -rf src-tauri/target
```

---

## Testing

```bash
# Run tests
npm test

# Type check
npm run check
```

---

## Font Configuration

Standard: 24px retro terminal font (Retrocal Mon)

Configure in `src/app.css` or component-specific styles.

---

## References

- [AGENTS.md](../../AGENTS.md)
- [docs/_index.md](../../docs/_index.md)
- [app/README.md](../../app/README.md)
- [app/docs/](../../app/docs/)

---

*Last Updated: 2026-01-13*
