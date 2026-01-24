# uDOS Vibe Context (Offline-First)

> **Primary context file for Mistral Vibe CLI** using Devstral Small 2 via Ollama

---

## 🎯 Read First (In Order)

1. [AGENTS.md](../AGENTS.md) — **Start here:** How work is done in this repo
2. [docs/\_index.md](../docs/_index.md) — Engineering entry point
3. [docs/roadmap.md](../docs/roadmap.md) — Current priorities (now/next/later)
4. [docs/devlog/](../docs/devlog/) — Recent development activity
5. [docs/decisions/](../docs/decisions/) — Architecture Decision Records (ADRs)

---

## 📚 Subsystem Entry Points

### Core (TUI Runtime)

- [core/README.md](../core/README.md)
- [core/docs/](../core/docs/)
- Command handlers: `core/commands/`
- Services: `core/services/`
- uPY interpreter: `core/interpreters/`

### App (GUI Client) — PRIVATE (/dev submodule)

- [app/README.md](../app/README.md)
- [app/docs/](../app/docs/)
- Tauri backend: `app/src-tauri/`
- Svelte frontend: `app/src/`

### Wizard (Always-On Server)

- [wizard/README.md](../wizard/README.md)
- [wizard/docs/](../wizard/docs/)
- AI providers: `wizard/providers/`
- Model routing: [docs/decisions/wizard-model-routing-policy.md](../docs/decisions/wizard-model-routing-policy.md)

### Extensions

- [extensions/README.md](../extensions/README.md)
- API Server: `extensions/api/`
- Transport: `extensions/transport/`

### Goblin Dev Server — PRIVATE (/dev submodule)

- [dev/goblin/README.md](../dev/goblin/README.md)
- Experimental features, localhost only

---

## 🏗️ Architecture Quick Reference

### Three Workspaces Model

- **Read formal spec:** [docs/specs/workspace-architecture.md](../docs/specs/workspace-architecture.md)

1. **Core** (Alpine/TUI) — Offline-first, no GUI assumptions
2. **App** (Tauri+Svelte) — GUI client, five markdown formats
3. **Wizard** (Always-on) — AI routing, webhooks, APIs, dev tooling

### Command Routing

```
User Input → SmartPrompt → Parser → CommandHandler → Specialized Handler → Service
```

### Transport Policy

**Private transports:** MeshCore, Bluetooth Private, NFC, QR, Audio
**Public signals:** Bluetooth Public (beacons only, never data)

### Version Management

**NEVER hardcode versions.** Use:

```bash
python -m core.version check
python -m core.version show
python -m core.version bump <component> <type>
```

---

## 📝 Documentation Rules

### Where Things Go

| Type                   | Location                    |
| ---------------------- | --------------------------- |
| **Project-wide truth** | `/docs/`                    |
| **Drafts/experiments** | `**/.dev/` (gitignored)     |
| **Cold storage**       | `**/.archive/` (gitignored) |
| **User workspace**     | `/memory/` (gitignored)     |

### Promotion Pattern

- Work in `.dev/` folders
- After ~2 weeks, promote to `/docs/` or archive
- Log decisions in `docs/decisions/ADR-####-*.md`
- Log daily work in `docs/devlog/YYYY-MM.md`

---

## 🤖 Vibe Configuration Context

### Default Model

**Devstral Small 2** (offline via Ollama)

### Cloud Escalation

See [Wizard Model Routing Policy](../docs/decisions/wizard-model-routing-policy.md)

- Default: **local-only**
- Cloud routing: **disabled by default**
- Escalation requires explicit policy approval

### Task Classification

When routing requests:

- Privacy: `private` | `internal` | `public`
- Intent: `code` | `test` | `docs` | `design` | `ops`
- Workspace: `core` | `app` | `wizard` | `extensions` | `docs`

---

## 🔧 Common Tasks

### Version Management

```bash
# Check all component versions
python -m core.version check

# Show version dashboard
python -m core.version show

# Bump a version
python -m core.version bump core build
```

### Launch Commands

```bash
# TUI
./start_udos.sh

# API + Dashboard (Dev Mode)
./Dev-Mode.command

# Tauri App Dev
./Launch-Tauri-Dev.command
```

### Testing

```bash
# Shakedown (47 tests)
./start_udos.sh
# Then type: SHAKEDOWN

# Python tests
pytest memory/tests/ core/tests/ -v
```

### Self-Healing

```bash
# In TUI:
REPAIR --pull          # Git sync
REPAIR --upgrade-all   # Update all
```

---

## 🚫 Critical Rules

### NEVER

1. Hardcode version strings
2. Bypass transport policy checks
3. Create standalone handlers (extend existing parent handlers)
4. Allow web access from Core (Wizard only)
5. Store secrets in `/memory/` (use encrypted key store)
6. Send data over Bluetooth Public (signals only)

### ALWAYS

1. Use `python -m core.version` for versions
2. Route commands through handler architecture
3. Check transport tier before sending data
4. Log with tags: `[LOCAL]` `[MESH]` `[BT-PRIV]` `[WIZ]` etc.
5. Maintain Alpine Linux compatibility

---

## 📊 Logging

### Primary Debug Log

`memory/logs/session-commands-YYYY-MM-DD.log` — **Check this first** for errors

### Other Logs

- `debug-YYYY-MM-DD.log` — General debug
- `system-YYYY-MM-DD.log` — System events
- `api-YYYY-MM-DD.log` — API/WebSocket

---

## 🎯 Current Focus (2026-01-13)

**Alpha v1.0.2.0:** Workspace Architecture + Alpine Distribution

- [ ] Vibe context setup (this file)
- [ ] Scoped Copilot instructions
- [ ] Wizard Server TUI
- [ ] Wizard Dev Mode
- [ ] TCZ packaging

See [docs/roadmap.md](../docs/roadmap.md) for details.

---

_Last Updated: 2026-01-13_
_For questions, check [AGENTS.md](../AGENTS.md) first_
