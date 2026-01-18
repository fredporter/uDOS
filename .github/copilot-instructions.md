# GitHub Copilot Instructions for uDOS

**uDOS** is an offline-first, distributed OS layer combining Python TUI (Tiny Core Linux), Tauri desktop GUI, custom uPY scripting, and cloud-optional services.

---

## 📚 Documentation Spine

**Primary reference (check these first):**

| Document | Purpose |
|----------|---------|
| [AGENTS.md](../AGENTS.md) | How work is done (architecture, policies, tooling) |
| [docs/_index.md](../docs/_index.md) | Engineering entry point |
| [docs/roadmap.md](../docs/roadmap.md) | Current priorities (Now/Next/Later) |

**Subsystem instructions** (when modifying specific components):
- [.github/instructions/core.instructions.md](.github/instructions/core.instructions.md) — TUI, handlers, services
- [.github/instructions/app.instructions.md](.github/instructions/app.instructions.md) — Tauri app, formats
- [.github/instructions/wizard.instructions.md](.github/instructions/wizard.instructions.md) — Server, AI routing
- [.github/instructions/extensions.instructions.md](.github/instructions/extensions.instructions.md) — API, transport

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

## � Directory Structure

**Workspace roots** (multi-root in VS Code):
- `core/` — TUI system, handlers, services
- `app-beta/` — Tauri + Svelte desktop app (v1.0.2.1)
- `app/` — Future implementations (iOS, native macOS, etc)
- `extensions/` — API, Transport (independent components)
- `wizard/` — Always-on server, AI routing

**Development** (see AGENTS.md for details):
- `/docs/` — Engineering spine (canonical truth)
- `docs/devlog/` — Chronological work notes
- `docs/decisions/` — Architecture Decision Records (ADRs)
- `docs/specs/` — Technical specifications
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

---

## 🔧 Development Workflow

### Version Bump Flow

\`\`\`bash
# 1. Make changes
# 2. Test
python -m core.version check

# 3. Bump version
python -m core.version bump core build

# 4. Commit
git add -A && git commit -m "core v1.0.0.65: description"
\`\`\`

---

## 🗺️ Roadmap

See \`dev/roadmap/ROADMAP.md\` for current development priorities.

---

## 🧪 Testing

\`\`\`bash
# Activate venv
source .venv/bin/activate

# Check versions
python -m core.version check

# Run shakedown (47 tests)
SHAKEDOWN

# Run pytest
pytest memory/tests/ -v
\`\`\`

---

## 🚀 Quick Commands

\`\`\`bash
# Launch TUI
bin/start_udos.sh

# Dev Mode (API + Dashboard)
bin/Launch-Dev-Mode.command

# Launch Tauri Dev
bin/Launch-Tauri-Dev.command

# Self-healing
REPAIR --pull        # Git sync
REPAIR --upgrade-all # Update all
\`\`\`

---

*Last Updated: 2026-01-07*
*Version: Alpha v1.0.0.64*
