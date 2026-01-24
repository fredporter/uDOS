# uDOS Quick Start Guide

Get up and running with uDOS in 5 minutes.

---

## Prerequisites

- **Python 3.9+** — For Core and Wizard components
- **Node.js 18+** — For App (Tauri + Svelte)
- **Git** — For cloning and submodule management

---

## Installation

### 1. Clone Repository (with Private Submodule)

```bash
git clone --recurse-submodules https://github.com/fredporter/uDOS.git
cd uDOS

# If you cloned without submodules:
git submodule update --init --recursive
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
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

Choose what you want to run:

### Option 1: Core TUI Only (Recommended for Testing)

The lightweight text-based interface, perfect for command testing and embedded systems.

```bash
./bin/start_udos.sh
```

**Features:**

- Offline-first command interface
- No server required
- Minimal resource usage

---

### Option 2: Wizard Server + Dashboard

Always-on backend service with web dashboard for APIs, webhooks, and AI model routing.

```bash
./bin/start_wizard.sh
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

**Options:**

```bash
./bin/start_wizard.sh 8765           # Custom port
./bin/start_wizard.sh                # Default port 8765
```

**Dashboard URLs:**

- `http://localhost:8765/` — Web dashboard
- `http://localhost:8765/api/v1` — REST API

**Note:** If npm isn't installed, a basic fallback HTML dashboard will be served with all API endpoints listed.

---

### Option 3: Goblin Dev Server (Experimental)

Development server with Notion sync, runtime execution, and task scheduling. **Localhost only**.

```bash
./bin/start_goblin.sh
```

**What this does:**

1. Activates virtual environment
2. Installs dependencies if needed
3. Starts Goblin Dev Server on port `8767`
4. Opens browser dashboard automatically

**Options:**

```bash
./bin/start_goblin.sh 8767           # Custom port
./bin/start_goblin.sh                # Default port 8767
```

**Features (Experimental):**

- Notion webhook sync
- TypeScript Markdown runtime execution
- Task scheduling (organic cron)
- Binder compilation

**Dashboard URLs:**

- `http://localhost:8767/` — Dev dashboard
- `http://localhost:8767/api/v0` — Experimental API (unstable)

---

### Option 4: Desktop App (Tauri + Svelte)

Modern GUI for uMarkdown with multiple format support.

```bash
cd app
npm install
npm run tauri dev
```

**Requires:**

- Node.js 18+
- Tauri CLI installed globally: `npm install -g @tauri-apps/cli@latest`

---

### Option 5: Full Development Mode (Everything)

TUI + Wizard Server + Goblin Dev Server + API in one command.

```bash
./bin/Launch-Dev-Mode.command
```

**Launches:**

- ✅ Core TUI (main terminal)
- ✅ Wizard Server (port 8765)
- ✅ Goblin Dev Server (port 8767)
- ✅ API Server (port 3000)

---

## What Each Component Does

| Component         | Port | Purpose                                  | Visibility    |
| ----------------- | ---- | ---------------------------------------- | ------------- |
| **Core TUI**      | —    | Text-based command interface             | Offline-first |
| **Wizard Server** | 8765 | Production APIs, model routing, webhooks | Production    |
| **Goblin Dev**    | 8767 | Notion sync, runtime, task scheduling    | Dev-only      |
| **API Extension** | 3000 | REST/WebSocket API server                | Optional      |
| **Tauri App**     | —    | Desktop GUI (runs locally)               | Optional      |

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

All launcher scripts handle `Ctrl+C` cleanly:

```bash
# Press Ctrl+C in the terminal where the service is running
^C
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
# TUI health checks (47 tests)
./bin/start_udos.sh memory/tests/shakedown.uscript

# Integration tests
source .venv/bin/activate
pytest dev/tests/ -v
```

---

## Troubleshooting

### Command Not Found: `python`

**Problem:** You see `python: command not found`

**Solution:** Make sure virtual environment is activated:

```bash
source .venv/bin/activate
```

### ModuleNotFoundError (Missing Dependencies)

**Problem:** `ModuleNotFoundError: No module named 'requests'` or similar

**Solution:** Install dependencies manually:

```bash
source .venv/bin/activate
pip install -r requirements.txt

# Or in smaller batches if the above hangs:
pip install google-generativeai openai anthropic
pip install google-auth google-auth-oauthlib google-api-python-client
pip install fastapi uvicorn flask aiohttp requests
pip install Pillow python-dotenv prompt_toolkit rich
```

### Port Already in Use

**Problem:** "Address already in use" error

**Solution:** Use a different port:

```bash
./bin/start_wizard.sh 9000   # Instead of default 8765
./bin/start_goblin.sh 9001   # Instead of default 8767
```

### Browser Won't Open

**Problem:** The launcher script doesn't auto-open a browser

**Solution:** Open manually:

```bash
# Wizard Server
open http://localhost:8765

# Goblin Dev Server
open http://localhost:8767
```

### Submodule Issues

**Problem:** `dev/` folder is empty

**Solution:**

```bash
git submodule update --init --recursive
```

---

## Next Steps

1. **Read Architecture** — See [AGENTS.md](AGENTS.md) for system design
2. **Explore Components** — Check [core/](core/), [wizard/](wizard/), [extensions/](extensions/)
3. **Write Your First Script** — uDOS supports `.ucode.md` and uPY scripting
4. **Join Development** — See [CONTRIBUTING.md](docs/contributing.md)

---

## Useful Resources

- **Architecture**: [AGENTS.md](AGENTS.md)
- **Component Docs**: [Core](core/README.md), [Wizard](wizard/ARCHITECTURE.md), [Extensions](extensions/README.md)
- **Roadmap**: [docs/roadmap.md](docs/roadmap.md)
- **Issues & Decisions**: [docs/decisions/](docs/decisions/)

---

**Need help?** Check the [Full Documentation](docs/) or open an issue on GitHub.
