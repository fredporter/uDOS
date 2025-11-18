# Markdown Viewer Changelog

## v1.0.24 - Clean Redesign (Current)

### 🎨 Major UI Overhaul
- **New Minimal Design**: Typo-inspired clean aesthetic with typography-first approach
- **CoreUI Icons**: Integrated 1500+ professional icons for UI elements
- **Collapsible Sidebar**: Toggle file browser for distraction-free reading
- **Improved Typography**: Optimized fonts, line length (65ch), and spacing for readability

### ✨ New Features

#### Theme System
- **Dark/Light Themes**: Clean color palettes optimized for both modes
- **Automatic Syntax Highlighting**: Theme-aware code blocks (GitHub Dark/Light)
- **Theme Persistence**: Remembers your preference across sessions
- **Theme Toggle**: Quick switch via toolbar button or `Ctrl+/`

#### Sidebar Controls
- **Collapsible Browser**: Hide file tree for focused reading
- **State Persistence**: Remembers collapsed/expanded state
- **Quick Toggle**: `Ctrl+B` or toolbar button
- **Smooth Animations**: 250ms transitions for all interactions

#### Edit Integration
- **Typo Editor Link**: Opens current file in Typo markdown editor
- **New Tab Launch**: Edit button opens Typo in separate window
- **Keyboard Shortcut**: `Ctrl+E` to launch editor
- **Smart Visibility**: Edit button appears only when file is loaded

#### File Management
- **Refresh Button**: Reload file list without page refresh
- **Fuzzy Search**: Fast, typo-tolerant file search
- **Category Tree**: Organized file navigation with expand/collapse
- **Active Highlighting**: Visual indicator for currently viewed file

### 📋 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+/` | Toggle Light/Dark Theme |
| `Ctrl+B` | Toggle Sidebar |
| `Ctrl+F` | Focus Search |
| `Ctrl+E` | Edit in Typo |
| `Ctrl+S` | Download File |

### 🎯 Design Philosophy

#### Typography-First
- **Humanist Fonts**: System UI, -apple-system, BlinkMacSystemFont
- **Optimal Line Length**: 65 characters for comfortable reading
- **Clear Hierarchy**: Consistent heading scales and spacing
- **Enhanced Readability**: 1.6 line height, generous margins

#### Minimal Interface
- **Subtle Borders**: Delicate separators (1px rgba)
- **Restrained Colors**: Professional gray scale with accent colors
- **Clean Header**: Minimal chrome, maximum content
- **Focus on Content**: UI fades to background when reading

#### Smooth Interactions
- **250ms Transitions**: Consistent animation timing
- **Hover States**: Clear interactive feedback
- **Collapsible Elements**: Graceful expand/collapse
- **Responsive Design**: Adapts to different viewport sizes

### 🔧 Technical Details

#### CSS Architecture
- **CSS Variables**: Theme-aware color system
- **Grid Layout**: Flexible sidebar/content arrangement
- **Custom Properties**: Centralized sizing and spacing
- **No External CSS Frameworks**: Pure CSS, no dependencies

#### Asset Integration
- **CoreUI Icons**: `/extensions/assets/icons/coreui/css/free.min.css`
- **CDN Scripts**: marked.js, highlight.js for performance
- **Optimized Fonts**: System fonts for instant rendering
- **Minimal Bundle**: Fast load times, no bloat

#### JavaScript Enhancements
- **LocalStorage**: Theme and sidebar state persistence
- **Smooth Scrolling**: Better navigation experience
- **Dynamic Icons**: Context-aware icon changes
- **Error Handling**: Graceful degradation

### 🗂️ File Structure
```
extensions/core/markdown/
├── server.py                          # Flask backend
├── templates/
│   └── index.html                     # Clean HTML template
└── static/
    ├── markdown-viewer.js             # Core logic
    ├── markdown-viewer-clean.css      # New minimal design
    ├── ucode-processor.js             # uCODE syntax support
    └── panel-processor.js             # PANEL syntax support
```

### 🔗 Integration Points

#### Typo Editor
- **Port**: 5173 (default Vite dev server)
- **URL**: `http://localhost:5173`
- **Launch**: Edit button or `Ctrl+E`
- **Note**: File must be opened manually in Typo (File System Access API limitation)

#### Asset Paths
- **Icons**: `../../assets/icons/coreui/`
- **Fonts**: System fonts (no external files)
- **CSS**: Self-contained in `markdown-viewer-clean.css`
- **JS**: CDN for marked.js and highlight.js

### 📝 Configuration

#### Theme Variables (CSS)
```css
:root[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --bg-secondary: #252525;
  --text-primary: #e8e8e8;
  --text-secondary: #a0a0a0;
  --accent: #60a5fa;
  --border: rgba(255, 255, 255, 0.1);
}

:root[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --text-primary: #1a1a1a;
  --text-secondary: #6c757d;
  --accent: #3b82f6;
  --border: rgba(0, 0, 0, 0.1);
}
```

#### Sidebar Settings
```javascript
// Width when expanded
.file-browser { width: 280px; }

// Collapsed state
.sidebar-collapsed .file-browser { width: 0; }

// Transition timing
transition: all 250ms ease;
```

### 🎨 Color Palette

#### Dark Theme
- **Background**: #1a1a1a (primary), #252525 (secondary)
- **Text**: #e8e8e8 (primary), #a0a0a0 (secondary)
- **Accent**: #60a5fa (blue)
- **Success**: #22c55e (green)
- **Warning**: #f59e0b (amber)
- **Danger**: #ef4444 (red)

#### Light Theme
- **Background**: #ffffff (primary), #f8f9fa (secondary)
- **Text**: #1a1a1a (primary), #6c757d (secondary)
- **Accent**: #3b82f6 (blue)
- **Success**: #16a34a (green)
- **Warning**: #d97706 (amber)
- **Danger**: #dc2626 (red)

### 🚀 Performance

#### Load Time
- **Initial**: ~200ms (system fonts, minimal CSS)
- **CDN Scripts**: ~500ms (marked.js, highlight.js)
- **File Load**: ~100ms (local Flask server)
- **Theme Switch**: Instant (CSS variables)

#### Bundle Size
- **HTML**: ~8KB (template)
- **CSS**: ~13KB (markdown-viewer-clean.css)
- **JS**: ~15KB (markdown-viewer.js)
- **Total**: ~36KB (excluding CDN scripts)

### 📚 Dependencies

#### Python (Backend)
- **Flask**: 2.0.0+ (web server)
- **markdown2**: 2.5.4+ (markdown parsing)
- **thefuzz**: 0.22.1+ (fuzzy search)
- **pygments**: 2.19.2+ (syntax highlighting)

#### JavaScript (Frontend)
- **marked.js**: 11.1.0 (markdown rendering)
- **highlight.js**: 11.9.0 (code syntax highlighting)
- **CoreUI Icons**: 2.0+ (UI icons)

### 🐛 Known Issues
- **Typo Integration**: File must be manually opened in Typo (File System Access API limitation)
- **PDF Export**: Browser print dialog, no custom PDF styling yet
- **Mobile**: Optimized for desktop, mobile improvements planned

### 🔮 Future Enhancements
- [ ] Direct file opening in Typo (if File System Access API allows)
- [ ] Custom PDF export with preserved styling
- [ ] Mobile-optimized layout
- [ ] More theme options (custom color schemes)
- [ ] Bookmark/favorites system
- [ ] Recent files list
- [ ] Full-text search across all files
- [ ] Table of contents generation
- [ ] Mermaid diagram support

### 🙏 Credits
- **Design Inspiration**: [Typo](https://github.com/ivanreese/typo) by Ivan Reese
- **Icons**: [CoreUI Icons](https://coreui.io/icons/) (MIT/CC BY 4.0)
- **Markdown**: [marked.js](https://marked.js.org/) (MIT)
- **Syntax Highlighting**: [highlight.js](https://highlightjs.org/) (BSD)
- **System Fonts**: Apple San Francisco, Segoe UI, system defaults

---

**Version**: 1.0.24
**Date**: 2024
**Author**: uDOS Development Team
