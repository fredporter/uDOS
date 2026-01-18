# Pixel Editor Font Integration - Quick Reference

**Version:** v1.0.0
**Date:** 2026-01-18
**Status:** ✅ Ready

---

## Quick Start

1. **Open Pixel Editor:** http://127.0.0.1:8765/ → Click "🎨 Pixel Editor"
2. **Open Character Picker:** Click "🔤 Character Picker" button
3. **Select Collection:** Choose from dropdown (e.g., "Sextant Blocks")
4. **Pick Character:** Click any character in grid (e.g., 🬀)
5. **Draw:** Tool auto-switches to "Font Character", click/drag on canvas

---

## Navigation Updates

| Old Label | New Label       | Route           |
| --------- | --------------- | --------------- |
| 🔤 Fonts  | 🔤 Font Manager | `/font-manager` |
| 🎨 Pixels | 🎨 Pixel Editor | `/pixel-editor` |

---

## Tools

| Tool           | Icon | Shortcut            | Draws                 |
| -------------- | ---- | ------------------- | --------------------- |
| Pencil         | ✏️   | Default             | Filled block █        |
| Font Character | 🔤   | Auto on char select | Selected Unicode char |
| Eraser         | 🗑️   | Manual              | Empty space           |

---

## Font Collections (8 total, 217 characters)

| Collection         | Count | Characters                | Use Case                |
| ------------------ | ----- | ------------------------- | ----------------------- |
| **Emoji**          | 72    | 🟢🔴🟡🔵⚪⚫🟤🟠🟣🟨 etc. | Colored patterns        |
| **Symbols**        | 33    | ☰☱☲☳☴☵☶☷ etc.     | I-Ching, symbols        |
| **Box Drawing**    | 25    | ─│┌┐└┘├┤┬┴┼ etc.          | ASCII art borders       |
| **Sextant Blocks** | 63    | 🬀🬁🬂🬃🬄🬅🬆🬇 etc.             | Teletext graphics (2×3) |
| **Retro Apple**    | 10    | Classic Mac fonts         | Vintage aesthetics      |
| **Retro C64**      | 10    | Commodore 64              | 8-bit style             |
| **Retro Gaming**   | 10    | Press Start 2P            | Arcade look             |
| **Retro Teletext** | 10    | Teletext 50               | BBC Micro style         |

---

## Keyboard Shortcuts

| Action           | Shortcut                    |
| ---------------- | --------------------------- |
| Toggle Grid      | Click "📐 Grid" button      |
| Zoom In          | Click "🔍+" button          |
| Zoom Out         | Click "🔍−" button          |
| Clear All        | Click "🗑️ Clear" (confirms) |
| Save JSON        | Click "💾 Save JSON"        |
| Load JSON        | Click "📂 Load JSON"        |
| Export SVG       | Click "⬇️ Export SVG"       |
| Character Picker | Click "🔤 Character Picker" |

---

## Workflow Example: Teletext Mosaic

```
1. Open Character Picker
2. Select "Sextant Blocks" collection
3. Click 🬀 (top-left 2×3 block)
4. Set foreground: WAYPOINT (yellow)
5. Set background: FOREST (green)
6. Draw on canvas
7. Switch to different sextant blocks as needed
8. Export SVG when done
```

---

## API Endpoints

### Collections

```bash
curl http://127.0.0.1:8765/api/v1/fonts/collections
```

### Characters

```bash
curl 'http://127.0.0.1:8765/api/v1/fonts/characters/sextant?limit=200'
```

---

## File Formats

### JSON (24×24 Grid)

```json
{
  "size": 24,
  "grid": [
    [
      {"char": "🬀", "fg": "WHITE", "bg": "BLACK"},
      ...
    ]
  ]
}
```

### SVG Export

- Preserves colors and characters
- Uses monospace font
- Viewbox: 480×480 (24 cells × 20px)

---

## Tips

### Best Practices

- Use **Sextant Blocks** for fine mosaic detail (2×3 pixels per cell)
- Use **Box Drawing** for clean borders and diagrams
- Use **Emoji** for quick colorful patterns
- Combine with uDOS 32-color palette for period-accurate retro designs

### Troubleshooting

- **Characters not showing:** Check if collection loaded (dropdown should show count)
- **Wrong character drawn:** Verify tool is set to "🔤 Font Character"
- **Colors not applying:** Check foreground/background color selectors
- **Grid not updating:** Refresh browser (Cmd+Shift+R)

---

## Next Steps

1. **Try All Collections:** Explore all 8 font collections
2. **Create Patterns:** Build teletext-style screens with sextant blocks
3. **Export Assets:** Save JSON grids for use in other projects
4. **Share Designs:** Export SVG for web/print use

---

## Known Limitations

- ⚠️ Sextant blocks may render differently across browsers
- ⚠️ SVG export uses `<text>` (may need font embedding for portability)
- ⚠️ No font face preview yet (coming soon)
- ⚠️ No recent/favorites yet (coming soon)

---

## Support

- **Documentation:** `/public/wizard/PIXEL-EDITOR-FONT-INTEGRATION.md`
- **API Docs:** http://127.0.0.1:8765/docs
- **Dashboard:** http://127.0.0.1:8765/

---

_Quick Reference v1.0.0_
_uDOS Wizard v1.1.0.0_
_Last Updated: 2026-01-18_
