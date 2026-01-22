# uDOS Launcher Scripts

Quick-start scripts for launching different uDOS components.

## Scripts Overview

### `start_udos.sh` — Core TUI

Launches the offline-first text-based interface.

```bash
./bin/start_udos.sh [uscript-file]
```

**Features:**

- Offline operation
- No dependencies
- Minimal footprint

---

### `start_wizard.sh` — Wizard Server + Web Dashboard

Launches the always-on production server with Svelte web dashboard.

```bash
./bin/start_wizard.sh [port]
```

**Default:** Port 8765

**Features:**

- Automatic Node.js/npm detection
- Automatic Svelte dashboard build
- Daemon mode (background service)
- Browser auto-launch
- Fallback HTML dashboard if npm not available

**What it does:**

1. Activates Python virtual environment
2. Installs Python dependencies
3. Checks for Node.js/npm
4. Builds Svelte dashboard (if npm available)
5. Starts Wizard Server in daemon mode
6. Opens browser dashboard

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
