# uDOS Architecture

**Version:** Alpha v1.0.0.64  
**Last Updated:** 2026-01-07

---

## Overview

uDOS is a Python-venv OS layer designed as an overlay for Tiny Core Linux. This document describes the directory structure and component organization.

---

## Root Directory

```
uDOS/
├── core/                    # Core TUI system (Python)
├── app/                     # uCode Markdown App (Tauri/Svelte)
├── wizard/                  # Wizard Server (always-on AI)
├── extensions/              # Extension modules
│   ├── api/                 # REST/WebSocket API
│   └── transport/           # Network transports
├── knowledge/               # Knowledge bank (231+ articles)
├── library/                 # Cloned third-party repos (gitignored)
├── packages/                # Distribution packages
├── memory/                  # User workspace (gitignored)
├── dev/                     # Development tools
├── wiki/                    # Documentation wiki
├── bin/                     # CLI launchers
├── .github/                 # GitHub config + Copilot instructions
└── .vscode/                 # VS Code settings
```

---

## Component Versions

Each major component maintains its own `version.json`:

| Component | Location | Description |
|-----------|----------|-------------|
| **Core** | `core/version.json` | TUI, uPY, MeshCore base |
| **API** | `extensions/api/version.json` | REST API, WebSocket |
| **App** | `app/version.json` | uCode Markdown App (Tauri) |
| **Wizard** | `wizard/version.json` | Wizard Server, Gmail relay |
| **Transport** | `extensions/transport/version.json` | MeshCore, Audio, QR |
| **Knowledge** | `knowledge/version.json` | Timestamp/contributor based |

---

## Core System (`/core`)

```
core/
├── version.json             # Core version
├── version.py               # Version manager
├── config.py                # Global configuration
├── uDOS_commands.py         # Command router
├── udos_core.py             # Core engine
├── uDOS_main.py             # Entry point
├── commands/                # Command handlers (92+)
│   ├── file_handler.py
│   ├── backup_handler.py
│   ├── shakedown_handler.py
│   ├── repair_handler.py
│   └── ...
├── services/                # Core services (140+)
│   ├── logging_manager.py   # Canonical logger
│   ├── file_picker_service.py
│   ├── state_manager.py
│   └── theme/               # Theme system
├── ui/                      # TUI components
│   ├── viewport.py
│   ├── pager.py
│   └── ...
├── security/                # Security infrastructure
│   ├── capabilities.yaml
│   ├── roles.yaml
│   ├── key_store.py
│   └── audit_logger.py
├── runtime/                 # Script interpreters
│   └── upy/                 # uPY scripting
├── input/                   # Input handlers
└── output/                  # Output formatters
```

---

## uCode Markdown App (`/app`)

Tauri-based desktop application with Svelte frontend.

```
app/
├── version.json             # App version
├── package.json             # Node dependencies
├── plugin.json              # Plugin manifest
├── src/                     # Svelte frontend
│   ├── lib/                 # Components
│   ├── routes/              # SvelteKit routes
│   └── app.html
├── src-tauri/               # Rust backend
│   ├── Cargo.toml
│   ├── src/
│   │   ├── main.rs
│   │   ├── commands.rs
│   │   └── lib.rs
│   └── tauri.conf.json
├── lib/                     # Embedded libraries (gitignored)
│   ├── typo/                # Typo editor
│   ├── marp/                # Marp presentations
│   └── gtx-form/            # Form builder
├── static/                  # Static assets
└── build/                   # Build output
```

---

## Wizard Server (`/wizard`)

Always-on server for web access, AI pipelines, and Gmail relay. **Realm B only.**

```
wizard/
├── version.json             # Wizard version
├── server.py                # Entry point
├── config/
│   ├── ai_costs.json        # Provider costs
│   └── ai_keys.template.json
├── providers/               # AI providers
│   ├── anthropic_client.py
│   ├── gemini_client.py
│   ├── openrouter_client.py
│   └── devstral_client.py
├── services/                # Server services
│   ├── gmail_relay.py
│   ├── web_scraper.py
│   └── ai_router.py
├── tools/                   # MCP tools
├── web/                     # Web interface
└── library/                 # Cloned AI repos (gitignored)
    └── home-assistant/
```

---

## Extensions

### API Server (`/extensions/api`)

REST and WebSocket API for TUI/App communication.

```
extensions/api/
├── version.json             # API version
├── server.py                # Entry point
├── routes/                  # Route handlers (18 modules)
│   ├── dashboard.py
│   ├── debug.py
│   ├── docs.py
│   ├── files.py
│   ├── knowledge.py
│   ├── wizard.py
│   └── ...
├── services/                # API services
└── websocket/               # WebSocket handlers
```

### Transport (`/extensions/transport`)

Network transport layers following uDOS transport policy.

```
extensions/transport/
├── version.json             # Transport version
├── policy.yaml              # Transport rules
├── validator.py             # Policy enforcement
├── meshcore/                # Primary P2P mesh
├── audio/                   # Acoustic packets
│   ├── codec.py
│   ├── transmitter.py
│   ├── receiver.py
│   └── groovebox.py         # MML synthesizer
└── qr/                      # Visual data transfer
```

---

## Knowledge Bank (`/knowledge`)

Offline-first survival and technical knowledge (231+ articles).

```
knowledge/
├── version.json             # Knowledge version
├── KNOWLEDGE-SYSTEM.md      # System documentation
├── checklists/              # Actionable checklists
├── survival/                # Survival guides
├── medical/                 # First aid
├── food/                    # Food & foraging
├── water/                   # Water sourcing
├── shelter/                 # Shelter building
├── fire/                    # Fire starting
├── navigation/              # Orientation
├── communication/           # Signal & comms
├── tech/                    # Technical guides
├── tools/                   # Tool making
├── making/                  # DIY & crafts
├── skills/                  # General skills
├── well-being/              # Mental health
├── community/               # Group dynamics
└── reference/               # Quick reference
```

---

## Library (`/library`)

Cloned third-party repositories. **Gitignored.**

```
library/
├── README.md                # Index of libraries
├── typo/                    # Typo markdown editor
├── marp/                    # Marp presentations
├── gtx-form/                # Typeform-style forms
├── gemini-cli/              # Google Gemini CLI
├── micro/                   # Micro text editor
├── piper/                   # TTS engine
├── nethack/                 # NetHack game
├── meshcore/                # MeshCore reference
├── tinycore/                # Tiny Core Linux
├── markdown-to-pdf/         # PDF generation
├── url-to-markdown/         # Web scraping
└── songscribe/              # Music notation
```

---

## User Workspace (`/memory`)

User files, settings, and logs. **Gitignored.**

```
memory/
├── settings.json            # User preferences
├── stacks/                  # Installed stacks
├── logs/                    # Application logs
│   ├── session-commands-YYYY-MM-DD.log  # PRIMARY DEBUG
│   ├── api_server.log
│   └── system-YYYY-MM-DD.log
├── docs/                    # User documents
├── drafts/                  # Work in progress
├── sandbox/                 # Experiments
└── scripts/                 # User scripts
```

---

## Two-Realm Architecture

### Realm A: User Device Mesh (Default)
- No internet dependency
- Device-to-device via private transports
- Runs: Core, App, Transport

### Realm B: Wizard Server (Explicit)
- May access web
- Communicates via private transports only
- Runs: Wizard, Gmail relay, AI pipelines

---

## Transport Policy

### Private Transports (Commands + Data)
- **MeshCore** - Primary P2P/mesh
- **Bluetooth Private** - Paired devices
- **NFC** - Physical contact
- **QR Relay** - Visual data transfer
- **Audio Relay** - Acoustic packets

### Public Signal Channels (No Data)
- **Bluetooth Public** - Beacons/presence only

---

## Related Documentation

- [Vision](./VISION.md) - What uDOS is and why
- [Commands](./commands/README.md) - Complete command reference
- [TinyCore Stack](./tinycore/README.md) - Installation & deployment
- [Contributing](./contributing/README.md) - How to help

---

*This document is maintained in the [uDOS Wiki](./README.md).*
