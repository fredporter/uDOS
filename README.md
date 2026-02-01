# uDOS - Offline-First OS Layer for Knowledge Systems 🌍

**uDOS** is a modular, offline-first Python/TypeScript runtime for building knowledge systems, TUI applications, and distributed tools. It's designed for air-gapped environments, minimal installations, and mesh networking.

**Primary Platform**: 🐧 **Alpine Linux** | **Multi-OS Support**: macOS, Ubuntu, Windows
**Current Status**: ✅ **Alpha v1.0.7** (January 25, 2026)

> 📚 **Documentation Hub:**
> - **👤 Users/Beginners** → [**wiki/START-HERE.md**](wiki/START-HERE.md) (2 min guide)
> - **🛠️ Developers** → [**docs/README.md**](docs/README.md) (specs & architecture)
> - **📖 Full Wiki** → [**wiki/README.md**](wiki/README.md) (all guides)

---

## 🚀 Quick Start

**IMPORTANT:** When you clone this repository, the module paths do NOT include `public/`. Use paths like `wizard.server`, not `public.wizard.server`.

```bash
# Clone repository (includes private submodule)
git clone --recurse-submodules https://github.com/fredporter/uDOS.git
cd uDOS

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### VS Code Workspaces (Optimized for Fast Development)

To avoid Copilot timeouts, use focused workspaces instead of the full workspace:

| Workspace                 | Purpose                       | Folders            | Use When                            |
| ------------------------- | ----------------------------- | ------------------ | ----------------------------------- |
| **uCODE.code-workspace**  | Core TUI development          | Root, Core, Docs   | Building handlers, services, TUI    |
| **Wizard.code-workspace** | Server & API development      | Root, Wizard, Docs | Building APIs, AI routing, webhooks |
| **uDOS.code-workspace**   | Full codebase (large context) | All 8 folders      | Full system exploration/refactoring |

**See [WORKSPACE-SPLIT.md](WORKSPACE-SPLIT.md) for details.**

### Platform Support

| Platform         | Status     | TUI     | Server | GUI  | Notes                           |
| ---------------- | ---------- | ------- | ------ | ---- | ------------------------------- |
| **Alpine Linux** | ✅ Primary | Full    | Full   | —    | Embedded/diskless, apk packages |
| **macOS**        | ✅ Dev     | Full    | Full   | Full | Homebrew, Tauri app             |
| **Ubuntu**       | ✅ Dev     | Full    | Full   | Full | APT packages                    |
| **Windows**      | ✅ Dev     | Limited | Full   | Full | Chocolatey, WSL2 recommended    |

**See [Alpine Installation Guide](docs/howto/alpine-install.md) for Alpine Linux setup.**

### Launch Options

Pick your starting point — each has a dedicated launcher script:

| What You Want                    | Command                         | Port     | Features                                |
| -------------------------------- | ------------------------------- | -------- | --------------------------------------- |
| **Text CLI (recommended first)** | `./bin/start_udos.sh`           | —        | Offline-first, no server needed         |
| **Web Dashboard + APIs**         | `./bin/start_wizard.sh`         | 8765     | Production server, webhooks, AI routing |
| **Dev Experiments**              | `./bin/start_goblin.sh`         | 8767     | Notion sync, runtime execution, tasks   |
| **Desktop App**                  | `cd app && npm run tauri dev`   | —        | GUI with markdown formats               |
| **Everything at once**           | `./bin/Launch-Dev-Mode.command` | Multiple | Full dev environment                    |

**See [QUICKSTART.md](QUICKSTART.md) for detailed launch instructions and options.**

For setup guide and troubleshooting, see [INSTALLATION.md](INSTALLATION.md).

---

## 📦 What's Inside

### Core Components

| Component      | Purpose                                       | Status     |
| -------------- | --------------------------------------------- | ---------- |
| **Wizard**     | Always-on server (APIs, webhooks, AI routing) | ✅ v1.1.0  |
| **Extensions** | Modular features (API, Transport, VS Code)    | ✅ v1.0.1  |
| **Core**       | TypeScript/Python runtime (Alpine-first)      | ✅ v1.1.0  |
| **App**        | Tauri+Svelte desktop client                   | ✅ v1.0.3  |
| **Knowledge**  | Curated knowledge base & guides               | ✅ Growing |

### Directory Structure

```
🏠 uDOS Root (PUBLIC)/
├── core/                      # TypeScript runtime + Python TUI
│   ├── framework/            # Distribution layer (NEW v1.1.0)
│   │   ├── schemas/          # JSON validation schemas
│   │   ├── templates/        # Customization templates
│   │   └── seed/             # Bootstrap data (~5KB)
│   ├── services/             # OS-aware services
│   ├── commands/             # 30+ command handlers
│   ├── os_specific/          # Platform adapters
│   └── tests/                # Test suites
├── wizard/                    # Production server (port 8765)
├── extensions/                # Public plugins & APIs
│   ├── api/                  # REST/WebSocket server
│   ├── transport/            # MeshCore, Bluetooth, NFC, QR, Audio
│   └── vscode/               # VS Code extension
├── memory/                    # User data layer (gitignored)
│   ├── bank/                 # User-customizable data
│   │   ├── ai/              # AI prompts & instructions
│   │   ├── checklists/      # User checklists
│   │   ├── code/            # uCODE scripts
│   │   ├── locations/       # Location database + places
│   │   ├── system/          # System scripts (startup/reboot)
│   │   └── .archive/        # Deprecated content
│   ├── logs/                # Runtime logs
│   └── wizard/              # Wizard server data
├── docs/                     # Engineering documentation
├── knowledge/                # Static reference library (237 entries)
│   ├── _index.json          # Searchable catalog (154KB)
│   ├── fire/, water/, shelter/, tools/, medical/, etc.
│   └── (frontmatter-tagged markdown files)
├── sonic/                    # Device library (Sonic Screwdriver)
├── library/                  # Alpine package definitions
├── distribution/             # Release artifacts
└── LICENSE.txt               # MIT License

🔒 dev/ (PRIVATE SUBMODULE)/
├── goblin/                   # Experimental dev server (port 8767)
├── app/                      # Tauri+Svelte desktop GUI
├── empire/                   # CRM system
├── groovebox/                # Music production tools
├── tests/                    # Integration tests
└── tools/                    # Dev utilities
```

**Three-Tier Architecture** (v1.1.0):
- **TIER 1 - Framework** (`/core/framework/`): Public, git-tracked, distributable
- **TIER 2 - Knowledge** (`/knowledge/`): Static reference library with searchable catalog
- **TIER 3 - Bank** (`/memory/bank/`): User data, P2P syncable, gitignored

---

## 🎯 Core Features

### Alpine Linux (Primary)

- **Lightweight** - Minimal base install (~130 MB)
- **Offline-First** - Default operation without internet
- **Diskless/Live Boot** - Run entirely in RAM with optional persistence (lbu)
- **APK Packages** - Fast, dependency-resolved package management
- **OpenRC Init** - Simple service management

**Setup**: See [Alpine Installation Guide](docs/howto/alpine-install.md)

### Wizard Server (Production)

- **Always-on APIs** - Device auth, sessions, model routing
- **AI Model Routing** - Local (Ollama) + cloud (OpenRouter) burst
- **Webhooks** - GitHub, Notion, Gmail integrations
- **Cost Tracking** - Budget enforcement, quota management
- **Extensible** - Plugin architecture for custom services

### Extensions

- **API Server** - RESTful & WebSocket interfaces
- **Transport Layer** - MeshCore P2P, Bluetooth private, NFC, QR, Audio
- **VS Code Integration** - Language support, snippets, debugging

### Core Runtime (TypeScript)

- **Markdown Execution** - Parse & execute code blocks
- **State Management** - Variables, objects, arrays with persistence
- **Sandboxed** - No file system access, deterministic
- **Mobile-Ready** - Works on iOS/iPadOS, no Python required

### Desktop App (Tauri)

- **5 Markdown Formats** - uCode, Story, Marp, Guide, Config
- **Rich Editing** - Frontmatter, code blocks, graphics
- **Offline-First** - Works without internet
- **Native Feel** - Tauri provides system integration

---

## 🔒 Transport Policy

**Private Transports** (data allowed):

- MeshCore P2P
- Bluetooth (paired)
- NFC (physical contact)
- QR Relay (visual)
- Audio Relay (acoustic packets)

**Public Channels** (beacons only):

- Bluetooth Public (discovery only)

---

## 📚 Documentation

**Start with:**

- [docs/](docs/) - Architecture & guides
- [wiki/](wiki/) - Quick reference & FAQ

**For developers:**

- [wizard/ARCHITECTURE.md](wizard/ARCHITECTURE.md) - System design
- [wizard/README.md](wizard/README.md) - Wizard server guide
- [extensions/README.md](extensions/README.md) - Extension development

**For users:**

- [knowledge/](knowledge/) - User guides and knowledge base

---

## 🛠️ Installation Options

### Lite (Default) - 7.3MB

```bash
git clone https://github.com/fredporter/uDOS-core.git
```

Core + knowledge base only. Perfect for air-gapped systems.

### Full - ~45MB

```bash
git clone --depth=1 https://github.com/fredporter/uDOS-core.git
pip install -r requirements.txt
```

Includes all extensions and tools.

### Development (Full Private Repo)

For TypeScript runtime, iOS/Android apps, and full development tools:

```bash
git clone https://github.com/fredporter/uDOS-dev.git
cd uDOS-dev
python -m core.version check
```

Private repo with full git history.

---

## 🚀 Getting Started

### Run Wizard Server

```bash
python -m public.wizard.server
# Opens on http://localhost:8765
# API docs: http://localhost:8765/docs
```

### Run Core TUI

```bash
python -m core.tui
# Interactive terminal interface
```

### Build Desktop App

```bash
cd ../app  # go to root app folder
npm install
npm run dev
```

### Run Tests

```bash
pytest public/wizard/tests/ -v
# or run full system test
```

---

## 🌐 Key APIs

**Wizard Server (Port 8765)**

- `GET /health` - Health check
- `POST /api/devices/auth` - Device authentication
- `GET /api/ai/route` - Model routing
- `GET /api/extensions/` - Extension repository

**API Server (Port 8000)**

- WebSocket support
- RESTful endpoints
- Real-time subscriptions

**Goblin Dev Server (Port 8767)** - _localhost only_

- Experimental features
- Task scheduling
- Notion sync (testing)

---

## 📋 Version History

| Version | Date         | Highlights                            |
| ------- | ------------ | ------------------------------------- |
| v1.0.6  | Jan 18, 2026 | Public repo cleanup                   |
| v1.0.5  | Jan 17, 2026 | Offline AI, SVG graphics              |
| v1.0.4  | Jan 16, 2026 | Goblin Dev Server, GitHub integration |
| v1.0.3  | Jan 15, 2026 | TypeScript runtime, Binder system     |

---

## 🤝 Contributing

This is an open-source project. Contributions welcome!

**Before contributing:**

1. Read [wizard/ARCHITECTURE.md](wizard/ARCHITECTURE.md)
2. Check [docs/](docs/) for contribution guidelines
3. Follow code style in subsystem READMEs

---

## 📄 License

MIT License - See [LICENSE.txt](LICENSE.txt)

---

## 🔗 Links

- **Public Repo (This)**: https://github.com/fredporter/uDOS-core
- **Private Dev Repo**: https://github.com/fredporter/uDOS-dev
- **Issues**: https://github.com/fredporter/uDOS-dev/issues
- **Discussions**: https://github.com/fredporter/uDOS-dev/discussions

---

**Last Updated:** January 18, 2026
**Status:** Alpha (stable, actively developed)
