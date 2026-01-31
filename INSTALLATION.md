# uDOS Public Distribution - Installation Guide

This is the public mirror of uDOS. This folder contains the distributable components ready to install and run standalone.

## What's Included

- `wizard/` — AI routing server and services (port 8765)
- `extensions/` — API, transport, VSCode language support
- `knowledge/` — Knowledge bank articles
- `docs/` — Engineering documentation
- `requirements.txt` — All Python dependencies

## Installation

### 1. Clone the Public Repository

```bash
git clone https://github.com/fredporter/uDOS-core.git
cd uDOS-core
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `prompt_toolkit` (already listed in `requirements.txt`) powers the SmartPrompt enhanced mode. Always launch uDOS through the provided launcher or `python uDOS.py` from a terminal where both stdin and stdout are TTYs so the TAB-based command selector, history keys, and predictor suggestions remain active.

### 4. Launch Components

uDOS uses a unified launcher system across all components. All launchers delegate to `bin/udos-common.sh` for consistent behavior.

### Available Launchers

| Component         | macOS Finder (.command)                | Terminal (CLI .sh)                             |
| ----------------- | -------------------------------------- | ---------------------------------------------- |
| **Core TUI**      | `bin/Launch-uDOS-TUI.command`          | `bin/start_udos.sh` or `bin/start-core-tui.sh` |
| **Wizard Server** | `bin/Launch-Wizard-Server.command`     | `bin/start-wizard-server.sh`                   |
| **Wizard TUI**    | —                                      | `bin/start-wizard-tui.sh`                      |
| **App Dev**       | `app/bin/Launch uMarkdown-dev.command` | `app/bin/start-app-dev.sh`                     |
| **Goblin Dev**    | `dev/bin/Launch-Goblin-Dev.command`    | `dev/bin/start-goblin-dev.sh`                  |
| **Empire Dev**    | `dev/bin/Launch-Empire-Server.command` | `dev/bin/start-empire-dev.sh`                  |

### Quick Start

**Core TUI (recommended for testing):**

```bash
./bin/start_udos.sh
```

**Wizard Server (production services):**

```bash
./bin/start-wizard-server.sh
```

**macOS users:** Double-click any `.command` file in Finder, or use `open bin/Launch-*.command` from terminal.

**All launchers automatically:**

- Activate Python virtual environment
- Install missing dependencies
- Run self-healing diagnostics
- Detect and resolve port conflicts

---

## Module Structure & Direct Execution

If you prefer to run services directly without launchers:

### Core TUI

```bash
source .venv/bin/activate
python uDOS.py
```

### Wizard Server (Alternative to Launcher)

```bash
source .venv/bin/activate
python -m wizard.server --port 8765
```

Wizard Server provides:

- REST API on port 8765
- Interactive web dashboard
- WebSocket support
- AI model routing (local-first with optional cloud burst)

### API Extension

```bash
source .venv/bin/activate
python -m extensions.api.server
# Starts on port 5001
```

## Directory Structure

After cloning, your directory structure will be:

```text
uDOS/
├── bin/                    # Launcher scripts (unified system)
│   ├── udos-common.sh     # Shared launcher library
│   ├── start_udos.sh      # Core TUI launcher
│   ├── start-wizard-server.sh
│   └── Launch-*.command   # macOS Finder launchers
├── core/                   # Core TUI runtime
├── wizard/                 # Wizard Server (port 8765)
├── extensions/             # API, transport, VSCode extension
├── docs/                   # Documentation
├── dev/                    # Private submodule (dev tools)
├── memory/                 # Local logs and user data
└── requirements.txt        # Python dependencies
```

## Troubleshooting

### ModuleNotFoundError: No module named 'wizard'

Make sure:

1. You're in the cloned `uDOS-core/` directory
2. Virtual environment is activated (`source venv/bin/activate`)
3. You've run `pip install -r requirements.txt`
4. You're using the correct module path (WITHOUT `public/`)

### Launcher Not Found or Permission Denied

**Problem:** `command not found: ./bin/start_udos.sh` or permission error

**Solution:** Make scripts executable:

```bash
chmod +x bin/*.sh
chmod +x bin/Launch-*.command
chmod +x dev/bin/*.sh
chmod +x app/bin/*.sh
```

### Virtual Environment Not Found

```bash
# Recreate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## For Private Development

If you want the full development environment with the desktop app and experimental features:

```bash
# Clone with private submodule (requires access)
git clone --recurse-submodules git@github.com:fredporter/uDOS.git
cd uDOS
```

The private `/dev/` submodule includes:

- `uMarkdown-app` — Desktop app source (Tauri + Svelte), mounted at `/app`
- `/dev/goblin/` — Experimental dev server
- `/dev/empire/` — CRM system
- `/dev/groovebox/` — Music production tools
- Full development tools and CI/CD

## Next Steps

1. Install and activate the virtual environment
2. Run `python -m wizard.server` to start the server
3. Check `wizard/README.md` for Wizard Server configuration
4. See `docs/` for architecture and development guides

---

**Last Updated:** January 24, 2026
**Current Status:** v1.0.7 (Active Development)
**Component Versions:**

- Core: v1.1.1.1 (Dev)
- Wizard: v1.1.0.2 (Alpha)
- API: v1.0.1.0 (Alpha)
- App: v1.0.6.1 (Alpha)
- Transport: v1.0.1.0

**Private Dev Submodule:** <https://github.com/fredporter/uDOS-dev>
