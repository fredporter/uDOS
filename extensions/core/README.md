# uDOS Core Components

Core shared components for uDOS extensions and web interfaces.

## Directory Structure

```
extensions/core/
├── css/              # Core CSS components
│   ├── udos-grid.css       # Grid system
│   ├── udos-syntax.css     # Syntax highlighting
│   ├── typography-system.css
│   └── udos-filepicker.css
├── js/               # JavaScript utilities
│   ├── typography-manager.js
│   ├── udos-controls.js
│   ├── udos-panels.js
│   └── udos-filepicker.js
├── themes/           # Theme definitions
│   ├── classic.css
│   ├── system.css
│   ├── system-mac.css
│   ├── classic-mac-patterns.css
│   ├── nes.css
│   └── udos-v13-theme.css
├── docs/             # Documentation
│   ├── CSS-FRAMEWORKS-GUIDE.md
│   ├── GRID-SYSTEM.md
│   ├── README-Typography.md
│   ├── shared-components.md
│   ├── SYSTEM-CSS-REFERENCE.md
│   ├── typography-showcase.html
│   └── ugrid-demo.html
└── assets/           # Static assets
    ├── icons/
    └── img/
```

## Core Components

### Grid System
The uDOS Grid System provides a consistent layout framework based on 16×16 pixel cells.
- `udos-grid.css`: Core grid implementation
- See `GRID-SYSTEM.md` for detailed documentation

### Typography
Advanced typography system with monospace optimization.
- `typography-system.css`: Core typography styles
- `typography-manager.js`: Dynamic font loading and management
- See `README-Typography.md` for usage

### Themes
Collection of themes matching different retro computing eras:
- Classic DOS
- System (Windows 3.x)
- Classic Mac
- NES-style

### UI Components
- File Picker: `udos-filepicker.css` + `udos-filepicker.js`
- Control Elements: `udos-controls.js`
- Panel Management: `udos-panels.js`

## Usage

1. Include required CSS:
```html
<link rel="stylesheet" href="/extensions/core/css/udos-grid.css">
<link rel="stylesheet" href="/extensions/core/themes/classic.css">
```

2. Include required JavaScript:
```html
<script src="/extensions/core/js/typography-manager.js"></script>
<script src="/extensions/core/js/udos-controls.js"></script>
```

3. Initialize components:
```javascript
// Initialize typography system
TypographyManager.init();

// Initialize UI controls
UDOSControls.init();
```

## Documentation

See the `docs/` directory for detailed documentation on each component:
- CSS Frameworks Guide
- Grid System Specification
- Typography System Guide
- Theme Development Guide

## Contributing

When adding new components:
1. Place component files in appropriate subdirectories
2. Include documentation in `docs/`
3. Update this README with new component information
4. Follow uDOS coding and style guidelines
