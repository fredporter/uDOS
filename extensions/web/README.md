# uDOS Web Extensions v1.0.1

**Universal Data Operating System - Web-Based Extensions Collection**

A comprehensive suite of web-based extensions providing a nostalgic yet modern interface for the uDOS ecosystem, featuring classic Mac styling, CSS framework showcases, and integrated screensaver systems.

## 🌟 What's New in v1.0.1

### 🎨 CSS Framework Showcase
- **4 Retro CSS Frameworks** with live interactive demos
- **Unified launcher** for all framework servers
- **Complete component galleries** showcasing each framework's capabilities

### 🖥️ Desktop Interface Revolution
- **macOS-style desktop** with icon grid layout
- **Light/Dark mode toggle** with authentic retro styling
- **After Dark screensaver integration** with multiple modes
- **Real-time server monitoring** and status indicators

### 🔤 Enhanced Typography
- **VT323 chunky retro fonts** throughout all interfaces
- **Authentic terminal aesthetic** with proper spacing and sizing

## 📦 Extension Collection

### 🎯 Core Extensions

#### Dashboard (Port 8001)
Modern desktop interface with classic Mac styling
- **Features**: Desktop icons, theme switching, screensavers, activity logging
- **Styling**: Classic Mac System 6/8.1 aesthetic with modern functionality
- **Screensavers**: Starfield, Matrix Rain, DVD Logo, Digital Clock

#### CSS Framework Showcase (Ports 8882-8885)
Live demos of 4 retro CSS frameworks:
- **classic.css** (8885) - Mac OS 8.1 interface components
- **NES.css** (8884) - 8-bit Nintendo-style elements
- **system.css** (8883) - Classic Mac System 6 styling
- **after-dark-css** (8882) - Screensaver collection

### 🛠️ Development Tools

#### Terminal (Port 8890)
Web-based terminal interface
- **Features**: Command execution, file system access, session persistence
- **Integration**: Direct uDOS command system access

#### Markdown Viewer (Port 8889)
Document viewer and light editor
- **Features**: Live preview, syntax highlighting, file browser integration
- **Formats**: Markdown, text files, documentation

#### Font Editor (Port 8888)
Bitmap font creator and editor
- **Features**: Character mapping, font preview, multiple export formats
- **Use Case**: Create custom fonts for retro interfaces

### 🎨 External Integrations

#### Typo Editor (Port 5173)
Modern markdown editor with live preview
- **Repository**: [rossrobino/typo](https://github.com/rossrobino/typo)
- **Features**: Slide mode, code execution, File System API, auto-save
- **Requirements**: Node.js v16+

## 🚀 Quick Start

### Automated Launch (Recommended)

```bash
# Launch all CSS framework demos
cd /Users/fredbook/Code/uDOS/extensions/web/css-frameworks
python3 launch_all.py

# Launch individual extensions
cd /Users/fredbook/Code/uDOS/extensions/web
python3 launch_web.py dashboard 8001
```

### Individual Extension Setup

```bash
# Dashboard (main interface)
cd dashboard && python3 -m http.server 8001

# CSS Framework demos
cd css-frameworks && python3 launch_all.py

# Terminal interface
cd terminal && python3 -m http.server 8890

# Markdown viewer
cd markdown-viewer && python3 -m http.server 8889

# Font editor
cd font-editor && python3 -m http.server 8888
```

### Typo Editor Setup (External)

```bash
# Install Node.js dependencies
cd /path/to/typo  # External repository
npm install
npm run dev  # Runs on port 5173
```

## 🎨 CSS Framework Details

### classic.css - Mac OS 8.1 Styling
- **Demo**: http://localhost:8885
- **Features**: Authentic Mac OS 8.1 window chrome, buttons, dialogs
- **Components**: 50+ interface elements with period-accurate styling
- **License**: MIT - https://github.com/NigelOToole/classic.css

### NES.css - 8-bit Nintendo Interface
- **Demo**: http://localhost:8884
- **Features**: Pixel-perfect 8-bit styling, retro gaming aesthetic
- **Components**: Buttons, containers, dialogs with authentic NES look
- **License**: MIT - https://github.com/nostalgic-css/NES.css

### system.css - Classic Mac System 6
- **Demo**: http://localhost:8883
- **Features**: Early Mac interface with file manager aesthetics
- **Components**: Clean, minimal styling with authentic Mac feel
- **License**: MIT - https://github.com/sakofchit/system.css

### after-dark-css - Screensaver Collection
- **Demo**: http://localhost:8882
- **Features**: 8 different CSS-based screensaver modes
- **Integration**: Full screensaver system in main dashboard
- **License**: MIT - https://github.com/bryanbraun/after-dark-css

## 🖥️ Dashboard Features

### Desktop Interface
- **Icon Grid Layout**: Clean 6-column desktop with proper spacing
- **Status Indicators**: Real-time server status on each icon
- **Color-Coded Folders**: Visual organization (Sandbox=yellow, Memory=green, etc.)
- **Double-Click Actions**: Open applications or dashboard

### Theme System
- **Light Mode**: Classic Mac gray (#c0c0c0) with dot pattern background
- **Dark Mode**: Terminal green (#00ff00) on black with retro aesthetics
- **Toggle**: 🌓 button in menu bar or `⌘T` keyboard shortcut
- **Persistence**: Theme preference saved across sessions

### Screensaver Integration
- **Starfield**: Animated twinkling stars across the screen
- **Matrix Rain**: Falling green characters in authentic Matrix style
- **DVD Logo**: Bouncing uDOS logo with color changes
- **Digital Clock**: Retro terminal-style clock display
- **Controls**: Launch from View menu or 🌌 desktop icon, exit with ESC

### Activity System
- **Real-Time Logging**: Timestamped activity entries
- **Server Monitoring**: Live status updates for all extensions
- **Performance Metrics**: Memory usage, uptime, request counts

## ⌨️ Keyboard Shortcuts

### Global Shortcuts
- `⌘T` - Toggle Light/Dark Mode
- `⌘R` - Refresh Dashboard
- `⌘S` - Open Sandbox Workspace
- `⌘M` - Open Memory Workspace
- `⌘D` - Open Data Workspace
- `⌘,` - System Preferences
- `ESC` - Exit Screensaver or Close Dashboard

### Screensaver Controls
- `ESC` - Exit current screensaver
- Click anywhere - Exit screensaver
- View Menu - Access all screensaver modes

## 🔧 Technical Architecture

### Dependencies
- **Python 3.8+** - HTTP servers and launch scripts
- **Node.js 16+** - Typo editor (external)
- **Modern Browser** - Chrome, Firefox, Safari (current versions)

### Port Allocation
- **8001** - Main Dashboard Interface
- **8882** - After Dark CSS Demo
- **8883** - System.css Demo
- **8884** - NES.css Demo
- **8885** - Classic.css Demo
- **8888** - Font Editor
- **8889** - Markdown Viewer
- **8890** - Terminal Interface
- **5173** - Typo Editor (external)

### File Structure
```
extensions/web/
├── version-manifest.json     # Version tracking and feature manifest
├── CHANGELOG-v1.0.1.md      # Detailed release notes
├── dashboard/               # Main desktop interface
├── css-frameworks/          # CSS framework showcase
│   ├── launch_all.py       # Unified launcher
│   ├── classic-demo/       # Mac OS 8.1 demo
│   ├── nes-demo/           # Nintendo 8-bit demo
│   ├── system-demo/        # System 6 demo
│   └── afterdark-demo/     # Screensaver demo
├── terminal/               # Web terminal
├── markdown-viewer/        # Document viewer
├── font-editor/           # Bitmap font editor
└── shared/                # Common resources
    ├── classic.css        # Shared styling
    ├── fonts/            # Font collection
    └── icons/           # Desktop icons
```

## 🎯 Use Cases

### Development Environment
- **Live CSS Testing** - Preview framework styling in real-time
- **Documentation Writing** - Markdown editing with live preview
- **Font Creation** - Design bitmap fonts for retro projects
- **Terminal Access** - Web-based command line interface

### Nostalgic Computing Experience
- **Authentic Retro Feel** - Period-accurate interface styling
- **Screensaver Nostalgia** - Classic computer screensaver modes
- **Typography** - Chunky bitmap fonts and authentic spacing
- **Desktop Metaphor** - Familiar icon-based desktop interaction

### Educational & Reference
- **CSS Framework Gallery** - Learn from well-designed retro frameworks
- **Interface Design History** - Experience different UI paradigms
- **Web Technology Showcase** - Modern web tech with retro aesthetics

## 🐛 Troubleshooting

### Common Issues

**Port Conflicts**
```bash
# Check for running servers
lsof -i :8001  # Replace with specific port

# Kill existing process
kill -9 PID_NUMBER
```

**Missing Dependencies**
```bash
# Ensure Python 3.8+
python3 --version

# For Typo editor - ensure Node.js 16+
node --version
npm --version
```

**Theme Not Persisting**
- Check browser localStorage permissions
- Ensure JavaScript is enabled
- Clear browser cache if needed

**Screensavers Not Working**
- Verify modern browser (Chrome/Firefox/Safari current)
- Check JavaScript console for errors
- Ensure CSS animations are enabled

### Performance Optimization

**Memory Usage**
- Close unused browser tabs
- Restart servers periodically for long sessions
- Monitor system resources with Activity Monitor

**Loading Speed**
- Use local network (avoid VPN for localhost)
- Clear browser cache periodically
- Ensure adequate disk space

## 📚 Documentation

### Framework Documentation
- [classic.css Documentation](https://github.com/NigelOToole/classic.css)
- [NES.css Documentation](https://github.com/nostalgic-css/NES.css)
- [system.css Documentation](https://github.com/sakofchit/system.css)
- [after-dark-css Documentation](https://github.com/bryanbraun/after-dark-css)
- [Typo Editor Documentation](https://github.com/rossrobino/typo)

### uDOS Integration
- See main uDOS documentation for server management
- Extension commands available through uDOS command system
- Workspace integration with main uDOS file structure

## 🤝 Contributing

### Adding New CSS Frameworks
1. Create demo directory in `css-frameworks/`
2. Add framework showcase HTML
3. Update `launch_all.py` with new port
4. Add framework to `version-manifest.json`
5. Update documentation

### Enhancing Existing Extensions
1. Fork the repository
2. Make changes in appropriate extension directory
3. Test all functionality
4. Update version numbers and changelog
5. Submit pull request with detailed description

## � License & Attribution

**uDOS Web Extensions**: MIT License

**Third-Party Frameworks**:
- classic.css - MIT License
- NES.css - MIT License
- system.css - MIT License
- after-dark-css - MIT License
- Typo Editor - MIT License
- VT323 Font - SIL Open Font License

See `version-manifest.json` for complete attribution details.

---

**uDOS Web Extensions v1.0.1** - Bringing the golden age of computing to the modern web with authentic styling, rich functionality, and nostalgic charm. 🖥️✨

**Options:**
- `--port <number>`: Use a different port
- `--no-browser`: Don't auto-open browser

```bash
🔮 server start typo --port 3000
🔮 server start typo --no-browser
```

#### Edit Files

```bash
🔮 edit --web myfile.md
# Starts typo server if not running, opens browser
```

#### Check Status

```bash
🔮 server status typo
# Shows: Running, PID, URL, uptime
```

#### Stop the Server

```bash
🔮 server stop typo
```

#### List All Servers

```bash
🔮 server list
```

### Manual Usage

```bash
cd extensions/web/typo
npm run dev
# Opens on http://localhost:5173
```

## File Bridge (Coming Soon)

Future updates will include automatic file bridging:
- Auto-load files from uDOS when opening
- Auto-save back to uDOS filesystem
- Real-time sync between browser and disk
- URL parameter support for direct file loading

**Current Workaround:**
1. Start typo: `server start typo`
2. Manually open/save files in the web interface
3. Files must be loaded using browser's file picker

## Configuration

### Default Port

Default: `5173` (Vite development server)

Change in uDOS command:
```bash
🔮 server start typo --port 8080
```

### Server State

Server state is tracked in: `sandbox/.server_state.json`

Contains:
- PID (process ID)
- Port number
- Start time
- URL

## Troubleshooting

### Port Already in Use

```
❌ Port 5173 is already in use
```

**Solution:** Use a different port or stop the conflicting process
```bash
🔮 server start typo --port 5174
```

### Node.js Not Found

```
❌ Node.js not found
```

**Solution:** Install Node.js
- macOS: `brew install node`
- Linux: `sudo apt install nodejs npm`
- Windows: Download from https://nodejs.org

### Dependencies Not Installed

```
⚠️  Dependencies not installed
```

**Solution:** Reinstall
```bash
cd extensions/web/typo
npm install
```

### Server Won't Stop

```bash
# Find and kill manually
ps aux | grep "npm run dev"
kill <PID>
```

Or use force stop:
```bash
🔮 server stop typo
# If that fails, manually clean up
rm sandbox/.server_state.json
```

## Development

### Local Changes

If you modify the typo source:

```bash
cd extensions/web/typo
npm run dev  # Development mode with hot reload
npm run build  # Production build
```

### Upstream Updates

Update to latest typo version:

```bash
cd extensions/web/typo
git pull origin main
npm install
```

## Architecture

```
uDOS
 └── extensions/
      └── web/
           └── typo/
                ├── src/           # Svelte source files
                ├── static/        # Static assets
                ├── package.json   # Dependencies
                ├── vite.config.ts # Build configuration
                └── node_modules/  # Installed packages (gitignored)
```

### Integration Points

1. **ServerManager** (`core/uDOS_server.py`)
   - Starts/stops npm dev server
   - Tracks process state
   - Manages ports

2. **EditorManager** (`core/uDOS_editor.py`)
   - Detects web mode
   - Calls ServerManager
   - Opens browser

3. **CommandHandler** (`core/uDOS_commands.py`)
   - `SERVER` commands
   - `EDIT --web` flag

## License

Typo is licensed under the MIT License.
See: https://github.com/rossrobino/typo/blob/main/LICENSE.md

## Links

- **Upstream Repository**: https://github.com/rossrobino/typo
- **Live Demo**: https://typo.robino.dev
- **Component Library**: https://drab.robino.dev
