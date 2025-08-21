# uDOS Style Guide v1.3 - BBC Mode 7 Edition

## BBC Mode 7 Authentic Design

### Inspired by BBC BASIC Manual
Following the design principles from [BBC BASIC for Windows Manual](https://www.bbcbasic.co.uk/bbcwin/manual/bbcwinh.html), uDOS implements authentic Mode 7 teletext graphics with chunky block UI elements.

### BBC Mode 7 Color Palette (New Vibrant Scheme)
```css
/* New uDOS Vibrant Color Palette */
--color-red: #ef4136        /* Vibrant Red (239,65,54) */
--color-orange: #f7941d     /* Vibrant Orange (247,148,29) */
--color-amber: #fbb040      /* Vibrant Amber (251,176,64) */
--color-yellow: #f9ed32     /* Vibrant Yellow (249,237,50) */
--color-blue: #00aeef       /* Vibrant Blue (0,174,239) */
--color-lime: #e9ff39       /* Vibrant Lime (233,255,57) */
--color-green: #8cff1f      /* Vibrant Green (140,255,31) */
--color-cyan: #00c6cc       /* Vibrant Cyan (0,198,204) */
--color-pink: #f08ed3       /* Vibrant Pink (240,142,211) */

/* Dark/Grey/Light variants for styling */
--color-black: #000000      /* Pure Black */
--color-dark-grey: #1a1a1a  /* Very Dark Grey */
--color-grey: #333333       /* Dark Grey */
--color-mid-grey: #666666   /* Medium Grey */
--color-light-grey: #999999 /* Light Grey */
--color-pale-grey: #cccccc  /* Pale Grey */
--color-white: #ffffff      /* Pure White */
```

### Mode 7 Display Characteristics
- **Resolution**: 40×25 characters (320×200 pixels effective)
- **Font**: MODE7GX3 (authentic BBC Micro teletext)
- **Character Size**: 16×20 pixels per character
- **Block Graphics**: SAA5050 standard block characters
- **Background**: Text backgrounds using color codes

## Chunky Block Graphics Buttons

### Button Design Philosophy
Based on BBC Mode 7 teletext graphics using solid block characters (█) for button backgrounds:

```html
<!-- BBC Mode 7 Button Structure -->
<button class="mode7-button">
    ▌█ BUTTON TEXT █▐<br>
    DESCRIPTION
</button>
```

### Button Color Variations
```css
.mode7-button         /* Green (default) */
.mode7-btn-blue       /* Blue for system functions */
.mode7-btn-red        /* Red for admin/critical */
.mode7-btn-magenta    /* Magenta for special functions */
.mode7-btn-cyan       /* Cyan for utilities */
```

### Block Character Set
- `█` - Full block (U+2588)
- `▌` - Left half block (U+258C) 
- `▐` - Right half block (U+2590)
- `▀` - Upper half block (U+2580)
- `▄` - Lower half block (U+2584)

## uDOS Professional Color Palette (Secondary)

### Core Colors (for modern elements)
```css
/* uDOS Professional Color Palette */
--udos-red: #ce4a4a        /* Muted Red - RGB(206,74,74) */
--udos-green: #48a56a      /* Forest Green - RGB(72,165,106) */
--udos-blue: #6688c3       /* Steel Blue - RGB(102,136,195) */
--udos-yellow: #eaaf41     /* Golden Yellow - RGB(234,175,65) */
--udos-purple: #b25da6     /* Soft Purple - RGB(178,93,166) */
--udos-cyan: #4a9fb8       /* Professional Cyan - RGB(74,159,184) */
--udos-orange: #d87538     /* Warm Orange - RGB(216,117,56) */
```

## UI Dashboard Integration

### Main Dashboard Grid
Based on BBC Mode 7 40×25 character layout:
- **3×3 Grid**: Primary module buttons
- **Center Layout**: 640×500 pixel viewport
- **Block Buttons**: Chunky teletext-style buttons

### Dashboard Categories
1. **uDOS Core Modules**
   - uCORE (System Core) - Green
   - uSERVER (Web Services) - Blue  
   - uSCRIPT (Automation) - Magenta

2. **User Modes**
   - WIZARD (Development) - Cyan
   - SORCERER (Admin Tools) - Red
   - IMP (Scripting) - Green

3. **Special Functions**
   - uKNOWLEDGE (Docs & Help) - Blue
   - TEMPLATES (Generators) - Magenta
   - TERMINAL (Command Line) - Cyan

### Template System Integration
```javascript
// Template system commands
openTemplates()           // Load template browser
template create [name]    // Create new template
template list            // List available templates
template apply [name]    // Apply template to project
```

### Documentation Integration
Links to comprehensive user manual following BBC BASIC manual structure:
- Command reference
- Function library
- Programming examples
- System integration guides

## Typography

### Authentic BBC Mode 7 Fonts
```css
/* Primary: Authentic MODE7GX teletext fonts */
--font-mode7gx3: 'MODE7GX3', monospace;     /* Standard teletext */
--font-mode7gx0: 'MODE7GX0', monospace;     /* Square aspect */
--font-mode7gx2: 'MODE7GX2', monospace;     /* Alternative */
--font-mode7gx4: 'MODE7GX4', monospace;     /* Wide aspect */
```

### Font Loading
```css
@font-face {
    font-family: 'MODE7GX3';
    src: url('/static/fonts/MODE7GX3.TTF') format('truetype'),
         url('/static/fonts/MODE7GX3.EOT') format('embedded-opentype');
}
```

## Interface Elements

### Mode 7 Screen Layout
- **Header Bar**: Double-height colorized title
- **Dashboard Grid**: 3×3 button matrix
- **Terminal Window**: Scrolling command output
- **Command Line**: Direct input with authentic prompt
- **Status Bar**: System information footer

### Visual Effects
- **Flashing Text**: CSS animation for attention
- **Color Backgrounds**: Text with Mode 7 background colors
- **Block Graphics**: Authentic teletext block characters

### Accessibility
- High contrast Mode 7 colors
- Clear button states
- Keyboard navigation support
- Screen reader compatible

## Best Practices

### Authentic Mode 7 Design
- Use only SAA5050 standard colors
- Employ block graphics for UI elements  
- Maintain 40×25 character grid layout
- Implement flashing text sparingly

### Button Design
- Use solid block backgrounds (█)
- Clear text labels with descriptions
- Color coding for function categories
- Hover states with color changes

### Modern Integration
- Responsive design for various screens
- Touch-friendly button sizes
- Smooth CSS transitions
- Progressive enhancement

## Implementation Files

### Core Interface
- `/uCORE/launcher/universal/ucode-ui/index.html` - Main Mode 7 interface
- `/uCORE/launcher/universal/ucode-ui/static/style.css` - Mode 7 styling
- `/uCORE/launcher/universal/ucode-ui/static/fonts/` - MODE7GX font files

### Documentation
- `/docs/uDOS-Style-Guide.md` - This style guide
- `/docs/user-guides/` - User manuals in BBC BASIC style

---

*uDOS Style Guide v1.3 - BBC Mode 7 Edition*  
*Inspired by BBC BASIC for Windows Manual*  
*Last Updated: August 21, 2025*
