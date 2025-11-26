# uDOS Core Fonts

This directory contains fonts used in the uDOS desktop environment and character editor.

## Fonts Included

### Classic Fonts
- **ChicagoFLF** - Classic Macintosh system font
- **ChiKareGo2** - Classic OS 9-style font
- **FindersKeepers** - Classic Finder-style font
- **Monaco** - Classic monospace font

### Retro/Gaming Fonts
- **C64_User_Mono_v1.0-STYLE** - Commodore 64 style font
- **giana** - C64 game font

## License Information

### Classic Fonts (ChicagoFLF, ChiKareGo2, FindersKeepers, Monaco)
These fonts are recreations/tributes to classic Macintosh system fonts.

- **ChicagoFLF**: Created by Robin Casady (fLf Fonts)
  - License: Free for personal and commercial use
  - Source: https://freefontsdownload.net/free-chicagoflf-font

- **ChiKareGo2**: Custom bitmap font
  - License: Free for use in open source projects

- **FindersKeepers**: Classic Finder tribute font
  - License: Free for personal use

- **Monaco**: Monospace font (tribute to Apple's Monaco)
  - License: Free for personal and commercial use

### C64 Fonts
- **C64_User_Mono_v1.0-STYLE**: Commodore 64 system font recreation
  - Author: Style
  - License: Free for personal and commercial use
  - Source: https://style64.org/

- **giana**: C64 game font
  - License: Free for personal use
  - Part of c64css3 project

## Usage

These fonts are centralized in `/extensions/core/fonts/` for:
- Desktop UI styling
- Character editor
- Retro terminal emulation
- Theme customization

### Loading Fonts in CSS

```css
@font-face {
  font-family: 'Chicago_12';
  src: url('/extensions/core/fonts/ChicagoFLF.woff2') format('woff2'),
       url('/extensions/core/fonts/ChicagoFLF.woff') format('woff');
}

@font-face {
  font-family: 'C64_User';
  src: url('/extensions/core/fonts/C64_User_Mono_v1.0-STYLE.woff') format('woff');
}
```

## Character Sets

The character editor supports multiple character sets:
- **ASCII**: Standard printable characters (32-126)
- **Block Graphics**: Unicode box drawing (▀▄█▌▐░▒▓)
- **C64 PETSCII**: Commodore 64 graphics characters (♠♥♦♣●○)
- **Teletext**: Teletext block graphics
- **Markdown**: Box drawing for tables and diagrams (─│┌┐└┘├┤┬┴┼)
- **Emoji**: GitHub emoji support (:smile: :fire: :heart:)
- **CoreUI Icons**: Icon font references

## Custom Font Creation

Users can create custom bitmap fonts using the character editor:
1. Draw glyphs in the 16×16 pixel grid
2. Map to keyboard keys or character codes
3. Export as JSON
4. Save to `/memory/fonts/` for personal use
5. Share with community via `/memory/shared/`

## Attribution

If you use these fonts in your project, please include attribution:

```
Fonts from uDOS Desktop Environment
- ChicagoFLF by Robin Casady (fLf Fonts)
- C64 fonts from Style64.org
- System fonts recreated for retro computing
```

## Adding New Fonts

To add a new font to uDOS:

1. Place `.woff` and `.woff2` files in this directory
2. Update `desktop.css` with `@font-face` declaration
3. Add to character editor character sets if applicable
4. Document license and attribution in this README
5. Test loading in desktop environment

## Support

For font issues or licensing questions:
- Check uDOS documentation: `/docs/`
- File issue: https://github.com/fredporter/uDOS/issues
- Community: uDOS wiki

---

**Last Updated**: 2025-11-18
**uDOS Version**: v1.0.24-extensions
