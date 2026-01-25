# Wizard Server Dev Mode Guide

**Version:** v1.0.0  
**Status:** ✅ Complete and Ready for Testing  
**Last Updated:** 2026-01-25

---

## 🚀 Quick Start

### Option 0: Dev Recovery TUI (Repair-first)

Use this when Wizard/Core might be broken. It runs diagnostics on startup
and exposes repair + backup/restore/cleanup commands.

```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python -m wizard.dev_tui
```

Or via launcher:

```bash
./bin/launch_wizard_dev_tui.sh
```

### Option 1: Integrated Mode (Server + TUI Together)

```bash
# Via VS Code task:
# "🧙 Wizard Dev Mode (Server + TUI)"

# Or manually:
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python wizard/launch_wizard_dev.py
```

**What happens:**

1. Server starts on `http://127.0.0.1:8765`
2. TUI appears automatically
3. Type commands (STATUS, SERVICES, AI, etc.)
4. Press EXIT to quit (stops server too)

### Option 2: Server Only

```bash
# Via VS Code task:
# "🧙 Wizard Server Only"

# Or manually:
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python wizard/launch_wizard_dev.py --no-tui
```

**Output:**

```
🧙 Wizard Server starting on http://127.0.0.1:8765
   Plugin Repo: ✓
   Web Proxy:   ✓
   AI Gateway:  ✗
   Gmail Relay: ✗
```

Then open another terminal and run:

```bash
python wizard/launch_wizard_dev.py --tui
```

### Option 3: TUI Only (Server Already Running)

```bash
# Via VS Code task:
# "🧙 Wizard TUI Only"

# Or manually:
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python wizard/launch_wizard_dev.py --tui
```

---

## 📋 TUI Commands

### Status & Monitoring

```
STATUS          Show real-time dashboard
SERVICES        List services and status
DEVICES         Show connected devices
QUOTA           View AI cost tracking
RATES           Rate limit configuration
```

### Assistant Management

```
AI STATUS       Show assistant provider status
AI MODELS       List available models
AI SWITCH <model>
                Switch to different model
```

**Available Models:**

- Local: `devstral-small-2`, `llama3.2`, `codellama`
- Cloud: `claude-sonnet-4`, `gemini-pro`, `mistral-large`

### Service Control

```
START <service> Start a service
STOP <service>  Stop a service
RESTART         Restart Wizard Server
```

**Services:**

- `web-proxy` — Web content fetching
- `gmail-relay` — Email integration
- `ai-gateway` — AI model routing
- `plugin-repo` — Plugin repository

### Information

```
CONFIG          Show current configuration
LOGS [filter] [count]
                View filtered logs
HELP            Show command reference
EXIT            Quit TUI (stops server)
```

### Maintenance (TUI + Dev Recovery TUI)

```
BACKUP [scope] [label]   Create .backup snapshot
RESTORE [scope] [--force] Restore latest backup
TIDY [scope]             Move junk into .archive
CLEAN [scope]            Reset scope into .archive
COMPOST [scope]          Move .archive/.backup/.tmp into /.compost
```

Scopes: `current | +subfolders | workspace | all` (default: workspace)

---

## 🔌 API Endpoints (for TUI)

### Health & Status

```
GET /health
→ {"status": "healthy", "services": {...}}

GET /api/v1/status
→ Device authentication required
```

### TUI Control Endpoints

```
GET /api/v1/devices
→ List connected devices

GET /api/v1/logs?filter=all&limit=20
→ Get filtered logs

POST /api/v1/models/switch
→ {"model": "devstral-small-2"}

POST /api/v1/services/{service}/{action}
→ Service control (start/stop/restart)
```

### Example Requests

```bash
# Check health
curl http://127.0.0.1:8765/health

# List devices
curl http://127.0.0.1:8765/api/v1/devices

# Get logs
curl "http://127.0.0.1:8765/api/v1/logs?filter=all&limit=10"

# Switch model
curl -X POST http://127.0.0.1:8765/api/v1/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2"}'

# Stop service
curl -X POST http://127.0.0.1:8765/api/v1/services/ai-gateway/stop
```

---

## 🧪 Testing

### Run Integration Tests

```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python test_wizard_dev_mode.py
```

**Test Coverage:**

- ✅ Server startup and process management
- ✅ Health endpoint response
- ✅ API endpoint availability
- ✅ TUI initialization and command handlers
- ✅ Graceful shutdown

### Manual Testing Checklist

1. **Server Startup**
   - [ ] Server starts on correct port
   - [ ] Health endpoint responds 200
   - [ ] No startup errors in logs

2. **TUI Interface**
   - [ ] STATUS shows dashboard
   - [ ] Commands execute without errors
   - [ ] Output is properly formatted

3. **API Endpoints**
   - [ ] GET /health returns 200
   - [ ] GET /api/v1/devices returns device list
   - [ ] Model switching accepts requests
   - [ ] Service control endpoints exist

4. **Shutdown**
   - [ ] EXIT command stops TUI
   - [ ] Server terminates gracefully
   - [ ] No hanging processes

---

## 🐛 Troubleshooting

### Server Won't Start

**Problem:** Port already in use

```bash
# Find process on port 8765
lsof -i :8765

# Kill it
kill -9 <PID>
```

**Problem:** Missing dependencies

```bash
# Reinstall requirements
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
pip install -r requirements.txt
```

### TUI Doesn't Connect to Server

**Problem:** Server not running

```bash
# Start server first
python wizard/launch_wizard_dev.py --no-tui

# In another terminal, start TUI
python wizard/launch_wizard_dev.py --tui
```

**Problem:** Wrong host/port

```bash
# Check server is listening
curl http://127.0.0.1:8765/health

# View server logs
tail -f memory/logs/wizard-server-*.log
```

### Commands Return Errors

**Check the logs:**

```bash
# Primary debug log
tail -f memory/logs/session-commands-$(date +%Y-%m-%d).log

# Server log
tail -f memory/logs/wizard-server-$(date +%Y-%m-%d).log
```

---

## 📂 File Structure

```
wizard/
├── launch_wizard_dev.py      # Main entry point (server + TUI launcher)
├── launch_wizard_tui.sh      # Bash wrapper
├── dev_server.py             # Dev mode server configuration
├── wizard_tui.py             # Terminal UI implementation (758 lines)
├── server.py                 # API server with TUI endpoints
├── config/
│   └── wizard.json          # Configuration
├── providers/                # AI provider integrations
├── services/                 # Core services
└── tests/                    # Test suite
```

---

## 🔄 Architecture

### Launch Flow (Integrated Mode)

```
launch_wizard_dev.py
  ├─ Creates WizardTUI instance
  ├─ Calls tui._start_server()
  │   └─ Spawns subprocess: dev_server.py
  ├─ Waits for health check
  ├─ Runs tui.run() (async prompt loop)
  └─ On EXIT, calls tui._stop_server()
```

### TUI → API Communication

```
User Input
  ↓
_process_command()
  ↓
Command Handler (e.g., _cmd_devices)
  ↓
HTTP Request to API (if needed)
  ↓
Response parsed & formatted
  ↓
Display to user
```

### API Endpoints (Wizard Server)

- `/health` — Health check (public)
- `/api/v1/devices` — Device listing (TUI)
- `/api/v1/logs` — Log viewing (TUI)
- `/api/v1/models/switch` — Model switching (TUI)
- `/api/v1/services/{service}/{action}` — Service control (TUI)

---

## 🎯 Next Steps

### For Testing (Tomorrow)

1. Run integration test: `python test_wizard_dev_mode.py`
2. Manual testing using checklist above
3. Verify all VS Code tasks work

### For Production

1. Implement actual device listing from persistent storage
2. Connect to real log system
3. Implement service start/stop via system controls
4. Add authentication layer
5. Production hardening

---

## 📚 Related Documentation

- [AGENTS.md](../AGENTS.md) — Development guidelines
- [docs/roadmap.md](../docs/roadmap.md) — Project roadmap
- [wizard/README.md](README.md) — Wizard Server overview

---

## 🏁 Success Criteria (v1.0.2.0)

✅ **Complete**

- [x] TUI interface with 11 command handlers
- [x] Integrated server + TUI launcher
- [x] VS Code tasks for all three modes
- [x] API endpoints for TUI control
- [x] Integration test suite
- [x] Comprehensive documentation

**Ready for:** Testing and feedback

**Next milestone:** TCZ distribution packaging

---

_Created: 2026-01-14_  
_Version: Wizard Dev Mode v1.0.0_
