# uDOS Quick Start Guide

Get up and running with uDOS in 5 minutes.

**Note:** uDOS is designed as a local Obsidian companion app. We recommend using [Obsidian](https://obsidian.md) as your independent text editor and vault reader. uDOS shares your vault using an open-box format—no sync required!

---

## Prerequisites

- **Python 3.9+** — For Core and Wizard components
- **Node.js 18+** — For App (Tauri + Svelte)
- **Git** — For cloning and submodule management

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/fredporter/uDOS.git
cd uDOS
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**If pip installation hangs or is slow,** install packages in smaller batches:

```bash
# AI providers
pip install google-generativeai openai anthropic

# Google services & auth
pip install google-auth google-auth-oauthlib google-api-python-client

# Core web & HTTP
pip install fastapi uvicorn flask flask-cors aiohttp requests

# UI & utilities
pip install Pillow python-dotenv prompt_toolkit rich pytest
```

---

## First-Time Launch Options

All launchers now use a unified system. Choose what you want to run:

### Option 1: Core TUI Only (Recommended for Testing)

The lightweight text-based interface, perfect for command testing and embedded systems.

**Terminal (CLI):**

```bash
./bin/Launch-uCODE.sh
```

**Features:**

- Offline-first command interface
- No server required
- Minimal resource usage

---

### Option 2: Wizard Server + Dashboard

Always-on backend service with web dashboard for APIs, webhooks, and AI model routing.

**Terminal (CLI):**

```bash
./bin/Launch-uCODE.sh wizard
```

**What this does:**

1. Activates virtual environment
2. Installs dependencies if needed
3. **Auto-builds the Svelte dashboard** (if npm is available)
4. Starts Wizard Server on port `8765` in **daemon mode** (background service)
5. Opens browser dashboard automatically

**Dashboard Tech Stack:**

- Built with **Svelte 4** + **Vite** + **Tailwind CSS**
- Real-time status monitoring
- Device session management
- Rate limit tracking
- WebSocket support
- **Runs as background service** (no blocking console prompt)

**Dashboard URLs:**

- `http://localhost:8765/` — Web dashboard
- `http://localhost:8765/api/v1` — REST API

**Note:** If npm isn't installed, a basic fallback HTML dashboard will be served with all API endpoints listed.

---

### Option 3: API Extension

REST/WebSocket API server for programmatic access.

```bash
python -m extensions.api.server
```

**What this does:**

1. Activates virtual environment (if needed)
2. Starts API server on port `5001`
3. Provides REST and WebSocket endpoints

**API URLs:**

- `http://localhost:5001/docs` — Swagger API documentation
- `http://localhost:5001/api/*` — REST endpoints

---

## What Each Component Does

| Component         | Port | Purpose                                  | Visibility    |
| ----------------- | ---- | ---------------------------------------- | ------------- |
| **Core TUI**      | —    | Text-based command interface             | Offline-first |
| **Wizard Server** | 8765 | Production APIs, model routing, webhooks | Production    |
| **API Extension** | 5001 | REST/WebSocket API server                | Optional      |

---

## Checking Versions

Each component has independent versioning:

```bash
python -m core.version check     # View all versions
python -m core.version show      # Dashboard
```

---

## Common Commands

### Stop a Running Service

All launchers handle `Ctrl+C` cleanly:

```bash
# Press Ctrl+C in the terminal where the service is running
^C
```

For background services started via .command files, find and kill the process:

```bash
# Find process
ps aux | grep "wizard.server\|goblin\|empire"

# Kill by PID
kill <PID>
```

### Debug Logs

Check these for errors:

```bash
# TUI debug log (most recent)
tail -f memory/logs/session-commands-*.log

# Wizard Server logs
tail -f memory/logs/api-*.log

# Goblin Dev logs
tail -f memory/logs/dev-*.log
```

### Run Tests

```bash
# Core TUI tests
source venv/bin/activate
pytest core/tests/ -v

# Wizard Server tests
pytest wizard/tests/ -v
```

---

## Troubleshooting

### Command Not Found: `python`

**Problem:** You see `python: command not found`

**Solution:** Make sure virtual environment is activated:

```bash
source venv/bin/activate
```

### ModuleNotFoundError (Missing Dependencies)

**Problem:** `ModuleNotFoundError: No module named 'requests'` or similar

**Solution:** Install dependencies manually:

```bash
source venv/bin/activate
pip install -r requirements.txt

# Or in smaller batches if the above hangs:
pip install google-generativeai openai anthropic
pip install google-auth google-auth-oauthlib google-api-python-client
pip install fastapi uvicorn flask aiohttp requests
pip install Pillow python-dotenv prompt_toolkit rich
```

### Port Already in Use

**Problem:** "Address already in use" error

**Solution:** The unified launcher system auto-detects port conflicts. If needed, manually specify a port:

```bash
./bin/Launch-uCODE.sh wizard --port 9000   # Custom port
```

### Browser Won't Open

**Problem:** The launcher script doesn't auto-open a browser

**Solution:** Open manually:

```bash
# Wizard Server
open http://localhost:8765
```

---

## Next Steps

1. **Read Architecture** — See [AGENTS.md](AGENTS.md) for system design
2. **Explore Components** — Check [core/](core/), [wizard/](wizard/), [extensions/](extensions/)
3. **Write Your First Script** — uDOS supports `.ucode.md` and uPY scripting
4. **Join Development** — See [Contributing](wiki/Contributing.md)

---

## Useful Resources

- **Architecture**: [AGENTS.md](AGENTS.md)
- **Component Docs**: [Core](core/README.md), [Wizard](wizard/ARCHITECTURE.md), [Extensions](extensions/README.md)
- **Roadmap**: [docs/development-streams.md](docs/development-streams.md)
- **Issues & Decisions**: [docs/decisions/](docs/decisions/)

---

**Need help?** Check the [Full Documentation](docs/) or open an issue on GitHub.
