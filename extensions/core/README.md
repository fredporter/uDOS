# system.css Integration - README

## Overview

This directory contains authentic fonts and icons from **system.css v0.1.11** by Sakun Acharige (@sakofchit). These assets provide an authentic Apple System 6 (1984-1991) aesthetic to the uDOS Desktop environment.

## Directory Structure

```
system.css/
├── fonts/                    # Authentic Mac OS fonts (WOFF/WOFF2)
│   ├── ChicagoFLF.woff2     # Display font (11KB)
│   ├── ChicagoFLF.woff      # Display font fallback (15KB)
│   ├── ChiKareGo2.woff2     # Chicago_12 - Primary UI (4KB)
│   ├── ChiKareGo2.woff      # Chicago_12 fallback (6KB)
│   ├── FindersKeepers.woff2 # Geneva_9 - Small text (3KB)
│   ├── FindersKeepers.woff  # Geneva_9 fallback (5KB)
│   ├── monaco.woff2         # Monospace (2KB)
│   └── monaco.woff          # Monospace fallback (4KB)
│
├── icon/                     # Authentic Mac OS UI icons (SVG)
│   ├── apple.svg            # Apple logo
│   ├── button.svg           # Standard button border
│   ├── button-default.svg   # Default button border (thicker)
│   ├── checkmark.svg        # Checkbox checkmark
│   ├── radio-border.svg     # Radio button border
│   ├── radio-border-focused.svg  # Focused radio border
│   ├── radio-dot.svg        # Radio selected dot
│   ├── scrollbar-up.svg     # Scrollbar up arrow
│   ├── scrollbar-up-active.svg   # Active up arrow
│   ├── scrollbar-down.svg   # Scrollbar down arrow
│   ├── scrollbar-down-active.svg # Active down arrow
│   ├── scrollbar-left.svg   # Scrollbar left arrow
│   ├── scrollbar-left-active.svg # Active left arrow
│   ├── scrollbar-right.svg  # Scrollbar right arrow
│   ├── scrollbar-right-active.svg # Active right arrow
│   └── select-button.svg    # Select dropdown button
│
├── CREDITS.md               # Full license and attribution
└── README.md                # This file
```

## Fonts

### Font Family Reference

| Font Family | File Name | Purpose | Size |
|------------|-----------|---------|------|
| **Chicago** | ChicagoFLF | Headings, titles | 11KB (woff2) |
| **Chicago_12** | ChiKareGo2 | Primary UI text, buttons, menus | 4KB (woff2) |
| **Geneva_9** | FindersKeepers | Labels, captions, small text | 3KB (woff2) |
| **Monaco** | monaco | Monospace, code, terminal | 2KB (woff2) |

### Usage in CSS

```css
/* Import from desktop/desktop.css */
@font-face {
  font-family: Chicago_12;
  src: url('../system.css/fonts/ChiKareGo2.woff2') format('woff2'),
       url('../system.css/fonts/ChiKareGo2.woff') format('woff');
  font-display: swap;
}

/* Apply to UI elements */
body {
  font-family: Chicago_12, Geneva_9, Chicago, Monaco, 'Courier New', monospace;
}
```

### Font Stack Rationale

1. **Chicago_12** - Primary (authentic Mac UI font)
2. **Geneva_9** - Fallback for small text
3. **Chicago** - Fallback for display
4. **Monaco** - Fallback for monospace
5. **'Courier New'** - System fallback
6. **monospace** - Generic fallback

## Icons

### Icon Reference

| Icon | File | Dimensions | Purpose |
|------|------|------------|---------|
| **Button Border** | button.svg | Variable | Standard button borders via border-image |
| **Default Button** | button-default.svg | Variable | Default button (thicker border) |
| **Checkmark** | checkmark.svg | 12x12 | Checkbox checked state |
| **Radio Border** | radio-border.svg | 12x12 | Radio button outline |
| **Radio Focused** | radio-border-focused.svg | 12x12 | Radio button focused outline |
| **Radio Dot** | radio-dot.svg | 7x7 | Radio button selected dot |
| **Scrollbar Arrows** | scrollbar-*.svg | Variable | Scrollbar directional controls |

### Usage in CSS

```css
/* Button borders */
.btn {
  border-image-source: url("../system.css/icon/button.svg");
  border-image-width: 6;
  border-image-slice: 6;
}

/* Checkboxes */
input[type="checkbox"]:checked + label::after {
  background: url("../system.css/icon/checkmark.svg");
}

/* Radio buttons */
input[type="radio"] + label::before {
  background: url("../system.css/icon/radio-border.svg");
}

/* Scrollbars */
::-webkit-scrollbar-button:vertical:decrement {
  background-image: url("../system.css/icon/scrollbar-up.svg");
}
```

## Implementation Details

### Path Resolution

Since the desktop CSS is served from `/extensions/core/desktop/desktop.css`, paths use `../` to access the system.css directory:

```
extensions/core/
├── desktop/
│   └── desktop.css  ← CSS file location
└── system.css/      ← Asset location
    ├── fonts/
    └── icon/
```

Path in CSS: `url('../system.css/fonts/ChiKareGo2.woff2')`
Resolves to: `/extensions/core/system.css/fonts/ChiKareGo2.woff2`

### Font Format

- **Primary**: WOFF2 (best compression, modern browsers)
- **Fallback**: WOFF (wider browser support)
- **Not used**: TTF/OTF (legacy format, larger file sizes)

### Icon Format

- **Format**: SVG (scalable, crisp at any size)
- **Encoding**: Direct file references (not data URIs)
- **Advantage**: Cacheable, easier to update

## Performance

### Font Loading

Total font payload: **~20KB compressed** (WOFF2)
- Chicago_12: 4KB
- Geneva_9: 3KB
- Monaco: 2KB
- ChicagoFLF: 11KB

All fonts use `font-display: swap` for optimal loading:
1. Browser uses fallback font immediately
2. Custom font loads in background
3. Text swaps to custom font when ready
4. Prevents blocking page render

### Icon Loading

Total icon payload: **~20KB** (SVG)
- 17 icons averaging 1-2KB each
- Browser caches all icons after first load
- Scrollbar icons load on-demand

## Browser Compatibility

### Fonts
- ✅ Chrome/Edge (WOFF2 since 2014)
- ✅ Firefox (WOFF2 since 2015)
- ✅ Safari (WOFF2 since 2016)
- ✅ All modern browsers (WOFF fallback)

### Icons
- ✅ All modern browsers (SVG support)
- ✅ CSS background-image
- ✅ CSS border-image
- ✅ Webkit scrollbar styling (Chrome, Safari, Edge)

## Design Principles

### Authentic System 6 Aesthetic

1. **Pure Monochrome**: Black (#000), white (#fff), grey (#c0c0c0)
2. **Pixel-Perfect Borders**: 1-2px solid lines, no gradients
3. **Chunky Typography**: Chicago_12 at 12px for that authentic 1-bit feel
4. **Checkerboard Patterns**: Scrollbar tracks use classic Mac pattern
5. **Drop Shadows**: Simple 4px offset shadows (no blur)

### System.css Philosophy

From the original project:
> "A design system for building retro Apple-inspired interfaces. Based on the final monochrome version of macOS, System 6."

Key characteristics:
- Bitmapped fonts recreated as web fonts
- Pixel-perfect icon recreation
- Authentic form controls
- Classic Mac window chrome
- 1-bit aesthetic (only black and white, no anti-aliasing)

## License

**MIT License** - See [CREDITS.md](./CREDITS.md) for full text

### Attribution Required

When using system.css assets, include attribution:

```
Based on system.css v0.1.11 by Sakun Acharige (@sakofchit)
https://github.com/sakofchit/system.css
Fonts recreated by @blogmywiki
```

### What You Can Do

✅ Use commercially
✅ Modify and distribute
✅ Use in proprietary software
✅ Sublicense

### What You Must Do

⚠️ Include license and copyright notice
⚠️ State changes if you modify the files

## References

- **Official Demo**: https://sakofchit.github.io/system.css/
- **GitHub**: https://github.com/sakofchit/system.css
- **NPM**: @sakun/system.css
- **CDN**: https://unpkg.com/@sakun/system.css
- **Font Source**: http://ascii.co.uk/art/apple
- **System 6 Reference**: https://en.wikipedia.org/wiki/System_6

## Integration History

### Phase 8.14 (November 18, 2024)

**Authentic system.css Integration**

1. Cloned official system.css repository
2. Copied authentic fonts (4 families, 10 files, ~60KB)
3. Copied authentic icons (17 SVG files, ~20KB)
4. Updated desktop.css to use system.css assets
5. Added comprehensive credits and documentation

**Changes**:
- Replaced local TTF/OTF fonts with authentic WOFF/WOFF2
- Updated all @font-face declarations
- Added Geneva_9 font family
- Updated button borders to use system.css button.svg
- Updated form controls (checkboxes, radio buttons) to use system.css icons
- Updated scrollbar arrows to use system.css scrollbar icons
- Added proper MIT license attribution

**Result**: Authentic Apple System 6 aesthetic with modern web font technology

## Troubleshooting

### Fonts Not Loading

**Symptom**: Text appears in fallback fonts
**Check**: Browser DevTools → Network tab
**Expected**: 200 status for `/system.css/fonts/*.woff2`

**Solution**:
1. Verify files exist in `extensions/core/system.css/fonts/`
2. Check CSS path uses `../system.css/fonts/`
3. Clear browser cache
4. Restart HTTP server

### Icons Not Appearing

**Symptom**: Form controls or scrollbars missing icons
**Check**: Browser DevTools → Network tab
**Expected**: 200 status for `/system.css/icon/*.svg`

**Solution**:
1. Verify files exist in `extensions/core/system.css/icon/`
2. Check CSS path uses `../system.css/icon/`
3. Verify browser supports webkit scrollbar styling
4. Test in Chrome/Safari/Edge (best compatibility)

### Path Resolution Errors

**Symptom**: 404 errors for system.css assets
**Cause**: CSS served from `desktop/` subdirectory

**Solution**: Always use `../` prefix:
- ❌ Wrong: `url('system.css/fonts/...')`
- ✅ Correct: `url('../system.css/fonts/...')`

## Maintenance

### Updating system.css

To update to a newer version:

```bash
cd /Users/fredbook/Code/uDOS/extensions

# Backup current version
mv core/system.css core/system.css.backup

# Clone new version
git clone https://github.com/sakofchit/system.css.git system-css-temp --depth=1

# Copy assets
mkdir -p core/system.css
cp -r system-css-temp/fonts core/system.css/
cp -r system-css-temp/icon core/system.css/

# Cleanup
rm -rf system-css-temp

# Update CREDITS.md with new version number
```

### Verifying Installation

Quick verification checklist:

```bash
# Check fonts (should show 10 files)
ls -la /Users/fredbook/Code/uDOS/extensions/core/system.css/fonts/

# Check icons (should show 17 files)
ls -la /Users/fredbook/Code/uDOS/extensions/core/system.css/icon/

# Test server
cd /Users/fredbook/Code/uDOS/extensions/core
python3 -m http.server 8888

# Open in browser
open http://localhost:8888/desktop/index.html
```

## Support

For issues with:
- **system.css assets**: https://github.com/sakofchit/system.css/issues
- **uDOS integration**: See main uDOS documentation
- **Font licensing**: See CREDITS.md

---

**Last Updated**: November 18, 2024
**system.css Version**: v0.1.11
**uDOS Version**: v1.0.24-extensions
**Integrated By**: uDOS Development Team
