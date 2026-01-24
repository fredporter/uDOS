# uDOS Launcher Guide

## Quick Start

### For macOS - Double-click to run

- **uDOS TUI:** `/bin/Launch-uDOS-TUI.command` - Interactive terminal interface
- **Wizard Server:** `/bin/Launch-Wizard-Server.command` - Production API server (port 8765)
- **Goblin Dev Server:** `/dev/goblin/bin/Launch-Goblin-Dev.command` - Experimental server (port 8767)

### From Terminal

```bash
# TUI
./bin/Launch-uDOS-TUI.command

# Wizard Server
./bin/Launch-Wizard-Server.command

# Goblin Dev Server
./dev/goblin/bin/Launch-Goblin-Dev.command

# Or shell script version
./dev/goblin/bin/launch-goblin-dev.sh
```

---

## Server Details

### 🧙 Wizard Production Server (Port 8765)

**Status:** PRODUCTION v1.1.0.0 (stable, frozen)

**Services:**

- AI Gateway (Ollama, OpenRouter, Vibe)
- Device Authentication + Sessions
- Extension Repository
- Notion Sync (Webhooks + Queue)
- Task Scheduler (Organic cron)
- Binder Compiler (PDF/JSON/Markdown)
- GitHub Integration
- Dev Mode Coordination

**Endpoints:**

- Web UI: `http://localhost:8765`
- API: `http://localhost:8765/api/v1/*`
- Docs: `http://localhost:8765/docs`
- ReDoc: `http://localhost:8765/redoc`

**Config:** `wizard/config/wizard.json` (committed, versioned)

---

### 👺 Goblin Dev Server (Port 8767)

**Status:** DEVELOPMENT v0.2.0 (unstable, experimental)

**Scope:** Local-only (127.0.0.1)

**Features:**

- Runtime Executor (TS Markdown execution)
- Experimental API routes (`/api/v0/*`)
- Svelte Dashboard (modern UI)
- Feature development sandbox

**Endpoints:**

- Dashboard: `http://127.0.0.1:8767`
- API: `http://127.0.0.1:8767/api/v0/*`
- Docs: `http://127.0.0.1:8767/docs`
- Server Info: `http://127.0.0.1:8767/api/v0/info`

**Config:** `/dev/goblin/config/goblin.json` (local-only, gitignored)

---

## Boot Sequence Output

When you launch a server, you'll see:

```text

╔═══════════════════════════════════════════════════════════════╗
║ 👺 Goblin Dev Server v0.2.0 ║
║ Experimental • Localhost Only • Breaking Changes OK ║
╚═══════════════════════════════════════════════════════════════╝

[BOOT] Checking environment...
[BOOT] uDOS Root: /Users/fredbook/Code/uDOS
[BOOT] Python: Python 3.9.6
[BOOT] Features: Notion sync, Runtime execution, Task scheduling, Binder compilation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👺 Goblin Dev Server v0.2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Virtual environment activated
[✓] Dependencies installed and ready
[BOOT] Starting Goblin Dev Server on port 8767...

```

---

## Troubleshooting

### Port Already In Use

```bash
# Check what's using the port
lsof -i :8765   # Wizard
lsof -i :8767   # Goblin

# Kill the process
kill -9 <PID>
```

### Missing Dependencies

```bash
# Activate venv and reinstall
source .venv/bin/activate
pip install -r requirements.txt
```

### Submodule Not Initialized

If you see "[⚠] Note: Goblin Dev Server is in the private submodule (dev/)"

```bash
git submodule update --init --recursive
cd dev && git pull origin main && cd ..
```

### Check Server Logs

```bash
# Wizard logs
cat memory/logs/wizard-*.log

# System logs
cat memory/logs/system-*.log

# Debug logs
cat memory/logs/debug-*.log
```

---

## Launcher Locations

```text
/bin/
├── Launch-uDOS-TUI.command          # TUI entry point
├── Launch-Wizard-Server.command     # Wizard (always-on)
└── (Goblin moved to dev/goblin/bin)

/dev/goblin/bin/
├── Launch-Goblin-Dev.command        # Goblin (.command for macOS)
└── launch-goblin-dev.sh             # Goblin (shell script)
```

---

## Development Workflow

### Start Development Stack

```bash
# Terminal 1: Core TUI
./bin/Launch-uDOS-TUI.command

# Terminal 2: Wizard API (in background)
./bin/Launch-Wizard-Server.command &

# Terminal 3: Goblin Dev (in background)
./dev/goblin/bin/Launch-Goblin-Dev.command &

# Terminal 4: Tauri App (if working on UI)
cd app/src
npm run tauri dev
```

### Access Each System

- **TUI:** Interactive prompt in Terminal 1
- **Wizard API:** `http://localhost:8765/docs`
- **Goblin Dashboard:** `http://127.0.0.1:8767`
- **Tauri App:** Launches in separate window

---

## Notes

- **Wizard** is production-stable and frozen. Changes go through RFC process.
- **Goblin** is experimental-only. Break things, iterate fast, promote to Wizard when stable.
- **TUI** is the primary user interface for offline-first usage.
- All servers require Python 3.9+ and virtual environment activation.

---

Last Updated: 2026-01-22
uDOS Alpha v1.0.2.0
