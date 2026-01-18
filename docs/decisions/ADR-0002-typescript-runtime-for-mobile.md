# ADR-0002: TypeScript Runtime Required for Mobile/iPad

**Status:** Accepted  
**Date:** 2026-01-15  
**Context:** Architecture clarification for uMarkdown cross-platform strategy

---

## Context

uDOS is developing a cross-platform markdown app with executable code blocks:

- **Desktop (macOS):** Tauri + Svelte app
- **Mobile (iOS/iPadOS):** Native app (future)

Both need to render and execute markdown files with runtime blocks (state, set, form, if, nav, panel, map).

Initial plan was to use Python services (Wizard/Goblin) for all execution, but mobile/iPad cannot run Python.

---

## Problem

**Mobile/iPad Constraint:** iOS/iPadOS apps cannot execute Python code natively.

**Requirement:** Mobile users must be able to:

1. Present markdown files offline
2. Execute runtime blocks (.ts code)
3. Collect form data interactively
4. Navigate between chapters/sections
5. Save state locally (SQLite)

**Current State:**

- Python services work great for desktop (Wizard on port 8765, Goblin on port 8767)
- Tauri app can call Python services via HTTP (localhost)
- Mobile has no Python runtime available

---

## Decision

**Build TypeScript runtime specifically for mobile/iPad offline execution.**

**Platform Strategy:**

### Desktop (macOS) - Python Services

- Tauri app calls Wizard/Goblin servers via HTTP
- Full Python capabilities: AI routing, Notion sync, task scheduling
- Wizard Server (8765) for production features
- Goblin Server (8767) for experimental features

### Mobile/iPad (iOS/iPadOS) - TypeScript Runtime

- Native TypeScript execution (no Python available)
- Sandboxed runtime for security
- SQLite for local data storage
- MeshCore sync with desktop when online

**Implementation:**

1. **v1.0.2.0:** Python services (Goblin) - desktop development
2. **v1.0.3.0:** TypeScript runtime scaffold - mobile preparation
3. **v1.0.4.0+:** iOS/iPadOS native app with TypeScript runtime

---

## Architecture

### TypeScript Runtime Components

```
/core/ (TypeScript Runtime)
├── parser.ts           # Markdown → AST
├── state-manager.ts    # Variables, objects, arrays
├── executors/
│   ├── state.ts       # State declarations
│   ├── set.ts         # Variable assignment
│   ├── form.ts        # Interactive forms
│   ├── if.ts          # Conditionals
│   ├── nav.ts         # Navigation
│   ├── panel.ts       # UI panels
│   └── map.ts         # Data mapping
├── storage/
│   └── sqlite.ts      # Local database (better-sqlite3)
└── sandbox.ts         # Execution isolation

/core-beta/ (Python TUI)
└── [Current Python implementation]
```

### Execution Flow

**Desktop:**

```
Markdown File → Tauri App → HTTP → Goblin Server → Python Runtime → Response
```

**Mobile:**

```
Markdown File → Native App → TypeScript Runtime → SQLite → Response
```

---

## Consequences

### Positive

✅ **Mobile offline capability:** Users can present and execute markdown files without internet
✅ **Platform independence:** Desktop uses Python, mobile uses TypeScript (each optimized)
✅ **Security:** Sandboxed TypeScript execution prevents malicious code
✅ **Sync flexibility:** MeshCore allows desktop ↔ mobile data sync when online

### Negative

❌ **Dual runtime maintenance:** Must maintain both Python and TypeScript runtimes
❌ **Feature parity:** Need to ensure both runtimes support same block types
❌ **Testing complexity:** Must test on both platforms

### Mitigation

- Share test cases between Python and TypeScript implementations
- Define canonical runtime spec (behavior documentation)
- Use TypeScript for mobile ONLY (desktop continues using Python)
- Keep runtime simple and deterministic (no AI, no network in TypeScript runtime)

---

## Alternatives Considered

### 1. Python-only (Desktop-only App)

**Rejected:** Eliminates mobile/iPad market entirely

### 2. WebAssembly Python (Pyodide)

**Rejected:**

- Large bundle size (~50MB)
- Performance issues on mobile
- Complex debugging

### 3. Server-required Mobile App

**Rejected:**

- Breaks offline-first principle
- Requires internet for all execution
- Not viable for field use

---

## References

- [Roadmap v1.0.3.0](../roadmap.md#v103-typescript-runtime-scaffold)
- [AGENTS.md Architecture](../../AGENTS.md#3-workspace-boundaries)
- [Goblin Dev Server](../../dev/goblin/README.md)

---

_This decision enables uDOS to support mobile/iPad while maintaining desktop Python services._
