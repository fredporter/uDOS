# uDOS Teletext - Polaroid Edition

Enhanced teletext interface with Polaroid C64 color palette and Mallard fonts.

## Features

### Visual Design
- **Polaroid Color Palette**: Full C64 color set (16 colors) with transparency variants
- **Mallard Blocky Font**: Authentic blocky teletext rendering
- **C64 Block Graphics**: PETSCII-style box drawing and mosaic characters
- **Scanline Effect**: CRT-style scanlines for retro authenticity
- **Responsive Design**: Adaptive scaling for all screen sizes

### Color Palette

#### Standard Teletext Colors
- Black, Red, Green, Yellow, Blue, Magenta, Cyan, White

#### Extended C64 Colors
- Orange, Brown, Light Red, Dark Gray, Gray, Light Green, Light Blue, Light Gray

#### Transparency Variants
Each color available with: `-10`, `-25`, `-50`, `-75` suffixes

### Commands

#### Navigation
- `PAGE nnn` or `P nnn` - Go to page number (100-899)
- `NEXT` or `N` - Next page
- `PREV` or `B` - Previous page (Back)
- `INDEX` or `I` - Return to page 100
- `nnn` - Type page number directly

#### Display
- `HELP` or `H` or `?` - Show command help
- `CLEAR` or `CLS` - Clear content area
- `COLOR name` - Set text color (RED, GREEN, YELLOW, BLUE, CYAN, MAGENTA, WHITE)
- `DEMO` - Show C64 block graphics demonstration
- `REVEAL` - Reveal concealed text

### Teletext Effects

- **Double Height**: `.double-height` class for 2x vertical text
- **Flash**: `.flash` class for blinking text
- **Conceal**: `.conceal` class for hidden text (reveal on hover or with REVEAL command)
- **Mosaic**: `.mosaic` class for block graphics rendering

### Block Graphics Characters

```
Box Drawing (Single):  ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ─ │
Box Drawing (Double):  ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬ ═ ║
Shading:               █ ▓ ▒ ░ (100%, 75%, 50%, 25%)
Half Blocks:           ▀ ▄ ▌ ▐
```

### Keyboard Shortcuts

- **Enter** - Execute command
- **Arrow Up** - Previous command in history
- **Arrow Down** - Next command in history

### Page Structure

Standard teletext page format:
- **40 characters wide** × **25 rows high**
- Header row (page title, number, clock)
- Status bar
- 20+ rows of content
- Command input bar

### JavaScript API

```javascript
// Execute a command
window.uDOS.teletext.processCommand('PAGE 200');

// Load a page
window.uDOS.teletext.loadPage(150);

// Update page number
window.uDOS.teletext.updatePage(300);

// Show status message
window.uDOS.teletext.showStatus('LOADING...');

// Show help
window.uDOS.teletext.showHelp();

// Show graphics demo
window.uDOS.teletext.showDemo();

// Clear content
window.uDOS.teletext.clearContent();

// Set color
window.uDOS.teletext.setColor('CYAN');

// Reveal concealed text
window.uDOS.teletext.revealConcealed();
```

### CSS Classes

#### Foreground Colors
```css
.fg-black, .fg-red, .fg-green, .fg-yellow
.fg-blue, .fg-magenta, .fg-cyan, .fg-white
.fg-orange, .fg-brown, .fg-light-red
.fg-dark-gray, .fg-gray, .fg-light-green
.fg-light-blue, .fg-light-gray
```

#### Background Colors
```css
.bg-black, .bg-red, .bg-green, .bg-yellow
.bg-blue, .bg-magenta, .bg-cyan, .bg-white
.bg-orange, .bg-brown, .bg-light-red
.bg-dark-gray, .bg-gray, .bg-light-green
.bg-light-blue, .bg-light-gray
```

#### Effects
```css
.double-height    /* 2x vertical scaling */
.double-height.lower  /* Bottom half of double-height */
.flash            /* Blinking text */
.conceal          /* Hidden until hover/reveal */
.mosaic           /* Block graphics font */
.mosaic-demo      /* Rainbow color cycle */
```

### Files

- **index-polaroid.html** - Main teletext interface
- **teletext-polaroid.css** - Polaroid palette styling
- **teletext-shell.js** - Command processor and logic
- **teletext-enhanced.css** - Original enhanced styles
- **teletext-enhanced.js** - Original teletext logic
- **index.html** - Original teletext interface

### Font Integration

The Polaroid edition uses **Mallard Blocky** font for authentic teletext rendering:

```css
@font-face {
  font-family: 'Mallard';
  src: url('../fonts/mallard-blocky/mallard-blocky.otf') format('opentype');
}
```

Font fallback chain: `Mallard → MODE7GX3 → Courier New → monospace`

### Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile: Responsive support with touch optimization

### Usage

1. Open `index-polaroid.html` in a modern browser
2. The page loads with the index page (100)
3. Type commands in the bottom command bar
4. Press Enter to execute

### Example Commands

```
HELP          Show command reference
DEMO          Display graphics showcase
PAGE 200      Go to page 200
NEXT          Next page
COLOR CYAN    Set cyan text color
CLEAR         Clear the display
REVEAL        Show hidden text
```

### Credits

**Original Teletext Concept**: BBC Ceefax (1974-2012)

**Fonts**:
- Mallard Blocky by "gid" via FontStruct
- MODE7GX3 teletext font

**uDOS Polaroid Enhancement** (v1.0.24):
- Polaroid C64 color palette integration
- Mallard font integration
- C64 block graphics support
- Command shell interface
- Enhanced responsive design

### License

MIT License - See `LICENSE.txt` for details

### Version

**1.0.24** - Teletext Polaroid Edition (Phase 3)

---

**READY.**
