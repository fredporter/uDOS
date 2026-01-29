# GitHub Copilot Instructions for uDOS

**uDOS** — Offline-first, distributed OS layer: Python TUI (Alpine Linux primary), Tauri GUI, custom uPY scripting, cloud-optional services.

---

## 🏗️ Repository Structure

| Location | Visibility | Purpose |
|----------|------------|---------|
| **/** (root) | PUBLIC | Core TUI, Wizard server, Extensions, Docs, Knowledge, Library |
| **/dev** (submodule) | PRIVATE | Goblin, Empire, App, Groovebox, Tests, Tools |
| **/memory** | LOCAL | User data, logs, credentials (gitignored) |

**Submodule:** `git submodule update --init --recursive`

---

## 📚 Documentation Hierarchy

**Start here:**
1. [AGENTS.md](../AGENTS.md) — Core development rules (lean version)
2. [docs/README.md](../docs/README.md) — Engineering entry point
3. [docs/development-streams.md](../docs/development-streams.md) — Current roadmap

**Component docs:**
- Core: `core/README.md` — Offline TUI runtime
- Wizard: `wizard/README.md` — Production server (port 8765)
- Extensions: `extensions/README.md` — API + Transport
- App: `app/README.md` — Tauri + Svelte GUI

---

## 🎯 Core Rules

1. **Offline-first** — No cloud by default; explicit opt-in for cloud features
2. **Modular** — Thin handlers → Services → Core
3. **Versioned** — `python -m core.version` (never hardcode versions)
4. **Policy-driven** — Transport rules enforced (private vs public)
5. **Logged** — Use canonical logger: `from core.services.logging_manager import get_logger`

---

## 🔒 Transport Policy

### Private (Data Allowed)
MeshCore, Bluetooth-Private, NFC, QR, Audio Relay

### Public (Signal Only)
Bluetooth-Public — NEVER carry data or commands

---

## 📝 Logging

```python
from core.services.logging_manager import get_logger
logger = get_logger('component-name')
logger.info('[LOCAL] Message')  # Use tags: [LOCAL] [MESH] [BT-PRIV] [NFC] [QR] [AUD] [CLOUD]
```

**Debug log:** `memory/logs/session-commands-YYYY-MM-DD.log`

---

## 📦 Component Boundaries

### Core (`core/**`)
- ✅ TUI, handlers, services, state management
- ❌ No cloud, web scraping, email, or GUI assumptions

### Wizard (`wizard/**`)
- ✅ AI routing, webhooks, Gmail relay, OAuth, cloud integration
- ❌ No Core logic duplication

### App (`app/**`)
- ✅ UI only (Tauri + Svelte)
- ❌ No business logic; delegate to Core

### Extensions (`extensions/**`)
- ✅ API + Transport (independent)
- ❌ No Core duplication

---

## 🗂️ Library Structure

- **`/library/`** — Tool container definitions (PUBLIC, tracked)
- **`/dev/library/`** — Local reference clones (PRIVATE, gitignored)

**Promotion:** Test in `/dev/library/` → Create definition in `/library/` → Commit definition only

---

## 🔧 Version Management

```bash
python -m core.version check           # Check all versions
python -m core.version show            # Dashboard
python -m core.version bump core build # Bump component
```

**Rule:** Never hardcode version strings.

---

## 🧪 Key Systems

| System | Purpose | File |
|--------|---------|------|
| **ShakedownHandler** | System validation | `core/commands/shakedown_handler.py` |
| **RepairHandler** | Self-healing | `core/commands/repair_handler.py` |
| **DebugEngine** | Breakpoints, watches | `core/services/debug_engine.py` |
| **Version Manager** | Component versioning | `core/version.py` |

---

## 🚀 Quick Start

```bash
# Launch TUI
./bin/start_udos.sh

# Check system
SHAKEDOWN

# Check versions
python -m core.version check

# Run tests
pytest core/tests/ -v
```

---

## 📂 Directory Structure

```
uDOS/
├── core/              # TUI runtime (offline-first)
├── wizard/            # Production server (port 8765)
├── extensions/        # API + Transport
├── docs/              # Engineering docs (canonical)
├── knowledge/         # Survival/skills knowledge base
├── library/           # Tool container definitions
├── memory/            # User data, logs (gitignored)
├── dev/               # Private submodule (goblin, empire, app, tests)
└── .archive/          # Historical snapshots (gitignored)
```

---

## 🔀 Submodule Workflow

```bash
# Update private submodule
cd dev && git pull origin main && cd ..
git add dev && git commit -m "Update dev submodule"

# Push both
git push                    # Public
cd dev && git push && cd .. # Private
```

---

## ✅ Testing

```bash
source .venv/bin/activate
SHAKEDOWN                      # 47 system tests
pytest core/tests/ -v          # Unit tests
pytest dev/tests/ -v           # Integration tests
```

---

## 📖 Additional Resources

- **Full docs:** [docs/README.md](../docs/README.md)
- **Roadmap:** [docs/development-streams.md](../docs/development-streams.md)
- **Architecture decisions:** `docs/decisions/ADR-*.md`
- **API docs:** `docs/specs/`

---

_Last Updated: 2026-01-29_
_Version: Simplified v2.0_
_Archive: `.archive/2026-01-29-docs/copilot-instructions-verbose.md`_
