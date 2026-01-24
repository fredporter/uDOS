# uDOS Agent Rules

> This file defines **how work is done** in the uDOS repository. It is the primary shared context for Agents, VS Code, offline Vibe (Devstral), and any cloud routing.

---

## 1. Purpose

uDOS is a **multi-system project** built around three major workspaces:

- **Core** — Alpine Linux–targeted, offline-first TUI runtime (no GUI, multi-OS support)
- **App** — GUI client (Tauri + Svelte now, native macOS + iOS/iPadOS later)
- **Wizard Server** — always-on services (webhooks, APIs, AI routing, packaging, dev tooling)

This file exists to:

- Prevent architectural drift
- Keep documentation sane and non-duplicated
- Ensure offline-first development remains viable
- Provide a single operational truth for all Agents

---

## 2. Core Principles

1. **Offline-first by default**\
   Local execution (Alpine Linux, Ollama, Devstral) is the baseline. Cloud services are optional extensions.

2. **Small, composable systems**\
   Handlers are thin. Shared logic lives in services/utils. Large behaviour is composed, not embedded.

3. **One source of truth for docs**\
   Drafts are allowed everywhere locally. Canonical truth lives in `/docs`.

4. **Explicit boundaries**\
   App, Core, Wizard, Extensions have different responsibilities and must not blur.

5. **Agents assist, humans decide**\
   Agents may propose changes, but architectural decisions are recorded explicitly.

6. **Version control is mandatory**\
   NEVER hardcode version strings. Always use `python -m core.version` commands.

---

## 3. Workspace Boundaries

### 3.1 Core (`core/`)

**What Core is:**

- Offline-first runtime
- TUI only (no GUI assumptions)
- Alpine Linux primary target (macOS, Ubuntu, Windows dev support)
- Houses command handlers, services, uPY interpreter
- Custom scripting language (uPY - restricted Python subset)
- OS-aware with platform-specific capabilities

**Core must NOT:**

- Depend on cloud connectivity
- Contain long-running servers
- Perform web scraping or email I/O
- Assume graphical capabilities

**Canonical docs:**

- `core/docs/`
- `core/README.md`
- Referenced from `docs/_index.md`

---

### 3.2 App (`dev/app/`) — PRIVATE SUBMODULE

**What App is:**

- User-facing GUI (uCode Markdown App)
- Currently Tauri + Svelte
- Future native macOS + iOS/iPadOS clients
- Five markdown formats: `-ucode.md`, `-story.md`, `-marp.md`, `-guide.md`, `-config.md`
- **Location:** `/dev/app/` (private submodule)

**App responsibilities:**

- Rendering frontmatter-based markdown formats
- User interaction and presentation
- Transport only (no business logic)

**App must NOT:**

- Reimplement Core logic
- Store long-term state
- Make architectural decisions

**Primary reference:**

- `dev/app/README.md`
- `dev/app/docs/`

---

### 3.3 Wizard Server (`wizard/`)

**What Wizard is:**

- Always-on service layer
- AI model routing (Ollama/Devstral local, OpenRouter cloud burst)
- Webhooks, APIs, scraping, email relay (Gmail)
- Packaging, distribution, sync, automation
- Dev tooling and Agent gateways

**Wizard responsibilities:**

- Policy and orchestration
- API key management and quotas
- Model routing (see `docs/decisions/wizard-model-routing-policy.md`)
- Dev tooling and Agent gateways
- Cloud integration (Wizard only, never Core)

**Wizard must NOT:**

- Duplicate Core runtime logic
- Break offline Core assumptions
- Expose child devices to web

---

### 3.3.1 Wizard Server (`wizard/server.py` — Port 8765)

**Status:** Production v1.1.0.0 (stable, frozen)

**What Wizard Server is:**

- Always-on service with web access (production-grade)
- Device authentication + session management
- Plugin repository API + distribution
- AI model routing (local-first with cloud escalation)
- Cost tracking + quota enforcement
- Real-time monitoring via WebSocket

**Wizard Server endpoints (locked):**

```
/health                    — Health check
/api/v1/devices/auth      — Device authentication
/api/v1/devices/sessions  — Session management
/api/v1/extensions/*      — Extension repository
/api/v1/cost/*            — Cost tracking
/api/v1/quotas/*          — Quota checks
/api/v1/ai/route          — Model routing
/ws                       — WebSocket updates
```

**Wizard Server must NOT:**

- Contain experimental APIs
- Support Notion sync (Dev Server only)
- Run task scheduling (Dev Server only)
- Implement TS runtime execution (Dev Server only)

**Configuration:** `wizard/config/wizard.json` (committed, versioned)

---

### 3.3.2 Goblin Dev Server (`dev/goblin/dev_server.py` — Port 8767)

**Status:** Development v0.1.0.0 (unstable, experimental)

**What Goblin Dev Server is:**

- Experimental always-on server for new features (localhost only)
- Notion sync + incoming webhooks
- TS Markdown runtime execution (parse, execute, state management)
- Task scheduling (organic cron model: Plant → Sprout → Prune → Trellis → Harvest → Compost)
- Project/mission management + binder compilation

**Goblin Dev Server endpoints (unstable — `/api/v0/*`):**

```
/health                         — Health check
/api/v0/notion/webhook          — Incoming Notion changes
/api/v0/notion/sync/status      — Current sync state
/api/v0/notion/maps             — Local ↔ Notion mappings
/api/v0/runtime/parse           — Parse .md to AST
/api/v0/runtime/execute         — Execute runtime block
/api/v0/runtime/state           — Get/set variables
/api/v0/tasks/schedule          — Schedule task
/api/v0/tasks/queue             — View scheduled queue
/api/v0/tasks/runs              — Task execution history
/api/v0/binder/compile          — Compile binder outputs
/api/v0/binder/chapters         — Get binder chapter structure
```

**Goblin Dev Server design:**

- Runs on `localhost:8767` (dev machines only)
- Endpoints prefixed `/api/v0/*` (unstable, subject to breaking changes)
- Isolated from production Wizard (independent state, config, services)
- Free to break and iterate rapidly
- Secret tokens local-only (gitignored)
- When features stabilize, promoted to Wizard or Core

**Configuration:** `/dev/goblin/config/goblin.json` (local-only, gitignored)

**Services:**

- `notion_sync_service.py` — Notion webhooks, SQLite queue, conflict detection
- `runtime_executor.py` — TS Markdown runtime (state, set, form, if, nav, panel, map blocks)
- `task_scheduler.py` — Organic cron with provider rotation and quota pacing
- `binder_compiler.py` — Multi-format compilation (Markdown, PDF, JSON, dev briefs)

---

### 3.4 Extensions (`extensions/`)

**Extensions are:**

- Optional, composable feature packs
- Must declare capabilities explicitly
- Must not assume always-on connectivity unless stated

Each extension must have:

- `README.md`
- `version.json`
- Clear dependency declaration

Current extensions:

**Public (in `/extensions/`):**

- `api/` - REST/WebSocket API server
- `transport/` - MeshCore, Audio, QR, NFC, Bluetooth transports
- `vscode/` - VS Code extension

**Wizard-only (in `/wizard/extensions/`):**

- `assistant/` - AI services (Gemini, Vibe CLI, Ollama)

**Goblin-only (in `/dev/goblin/services/`):**

- `notion_sync_service.py` - Notion webhooks + publish mode
- `runtime_executor.py` - TS Markdown runtime
- `task_scheduler.py` - Organic cron scheduling
- `binder_compiler.py` - Binder output compilation

**Private (in `/dev/groovebox/`):**

- Music production tools (MML, 808 drums)

> **📌 Repository Structure (2026-01-21):**
>
> - **PUBLIC (root):** `core/`, `wizard/`, `extensions/`, `docs/`, `knowledge/`, `library/`, `distribution/`
> - **PRIVATE (/dev submodule):** `goblin/`, `empire/`, `app/`, `groovebox/`, `tests/`, `tools/`
> - **LOCAL (memory/):** User data, logs, credentials — never committed
>
> **Library workflow:** Test in `/dev/library/` → Create definition in `/library/` → Commit → Distribute

---

## 4. Documentation Rules (Critical)

### 4.1 The Documentation Spine

All **project-wide truth** lives under:

```text
/docs
  _index.md        # entry point
  roadmap.md       # now / next / later
  devlog/          # chronological notes (YYYY-MM.md)
  decisions/       # ADRs (why we chose X)
  howto/           # repeatable procedures
  specs/           # stable technical specs
```

If information matters across subsystems, it belongs here.

---

### 4.2 Drafts, Scratch, and Local Notes

- Drafts and experiments live in `**/.dev/` (local-only, gitignored)
- Cold storage lives in `**/.archive/` (local-only)

**Promotion rule:**\
If a note is still useful after ~2 weeks, it must be promoted into `/docs` or archived.

---

### 4.3 Dev Log Discipline

- Ongoing work is recorded in `docs/devlog/YYYY-MM.md`
- Keep entries short and factual
- Link to commits, tests, or scripts when relevant
- Cloud escalation events MUST be logged (cost + reason)

---

### 4.4 Decisions (ADRs)

Use `docs/decisions/ADR-####-*.md` when:

- There is a trade-off
- A boundary is defined or changed
- A tool or architecture is chosen or rejected

Decisions explain **why**, not just **what**.

Format:

```markdown
# ADR-####: Title

**Status:** Accepted | Rejected | Superseded
**Date:** YYYY-MM-DD
**Context:** What is the issue?
**Decision:** What did we decide?
**Consequences:** What are the trade-offs?
```

---

## 5. Transport Policy (Non-Negotiable)

### Private Transports (Commands + Data Allowed)

- **MeshCore** - Primary P2P/mesh
- **Bluetooth Private** - Paired devices
- **NFC** - Physical contact
- **QR Relay** - Visual data transfer
- **Audio Relay** - Acoustic packets

### Public Signal Channels (No Data Ever)

- **Bluetooth Public** - Beacons/presence only
- NEVER carry uDOS data or commands

**Logging tags:** `[LOCAL]` `[MESH]` `[BT-PRIV]` `[BT-PUB]` `[NFC]` `[QR]` `[AUD]` `[WIZ]` `[GMAIL]`

---

## 6. Agents, Models, and Tooling

### 6.1 Terminology

- Use the term **Agent** (not AI)
- Agents assist with analysis, drafting, and code generation

---

### 6.2 Offline-first Agent Setup

Default development Agent:

- **Devstral Small 2** via Ollama (offline)

This is the baseline for:

- Code edits
- Refactors
- Test generation
- Documentation drafting

---

### 6.3 Cloud Escalation (Optional)

Cloud routing (eg OpenRouter) is:

- Optional
- Policy-controlled (Wizard Server)
- Used only when explicitly required
- See `docs/decisions/wizard-model-routing-policy.md`

When cloud escalation is used:

- Reason must be noted in dev log
- Costs must be tracked
- Secrets must be redacted

---

## 7. Version Management

### 7.1 Independent Component Versioning

Each component has its own `version.json`:

| Component | Location                            | Version         |
| --------- | ----------------------------------- | --------------- |
| Core      | `core/version.json`                 | v1.1.0.0        |
| API       | `extensions/api/version.json`       | v1.1.0.0        |
| App       | `app/version.json`                  | v1.0.3.0        |
| Wizard    | `wizard/version.json`               | v1.1.0.0        |
| Transport | `extensions/transport/version.json` | v1.0.1.0        |
| Knowledge | `knowledge/version.json`            | Timestamp-based |

### 7.2 Version Manager Commands

```bash
# Check all versions
python -m core.version check

# Show version dashboard
python -m core.version show

# Bump a component
python -m core.version bump core build
python -m core.version bump api patch
```

**NEVER hardcode version strings** - always use the version manager.

---

## 8. VS Code and Workflow Integration

- VS Code tasks are helpers, not the source of truth
- Canonical workflows are defined in uDOS-native formats (Markdown first)
- Multi-root workspace is preferred:
  - `app/`
  - `core/`
  - `wizard/`
  - `extensions/`
  - `docs/`

---

## 9. Safety, Secrets, and State

- Secrets must never be committed
- Local secrets belong in:
  - `memory/private/`
  - OS keychain mechanisms
  - `wizard/config/*.json` (local-only, gitignored)
- Audit and security tooling lives in Core/Wizard, not App

---

## 10. Command Routing Architecture

```
User Input → SmartPrompt → Parser → CommandHandler → Specialized Handler → Service
```

**Handler Pattern:**

```python
class FileHandler(BaseCommandHandler):
    def handle(self, command, params, grid, parser):
        if command == "NEW": return self._handle_new(params)
        elif command == "DELETE": return self._handle_delete(params)
```

**Key Handlers:**

- ShakedownHandler - System validation (47 tests)
- RepairHandler - Self-healing, git pull, upgrades
- BundleHandler - Package bundling
- CaptureHandler - Screenshot/recording
- WellbeingHandler - User wellness features
- MaintenanceHandler - TIDY/CLEAN workspace

---

## 11. Logging System

### Primary Debug Log

`memory/logs/session-commands-YYYY-MM-DD.log` - **CHECK THIS FIRST** for TUI errors

### Other Logs

- `debug-YYYY-MM-DD.log` - General debug
- `system-YYYY-MM-DD.log` - System events
- `api-YYYY-MM-DD.log` - API/WebSocket

### Canonical Logger

```python
from core.services.logging_manager import get_logger

logger = get_logger('system-startup')
logger.info('[LOCAL] uDOS starting...')
```

---

## 12. Testing

```bash
# Activate venv
source .venv/bin/activate

# Run shakedown (47 tests)
./start_udos.sh
# Then type: SHAKEDOWN

# Run pytest
pytest memory/tests/ core/tests/ -v
```

---

## 13. Final Rule

If something feels unclear:

1. Check `AGENTS.md` (this file)
2. Check `docs/_index.md`
3. Check the roadmap and recent dev logs
4. Check subsystem-specific instructions:
   - `.github/instructions/core.instructions.md`
   - `.github/instructions/app.instructions.md`
   - `.github/instructions/wizard.instructions.md`
   - `.github/instructions/extensions.instructions.md`

If it still isn't clear, **write it down and promote it properly**.

---

_Last Updated: 2026-01-21_
_uDOS Alpha v1.0.2.0 (Pre-release)_
_Structure: Public root + Private /dev submodule_
