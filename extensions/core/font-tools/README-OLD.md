# 🔮 uDOS Font Editor

**Retro-inspired 16×16 bitmap font creator for uDOS terminal**

Create custom monospace fonts with pixel-perfect precision. Perfect for ASCII art, box-drawing characters, UI icons, and retro aesthetics.

---

## 🎯 Features

- **16×16 Pixel Grid**: Standard uCELL format
- **Real-time Preview**: See your font in action instantly
- **Auto-Save**: All changes saved to browser localStorage
- **Export/Import**: JSON format for sharing and backup
- **120 Character Slots**: ASCII + Box Drawing + Block Elements
- **Editing Tools**: Clear, Fill, Flip H/V, Rotate, Invert
- **Copy/Paste**: Duplicate glyphs quickly
- **Keyboard Shortcuts**: Fast pixel-perfect editing
- **Retro Design**: Green-on-black terminal aesthetic

---

## 🚀 Quick Start

### Local File
1. Open `index.html` in your browser
2. Start drawing on the 16×16 grid
3. Click or drag to draw pixels
4. Right-click or drag to erase

### With HTTP Server
```bash
cd extensions/web/font-editor
python3 -m http.server 8000
# Open http://localhost:8000
```

---

## 🎨 How to Use

### Drawing
- **Left Click + Drag**: Draw pixels (green)
- **Right Click + Drag**: Erase pixels (black)
- Grid auto-saves to browser localStorage

### Glyph Selection
- Use dropdown to select character to edit
- Navigate with **←/→** arrow keys or buttons
- Currently editing character shown in sidebar

### Tools
| Tool | Button | Shortcut | Description |
|------|--------|----------|-------------|
| Clear | ⬜ Clear | `Space` | Erase entire grid |
| Fill | ⬛ Fill | `F` | Fill entire grid |
| Flip H | ↔️ Flip H | `H` | Mirror horizontally |
| Flip V | ↕️ Flip V | `V` | Mirror vertically |
| Rotate | 🔄 Rotate | `R` | Rotate 90° clockwise |
| Invert | ◐ Invert | `I` | Swap on/off pixels |
| Copy | 📋 Copy | `C` | Copy current glyph |
| Paste | 📄 Paste | `P` | Paste copied glyph |

### File Operations
- **Export JSON**: Download font as `.json` file
- **Import JSON**: Load previously saved font
- **Reset All**: Clear all glyphs (requires confirmation)

### Metadata
- **Font Name**: Set custom font name (used in export filename)
- **Author**: Add your name to the font metadata

### Preview
- **Live Preview**: See your font rendered in real-time
- **Custom Text**: Edit preview text to test specific characters
- Default: "THE QUICK BROWN FOX 0123456789"

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Clear current glyph |
| `F` | Fill current glyph |
| `H` | Flip horizontally |
| `V` | Flip vertically |
| `R` | Rotate 90° clockwise |
| `I` | Invert pixels |
| `C` | Copy current glyph |
| `←` / `→` | Navigate prev/next character |
| `↑` / `↓` | Jump 16 characters |

---

## 📁 File Format

Fonts are saved as JSON with this structure:

```json
{
  "fontName": "uDOS Custom",
  "author": "Your Name",
  "gridSize": "16x16",
  "baseline": 12,
  "created": "2025-10-31T12:00:00.000Z",
  "modified": "2025-10-31T12:30:00.000Z",
  "version": "1.0",
  "glyphs": {
    "U+0041": [
      "0000000000000000",
      "0000000110000000",
      "0000001111000000",
      "0000011001100000",
      "0000110000110000",
      "0001111111111000",
      "0001100000011000",
      "0011000000001100",
      "0011000000001100",
      "0000000000000000",
      "0000000000000000",
      "0000000000000000",
      "0000000000000000",
      "0000000000000000",
      "0000000000000000",
      "0000000000000000"
    ]
  }
}
```

Each glyph is a 16-element array of binary strings (`0` = off, `1` = on).

---

## 🎯 Character Ranges

### ASCII Printable (95 chars)
- U+0020 to U+007E
- Letters, numbers, punctuation, symbols

### Box Drawing (17 chars)
- U+2500 to U+2555
- Lines, corners, intersections
- Single and double-line variants

### Block Elements (8 chars)
- U+2580 to U+2593
- Half blocks, full blocks, shades

---

## 🔗 Integration with uDOS

### Export for Terminal Use
1. Create your font in the editor
2. Click **💾 Export JSON**
3. File saves as `uFONT-YYYYMMDD-FontName.json`
4. Convert to WOFF2 (future feature)
5. Load into `cmd.js` terminal

### Current Workflow
```bash
# 1. Create font in editor
# 2. Export JSON
# 3. (Future) Convert to WOFF2:
#    python3 core/font_converter.py font.json font.woff2
# 4. Load in terminal:
#    FONT INSTALL custom.woff2
```

---

## 💾 Storage

- **Auto-Save**: All changes saved to `localStorage`
- **Key**: `udos-font-editor`
- **Clipboard**: Glyph copy/paste uses `udos-font-clipboard`
- **Persistence**: Survives browser refresh
- **Clearing**: Use "Reset All" or clear browser storage

---

## 🎨 Example Fonts

### Template Ideas
- **Teletext**: BBC Micro style chunky text
- **C64 PETSCII**: Commodore 64 character set
- **LCD 7-Segment**: Calculator/digital clock style
- **Pixel Art**: Custom game/demo fonts
- **ASCII Art**: Box-drawing heavy designs

---

## 🛠️ Technical Details

### Architecture
- **Pure Vanilla JS**: No frameworks required
- **HTML5 Canvas**: Pixel-perfect rendering
- **localStorage API**: Persistent storage
- **CSS Grid/Flexbox**: Responsive layout

### Browser Compatibility
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile: ⚠️ Touch support limited (use desktop)

### File Size
- **Application**: ~50KB total (HTML + CSS + JS)
- **Font Data**: ~2KB per font (vs 625KB for Monaspace)
- **300× smaller** than standard web fonts

---

## 🔮 Future Features

- [ ] WOFF2 export (direct web font generation)
- [ ] Template fonts (Teletext, C64, LCD)
- [ ] Undo/Redo history
- [ ] Multi-glyph select and batch operations
- [ ] Import from existing fonts
- [ ] Variable baseline setting
- [ ] Grid size options (8×8, 32×32)
- [ ] Color/grayscale support
- [ ] Export to sprite sheet

---

## 📚 Resources

- **uDOS Font Documentation**: `../../docs/FONTS.md`
- **uCELL Standard**: 16×16 pixel grid
- **FontTools**: Python library for WOFF2 conversion
- **Monaspace Integration**: CSS unicode-range fallback

---

## 🐛 Troubleshooting

### Glyphs not saving
- Check browser localStorage is enabled
- Clear cache and reload
- Export JSON as backup before clearing storage

### Preview not updating
- Ensure glyph has at least one pixel drawn
- Check browser console for errors
- Try refresh (F5)

### Keyboard shortcuts not working
- Click outside of input fields
- Ensure focus is on the page (click canvas)
- Check browser doesn't override shortcuts

---

## 📄 License

Part of the uDOS project. See main repository for license.

---

**Made with 💚 for retro computing enthusiasts**

*uDOS Font Editor v1.0 - 16×16 Bitmap Font Creator*
