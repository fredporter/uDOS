# uDOS Launcher Scripts

Quick-start scripts for launching uDOS components.

## 🚀 Quick Start

### Double-Click Launchers (macOS)

- **`Launch-uDOS-TUI.command`** — TUI interface (offline-first)
- **`Launch-Wizard-Server.command`** — Production API server (port 8765)
- **For Goblin:** See `/dev/goblin/bin/Launch-Goblin-Dev.command`

### Terminal Launch

```bash
./bin/Launch-uDOS-TUI.command           # TUI
./bin/Launch-Wizard-Server.command      # Wizard API
./dev/goblin/bin/Launch-Goblin-Dev.command  # Goblin (experimental)
```

---

## 📊 Server Overview

### 🧙 Wizard Production Server

**Location:** `Launch-Wizard-Server.command`
**Port:** 8765
**Status:** Production v1.1.0.0 (stable, frozen)

**Features:**

- AI Gateway (Ollama, OpenRouter, Vibe)
- Device Authentication + Sessions
- Extension Repository
- Notion Sync + Task Scheduler
- Binder Compiler
- GitHub Integration
- Dev Mode Coordination

**Access:**

- API: `http://localhost:8765/api/v1/*`
- Docs: `http://localhost:8765/docs`

---

### 👺 Goblin Experimental Server

**Location:** `/dev/goblin/bin/Launch-Goblin-Dev.command`
**Port:** 8767
**Status:** Experimental v0.2.0 (unstable, breaking changes OK)

**Features:**

- Runtime Executor (TS Markdown)
- Svelte Dashboard
- Experimental `/api/v0/*` routes
- Local-only (127.0.0.1)

**Access:**

- Dashboard: `http://127.0.0.1:8767`
- Docs: `http://127.0.0.1:8767/docs`

---

### 🖥️ uDOS TUI

**Location:** `Launch-uDOS-TUI.command`
**Status:** Production (offline-first)

**Features:**

- Interactive terminal interface
- No network required
- SmartPrompt command parser
- Full system access

---

## 📋 Boot Sequence

All launchers show environment checks before starting:

```
╔═══════════════════════════════════════════════════════════════╗
║            🧙 Wizard Production Server v1.1.0.0               ║
║      Always-On • AI Routing • Webhooks • Device Auth          ║
╚═══════════════════════════════════════════════════════════════╝

[BOOT] Checking environment...
[BOOT] uDOS Root: /Users/fredbook/Code/uDOS
[BOOT] Python: Python 3.9.6

[✓] Virtual environment activated
[✓] Dependencies installed and ready
[BOOT] Starting Wizard Server on port 8765...
```

---

## 🔧 Troubleshooting

### Port Already In Use

```bash
lsof -i :8765   # Wizard
lsof -i :8767   # Goblin
kill -9 <PID>
```

### Virtual Environment Issues

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Submodule Not Found

```bash
git submodule update --init --recursive
```

### Check Server Logs

```bash
cat memory/logs/wizard-*.log
cat memory/logs/system-*.log
cat memory/logs/debug-*.log
```

---

## 📂 Launcher Directory Structure

```
/bin/
├── README.md                        # This file
├── Launch-uDOS-TUI.command          # TUI entry point
├── Launch-Wizard-Server.command     # Wizard (always-on)
└── launch-udos-dev.sh               # Dev setup

/dev/goblin/bin/
├── Launch-Goblin-Dev.command        # Goblin (experimental)
└── launch-goblin-dev.sh             # Shell script version
```

---

## 🧪 Full Development Stack

Start all servers for development:

**Terminal 1 - TUI:**

```bash
./bin/Launch-uDOS-TUI.command
```

**Terminal 2 - Wizard:**

```bash
./bin/Launch-Wizard-Server.command &
```

**Terminal 3 - Goblin:**

```bash
./dev/goblin/bin/Launch-Goblin-Dev.command &
```

**Terminal 4 - App (optional):**

```bash
cd app && npm run tauri dev
```

**Access:**

- TUI: Terminal 1 (interactive)
- Wizard: http://localhost:8765/docs
- Goblin: http://127.0.0.1:8767
- App: Native window

---

## 📚 Legacy Scripts

The following scripts are still available for direct use:

### `start_udos.sh` — Core TUI

```bash
./bin/start_udos.sh [uscript-file]
```

Features: Offline, no dependencies, minimal footprint

---

### `start_goblin.sh` — Goblin Dev Server (Experimental)

Launches the development server with Notion sync and runtime execution.

```bash
./bin/start_goblin.sh [port]
```

**Default:** Port 8767

**Features:**

- Notion webhook integration
- TypeScript Markdown runtime
- Task scheduling
- Localhost-only mode

---

## Setup Requirements

### Python

- Python 3.9+
- Virtual environment (auto-created if missing)
- Dependencies from `requirements.txt`

### Node.js (Optional, for Full Svelte Dashboard)

- Node.js 18+
- npm 9+

#### Installing Node.js

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install -y nodejs npm
```

**macOS (with Homebrew):**

```bash
brew install node
```

**Other systems:**
Visit https://nodejs.org/

### Browser

Any modern browser (Chrome, Firefox, Safari, Edge)

---

## Usage Examples

### Quick Start (Fallback Dashboard)

```bash
# No prerequisites needed
./bin/start_wizard.sh
```

### With Full Svelte Dashboard

```bash
# First install Node.js (see above)
# Then:
./bin/start_wizard.sh

# Script will auto-build dashboard
```

### Manual Dashboard Build

```bash
cd wizard/dashboard
npm install
npm run build

# Then start server
../bin/start_wizard.sh
```

### Custom Port

```bash
./bin/start_wizard.sh 9000
./bin/start_goblin.sh 9001
```

### Run in Background

```bash
./bin/start_wizard.sh 8765 &

# Access at http://localhost:8765

# Stop server:
kill %1
```

---

## Troubleshooting

### Python Error: "command not found"

**Solution:** Activate virtual environment manually:

```bash
source .venv/bin/activate
```

### npm Not Found

**Solution:** Install Node.js (see above), then re-run script.

The script will:

1. Show you the install command for your OS
2. Continue with fallback HTML dashboard
3. Show instructions for manual dashboard build

### Port Already in Use

**Solution:** Use a different port:

```bash
./bin/start_wizard.sh 9000   # Instead of 8765
./bin/start_goblin.sh 9001   # Instead of 8767
```

### Browser Won't Auto-Open

**Solution:** Open manually:

```bash
# Wizard
open http://localhost:8765

# Goblin
open http://localhost:8767
```

### Server Won't Start

**Check logs:**

```bash
tail -f memory/logs/api-*.log
tail -f memory/logs/dev-*.log
```

---

## Dashboard Information

### Fallback Dashboard

- Basic HTML interface
- Shows all API endpoints
- No npm/build required
- Read-only display

### Full Svelte Dashboard

- Interactive real-time updates
- Device management
- Rate limit monitoring
- Cost tracking
- WebSocket support
- Requires Node.js 18+

---

## API Endpoints

### Wizard Server (`http://localhost:8765`)

- `/` — Web dashboard
- `/health` — Health check
- `/api/v1/` — REST API
- `/api/v1/ai/models` — AI models
- `/api/v1/status` — Server status
- `/ws` — WebSocket

### Goblin Dev (`http://localhost:8767`)

- `/` — Dev dashboard
- `/api/v0/runtime/execute` — Code execution
- `/api/v0/tasks/schedule` — Task scheduling
- `/api/v0/notion/sync` — Notion sync

---

## Advanced Options

### Wizard Server Command-Line Args

```bash
python -m wizard.server --help
```

Options:

- `--port PORT` — Server port (default: 8765)
- `--host HOST` — Bind address (default: 0.0.0.0)
- `--debug` — Enable debug mode
- `--no-interactive` — Daemon mode (used by launcher)

### Development Mode

```bash
# Watch mode for Svelte dashboard
cd wizard/dashboard
npm run dev
# Available at http://localhost:5174
```

---

## Files Modified

- `bin/start_udos.sh` — Core launcher
- `bin/start_wizard.sh` — Wizard + Dashboard launcher ⭐
- `bin/start_goblin.sh` — Goblin launcher
- `wizard/dashboard/package.json` — Svelte build config
- `wizard/server.py` — Fallback dashboard HTML

---

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review debug logs in `memory/logs/`
3. Check [QUICKSTART.md](../QUICKSTART.md)
4. Visit [uDOS GitHub](https://github.com/fredporter/uDOS)
