# Character Editor with Font/Character Keyboards

## Overview

The uDOS Character Editor is a comprehensive bitmap font editor with dual on-screen keyboards for rapid character set selection and glyph creation. It supports multiple character sets including ASCII, block graphics, C64 PETSCII, Teletext, Markdown box drawing, GitHub emoji, and CoreUI icons.

## Features

### Core Editing
- **16×16 Pixel Grid** - High-resolution bitmap editing
- **95 ASCII Glyphs** - Complete printable ASCII set (32-126)
- **Drawing Tools** - Clear, Fill, Flip H/V, Rotate, Invert, Copy/Paste
- **Live Preview** - Real-time text preview with custom fonts
- **Export/Import** - JSON format for sharing and backup
- **Save to /memory** - Store custom character sets

### Dual Keyboard System

#### Left-Hand Keypad
Maps to physical keyboard keys: **1-5, Q-Y, A-G, Z-B** (21 keys)

```
1  2  3  4  5
Q  W  E  R  T  Y
A  S  D  F  G
Z  X  C  V  B
```

#### Right-Hand Keypad
Maps to physical keyboard keys: **6-0, U-P, H-L, N-M** (24 keys)

```
6  7  8  9  0  -
U  I  O  P  [  ]
H  J  K  L  ;  '
N  M  ,  .  /  \
```

### Character Sets

#### 1. ASCII (Default)
Standard printable characters mapped to keyboard keys.

**LH Keys**: 1 2 3 4 5 Q W E R T Y A S D F G Z X C V B
**RH Keys**: 6 7 8 9 0 - U I O P [ ] H J K L ; ' N M , . / \

#### 2. Block Graphics (Unicode)
Box drawing and shading characters for ASCII art and diagrams.

**Included Characters**:
- Upper/lower blocks: ▀ ▄
- Full block: █
- Half blocks: ▌ ▐
- Shading: ░ ▒ ▓
- Quarter blocks: ▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟
- Squares: ■ □ ▪ ▫
- Lines: ▬ ▭ ▮ ▯ ▰ ▱

**LH Keys**: ▀ ▄ █ ▌ ▐ ░ ▒ ▓ ▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟ ■ □ ▪
**RH Keys**: ▫ ▬ ▭ ▮ ▯ ▰ ▱ ◆ ◇ ◈ ◉ ◊ ○ ◌ ◍ ◎ ● ◐ ◑ ◒ ◓ ◔ ◕ ◖

**Use Cases**:
- Terminal UI graphics
- ASCII art
- Progress bars
- Retro game mockups
- Data visualization

#### 3. C64 PETSCII
Commodore 64 graphics characters and symbols.

**Included Characters**:
- Card suits: ♠ ♥ ♦ ♣
- Circles: ● ○
- Blocks: ▌ ▐ ▀ ▄ █
- Box drawing: ├ ┤ ┬ ┴ ┼
- Rounded corners: ╭ ╮ ╰ ╯
- Diagonals: ╱ ╲ ╳
- Shading: ▒ ░ ▓
- Shapes: ■ □ ◆ ◇ ▪ ▫
- Stars: ★ ☆
- Triangles: ◗ ◖
- Arrows: ◄ ► ▲ ▼ ← → ↑ ↓ ↔

**LH Keys**: ♠ ♥ ♦ ♣ ● ○ ▌ ▐ ▀ ▄ █ ├ ┤ ┬ ┴ ┼ ╭ ╮ ╰ ╯ ╱
**RH Keys**: ╲ ╳ ▒ ░ ▓ ■ □ ◆ ◇ ▪ ▫ ★ ☆ ◗ ◖ ◄ ► ▲ ▼ ← → ↑ ↓ ↔

**Use Cases**:
- C64-style games
- Retro bulletin boards
- Text adventure games
- ASCII art with flair

#### 4. Teletext Blocks
BBC Teletext mosaic graphics for broadcast-style layouts.

**Included Characters**:
- Primary blocks: █ ▌ ▐ ▀ ▄
- Quarter blocks: ▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟
- Squares: ■ □ ▪ ▫
- Lines: ▬ ▭ ▮ ▯ ▰ ▱
- Shading: ░ ▒ ▓
- Shapes: ◣ ◤ ◥ ◢ ◆ ◇ ◈
- Circles: ○ ● ◉ ◎ ◐ ◑ ◒ ◓ ◔ ◕

**LH Keys**: █ ▌ ▐ ▀ ▄ ▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟ ■ □ ▪ ▫ ▬ ▭
**RH Keys**: ▮ ▯ ▰ ▱ ░ ▒ ▓ ◣ ◤ ◥ ◢ ◆ ◇ ◈ ○ ● ◉ ◎ ◐ ◑ ◒ ◓ ◔ ◕

**Use Cases**:
- Teletext-style displays
- Mosaic graphics
- Retro information screens
- Broadcasting UIs

#### 5. Markdown Drawing
Box drawing characters for tables, diagrams, and flowcharts.

**Included Characters**:
- Single lines: ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
- Double lines: ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬
- Rounded corners: ╭ ╮ ╯ ╰
- Diagonals: ╱ ╲ ╳
- Block heights: ▁ ▂ ▃ ▄ ▅ ▆ ▇ █
- Block widths: ▏ ▎ ▍ ▌ ▋ ▊ ▉

**LH Keys**: ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩
**RH Keys**: ╬ ╭ ╮ ╯ ╰ ╱ ╲ ╳ ▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ▏ ▎ ▍ ▌ ▋ ▊ ▉ ▉

**Use Cases**:
- Markdown tables
- ASCII diagrams
- Flowcharts
- Code documentation
- Terminal UI borders

**Example Table**:
```
╔═══════╦═══════╗
║ Name  ║ Value ║
╠═══════╬═══════╣
║ Data  ║  123  ║
╚═══════╩═══════╝
```

#### 6. GitHub Emoji
Unicode emoji with GitHub shortcodes support.

**Popular Emoji** (45 included):
- Faces: 😀 😃 😄 😁 😅 😂 🤣 😊 😇 🙂 🙃 😉 😌 😍 🥰 😘 😗 😙 😚 😋
- Expressions: 😛 😝 😜 🤪 🤨 🧐 🤓 😎 🤩 🥳 😏 😒 😞 😔 😟 😕 🙁 ☹️ 😣 😖
- Symbols: ❤️ 🔥 ⭐ ✨ 🎉 🚀 💥 ⚡ 💡 👍 👎 👏 🙏 💪 👌

**Shortcode Support**:
`:smile:` → 😄 | `:heart:` → ❤️ | `:fire:` → 🔥 | `:star:` → ⭐
`:sparkles:` → ✨ | `:tada:` → 🎉 | `:rocket:` → 🚀 | `:zap:` → ⚡
`:bulb:` → 💡 | `:+1:` → 👍 | `:clap:` → 👏 | `:muscle:` → 💪

**LH Keys**: 😀 😃 😄 😁 😅 😂 🤣 😊 😇 🙂 🙃 😉 😌 😍 🥰 😘 😗 😙 😚 😋 😛
**RH Keys**: 😝 😜 🤪 🤨 🧐 🤓 😎 🤩 🥳 😏 😒 😞 😔 😟 😕 🙁 ☹️ 😣 😖 😫 😩 🥺 😢 😭

**Use Cases**:
- Expressive documentation
- Status indicators
- User feedback
- Social media content
- README files

**Full emoji reference**: https://gist.github.com/rxaviers/7360908

#### 7. CoreUI Icons
Modern icon set for UI design and prototyping.

**Included Icons** (24 common):
- Files: 📁 📄 💾 🖼️ 📊
- Tools: ⚙️ 🔧 🔨 ✏️ 📝 📋 📌
- Search: 🔍 🔎
- UI: 🏠 🌐 📧 📞 ⏰ 📅 🎨
- Devices: 🖥️ 💻 ⌨️ 🖱️ 🖨️

**LH Keys**: 📁 📄 💾 🖼️ 📊 ⚙️ 🔧 🔨 ✏️ 📝 📋 📌 🔍 🔎 🏠 🌐 📧 📞 ⏰ 📅 🎨
**RH Keys**: 🖥️ 💻 ⌨️ 🖱️ 🖨️ 📱 📲 🔋 🔌 💡 🔦 📡 🛰️ 🎮 🎯 🎲 🎭 🎪 🎬 🎤 🎧 📻 📺 📷

**Use Cases**:
- UI mockups
- Icon font creation
- Desktop applications
- Web design
- Pixel art references

**CoreUI Source**: https://coreui.io/icons/ (CC BY 4.0)

## Usage

### Basic Workflow

1. **Open Character Editor**
   - Desktop: Double-click "Text Editor" icon
   - Direct: Open `character-editor.html` in browser

2. **Select Character Set**
   - Click character set button: ASCII, Blocks, C64, etc.
   - Keypads update to show available characters

3. **Choose Character**
   - Click character in keypad OR
   - Click character in ASCII selector (32-126)

4. **Draw Glyph**
   - Click pixels to draw
   - Right-click to erase
   - Use tools: Clear, Fill, Flip, Rotate, Invert

5. **Use Tools**
   - **Clear** (Space): Erase all pixels
   - **Fill** (F): Fill all pixels
   - **Flip H** (H): Mirror horizontally
   - **Flip V** (V): Mirror vertically
   - **Rotate** (R): Rotate 90° clockwise
   - **Invert** (I): Flip all pixels
   - **Copy** (C): Copy current glyph
   - **Paste** (P): Paste copied glyph

6. **Preview**
   - See live preview of font in use
   - Edit preview text to test specific words

7. **Save**
   - **Export JSON**: Download font file
   - **Save to /memory**: Store in uDOS (requires file picker)
   - **Auto-save**: LocalStorage backup

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Space** | Clear grid |
| **F** | Fill grid |
| **H** | Flip horizontal |
| **V** | Flip vertical |
| **R** | Rotate 90° |
| **I** | Invert pixels |
| **C** | Copy glyph |
| **P** | Paste glyph |
| **←** | Previous character |
| **→** | Next character |

### Saving Custom Fonts

#### Method 1: Export JSON
```
1. Click "Export JSON"
2. File downloads: custom-font-TIMESTAMP.json
3. Store anywhere on your system
```

#### Method 2: Save to /memory
```
1. Click "Save to /memory"
2. Follow instructions to place in:
   /memory/fonts/
   /memory/themes/
   /memory/shared/
3. Load later via file picker
```

#### JSON Format
```json
{
  "name": "My Custom Font",
  "author": "Your Name",
  "version": "1.0",
  "gridSize": 16,
  "charset": "blocks",
  "timestamp": "2025-11-18T...",
  "glyphs": {
    "65": ["0000000000000000", ...],
    "66": ["0000000000000000", ...],
    ...
  }
}
```

### Character Set Applications

#### Terminal Graphics
Use **Block Graphics** or **Markdown** sets to create:
- Progress bars: `[████░░░░░░] 40%`
- Boxes: `╭───────╮`
- Borders: `║ Text ║`
- Menus: `├ Option ┤`

#### Retro Games
Use **C64 PETSCII** for:
- Player: ☺
- Enemies: ♠ ♥ ♦ ♣
- Walls: █
- Items: ● ○ ◆
- UI: ╭─────╮

#### Documentation
Use **Markdown** for:
- Tables with proper borders
- Flowcharts with boxes and arrows
- Code block frames
- Diagram structures

#### Expressive Content
Use **Emoji** for:
- Status: ✅ ❌ ⚠️
- Reactions: 😍 🔥 👍
- Categories: 📁 📄 🎨
- Actions: 🚀 💡 🎯

## Integration with uDOS

### Desktop Integration
The character editor is embedded in the uDOS desktop:
```html
<iframe src="character-editor.html"
        style="width: 100%; height: 100%; border: none;">
</iframe>
```

### Theme System
Custom fonts can be used in themes:
```json
{
  "name": "My Theme",
  "fonts": {
    "primary": "/memory/fonts/my-custom-font.json"
  }
}
```

### File Picker Integration
Load/save fonts via file picker:
- Browse `/memory/fonts/`
- Open in character editor
- Save back to `/memory/`

## Font Library Organization

### Recommended Structure
```
/memory/fonts/
  ├── ascii/
  │   └── standard-ascii.json
  ├── blocks/
  │   ├── box-drawing.json
  │   └── shading-blocks.json
  ├── c64/
  │   ├── petscii-full.json
  │   └── c64-symbols.json
  ├── teletext/
  │   └── mosaic-graphics.json
  ├── markdown/
  │   ├── table-borders.json
  │   └── diagrams.json
  └── custom/
      └── my-creations/
```

### Sharing Fonts
Share custom fonts via:
1. `/memory/shared/` folder
2. Export JSON and commit to repo
3. Community wiki
4. GitHub Gists

## Advanced Features

### Batch Operations
1. Create multiple glyphs quickly by:
   - Using Copy/Paste between characters
   - Switching characters with arrow keys
   - Using consistent tools (Flip, Rotate)

### Font Metadata
Track your font details:
- **Name**: Descriptive font name
- **Author**: Your name/handle
- **Version**: Increment for updates
- **Charset**: Document primary character set
- **Notes**: Usage instructions

### Template Fonts
Start from existing fonts:
1. Import base font
2. Modify specific glyphs
3. Export as new variant
4. Document changes

## Character Set Reference

### Unicode Blocks Used
- **Box Drawing** (U+2500–U+257F)
- **Block Elements** (U+2580–U+259F)
- **Geometric Shapes** (U+25A0–U+25FF)
- **Miscellaneous Symbols** (U+2600–U+26FF)
- **Emoticons** (U+1F600–U+1F64F)

### Font Coverage
- **ASCII**: 95 glyphs (32-126)
- **Extended**: 200+ block/box characters
- **Emoji**: 100+ common emoji
- **Icons**: 500+ CoreUI icons

## Performance Tips

1. **Save Frequently**: Auto-save enabled via localStorage
2. **Export Backups**: Periodically export JSON
3. **Test in Preview**: Check font rendering before saving
4. **Use Keyboard**: Shortcuts faster than mouse
5. **Batch Similar**: Group similar glyphs together

## Troubleshooting

### Characters Not Displaying
- Check browser font support
- Verify Unicode compatibility
- Test with different fonts in preview

### Save to /memory Not Working
- Requires server-side file write support
- Use Export JSON as backup method
- Check file picker integration

### Keypad Not Updating
- Refresh page
- Check JavaScript console for errors
- Verify character set data loaded

## Resources

### Documentation
- **Character Editor**: `/extensions/core/desktop/CHARACTER-EDITOR-INTEGRATION.md`
- **Font License**: `/extensions/core/fonts/README.md`
- **Icon License**: `/extensions/icons/coreui/README.md`

### External References
- **Unicode Box Drawing**: https://en.wikipedia.org/wiki/Box-drawing_character
- **GitHub Emoji**: https://gist.github.com/rxaviers/7360908
- **CoreUI Icons**: https://coreui.io/icons/
- **PETSCII**: https://en.wikipedia.org/wiki/PETSCII

### Community
- **uDOS Wiki**: https://github.com/fredporter/uDOS/wiki
- **Font Gallery**: `/memory/shared/fonts/`
- **Issues**: https://github.com/fredporter/uDOS/issues

---

**Version**: 1.1.0 (Enhanced with Keypads)
**Last Updated**: 2025-11-18
**uDOS**: v1.0.24-extensions
