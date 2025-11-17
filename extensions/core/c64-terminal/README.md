# uDOS C64 Terminal

An authentic Commodore 64 terminal experience with modern web technologies.

## Features

### Visual Design
- **Polaroid Color Palette**: Extended C64 color set with 16 base colors and transparency variants (10%, 25%, 50%, 75%)
- **PetMe Font**: Authentic PETSCII character rendering using PetMe64 and PetMe128 fonts
- **Scanline Effect**: CRT-style scanlines for retro authenticity
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Boot Sequence
1. **Loading Screen** (2 seconds): Animated color cycle bars with "LOADING..." text
2. **Splash Screen** (3 seconds): ASCII uDOS logo with progress bar animation
3. **Terminal Ready**: Classic C64 command prompt

Press **ESC** during boot to skip directly to terminal (development mode).

### Terminal Commands

#### System Commands
- `HELP` - Display available commands and usage
- `LIST` - Show available programs
- `LOAD "program"` - Load a program into memory
- `RUN` - Execute the loaded program
- `CLEAR` - Clear terminal output

#### Output Commands
- `PRINT "text"` - Display text on screen
- `COLOR fg bg` - Change foreground/background colors (0-15)

#### Memory Commands
- `POKE address,value` - Write value to memory address
- `PEEK(address)` - Read value from memory address
- `SYS address` - Execute machine code at address

#### Graphics Commands
- `CHARS` - Toggle character reference panel
- `EMOJI` - Run emoji showcase demo

### Demo Programs

#### HELLO
ASCII art welcome message with PETSCII border graphics.

```
LOAD "HELLO"
RUN
```

#### COLORS
Interactive demonstration of all 16 Polaroid palette colors with color codes.

```
LOAD "COLORS"
RUN
```

#### GRAPHICS
PETSCII block graphics showcase featuring 128+ Unicode characters.

```
LOAD "GRAPHICS"
RUN
```

#### EMOJI
Monocolor emoji grid display with categories (faces, hands, hearts, stars, arrows, tech, gaming, numbers).

```
LOAD "EMOJI"
RUN
```

### Function Keys

- **F1** - HELP (display command reference)
- **F3** - LIST (show programs)
- **F5** - RUN (execute loaded program)
- **F7** - CLEAR (clear terminal)
- **F8** - Toggle character reference panel

### Character Reference Panel

Toggle with **F8** or the `CHARS` command.

#### Block Graphics Tab
- 128+ PETSCII Unicode characters
- Box drawing: single and double lines
- Shading: light, medium, dark
- Geometric shapes: blocks, triangles, circles
- Special symbols: hearts, diamonds, spades, clubs, notes
- Click any character to copy to clipboard

#### Emoji Tab
- 200+ monocolor emoji organized by category
- Faces & emotions
- Hands & gestures
- Hearts & symbols
- Stars & weather
- Arrows & symbols
- Tech & objects
- Gaming & fun
- Numbers & math
- Click any emoji to insert into command input

### Color Palette

#### C64 Base Colors (0-15)
0. Black (`#000000`)
1. White (`#FFFFFF`)
2. Red (`#880000`)
3. Cyan (`#AAFFEE`)
4. Purple (`#CC44CC`)
5. Green (`#00CC55`)
6. Blue (`#0000AA`)
7. Yellow (`#EEEE77`)
8. Orange (`#DD8855`)
9. Brown (`#664400`)
10. Light Red (`#FF7777`)
11. Dark Gray (`#333333`)
12. Gray (`#777777`)
13. Light Green (`#AAFF66`)
14. Light Blue (`#0088FF`)
15. Light Gray (`#BBBBBB`)

#### Transparency Variants
Each color available with: `-10`, `-25`, `-50`, `-75` suffixes for transparency levels.

Example: `bg-blue-50` (50% transparent blue background)

### Terminal Defaults
- **Background**: Blue (`#0000AA`)
- **Foreground**: Light Blue (`#0088FF`)
- **Cursor**: Cyan (`#AAFFEE`) with blink animation
- **Border**: Cyan with 8px width

### Command History
- **Arrow Up** - Previous command
- **Arrow Down** - Next command
- **Tab** - Autocomplete command

### JavaScript API

#### Terminal Control
```javascript
// Execute a command
window.uDOS.terminal.executeCommand('LIST');

// Clear screen
window.uDOS.terminal.clearScreen();

// Append output
window.uDOS.terminal.appendOutput('Hello, World!', 'light-green');

// Update status
window.uDOS.terminal.updateStatus('READY.');
```

#### Block Graphics
```javascript
// Draw a box
const box = window.uDOS.blockGraphics.drawBox(40, 10, 'TITLE');

// Draw progress bar
const bar = window.uDOS.blockGraphics.drawProgressBar(75, 20);

// Create pattern
const pattern = window.uDOS.blockGraphics.createPattern('█', 10, 5);

// Access characters
const fullBlock = window.uDOS.blockGraphics.chars.FULL_BLOCK; // █
const allChars = window.uDOS.blockGraphics.allChars; // Array of 128+ chars
```

#### Emoji Support
```javascript
// Get all emoji
const all = window.uDOS.emoji.getAll();

// Get by category
const faces = window.uDOS.emoji.getCategory('faces');

// Insert emoji
window.uDOS.emoji.insert('🎮');

// Access emoji set
const emojiSet = window.uDOS.emoji.set;
```

#### Boot Sequence
```javascript
// Skip splash (development)
window.uDOS.skipSplash();
```

## Installation

1. Copy the `c64-terminal` folder to `extensions/core/`
2. Ensure PetMe fonts are installed in `extensions/fonts/petme/`
3. Open `index.html` in a modern browser

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Responsive support

## Credits

**Original C64 CSS3** by Roel Nieskens (Pixelambacht)
- MIT License
- https://pixelambacht.nl/2013/css3-c64/

**uDOS Enhancements** (v1.0.24)
- Polaroid color palette with transparency
- PetMe font integration (PETSCII)
- uDOS splash sequence
- Terminal command processor
- Block graphics support (128+ characters)
- Monocolor emoji support (200+ emoji)
- Function keys and character reference
- Demo programs and JavaScript API

## License

MIT License - See `LICENSE.txt` for details

## Version

**1.0.24** - C64 Terminal Enhancement (Phase 2)

---

**READY.**
