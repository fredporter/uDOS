# CoreUI Icons for uDOS

This directory contains the CoreUI free icon set used in the uDOS desktop environment.

## About CoreUI Icons

CoreUI Icons is a modern, free icon set with over 500 icons in multiple variants.

- **Icons**: 550+ icons
- **Format**: SVG
- **Style**: Linear, clean, professional
- **License**: CC BY 4.0 (See LICENSE below)

## Icons Used in uDOS Desktop

### Desktop Icons
- **cil-terminal.svg** - Terminal/CLI
- **cil-book.svg** - Documentation
- **cil-tv.svg** - Display
- **cil-text.svg** - Text Editor
- **cil-apps.svg** - Applications
- **cil-folder.svg** - File Browser

### Common UI Icons
- **cil-home.svg** - Home
- **cil-settings.svg** - Settings/Preferences
- **cil-search.svg** - Search
- **cil-file.svg** - File
- **cil-save.svg** - Save
- **cil-trash.svg** - Delete
- **cil-copy.svg** - Copy
- **cil-clipboard.svg** - Clipboard
- **cil-edit.svg** / **cil-pencil.svg** - Edit
- **cil-check.svg** - Confirm
- **cil-x.svg** - Close/Cancel
- **cil-plus.svg** - Add
- **cil-minus.svg** - Remove

### Navigation Icons
- **cil-arrow-left.svg** / **cil-arrow-right.svg** - Navigation
- **cil-arrow-top.svg** / **cil-arrow-bottom.svg** - Scroll
- **cil-chevron-*.svg** - Expand/Collapse

### Status Icons
- **cil-check-circle.svg** - Success
- **cil-x-circle.svg** - Error
- **cil-info.svg** - Information
- **cil-warning.svg** - Warning

### Media Icons
- **cil-media-play.svg** / **cil-media-pause.svg** - Playback
- **cil-volume-*.svg** - Audio controls
- **cil-image.svg** - Images

## License

### CoreUI Icons License

**License**: Creative Commons Attribution 4.0 International (CC BY 4.0)

**Copyright**: (c) 2024 creativeLabs Łukasz Holeczek

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.

**Attribution Example**:
```
Icons by CoreUI (https://coreui.io/icons/)
Licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
```

**Full License**: https://creativecommons.org/licenses/by/4.0/

## Usage in uDOS

### In HTML
```html
<img src="/extensions/icons/coreui/cil-terminal.svg" alt="Terminal" width="24" height="24">
```

### In CSS
```css
.icon-terminal {
  background-image: url('/extensions/icons/coreui/cil-terminal.svg');
  width: 24px;
  height: 24px;
}
```

### In Desktop Configuration
```javascript
{
  id: 'terminal',
  icon: '/extensions/icons/coreui/cil-terminal.svg',
  label: 'Terminal',
  action: 'openTerminal'
}
```

### In Character Editor

CoreUI icons can be:
1. Referenced in icon palette
2. Converted to bitmap glyphs (16×16 simplified versions)
3. Used as templates for custom icon creation

## Icon Naming Convention

CoreUI uses the `cil-` prefix (CoreUI Linear):
- **cil-[name].svg** - Standard icon
- Example: `cil-home.svg`, `cil-user.svg`

## Finding Icons

Browse all 550+ icons:
- **CoreUI Website**: https://coreui.io/icons/
- **GitHub**: https://github.com/coreui/coreui-icons
- **Search**: Use the character editor icon palette or browse this directory

## Customization

To modify CoreUI icons for uDOS:

1. Open SVG in text editor or vector graphics tool
2. Adjust size, colors, or styling
3. Save with descriptive name
4. Maintain attribution in comments
5. Document changes

Example SVG modification:
```xml
<!-- CoreUI cil-home.svg - Modified for uDOS -->
<!-- Original: https://coreui.io/icons/ -->
<svg>...</svg>
```

## Integration with Character Editor

The character editor's **Icons** character set includes:
- CoreUI icons as visual references
- Click to insert icon reference in grid
- Create bitmap versions for pixel art
- Export custom icon sets

## Adding More CoreUI Icons

uDOS currently includes ~40 commonly used CoreUI icons. To add more:

1. Download from https://github.com/coreui/coreui-icons
2. Copy `.svg` files to this directory
3. Update icon palette in character-editor.html
4. Test loading in desktop environment
5. Commit with attribution

## Alternative Icon Sets

uDOS also supports:
- **System Icons** (`/extensions/core/icons/`) - Classic Mac UI elements
- **Custom Icons** (`/memory/fonts/`) - User-created glyphs
- **Emoji** - GitHub emoji codes

## Resources

- **CoreUI Icons Website**: https://coreui.io/icons/
- **GitHub Repository**: https://github.com/coreui/coreui-icons
- **Icon Font**: https://coreui.io/icons/icon-font/
- **License Info**: https://creativecommons.org/licenses/by/4.0/

## Attribution in Projects

When using CoreUI icons in your uDOS projects or themes:

```markdown
## Icons

Icons provided by CoreUI Icons (https://coreui.io/icons/)
Licensed under CC BY 4.0
```

Or in code comments:
```javascript
// Icons: CoreUI Icons (CC BY 4.0) - https://coreui.io/icons/
```

## Support

For CoreUI icon issues:
- **CoreUI Support**: https://coreui.io/support/
- **uDOS Issues**: https://github.com/fredporter/uDOS/issues
- **Icon Requests**: File an issue on uDOS GitHub

## Version

- **CoreUI Icons Version**: Free 3.0+
- **Icons Included**: ~40 essential icons
- **Last Updated**: 2025-11-18
- **uDOS Version**: v1.0.24-extensions

---

**Attribution**: Icons by CoreUI (https://coreui.io/icons/) licensed under CC BY 4.0
