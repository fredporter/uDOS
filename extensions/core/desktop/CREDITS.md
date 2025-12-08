# Desktop Extension - Credits

## Primary Framework: system.css

### Core UI Library
- **system.css**: Authentic Classic desktop CSS framework (based on Apple System 6 - final monochrome Mac OS)
- **Version**: v0.1.11
- **Author**: Sakun Acharige (@sakofchit)
- **Source**: https://github.com/sakofchit/system.css
- **License**: MIT License
- **Internal reference**: **Classic styling**
- **Usage**: Authentic fonts, icons, and UI styling for classic desktop aesthetic

### Fonts (by @blogmywiki)
All fonts meticulously recreated to match original Mac OS System 6:
- **Chicago_12** (ChiKareGo2): Primary UI font for menus, dialogs, buttons
- **Geneva_9** (FindersKeepers): Small system font for labels and captions
- **ChicagoFLF**: Display font for headings and titles
- **Monaco**: Monospace font for terminal and code
- **Format**: WOFF2/WOFF (modern web fonts)
- **Location**: `/extensions/core/system.css/fonts/`
- **Credits**: See `/extensions/core/system.css/CREDITS.md`

### Icons (system.css)
Authentic Classic desktop UI icons (Mac OS System 6 style):
- Form controls: checkboxes, radio buttons, checkmarks
- Buttons: standard and default button borders
- Scrollbars: arrow icons for all directions (active/inactive states)
- **Location**: `/extensions/core/system.css/icon/`
- **Format**: SVG
- **Count**: 17 authentic UI icons

## Additional Icons: Mono Icon Theme

### Desktop Application Icons
- **Mono Icon Theme**: Professional monochrome icon set
- **Author**: Vitali Hirsch (@witalihirsch)
- **Source**: https://github.com/witalihirsch/Mono-icon-theme
- **License**: GPL-3.0
- **Usage**: Desktop application shortcuts (Terminal, Files, Knowledge, etc.)
- **Location**: `/extensions/icons/mono/`
- **Count**: 1000+ SVG icons
- **Categories**: devices, mimetypes, places, legacy, categories, actions, apps

## Historical References

### Early Mac Desktop Development
- **Classicy Desktop** by Robbie Byrd: Initial reference (Phase 7)
- **Source**: https://github.com/robbiebyrd/classicy
- **License**: MIT License
- **Usage**: Studied for window management patterns

### Color Scheme Evolution
- **Phase 7** (v1.0.24): Initial Synthwave DOS + System 7 hybrid
- **Phase 8.12** (v1.0.24): Transition to pure monochrome
- **Phase 8.13** (v1.0.24): Cleanup and Mono icons integration
- **Current**: Authentic system.css with monochrome aesthetic

## Design Philosophy

### Apple System 6 (1984-1991) - Original Inspiration
- **Interface**: Final monochrome Mac OS version
- **Color Palette**: Pure black (#000), white (#fff), grey (#c0c0c0)
- **Typography**: Chicago_12 primary, Geneva_9 secondary, Monaco monospace
- **Patterns**: Checkerboard scrollbar tracks, pixel-perfect borders
- **Window Chrome**: Classic window shadows (4px offset)
- **Internal reference**: **Classic styling** (brand-neutral)

### uDOS Integration
- **system.css assets**: Primary UI chrome (buttons, forms, scrollbars, fonts)
- **Mono icons**: Desktop application shortcuts
- **Custom features**: Command Palette (Cmd/Ctrl+K), window management, keyboard shortcuts

## JavaScript Implementation

### Window Management
- **Custom Implementation**: uDOS Desktop window manager
- **Features**:
  * Draggable windows with classic shadows
  * Command Palette (Cmd/Ctrl+K)
  * Keyboard shortcuts (Cmd/Ctrl+W to close)
  * Desktop icon grid system
  * Focus management

## License Summary

### MIT Licensed Components
- system.css (fonts, icons, CSS framework) - Sakun Acharige
- Classicy Desktop (reference) - Robbie Byrd

### GPL-3.0 Licensed Components
- Mono Icon Theme (desktop icons) - Vitali Hirsch

### Public Domain / Fair Use
- Classic desktop interface design (inspired by Mac OS System 6, 1984-1991)
- Trademark: Mac OS and System 6 are trademarks of Apple Inc.

All fonts properly licensed - see `/extensions/core/system.css/CREDITS.md` for detailed attribution.

## Version History

- **Phase 7** (November 17, 2024): Initial System Desktop with Synthwave colors
- **Phase 8.12** (November 18, 2024): Pure monochrome styling, Chicago fonts
- **Phase 8.13** (November 18, 2024): Cleanup, Mono icons integration
- **Phase 8.14** (November 18, 2024): Authentic system.css fonts and icons

---

**Created**: November 17, 2024
**Last Updated**: November 18, 2024
**Version**: v1.0.24-extensions
**Aesthetic**: Apple System 6 (1984-1991) via system.css v0.1.11
**License**: See main uDOS LICENSE
