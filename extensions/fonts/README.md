# uDOS Extensions - Retro Fonts Collection

This folder contains legally licensed retro fonts for use across uDOS extensions.

## 📁 Font Families

### **chicago/** - Apple System Font
Classic Macintosh System font recreations.

**Variants:**
- `ChicagoFLF.ttf` - Public domain recreation (recommended)
- `chicago-12-1.otf` - Enhanced FontStruct variant (CC BY-SA)

**Use in:** System 7 Desktop, classic Mac interfaces

### **mallard/** - BBC Teletext Font
Authentic BBC Teletext rendering fonts.

**Variants:**
- `mallard-blocky.otf` - Base version
- `mallard-blockier.otf` - Angular variant
- `mallard-smooth.otf` - Softened edges
- `mallard-smoother.otf` - Extra smooth
- `mallard-neueue.otf` - Modern interpretation
- `mallard-tiny.otf` - Compact variant

**Use in:** Teletext extension, retro broadcast interfaces

### **petme/** - Commodore PET/CBM Font
Authentic Commodore computer fonts.

**Variants:**
- `PetMe.ttf` - Standard PET/CBM
- `PetMe64.ttf` - Commodore 64
- `PetMe128.ttf` - Commodore 128
- `PetMe2X.ttf`, `PetMe2Y.ttf` - Scaled variants
- `PetMe642Y.ttf`, `PetMe1282Y.ttf` - C64/C128 scaled

**Use in:** C64 Terminal, Commodore-themed interfaces

## 📄 Licensing

All fonts are legally distributable. See `LICENSE_ASSESSMENT.md` for complete legal analysis.

**Quick Summary:**
- ✅ Chicago (ChicagoFLF): Public domain
- ✅ Chicago (12-1): CC BY-SA 3.0
- ✅ Mallard: CC BY-SA 3.0
- ✅ PetMe: Kreative Software Free Use License v1.2f

## 🎨 Usage in Extensions

### Font Fallback Stacks

uDOS uses proper fallback stacks to ensure text displays correctly even if custom fonts fail to load.

**Recommended Fallback Patterns:**

```css
/* Chicago (System 7 Desktop) */
font-family: 'Chicago', 'Chicago FLF', -apple-system, BlinkMacSystemFont, monospace;

/* Mallard (Teletext) */
font-family: 'Mallard', 'MODE7GX3', 'Courier New', monospace;

/* PetMe (C64 Terminal) */
font-family: 'PetMe64', 'PetMe', 'Courier New', monospace;

/* Generic Monospace */
font-family: 'Monaco', 'Courier New', 'Courier', monospace;
```

### CSS @font-face Example

```css
/* Chicago Font */
@font-face {
    font-family: 'Chicago';
    src: url('fonts/chicago/ChicagoFLF.ttf') format('truetype');
    font-display: swap;
}

/* Mallard Font */
@font-face {
    font-family: 'Mallard';
    src: url('fonts/mallard/mallard-blocky.otf') format('opentype');
    font-display: swap;
}

/* PetMe Font */
@font-face {
    font-family: 'PetMe64';
    src: url('fonts/petme/PetMe64.ttf') format('truetype');
    font-display: swap;
}
```

### Using in Extensions

```html
<!-- System 7 Desktop -->
<div style="font-family: 'Chicago', -apple-system, monospace;">
    Classic Mac Interface
</div>

<!-- Teletext -->
<div style="font-family: 'Mallard', 'Courier New', monospace;">
    BBC Teletext Page 100
</div>

<!-- C64 Terminal -->
<div style="font-family: 'PetMe64', 'Courier New', monospace;">
    READY.
</div>
```

**Best Practices:**
- Always include `font-display: swap` to prevent invisible text
- Use relative paths from extension root (e.g., `fonts/chicago/`)
- Include generic fallbacks (`monospace`, `sans-serif`)
- Test with fonts disabled to verify fallbacks work

## 🔧 Maintenance

- **Added**: November 2024 (v1.0.24 reorganization)
- **Cleanup**: November 17, 2025
  - Removed: sysfont (uncertain provenance)
  - Consolidated: Mallard (6 variants → 1 folder)
  - Consolidated: Chicago (2 variants → 1 folder)

## 📚 Resources

- **FontStruct**: https://fontstruct.com (Chicago, Mallard sources)
- **Kreative Software**: https://www.kreativekorp.com/software/fonts/ (PetMe fonts)
- **License Details**: See `LICENSE_ASSESSMENT.md`

---

**All fonts properly licensed for use in uDOS extensions.**
