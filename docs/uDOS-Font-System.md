# uDOS Font System Documentation

## 🎨 Font Overview

uDOS uses a carefully curated font system designed for optimal development experience, retro aesthetics, and modern usability.

### 📚 Font Stack Architecture

```
Primary Stack: JetBrains Mono → Monaco → Menlo → Consolas → monospace
Terminal Stack: VT323 → Share Tech Mono → Courier New → monospace  
Display Stack: Orbitron → Arial → sans-serif
Retro Stack: Space Mono → Nova Mono → monospace
System Stack: -apple-system → BlinkMacSystemFont → Segoe UI → system-ui
```

## 🌐 Web Fonts (Google Fonts Integration)

### Core Development Fonts
- **JetBrains Mono** - Modern development font with ligatures
- **VT323** - Authentic retro terminal aesthetic  
- **Share Tech Mono** - Futuristic tech appearance
- **Orbitron** - Sci-fi display headers
- **Space Mono** - Vintage computing feel
- **Nova Mono** - Clean, minimal monospace

### Font Loading
```css
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
```

## 🎯 Font Usage in uDOS

### Command Interface
```bash
fonts                    # Show font information
font primary            # Switch to JetBrains Mono
font terminal           # Switch to VT323 retro
font display            # Switch to Orbitron headers
font retro              # Switch to Space Mono vintage
font effects            # Toggle neon/glow effects
font reset              # Reset to default
```

### CSS Classes
```css
.font-primary    { font-family: var(--font-primary); }
.font-terminal   { font-family: var(--font-terminal); }
.font-display    { font-family: var(--font-display); }
.font-retro      { font-family: var(--font-retro); }
.font-system     { font-family: var(--font-system); }
```

## ✨ Special Effects

### Glow Effects
```css
.font-glow       { text-shadow: 0 0 10px currentColor; }
.font-neon       { text-shadow: 0 0 5px currentColor, 0 0 10px currentColor, 0 0 20px currentColor; }
.font-retro-glow { text-shadow: 0 0 2px #00ff88, 0 0 4px #00ff88, 0 0 8px #00ff88; }
```

### Rainbow Text
```css
.font-rainbow {
    background: linear-gradient(45deg, #ff0088, #8800ff, #0088ff, #00ff88, #ffff00, #ff8800);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: fontRainbow 3s ease-in-out infinite;
}
```

## 🔧 Font Management Scripts

### Available Scripts
- `demo-fonts` - Display font demonstration
- `install-retro-fonts` - Install retro font collection
- `font-troubleshoot` - Diagnose font issues

### Usage Examples
```bash
# Show font demo
./uCORE/bin/demo-fonts

# Install fonts
./uCORE/bin/install-retro-fonts

# Troubleshoot issues
./uCORE/bin/font-troubleshoot
```

## 🎨 ASCII Art Integration

### ASCII Font Styling
```css
.ascii-art    { font-family: 'VT323', monospace; line-height: 0.8; }
.ascii-banner { font-family: 'Share Tech Mono', monospace; line-height: 1; }
.ascii-block  { font-family: 'JetBrains Mono', monospace; line-height: 1; }
```

### Character Sets
```
Block Graphics: ░▒▓█▄▀■□▲►◄▼
Box Drawing: ═══╔╗╚╝║─│┌┐└┘
Special: ••• ▓▓▓ ░░░ ▒▒▒ ████
```

## 🌈 Dynamic Font Switching

The uDOS interface supports real-time font switching through:

1. **Command Interface** - Type font commands
2. **Font Panel Controls** - Click buttons to cycle
3. **JavaScript API** - Programmatic control
4. **CSS Variables** - Theme-based switching

### JavaScript Control
```javascript
// Change font
window.udos.changeFont('terminal');

// Toggle effects
window.udos.toggleFontEffects();

// Cycle through fonts
cycleFont();
```

## 🔍 Font Fallback Strategy

1. **Web Fonts** - Primary choice (Google Fonts)
2. **System Fonts** - macOS/Windows/Linux defaults
3. **Generic Families** - monospace, sans-serif
4. **Graceful Degradation** - Always readable

## 🎮 Gaming & Retro Aesthetics

uDOS fonts are specifically chosen to evoke:
- **80s Terminal Computing** (VT323)
- **Sci-Fi Interfaces** (Orbitron)
- **Modern Development** (JetBrains Mono)
- **Vintage Gaming** (Space Mono)

## 📱 Cross-Platform Support

### macOS
- Native Monaco/Menlo support
- Font Book integration
- Retina display optimization

### Windows
- Consolas fallbacks
- ClearType rendering
- High-DPI scaling

### Linux
- DejaVu Sans Mono
- Fontconfig integration
- X11/Wayland support

## 🎯 Performance Optimization

- **Subset Loading** - Only required characters
- **Font Display Swap** - Immediate text rendering
- **Preload Hints** - Faster loading
- **Local Fallbacks** - No network dependency

---

*uDOS Font System v1.3 - Universal Development Operating System*
