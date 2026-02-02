# Wizard Font Manager Quick Reference

**Version:** 1.0.0 | **Location:** `/fonts/`

---

## 🎯 Quick Commands

```bash
# (Optional) Distribute fonts to targets
cd ~/uDOS/wizard/fonts
./distribute.sh

# Check what's in the repository
ls -R

# View font manifest
cat manifest.json | jq .

# Add new font
# 1. Copy font file to appropriate directory
# 2. Update manifest.json
# 3. Run ./distribute.sh
```

---

## 📁 Repository Structure

```
/fonts/          ← Central repository (source of truth)
├── manifest.json           ← Metadata, credits, settings
├── README.md              ← Full documentation
├── QUICK-REFERENCE.md     ← This file
├── distribute.sh          ← Distribution script
├── retro/                 ← Retro computing fonts
│   ├── c64/
│   ├── teletext/
│   ├── apple/
│   └── gaming/
├── emoji/                 ← Emoji fonts
└── custom/                ← User fonts
```

---

## 📊 Available Fonts

| Font                 | Type  | Grid  | Path                                    |
| -------------------- | ----- | ----- | --------------------------------------- |
| **PetMe64**          | Mono  | 24x24 | `retro/c64/PetMe64.ttf`                 |
| **Teletext50**       | Mono  | 24x24 | `retro/teletext/Teletext50.otf`         |
| **Chicago**          | Mono  | 24x24 | `retro/apple/Chicago.ttf`               |
| **ChicagoFLF**       | Mono  | 24x24 | `retro/apple/ChicagoFLF.ttf`            |
| **Monaco**           | Mono  | 24x24 | `retro/apple/monaco.ttf`                |
| **Los Altos**        | Sans  | 24x24 | `retro/apple/Los Altos.ttf`             |
| **Sanfrisco**        | Sans  | 24x24 | `retro/apple/Sanfrisco.ttf`             |
| **Press Start 2P**   | Mono  | 24x24 | `retro/gaming/PressStart2P-Regular.ttf` |
| **Noto Color Emoji** | Color | 24x24 | `emoji/NotoColorEmoji.ttf`              |
| **Noto Emoji**       | Mono  | 24x24 | `emoji/NotoEmoji-Regular.ttf`           |

---

## 🎨 Monosorts Settings

Each font in `manifest.json` has `monosorts` settings for 24x24 grid rendering:

```json
"monosorts": {
  "centering": "baseline" | "ink-center",
  "verticalOffset": 0,      // pixels
  "horizontalOffset": 0     // pixels
}
```

**Centering modes:**

- `baseline` - Align to font baseline
- `ink-center` - Center actual ink area (best for block graphics)

**Offsets:**

- Positive values move character down/right
- Negative values move character up/left
- Values in target resolution pixels (24x24)

---

## 🔄 Distribution Flow

```
1. Source: /fonts/      (Central repository)
           ↓
2. Script: ./distribute.sh          (Optional distribution)
           ↓
3. Target: (optional targets defined in manifest.json)
```

---

## 📝 Manifest Schema

```json
{
  "collections": {
    "category": {
      "subcategory": {
        "FontName": {
          "file": "path/to/font.ttf",
          "name": "Display Name",
          "type": "mono" | "color",
          "gridSize": 24,
          "author": "Author Name",
          "license": "License Type",
          "url": "https://source.url",
          "description": "Description",
          "monosorts": {
            "centering": "baseline" | "ink-center",
            "verticalOffset": 0,
            "horizontalOffset": 0
          }
        }
      }
    }
  }
}
```

---

## 🚀 Adding New Fonts

### Step 1: Copy Font File

```bash
cp /path/to/newfont.ttf /fonts/bundled/category/
```

### Step 2: Update Manifest

Add entry to `manifest.json`:

```json
"NewFont": {
  "file": "category/newfont.ttf",
  "name": "New Font",
  "type": "mono",
  "gridSize": 24,
  "author": "Author",
  "license": "License",
  "description": "Description",
  "monosorts": {
    "centering": "baseline",
    "verticalOffset": 0,
    "horizontalOffset": 0
  }
}
```

### Step 3: Distribute

```bash
cd ~/uDOS/fonts && ./distribute.sh
```

### Step 4: Test

Use the Wizard dashboard font manager at `/#/font-manager`.

---

## 📜 License Summary

| License             | Commercial | Modified | Redistributed | Attribution |
| ------------------- | ---------- | -------- | ------------- | ----------- |
| **OFL**             | ✅         | ✅       | ✅            | ✅ Required |
| **Apache 2.0**      | ✅         | ✅       | ✅            | ✅ Required |
| **Free (Personal)** | ❌         | ❌       | ❌            | ✅ Required |

All fonts retain original credits and attribution.

---

## 🔗 Integration

### Wizard Dashboard

- Reads fonts from `/api/fonts/manifest`
- Loads font files via `/api/fonts/file?path=...`
- Uses manifest metadata for rendering

### Future Mac App

- Will read from manifest.json
- Google Fonts API integration
- System-wide font installation

---

**Part of uDOS Alpha v1.0.2.0**
**uFont Manager Beta**
