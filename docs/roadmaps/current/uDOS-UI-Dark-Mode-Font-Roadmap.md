# uDOS UI Dark Mode & Font System Roadmap
*Version: 1.0 • Date: 26 August 2025*

This roadmap outlines the implementation of comprehensive dark mode support and advanced font management for the uDOS browser UI system, integrating with the existing 8-theme color palette and 16-font redistributable pack.

---

## 🎯 Goals
- Implement **seamless dark mode toggle** for all 8 existing color themes
- Create **advanced font selection system** with live preview
- Integrate **micro editor** for markdown editing within browser UI
- Ensure **accessibility compliance** and **cross-platform compatibility**
- Maintain **uCORE command mode** integration with **ASCII block output**

---

## 🌓 Dark Mode Implementation

### Phase 1: Theme System Enhancement
- [ ] **Dark Variants**: Create dark mode variants for all 8 themes
  - [ ] Polaroid Dark (high-contrast monochrome)
  - [ ] Retro Unicorn Dark (vivid neon on black)
  - [ ] Nostalgia Dark (muted earth tones)
  - [ ] Tropical Sunrise Dark (warm sunset palette)
  - [ ] Pastel Power Dark (soft dark pastels)
  - [ ] Arcade Pastels Dark (retro gaming dark)
  - [ ] Grayscale Dark (true dark monochrome)
  - [ ] Solar Punk Dark (eco-tech dark mode)

### Phase 2: UI Controls
- [ ] **Theme Picker Component**: Dropdown with live preview
- [ ] **Dark Mode Toggle**: System-aware automatic switching
- [ ] **Persistence**: Save user preferences to uMEMORY
- [ ] **CSS Variable System**: Seamless light/dark transitions

### Phase 3: Component Updates
- [ ] **Terminal Display**: Dark mode terminal themes
- [ ] **Grid System**: Dark-optimized ASCII block characters
- [ ] **Dashboard Panels**: Dark background adaptations
- [ ] **Map Visualization**: Dark-friendly color schemes

---

## 🔤 Font System Enhancement

### Phase 1: Font Loader Integration
- [ ] **Dynamic Font Loading**: Load 16-font pack via CSS
- [ ] **Font Fallback System**: OS-specific monospace fallbacks
- [ ] **Font Aliases**: Map semantic names to TTF files
- [ ] **Performance Optimization**: Lazy loading and caching

### Phase 2: Font Selection UI
- [ ] **Font Picker Component**: Live preview with sample text
- [ ] **Category Filtering**: Screen, Terminal, Display, Retro categories
- [ ] **Size Controls**: Dynamic font size adjustment
- [ ] **Letter Spacing**: Configurable for pixel fonts

### Phase 3: Advanced Features
- [ ] **Font Pairing**: Automatic complementary font suggestions
- [ ] **ASCII Test Renderer**: Box-drawing character validation
- [ ] **Grid Compatibility**: Ensure proper monospace alignment
- [ ] **Export Settings**: Save font configurations

---

## 📝 Micro Editor Integration

### Phase 1: Extension Development
- [ ] **Micro Editor Extension**: Create `extensions/core/editors/micro-editor`
- [ ] **Installation Script**: Auto-download and install micro binary
- [ ] **Command Integration**: `[EDIT] <filename>` uCODE command
- [ ] **Platform Detection**: macOS, Linux, Windows compatibility

### Phase 2: Browser UI Integration
- [ ] **Editor Tab**: Dedicated markdown editor within browser UI
- [ ] **File Browser**: Navigate and open files from uMEMORY/sandbox
- [ ] **Syntax Highlighting**: Markdown, bash, JSON support
- [ ] **Live Preview**: Side-by-side markdown rendering

### Phase 3: Advanced Features
- [ ] **uCODE Syntax**: Custom syntax highlighting for uDOS commands
- [ ] **Template Integration**: Quick access to uDOS templates
- [ ] **Auto-Save**: Periodic saves to sandbox/documents
- [ ] **Version Control**: Git integration for documentation

---

## 🏗️ Implementation Architecture

### CSS Theme System
```css
/* Dark Mode Variables */
[data-theme="polaroid"][data-mode="dark"] {
    --bg-primary: #121212;
    --bg-secondary: #1E1E1E;
    --text-primary: #FFFFFF;
    --text-secondary: #CCCCCC;
    /* Maintain accent colors with dark backgrounds */
}
```

### Font Management System
```json
{
    "fontCategories": {
        "screen": ["IBM Plex Mono", "Hack", "Ubuntu Mono"],
        "terminal": ["VT323", "Space Mono", "C64 Pro Mono"],
        "display": ["Press Start 2P", "Major Mono Display"],
        "utility": ["Share Tech Mono", "DejaVu Sans Mono"]
    },
    "fontSettings": {
        "defaultCategory": "screen",
        "fallbackStack": ["monospace"],
        "allowUserFonts": true
    }
}
```

### Micro Editor Command Structure
```bash
# uCORE command integration
[EDIT] <file.md>           # Open file in micro editor
[EDIT|NEW] <filename>      # Create new file and open
[EDIT|BROWSER]             # Open browser-based editor
[EDIT|CONFIG]              # Configure editor settings
```

---

## 📱 Browser UI Components

### Dark Mode Toggle Component
```javascript
class DarkModeToggle {
    constructor() {
        this.initSystemPreference();
        this.bindEvents();
    }

    toggle() {
        const currentMode = document.documentElement.dataset.mode;
        const newMode = currentMode === 'dark' ? 'light' : 'dark';
        this.setMode(newMode);
        this.savePreference(newMode);
    }
}
```

### Font Selector Component
```javascript
class FontSelector {
    constructor() {
        this.loadFontList();
        this.initPreview();
    }

    renderFontCard(font) {
        return `
            <div class="font-card" data-font="${font.file}">
                <h3 style="font-family: '${font.name}'">${font.name}</h3>
                <p class="sample">uDOS █▒░ 123 ABC</p>
                <span class="category">${font.category}</span>
            </div>
        `;
    }
}
```

---

## 🧪 Testing Matrix

### Dark Mode Testing
- [ ] **Theme Consistency**: All 8 themes work in dark mode
- [ ] **Contrast Ratios**: WCAG AA compliance for accessibility
- [ ] **System Integration**: Respects OS dark mode preferences
- [ ] **Component Coverage**: All UI elements adapt properly

### Font System Testing
- [ ] **Cross-Platform**: Fonts render correctly on macOS/Linux/Windows
- [ ] **ASCII Characters**: Box-drawing and block characters display properly
- [ ] **Grid Alignment**: Monospace alignment maintained
- [ ] **Performance**: Font loading doesn't impact UI responsiveness

### Micro Editor Testing
- [ ] **Installation**: Auto-installer works on all platforms
- [ ] **File Operations**: Create, edit, save, delete functionality
- [ ] **Syntax Highlighting**: Markdown and uCODE highlighting
- [ ] **Integration**: Commands work from uCORE and browser UI

---

## 🔄 Migration Strategy

### Phase 1: Foundation (Week 1)
1. Extend existing theme system with dark mode variants
2. Create font management infrastructure
3. Develop micro editor extension framework

### Phase 2: Integration (Week 2)
1. Implement browser UI controls for themes and fonts
2. Add micro editor to extension registry
3. Create command handlers in uCORE

### Phase 3: Polish (Week 3)
1. Advanced features and accessibility improvements
2. Performance optimization and caching
3. Documentation and user guides

---

## 📚 Documentation Requirements

### User Documentation
- [ ] **Theme Guide**: How to switch themes and enable dark mode
- [ ] **Font Guide**: Font selection and customization
- [ ] **Editor Guide**: Using micro editor for markdown files
- [ ] **Accessibility Guide**: Dark mode and font size for accessibility

### Developer Documentation
- [ ] **Theme API**: Creating custom themes and dark mode variants
- [ ] **Font Integration**: Adding new fonts to the system
- [ ] **Editor Extensions**: Extending micro editor functionality
- [ ] **Component Guide**: Using dark mode and font components

---

## 🎯 Success Metrics

### User Experience
- **Theme Switching**: < 200ms transition between light/dark modes
- **Font Loading**: < 1s to load and apply new fonts
- **Editor Launch**: < 500ms to open micro editor
- **Accessibility**: WCAG AA compliance for all themes

### Technical Performance
- **Bundle Size**: < 2MB total for font pack
- **Memory Usage**: < 50MB additional for font system
- **CSS Variables**: Consistent theming across all components
- **Platform Support**: 100% compatibility across target platforms

---

## 📝 Changelog
- **1.0 (26-Aug-2025)**: Initial roadmap created for dark mode, font system, and micro editor integration

---

## 🔗 Related Roadmaps
- [uDOS Font Roadmap](./uDOS-Font-Roadmap.md) - 16-font redistributable pack
- [uDOS Interface Layer Roadmap](./uDOS-Interface-Layer-Roadmap.md) - Browser UI architecture
- [uDOS Extension System Roadmap](./uDOS-Extension-System-Roadmap.md) - Extension framework
