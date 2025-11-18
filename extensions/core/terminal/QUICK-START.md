# uDOS Terminal - Quick Start Guide

## Installation

The terminal is ready to use! No build process required.

### Option 1: Direct File Access

```bash
# Navigate to terminal directory
cd /Users/fredbook/Code/uDOS/extensions/core/terminal

# Open in browser
open index.html
```

### Option 2: HTTP Server (Recommended)

```bash
# Use the included launcher script
./start.sh

# Or specify custom port
./start.sh 3000

# Or manually start server
python3 -m http.server 8000
```

Then navigate to: `http://localhost:8000`

## First Launch

1. **Splash Screen** - Color-cycling boot sequence (5 seconds)
   - Click or press any key to skip

2. **Terminal Ready** - Main 80×30 terminal appears
   - Centered on screen
   - C64-style fonts and colors
   - Function keys at bottom

3. **Try Commands**:
   ```
   > HELP      (Show all commands)
   > STATUS    (System info)
   > GUIDE     (Terminal guide)
   > CHARS     (Character reference)
   ```

## Function Keys

Press or click function keys for quick actions:

- **F1** - Help
- **F2** - Knowledge
- **F3** - List
- **F7** - Clear
- **F8** - Characters

## Character Reference

Press **F8** to open the character panel:
- **Block Graphics** - Box drawing and fills
- **PETSCII** - C64 character set
- **Emoji** - Monosort monochrome icons

Click any character to copy to clipboard.

## uDOS Core Integration

### Check Connection Status

```
> STATUS
```

Look for:
- `✓ CONNECTED TO uDOS CORE` - Full mode
- `⚠ RUNNING IN STANDALONE MODE` - Limited mode

### Start uDOS Core

If you see standalone mode:

```bash
# In another terminal
cd /Users/fredbook/Code/uDOS
./start_udos.sh
```

Then refresh the web terminal.

## Basic Commands

### System
```
HELP      - Command list
STATUS    - System status
VERSION   - Show version
CLEAR     - Clear screen
GUIDE     - Full guide
```

### Files (requires core)
```
LIST      - List directory
TREE      - Directory tree
EDIT      - Edit file
RUN       - Run script
```

### Knowledge (requires core)
```
KNOWLEDGE - Knowledge commands
K-LIST    - List articles
K-SEARCH  - Search
```

## Keyboard Shortcuts

- **↑/↓** - Command history
- **ESC** - Clear input
- **Ctrl+L** - Clear screen
- **Enter** - Execute command
- **F1-F8** - Function keys

## Visual Features

### Color Scheme (Synthwave DOS)
- **Background**: Deep space blue (#0a1628)
- **Text**: Neon cyan (#00E5FF)
- **Headers**: Hot magenta (#E91E63)
- **Prompts**: Bright yellow (#FFEB3B)
- **Success**: Neon green (#00E676)
- **Errors**: Bright red (#FF1744)

### Display Specs
- **Grid**: 80 columns × 30 rows
- **Font**: PetMe64 (authentic C64)
- **Size**: 960×600 pixels (12×20 per char)
- **Scrolling**: Vertical with custom scrollbar

## Tips & Tricks

### 1. Emoji in Commands

Use emoji codes:
```
> echo :rocket: Launch!
🚀 Launch!
```

### 2. Box Drawing

```
> echo ┌─────────┐
> echo │ Hello!  │
> echo └─────────┘
```

### 3. Command History

Press **↑** to recall previous commands.

### 4. Quick Clear

Press **F7** or type `CLEAR`.

### 5. Character Lookup

Press **F8**, find character, click to copy.

## Troubleshooting

### Terminal Not Displaying

1. Check browser console (F12)
2. Ensure JavaScript is enabled
3. Try different browser

### Commands Not Working

1. Check if uDOS core is running
2. Terminal shows connection status on startup
3. Some commands require core connection

### Fonts Not Loading

1. Check font files in `/fonts` directory
2. Browser should download PetMe fonts
3. Fallback to system monospace if needed

### Scrollbar Not Showing

1. Add more output to terminal
2. Scrollbar appears when content exceeds 30 lines
3. Check CSS is loading correctly

## Advanced Usage

### Custom API Endpoint

Edit `static/terminal.js`:
```javascript
const state = {
  udosApiUrl: 'http://your-server:port/api'
};
```

### Customize Display

Edit `terminal.css`:
```css
:root {
  --char-width: 12px;
  --char-height: 20px;
  --term-cols: 80;
  --term-rows: 30;
}
```

### Add Custom Commands

Edit `static/commands.js` and add to `LocalCommands`:
```javascript
async MYCMD(args) {
  return {
    output: ['Custom output'],
    success: true
  };
}
```

## Next Steps

1. **Explore Commands** - Try `HELP` for full list
2. **Connect to Core** - Full uDOS integration
3. **Customize Appearance** - Edit CSS variables
4. **Add Commands** - Extend functionality

## Resources

- **README.md** - Full documentation
- **GRID-SYSTEM.md** - uGRID reference
- **uDOS Wiki** - Complete system docs

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║              uDOS TERMINAL QUICK REFERENCE                ║
╠═══════════════════════════════════════════════════════════╣
║ F1  Help      │ F5  Run       │ ↑/↓  History              ║
║ F2  Knowledge │ F6  Status    │ ESC  Clear Input          ║
║ F3  List      │ F7  Clear     │ ^L   Clear Screen         ║
║ F4  Edit      │ F8  Chars     │ ⏎    Execute              ║
╠═══════════════════════════════════════════════════════════╣
║ HELP - Commands │ STATUS - Info  │ CLEAR - Screen        ║
║ LIST - Files    │ GUIDE - Guide  │ CHARS - Reference     ║
╚═══════════════════════════════════════════════════════════╝
```

---

**uDOS Terminal v1.0.24** - Simple, fast, powerful

