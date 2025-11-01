# Quick Start: uDOS Web Terminal

## Instant Launch

### From CLI
```bash
# Start uDOS
./start_udos.sh

# Launch web terminal
🌀 uDOS> WEB
```

Browser opens automatically to http://localhost:8888

### Manual Launch
```bash
cd extensions/web/terminal
python3 server.py
# Open browser to http://localhost:8888
```

## Web Terminal Commands

Once in the browser terminal:

### Essential Commands
```
🌀 uDOS> HELP          # Show all commands
🌀 uDOS> DASH          # ASCII dashboard
🌀 uDOS> STATUS        # Terminal info
🌀 uDOS> CLEAR         # Clear screen
```

### Theme Commands
```
🌀 uDOS> THEME MATRIX  # Green on black (default)
🌀 uDOS> THEME AMBER   # Amber CRT style
🌀 uDOS> THEME CYAN    # Cyan on black
🌀 uDOS> THEME MONO    # White on black
```

### Keyboard Shortcuts
- `Ctrl+C` - Cancel command
- `Ctrl+L` - Clear screen
- `↑/↓` - Command history
- `Backspace` - Delete character
- `Enter` - Execute command

## Features

✅ **Full Terminal Emulation** - xterm.js 5.3.0
✅ **ASCII Art Support** - Box drawing, Unicode, colors
✅ **Splash Screen** - uDOS branding on load
✅ **Command History** - Up/down arrow navigation
✅ **Multiple Themes** - 4 color schemes
✅ **Responsive** - Adapts to window size
✅ **Independent** - Runs alongside CLI instance

## Auto-Start Servers

uDOS automatically starts required web servers:

- **Port 9000** - Markdown Viewer
- **Port 8887** - Dashboard
- **Port 8888** - Web Terminal

Check server status:
```bash
🌀 uDOS> REPAIR check
```

## Troubleshooting

### Server Won't Start
```bash
# Check if port in use
lsof -i :8888

# Kill process if needed
kill -9 <PID>

# Try different port
cd extensions/web/terminal
python3 server.py --port 9999
```

### Terminal Not Loading
1. Check browser console (F12)
2. Verify server is running: `lsof -i :8888`
3. Check internet connection (xterm.js loads from CDN)
4. Try different browser

### Commands Not Working
Currently commands are mocked. Full backend integration coming in Phase 2.

## What's Next

### Phase 2 (Coming Soon)
- WebSocket backend connection
- Real command execution
- File operations
- AI integration

### Future Features
- Multi-tab support
- Split panes
- Session recording
- Collaborative sessions

## More Info

📖 Full documentation: `extensions/web/terminal/README.md`
📝 Technical details: `docs/V1.2-DYNAMIC-COMMANDS-WEB-TERMINAL.md`
💬 Help: Type `HELP` in either CLI or web terminal
