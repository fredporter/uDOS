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

### 4. Run Services

#### Option A: Wizard Server (always-on services)

```bash
python -m wizard.server
# Starts on port 8765
# Access: http://localhost:8765
```

#### Option B: Dev Mode (via Wizard Server)

```bash
# Start Wizard Server first
python -m wizard.server &

# Then activate dev mode in TUI
./bin/start_udos.sh
> DEV MODE activate

# Or use REST API
curl -X POST http://localhost:8765/api/v1/dev/activate
```

Dev Mode includes:

- Goblin dev server (localhost:8767)
- Notion sync, task scheduling, runtime executor
- Real-time WebSocket updates
- Full Wizard API access with dev features

#### Option C: API Server

```bash
python -m extensions.api.server
# Starts on port 5001
```

## Module Structure (When Cloned)

After cloning, your directory structure will be:

```text

uDOS-core/
├── wizard/ # Wizard Server (port 8765)
├── extensions/ # API, transport, VSCode extension
├── knowledge/ # Knowledge bank articles
├── docs/ # Documentation
├── requirements.txt # Python dependencies
└── README.md # This file

```

**Key point:** When you run Python from this directory, use module paths WITHOUT `public/` prefix:

✅ Correct:

```bash
python -m wizard.server
python -m extensions.api.server
```

❌ Incorrect (don't do this):

```bash
python -m public.wizard.server     # Won't find anything
```

## Troubleshooting

### ModuleNotFoundError: No module named 'wizard'

Make sure:

1. You're in the cloned `uDOS-core/` directory
2. Virtual environment is activated (`source venv/bin/activate`)
3. You've run `pip install -r requirements.txt`
4. You're using the correct module path (WITHOUT `public/`)

#### Port already in use

Wizard Server defaults to port 8765. If already in use:

```bash
python wizard/cli_port_manager.py conflicts
python wizard/cli_port_manager.py kill :8765
```

## For Private Development

If you want the full development environment with the desktop app and experimental features:

```bash
# Clone with private submodule (requires access)
git clone --recurse-submodules git@github.com:fredporter/uDOS.git
cd uDOS
```

The private `/dev/` submodule includes:

- `uMarkdown-app` — Desktop app source (Tauri + Svelte), mounted at `/app/src`
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

**Last Updated:** January 21, 2026
**Version:** Alpha v1.0.2.0
**Private Dev Submodule:** <https://github.com/fredporter/uDOS-dev>
