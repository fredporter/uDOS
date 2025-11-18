# uDOS Web Terminal v1.0.24

Modern web-based terminal with C64 aesthetics, full uDOS core integration, and advanced character support.

## Features

### 🎨 Visual Design
- **C64 Authentic Fonts**: PetMe64/128 fonts for genuine Commodore 64 look
- **Synthwave DOS Palette**: Electric blues, magentas, and cyans
- **80×30 Character Grid**: Standard terminal dimensions, perfectly centered
- **Color Cycle Splash**: Animated background during boot sequence
- **Responsive Scrollbar**: Vertical scrolling for output overflow

### 🔤 Character Support
- **PETSCII Characters**: Full C64 character set
- **Block Graphics**: Drawing characters for boxes, borders, and charts
- **Monosort Emoji**: Monochrome emoji suitable for terminal display
- **Box Drawing**: Single and double-line box characters

### ⚡ Core Integration
- **uDOS Command System**: Full integration with core command handlers
- **Web CLI I/O**: HTTP API communication with uDOS core
- **Fallback Mode**: Standalone operation when core is unavailable
- **Session Management**: Persistent terminal sessions

### 🎮 Interactive Features
- **Function Keys (F1-F8)**: Quick access to common commands
- **Command History**: Navigate previous commands with ↑/↓
- **Character Reference**: F8 opens PETSCII & emoji panel
- **Auto-scroll**: Output viewport scrolls to bottom automatically

## 🚀 Quick Start

### Launch Server (v1.0.25 Unified Server)
```bash
# From terminal directory
./start.sh

# Or from extensions/core directory
./launch.sh terminal

# Or directly with Python
python3 extensions_server.py terminal
```

Opens at: `http://localhost:8889`

## Usage

### Starting the Terminal

```bash
# Open in browser
open index.html

# Or serve via HTTP
python -m http.server 8000
# Then navigate to http://localhost:8000
```

### Connecting to uDOS Core

The terminal automatically connects to uDOS core on `http://localhost:8890`.

If core is not available, terminal runs in standalone mode with limited command set.

### Basic Commands

```
HELP        - Show command list
STATUS      - System status
LIST        - List directory
CLEAR       - Clear screen
GUIDE       - Terminal guide
VERSION     - Show version
```

### Function Keys

- **F1** - Help System
- **F2** - Knowledge Base
- **F3** - List Directory
- **F4** - Edit File
- **F5** - Run Script
- **F6** - System Status
- **F7** - Clear Screen
- **F8** - Character Reference

### Keyboard Shortcuts

- **↑/↓** - Navigate command history
- **ESC** - Clear current input
- **Ctrl+L** - Clear screen
- **Tab** - Auto-complete (future)

## Character Reference

### Block Graphics

Access via **F8** or `CHARS` command.

```
█ ▀ ▄ ▌ ▐ ░ ▒ ▓
┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬
```

### Box Drawing Examples

```
┌─────────────┐
│  Single Box │
└─────────────┘

╔═════════════╗
║ Double Box  ║
╚═════════════╝
```

### Emoji Support

Use emoji codes in commands:

```
> echo :rocket: Launch complete!
🚀 Launch complete!
```

Available categories:
- SYSTEM: 🚀 ⚙ 🔧 🔨 🔑 🔒 💡
- STATUS: ✅ ❌ ⚠ ℹ ⭐ ⚡ 🔥
- FILES: 📄 📁 📚 📋 📊 🗄
- TECH: 💻 📱 ⌨ 🔋 🤖

## Technical Specifications

### Display Grid
- **Columns**: 80 characters
- **Rows**: 30 lines
- **Character Size**: 12×20 pixels
- **Total Dimensions**: 960×600 pixels

### Color Palette (Synthwave DOS)

```css
--color-blue-dark:      #0a1628  /* Background */
--color-cyan-bright:    #00E5FF  /* Primary text */
--color-magenta-bright: #E91E63  /* Headers */
--color-orange-bright:  #FFEB3B  /* Prompts */
--color-green-bright:   #00E676  /* Success */
--color-red-bright:     #FF1744  /* Errors */
```

### Fonts Required

1. **PetMe64/128** - Main terminal font (included)
2. **Monosort/Noto Color Emoji** - Emoji support
3. **C64 User Mono** - Fallback font

## API Integration

### Command Execution

```javascript
// Execute command via core API
POST http://localhost:8890/api/command
{
  "session_id": "web-term-xxx",
  "command": "LIST",
  "cwd": "/knowledge"
}
```

### Response Format

```javascript
{
  "output": ["Line 1", "Line 2", ...],
  "success": true,
  "cwd": "/current/directory",
  "error": null
}
```

### Session Management

```javascript
// Check core status
GET http://localhost:8890/api/status

// Stream output (for long commands)
POST http://localhost:8890/api/command/stream
```

## File Structure

```
extensions/core/terminal/
├── index.html              # Main HTML file
├── terminal.css            # Synthwave DOS styling
├── static/
│   ├── splash.js          # Boot sequence & color cycle
│   ├── terminal.js        # Main terminal logic
│   ├── commands.js        # Command API integration
│   ├── block-graphics.js  # PETSCII & block characters
│   └── emoji-support.js   # Monosort emoji system
├── fonts/                 # Font files (if local)
└── README.md             # This file
```

## Configuration

### Terminal Settings

Edit `terminal.js` to configure:

```javascript
const state = {
  udosApiUrl: 'http://localhost:8890/api',  // Core API endpoint
  // ... other settings
};
```

### Display Settings

Edit CSS variables in `terminal.css`:

```css
:root {
  --char-width: 12px;      /* Character width */
  --char-height: 20px;     /* Character height */
  --term-cols: 80;         /* Terminal columns */
  --term-rows: 30;         /* Terminal rows */
}
```

## Browser Support

- **Chrome/Edge** 90+
- **Firefox** 88+
- **Safari** 14+

Requires:
- CSS Grid
- Fetch API
- Custom Properties
- ES6 JavaScript

## Performance

- **Lightweight**: ~50KB total (uncompressed)
- **Fast Rendering**: CSS Grid + GPU acceleration
- **Smooth Animations**: CSS transitions
- **Efficient Scrolling**: Virtual viewport

## Credits

- **C64 Fonts**: PetMe font family
- **Color Palette**: Synthwave DOS theme
- **Inspiration**: Commodore 64 BASIC
- **uDOS Core**: Universal Digital Operations System

## Version History

### v1.0.24 (Current)
- Full rebuild with Synthwave DOS palette
- 80×30 centered terminal grid
- Color cycle splash sequence
- PETSCII & block graphics support
- Monosort emoji integration
- uDOS core API integration
- Function key shortcuts

### v1.0.x (Legacy)
- Original C64 terminal implementation

## License

Part of uDOS v1.0.24 - Universal Digital Operations System

---

**uDOS Terminal** - Retro aesthetics, modern power
