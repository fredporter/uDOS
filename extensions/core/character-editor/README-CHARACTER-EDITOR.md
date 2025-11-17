# uDOS Font Manager v1.0.24

Comprehensive font creation and management suite with Synthwave DOS C64 styling.

## Features

### Bitmap Editor
- **16×16 Grid Editor**: Pixel-perfect bitmap font creation
- **Drawing Tools**: Draw, erase, fill, line
- **Transform Tools**: Flip H/V, rotate, invert
- **Edit Tools**: Copy, paste, undo, clear
- **Character Navigation**: Arrow keys, dropdown selector
- **Real-time Preview**: Instant character set visualization
- **Auto-save**: localStorage persistence
- **Export Options**: JSON, PNG, CSS

### TTF/OTF Viewer
- **Font Upload**: Load TTF, OTF, WOFF, WOFF2 files
- **Font Information**: Family, style, weight, format, size
- **Bitmap Preview**: Render text at any size
- **Glyph Catalog**: Browse all available glyphs
- **TTF to Bitmap**: Convert TTF fonts to 16×16 bitmap format
- **Character Ranges**: ASCII, Box Drawing, Block Elements

### Emoji Designer
- **32×32 Canvas**: High-resolution emoji creation
- **Color Palette**: 16 C64 Synthwave DOS colors
- **Emoji Library**: Save and manage custom emoji
- **Grid-aligned**: Perfect for terminal display

### Font Library
- **Library Management**: Save, load, organize fonts
- **Search & Filter**: Find fonts by name or category
- **Categories**: System, Custom, Imported, Emoji
- **Quick Upload**: Drag and drop TTF/OTF files

### Sandbox Integration
- **Export to /memory/sandbox**: Save fonts for uDOS scripts
- **JSON Format**: Standard uDOS bitmap font format
- **Metadata**: Name, version, author, license

## Usage

### Bitmap Editor

#### Creating a Font
1. Click **New Font** to start fresh
2. Select a character from the dropdown
3. Click or drag on the grid to draw pixels
4. Use tools to transform and edit
5. Navigate with ← → arrow keys
6. Save to library or export

#### Drawing Controls
- **Left Click + Drag**: Draw pixels
- **Right Click + Drag**: Erase pixels
- **Tool Buttons**: Switch between draw/erase/fill/line modes

#### Keyboard Shortcuts
- `D` - Draw tool
- `E` - Erase tool
- `F` - Fill (Ctrl+F to fill grid)
- `C` - Copy character (Ctrl+C)
- `V` - Paste character (Ctrl+V)
- `Z` - Undo (Ctrl+Z)
- `←` - Previous character
- `→` - Next character

### TTF Processor

#### Loading a Font
1. Click **Upload TTF/OTF** in the library sidebar
2. Select a .ttf, .otf, .woff, or .woff2 file
3. Switch to the **TTF Viewer** tab
4. View font information and glyphs

#### Converting to Bitmap
1. Load a TTF/OTF font
2. Browse the glyph catalog
3. Click **Generate 16×16 Bitmap Font**
4. Font automatically loads in Bitmap Editor
5. Refine pixels as needed
6. Export or save to sandbox

### Font Properties

#### Metadata
- **Name**: Font display name
- **Author**: Creator name
- **Version**: Semantic version (1.0.0)
- **License**: MIT, CC0, OFL, or Custom

#### Grid Settings
- **Grid Size**: 8×8, 16×16, or 32×32
- **Show Grid**: Toggle grid lines
- **Show Baseline**: Toggle baseline guide

#### Export Options
- **Export JSON**: Download as .json file
- **Export PNG**: Sprite sheet (future)
- **Export CSS**: @font-face CSS (future)
- **Save to Sandbox**: Export to /memory/sandbox

### Preview

#### Live Preview
- **Background**: Black, Blue, White, Gray
- **Color**: Cyan, Green, Yellow, White
- **Scale**: 1x, 2x, 3x, 4x
- **Sample Text**: Customize preview text

## File Format

### Bitmap Font JSON
```json
{
  "name": "My Custom Font",
  "version": "1.0.0",
  "author": "Your Name",
  "license": "MIT",
  "gridSize": 16,
  "glyphs": {
    "A": [
      [0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0],
      ...
    ],
    "B": [...],
    ...
  }
}
```

### Grid Format
- Each glyph is a 2D array of 0s and 1s
- 0 = empty pixel (background)
- 1 = filled pixel (foreground)
- Grid size: 16×16 (default), 8×8, or 32×32

## Color Palette

The Font Manager uses the **Synthwave DOS C64 color palette**:

- Black (`#000000`)
- White (`#FFFFFF`)
- Red (`#880000`)
- Cyan (`#AAFFEE`)
- Purple (`#CC44CC`)
- Green (`#00CC55`)
- Blue (`#0000AA`)
- Yellow (`#EEEE77`)
- Orange (`#DD8855`)
- Brown (`#664400`)
- Light Red (`#FF7777`)
- Dark Gray (`#333333`)
- Gray (`#777777`)
- Light Green (`#AAFF66`)
- Light Blue (`#0088FF`)
- Light Gray (`#BBBBBB`)

## Browser Compatibility

- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Full support (14+)
- **Mobile**: Partial support (touch drawing)

## Files

- **font-manager.html** - Main application interface
- **font-manager.css** - Synthwave DOS styling
- **font-manager-app.js** - Application controller
- **bitmap-editor.js** - 16×16 grid editor
- **ttf-processor.js** - TTF to bitmap converter
- **emoji-designer.js** - Emoji creation tool
- **font-manager-core.js** - Utility functions

## Integration with uDOS

### Sandbox Workflow

1. Create or import a font
2. Click **Save to Sandbox**
3. Font is exported to `/memory/sandbox/`
4. Use in uDOS scripts:

```python
# Load custom font
font = load_sandbox_font('my-custom-font.json')

# Render text with custom font
render_text("Hello World", font)
```

### Character Sets

The Font Manager supports standard uDOS character ranges:
- **ASCII**: 0x20-0x7E (printable characters)
- **Box Drawing**: 0x2500-0x257F (└─┐┌┴┬├┤┼)
- **Block Elements**: 0x2580-0x259F (█▓▒░▀▄▌▐)

## Credits

**uDOS Font Manager** v1.0.24
- Synthwave DOS C64 color palette
- Chicago and PetMe font integration
- TTF bitmap conversion
- Sandbox export workflow

**Original Font Editor** (v1.3)
- 16×16 grid bitmap editor
- System.css retro styling

## License

MIT License - See `LICENSE.txt` for details

## Version History

- **v1.0.24** - Font Manager rebuild with Synthwave DOS styling, TTF support
- **v1.3** - Original font editor with System 6 styling
- **v1.0** - Initial bitmap font editor

---

**READY.**
