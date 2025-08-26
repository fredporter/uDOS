
# uDOS Font Roadmap (Redistributable Pack)
*Version: 1.0 • Date: 26 Aug 2025*

This roadmap locks in a **16‑font, open‑licensed** set for uDOS. It prioritises mono‑sort (monospaced) faces for ASCII/Unicode box drawing, BBC/Teletext vibes, and C64/retro micro aesthetics — while staying fully redistributable (OFL/Apache/Ubuntu licences).

---

## 🎯 Goals
- Ship a **legally clean** core font pack (OFL/Apache/Ubuntu licences).
- Ensure **terminal clarity**, **ASCII block accuracy**, and **cross‑platform** behaviour.
- Provide **OS fallbacks** and a simple **alias → file** mapping for loaders.
- Document **optional retro extras** (user‑installed) without bundling them.

---

## ✅ Final Selection — 16 Fonts (All Redistributable)
| # | Font (Bundle Name) | Licence | Role / Usage in uDOS | Inspiration / Notes | Source |
|---:|---|---|---|---|---|
| 1 | IBM Plex Mono | OFL | Screen (default body mono) | Modern IBM feel; wide coverage | Google Fonts |
| 2 | Roboto Mono | Apache 2.0 | Dashboard / general UI | Neutral utility mono | Google Fonts |
| 3 | Hack | Permissive | Dashboard / developer panels | Crisp coding mono | Source repo / GF mirrors |
| 4 | DejaVu Sans Mono | Permissive | Unicode fallback / system | Huge glyph coverage | DejaVu project |
| 5 | VT323 | OFL | Terminal / CRT | Teletext / early Mac SF vibes | Google Fonts |
| 6 | Space Mono | OFL | Terminal alt / headings | Chunky, Monaco‑ish | Google Fonts |
| 7 | Share Tech Mono | OFL | Utility labels / HUD | Geneva‑ish, futuristic | Google Fonts |
| 8 | Ubuntu Mono | UFL | Friendly terminal body | Soft curves, readable | Google Fonts |
| 9 | Press Start 2P | OFL | Banner / arcade UI | Chicago‑ish pixel menu | Google Fonts |
| 10 | Silkscreen | OFL | Tiny UI captions | Bitmap‑style small sizes | Google Fonts |
| 11 | DotGothic16 | OFL | Teletext‑like display | Chunky pixel weight | Google Fonts |
| 12 | C64 Pro Mono | OFL | C64 authenticity | Commodore 64 feel | Public OFL build |
| 13 | Major Mono Display | OFL | Display headlines | Playful monoline caps | Google Fonts |
| 14 | Fira Code | OFL | Dev mode (ligatures) | Modern coding mono | Google Fonts |
| 15 | Terminus | OFL/GPL | Block/ASCII shading | Tight pixel grid | Official builds |
| 16 | DSEG7 Classic | OFL | LCD counters/timers | True 7‑segment display | GitHub / GF mirrors |

> All entries are OFL/Apache/Ubuntu or similarly permissive. Where multiple distributions exist, prefer the official/open source repos.

---

## 🖥️ System Monospace Fallbacks (Do Not Bundle Names — use if installed)
Use these fallbacks in your CSS/terminal configs after the bundled TTF name.

- **macOS**: `Menlo`, `SF Mono`
- **Windows**: `Consolas`, `Courier New`
- **Linux/Unix**: `DejaVu Sans Mono`, `Liberation Mono`

Example CSS family stack:
```css
font-family: "IBM Plex Mono", "Menlo", "SF Mono", monospace;
```

---

## 📦 Pack Structure
```
fonts/
  core/
    IBM-Plex-Mono-Regular.ttf
    IBM-Plex-Mono-Bold.ttf
    RobotoMono-Regular.ttf
    Hack-Regular.ttf
    DejaVuSansMono.ttf
    VT323-Regular.ttf
    SpaceMono-Bold.ttf
    ShareTechMono-Regular.ttf
    UbuntuMono-Regular.ttf
    PressStart2P-Regular.ttf
    Silkscreen-Regular.ttf
    DotGothic16-Regular.ttf
    C64ProMono.ttf
    MajorMonoDisplay-Regular.ttf
    FiraCode-Regular.ttf
    Terminus-Regular.ttf
    DSEG7Classic-Regular.ttf
  README.md
```

---

## 🔧 Alias Mapping (drop‑in example)
Save as `fonts/fonts.json`:

```json
{
  "screen":        "IBM-Plex-Mono-Regular.ttf",
  "terminal":      "VT323-Regular.ttf",
  "wallboard":     "SpaceMono-Bold.ttf",
  "dashboard":     "RobotoMono-Regular.ttf",
  "banner":        "PressStart2P-Regular.ttf",
  "dotmatrix":     "Silkscreen-Regular.ttf",
  "lcd":           "DSEG7Classic-Regular.ttf",
  "grayscale":     "Terminus-Regular.ttf",
  "devmode":       "FiraCode-Regular.ttf",
  "retro_c64":     "C64ProMono.ttf",
  "utility":       "ShareTechMono-Regular.ttf",
  "alt_screen":    "Hack-Regular.ttf",
  "fallback":      "DejaVuSansMono.ttf",
  "display":       "MajorMonoDisplay-Regular.ttf",
  "ubuntu":        "UbuntuMono-Regular.ttf",
  "ibmplex_bold":  "IBM-Plex-Mono-Bold.ttf"
}
```

---

## 🔌 Loader Tips
- Always list a bundled TTF **first**, then two **OS fallbacks** (per platform).
- Keep **letter‑spacing** configurable: pixel fonts often need `letter-spacing: 0` to `0.02em`.
- For small sizes, prefer **Silkscreen** or **Press Start 2P**; avoid sub‑pixel smoothing for authenticity.

---

## 🧰 Optional Retro Extras (User‑Installed, not bundled)
To get authentic nostalgia (licensing varies; do not redistribute with uDOS), users may install these separately and enable them in settings:

- **Apple Classics**: Chicago, Geneva, Monaco, New York, etc. (e.g., TinkerDifferent packs)
- **BBC/Teletext**: MODE7 clones (various authors)
- **Amiga Scene Fonts**: e.g., MicroKnight
- **C64 Alternatives**: Non‑OFL variants

> Document clearly: “Install separately for personal use; not shipped with uDOS.”

---

## 📏 Testing Matrix
1. Verify **box‑drawing** and block characters (`█ ▒ ░ ▀ ▄ ▌ ▐`) across all 16 fonts.
2. Test core **grid sizes** (80×30, 64×24, 40×16) for legibility.
3. Confirm **fallback stacks** on macOS, Windows, Linux.
4. Validate **font‑license files** are present in the `fonts/core/` folder.
5. Render **sample dashboards** for each role (Wallboard/Screen/Dashboard/Terminal).

---

## 📝 Changelog
- **1.0 (26‑Aug‑2025)**: Initial 16‑font curated pack finalised and documented.
