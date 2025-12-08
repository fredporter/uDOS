# uDOS Assets Library

**Centralized asset management for all uDOS extensions**

## Directory Structure

```
assets/
├── fonts/          # All font files (WOFF, WOFF2, TTF)
├── icons/          # All icon sets (SVG, PNG)
├── css/            # Shared CSS frameworks and themes
├── js/             # Shared JavaScript libraries
└── README.md       # This file
```

## Fonts (`fonts/`)

### System Fonts
- **ChiKareGo2** (Chicago_12) - Primary UI font, Apple System 6 style
- **FindersKeepers** (Geneva_9) - Small text font, classic Mac
- **ChicagoFLF** - Display font, Mac System 6
- **monaco** - Monospace font, classic Mac terminal

### Specialty Fonts
- **C64_User_Mono** - Commodore 64 style
- **giana** - Retro gaming style
- **chicago/** - Extended Chicago font family
- **mallard/** - Custom display fonts
- **petme/** - PET-style fonts

**Formats**: WOFF2 (primary), WOFF (fallback)
**License**: See individual font directories and `LICENSE_ASSESSMENT.md`

## Icons (`icons/`)

### System Icons (system.css v0.1.11)
Classic Mac System 6 UI elements:
- `button.svg`, `button-default.svg` - Button styles
- `checkmark.svg` - Checkbox checkmark
- `radio-border.svg`, `radio-dot.svg` - Radio button elements
- `scrollbar-*.svg` - Scrollbar arrows (up, down, left, right)
- `select-button.svg` - Dropdown select button
- `apple.svg` - Apple logo

### CoreUI Icons
1500+ icons from CoreUI Icons (MIT License):
- Located in `coreui/` subdirectory
- SVG, PNG, and webfont formats
- Free, brand, and flag icon sets

**License**: See `icons/coreui/README.md` and individual READMEs

## CSS (`css/`)

### Theme Frameworks
- **synthwave-dos-colors.css** - Synthwave/DOS color palette
- **classic-mac-patterns.css** - Mac OS classic patterns
- **system.css** - Complete system.css v0.1.11 framework
- **system-mac.css** - Mac System 6 UI components
- **classic.css** - Classic computing aesthetics
- **arcade.css** - Arcade-style UI framework

### Typography
- **typography-system.css** - System font definitions
- **typography-manager.js** - Font loading and management

### uDOS Components
- **udos-grid.css** - Grid layout system
- **udos-syntax.css** - Code syntax highlighting
- **udos-filepicker.css** - File picker component
- **udos-v13-theme.css** - Version 1.3 theme

### Icon Integration
- **mac-icons.css** - Mac icon font integration

## JavaScript (`js/`)

### UI Components
- **udos-controls.js** - Form controls and widgets
- **udos-panels.js** - Panel components
- **udos-option-selector.js** - Option selection UI
- **udos-filepicker.js** - File picker implementation
- **typography-manager.js** - Font loading and management

## Usage

### In HTML
```html
<!-- Fonts -->
<link rel="stylesheet" href="../assets/fonts/chicago/chicago.css">

<!-- Icons -->
<link rel="stylesheet" href="../assets/icons/coreui/css/free.min.css">

<!-- CSS Frameworks -->
<link rel="stylesheet" href="../assets/css/synthwave-dos-colors.css">
<link rel="stylesheet" href="../assets/css/system.css">
<link rel="stylesheet" href="../assets/css/udos-grid.css">

<!-- JavaScript -->
<script src="../assets/js/udos-controls.js"></script>
<script src="../assets/js/typography-manager.js"></script>
```

### In CSS
```css
/* Import from assets */
@import url('../assets/css/synthwave-dos-colors.css');
@import url('../assets/css/typography-system.css');

/* Use fonts */
@font-face {
  font-family: 'Chicago_12';
  src: url('../assets/fonts/ChiKareGo2.woff2') format('woff2'),
       url('../assets/fonts/ChiKareGo2.woff') format('woff');
}

/* Use icons */
.button {
  background-image: url('../assets/icons/button.svg');
}

/* CoreUI Icons */
.icon-menu::before {
  content: "\ea60"; /* cil-menu */
}
```

## Path Resolution

From different extension locations:

**From `/extensions/core/desktop/`**:
```
../../assets/fonts/
../../assets/icons/
../../assets/css/
../../assets/js/
```

**From `/extensions/core/markdown/`**:
```
../../assets/fonts/
../../assets/icons/
../../assets/css/
../../assets/js/
```

## Credits

### Fonts
- **system.css fonts** - Recreated by @blogmywiki, MIT License
- **Chicago, Geneva, Monaco** - Classic Apple fonts (system.css v0.1.11)
- **C64 User Mono** - Commodore 64 style font
- See `fonts/LICENSE_ASSESSMENT.md` for complete attribution

### Icons
- **system.css icons** - Sakun Acharige (@sakofchit), MIT License
- **CoreUI Icons** - 1500+ icons (CC BY 4.0, MIT, CC0)
  - CSS files: `icons/coreui/css/free.min.css`, `all.min.css`, `brand.min.css`, `flag.min.css`
  - Icon classes: `cil-*` (e.g., `<i class="cil-menu"></i>`)
  - https://coreui.io/icons/
- **CoreUI Icons** - CoreUI.io, MIT License (free icons), CC BY 4.0 (icons), SIL OFL 1.1 (fonts)
- See individual icon directories for specific licenses

### CSS Frameworks
- **system.css v0.1.11** - Sakun Acharige (@sakofchit), MIT License
- **Arcade.css** - Various contributors
- **uDOS frameworks** - Fred Porter, MIT License

### JavaScript
- **uDOS components** - Fred Porter, MIT License

## Migration Notes

### Old Paths → New Paths

**Fonts**:
- `../fonts/` → `../assets/fonts/`
- `../core/fonts/` → `../assets/fonts/`

**Icons**:
- `../icons/` → `../assets/icons/`
- `../core/icons/` → `../assets/icons/`

**CSS**:
- `../core/css/` → `../assets/css/`
- Shared CSS now centralized

**JavaScript**:
- `../core/js/` → `../assets/js/`
- Shared JS now centralized

### Archive Locations
Old directories have been archived to:
- `/extensions/archive/old-fonts/`
- `/extensions/archive/old-icons/`
- `/extensions/archive/old-core-assets/`

## Maintenance

### Adding New Assets

1. **Fonts**: Add to `assets/fonts/` with README and license info
2. **Icons**: Add to `assets/icons/` with attribution
3. **CSS**: Add to `assets/css/` with documentation
4. **JS**: Add to `assets/js/` with JSDoc comments

### Updating Paths

When moving or renaming assets:
1. Update this README
2. Update all extension references
3. Update CREDITS.md files
4. Test all extensions

### License Compliance

All assets must include:
- License file or reference
- Attribution to original authors
- Usage restrictions (if any)

## Version History

**v1.0.24** (November 18, 2025)
- Initial consolidated assets structure
- Merged fonts/, core/fonts/, icons/, core/icons/
- Centralized CSS and JS from core/
- Created comprehensive documentation
- Archived old structure

---

**Location**: `/extensions/assets/`
**Maintained by**: uDOS Project
**License**: Mixed (see individual asset directories)
