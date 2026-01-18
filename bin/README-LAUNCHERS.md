# 🚀 uDOS Launch Scripts Reference

All launch scripts are located in `/bin/` and automatically detect service availability via port checking.

---

## 📋 Quick Reference

| Launcher       | Command                          | Port | Purpose                                     | Status         |
| -------------- | -------------------------------- | ---- | ------------------------------------------- | -------------- |
| **Goblin Dev** | `./Launch-Goblin-Dev.command`    | 8767 | Experimental server (GitHub, AI, Workflows) | Development ⚙️ |
| **Wizard Dev** | `./Launch-Wizard-Dev.command`    | 8765 | Production server features                  | Production 🏭  |
| **uMarkdown**  | `./Launch-uMarkdown-Dev.command` | 5173 | Tauri desktop app + Goblin                  | Unstable 🎨    |
| **TUI**        | `./Launch-TUI.command`           | -    | Terminal user interface                     | Stable 📟      |
| **Dev Mode**   | `./Launch-Dev-Mode.command`      | -    | Combined launcher (TUI + services)          | Stable ✅      |

---

## 🎯 Usage Guide

### For Quick Development (Recommended)

**Option 1: Full Dev Environment**

```bash
./Launch-Dev-Mode.command
```

Launches TUI with all background services (Goblin, Wizard, API).

**Option 2: Individual Services**

**Goblin Dev Server** — For GitHub automation, AI requests, task scheduling

```bash
./Launch-Goblin-Dev.command
```

- Port: `8767`
- API: http://127.0.0.1:8767
- Docs: http://127.0.0.1:8767/docs
- Services: GitHub sync, Mistral AI, Workflow manager

**Wizard Production Server** — For production features

```bash
./Launch-Wizard-Dev.command
```

- Port: `8765`
- API: http://127.0.0.1:8765
- Production-stable features
- Device auth, plugin repository, AI routing

**uMarkdown App** — Desktop Tauri app + Goblin server

```bash
./Launch-uMarkdown-Dev.command
```

- Frontend: http://127.0.0.1:5173 (Tauri dev server)
- Goblin Backend: http://127.0.0.1:8767
- Requires: Rust toolchain, Node.js, npm
- Includes: Svelte UI, 5 markdown formats

**TUI** — Terminal interface

```bash
./Launch-TUI.command
```

- No port (local terminal)
- Shows available services on startup
- Links to other launchers

---

## 🔧 Shared Infrastructure

### `udos-urls.sh` — Service Discovery Helper

All launchers source this utility for:

- **Consistent color-coded output** (ANSI terminal colors)
- **Live port detection** (checks if service is running)
- **Service status display** (✅ running, ❌ stopped, ⏳ starting)
- **URL formatting** (standardized service links)

**Key Functions:**

```bash
# Display service category header
print_service_urls "Title Here"

# Display single service with status
print_service "Goblin" "http://127.0.0.1:8767" "Description" "✅"

# Display all services with live port checks
print_all_services

# Show common commands
print_quick_reference
```

**Example Output:**

```
═══════════════════════════════════════════════════════════════════════════
  ✅ Goblin Dev     http://127.0.0.1:8767    Experimental features
  ✅ Wizard Prod    http://127.0.0.1:8765    Production server
  ⏳ uMarkdown      http://127.0.0.1:5173    Tauri app dev
  ❌ API Server     http://127.0.0.1:5001    REST API
═══════════════════════════════════════════════════════════════════════════
```

---

## 📊 Service Architecture

```
┌──────────────────────────────────────┐
│   TUI (Local Terminal)               │
│   - Command handlers                 │
│   - Local execution                  │
└────────────┬─────────────────────────┘
             │
             ├─→ [8765] Wizard Server (Production)
             │           ├─ Device auth
             │           ├─ AI routing
             │           └─ Plugin repository
             │
             ├─→ [8767] Goblin Dev Server (Experimental)
             │           ├─ GitHub integration
             │           ├─ Mistral AI
             │           └─ Task scheduling
             │
             ├─→ [5001] API Server (Extensions)
             │           └─ REST/WebSocket API
             │
             └─→ [5173] Tauri App (Frontend Dev)
                       └─ uMarkdown (Svelte UI)
```

---

## 🚨 Common Issues & Fixes

### Issue: "Port XXXX already in use"

**Solution:**

```bash
# Find process using port
lsof -i :8767

# Kill process
kill -9 <PID>

# Or let the launcher auto-detect and suggest fix
```

### Issue: "Virtual environment not found"

**Solution:**

```bash
# Create venv
python3 -m venv .venv

# Run launcher again
./Launch-Goblin-Dev.command
```

### Issue: Tauri app fails to start (uMarkdown)

**Common Causes & Fixes:**

1. **Rust not installed**

   ```bash
   rustup update
   rustup target add aarch64-apple-darwin  # or x86_64-apple-darwin
   ```

2. **Cargo cache corrupted**

   ```bash
   rm -rf src-tauri/target
   cargo clean
   ```

3. **npm dependencies missing**

   ```bash
   npm install
   npm run tauri dev
   ```

4. **Goblin server not starting**
   - Check port 8767: `lsof -i :8767`
   - Check Python venv exists: `ls -la .venv/`
   - Run Goblin separately: `./Launch-Goblin-Dev.command`

### Issue: "ModuleNotFoundError: No module named 'dev.goblin'"

**Solution:**

```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="/Users/fredbook/Code/uDOS:$PYTHONPATH"

# Run launcher again
./Launch-Goblin-Dev.command
```

---

## 🔍 Debugging & Logs

### Check Service Status

```bash
# Which services are running?
lsof -i -P -n | grep LISTEN

# Goblin running?
lsof -i :8767

# Wizard running?
lsof -i :8765

# App dev server running?
lsof -i :5173
```

### View Recent Logs

```bash
# TUI session commands
tail -f memory/logs/session-commands-$(date +%Y-%m-%d).log

# Tauri/App errors
tail -f memory/logs/tauri-dev-*.log

# API server
tail -f memory/logs/api_server.log

# All logs
ls -lht memory/logs/*.log | head -10
```

### Run with Verbose Output

Each launcher can be modified to add verbose flags:

**Goblin:**

```bash
# Edit Launch-Goblin-Dev.command, change:
python "$PROJECT_ROOT/dev/goblin/goblin_server.py"

# To:
python -u "$PROJECT_ROOT/dev/goblin/goblin_server.py" --debug
```

---

## 📦 Environment Setup

### Virtual Environment

All Python services use `.venv/` virtual environment:

```bash
# Create (one-time)
python3 -m venv .venv

# Activate manually
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

Launchers automatically:

- Check venv exists
- Activate venv before running
- Set `PYTHONPATH` for module imports
- Create log directory

### Configuration Files

**Goblin Config** (local, gitignored):

```
dev/goblin/config/goblin.json
```

**Wizard Config** (local, gitignored):

```
wizard/config/wizard.json
```

**Environment Variables** (set by launchers):

- `PYTHONPATH` — Include project root
- `VITE_API_URL` — Frontend API endpoint (uMarkdown)
- `TAURI_PRIVATE_KEY` — Optional Tauri signing key

---

## 🚀 Advanced Usage

### Run Multiple Services in Parallel

**Terminal 1:** Start Goblin

```bash
./Launch-Goblin-Dev.command
```

**Terminal 2:** Start Wizard

```bash
./Launch-Wizard-Dev.command
```

**Terminal 3:** Start uMarkdown

```bash
./Launch-uMarkdown-Dev.command
```

**Terminal 4:** Start TUI (connects to all services)

```bash
./Launch-TUI.command
```

### Create Custom Launcher

Copy an existing launcher and modify:

```bash
cp bin/Launch-Goblin-Dev.command bin/Launch-MyService.command
chmod +x bin/Launch-MyService.command

# Edit the file and update:
# - PORT number
# - Python module path
# - Service description
# - Environment variables
```

### Integration with VS Code

Add to `.vscode/tasks.json`:

```json
{
  "label": "Launch Goblin Dev",
  "type": "shell",
  "command": "./bin/Launch-Goblin-Dev.command",
  "group": { "kind": "none", "isDefault": false },
  "isBackground": true
}
```

Then run: `Cmd+Shift+P` → "Tasks: Run Task" → "Launch Goblin Dev"

---

## 📞 Support

### Stuck?

1. Check logs in `memory/logs/`
2. Verify port availability: `lsof -i :PORT`
3. Ensure venv exists: `ls -la .venv/`
4. Check PYTHONPATH: `echo $PYTHONPATH`

### Questions?

See [AGENTS.md](../AGENTS.md) and [docs/\_index.md](../docs/_index.md) for architecture.

---

**Last Updated:** 2026-01-17  
**Version:** Launcher System v1.0.0  
**Status:** Production Ready ✅
