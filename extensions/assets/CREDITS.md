# uDOS Assets Credits

Complete attribution for all fonts, icons, CSS frameworks, and JavaScript libraries.

## Fonts

### System.css Fonts (MIT License)
**ChiKareGo2** (Chicago_12), **FindersKeepers** (Geneva_9), **ChicagoFLF**, **monaco**

- **Source**: system.css v0.1.11
- **Author**: Sakun Acharige (@sakofchit)
- **Font Recreation**: @blogmywiki
- **License**: MIT License
- **URL**: https://github.com/sakofchit/system.css
- **Usage**: Classic System 6 UI fonts

### Specialty Fonts

#### C64 User Mono
- **Style**: Commodore 64 monospace
- **License**: Custom (see font directory)
- **Usage**: Retro computing aesthetics

#### Chicago Family
- **Location**: `fonts/chicago/`
- **Style**: Extended Chicago font family
- **License**: See font directory

#### Mallard Fonts
- **Location**: `fonts/mallard/`
- **License**: See font directory

#### PetMe Fonts
- **Location**: `fonts/petme/`
- **Style**: PET computer style
- **License**: See font directory

**Complete Font Licensing**: See `fonts/LICENSE_ASSESSMENT.md`

## Icons

### System.css Icons (MIT License)
**18 SVG Icons**: Buttons, checkmarks, radio buttons, scrollbar arrows, Apple logo

- **Author**: Sakun Acharige (@sakofchit)
- **Source**: system.css v0.1.11
- **License**: MIT License
- **URL**: https://github.com/sakofchit/system.css
- **Icons**:
  - `button.svg`, `button-default.svg`
  - `checkmark.svg`
  - `radio-border.svg`, `radio-border-focused.svg`, `radio-dot.svg`
  - `scrollbar-up.svg`, `scrollbar-down.svg`, `scrollbar-left.svg`, `scrollbar-right.svg`
  - `scrollbar-up-active.svg`, `scrollbar-down-active.svg`, `scrollbar-left-active.svg`, `scrollbar-right-active.svg`
  - `select-button.svg`
  - `apple.svg`

### CoreUI Icons (Mixed Licenses)
**1500+ Icons**: Free, brand, and flag icon sets with CSS integration

- **Source**: CoreUI Icons v2.0+
- **URL**: https://coreui.io/icons/
- **Location**: `icons/coreui/`
- **CSS Files**: `icons/coreui/css/` (free.min.css, all.min.css, brand.min.css, flag.min.css)
- **Font Files**: `icons/coreui/fonts/` (CoreUI-Icons-Free.ttf, .woff, .woff2, .eot, .svg)

**Licenses**:
- **Free Icons**: CC BY 4.0 (SVG/JS), SIL OFL 1.1 (fonts), MIT (code)
- **Brand Icons**: CC0 1.0 Universal (trademarks belong to respective owners)
- **Flag Icons**: CC0 1.0 Universal

**CSS Integration**:
- Copied from `/extensions/cloned/coreui/` to `/extensions/assets/icons/coreui/`
- Includes: `free.css`, `all.css`, `brand.css`, `flag.css` (+ minified versions and maps)
- Font files: `.ttf`, `.woff`, `.woff2`, `.eot`, `.svg` formats for broad compatibility
- Font references updated for unified asset structure

**Usage**:
```html
<link rel="stylesheet" href="/assets/icons/coreui/css/free.min.css">
<i class="cil-menu"></i>
<i class="cil-pencil"></i>
<i class="cil-moon"></i>
```

**Documentation**: See `icons/coreui/README.md`

## CSS Frameworks

### System.css v0.1.11 (MIT License)
**Complete Classic System 6 UI framework**

- **Author**: Sakun Acharige (@sakofchit)
- **License**: MIT License
- **URL**: https://github.com/sakofchit/system.css
- **Files**:
  - `system.css` - Main framework
  - `system-classic.css` - Classic-specific components
  - `typography-system.css` - Font definitions
  - `classic-patterns.css` - Background patterns

### Arcade.css
**Nintendo Entertainment System UI framework**

- **License**: MIT License
- **URL**: https://github.com/nostalgic-css/NES.css
- **File**: `nes.css`

### uDOS Frameworks (MIT License)
**Custom frameworks developed for uDOS**

- **Author**: Fred Porter
- **License**: MIT License
- **Files**:
  - `synthwave-dos-colors.css` - Synthwave/DOS color palette
  - `udos-grid.css` - Grid layout system
  - `udos-syntax.css` - Code syntax highlighting
  - `udos-filepicker.css` - File picker component
  - `udos-v13-theme.css` - Version 1.3 theme
  - `classic.css` - Classic computing aesthetics
  - `classic-icons.css` - Classic icon integration

## JavaScript Libraries

### uDOS Components (MIT License)
**Custom UI components and utilities**

- **Author**: Fred Porter
- **License**: MIT License
- **Files**:
  - `udos-controls.js` - Form controls and widgets
  - `udos-panels.js` - Panel components
  - `udos-option-selector.js` - Option selection UI
  - `udos-filepicker.js` - File picker implementation
  - `typography-manager.js` - Font loading and management

## License Summary

### MIT License Assets
- system.css (fonts, icons, CSS)
- NES.css
- uDOS custom frameworks
- uDOS JavaScript components

### Creative Commons Assets
- CoreUI free icons (CC BY 4.0)
- CoreUI brand/flag icons (CC0 1.0)

### Font-Specific Licenses
- SIL OFL 1.1 (CoreUI webfonts)
- Custom licenses (see individual font directories)

## Attribution Requirements

### Using system.css Assets
```html
<!--
  system.css v0.1.11
  Copyright (c) 2020 Sakun Acharige (@sakofchit)
  Licensed under MIT License
  https://github.com/sakofchit/system.css
-->
```

### Using CoreUI Icons
```html
<!--
  CoreUI Icons
  Copyright (c) 2024 CoreUI
  Free Icons: CC BY 4.0
  https://coreui.io/icons/
-->
```

### Using uDOS Assets
```html
<!--
  uDOS Extensions
  Copyright (c) 2024-2025 Fred Porter
  Licensed under MIT License
-->
```

## Full License Texts

### MIT License
```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### SIL OFL 1.1 (Font License)
See: https://scripts.sil.org/OFL

### CC BY 4.0 (CoreUI Free Icons)
See: https://creativecommons.org/licenses/by/4.0/

### CC0 1.0 Universal (CoreUI Brand/Flag Icons)
See: https://creativecommons.org/publicdomain/zero/1.0/

## Acknowledgments

Special thanks to:
- **Sakun Acharige** (@sakofchit) - system.css framework and authentic Mac assets
- **@blogmywiki** - Font recreation and preservation
- **CoreUI Team** - Comprehensive icon library
- **NES.css Contributors** - Retro gaming aesthetics
- **Open source community** - Making these resources freely available

## Version History

**November 18, 2025** - Initial consolidated credits
- Merged all font, icon, CSS, and JS attributions
- Centralized license information
- Created comprehensive documentation

---

**Maintained by**: uDOS Project
**Last Updated**: November 18, 2025
**License Compliance**: All assets properly attributed
