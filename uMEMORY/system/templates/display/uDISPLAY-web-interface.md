# uGRID Web Display Template

**Template**: uDISPLAY-web-interface.md
**Version**: v1.0.4.1
**Purpose**: Modern web interface layouts and responsive design
**Integration**: IBM Plex Mono, CSS Grid, progressive enhancement

---

## 🌐 Web Display Architecture

### Modern Web Configuration
```css
.display-web {
    font-family: var(--font-primary);
    background: #ffffff;
    color: #333333;
    font-size: 14px;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
```

### Font Specifications

#### IBM Plex Mono (Primary)
```css
.font-primary {
    font-family: 'IBM Plex Mono', 'Menlo', 'Consolas', monospace;
    font-weight: 300; /* Light */
    font-weight: 400; /* Regular */
    font-weight: 500; /* Medium */
    font-weight: 700; /* Bold */
}
```

#### Roboto Mono (Alternative)
```css
.font-secondary {
    font-family: 'Roboto Mono', 'Menlo', 'Consolas', monospace;
    font-size: 14px;
    line-height: 1.5;
}
```

#### Space Mono (Headers)
```css
.font-display {
    font-family: var(--font-display);
    font-weight: 400;
    font-weight: 700;
    letter-spacing: 0.5px;
}
```

---

## 🎨 Modern Color Schemes

### Light Theme (Default)
```css
.theme-light {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-accent: #e9ecef;
    --text-primary: #333333;
    --text-secondary: #6c757d;
    --text-muted: #adb5bd;
    --border-color: #dee2e6;
    --shadow: rgba(0, 0, 0, 0.1);
}
```

### Dark Theme
```css
.theme-dark {
    --bg-primary: #1e1e1e;
    --bg-secondary: #2d2d2d;
    --bg-accent: #404040;
    --text-primary: #ffffff;
    --text-secondary: #cccccc;
    --text-muted: #999999;
    --border-color: #555555;
    --shadow: rgba(0, 0, 0, 0.3);
}
```

### High Contrast
```css
.theme-high-contrast {
    --bg-primary: #000000;
    --bg-secondary: #ffffff;
    --text-primary: #ffffff;
    --text-secondary: #000000;
    --border-color: #ffffff;
    --shadow: none;
}
```

### uDOS Branded
```css
.theme-udos {
    --bg-primary: #f8f9fa;
    --bg-secondary: #ffffff;
    --accent-blue: #2196F3;
    --accent-green: #00E676;
    --accent-red: #FF1744;
    --accent-yellow: #FFEB3B;
    --accent-purple: #E91E63;
    --accent-cyan: #00E5FF;
}
```

---

## 📐 Responsive Grid Layouts

### Desktop Layout (1200px+)
```css
.ugrid-desktop {
    display: grid;
    grid-template-columns: 250px 1fr 300px;
    grid-template-rows: 64px 1fr 48px;
    grid-template-areas:
        "sidebar header actions"
        "sidebar content panel"
        "sidebar footer panel";
    min-height: 100vh;
    gap: 16px;
}
```

### Tablet Layout (768px - 1199px)
```css
@media (min-width: 768px) and (max-width: 1199px) {
    .ugrid-responsive {
        grid-template-columns: 200px 1fr;
        grid-template-rows: 56px 1fr 48px;
        grid-template-areas:
            "sidebar header"
            "sidebar content"
            "sidebar footer";
    }
}
```

### Mobile Layout (320px - 767px)
```css
@media (max-width: 767px) {
    .ugrid-responsive {
        grid-template-columns: 1fr;
        grid-template-rows: 56px 1fr 64px 48px;
        grid-template-areas:
            "header"
            "content"
            "sidebar"
            "footer";
    }
}
```

---

## 🧩 Component Templates

### Navigation Header
```html
<header class="web-header">
    <div class="header-brand">
        <div class="brand-logo">uDOS</div>
        <div class="brand-version">v1.0.4.1</div>
    </div>
    <nav class="header-nav">
        <a href="#dashboard" class="nav-link active">Dashboard</a>
        <a href="#memory" class="nav-link">Memory</a>
        <a href="#scripts" class="nav-link">Scripts</a>
        <a href="#settings" class="nav-link">Settings</a>
    </nav>
    <div class="header-actions">
        <button class="btn btn-primary">Connect</button>
        <div class="user-menu">Ghost</div>
    </div>
</header>
```

```css
.web-header {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    padding: 0 24px;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-color);
    font-family: var(--font-primary);
}

.brand-logo {
    font-family: var(--font-display);
    font-size: 20px;
    font-weight: 700;
    color: var(--accent-blue);
}

.header-nav {
    display: flex;
    justify-content: center;
    gap: 32px;
}

.nav-link {
    text-decoration: none;
    color: var(--text-secondary);
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 4px;
    transition: all 0.2s ease;
}

.nav-link:hover,
.nav-link.active {
    color: var(--accent-blue);
    background: var(--bg-accent);
}
```

### Card Component
```html
<div class="card">
    <div class="card-header">
        <h3 class="card-title">System Status</h3>
        <div class="card-actions">
            <button class="btn btn-icon">⚙️</button>
        </div>
    </div>
    <div class="card-content">
        <div class="status-grid">
            <div class="status-item">
                <div class="status-label">CPU</div>
                <div class="status-value">12%</div>
            </div>
            <div class="status-item">
                <div class="status-label">Memory</div>
                <div class="status-value">45%</div>
            </div>
            <div class="status-item">
                <div class="status-label">Storage</div>
                <div class="status-value">67%</div>
            </div>
        </div>
    </div>
</div>
```

```css
.card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px var(--shadow);
    overflow: hidden;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-secondary);
}

.card-title {
    font-family: var(--font-primary);
    font-size: 16px;
    font-weight: 500;
    margin: 0;
    color: var(--text-primary);
}

.card-content {
    padding: 20px;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 16px;
}

.status-item {
    text-align: center;
}

.status-label {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 4px;
}

.status-value {
    font-family: var(--font-primary);
    font-size: 18px;
    font-weight: 500;
    color: var(--accent-blue);
}
```

### Data Table
```html
<div class="data-table">
    <table class="table">
        <thead>
            <tr>
                <th>Process</th>
                <th>Status</th>
                <th>CPU</th>
                <th>Memory</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="process-name">uCORE</td>
                <td><span class="status-badge status-active">Active</span></td>
                <td class="metric">2.1%</td>
                <td class="metric">12.5MB</td>
                <td>
                    <button class="btn btn-sm">Stop</button>
                    <button class="btn btn-sm">Restart</button>
                </td>
            </tr>
            <!-- More rows... -->
        </tbody>
    </table>
</div>
```

```css
.data-table {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    overflow: hidden;
}

.table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-primary);
    font-size: 13px;
}

.table th {
    background: var(--bg-secondary);
    padding: 12px 16px;
    text-align: left;
    font-weight: 500;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border-color);
}

.table td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
}

.table tr:last-child td {
    border-bottom: none;
}

.table tr:hover {
    background: var(--bg-accent);
}

.status-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 500;
}

.status-active {
    background: #d4edda;
    color: #155724;
}

.process-name {
    font-family: var(--font-code);
    font-weight: 500;
}

.metric {
    font-family: var(--font-code);
    text-align: right;
    color: var(--accent-blue);
}
```

---

## 🎯 Interactive Elements

### Button System
```css
.btn {
    display: inline-flex;
    align-items: center;
    padding: 8px 16px;
    font-family: var(--font-primary);
    font-size: 14px;
    font-weight: 500;
    text-decoration: none;
    border: 1px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.btn:hover {
    background: var(--bg-accent);
    transform: translateY(-1px);
    box-shadow: 0 2px 4px var(--shadow);
}

.btn-primary {
    background: var(--accent-blue);
    color: #ffffff;
}

.btn-primary:hover {
    background: #1976d2;
}

.btn-sm {
    padding: 4px 8px;
    font-size: 12px;
}

.btn-icon {
    padding: 8px;
    border-radius: 4px;
}
```

### Form Elements
```css
.form-group {
    margin-bottom: 16px;
}

.form-label {
    display: block;
    font-family: var(--font-primary);
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 6px;
}

.form-input {
    width: 100%;
    padding: 8px 12px;
    font-family: var(--font-primary);
    font-size: 14px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    transition: border-color 0.2s ease;
}

.form-input:focus {
    outline: none;
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.form-select {
    appearance: none;
    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z" fill="currentColor"/></svg>');
    background-repeat: no-repeat;
    background-position: right 8px center;
    background-size: 16px;
    padding-right: 32px;
}
```

---

## 📱 Progressive Enhancement

### Mobile-First Approach
```css
/* Base styles for mobile */
.ugrid-progressive {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px;
}

/* Tablet enhancement */
@media (min-width: 768px) {
    .ugrid-progressive {
        grid-template-columns: repeat(2, 1fr);
        gap: 24px;
        padding: 24px;
    }
}

/* Desktop enhancement */
@media (min-width: 1200px) {
    .ugrid-progressive {
        grid-template-columns: repeat(3, 1fr);
        gap: 32px;
        padding: 32px;
    }
}
```

### Touch-Friendly Interfaces
```css
.touch-friendly {
    min-height: 44px;
    min-width: 44px;
    padding: 12px;
}

@media (hover: hover) {
    .touch-friendly:hover {
        background: var(--bg-accent);
    }
}

@media (hover: none) {
    .touch-friendly:active {
        background: var(--bg-accent);
        transform: scale(0.98);
    }
}
```

---

## 🎨 Animation System

### Smooth Transitions
```css
.transition-smooth {
    transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.transition-bounce {
    transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

### Loading States
```css
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.loading {
    animation: pulse 2s infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.spinner {
    animation: spin 1s linear infinite;
}
```

---

*uDOS v1.0.4.1 Web Display Template*
*Modern, responsive web interfaces with IBM Plex Mono typography*
