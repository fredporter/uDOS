# GitHub Copilot Instructions for uDOS

**uDOS** is an offline-first, distributed OS layer combining Python TUI (Alpine Linux primary, multi-OS support), Tauri desktop GUI, custom uPY scripting, and cloud-optional services.

---

## 🏗️ Repository Structure (IMPORTANT)

**This is a PUBLIC repo with a PRIVATE submodule:**

| Location | Visibility | Contents |
|----------|------------|----------|
| **Root** (this repo) | PUBLIC | Core, Wizard, Extensions, Docs, Knowledge, Library |
| **/dev** (submodule) | PRIVATE | Goblin, Empire, App, Groovebox, Tests, Tools |
| **/memory** | LOCAL | User data, logs, credentials (never committed) |

**Submodule setup:**
```bash
git clone --recurse-submodules git@github.com:fredporter/uDOS.git
# Or if already cloned:
git submodule update --init --recursive
```

---

## 📚 Documentation Spine

**Primary reference (check these first):**

| Document | Purpose |
|----------|---------|
| [AGENTS.md](../AGENTS.md) | **Lean rules** for fast dev rounds (verbose archived) |
| [docs/README.md](../docs/README.md) | Engineering entry point |
| [docs/development-streams.md](../docs/development-streams.md) | Current priorities (Now/Next/Later) |

**Subsystem instructions** (when modifying specific components):
- [instructions/core.instructions.md](instructions/core.instructions.md) — TUI, handlers, services
- [instructions/app.instructions.md](instructions/app.instructions.md) — Tauri app, formats (public scaffold at /app, source in /app/src)
- [instructions/wizard.instructions.md](instructions/wizard.instructions.md) — Server, AI routing
- [instructions/extensions.instructions.md](instructions/extensions.instructions.md) — API, transport

---

## 🎯 Core Principles

1. **Offline-first** — Default: no internet required. Cloud features explicit and optional.
2. **Modular** — Thin handlers, shared services, clean boundaries. Core → API → Transport → UI.
3. **Versioned** — Each component independently versioned. **Never hardcode** version strings.
4. **Documented** — Canonical in `/docs/`, drafts in `.dev/`, archive in `.archive/`
5. **Policy-driven** — Transport rules, architectural boundaries enforced consistently.

---

## 📦 Component Versioning

Each component independently versioned via `version.json`:

```bash
python -m core.version check    # Check all versions
python -m core.version show     # Dashboard
python -m core.version bump core build  # Bump specific component
```

**Rule:** Never hardcode version strings. Use version manager.

---

## 📁 Directory Structure

**PUBLIC (root repo):**
- `core/` — TUI system, handlers, services (TypeScript runtime)
- `wizard/` — Production server, AI routing
- `extensions/` — API, Transport (independent components)
- `docs/` — Engineering spine (canonical truth)
- `knowledge/` — Survival/skills knowledge base
- `library/` — Tool container definitions

**PRIVATE (/dev submodule):**
- `dev/goblin/` — Experimental dev server
- `dev/empire/` — CRM system
- `uMarkdown-app` — Desktop app source (Tauri + Svelte), mounted at `/app/src`
- `dev/groovebox/` — Music production tools
- `dev/tests/` — Integration tests
- `dev/tools/` — Development utilities

**LOCAL (untracked):**
- `memory/` — User data, logs, credentials
- `.dev/` — Active drafts (gitignored)
- `.archive/` — Version history (gitignored)

---

## 🔒 Transport Policy (Non-Negotiable)

### Private Transports (Commands + Data Allowed)

- **MeshCore** - Primary P2P/mesh
- **Bluetooth Private** - Paired devices
- **NFC** - Physical contact
- **QR Relay** - Visual data transfer
- **Audio Relay** - Acoustic packets

### Public Signal Channels (No Data Ever)

- **Bluetooth Public** - Beacons/presence only
- NEVER carry uDOS data or commands

---

## 📝 Logging System

**Canonical Logger:** `core.services.logging_manager.get_logger()`

```python
from core.services.logging_manager import get_logger

logger = get_logger('system-startup')
logger.info('[LOCAL] uDOS starting...')
```

**Primary Debug Log:** `memory/logs/session-commands-YYYY-MM-DD.log` — CHECK THIS FIRST for TUI errors

---

## 🧪 Key Systems

| System | Purpose | File |
|--------|---------|------|
| **ShakedownHandler** | System validation (141 tests, 99.3% pass) | `core/commands/shakedown_handler.py` |
| **RepairHandler** | Self-healing, git pull, upgrades | `core/commands/repair_handler.py` |
| **Version Manager** | Independent component versioning | `core/version.py` |
| **DebugEngine** | Breakpoints, watch lists, call stacks | `core/services/debug_engine.py` |

---

## 📚 Library Structure

**`/library/`** — Tool container definitions (PUBLIC, tracked)
- `marp/`, `micro/`, `typo/`, etc. — Container definitions (container.json + setup scripts)
- Only `container.json`, setup scripts (`.sh`, `.py`), and docs tracked; cloned repos ignored
- Distributed via public repo

**`/dev/library/`** — Local reference clones (PRIVATE, gitignored)
- `gtx-form/`, `home-assistant/`, etc. — External repos cloned locally for development
- Only setup scripts and docs tracked; full cloned repos ignored locally
- Reference copies for testing before promotion
- Part of private submodule

**Promotion Pattern:** Test cloned repo in `/dev/library/` → Create container definition in `/library/` → Commit definition only → Distribute

---

## 🔧 Development Workflow

### Version Bump Flow

```bash
# 1. Make changes
# 2. Test
python -m core.version check

# 3. Bump version
python -m core.version bump core build

# 4. Commit
git add -A && git commit -m "core v1.0.0.65: description"
```

### Submodule Workflow

```bash
# Update private submodule
cd dev && git pull origin main && cd ..
git add dev && git commit -m "Update dev submodule"

# Push both repos
git push                    # Push public
cd dev && git push && cd .. # Push private
```

---

## 🗺️ Roadmap

See `dev/roadmap/ROADMAP.md` for current development priorities.

---

## 🧪 Testing

```bash
# Activate venv
source .venv/bin/activate

# Check versions
python -m core.version check

# Run shakedown (47 tests)
SHAKEDOWN

# Run pytest
pytest dev/tests/ -v
```

---

## 🚀 Quick Commands

```bash
# Launch TUI
bin/start_udos.sh

# Activate Dev Mode (via Wizard)
./bin/start_udos.sh
> DEV MODE activate

# Or via REST API
curl -X POST http://localhost:8765/api/v1/dev/activate

# Self-healing
REPAIR --pull        # Git sync
REPAIR --upgrade-all # Update all
```

---

*Last Updated: 2026-01-21*
*Version: Alpha v1.0.2.0*
*Structure: Public root + Private /dev submodule*
