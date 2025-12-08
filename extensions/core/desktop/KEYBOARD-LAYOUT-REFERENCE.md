# Character Editor Keyboard Layout Reference

## Physical Keyboard Mapping

```
┌─────────────────────────────────────────────────────────┐
│  LEFT HAND KEYS              RIGHT HAND KEYS             │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1  2  3  4  5               6  7  8  9  0  -            │
│  Q  W  E  R  T  Y            U  I  O  P  [  ]            │
│  A  S  D  F  G               H  J  K  L  ;  '            │
│  Z  X  C  V  B               N  M  ,  .  /  \            │
│                                                           │
│  [21 keys]                   [24 keys]                   │
└─────────────────────────────────────────────────────────┘
```

## Character Set Layouts

### 1. ASCII (Standard)
```
LH: 1  2  3  4  5               RH: 6  7  8  9  0  -
    Q  W  E  R  T  Y                U  I  O  P  [  ]
    A  S  D  F  G                   H  J  K  L  ;  '
    Z  X  C  V  B                   N  M  ,  .  /  \
```

### 2. Block Graphics
```
LH: ▀  ▄  █  ▌  ▐               RH: ▫  ▬  ▭  ▮  ▯  ▰
    ░  ▒  ▓  ▖  ▗  ▘                ▱  ◆  ◇  ◈  ◉  ◊
    ▙  ▚  ▛  ▜  ▝                   ○  ◌  ◍  ◎  ●  ◐
    ▞  ▟  ■  □  ▪                   ◑  ◒  ◓  ◔  ◕  ◖
```

**Use Cases:**
- Terminal UI graphics
- ASCII art
- Progress bars: [████░░░░░░] 40%
- Retro game graphics

### 3. C64 PETSCII
```
LH: ♠  ♥  ♦  ♣  ●               RH: ╲  ╳  ▒  ░  ▓  ■
    ○  ▌  ▐  ▀  ▄  █                □  ◆  ◇  ▪  ▫  ★
    ├  ┤  ┬  ┴  ┼                   ☆  ◗  ◖  ◄  ►  ▲
    ╭  ╮  ╰  ╯  ╱                   ▼  ←  →  ↑  ↓  ↔
```

**Use Cases:**
- C64-style games
- Retro bulletin boards
- Text adventures
- ASCII art with flair

### 4. Teletext Blocks
```
LH: █  ▌  ▐  ▀  ▄               RH: ▮  ▯  ▰  ▱  ░  ▒
    ▖  ▗  ▘  ▙  ▚  ▛                ▓  ◣  ◤  ◥  ◢  ◆
    ▜  ▝  ▞  ▟  ■                   ◇  ◈  ○  ●  ◉  ◎
    □  ▪  ▫  ▬  ▭                   ◐  ◑  ◒  ◓  ◔  ◕
```

**Use Cases:**
- Teletext displays
- Mosaic graphics
- Broadcasting UIs
- Retro information screens

### 5. Markdown Drawing
```
LH: ─  │  ┌  ┐  └               RH: ╬  ╭  ╮  ╯  ╰  ╱
    ┘  ├  ┤  ┬  ┴  ┼                ╲  ╳  ▁  ▂  ▃  ▄
    ═  ║  ╔  ╗  ╚                   ▅  ▆  ▇  █  ▏  ▎
    ╝  ╠  ╣  ╦  ╩                   ▍  ▌  ▋  ▊  ▉  ▉
```

**Example Table:**
```
╔═══════╦═══════╗
║ Name  ║ Value ║
╠═══════╬═══════╣
║ Data  ║  123  ║
╚═══════╩═══════╝
```

**Example Diagram:**
```
┌─────────┐
│ Process │
└────┬────┘
     │
     ▼
┌─────────┐
│ Output  │
└─────────┘
```

### 6. GitHub Emoji
```
LH: 😀  😃  😄  😁  😅              RH: 😝  😜  🤪  🤨  🧐  🤓
    😂  🤣  😊  😇  🙂  🙃              😎  🤩  🥳  😏  😒  😞
    😉  😌  😍  🥰  😘                  😔  😟  😕  🙁  ☹️  😣
    😗  😙  😚  😋  😛                  😖  😫  😩  🥺  😢  😭
```

**Shortcodes:**
```
:smile:       → 😄     :heart:      → ❤️
:laughing:    → 😆     :fire:       → 🔥
:heart_eyes:  → 😍     :star:       → ⭐
:grin:        → 😁     :sparkles:   → ✨
:wink:        → 😉     :tada:       → 🎉
:blush:       → 😊     :rocket:     → 🚀
:rage:        → 😡     :zap:        → ⚡
:+1:          → 👍     :bulb:       → 💡
```

**Reference:** https://gist.github.com/rxaviers/7360908

### 7. CoreUI Icons
```
LH: 📁  📄  💾  🖼️  📊              RH: 🖥️  💻  ⌨️  🖱️  🖨️  📱
    ⚙️  🔧  🔨  ✏️  📝  📋              📲  🔋  🔌  💡  🔦  📡
    📌  🔍  🔎  🏠  🌐                  🛰️  🎮  🎯  🎲  🎭  🎪
    📧  📞  ⏰  📅  🎨                  🎬  🎤  🎧  📻  📺  📷
```

**Common Uses:**
```
📁 Folder      🏠 Home       ⚙️ Settings    💾 Save
📄 File        🔍 Search     ✏️ Edit        🗑️ Delete
📊 Chart       ⬆️ Upload     ⬇️ Download    📋 Copy
```

## Quick Reference

### Character Categories

| Set       | Type          | Count | Examples                  |
|-----------|---------------|-------|---------------------------|
| ASCII     | Standard      | 21+24 | 1-5 Q-Y A-G Z-B + others |
| Blocks    | Graphics      | 45    | ▀▄█▌▐░▒▓■□▪▫             |
| C64       | PETSCII       | 45    | ♠♥♦♣●○★☆←→↑↓             |
| Teletext  | Mosaic        | 45    | █▌▐▀▄◆◇○●                |
| Markdown  | Box Drawing   | 45    | ─│┌┐└┘├┤┬┴┼═║            |
| Emoji     | Unicode       | 45    | 😀😃😄😁❤️🔥⭐            |
| Icons     | CoreUI        | 24    | 📁📄💾⚙️🔍                |

### Keyboard Shortcuts

| Key       | Action          | Description                    |
|-----------|-----------------|--------------------------------|
| Space     | Clear Grid      | Erase all pixels              |
| F         | Fill Grid       | Fill all pixels               |
| H         | Flip Horizontal | Mirror left-right             |
| V         | Flip Vertical   | Mirror top-bottom             |
| R         | Rotate 90°      | Rotate clockwise              |
| I         | Invert          | Flip all pixels               |
| C         | Copy            | Copy current glyph            |
| P         | Paste           | Paste copied glyph            |
| ←         | Previous Char   | Move to previous character    |
| →         | Next Char       | Move to next character        |

### Character Set Selection

Click the character set button at the top:
```
[ASCII] [Blocks] [C64] [Teletext] [Markdown] [Emoji] [Icons]
```

Active character set highlighted in black.

## Usage Patterns

### Terminal Graphics
```markdown
Use: Block Graphics, Markdown
Example:
┌─────────────────────────────┐
│ ▓▓▓▓▓▓░░░░░░░░░░ 40% Loading│
└─────────────────────────────┘
```

### Retro Game UI
```markdown
Use: C64 PETSCII
Example:
╭─────────────╮
│ ♥♥♥ LIVES   │
│ ★★★★★ SCORE │
│ → START     │
╰─────────────╯
```

### Documentation Tables
```markdown
Use: Markdown Drawing
Example:
║ Feature ║ Status ║
╠═════════╬════════╣
║ Editor  ║   ✓    ║
║ Fonts   ║   ✓    ║
```

### Status Indicators
```markdown
Use: Emoji
Example:
✅ Complete
❌ Failed
⚠️ Warning
🔄 Processing
```

## Tips & Tricks

1. **Mix Character Sets**: Switch between sets to combine styles
2. **Use Copy/Paste**: Duplicate complex patterns quickly
3. **Start with Templates**: Begin with existing characters, modify
4. **Preview Often**: Check rendering in preview pane
5. **Save Frequently**: Export JSON backups regularly

## Unicode Reference

### Block Elements (U+2580–U+259F)
- Upper half: ▀ (U+2580)
- Lower half: ▄ (U+2584)
- Full block: █ (U+2588)
- Left half: ▌ (U+258C)
- Right half: ▐ (U+2590)

### Box Drawing (U+2500–U+257F)
- Horizontal: ─ (U+2500)
- Vertical: │ (U+2502)
- Corners: ┌ ┐ └ ┘
- Intersections: ├ ┤ ┬ ┴ ┼

### Geometric Shapes (U+25A0–U+25FF)
- Black square: ■ (U+25A0)
- White square: □ (U+25A1)
- Black diamond: ◆ (U+25C6)
- White diamond: ◇ (U+25C7)
- Black circle: ● (U+25CF)
- White circle: ○ (U+25CB)

## Resources

- **Character Editor**: `http://localhost:8888/core/desktop/character-editor.html`
- **Documentation**: `/extensions/core/desktop/CHARACTER-EDITOR-KEYBOARDS.md`
- **Font Licenses**: `/extensions/core/fonts/README.md`
- **Icon Licenses**: `/extensions/icons/coreui/README.md`
- **GitHub Emoji**: https://gist.github.com/rxaviers/7360908
- **Unicode Reference**: https://unicode-table.com/

---

**Version**: 1.1.0
**Date**: 2025-11-18
**uDOS**: v1.0.24-extensions
