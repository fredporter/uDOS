# 📖 glow - Terminal Markdown Renderer for uDOS

**glow** is a terminal markdown renderer that brings beautiful markdown viewing to command-line workflows. Perfect for reviewing uDOS documentation and mission files.

## 🚀 Installation

### Via VS Code Task
1. Press `Cmd+Shift+P`
2. Type "Tasks: Run Task"
3. Select "📖 View markdown with glow"

### Manual Installation
```bash
./uCode/packages/install-glow.sh
```

## 🎯 Usage

### VS Code Integration
1. Press `Cmd+Shift+P`
2. Type "Tasks: Run Task"  
3. Select "📖 View markdown with glow"
4. File will be rendered with beautiful formatting

### Command Line Examples
```bash
# View README with glow
glow README.md

# View mission file
glow ./uMemory/missions/mission-001.md

# Browse all markdown files
glow .

# View with pager
glow -p README.md

# View specific file from URL
glow https://raw.githubusercontent.com/user/repo/main/README.md
```

## 🧠 uDOS Integration Workflows

### Mission Review
```bash
# View latest mission
glow $(ls -t ./uMemory/missions/mission-*.md | head -1)

# Browse all missions interactively
glow ./uMemory/missions/

# View mission with line numbers
glow -l ./uMemory/missions/mission-001.md
```

### Documentation Navigation
```bash
# View all documentation
glow ./docs/

# View specific template
glow ./uTemplate/mission-template.md

# View roadmap and progress
glow ./progress/ROADMAP_STATUS.md
```

### Dashboard Integration
```bash
# Generate and view dashboard
./uCode/dash.sh build && glow ./uMemory/dashboard.md

# View project status
glow ./docs/development/architecture/REPO_STRUCTURE_v1.0.md
```

## ⚙️ Configuration

Create `~/.config/glow/glow.yml` for custom styling:
```yaml
# Style options: auto, dark, light, notty
style: "auto"

# Width options: number, auto
width: 120

# Show local files in file picker
show_all_files: true

# Mouse support
mouse: true

# Pager options
pager: true
```

## 🎨 Styling Options

### Built-in Styles
- `auto` - Adapts to terminal theme
- `dark` - Dark theme optimized
- `light` - Light theme optimized  
- `notty` - Plain text output

### Custom Themes
```bash
# List available styles
glow --style help

# Use specific style
glow --style dark README.md
```

## 🔧 uDOS Integration Features

- **Mission Rendering**: Beautiful display of mission files
- **Template Preview**: Enhanced template viewing
- **Documentation Browser**: Interactive docs navigation
- **Dashboard Display**: Formatted dashboard viewing
- **VS Code Integration**: Direct task integration
- **uScript Support**: Available in automation workflows

## 📝 Best Practices

1. **Quick Reviews**: Use glow for rapid markdown file scanning
2. **Mission Briefings**: Beautiful mission file presentations
3. **Documentation**: Enhanced readme and doc viewing
4. **Template Previews**: Preview templates before use
5. **Status Reports**: Formatted progress and status display

---

*Beautiful markdown rendering for enhanced uDOS documentation experience.*
