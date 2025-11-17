# Teletext Extension - Credits

## BBC Teletext Standards

### Teletext Specification
- **Standard**: BBC Teletext Level 1 (1976)
- **Character Set**: 40×25 character grid
- **Graphics**: Mode 7 block graphics and mosaic characters
- **Colors**: 8 colors (black, red, green, yellow, blue, magenta, cyan, white)

### Fonts
- **Mallard Font Family**: 6 variants for authentic BBC Teletext rendering
- **Author**: "gid" (FontStruct.com)
- **License**: Creative Commons Attribution Share Alike 3.0
- **Variants**:
  - mallard-blocky.otf (base version)
  - mallard-blockier.otf (angular)
  - mallard-smooth.otf (softened)
  - mallard-smoother.otf (extra smooth)
  - mallard-neueue.otf (modern)
  - mallard-tiny.otf (compact)
- **Location**: `/extensions/fonts/mallard/`
- **Full License**: `/extensions/fonts/mallard/LICENSE.txt`

## Color Palette

### Polaroid Enhancement
- **Phase 3** (November 2024): Teletext Polaroid Enhancement
- **Purpose**: Synthwave DOS color integration with BBC Teletext standards
- **Documentation**: See `README-POLAROID.md`

## Implementation

### Core Technology
- **HTML5**: Semantic markup for teletext pages
- **CSS3**: Mode 7 graphics emulation, block character rendering
- **JavaScript**: Page navigation, control codes, character set management

### Features
- Authentic 40×25 character grid
- Mode 7 block graphics support
- Teletext control codes (colors, graphics, flash, etc.)
- Page numbering system (100-899)
- Double-height text support
- Hidden/revealed text functionality

## Design References

### BBC Teletext
- **Service**: CEEFAX (BBC), Oracle (ITV)
- **Era**: 1976-2012
- **Technology**: Vertical blanking interval broadcast
- **Standards**: Teletext Level 1 specification

### Historical Context
- UK broadcast standard
- Information service via TV signal
- News, weather, subtitles, program listings
- Iconic retro aesthetic

## Development

### v1.0.24 Reorganization
- **Phase 3** (Commit 9afaf4b): Polaroid enhancement
- **Features**: Synthwave DOS colors, improved rendering, BBC standards compliance
- **Integration**: Mallard fonts, authentic character grid

---

**Created**: November 2024
**Version**: v1.0.24
**License**: See main uDOS LICENSE
**Font Attribution**: Mallard family by gid (FontStruct.com), CC BY-SA 3.0
