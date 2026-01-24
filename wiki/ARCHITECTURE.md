# uDOS Architecture

**Version:** Core v1.0.0.65
**Last Updated:** 2026-01-24
**Status:** Active Standard

uDOS is a Python-based OS layer designed as an overlay for Tiny Core Linux. This document describes the directory structure and component organization.

---

## Overview

```
uDOS/
├── core/                    # Core TUI system (Python)
├── app/                     # uCode Markdown App (Tauri/Svelte)
├── wizard/                  # Wizard Server (always-on AI services)
├── extensions/              # Extension modules
│   ├── api/                 # REST/WebSocket API
│   └── transport/           # Network transports
├── knowledge/               # Knowledge bank (240+ articles)
├── library/                 # Third-party libraries (gitignored)
├── memory/                  # User workspace (gitignored)
├── wiki/                    # Public documentation
├── docs/                    # Engineering documentation
├── bin/                     # CLI launchers
└── .github/                 # GitHub & CI configuration
```

---

## Component Versions

Each major component maintains independent versioning:

| Component     | Location                            | Current  | Purpose                      |
| ------------- | ----------------------------------- | -------- | ---------------------------- |
| **Core**      | `core/version.json`                 | v1.1.0.0 | TUI, uPY, handlers, services |
| **API**       | `extensions/api/version.json`       | v1.1.0.0 | REST/WebSocket API           |
| **App**       | `app/version.json`                  | v1.0.6.1 | Tauri desktop client         |
| **Wizard**    | `wizard/version.json`               | v1.1.0.2 | Server, AI routing, relays   |
| **Transport** | `extensions/transport/version.json` | v1.0.1.0 | MeshCore, audio, QR, NFC     |
| **Knowledge** | `knowledge/version.json`            | v1.0.0.0 | Survival guides, reference   |

**Version Format:** `MAJOR.MINOR.PATCH.BUILD`

---

## Core System (`core/`)

**Python offline-first TUI runtime**

```
core/
├── version.json             # Version metadata
├── version.py               # Version manager
├── config.py                # Global configuration
├── uDOS_commands.py         # Command router
├── udos_core.py             # Core engine
├── uDOS_main.py             # Entry point
├── commands/                # Command handlers (92+ commands)
│   ├── file_handler.py
│   ├── backup_handler.py
│   ├── shakedown_handler.py
│   ├── repair_handler.py
│   └── ...
├── services/                # Core services (140+ services)
│   ├── logging_manager.py   # ✅ Canonical logger
│   ├── file_service.py
│   ├── state_manager.py
│   └── theme/
├── ui/                      # TUI components
│   ├── viewport.py
│   ├── pager.py
│   └── ...
├── security/                # Security
│   ├── capabilities.yaml
│   ├── roles.yaml
│   └── audit_logger.py
├── runtime/                 # Interpreters
│   └── upy/                 # uPY scripting language
└── input/output/            # I/O handlers
```

**Key Features:**

- No dependencies on cloud connectivity
- 92+ command handlers
- 140+ core services
- uPY scripting language interpreter
- Theme system
- Security and audit logging

---

## uCode Markdown App (`app/`)

**Tauri-based desktop client** — Renders five markdown formats

```
app/
├── version.json             # App version
├── src/                     # Svelte frontend
│   ├── lib/                 # Components
│   ├── routes/              # SvelteKit routes
│   └── app.html
├── src-tauri/               # Rust backend
│   ├── Cargo.toml
│   └── src/
├── bin/                     # Dev launchers
└── docs/                    # Migration notes
```

**Markdown Formats:**

1. **uCode** (`.ucode.md`) — Executable with uPY runtime
2. **Story** (`.story.md`) — Interactive narratives
3. **Marp** (`.marp.md`) — Full-screen presentations
4. **Guide** (`.guide.md`) — Knowledge articles
5. **Config** (`.config.md`) — Configuration documents

**Status:** v1.0.6.1 (Alpha)

---

## Wizard Server (`wizard/`)

**Always-on service layer** — Optional, explicit activation

```
wizard/
├── version.json             # Wizard version
├── server.py                # Entry point
├── config/                  # Configuration
├── providers/               # AI providers
│   ├── anthropic_client.py
│   ├── gemini_client.py
│   ├── openrouter_client.py
│   └── ollama_local.py
├── services/                # Server services
│   ├── gmail_relay.py       # Gmail integration
│   ├── ai_router.py         # Model routing
│   └── rate_limiter.py
├── tools/                   # MCP tools
└── extensions/              # Wizard-specific extensions
```

**Capabilities:**

- AI model routing (local-first, optional cloud burst)
- Gmail relay (Wizard-only)
- Web scraping & API integration
- Cost tracking & quota management
- Device session management
- Plugin repository

**Status:** v1.1.0.2 (Stable, Production)

---

## Extensions

### API Server (`extensions/api/`)

**REST and WebSocket API** for TUI/App communication

```
extensions/api/
├── version.json             # API version
├── server.py                # Entry point
├── routes/                  # Route handlers (18 modules)
│   ├── files.py
│   ├── knowledge.py
│   ├── ai.py
│   └── ...
└── services/                # API services
```

**Status:** v1.1.0.0 (Alpha)

### Transport (`extensions/transport/`)

**Network transport layers** — Private transports only

```
extensions/transport/
├── version.json
├── policy.yaml              # ⚠️ Transport policy (non-negotiable)
├── validator.py             # Policy enforcement
├── meshcore/                # Primary P2P mesh
├── audio/                   # Acoustic data transfer
├── qr/                      # Visual QR relay
├── nfc/                     # NFC contact
└── bluetooth/               # Private pairing
```

**Transport Tiers:**

**Private (Commands + Data Allowed):**

- MeshCore - Primary P2P/mesh
- Bluetooth Private - Paired devices
- NFC - Physical contact
- QR Relay - Visual data transfer
- Audio Relay - Acoustic packets

**Public Signal Only (NO DATA):**

- Bluetooth Public - Beacons/presence ONLY

**Status:** v1.0.1.0 (Alpha)

---

## Knowledge Bank (`knowledge/`)

**Offline-first survival and technical knowledge** — 240+ articles, read-only distribution

```
knowledge/
├── version.json
├── survival/                # Fire, water, shelter, food
├── medical/                 # First aid, health
├── communication/           # Signals, messaging
├── tech/                    # Technology guides
├── skills/                  # General skills
├── navigation/              # Orientation, maps
├── tools/                   # Tool making
├── food/                    # Foraging, cooking
├── water/                   # Sourcing, purification
├── shelter/                 # Building, structures
├── fire/                    # Fire starting
└── reference/               # Checklists, quick ref
```

**Updates:** Distributed with software releases, versioned independently

---

## User Workspace (`memory/`)

**Personal data, configuration, logs** — Gitignored, never uploaded without consent

```
memory/
├── user.json                # Profile & settings
├── state.json               # Session state
├── logs/                    # Application logs
│   └── session-commands-YYYY-MM-DD.log  ← PRIMARY DEBUG LOG
├── docs/                    # User documents
├── ucode/                   # User scripts
├── contributions/           # Wiki submissions
└── saves/                   # Game checkpoints
```

**Important:** All user data stays local. Mesh sync available on request.

---

## Two-Realm Architecture

### Realm A: User Device Mesh (Default)

- ✅ No internet dependency
- ✅ Device-to-device via **private transports only**
- ✅ Runs: Core, App, Transport extensions

### Realm B: Wizard Server (Explicit Opt-In)

- ⚠️ May access web/cloud services
- ✅ Communicates with devices via private transports only
- ✅ Runs: Wizard, AI routing, Gmail relay, web tools

**Rule:** Wizard never exposes devices to the internet.

---

## Transport Policy (Non-Negotiable)

See [extensions/transport/policy.yaml](../extensions/transport/policy.yaml)

```
PRIVATE TRANSPORTS (Commands + Data Allowed):
- MeshCore      → Primary mesh
- Bluetooth Priv → Paired devices
- NFC           → Physical contact
- QR Relay      → Visual transfer
- Audio Relay   → Acoustic packets

PUBLIC SIGNALS (NO DATA EVER):
- Bluetooth Pub → Beacons/presence only
  ⚠️ NEVER carry commands or data
```

**Logging Tags:**

```
[LOCAL]   = Device operation
[MESH]    = MeshCore
[BT-PRIV] = Bluetooth Private
[BT-PUB]  = Bluetooth Public (signal only!)
[NFC]     = NFC contact
[QR]      = QR relay
[AUD]     = Audio transport
[WIZ]     = Wizard operation
```

---

## Directory Organization

| Location       | Type    | Purpose                       |
| -------------- | ------- | ----------------------------- |
| `/core/`       | System  | Python TUI runtime            |
| `/app/`        | System  | Desktop client                |
| `/wizard/`     | System  | Always-on server              |
| `/extensions/` | System  | API, Transport, etc.          |
| `/knowledge/`  | System  | Read-only guides              |
| `/library/`    | Cache   | Cloned libraries (gitignored) |
| `/memory/`     | User    | Workspace (gitignored)        |
| `/wiki/`       | Docs    | Public documentation          |
| `/docs/`       | Docs    | Engineering spine             |
| `/bin/`        | Scripts | Launchers                     |
| `/.github/`    | Config  | GitHub, CI, Copilot           |

---

## Data Classification

### System Data (Read-Only, Distributed)

- `core/` — Python modules
- `knowledge/` — Global knowledge
- `mapdata/` — Pregenerated maps
- `extensions/` — API, transport, tools

**Update:** Software releases

### User Data (Read-Write, Local)

- `memory/` — All user files
- `memory/contributions/` — Wiki submissions
- `memory/mapdata/` — User discoveries

**Update:** Never uploaded without consent

---

## Related Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — How to contribute
- **[STYLE-GUIDE.md](STYLE-GUIDE.md)** — Code standards
- **[VISION.md](VISION.md)** — Project philosophy
- **[architecture/](architecture/)** — Detailed specs
- **[../AGENTS.md](../AGENTS.md)** — Development guidelines
- **[../docs/](../docs/)** — Engineering docs

---

**Status:** Active Architecture
**Repository:** https://github.com/fredporter/uDOS
**License:** [LICENSE.txt](../LICENSE.txt)
