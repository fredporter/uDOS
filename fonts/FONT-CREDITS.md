# Font Credits & Licenses

**Version:** 1.0.0  
**Last Updated:** 2026-01-26

---

## 📋 Overview

This document provides proper attribution and licensing information for all fonts used in uDOS.

---

## 🖥️ Code Fonts

### Monaspace Font Family

- **Fonts:** Argon, Xenon, Krypton, Neon, Radon
- **Version:** v1.301 (Frozen)
- **Author:** GitHub Next
- **Source:** [github.com/githubnext/monaspace](https://github.com/githubnext/monaspace)
- **License:** **OFL (SIL Open Font License)**
- **Usage:** Programming, code blocks, `.ucode`, `.udos`, `.wizard`, `.mission` files
- **Files:**
  - `bundled/code/MonaspaceArgon-Regular.ttf`
  - `bundled/code/MonaspaceXenon-Regular.ttf`
  - `bundled/code/MonaspaceKrypton-Regular.ttf`
  - `bundled/code/MonaspaceNeon-Regular.ttf`
  - `bundled/code/MonaspaceRadon-Regular.ttf`

---

## 📝 Prose Fonts

### SF Pro

- **Author:** Apple Inc.
- **License:** **Apple Font License** (Bundled with macOS)
- **Usage:** System UI, default heading/body font
- **File:** `bundled/prose/SF-Pro.ttf`
- **Note:** For development/testing only. Not redistributable.

### Iowan Old Style

- **Author:** John Downer (Bitstream)
- **License:** **Commercial** (Bundled with macOS)
- **Usage:** Default serif prose font
- **File:** `bundled/prose/iowanoldstyle_bold.otf`
- **Note:** For development/testing only. Not redistributable.

### Chicago

- **Author:** Susan Kare (Apple Inc.)
- **Source:** Classic Macintosh System 7
- **License:** **Historical Apple System Font**
- **Usage:** Retro Mac UI, display
- **File:** `bundled/prose/Chicago.ttf`
- **Note:** Historical font, educational use only.

### Monaco

- **Author:** Susan Kare (Apple Inc.)
- **Source:** Classic Macintosh
- **License:** **Historical Apple System Font**
- **Usage:** Monospace terminal font
- **File:** `bundled/prose/monaco.ttf`
- **Note:** Historical font, educational use only.

### Los Altos

- **Author:** Unknown
- **License:** **Free**
- **Usage:** Mac-inspired UI sans
- **File:** `bundled/prose/Los Altos.ttf`

### Sanfrisco

- **Author:** Unknown
- **License:** **Free**
- **Usage:** Modern Mac-style UI sans
- **File:** `bundled/prose/Sanfrisco.ttf`

### Torrance

- **Author:** Unknown
- **License:** **Free**
- **Usage:** Display/decorative
- **File:** `bundled/prose/Torrance.ttf`

### Quicksand

- **Author:** Andrew Paglinawan
- **Source:** [Google Fonts](https://fonts.google.com/specimen/Quicksand)
- **License:** **OFL (SIL Open Font License)**
- **Usage:** Rounded sans serif
- **File:** `bundled/prose/Quicksand-VariableFont_wght.ttf`

### UnifrakturCook

- **Author:** j. 'mach' wust
- **Source:** [Google Fonts](https://fonts.google.com/specimen/UnifrakturCook)
- **License:** **OFL (SIL Open Font License)**
- **Usage:** Blackletter/Gothic display
- **File:** `bundled/prose/UnifrakturCook-Bold.ttf`

---

## 🕹️ Retro/Teletext Fonts

### PetMe64

- **Author:** Style64.org
- **Source:** [style64.org/petme-c64](https://style64.org/petme-c64)
- **License:** **Free for personal use**
- **Usage:** Commodore 64 PETSCII graphics
- **File:** `bundled/retro/PetMe64.ttf`

### Teletext50

- **Author:** Simon Rawles
- **Source:** [github.com/simon-rawles/teletext50](https://github.com/simon-rawles/teletext50)
- **License:** **OFL (SIL Open Font License)**
- **Usage:** BBC Micro Teletext with block graphics
- **File:** `bundled/retro/Teletext50.otf`

### Press Start 2P

- **Author:** CodeMan38
- **Source:** [Google Fonts](https://fonts.google.com/specimen/Press+Start+2P)
- **License:** **OFL (SIL Open Font License)**
- **Usage:** Arcade/gaming pixel font
- **File:** `bundled/retro/PressStart2P-Regular.ttf`

---

## 🎨 Emoji Fonts

### Noto Color Emoji

- **Author:** Google
- **Source:** [github.com/googlefonts/noto-emoji](https://github.com/googlefonts/noto-emoji)
- **License:** **OFL (SIL Open Font License)**
- **Usage:** Full-color emoji rendering
- **File:** `emoji/NotoColorEmoji.ttf`

### Noto Emoji (Monochrome)

- **Author:** Google
- **Source:** [github.com/googlefonts/noto-emoji](https://github.com/googlefonts/noto-emoji)
- **License:** **OFL (SIL Open Font License)**
- **Usage:** Monochrome emoji fallback
- **File:** `emoji/NotoEmoji-Regular.ttf`

---

## 📜 License Summary

| License                     | Fonts                                                                        | Redistribution   | Commercial Use   |
| --------------------------- | ---------------------------------------------------------------------------- | ---------------- | ---------------- |
| **OFL (Open Font License)** | Monaspace, Teletext50, Press Start 2P, Quicksand, UnifrakturCook, Noto Emoji | ✅ Yes           | ✅ Yes           |
| **Apple Font License**      | SF Pro, Iowan Old Style                                                      | ❌ No            | ❌ No (dev only) |
| **Historical/Apple System** | Chicago, Monaco                                                              | ⚠️ Educational   | ⚠️ Educational   |
| **Free (unspecified)**      | Los Altos, Sanfrisco, Torrance                                               | ⚠️ Check usage   | ⚠️ Check usage   |
| **Personal Use Only**       | PetMe64                                                                      | ❌ No commercial | ❌ Personal only |

---

## ⚠️ Important Notes

### Apple Fonts (SF Pro, Iowan Old Style, Chicago, Monaco)

These fonts are included for **development and testing purposes only**. They are:

- Bundled with macOS
- Subject to Apple's licensing terms
- **NOT redistributable** in production releases
- Should be replaced with system font stacks in production

### System Font Fallbacks

For production deployment, use CSS system font stacks:

```css
/* Sans Serif */
font-family:
  ui-sans-serif,
  system-ui,
  -apple-system,
  "Segoe UI",
  sans-serif;

/* Serif */
font-family: ui-serif, "Iowan Old Style", "Palatino Linotype", serif;

/* Monospace */
font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
```

### OFL Fonts (Freely Redistributable)

The following fonts can be safely redistributed:

- ✅ **Monaspace** (all 5 variants)
- ✅ **Teletext50**
- ✅ **Press Start 2P**
- ✅ **Quicksand**
- ✅ **UnifrakturCook**
- ✅ **Noto Emoji** (both color and mono)

---

## 📚 Additional Resources

- **SIL Open Font License:** [scripts.sil.org/OFL](https://scripts.sil.org/OFL)
- **Google Fonts:** [fonts.google.com](https://fonts.google.com)
- **Monaspace:** [monaspace.githubnext.com](https://monaspace.githubnext.com)
- **Apple Font License:** Included with macOS (see system documentation)

---

## 🔄 Version History

- **v1.0.0** (2026-01-26) - Initial credits documentation
  - Added Monaspace family
  - Added prose fonts
  - Added retro/teletext fonts
  - Added emoji fonts

---

**Status:** Active Reference  
**Maintained by:** uDOS Font Management  
**Next Review:** 2026-03-01
