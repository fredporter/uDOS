---
title: Three-Workspace Architecture
status: active
version: 1.0.0
promoted: 2026-01-13
from: dev/roadmap/3-workspaces.md
---

# Three-Workspace Architecture

> Design pattern for uDOS as three distinct products sharing one engineering spine.

---

## Overview

uDOS is **three separate products** with a **unified engineering context**:

| Product | Location | Purpose |
|---------|----------|---------|
| **Core** | `core/` | TUI runtime, commands, uPY interpreter (Tiny Core Linux) |
| **App** | `app/` | GUI client (Tauri + Svelte now; native macOS/iOS later) |
| **Wizard** | `wizard/` | Always-on server (webhooks, APIs, AI routing, packaging) |

**Key principle:** One repo, three workspaces, one doc spine.

---

## Why Three Workspaces?

### Problem to Avoid
Three separate products can lead to three separate wikis, duplicated docs, inconsistent conventions.

### Solution
Keep docs in a **single engineering spine** (`/docs`) while allowing each workspace to maintain its own technical reference.

---

## Architectural Boundaries

### Core (`core/`)
**What it is:**
- Offline-first runtime
- TUI only (no GUI assumptions)
- TinyCore Linux compatible
- Command handlers, services, uPY interpreter
- Custom scripting language (uPY — restricted Python)

**Core must NOT:**
- Depend on cloud connectivity
- Contain long-running servers
- Perform web scraping or email I/O
- Assume graphical capabilities

**Authority:**
- Canonical docs: `core/docs/`
- README: `core/README.md`
- Referenced from: `docs/_index.md`

**Example docs:**
- `core/docs/COMMAND-ARCHITECTURE.md`
- `core/docs/FILESYSTEM-ARCHITECTURE.md`
- `core/docs/INPUT-SYSTEM.md`

---

### App (`app/`)
**What it is:**
- User-facing GUI (uCode Markdown App)
- Currently: Tauri + Svelte
- Future: Native macOS + iOS/iPadOS clients
- Five markdown formats: `-ucode.md`, `-story.md`, `-marp.md`, `-guide.md`, `-config.md`

**App responsibilities:**
- Rendering frontmatter-based markdown formats
- User interaction and presentation
- Transport layer only (no business logic)

**App must NOT:**
- Reimplement Core logic
- Store long-term state locally
- Make architectural decisions

**Authority:**
- Canonical docs: `app/docs/`
- README: `app/README.md`
- Build/run guide: `app/README.md`

**Example docs:**
- `app/docs/APP-ARCHITECTURE.md`
- `app/docs/KEYBOARD-SHORTCUTS.md`
- `app/docs/ICON-SYSTEM-SUMMARY.md`

---

### Wizard (`wizard/`)
**What it is:**
- Always-on service layer
- AI model routing (Ollama/Devstral local, OpenRouter cloud burst)
- Webhooks, APIs, scraping, email relay (Gmail)
- Packaging, distribution, sync, automation
- Dev tooling and Agent gateways

**Wizard responsibilities:**
- Policy and orchestration
- API key management and quotas
- Model routing (see `docs/decisions/wizard-model-routing-policy.md`)
- Cloud integration (Wizard only, never Core)
- Dev tooling gateway

**Wizard must NOT:**
- Duplicate Core runtime logic
- Break offline Core assumptions
- Expose child devices to web

**Authority:**
- README: `wizard/README.md`
- Technical docs: `wizard/docs/` (to be created)
- Policy: `docs/decisions/wizard-model-routing-policy.md`

---

## Single Engineering Spine (`/docs`)

While each workspace has its own technical reference, **project-wide truth** lives in `/docs`:

```
/docs
├── _index.md           # Entry point, links to all subsystems
├── roadmap.md          # Now/Next/Later priorities
├── devlog/             # Monthly development notes
├── decisions/          # Architecture Decision Records
├── howto/              # Repeatable procedures (cross-subsystem)
└── specs/              # Finalized specifications
    ├── workspace-architecture.md (this file)
    ├── vibe-setup.md
    └── ...
```

### Doc Types in `/docs`

| Type | Location | Purpose | Immutable? |
|------|----------|---------|-----------|
| Roadmap | `roadmap.md` | What + sequencing | No (updated weekly) |
| Development log | `devlog/YYYY-MM.md` | What happened + links | No (monthly file) |
| Decisions | `decisions/ADR-*.md` | Why we chose X | Yes (immutable) |
| How-to | `howto/*.md` | Repeatable procedures | No (evolves) |
| Specs | `specs/*.md` | Finalized tech specs | Mostly yes (stable) |

### Subsystem Documentation (Local Authority)

Each workspace keeps its technical reference:

```
core/docs/          ← Core architecture details
app/docs/           ← App-specific architecture
wizard/docs/        ← Wizard service details
extensions/*/docs/  ← Extension specifications
```

**Rule:** These are **technical references**, not project-wide truth. Project-wide truth is in `/docs`.

---

## Promotion Pipeline

### Drafts (Local, Gitignored)
```
core/.dev/
app/.dev/
wizard/.dev/
dev/.dev/
```

**Purpose:** Scratchpad. Work freely. No review needed.

### Promotion (After ~2 Weeks)

If a draft is still useful after 2 weeks, promote to:

| Content | Destination |
|---------|-------------|
| Release highlights | `docs/devlog/YYYY-MM.md` |
| Architecture decision | `docs/decisions/ADR-####-*.md` |
| Repeatable procedure | `docs/howto/*.md` |
| Technical spec | `docs/specs/*.md` |
| Quick tip | Subsystem README or `.dev/` |

### Archive (No Longer Relevant)

Move to:
```
core/.archive/YYYY-MM-DD/
dev/.archive/YYYY-MM-DD/
app/.archive/YYYY-MM-DD/
```

**Purpose:** Cold storage. Kept for reference; not active.

---

## Workspace-Specific Setup

### VS Code Multi-Root Workspace

uDOS-Alpha.code-workspace should include:
```json
{
  "folders": [
    { "path": ".", "name": "🏠 uDOS Root" },
    { "path": "core", "name": "⚙️ Core" },
    { "path": "app", "name": "🖥️ App" },
    { "path": "wizard", "name": "🧙 Wizard" },
    { "path": "extensions/api", "name": "🔌 API" },
    { "path": "extensions/transport", "name": "📡 Transport" },
    { "path": "docs", "name": "📚 Docs" }
  ],
  "settings": {
    "python.defaultInterpreterPath": "${workspaceFolder:⚙️ Core}/../.venv/bin/python"
  }
}
```

**Benefits:**
- VS Code respects workspace boundaries
- Tasks, search scope, and Copilot instructions can target specific workspaces
- Extensions can activate per-workspace

---

## Communication Between Workspaces

### Core ↔ App
- **Transport:** REST API (`extensions/api/`) or WebSocket
- **Core provides:** Commands, state, knowledge
- **App provides:** GUI rendering, user input

### Core ↔ Wizard
- **Transport:** REST API, WebSocket
- **Core provides:** Local execution results
- **Wizard provides:** Cloud services, routing, scheduling

### App ↔ Wizard
- **Transport:** REST API, WebSocket
- **App provides:** User requests
- **Wizard provides:** Complex/async operations

### No Direct Core ↔ Web
**Non-negotiable rule:** Core never speaks to the internet directly. Wizard is the only cloud gateway.

---

## Policy Enforcement (Transport)

### Private Transports (Commands + Data Allowed)
- **MeshCore** — Primary P2P/mesh
- **Bluetooth Private** — Paired devices
- **NFC** — Physical contact
- **QR Relay** — Visual data transfer
- **Audio Relay** — Acoustic packets

### Public Signal Channels (No Data Ever)
- **Bluetooth Public** — Beacons/presence only
- **NEVER** carry uDOS data or commands

**Logging tags (required):**
```
[LOCAL]    - Local device operation
[MESH]     - MeshCore P2P
[BT-PRIV]  - Bluetooth Private
[BT-PUB]   - Bluetooth Public (signal only!)
[NFC]      - NFC contact
[QR]       - QR relay
[AUD]      - Audio transport
[WIZ]      - Wizard Server operation
[GMAIL]    - Gmail relay (Wizard only)
```

---

## Quick Reference: Who Owns What?

| Concern | Owner | Authority |
|---------|-------|-----------|
| Command architecture | Core | `core/docs/COMMAND-ARCHITECTURE.md` |
| App rendering | App | `app/docs/APP-ARCHITECTURE.md` |
| Model routing | Wizard | `docs/decisions/wizard-model-routing-policy.md` |
| Transport policy | Extensions | `extensions/transport/policy.yaml` |
| Cross-project roadmap | Root `/docs` | `docs/roadmap.md` |
| Secrets/keys | Local (never git) | `.vibe/config.toml`, OS keychain |

---

## Version Management

Each workspace has its own version:

```bash
# Check all versions
python -m core.version check

# Show version dashboard
python -m core.version show

# Bump a component
python -m core.version bump core build
python -m core.version bump app patch
python -m core.version bump wizard minor
```

**Never hardcode version strings.** Always use the version manager.

---

## Testing Strategy

### Unit Tests (Per Workspace)
- `core/tests/` — Core logic tests
- `app/tests/` — Component tests (Svelte + Tauri)
- `wizard/tests/` — Service tests
- `extensions/*/tests/` — Extension-specific tests

### Integration Tests
- `memory/tests/` — Full-stack scenarios
- Run via SHAKEDOWN in TUI: `SHAKEDOWN` (47 tests)
- Or: `pytest memory/tests/ -v`

---

## Build/Release Strategy

### Development
```bash
# Core TUI
./start_udos.sh

# App GUI
npm run dev  # in app/

# Wizard Server
python wizard/server.py
```

### Distribution (Per Workspace)
- **Core:** TCZ packages (TinyCore)
- **App:** DMG (macOS), then native apps (iOS/macOS)
- **Wizard:** Docker, pip wheel, or system package
- **Knowledge:** Git-based sync or CDN

---

## Example: Adding a New Feature Across Workspaces

**Scenario:** Add a new "notes" command in Core, display in App.

### Step 1: Core
- Add handler in `core/commands/notes_handler.py`
- Add service in `core/services/notes_service.py`
- Test with `pytest core/tests/test_notes.py`
- Update `core/docs/COMMAND-ARCHITECTURE.md` if needed

### Step 2: App
- Add UI component in `app/src/components/NotesView.svelte`
- Call Core API (or WebSocket) for data
- Test component in Svelte dev mode

### Step 3: Wizard (Optional)
- If "notes sync" needed: add sync service in `wizard/services/`
- Update routing policy if needed

### Step 4: Documentation
- Update `docs/devlog/YYYY-MM.md`
- Add to `docs/roadmap.md` when complete
- Promote any design notes from `.dev/` to `docs/specs/` if stable

---

## Checklist: Three-Workspace Setup

- [x] Core, App, Wizard have clear boundaries
- [x] `/docs` is the single source of project truth
- [x] Subsystem docs are technical references
- [x] Transport policy is documented and enforced
- [x] Version management is centralized
- [x] No hard-coded secrets in git
- [x] Drafts live in `.dev/`, promoted or archived regularly
- [ ] VS Code multi-root workspace is set up
- [ ] CI/CD respects the three workspaces

---

*Promoted from: dev/roadmap/3-workspaces.md (2026-01-13)*  
*Status: Active (v1.0.0)*
