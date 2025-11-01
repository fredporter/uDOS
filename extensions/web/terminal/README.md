# 🎮 uDOS Enhanced NES Terminal v1.3

A fully-featured retro terminal with NES.css styling, viewport control, theme switching, and splash screen support.

## ✨ Features

### � **Visual Features**
- **NES.css Styling** - Authentic 8-bit retro gaming aesthetic
- **Theme Switching** - Toggle between dark and light modes
- **Viewport Control** - 5 viewport sizes (Compact → Standard → Large → Wide → Fullscreen)
- **Splash Screen** - Animated ASCII art display
- **Block Graphics** - Full support for box drawing, blocks, and symbols
- **Toast Notifications** - Non-intrusive status messages

### 🛠️ **Functional Features**
- **Command History** - Navigate with ↑/↓ arrows
- **Settings Persistence** - Theme, viewport, and font size saved to localStorage
- **Live Status Updates** - Real-time connection monitoring
- **Modal Settings** - Comprehensive settings dialog
- **Keyboard Shortcuts** - Quick access to common functions
- **Responsive Design** - Works on desktop and mobile

## Usage

### From CLI
```bash
# Launch web terminal in browser
WEB
```

### From Web Dashboard
Navigate to http://localhost:8887 and click "Web Terminal" card.

### Manual Launch
```bash
cd extensions/web/terminal
python3 server.py --port 8888
# Then open browser to http://localhost:8888
```

## Commands

### Built-in Commands
All these work in the web terminal:

- `HELP` - Show command reference
- `DASH` / `DASHBOARD` - Display ASCII dashboard
- `STATUS` - Show terminal status
- `THEME <name>` - Change color theme (MATRIX|AMBER|CYAN|MONO)
- `CLEAR` / `BLANK` - Clear terminal screen

### Keyboard Shortcuts
- `Ctrl+C` - Cancel current command
- `Ctrl+L` - Clear screen (alternative to CLEAR)
- `Up/Down Arrow` - Navigate command history
- `Backspace` - Delete character
- `Enter` - Execute command

## Architecture

### Files
```
extensions/web/terminal/
├── index.html          # Main terminal interface
├── server.py           # HTTP server
└── README.md           # This file
```

### Technology Stack
- **Frontend**: xterm.js, vanilla JavaScript
- **Backend**: Python http.server (for now)
- **Future**: WebSocket connection to uDOS backend

## Development

### Current Status
✅ **Completed:**
- xterm.js integration
- Splash screen and branding
- ASCII dashboard
- Built-in help system
- Theme switching
- Command history
- Server auto-start

🔄 **In Progress:**
- WebSocket connection to uDOS backend
- Full command execution
- File operations
- AI integration

📋 **Planned:**
- Multi-user support
- Session persistence
- Cloud deployment
- Mobile optimization

### Adding New Commands

Commands are currently mocked in `index.html`. To add a new command:

```javascript
// In executeCommand() function
else if (upperCmd === 'YOURCOMMAND') {
    handleYourCommand(cmd);
}

// Add handler function
function handleYourCommand(cmd) {
    term.writeln('Your command output');
    term.writeln('Multiple lines supported');
}
```

### Customizing Themes

Edit the theme colors in `index.html`:

```javascript
function applyTheme(fg, bg) {
    term.options.theme.foreground = fg;  // Text color
    term.options.theme.background = bg;  // Background color
    term.options.theme.cursor = fg;      // Cursor color
    document.body.style.background = bg;
    term.writeln('\x1b[32m✅ Theme applied!\x1b[0m');
}
```

## Integration with uDOS

### Auto-Start on Health Check
The startup health check (`uDOS_startup.py`) automatically:
1. Checks if web terminal server is running on port 8888
2. Starts the server if not running
3. Reports status in health check output

### Command Handler
The `WEB` command (`uDOS_commands.py`):
1. Checks if terminal directory exists
2. Starts server if needed
3. Opens browser to terminal URL
4. Provides status feedback

## Troubleshooting

### Server Won't Start
```bash
# Check if port 8888 is in use
lsof -i :8888

# Kill existing process
kill -9 <PID>

# Or use different port
cd extensions/web/terminal
python3 server.py --port 9999
```

### Terminal Not Loading
1. Check browser console for errors
2. Verify xterm.js CDN is accessible
3. Check server.py is running
4. Try different browser

### Commands Not Working
Commands are currently mocked. Full backend integration coming soon via WebSocket.

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic terminal emulation
- ✅ Splash screen and dashboard
- ✅ Theme switching
- ✅ Command history

### Phase 2 (Next)
- 🔄 WebSocket backend connection
- 🔄 Full command execution
- 🔄 File browser integration
- 🔄 Real-time system status

### Phase 3 (Future)
- 📋 Multi-tab support
- 📋 Split panes
- 📋 Session recording/playback
- 📋 Collaborative sessions

## Resources

- [xterm.js Documentation](https://xtermjs.org/)
- [xterm.js API Reference](https://xtermjs.org/docs/api/terminal/terminal/)
- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [ASCII Art Generator](http://patorjk.com/software/taag/)

## License

Part of uDOS - Unified Data Operations System
See main LICENSE.txt for details.
