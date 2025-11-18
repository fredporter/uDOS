# PetMe Font Family

**Authentic Commodore PET/CBM Computer Fonts**

---

## Overview

The PetMe font family recreates the classic character sets from Commodore PET and CBM computers. Perfect for retro computing themes, terminal emulators, and vintage-style interfaces.

## Font Variants

### Standard Resolutions
- **PetMe.ttf** - Base PetMe font (standard resolution)
- **PetMe64.ttf** - Commodore 64 variant
- **PetMe128.ttf** - Commodore 128 variant

### Extended Variants
- **PetMe2X.ttf** - 2X width (double-wide characters)
- **PetMe2Y.ttf** - 2Y height (double-height characters)
- **PetMe642Y.ttf** - C64 with 2Y height
- **PetMe1282Y.ttf** - C128 with 2Y height

## Usage

### Terminal/Console
Perfect for:
- Retro terminal emulators
- Command-line interfaces
- Text editors with vintage themes
- ASCII art displays

### uDOS Themes
Use in theme configuration:
```json
{
  "theme": {
    "name": "commodore",
    "font": "PetMe64",
    "font_size": 12
  }
}
```

### Web Applications
```css
@font-face {
  font-family: 'PetMe';
  src: url('fonts/petme/PetMe.ttf') format('truetype');
}

.retro-terminal {
  font-family: 'PetMe', monospace;
  font-size: 14px;
  line-height: 1.2;
}
```

## Character Support

- Full ASCII character set (0x20-0x7E)
- Commodore PETSCII graphics characters
- Box-drawing characters
- Block graphics
- Authentic 8×8 pixel matrix design

## Recommended Settings

### For Modern Displays (High DPI)
- Font Size: 14-16pt
- Line Height: 1.2-1.4
- Letter Spacing: Normal
- Anti-aliasing: Off (for authentic pixel look)

### For Low Resolution / Retro Displays
- Font Size: 10-12pt
- Line Height: 1.0-1.2
- Letter Spacing: Normal
- Anti-aliasing: Off

## License

**Kreative Software Relay Fonts Free Use License v1.2f**

### You MAY:
✅ Use the fonts free of charge
✅ Display and embed in applications
✅ Redistribute with proper attribution
✅ Include in open-source projects

### You MAY NOT:
❌ Sell copies of the fonts for a fee
❌ Modify or create derivative works
❌ Remove or alter license information
❌ Use without including this license

### Requirements:
- Include `FreeLicense.txt` verbatim
- Credit Kreative Korporation / Kreative Software
- Distribute documentation with fonts

See `FreeLicense.txt` for complete license terms.

## Credits

**Created by**: Kreative Software / Kreative Korporation
**Based on**: Original Commodore PET/CBM character ROM
**License**: Kreative Software Relay Fonts Free Use License v1.2f

## Historical Context

The PetMe fonts recreate the iconic character sets from:
- **Commodore PET** (1977) - First personal computer from Commodore
- **Commodore CBM** (1980s) - Business-oriented Commodore systems
- **Commodore 64** (1982) - Best-selling single computer model of all time
- **Commodore 128** (1985) - Advanced 8-bit computer

These fonts preserve the authentic 8×8 pixel grid design that defined early personal computing.

## Related Fonts

Other retro fonts in uDOS collection:
- **ChicagoFLF** - Classic Macintosh System font
- **chicago-12-1** - Enhanced Chicago variant
- **Mallard family** - Modern monospace with retro feel
- **sysfont** - Clean system font

## Support

For issues or questions about PetMe fonts:
- **License questions**: Contact Kreative Software
- **uDOS integration**: See main uDOS documentation
- **Technical issues**: Check uDOS issue tracker

---

**Part of the uDOS font collection**
**See**: `../LICENSE_ASSESSMENT.md` for complete licensing overview
