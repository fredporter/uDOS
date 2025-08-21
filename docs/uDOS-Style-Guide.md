# uDOS Style Guide v1.3

## Professional Color Palette

### Core Colors
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

### Neutral Colors
```css
--udos-black: #000000      /* Pure Black */
--udos-white: #ffffff      /* Pure White */
--udos-grey: #808080       /* Medium Grey */
--udos-light-grey: #c0c0c0 /* Light Grey */
--udos-dark-grey: #404040  /* Dark Grey */
```

## ANSI Terminal Codes

### Professional Palette ANSI Codes
```bash
# Professional palette using 24-bit color codes
RED='\033[38;2;206;74;74m'      # Muted Red
GREEN='\033[38;2;72;165;106m'   # Forest Green
BLUE='\033[38;2;102;136;195m'   # Steel Blue
YELLOW='\033[38;2;234;175;65m'  # Golden Yellow
PURPLE='\033[38;2;178;93;166m'  # Soft Purple
CYAN='\033[38;2;74;159;184m'    # Professional Cyan
NC='\033[0m'                    # No Color (reset)
BOLD='\033[1m'                  # Bold text
```

## Usage Guidelines

### Primary Usage
- **Forest Green (#48a56a)**: Primary text, success messages, main interface elements
- **Steel Blue (#6688c3)**: Secondary text, information, headers
- **Golden Yellow (#eaaf41)**: Highlights, warnings, accent elements
- **Soft Purple (#b25da6)**: Special elements, user prompts, distinctive features
- **Muted Red (#ce4a4a)**: Errors, alerts, critical information

### Typography

#### Fonts
- **Default**: Courier Prime - Clean, readable terminal font
- **Terminal**: Source Code Pro - Modern programming font
- **BBS/ANSI**: Share Tech Mono - Retro computing feel
- **C64**: Courier Prime - Classic computing style
- **Acorn**: Cutive Mono - Typewriter aesthetic
- **Display**: Major Mono Display - Large display terminal

#### Font Stack Priority
```css
font-family: 'Courier Prime', 'Courier New', 'Monaco', monospace;
```

## Interface Elements

### Backgrounds
- **Dark Theme**: #001122 (Primary), #000a11 (Secondary)
- **Light Theme**: #f0f0f0 (Primary), #e0e0e0 (Secondary)

### Borders and Lines
- **Primary Border**: Forest Green (#48a56a)
- **Secondary Border**: Professional Cyan (#4a9fb8)

### Status Indicators
- **Connected**: Forest Green (#48a56a)
- **Disconnected**: Muted Red (#ce4a4a)
- **Warning**: Golden Yellow (#eaaf41)
- **Information**: Steel Blue (#6688c3)

## Rainbow Gradients

### Header Rainbow Sequence
```css
background: linear-gradient(90deg,
    #ce4a4a 0%,     /* Muted Red */
    #d87538 14%,    /* Orange */
    #eaaf41 28%,    /* Golden Yellow */
    #48a56a 42%,    /* Forest Green */
    #4a9fb8 57%,    /* Professional Cyan */
    #6688c3 71%,    /* Steel Blue */
    #b25da6 85%,    /* Soft Purple */
    #b25da6 100%    /* Soft Purple */
);
```

## Typography

### Authentic Retro Computing Fonts
```css
/* Core retro computing fonts - VT323 for authentic BBC Micro */
--font-default: 'VT323', 'Monaco', 'Courier New', monospace;            /* Default: Authentic BBC Micro */
--font-acorn: 'VT323', 'Monaco', 'Courier New', monospace;              /* BBC Micro/Acorn (VT323 - Authentic!) */
--font-c64: 'Nova Mono', 'Monaco', 'Courier New', monospace;            /* Commodore 64 (PETSCII-style) */
--font-terminal: 'Source Code Pro', 'Monaco', 'Courier New', monospace; /* Modern Terminal */
```

### Authentic C64 Font Option
For the most authentic Commodore 64 experience, download **Pet Me 64** from [Kreative Korp](https://www.kreativekorp.com/software/fonts/c64/). This is the definitive Commodore 64 font with complete PETSCII character support and authentic pixel-perfect reproduction of the original character generator ROM.

### Content & Support Fonts
```css
/* Fonts for content and UI elements */
--font-markdown: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
--font-code: 'JetBrains Mono', 'Source Code Pro', 'Cutive Mono', monospace;
--font-emoji: 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;
```

### Font Characteristics
- **VT323**: Based on DEC VT320 terminal and BBC Micro MODE 7 teletext
- **Share Tech Mono**: Clean, modern interpretation of C64 character set
- **Source Code Pro**: Contemporary terminal font for modern development

### Default Theme
- **Default Mode**: Dark theme with professional color palette  
- **Default Font**: BBC Micro VT323 (authentic teletext/MODE 7 style)
- **Font Order**: BBC Micro → C64 → Terminal → (cycle repeats)
- **Emoji Support**: Full Unicode emoji support in all fonts

## Best Practices

### Accessibility
- Maintain sufficient contrast ratios (4.5:1 minimum)
- Use color coding with additional visual indicators
- Provide theme switching options

### Consistency
- Use the defined color variables throughout all components
- Maintain consistent font stacks across interfaces
- Apply consistent spacing and sizing

### Professional Appearance
- Prefer muted tones over bright neon colors
- Use subtle shadows and effects
- Maintain clean, uncluttered layouts

## Implementation Files

### Web Interface
- `/uCORE/launcher/universal/ucode-ui/static/style.css`
- `/uCORE/launcher/universal/ucode-ui/static/fonts.css`

### Terminal Scripts
- `/uSCRIPT/library/ucode/ascii.sh`
- All core uDOS command scripts

### Documentation
- This style guide: `/docs/uDOS-Style-Guide.md`

---

*uDOS Style Guide v1.3 - Professional Color Palette*
*Last Updated: August 21, 2025*
