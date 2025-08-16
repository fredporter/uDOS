# 🔍 fd - Fast File Finder for uDOS

**fd** is a modern replacement for the `find` command with intuitive syntax and excellent performance. This integration brings fast file discovery to uDOS workflows.

## 🚀 Installation

### Via VS Code Task
1. Press `Cmd+Shift+P`
2. Type "Tasks: Run Task"
3. Select "🔍 Find files with fd"

### Manual Installation
```bash
./uCode/packages/install-fd.sh
```

## 🎯 Usage

### VS Code Integration
1. Press `Cmd+Shift+P`
2. Type "Tasks: Run Task"  
3. Select "🔍 Find files with fd"
4. Enter search pattern when prompted

### Command Line Examples
```bash
# Find all markdown files
fd '\.md$'

# Find files in uMemory directory
fd . ./uMemory/

# Find mission files
fd 'mission.*\.md$' ./uMemory/missions/

# Case-insensitive search
fd -i 'readme'

# Find directories only
fd -t d template

# Execute command on results
fd '\.log$' -x bat {}
```

## 🧠 AI-Assisted Workflows

### Common uDOS Patterns
```bash
# Find all mission files
fd 'mission-.*\.md$' ./uMemory/missions/

# Find template files
fd 'template.*\.md$' ./uTemplate/

# Find log files from today
fd '\.log$' ./uMemory/logs/ | grep $(date +%Y-%m-%d)

# Find configuration files
fd 'config\.(json|yaml|md)$'
```

### Integration with Other Tools
```bash
# Combine with ripgrep for content search
fd '\.md$' | xargs rg "TODO"

# Combine with bat for file viewing
fd 'README\.md$' -x bat {}

# Find and edit files
fd 'mission.*\.md$' | head -5 | xargs code
```

## ⚙️ Configuration

Create `~/.config/fd/ignore` for custom ignore patterns:
```
node_modules/
.git/
*.tmp
*.log
```

## 🔧 uDOS Integration Features

- **Template Discovery**: Quickly find template files across uTemplate/
- **Mission Management**: Fast location of mission files in uMemory/
- **Log Analysis**: Efficient log file discovery
- **VS Code Integration**: Direct integration with editor workflows
- **uScript Support**: Available in uScript automation scripts

---

*Fast, intuitive file finding for the uDOS ecosystem.*
