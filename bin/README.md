# uDOS Unified Launcher

One entry point for everything: **Launch-uCODE.sh**

---

## 🚀 Quick Start

### Unified Launcher

Run:

```bash
./bin/Launch-uCODE.sh
```

### Process Management

```bash
# Stop all uDOS processes cleanly
./bin/kill-udos.sh

# Restart after cleanup
./bin/Launch-uCODE.sh
```

### Command-Line Launch

```bash
# Interactive menu
./bin/Launch-uCODE.sh

# Direct component launch
./bin/Launch-uCODE.sh core              # Core TUI (default)
./bin/Launch-uCODE.sh wizard            # Wizard Server
./bin/Launch-uCODE.sh goblin            # Goblin Dev (dev role only)
./bin/Launch-uCODE.sh app               # App Dev (dev role only)

# With explicit mode
./bin/Launch-uCODE.sh wizard server     # Equivalent to: wizard server
./bin/Launch-uCODE.sh core tui          # Equivalent to: core tui
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
├── Launch-uCODE.sh           # ← Single unified entry point
├── udos-common.sh            # Shared helper functions
├── install.sh                # Installation setup
├── port-manager              # Port conflict detection
├── udos-self-heal.sh         # Self-healing utilities
└── README.md                 # This file
```

**Archived:** Legacy launchers are deprecated and should not be used.

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
./bin/Launch-uCODE.sh core

# In another terminal, start Wizard
./bin/Launch-uCODE.sh wizard

# In another, start Goblin for experimental work
./bin/Launch-uCODE.sh goblin

# In another, develop the App
./bin/Launch-uCODE.sh app
```

### Integration with VS Code

The workspace includes tasks for each component (see `uDOS.code-workspace`).

---

## ✨ Why Unified Launcher?

**Before:** multiple launchers, unclear which to use
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
├── Launch-uCODE.sh                  # Unified entry point
├── udos-common.sh                   # Shared helpers
└── udos-self-heal.sh                # Maintenance utility
```

---

## 🧪 Full Development Stack

Start all servers for development:

**Terminal 1 - TUI:**

```bash
./bin/Launch-uCODE.sh core
```

**Terminal 2 - Wizard:**

```bash
./bin/Launch-uCODE.sh wizard &
```

**Terminal 3 - Goblin:**

```bash
./bin/Launch-uCODE.sh goblin &
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

## Single Entry Point

Use `./bin/Launch-uCODE.sh` for all components. It detects role and availability
and routes to the correct runtime.

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
./bin/Launch-uCODE.sh wizard
```

### With Full Svelte Dashboard

```bash
# First install Node.js (see above)
# Then:
./bin/Launch-uCODE.sh wizard

# Script will auto-build dashboard
```

### Manual Dashboard Build

```bash
cd wizard/dashboard
npm install
npm run build

# Then start server
../bin/Launch-uCODE.sh wizard
```

### Custom Port

```bash
./bin/Launch-uCODE.sh wizard --port 9000
./bin/Launch-uCODE.sh goblin --port 9001
```

### Run in Background

```bash
./bin/Launch-uCODE.sh wizard &

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
./bin/Launch-uCODE.sh wizard --port 9000   # Instead of 8765
./bin/Launch-uCODE.sh goblin --port 9001   # Instead of 8767
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

- `bin/Launch-uCODE.sh` — Unified launcher
- `bin/udos-common.sh` — Shared launcher helpers
- `bin/udos-self-heal.sh` — Maintenance utility

---

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review debug logs in `memory/logs/`
3. Check [QUICKSTART.md](../QUICKSTART.md)
4. Visit [uDOS GitHub](https://github.com/fredporter/uDOS)
