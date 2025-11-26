# POKE Command Quick Reference

**Version:** v1.5.0+
**Purpose:** Manage web-based extension servers
**Architecture:** Python subprocess (non-blocking as of v1.6.0)

---

## Basic Commands

### Start a Server
```bash
POKE START <name> [--port N] [--no-browser]
```

**Examples:**
```bash
POKE START typo              # Start typo editor (port 5173)
POKE START dashboard         # Start dashboard (port 8887)
POKE START terminal --port 9000  # Custom port
```

**Behavior (v1.6.0+):**
- Returns immediately (non-blocking)
- Server starts in background
- Status: "starting" for ~3 seconds
- Check with `POKE STATUS` to confirm ready

---

### Check Status
```bash
POKE STATUS [name]
```

**Examples:**
```bash
POKE STATUS           # All servers
POKE STATUS typo      # Specific server
```

**Output:**
```
🟢 typo is running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 PID: 19176
🔗 URL: http://localhost:5173
🔌 Port: 5173 ✅
⏱️  Uptime: 2h 15m
📋 Logs: memory/logs/typo_5173.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏹️  Stop: POKE STOP typo
```

**Status Indicators:**
- 🟢 Running and responding
- 🟡 Process alive but port not ready (starting)
- ❌ Not running

---

### Stop a Server
```bash
POKE STOP <name>
```

**Example:**
```bash
POKE STOP typo
```

**Behavior:**
1. Sends SIGTERM (graceful shutdown)
2. Waits up to 5 seconds
3. Sends SIGKILL if still running
4. Cleans up state file

---

### Restart a Server
```bash
POKE RESTART <name>
```

**Example:**
```bash
POKE RESTART dashboard
```

Equivalent to: `POKE STOP + POKE START`

---

## Available Servers

### Core Extensions (Built-in)
- `dashboard` - NES-style customizable dashboard (port 8887)
- `terminal` - C64 PETSCII terminal (port 8890)
- `teletext` - BBC Teletext viewer (port 9002)
- `markdown` - Knowledge base viewer (port 9000)
- `character` - Pixel art editor (port 8891)

### Cloned Extensions (External)
- `typo` - Web markdown editor (port 5173)
  - Location: `extensions/cloned/typo/`
  - Requires: Node.js, npm

---

## Server Management

### List All Available
```bash
POKE LIST
```

Shows installed status and running state for all extensions.

### Health Check
```bash
POKE HEALTH
```

**Output:**
```
🏥 Server Health Report
========================================
📊 Summary:
   ✅ Running: 2
   ❌ Stopped: 3
   📈 Total: 5

📊 System Health: 40.0%
⚠️  System health is moderate
```

---

## Troubleshooting

### Server Won't Start

**Check logs:**
```bash
cat memory/logs/typo_5173.log
```

**Common issues:**
- Port already in use
- Missing dependencies (npm packages)
- Permission errors

**Fix port conflict:**
```bash
# Find process using port
lsof -ti:5173

# Kill it
kill -9 <PID>

# Or use different port
POKE START typo --port 5174
```

### Server Shows "Starting" Forever

**Check process:**
```bash
ps -p <PID>
```

**View live logs:**
```bash
tail -f memory/logs/typo_5173.log
```

**Restart:**
```bash
POKE STOP typo
POKE START typo
```

### TUI Becomes Unresponsive

**v1.5.x (old):** `time.sleep(2)` blocked main thread
**v1.6.0+ (fixed):** Non-blocking startup

**If still frozen:**
1. Kill main uDOS process: `kill -9 <PID>`
2. Clean state file: `rm sandbox/.server_state.json`
3. Restart: `python uDOS.py`

---

## State Management

### State File Location
```bash
sandbox/.server_state.json
```

### State File Format
```json
{
  "typo": {
    "pid": 19176,
    "port": 5173,
    "started_at": 1764115137.262,
    "url": "http://localhost:5173",
    "log_file": "memory/logs/typo_5173.log",
    "status": "running"
  }
}
```

### Clean Stale State
```bash
# Automatic on next POKE STATUS
POKE STATUS

# Manual cleanup
rm sandbox/.server_state.json
```

---

## Process Management

### How Servers Are Spawned

**v1.6.0+ Architecture:**
```python
subprocess.Popen(
    [python, 'extensions_server.py', 'dashboard'],
    stdout=log_file,
    stderr=subprocess.STDOUT,
    start_new_session=True  # Detach from parent
)
```

**Benefits:**
- Background process (doesn't block uDOS)
- Survives uDOS restart (if detached)
- Logs captured to file

**Cleanup on uDOS Exit:**
```python
ServerManager.cleanup_all()  # Stops all servers
```

### Manual Process Management

**List all server processes:**
```bash
ps aux | grep 'extensions_server.py\|npm run dev'
```

**Kill all servers:**
```bash
pkill -f 'extensions_server.py'
pkill -f 'npm run dev'
```

**Kill specific port:**
```bash
lsof -ti:5173 | xargs kill -9
```

---

## Extension Development

### Add New Server

1. **Create extension directory:**
   ```bash
   mkdir -p extensions/core/myserver
   ```

2. **Add to ServerManager:**
   ```python
   # In server.py
   server_map = {
       'myserver': 'myserver',  # name -> extension_name
       ...
   }
   ```

3. **Set default port:**
   ```python
   default_ports = {
       'myserver': 8900,
       ...
   }
   ```

4. **Test:**
   ```bash
   POKE START myserver
   POKE STATUS myserver
   ```

### Server Requirements

- **Static server:** HTML/CSS/JS files only
- **Node server:** package.json with `npm run dev`
- **Python server:** Flask/FastAPI app
- **Logs:** Must write to stdout/stderr (captured to log file)

---

## Best Practices

### Starting Servers
- ✅ Use `POKE START` (non-blocking)
- ✅ Check status with `POKE STATUS` after ~3 seconds
- ❌ Don't run multiple starts in rapid succession
- ❌ Don't assume immediate availability

### Stopping Servers
- ✅ Use `POKE STOP` for graceful shutdown
- ✅ Wait 1-2 seconds before restart
- ❌ Don't `kill -9` unless necessary
- ❌ Don't delete state file while servers running

### Debugging
- ✅ Check logs first: `cat memory/logs/<name>_<port>.log`
- ✅ Verify port availability: `lsof -ti:<port>`
- ✅ Test server manually: `curl http://localhost:<port>`
- ❌ Don't ignore health check warnings

---

## API (For Extension Developers)

### Python Integration
```python
from extensions.core.server_manager.server import ServerManager

mgr = ServerManager()

# Start server
success, msg = mgr.start_server('typo', port=5173, open_browser=True)

# Check status
status = mgr.get_status('typo')

# Stop server
success, msg = mgr.stop_server('typo')
```

### Command Handler Integration
```python
# In system_handler.py
def handle_output(self, params, grid, parser):
    from extensions.core.server_manager.server import ServerManager
    server_manager = ServerManager()

    if params[0] == 'START':
        return server_manager.start_server(params[1])
```

---

## FAQ

**Q: Why Python instead of Rust?**
A: Python subprocess is sufficient, cross-platform, and easy to debug. Rust would be overkill for simple process spawning.

**Q: Can servers survive uDOS restart?**
A: Yes, if started with `start_new_session=True` (default in v1.6.0+).

**Q: How do I auto-start servers on uDOS launch?**
A: Add to `memory/startup.uscript`:
```
POKE START dashboard
POKE START typo
```

**Q: Can I run multiple instances of the same server?**
A: Yes, with different ports:
```bash
POKE START typo --port 5173
POKE START typo --port 5174  # Not currently supported - needs name aliasing
```

**Q: How do I see server logs in real-time?**
A: Use `tail -f memory/logs/<name>_<port>.log`

---

## Changelog

### v1.6.0 (2025-11-26)
- ✅ **Fixed:** TUI non-responsiveness
- ✅ **Changed:** Removed blocking `time.sleep(2)` validation
- ✅ **Added:** Async health checks via `_is_port_open()`
- ✅ **Added:** Status indicators (🟢/🟡/❌)
- ✅ **Added:** Non-blocking browser opening (threading)

### v1.5.0
- Initial POKE command implementation
- Basic server management (start/stop/status)
- State persistence in JSON

---

**See Also:**
- `dev/notes/tui-responsiveness-analysis.md` - Technical deep-dive
- `extensions/core/server_manager/server.py` - Implementation
- `wiki/Extensions-Server.md` - Extension development guide
