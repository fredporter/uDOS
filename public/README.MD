# uDOS - Offline-First OS Layer for Knowledge Systems 🌍

**uDOS** is a modular, offline-first Python/TypeScript runtime for building knowledge systems, TUI applications, and distributed tools. It's designed for air-gapped environments, minimal installations, and mesh networking.

**Current Status**: ✅ **Alpha v1.0.6.0** (January 18, 2026)

---

## 🚀 Quick Start

**IMPORTANT:** When you clone this repository, the module paths do NOT include `public/`. Use paths like `wizard.server`, not `public.wizard.server`.

```bash
# Clone repository
git clone https://github.com/fredporter/uDOS-core.git
cd uDOS-core

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run Wizard Server (always-on services)
python -m wizard.server

# See INSTALLATION.md for full setup guide and troubleshooting
```

---

## 📦 What's Inside

### Core Components

| Component      | Purpose                                       | Status      |
| -------------- | --------------------------------------------- | ----------- |
| **Wizard**     | Always-on server (APIs, webhooks, AI routing) | ✅ v1.1.0.0 |
| **Extensions** | Modular features (API, Transport, VS Code)    | ✅ v1.0.1.0 |
| **Core**       | TypeScript runtime for iOS/Android            | ✅ v1.1.0   |
| **App**        | Tauri+Svelte desktop client                   | ✅ v1.0.3.0 |
| **Knowledge**  | Curated knowledge base & guides               | ✅ Growing  |

### Directory Structure

```
public/
├── wizard/              # Production server (Python, port 8765)
├── extensions/          # Public plugins & APIs
│   ├── api/            # REST/WebSocket server
│   ├── transport/      # MeshCore, Bluetooth, NFC, QR, Audio
│   └── vscode/         # VS Code extension
├── knowledge/          # Knowledge base (guides, specs, docs)
├── library/            # Assets, fonts, icons
├── distribution/       # Release artifacts & packages
├── docs/               # Public documentation (stub)
├── wiki/               # Public wiki (stub)
├── requirements.txt    # Python dependencies
└── LICENSE.txt         # MIT License
```

---

## 🎯 Core Features

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
- `POST /api/v1/devices/auth` - Device authentication
- `GET /api/v1/ai/route` - Model routing
- `GET /api/v1/extensions/` - Extension repository

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

| Version  | Date         | Focus                                 |
| -------- | ------------ | ------------------------------------- |
| v1.0.6.0 | Jan 18, 2026 | Public repo cleanup                   |
| v1.0.5.0 | Jan 17, 2026 | Offline AI, SVG graphics              |
| v1.0.4.0 | Jan 16, 2026 | Goblin Dev Server, GitHub integration |
| v1.0.3.0 | Jan 15, 2026 | TypeScript runtime, Binder system     |

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
