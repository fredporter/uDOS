# uDOS Display Template Index

**Version**: v1.0.4.1
**Purpose**: Index of all uGRID display templates and components
**Integration**: Font registry, STYLE-GUIDE.md, GRID-DISPLAY.md

---

## 📁 Template Structure

```
uMEMORY/system/templates/display/
├── README.md                        # This index file
├── uDISPLAY-base-layout.md          # Core 16×16 uCELL system
├── uDISPLAY-terminal-interface.md   # VT323 terminal displays
├── uDISPLAY-retro-pixel.md          # 8-bit gaming and pixel art
└── uDISPLAY-web-interface.md        # Modern web responsive layouts
```

---

## 🎯 Template Categories

### 🔲 Base Layout System
**File**: `uDISPLAY-base-layout.md`
**Purpose**: Foundation uCELL and uTILE architecture
**Fonts**: All font stacks from registry
**Features**:
- 16×16 uCELL specifications
- 4× resolution system (64×64 effective)
- Text box configurations (12×12, 14×14, 10×10, 16×16)
- uCELL state management (active, inactive, disabled, hidden, overlay)
- CSS Grid integration
- Color palette integration

### 🖥️ Terminal Interface
**File**: `uDISPLAY-terminal-interface.md`
**Purpose**: Authentic terminal display with VT323 font
**Primary Fonts**: VT323, Ubuntu Mono, DejaVu Sans Mono
**Features**:
- 80×24 standard terminal layouts
- ANSI color support
- ASCII art integration
- Cursor animations and typing effects
- CRT screen effects with scanlines
- Responsive terminal sizing
- Retro phosphor glow effects

### 🕹️ Retro Pixel Display
**File**: `uDISPLAY-retro-pixel.md`
**Purpose**: 8-bit gaming and pixel art aesthetics
**Primary Fonts**: Press Start 2P, Silkscreen, C64 Pro Mono
**Features**:
- Pixel-perfect rendering
- Classic gaming color palettes (Arcade, C64, Game Boy, NES)
- Sprite grid systems (8×8, 16×16, 32×32)
- Gaming UI components (health bars, score displays, dialogue boxes)
- Retro effects (scanlines, chromatic aberration, pixel shimmer)
- Menu systems and status windows

### 🌐 Web Interface
**File**: `uDISPLAY-web-interface.md`
**Purpose**: Modern responsive web layouts
**Primary Fonts**: IBM Plex Mono, Roboto Mono, Space Mono
**Features**:
- Responsive grid layouts (desktop, tablet, mobile)
- Modern color themes (light, dark, high contrast, uDOS branded)
- Component templates (headers, cards, tables)
- Interactive elements (buttons, forms, navigation)
- Progressive enhancement
- Touch-friendly interfaces
- Smooth animations

---

## 🎨 Font Integration

### Font Registry Reference
All templates integrate with `/uMEMORY/system/uDATA-font-registry.json`:

#### Primary Pack (Google Fonts)
- **IBM Plex Mono**: Primary monospace, web interfaces
- **VT323**: Terminal and retro displays
- **Space Mono**: Headers and scientific notation
- **Roboto Mono**: General purpose alternative
- **Press Start 2P**: 8-bit gaming style
- **Silkscreen**: Pixel art and bitmap graphics
- **Major Mono Display**: Large display text
- **Share Tech Mono**: Alternative to Roboto Mono

#### Extended Pack
- **Fira Code**: Programming with ligatures
- **Hack**: Code display alternative
- **C64 Pro Mono**: Commodore 64 authentic style
- **DSEG7 Classic**: 7-segment LCD displays

#### System Fallbacks
- **macOS**: Menlo, SF Mono, Monaco
- **Windows**: Consolas, Courier New, Lucida Console
- **Linux**: DejaVu Sans Mono, Liberation Mono, Ubuntu Mono

---

## 🔄 CSS Variable System

### Global Font Variables
```css
:root {
    --font-primary: IBM Plex Mono, Menlo, Consolas, DejaVu Sans Mono, monospace;
    --font-retro: VT323, Press Start 2P, Silkscreen, Courier New, monospace;
    --font-display: Major Mono Display, Space Mono, Impact, monospace;
    --font-code: Fira Code, IBM Plex Mono, Hack, Menlo, Consolas, monospace;
    --font-terminal: VT323, Ubuntu Mono, DejaVu Sans Mono, Courier New, monospace;
    --font-pixel: Silkscreen, Press Start 2P, Courier New, monospace;
    --font-lcd: DSEG7 Classic, Major Mono Display, Courier New, monospace;
    --font-c64: C64 Pro Mono, VT323, Courier New, monospace;
}
```

### Color System Integration
Templates inherit color variables from `/uMEMORY/system/uDATA-colours.json`:
- **Polaroid Palette**: Default high-contrast
- **8 Complete Palettes**: 128 total colors available
- **ANSI Support**: Terminal color compatibility
- **Theme Support**: Light, dark, high contrast variations

---

## 📐 Grid System Standards

### uCELL Specifications
- **Base Size**: 16×16 pixels
- **4× Resolution**: 64×64 effective detail
- **Text Areas**: 12×12 (default), 14×14 (compact), 10×10 (extended), 16×16 (edge-to-edge)
- **State Classes**: active, inactive, disabled, hidden, overlay

### Layout Grids
- **4×4 Grid**: 64×64 total (small widgets)
- **8×8 Grid**: 128×128 total (medium layouts)
- **16×16 Grid**: 256×256 total (full screens)
- **Custom Grids**: Terminal (80×24), Mobile responsive

---

## 🎯 Display Contexts

### Terminal Context
- **Primary Font**: VT323
- **Background**: Black (#000000)
- **Foreground**: Green (#00ff00) or custom
- **Effects**: Scanlines, CRT curvature, phosphor glow
- **Layouts**: 80×24, 40×12, 120×30

### Web Context
- **Primary Font**: IBM Plex Mono
- **Themes**: Light, dark, high contrast
- **Responsive**: Mobile-first progressive enhancement
- **Components**: Cards, tables, forms, navigation

### Retro Context
- **Primary Font**: Press Start 2P or Silkscreen
- **Palettes**: Arcade, C64, Game Boy, NES
- **Effects**: Pixel shimmer, chromatic aberration
- **Components**: Health bars, dialogue boxes, menus

### Desktop Context
- **Primary Font**: IBM Plex Mono
- **Fallbacks**: System fonts (Menlo, SF Mono, Consolas)
- **Layout**: Native grid systems
- **Integration**: OS-specific styling

---

## 🚀 Usage Guidelines

### Template Selection
1. **Base Layout**: Start with `uDISPLAY-base-layout.md` for uCELL foundations
2. **Terminal Apps**: Use `uDISPLAY-terminal-interface.md` for CLI interfaces
3. **Gaming/Retro**: Use `uDISPLAY-retro-pixel.md` for 8-bit aesthetics
4. **Web Apps**: Use `uDISPLAY-web-interface.md` for modern responsive layouts

### Implementation Steps
1. Choose appropriate template based on display context
2. Import CSS variables from font registry
3. Apply base uCELL grid structure
4. Customize colors using palette system
5. Add interactive elements and animations
6. Test across different devices and contexts

### Best Practices
- Always include fallback fonts for cross-platform compatibility
- Use CSS variables for consistent theming
- Implement responsive design for web contexts
- Maintain pixel-perfect rendering for retro contexts
- Test font loading and performance
- Validate accessibility across all themes

---

## 🔧 Integration with uDOS Core

### File Relationships
- **Font Registry**: `/uMEMORY/system/uDATA-font-registry.json`
- **Color System**: `/uMEMORY/system/uDATA-colours.json`
- **Style Guide**: `/docs/STYLE-GUIDE.md`
- **Grid Reference**: `/docs/GRID-DISPLAY.md`
- **Templates**: `/uMEMORY/system/templates/display/`

### Command Integration
Templates work with uCORE commands:
- `get template uDISPLAY-base-layout.md` - Retrieve template
- `template process display-config.json` - Process with variables
- `post template generated-layout.css` - Save processed output

### Role-Based Access
Templates respect 8-role hierarchy:
- **Ghost**: View-only access to templates
- **Tomb**: Basic template usage
- **Crypt+**: Full template modification and creation
- **Wizard**: Core template system development

---

*uDOS v1.0.4.1 Display Template Index*
*Complete guide to uGRID display system templates and font integration*
