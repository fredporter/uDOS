# Markdown Viewer Web Extension

**Port:** 9000
**Purpose:** Browse and view uDOS knowledge library with markdown rendering
**Features:** Fuzzy search, emoji support, syntax highlighting, knowledge browser

---

## Features

- 📚 **Knowledge Library Browser** - Navigate all 8 categories
- 🔍 **Fuzzy Search** - Fast file/content search with typo tolerance
- 📝 **Markdown Rendering** - Full GitHub-flavored markdown support
- 🎨 **Syntax Highlighting** - Code blocks with language detection
- 😀 **Emoji Support** - Native UTF-8 emoji rendering
- 📊 **Teletext Graphics** - Preserved in code blocks
- 🔗 **Smart Links** - Auto-link to related diagrams/guides
- 📱 **Responsive** - Works on all screen tiers

---

## Installation

```bash
# Add required packages
pip install flask markdown2 pygments thefuzz

# Or use updated requirements.txt
pip install -r requirements.txt
```

---

## Usage

### Start Server

```bash
cd extensions/bundled/web/markdown-viewer
python server.py
```

Or from uDOS CLI:
```
[WEB|START|markdown-viewer]
```

Then open: http://localhost:9000

### Browse Knowledge

1. **Categories View** - Click category to expand
2. **Fuzzy Search** - Type to filter (handles typos)
3. **View Document** - Click file to render markdown
4. **Navigate** - Follow internal links automatically

### Search Examples

```
🔍 "wter purif"  → Finds "water-purification"
🔍 "if els"      → Finds "if-else"
🔍 "sqare not"   → Finds "square-knot"
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
