# Using Typo for Markdown Viewing

**Quick Start:** All markdown viewing in uDOS now uses Typo's preview mode!

---

## Basic Usage

### View a Markdown File
```bash
FILE SHOW knowledge/water/filtration.md --web
```
**Result:** Opens in Typo preview mode with beautiful rendering

### Start Markdown Viewer
```bash
POKE START markdown
```
**Result:** Launches Typo on port 5173, ready to browse and view markdown files

### View Specific File on Startup
```bash
POKE START markdown
# Then navigate to the file in Typo's file browser
# Or use the URL: http://localhost:5173?file=/path/to/file.md
```

---

## Why Typo Preview Mode?

### Features
- ✅ **Live rendering** - See changes instantly
- ✅ **Split mode** - Edit and preview side-by-side
- ✅ **File browser** - Navigate your knowledge base
- ✅ **Search** - Find content quickly
- ✅ **Modern UI** - Clean, polished interface
- ✅ **Syntax highlighting** - Code blocks look great
- ✅ **Dark mode** - Easy on the eyes

### Comparison

| Feature | Old markdown-viewer | Typo Preview |
|---------|-------------------|--------------|
| Rendering | Static HTML | Live markdown |
| Editing | ❌ No | ✅ Full editor |
| Preview | ✅ Basic | ✅ Advanced |
| Navigation | ❌ None | ✅ File tree |
| Search | ❌ No | ✅ Full-text |
| UI | 🕰️ Basic | 🚀 Modern |
| Updates | ❌ None | ✅ Regular |

---

## Integration with uDOS Commands

### GUIDE Command
```bash
GUIDE SHOW water_filtration
# Displays in terminal

# To view in Typo preview:
FILE SHOW knowledge/water/filtration.md --web
```

### KNOWLEDGE Command
```bash
KNOWLEDGE SHOW "Water Purification"
# Shows summary in terminal

# Open full document in Typo:
FILE SHOW knowledge/water/water_purification.md --web
```

### TREE Command
```bash
TREE knowledge
# Shows structure

# Browse in Typo's file tree:
POKE START markdown
# Navigate visually
```

---

## Advanced Usage

### Open Specific File via URL
```bash
# Start Typo
POKE START markdown

# Then in browser:
http://localhost:5173?file=/Users/you/Code/uDOS/knowledge/water/filtration.md
```

### Preview Mode vs Edit Mode
Typo automatically switches between modes:
- **Preview only** - When opened via `FILE SHOW --web`
- **Edit + Preview** - When opened normally from file browser
- **Toggle** - Use Typo's UI buttons to switch

### Custom Port
```bash
POKE START markdown --port 5174
```

### Stop Server
```bash
POKE STOP typo
# or
POKE STOP markdown  # Same server
```

---

## Workflow Examples

### 1. Research Workflow
```bash
# Find topic
KNOWLEDGE SEARCH "water purification"

# View in Typo
FILE SHOW knowledge/water/water_purification.md --web

# Edit notes
# (Switch to edit mode in Typo UI)

# Save automatically (Typo saves to disk)
```

### 2. Documentation Review
```bash
# Start viewer
POKE START markdown

# Browse file tree in Typo
# Click through knowledge/
# Review each guide
# Make edits inline
```

### 3. Tutorial Mode
```bash
# Start interactive guide
GUIDE START water_filtration

# Follow steps in terminal

# View diagrams in Typo
FILE SHOW knowledge/water/filtration_diagram.md --web
```

---

## Tips & Tricks

### 1. Keyboard Shortcuts (in Typo)
- `Ctrl+B` - Toggle file browser
- `Ctrl+P` - Quick file search
- `Ctrl+F` - Find in document
- `Ctrl+/` - Toggle preview

### 2. File Organization
Typo shows your file tree, so keep knowledge/ organized:
```
knowledge/
├── water/
│   ├── README.md          # Category overview
│   ├── filtration.md      # Topic guides
│   └── sources.md
├── fire/
└── ...
```

### 3. Cross-References
Use markdown links in your docs:
```markdown
See also: [Water Sources](./sources.md)
```
Typo will make these clickable!

### 4. Images
```markdown
![Diagram](../diagrams/water_filter.svg)
```
Typo renders images inline.

### 5. Code Blocks
```markdown
\`\`\`bash
POKE START markdown
\`\`\`
```
Syntax highlighting works automatically.

---

## Troubleshooting

### Typo Won't Start
```bash
# Check if port is in use
lsof -ti:5173

# Kill existing process
kill -9 <PID>

# Restart
POKE START markdown
```

### File Doesn't Open
```bash
# Check file path (absolute vs relative)
FILE SHOW ./knowledge/water/filtration.md --web  # ❌ Might fail

# Use full path
FILE SHOW knowledge/water/filtration.md --web    # ✅ Better
```

### Preview Not Rendering
1. Check browser console (F12)
2. Verify file is valid markdown
3. Try refreshing (Ctrl+R)
4. Restart Typo: `POKE RESTART markdown`

---

## Migration from Old Viewer

If you have scripts or aliases using the old markdown-viewer:

### Update Scripts
```bash
# Old .uscript files
# Find: POKE START markdown-viewer
# Replace: POKE START markdown
```

### Update Aliases
```bash
# If you had:
alias mdview='uDOS -c "POKE START markdown-viewer"'

# Change to:
alias mdview='uDOS -c "POKE START markdown"'
```

### No Action Needed
Most commands work automatically:
- `FILE SHOW *.md --web` - Already updated
- `POKE START markdown` - Works both ways

---

## FAQ

**Q: Can I still use the old markdown-viewer?**  
A: It's archived but not deleted. You can restore from `extensions/archive/markdown-viewer-legacy/` if absolutely necessary. Not recommended.

**Q: Does Typo save changes automatically?**  
A: Yes! Edits are saved to disk immediately.

**Q: Can I use Typo without uDOS?**  
A: Yes! Typo is a standalone app. Navigate to `extensions/cloned/typo/` and run `npm run dev`.

**Q: What about performance?**  
A: Typo uses ~120MB RAM vs old viewer's ~50MB. Worth it for the features!

**Q: Can I customize Typo's appearance?**  
A: Typo has built-in themes. Check its settings menu.

**Q: Will my markdown files work in Typo?**  
A: Yes! Typo supports standard markdown + common extensions (tables, code blocks, etc.)

---

## See Also

- `wiki/POKE-Command-Reference.md` - Complete POKE documentation
- `extensions/cloned/typo/README.md` - Typo's official docs
- `dev/notes/markdown-viewer-migration.md` - Migration details
- `extensions/archive/README.md` - Archive information

---

**Enjoy Typo's preview mode!** 🚀
