# uDOS Core Icons

This directory contains system icons used in the uDOS desktop environment.

## Icons Included

### System Icons (SVG)
- **apple.svg** - Mac menu bar apple icon
- **button.svg** / **button-default.svg** - Button styling elements
- **checkmark.svg** - Checkbox/selection indicator
- **radio-border.svg** / **radio-border-focused.svg** / **radio-dot.svg** - Radio button elements
- **scrollbar-*.svg** - Scrollbar controls (up, down, left, right, active states)
- **select-button.svg** - Dropdown/select control

## License Information

### system.css Icons
These icons are part of the system.css project, recreating classic Mac OS UI elements.

- **License**: MIT License
- **Source**: https://github.com/sakofchit/system.css
- **Attribution**: Copyright (c) 2020 Saketh Kasibatla

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

## CoreUI Icons

CoreUI icons are stored separately in `/extensions/icons/coreui/`.

See `/extensions/icons/coreui/LICENSE` for CoreUI icon licensing.

## Usage

### In CSS

```css
.checkbox {
  background-image: url('/extensions/core/icons/checkmark.svg');
}

.scrollbar-up {
  background-image: url('/extensions/core/icons/scrollbar-up.svg');
}
```

### In HTML

```html
<img src="/extensions/core/icons/apple.svg" alt="Menu">
```

### In Character Editor

System icons can be referenced in the character editor for creating custom glyphs based on UI elements.

## Icon Sets Integration

The character editor supports multiple icon sources:

1. **System Icons** (this folder) - UI control elements
2. **CoreUI Icons** (`/extensions/icons/coreui/`) - Modern icon set
3. **Custom Glyphs** - User-created bitmap icons in `/memory/fonts/`

## Creating Custom Icons

To add custom icons:

1. Create SVG file with consistent size (typically 16×16 or 24×24)
2. Save to this directory
3. Reference in CSS or HTML
4. Optional: Add to character editor icon palette

### SVG Guidelines

- Use viewBox for scalability
- Keep paths simple for rendering performance
- Use monochrome for system consistency
- Test at multiple sizes

## Icon Palette

Character editor provides icon insertion:
- System icons for UI mockups
- CoreUI icons for modern interfaces
- Emoji for expressive content
- Custom glyphs for specialized needs

## Attribution

When using uDOS icons in projects:

```
Icons from uDOS Desktop Environment
- System icons based on system.css (MIT License)
- CoreUI Icons (CoreUI License)
- Custom icons by uDOS contributors
```

## Adding New Icon Sets

To integrate a new icon library:

1. Create subdirectory: `/extensions/icons/[name]/`
2. Add icon files
3. Create LICENSE file
4. Update character editor icon palette
5. Document in this README
6. Add to desktop.css if needed

## Resources

- **system.css Icons**: https://github.com/sakofchit/system.css
- **CoreUI Icons**: https://coreui.io/icons/
- **Icon Design Guidelines**: `/docs/guides/icon-design.md`
- **Character Editor Docs**: `/extensions/core/desktop/CHARACTER-EDITOR-INTEGRATION.md`

## Support

For icon-related issues:
- Check uDOS documentation: `/docs/`
- File issue: https://github.com/fredporter/uDOS/issues
- Community: uDOS wiki

---

**Last Updated**: 2025-11-18
**uDOS Version**: v1.0.24-extensions
