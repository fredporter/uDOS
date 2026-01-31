# uDOS Agent Rules (Lean)

> **Fast dev rounds**: Essential rules only. See `.archive/2026-01-29/AGENTS-verbose.md` for full context.

---

## System Architecture

- **Core** (`core/`) — Offline TUI, Alpine Linux, no cloud, no GUI
- **Wizard** (`wizard/`) — Always-on services, AI routing, webhooks, APIs (port 8765)
- **Goblin** (`dev/goblin/`) — Experimental dev server (port 8767, `/api/v0/*`)
- **App** (`app/`) — Tauri+Svelte GUI, no business logic, transport only

---

## Critical Rules

1. **Offline-first** — Local execution baseline; cloud optional
2. **Thin handlers** — Logic in services, not handlers
3. **Never hardcode versions** — Use `python -m core.version`
4. **No boundary blur** — Core=offline, Wizard=cloud, App=UI only
5. **Docs in `/docs`** — Drafts in `.dev/`, archive in `.archive/`
6. **Check subsystem instructions** — `.github/instructions/*.md` for details


---

## Quick Reference

### Core Must NOT
- Cloud connectivity, servers, scraping, email, GUI assumptions

### Wizard Only
- AI routing, webhooks, Gmail relay, OAuth, cloud integration

### App Must NOT
- Business logic, state storage, Core duplication

### Transport Policy
- **Private** (data allowed): MeshCore, BT-Private, NFC, QR, Audio
- **Public** (signal only): BT-Public — NEVER data

### Logging Tags
`[LOCAL]` `[MESH]` `[BT-PRIV]` `[BT-PUB]` `[NFC]` `[QR]` `[AUD]` `[WIZ]` `[CLOUD]` `[GMAIL]`

### Canonical Logger
```python
from core.services.logging_manager import get_logger
logger = get_logger('component-name')
logger.info('[LOCAL] message')
```

### Version Commands
```bash
python -m core.version check          # Check all
python -m core.version show           # Dashboard
python -m core.version bump core build # Bump component
```

---

## Documentation Structure

```
/docs/
  _index.md           # Entry point
  development-streams.md  # Current priorities
  devlog/YYYY-MM.md   # Monthly logs
  decisions/ADR-*.md  # Architectural decisions
  specs/              # Technical specs
  examples/           # Code examples
```

**Drafts:** `**/.dev/` (gitignored)
**Archive:** `**/.archive/` (local-only)
**Promotion:** Useful after 2 weeks → `/docs/` or archive

---

## Repository Structure

**PUBLIC (root):** `core/`, `wizard/`, `extensions/`, `docs/`, `knowledge/`, `library/`
**PRIVATE (/dev):** `goblin/`, `empire/`, `app/`, `groovebox/`, `tests/`, `tools/`
**LOCAL (memory/):** Logs, credentials — never committed

---

## When Stuck

1. Check `.github/instructions/{core,wizard,app,extensions}.instructions.md`
2. Check `docs/_index.md`
3. Check `docs/development-streams.md`
4. Check `memory/logs/session-commands-YYYY-MM-DD.log` for TUI errors
5. If unclear → document and promote

---

_Last Updated: 2026-01-29_
_Structure: Lean reference (verbose archived)_
