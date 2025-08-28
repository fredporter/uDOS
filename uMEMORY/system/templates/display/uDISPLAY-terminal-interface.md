# uGRID Terminal Display Template

**Template**: uDISPLAY-terminal-interface.md
**Version**: v1.0.4.1
**Purpose**: Terminal-specific display layouts and formatting
**Integration**: VT323 font, ANSI colors, retro aesthetics

---

## 🖥️ Terminal Display Architecture

### Terminal Context Configuration
```css
.display-terminal {
    font-family: var(--font-terminal);
    background: #000000;
    color: #00ff00;
    font-size: 14px;
    line-height: 18px;
    letter-spacing: 0.5px;
    -webkit-font-smoothing: none;
    font-smooth: never;
}
```

### VT323 Font Specifications
- **Primary**: VT323 (Google Fonts OFL)
- **Fallback**: Ubuntu Mono, DejaVu Sans Mono, Courier New
- **Size**: 14px terminal, 16px display
- **Weight**: 400 (normal)
- **Smoothing**: Disabled for authentic pixelated look

---

## 🎨 Terminal Color Schemes

### Classic Green Terminal
```css
.terminal-green {
    background: #000000;
    color: #00ff00;
    border: 2px solid #003300;
}

.terminal-green .cursor {
    background: #00ff00;
    animation: blink 1s infinite;
}
```

### Amber Terminal
```css
.terminal-amber {
    background: #000000;
    color: #ffb000;
    border: 2px solid #332200;
}
```

### Classic White on Black
```css
.terminal-classic {
    background: #000000;
    color: #ffffff;
    border: 2px solid #333333;
}
```

### Modern Dark
```css
.terminal-modern {
    background: #1e1e1e;
    color: #d4d4d4;
    border: 2px solid #404040;
}
```

---

## 📐 Terminal Grid Layouts

### 80×24 Standard Terminal
```html
<div class="ugrid terminal-80x24 display-terminal terminal-green">
    <div class="terminal-header">
        uDOS v1.0.4.1 - Terminal Mode
    </div>
    <div class="terminal-content">
        <!-- 80 characters × 24 rows -->
    </div>
    <div class="terminal-status">
        Ghost@uDOS:~/$ _
    </div>
</div>
```

```css
.terminal-80x24 {
    width: 80ch;
    height: 24em;
    display: grid;
    grid-template-rows: auto 1fr auto;
    padding: 8px;
    border: 2px solid #333;
}
```

### Compact Terminal (40×12)
```css
.terminal-40x12 {
    width: 40ch;
    height: 12em;
    font-size: 12px;
    line-height: 16px;
}
```

### Wide Terminal (120×30)
```css
.terminal-120x30 {
    width: 120ch;
    height: 30em;
    font-size: 13px;
    line-height: 17px;
}
```

---

## 🌈 ANSI Color Support

### Standard ANSI Colors
```css
.terminal-ansi {
    --ansi-black: #000000;
    --ansi-red: #ff0000;
    --ansi-green: #00ff00;
    --ansi-yellow: #ffff00;
    --ansi-blue: #0000ff;
    --ansi-magenta: #ff00ff;
    --ansi-cyan: #00ffff;
    --ansi-white: #ffffff;

    /* Bright variants */
    --ansi-bright-black: #808080;
    --ansi-bright-red: #ff8080;
    --ansi-bright-green: #80ff80;
    --ansi-bright-yellow: #ffff80;
    --ansi-bright-blue: #8080ff;
    --ansi-bright-magenta: #ff80ff;
    --ansi-bright-cyan: #80ffff;
    --ansi-bright-white: #ffffff;
}
```

### Color Classes
```css
.ansi-0 { color: var(--ansi-black); }
.ansi-1 { color: var(--ansi-red); }
.ansi-2 { color: var(--ansi-green); }
.ansi-3 { color: var(--ansi-yellow); }
.ansi-4 { color: var(--ansi-blue); }
.ansi-5 { color: var(--ansi-magenta); }
.ansi-6 { color: var(--ansi-cyan); }
.ansi-7 { color: var(--ansi-white); }

/* Background colors */
.ansi-bg-0 { background: var(--ansi-black); }
.ansi-bg-1 { background: var(--ansi-red); }
/* etc... */
```

---

## 🔤 ASCII Art Integration

### ASCII Box Drawing
```css
.ascii-box {
    font-family: var(--font-terminal);
    line-height: 1;
    white-space: pre;
}
```

### Standard Box Characters
```
┌─┬─┐  ╔═╦═╗  ┏━┳━┓
├─┼─┤  ╠═╬═╣  ┣━╋━┫
└─┴─┘  ╚═╩═╝  ┗━┻━┛
```

### Block Characters
```
█ ▀ ▄ ▌ ▐ ░ ▒ ▓
```

### uDOS Banner Integration
```html
<div class="terminal-banner">
<pre class="ascii-art">
██╗   ██╗██████╗  ██████╗ ███████╗
██║   ██║██╔══██╗██╔═══██╗██╔════╝
██║   ██║██║  ██║██║   ██║███████╗
██║   ██║██║  ██║██║   ██║╚════██║
╚██████╔╝██████╔╝╚██████╔╝███████║
 ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
</pre>
</div>
```

---

## ⚡ Interactive Elements

### Cursor Animation
```css
@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}

.cursor {
    background: currentColor;
    color: inherit;
    animation: blink 1s infinite;
    width: 1ch;
    height: 1em;
    display: inline-block;
}
```

### Typing Effect
```css
@keyframes typing {
    from { width: 0; }
    to { width: 100%; }
}

.typing-text {
    width: 0;
    overflow: hidden;
    white-space: nowrap;
    border-right: 2px solid;
    animation: typing 2s steps(40, end);
}
```

### Scrolling Text
```css
.terminal-scroll {
    overflow-y: scroll;
    scrollbar-width: thin;
    scrollbar-color: #333 #000;
}

.terminal-scroll::-webkit-scrollbar {
    width: 8px;
}

.terminal-scroll::-webkit-scrollbar-track {
    background: #000;
}

.terminal-scroll::-webkit-scrollbar-thumb {
    background: #333;
    border-radius: 4px;
}
```

---

## 🎯 Component Templates

### Command Prompt
```html
<div class="terminal-prompt">
    <span class="prompt-user ansi-2">Ghost</span>
    <span class="prompt-separator ansi-7">@</span>
    <span class="prompt-host ansi-6">uDOS</span>
    <span class="prompt-separator ansi-7">:</span>
    <span class="prompt-path ansi-4">~/sandbox</span>
    <span class="prompt-symbol ansi-7">$ </span>
    <span class="cursor"></span>
</div>
```

### Status Line
```html
<div class="terminal-status">
    <span class="status-left">
        uDOS v1.0.4.1 | Role: Ghost | Mode: Terminal
    </span>
    <span class="status-right">
        2025-08-26 02:30:45 UTC
    </span>
</div>
```

### Progress Bar
```html
<div class="terminal-progress">
    <span class="progress-label">Loading: </span>
    <span class="progress-bar">
        [████████████████████████████████████████] 100%
    </span>
</div>
```

---

## 📱 Responsive Terminal

### Mobile Terminal (20×10)
```css
@media (max-width: 480px) {
    .terminal-responsive {
        width: 20ch;
        height: 10em;
        font-size: 10px;
        line-height: 12px;
    }
}
```

### Tablet Terminal (60×20)
```css
@media (min-width: 481px) and (max-width: 768px) {
    .terminal-responsive {
        width: 60ch;
        height: 20em;
        font-size: 12px;
        line-height: 15px;
    }
}
```

### Desktop Terminal (80×24)
```css
@media (min-width: 769px) {
    .terminal-responsive {
        width: 80ch;
        height: 24em;
        font-size: 14px;
        line-height: 18px;
    }
}
```

---

## 🎨 Retro Effects

### CRT Screen Effect
```css
.terminal-crt {
    position: relative;
    overflow: hidden;
}

.terminal-crt::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
        transparent 50%,
        rgba(0, 255, 0, 0.03) 50%
    );
    background-size: 100% 4px;
    pointer-events: none;
}

.terminal-crt::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(
        ellipse at center,
        transparent 0%,
        rgba(0, 0, 0, 0.1) 100%
    );
    pointer-events: none;
}
```

### Phosphor Glow
```css
.terminal-glow {
    text-shadow:
        0 0 5px currentColor,
        0 0 10px currentColor,
        0 0 15px currentColor;
}
```

---

*uDOS v1.0.4.1 Terminal Display Template*
*VT323 font integration with authentic retro terminal aesthetics*
