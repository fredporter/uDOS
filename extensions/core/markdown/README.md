# 📚 uDOS Markdown Viewer

**Version**: 1.0.25
**Type**: Core Extension
**Port**: 9000
**Purpose**: Minimal markdown viewer with typography-first design and Typo editor integration

---

## 🚀 Quick Start

### Launch Server (v1.0.25 Unified Server)
```bash
# From markdown directory
./start.sh

# Or from extensions/core directory
./launch.sh markdown

# Or directly with Python
python3 extensions_server.py markdown
```

Opens at: `http://localhost:9000`

---

## ✨ Features

### 🎨 **Clean Reading Experience**
- **Minimal Design**: Distraction-free interface inspired by [Typo](https://github.com/ivanreese/typo)
- **Dark/Light Themes**: Professional color schemes optimized for reading
- **Typography-First**: Humanist fonts, optimal line length (65ch), 1.6 line height
- **Smooth Interactions**: Polished 250ms transitions throughout
- **Collapsible Sidebar**: Hide file browser for focused reading (`Ctrl+B`)

### 🎨 **Syntax Highlighting**
- Highlight.js (11.9.0) with GitHub themes
- Theme-aware: GitHub Dark (dark mode) / GitHub Light (light mode)
- Support for 190+ languages
- Automatic language detection

### 📂 **File Management**
- **Category Tree**: Organized navigation by folder structure
- **Fuzzy Search**: Fast, typo-tolerant file finder
- **Active Highlighting**: Visual indicator of current file
- **Refresh Button**: Reload file list without page refresh

### ✏️ **Editor Integration**
- **Typo Link**: One-click launch to edit files in Typo editor
- **Edit Button**: Opens Typo in new tab (http://localhost:5173)
- **Keyboard Shortcut**: `Ctrl+E` for quick access
- **Smart Visibility**: Edit button appears only when file is loaded

### ⌨️ **uCODE Command System**
Interactive commands embedded in markdown:
```
[FILE|READ|/path/to/file.txt]
[SYSTEM|INFO]
[HELP|COMMAND|grep]
[WEB|START|dashboard]
```
Commands are **clickable** and execute actions directly!

### 📦 **PANEL Callouts**
Enhanced callout blocks:
```
:::note / :::warning / :::danger / :::success
Your content here
:::
```

### 👁️ **View Modes**
- **Rendered**: Clean markdown display
- **Source**: Raw markdown viewing
- **Split**: Side-by-side view (future)

### 🔍 **Smart Features**
- 📚 Knowledge Library Browser with category organization
- 🔍 Fuzzy search with typo tolerance
- 📊 File metadata (size, modified date)
- 📑 Clean breadcrumb navigation
- 😀 Full emoji support
- 🖥️ Desktop-optimized responsive design

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+/` | Toggle Light/Dark Theme |
| `Ctrl+B` | Toggle Sidebar |
| `Ctrl+F` | Focus Search |
| `Ctrl+E` | Edit in Typo |
| `Ctrl+S` | Download File |

---

## 🚀 Installation

```bash
# Install Python dependencies
pip install flask markdown2 thefuzz pygments

# Or use requirements.txt
pip install -r requirements.txt
```

### CoreUI Icons
Icons are automatically loaded from `/extensions/assets/icons/coreui/`

No additional installation needed - included in uDOS asset consolidation.

---

## 📖 Usage

### Start Server

```bash
# From uDOS root
cd extensions/core/markdown
/path/to/venv/bin/python server.py

# Or if Python is in PATH
python server.py
```

### Access Viewer
Open http://localhost:9000 in your browser
```

Or from uDOS CLI:
```
[WEB|START|markdown-viewer]
```

Then open: **http://localhost:9000**

### Navigation

1. **Browse Categories** - Click to expand/collapse categories
2. **Search Files** - Type in search box (fuzzy matching)
3. **View Document** - Click file to load
4. **Switch Views** - Use view mode dropdown
5. **Toggle Theme** - Click moon icon or `Ctrl+/`

### uCODE Examples

Embed interactive commands in your markdown:

```markdown
Read a file: [FILE|READ|/knowledge/survival/water.md]
Get system info: [SYSTEM|INFO]
Search knowledge: [SEARCH|water purification]
Open dashboard: [WEB|START|dashboard]
Copy text: [COPY|Hello World]
```

Click any command to execute it!

### PANEL Examples

Create callout blocks:

```markdown
:::note
This is a note with **markdown** support
:::

:::warning
⚠️ Important warning message
:::

:::danger
🛑 Critical safety information
:::

:::success
✅ Task completed successfully
:::
```

---

## API Endpoints

```
GET  /                         Main viewer interface
GET  /api/browse               List knowledge library
GET  /api/search?q=query       Fuzzy search
GET  /api/render?path=file.md  Render markdown to HTML
GET  /api/diagrams             List all diagrams
GET  /api/categories           Get category tree
```

---

## Configuration

Edit `config.json`:

```json
{
  "port": 9000,
  "knowledge_root": "../../../../knowledge",
  "diagrams_root": "../../../../data/system/diagrams",
  "fuzzy_threshold": 60,
  "max_results": 50,
  "enable_emoji": true,
  "enable_syntax_highlight": true,
  "theme": "github-dark"
}
```

---

## Technology Stack

- **Backend:** Flask (Python web framework)
- **Markdown:** markdown2 (GitHub-flavored markdown)
- **Search:** thefuzz (fuzzy string matching)
- **Highlighting:** Pygments (syntax highlighting)
- **Frontend:** Vanilla JS + CSS (no heavy frameworks)
- **Emoji:** Native UTF-8 support

---

## Development

```bash
# Install dev dependencies
pip install flask markdown2 pygments thefuzz python-emoji

# Run in debug mode
FLASK_DEBUG=1 python server.py

# Test fuzzy search
python -c "from thefuzz import fuzz; print(fuzz.ratio('water purif', 'water-purification'))"
```

---

## Integration with uDOS

### KB Command Enhancement

```ucode
[KB|BROWSE]           → Opens markdown viewer
[KB|SEARCH|query]     → Fuzzy search, shows in viewer
[KB|VIEW|path]        → Render specific markdown file
```

### GUIDE Command

```ucode
[GUIDE|KB|topic]      → Opens in markdown viewer with navigation
[GUIDE|DIAGRAM|name]  → Shows diagram with related guides
```

---

## File Structure

```
markdown-viewer/
├── server.py           # Flask application
├── config.json         # Configuration
├── README.md           # This file
├── manifest.json       # Extension metadata
├── static/
│   ├── style.css       # Styling
│   ├── viewer.js       # Frontend logic
│   └── search.js       # Fuzzy search UI
└── templates/
    ├── index.html      # Main viewer
    ├── browse.html     # Category browser
    └── search.html     # Search interface
```

---

## Emoji Support

**Native UTF-8** - No font file needed!

Supported everywhere:
- ✅ In markdown headings
- ✅ In tables and lists
- ✅ In code blocks (preserved)
- ✅ In search results
- ✅ In file names

Example usage:
```markdown
## 🔥 Fire Starting Methods
- ⚠️ **Warning:** Practice in safe area
- 📊 Success Rate: ████████░░ 80%
- 🎯 Difficulty: Medium
```

---

## Future Enhancements

- [ ] Table of contents auto-generation
- [ ] Export to PDF (text-based)
- [ ] Diagram editor integration
- [ ] Multi-file search (grep-like)
- [ ] Version history viewer
- [ ] Collaborative editing
- [ ] Mobile app companion

---

**Version:** 1.0.21
**Status:** In Development
**Dependencies:** Flask, markdown2, Pygments, thefuzz
