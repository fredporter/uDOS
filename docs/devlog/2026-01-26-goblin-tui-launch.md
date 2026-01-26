# Goblin TUI & Auto-Dashboard Launch - 2026-01-26

**Status:** ✅ Complete  
**Scope:** Goblin MODE Playground enhancements

---

## What Was Built

### 1. Interactive TUI ✅

**New File:** `/dev/goblin/goblin_tui.py` (300+ lines)

**Features:**

- Interactive `goblin>` command prompt
- Server health checks
- Quick MODE testing commands
- Dashboard browser launcher
- Recent logs viewer
- Clean shutdown handling

**Commands:**

```
help     - Show available commands
status   - Check server health
modes    - List available MODEs
dash     - Open dashboard in browser
teletext - Quick teletext render test
terminal - Quick terminal render test
logs     - Show recent server logs
exit     - Exit TUI (prompts to stop server)
```

### 2. Auto-Dashboard Launch ✅

**Modified:**

- `/dev/goblin/bin/launch-goblin-server.sh`
- `/dev/goblin/bin/launch-goblin-dashboard.sh`
- `/dev/bin/Launch-Goblin-Dev.command`

**New Behavior:**

1. Server starts in **background** (not blocking)
2. Dashboard **auto-opens** in browser after 2-3 seconds
3. Interactive TUI launches with `goblin>` prompt
4. Clean exit: type `exit`, optionally stop server

---

## Launch Flow

### Old Behavior

```bash
./dev/bin/Launch-Goblin-Dev.command
# → Server starts (foreground, blocks terminal)
# → User sees logs scrolling
# → Must Ctrl+C to stop
# → No dashboard auto-open
```

### New Behavior

```bash
./dev/bin/Launch-Goblin-Dev.command
# → Server starts (background, PID shown)
# → Dashboard auto-opens in browser
# → TUI prompt appears: goblin>
# → Type 'help' for commands
# → Type 'exit' to quit cleanly
# → Prompts: "Stop Goblin server? [Y/n]"
```

---

## Example Session

```bash
$ ./dev/bin/Launch-Goblin-Dev.command

╔═══════════════════════════════════════════════════════════════╗
║              🧪 Goblin MODE Playground - TUI                  ║
╚═══════════════════════════════════════════════════════════════╝
Version: v0.2.0.0 | Port: 8767 | Experimental

✅ Server started (PID: 12345)
✅ Server: http://localhost:8767
✅ Dashboard: http://localhost:5174

Opening dashboard...
[Browser launches with http://localhost:5174]

Starting interactive TUI...

Available Commands:
  help     - Show this help
  status   - Check server status
  modes    - List available MODEs
  dash     - Open dashboard in browser
  teletext - Quick teletext test
  terminal - Quick terminal test
  logs     - Show recent server logs
  exit     - Exit TUI

goblin> status
✅ Server online
   Version: 0.2.0.0
   Status: ok

goblin> teletext
Testing Teletext MODE...

▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

✅ Teletext MODE working

goblin> modes
Available MODEs:
  1. Teletext - Retro patterns, ANSI art
  2. Terminal - Escape codes, color schemes

goblin> exit

Goblin TUI session ended

Stop Goblin server? [Y/n] y
✅ Server stopped
✅ Goblin Dev Server stopped
```

---

## Files Changed

### Created

1. `/dev/goblin/goblin_tui.py` - Interactive TUI
2. `/dev/goblin/TUI-GUIDE.md` - TUI documentation

### Modified

1. `/dev/goblin/bin/launch-goblin-server.sh`
   - Server runs in background
   - Launches TUI after startup
   - Prompts to stop server on exit

2. `/dev/goblin/bin/launch-goblin-dashboard.sh`
   - Auto-opens browser after 3 seconds
   - Uses macOS `open` command

3. `/dev/bin/Launch-Goblin-Dev.command`
   - Background server launch
   - Auto-open dashboard
   - TUI integration
   - Clean shutdown

4. `/dev/goblin/README.md`
   - Updated Quick Start section
   - Added TUI documentation links

---

## Technical Details

### Background Server Launch

```bash
# Start server in background, redirect output
python goblin_server.py > /dev/null 2>&1 &
SERVER_PID=$!

# Continue with TUI
python goblin_tui.py

# On exit, kill server
kill $SERVER_PID 2>/dev/null
```

### Auto-Open Dashboard

**Shell Script:**

```bash
# Open browser after 3-second delay
(sleep 3 && open http://localhost:5174) &
```

**Python TUI:**

```python
import webbrowser
webbrowser.open("http://localhost:5174")
```

### TUI Prompt Loop

```python
while self.running:
    command = input(f"\ngoblin> ").strip().lower()
    self.handle_command(command)
```

---

## Benefits

### User Experience

1. **Faster workflow** - No manual browser opening
2. **Cleaner terminal** - Server logs hidden
3. **Interactive testing** - Quick MODE commands
4. **Professional UX** - Like Wizard Server console

### Development

1. **Non-blocking** - Server runs in background
2. **Easy testing** - Built-in test commands
3. **Clean shutdown** - Prompts user before killing
4. **Reusable** - TUI can be extended with more commands

---

## Comparison

| Feature         | Old Launcher          | New Launcher              |
| --------------- | --------------------- | ------------------------- |
| **Server mode** | Foreground (blocking) | Background (non-blocking) |
| **Dashboard**   | Manual open           | Auto-opens in 3 seconds   |
| **Terminal**    | Logs scrolling        | Clean TUI prompt          |
| **Testing**     | Manual curl/browser   | Built-in commands         |
| **Shutdown**    | Ctrl+C                | `exit` + prompt           |
| **UX**          | Developer-focused     | User-friendly             |

---

## Integration

### With Self-Healing System

Launcher still runs self-healing check before starting:

```bash
python -m core.services.self_healer goblin
# → Checks dependencies, ports, permissions
# → Auto-repairs if needed
# → Then launches server + TUI
```

### With Dashboard

Dashboard launcher also auto-opens browser:

```bash
./dev/goblin/bin/launch-goblin-dashboard.sh
# → npm run dev starts
# → Browser opens after 3 seconds
# → No manual navigation needed
```

---

## Future Enhancements

### Planned TUI Commands

- `restart` - Restart server without exiting TUI
- `config` - Edit goblin.json interactively
- `deploy` - Deploy MODE to Core
- `benchmark` - Run performance tests
- `clear` - Clear terminal screen
- `history` - Show command history

### Multi-Terminal Support

```bash
# Launch all in one command
./dev/bin/Launch-Goblin-Full.command
# → Terminal 1: Server + TUI
# → Terminal 2: Dashboard auto-opens
# → Terminal 3: Logs tail -f
```

---

## See Also

- [Goblin TUI Guide](../dev/goblin/TUI-GUIDE.md)
- [Goblin README](../dev/goblin/README.md)
- [Goblin Quick Reference](../dev/goblin/QUICK-REFERENCE.md)

---

**Status:** Production Ready  
**Last Updated:** 2026-01-26  
**Tested:** ✅ macOS (launch scripts, browser auto-open, TUI prompt)  
**Next:** Roll out similar TUI to Wizard/Empire servers
