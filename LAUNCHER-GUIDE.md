# uDOS Launcher Guide

## Quick Start

### For macOS - Double-click to run

- **Core TUI:** `/bin/Launch-uDOS-TUI.command` - Interactive terminal interface
- **Wizard Server:** `/bin/Launch-Wizard-Server.command` - Production API server (port 8765)

### From Terminal

```bash
# Core TUI
./bin/Launch-uDOS-TUI.command

# Wizard Server
./bin/Launch-Wizard-Server.command
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

## Boot Sequence Output

When you launch a server, you'll see:

```text

╔═══════════════════════════════════════════════════════════════╗
║ 🧙 Wizard Server v1.1.0.0 ║
║ Production • Always-On • Frozen API ║
╚═══════════════════════════════════════════════════════════════╝

[BOOT] Checking environment...
[BOOT] uDOS Root: /Users/fredbook/Code/uDOS
[BOOT] Python: Python 3.9.6
[BOOT] Features: AI Gateway, Plugin Repository, Device Auth, GitHub Integration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧙 Wizard Server v1.1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Virtual environment activated
[✓] Dependencies installed and ready
[BOOT] Starting Wizard Server on port 8765...

```

---

## Troubleshooting

### Port Already In Use

```bash
# Check what's using the port
lsof -i :8765   # Wizard

# Kill the process
kill -9 <PID>
```

### Missing Dependencies

```bash
# Activate venv and reinstall
source .venv/bin/activate
pip install -r requirements.txt
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
├── Launch-uDOS-TUI.command          # Core TUI entry point
└── Launch-Wizard-Server.command     # Wizard API server (always-on)
```

---

## Development Workflow

### Start Development Stack

```bash
# Terminal 1: Core TUI
./bin/Launch-uDOS-TUI.command

# Terminal 2: Wizard API (in background)
./bin/Launch-Wizard-Server.command &
```

### Access Each System

- **Core TUI:** Interactive prompt in Terminal 1
- **Wizard API:** `http://localhost:8765/docs`

---

## Notes

- **Wizard** is production-stable (v1.1.0.0) and frozen. Changes go through RFC process.
- **Core** is the offline-first TUI runtime. Alpine Linux primary target with multi-OS support.
- Both systems require Python 3.9+ and virtual environment activation.
- For experimental development, see private `/dev` submodule.

---

Last Updated: 2026-01-22
uDOS Alpha v1.0.2.0
