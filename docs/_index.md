# uDOS Engineering Index

> **Start here** for all project-wide documentation.

---

## 🎯 Essential Reading

| Document | Purpose |
|----------|---------|
| [AGENTS.md](../AGENTS.md) | How work is done in this repo |
| [roadmap.md](roadmap.md) | Now / Next / Later |
| [devlog/](devlog/) | Chronological development notes |
| [decisions/](decisions/) | Architecture Decision Records (ADRs) |

---

## 🏗️ Subsystems

| System | Entry Point | Description |
|--------|-------------|-------------|
| **Core** | [core/README.md](../core/README.md) | TUI runtime, command handlers, uPY interpreter |
| **App** | [app/README.md](../app/README.md) | uCode Markdown App (Tauri + Svelte) |
| **Wizard** | [wizard/README.md](../wizard/README.md) | Always-on server, AI routing, dev tooling |
| **Extensions** | [extensions/README.md](../extensions/README.md) | API, Transport, optional feature packs |

### Architecture & Setup

- [Three-Workspace Architecture](specs/workspace-architecture.md) — Core, App, Wizard boundaries
- [Vibe Setup (Offline Agent)](specs/vibe-setup.md) — VS Code, Copilot, Vibe CLI context

### Core Documentation

- [Command Architecture](../core/docs/COMMAND-ARCHITECTURE.md)
- [Handler Pattern](../core/docs/)
- [Services Overview](../core/docs/)
- [uPY Interpreter](../core/docs/)

### App Documentation

- [Format Architecture](../app/docs/) - Five markdown formats
- [Frontmatter Spec](../app/docs/)
- [Tauri Integration](../app/docs/)

### Wizard Documentation

- [Model Routing Policy](decisions/wizard-model-routing-policy.md)
- [AI Provider Integration](../wizard/docs/)
- [Gmail Relay](../wizard/docs/)

---

## 📚 Key References

| Document | Location |
|----------|----------|
| Project Structure | [structure.txt](../structure.txt) |
| Port Registry | [extensions/PORT-REGISTRY.md](../extensions/PORT-REGISTRY.md) |
| Knowledge Bank | [knowledge/README.md](../knowledge/README.md) |
| Copilot Instructions | [.github/copilot-instructions.md](../.github/copilot-instructions.md) |
| Vibe Context | [.vibe/CONTEXT.md](../.vibe/CONTEXT.md) |

---

## 🔧 Quick Commands

```bash
# Version management
python -m core.version check        # Check all versions
python -m core.version show         # Dashboard
python -m core.version bump core build

# Launch
./start_udos.sh                     # TUI
./Dev-Mode.command                  # API + Dashboard
./Launch-Tauri-Dev.command          # App dev mode

# Testing
SHAKEDOWN                           # 47 system tests (in TUI)
pytest memory/tests/ -v             # Python tests

# Self-healing
REPAIR --pull                       # Git sync
REPAIR --upgrade-all                # Update all
```

---

## 📝 How to Contribute Docs

### Drafts (Local Only)

- Work in `**/.dev/` folders (gitignored)
- Experiment freely

### Promotion (After ~2 weeks)

Move to canonical locations:

| Type | Destination |
|------|-------------|
| Current work | `docs/devlog/YYYY-MM.md` |
| Architecture decision | `docs/decisions/ADR-####-*.md` |
| Repeatable procedure | `docs/howto/*.md` |
| Technical spec | `docs/specs/*.md` |
| Long-term plan | `docs/roadmap.md` |

### Archive (No longer relevant)

- Move to `**/.archive/YYYY-MM-DD/` (gitignored)

---

## 🗺️ Directory Map

```
/
├── AGENTS.md                    # How we work
├── docs/                        # Engineering spine
│   ├── _index.md               # This file
│   ├── roadmap.md              # Now/Next/Later
│   ├── devlog/                 # Monthly logs
│   ├── decisions/              # ADRs
│   ├── howto/                  # Procedures
│   └── specs/                  # Technical specs
├── core/                        # TUI runtime
├── app/                         # GUI client
├── wizard/                      # Always-on server
├── extensions/                  # Optional features
├── knowledge/                   # Knowledge bank (231+ articles)
├── library/                     # Third-party repos (gitignored)
├── memory/                      # User workspace (gitignored)
└── dev/                         # Engineering workshop
```

---

## 🎯 Current Focus

See [docs/roadmap.md](roadmap.md) for details.

**Alpha v1.0.2.0:** TinyCore Distribution
- TCZ packaging
- Stack installer (ultra/micro/mini/core/standard/wizard)
- ISO builder
- Platform detection

---

*Last Updated: 2026-01-13*  
*For questions, check AGENTS.md first*
