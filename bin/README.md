# uDOS Unified Launcher

One entry point for everything: **Launch-uCODE** (`.command` for macOS, `.sh` for Linux)

---

## 🚀 Quick Start

### Platform-Specific Launchers

**macOS:** Double-click `Launch-uCODE.command` or run `./bin/Launch-uCODE.command`
**Linux:** Run `./bin/Launch-uCODE.sh` (Ubuntu, Alpine, etc.)

Both launchers provide the same functionality with platform-specific optimizations.

### Process Management

```bash
# Stop all uDOS processes cleanly
./bin/kill-udos.sh

# Restart after cleanup
./bin/Launch-uCODE.sh
```

### Single Entry Point (macOS)

**Double-click:** `Launch-uCODE.command`

Shows an interactive menu:

```
╔═════════════════════════════════════════════════════╗
║       uCODE - Unified Launcher                      ║
║      Role: dev                                      ║
╚═════════════════════════════════════════════════════╝

  1) Core TUI - Terminal interface (offline-first)
  2) Wizard Server - Always-on services (port 8765)
  3) Goblin Dev Server - Experimental features (port 8767)
  4) App Dev - uMarkdown app development

  q) Quit

Select component [1-4]:
```

### Command-Line Launch

```bash
# Interactive menu
./Launch-uCODE.command

# Direct component launch
./Launch-uCODE.command core              # Core TUI (default)
./Launch-uCODE.command wizard            # Wizard Server
./Launch-uCODE.command goblin            # Goblin Dev (dev role only)
./Launch-uCODE.command app               # App Dev (dev role only)

# With explicit mode
./Launch-uCODE.command wizard server     # Equivalent to: wizard server
./Launch-uCODE.command core tui          # Equivalent to: core tui
```

---

## 🎯 What's Available

### Core TUI (Recommended)

- **Offline-first** terminal interface
- No network required
- Full command system
- Game/exploration system
- Smart command parser
- Always available

### Wizard Server (Production)

- **Port:** 8765
- **Status:** v1.1.0.0 (stable, frozen)
- AI model routing (Ollama → OpenRouter)
- Device authentication & sessions
- Extension repository & management
- GitHub integration & monitoring
- Webhooks & API endpoints
- Binder compilation
- Cost tracking & quotas

### Goblin Dev Server (Experimental)

- **Port:** 8767
- **Status:** v0.2.0 (unstable, experimental)
- TS Markdown runtime executor
- Webhook handling (local)
- Task scheduling (organic cron)
- Binder compilation
- Experimental `/api/v0/*` routes
- **Dev role only** (requires `/dev/.git`)

### App Dev (Tauri + Svelte)

- uMarkdown editor development
- macOS native app
- Future: iOS/iPadOS
- **Dev role only**

---

## 🔒 User Roles

### **dev** role

- Access to all components
- Required: `/dev/.git` submodule or `DEV_MODE=1`
- Can run Core, Wizard, Goblin, App

### **user** role

- Core TUI only
- Offline-first experience
- Default when `/dev` is not present

---

## 📁 Consolidated File Structure

After cleanup (2026-01-29):

```
bin/
├── Launch-uCODE.command      # ← Single unified entry point
├── udos-common.sh            # Shared helper functions
├── udos                       # Python script launcher
├── install.sh                # Installation setup
├── port-manager              # Port conflict detection
├── udos-self-heal.sh         # Self-healing utilities
└── README.md                 # This file
```

**Archived:** All other `.command` and `.sh` files moved to `.archive/bin-launchers-2026-01-29/`

---

## 🔧 Technical Details

### Component Detection

The launcher automatically detects:

```bash
Core:      /uDOS/uDOS.py + /uDOS/core/
Wizard:    /uDOS/wizard/server.py
Goblin:    /uDOS/dev/goblin/dev_server.py
App:       /uDOS/app/package.json
```

### Role Detection

```bash
dev:   if $DEV_MODE=1 OR /dev/.git exists
user:  otherwise (default)
```

### Environment Setup

All launchers:

1. Source `udos-common.sh` for paths and colors
2. Resolve `UDOS_ROOT` intelligently (works from anywhere)
3. Check Python environment (uses `venv` if available)
4. Validate dependencies before launch
5. Show boot sequence with environment info

---

## 📖 Boot Sequence Example

```
╔═══════════════════════════════════════════════════════╗
║       uCODE - Unified Terminal TUI                    ║
║      Offline-First • Game System • Full Commands      ║
╚═══════════════════════════════════════════════════════╝

[BOOT] Resolving uDOS root...
[BOOT] uDOS Root: /Users/you/Code/uDOS
[BOOT] Python: 3.9.6 (venv/bin/python)
[✓] Virtual environment activated
[✓] Dependencies validated
[BOOT] User role: dev
[BOOT] Available: core, wizard, goblin, app

🧙 uCODE Ready
Type HELP for commands
```

---

## 🚀 For Developers

### Quick development workflow

```bash
# Start Core TUI
./Launch-uCODE.command core

# In another terminal, start Wizard
./Launch-uCODE.command wizard

# In another, start Goblin for experimental work
./Launch-uCODE.command goblin

# In another, develop the App
./Launch-uCODE.command app
```

### Integration with VS Code

The workspace includes tasks for each component (see `uDOS.code-workspace`).

---

## ✨ Why Unified Launcher?

**Before:** 4+ separate `.command` files, confusing menu, unclear which to use
**After:** 1 smart entry point, auto-detects components, shows what's available

**Benefits:**

- ✅ Single entry point (less confusion)
- ✅ Smart role/component detection
- ✅ Works from anywhere
- ✅ No hardcoded paths
- ✅ Interactive menu when needed
- ✅ CLI automation friendly
- ✅ Future-proof (easy to add new components)

---

**Last Updated:** 2026-01-29

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
source venv/bin/activate
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
./bin/start_udos.sh [script-file.md]
```

Features: Offline, no dependencies, minimal footprint

---

### `start_goblin.sh` — Goblin Dev Server (Experimental)

Launches the development server with runtime execution and binder tooling.

```bash
./bin/start_goblin.sh [port]
```

**Default:** Port 8767

**Features:**

- Webhook integration
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
source venv/bin/activate
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
- `/api/` — REST API
- `/api/ai/models` — AI models
- `/api/status` — Server status
- `/ws` — WebSocket

### Goblin Dev (`http://localhost:8767`)

- `/` — Dev dashboard
- `/api/v0/runtime/execute` — Code execution
- `/api/v0/tasks/schedule` — Task scheduling
- `/api/v0/binder/compile` — Binder compilation

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
