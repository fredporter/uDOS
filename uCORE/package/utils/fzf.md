# 🔍 fzf - Fuzzy Finder for uDOS

**fzf** is a general-purpose command-line fuzzy finder that enhances uDOS workflows with interactive file selection and filtering capabilities.

## 🚀 Installation

### Manual Installation
```bash
./uCode/packages/install-fzf.sh
```

## 🎯 Usage

### Basic Fuzzy Finding
```bash
# Interactive file finder
fzf

# Find and open file with default editor
fzf | xargs code

# Find in specific directory
fd . ./uMemory/missions/ | fzf

# Multi-select mode
fzf -m
```

## 🧠 uDOS Integration Workflows

### Mission Management
```bash
# Interactive mission selection
mission=$(fd 'mission-.*\.md$' ./uMemory/missions/ | fzf --preview 'bat {}')
[ -n "$mission" ] && code "$mission"

# Select active missions
fd 'mission-.*\.md$' ./uMemory/missions/ | fzf -m --preview 'glow {}'

# Find and edit mission templates
fd 'mission-template.*\.md$' ./uTemplate/ | fzf --preview 'bat {}'
```

### Template Selection
```bash
# Interactive template browser
template=$(fd '.*template.*\.md$' ./uTemplate/ | fzf --preview 'glow {}')
[ -n "$template" ] && ./uCode/ucode.sh CREATE FROM "$template"

# Find specific template types
fd 'move-template.*\.md$' ./uTemplate/ | fzf --preview 'bat {} --style=numbers'
```

### Log File Analysis
```bash
# Interactive log file selection
log_file=$(fd '\.log$' ./uMemory/logs/ | fzf --preview 'tail -20 {}')
[ -n "$log_file" ] && bat "$log_file"

# Find logs by date
fd "$(date +%Y-%m-%d).*\.log$" ./uMemory/logs/ | fzf --preview 'bat {}'
```

### Command History
```bash
# Enhanced command history search
history | fzf

# Search uCode command history
grep "ucode.sh" ~/.zsh_history | fzf

# Interactive git branch selection
git branch | fzf | xargs git checkout
```

## 🔧 Advanced Features

### Preview Integration
```bash
# With bat for syntax highlighting
fzf --preview 'bat --color=always {}'

# With glow for markdown
fd '\.md$' | fzf --preview 'glow {}'

# With ls for directories
fd -t d | fzf --preview 'ls -la {}'

# Custom preview command
fzf --preview 'if [ -d {} ]; then ls -la {}; else bat {}; fi'
```

### Custom Key Bindings
```bash
# In ~/.zshrc or ~/.bashrc
export FZF_DEFAULT_OPTS="
  --height 60%
  --layout=reverse
  --border
  --preview-window=right:50%
  --bind 'ctrl-y:execute-silent(echo {} | pbcopy)'
  --bind 'ctrl-e:execute(code {})'
  --bind 'ctrl-v:execute(bat {})'
"

# Custom uDOS shortcuts
alias fmission='fd "mission-.*\.md$" ./uMemory/missions/ | fzf --preview "glow {}"'
alias ftemplate='fd "template.*\.md$" ./uTemplate/ | fzf --preview "bat {}"'
alias flog='fd "\.log$" ./uMemory/logs/ | fzf --preview "tail -20 {}"'
```

### Pipeline Integration
```bash
# Search content and select files
rg -l "TODO" | fzf --preview 'rg --color=always "TODO" {}'

# Find and process files
fd '\.md$' | fzf -m | xargs glow

# Interactive git file selection
git ls-files | fzf -m --preview 'git log --oneline {}'
```

## 📊 uDOS Dashboard Integration

### Interactive Dashboard Navigation
```bash
# Browse dashboard components
echo -e "missions\nlogs\ntemplates\npackages\nstatus" | fzf | while read component; do
  case $component in
    missions) fd 'mission-.*\.md$' ./uMemory/missions/ | fzf --preview 'glow {}' ;;
    logs) fd '\.log$' ./uMemory/logs/ | fzf --preview 'tail -20 {}' ;;
    templates) fd 'template.*\.md$' ./uTemplate/ | fzf --preview 'bat {}' ;;
    packages) cat ./package/manifest.json | jq -r '.packages | to_entries[] | .key' | fzf ;;
    status) ./uCode/dash.sh build ;;
  esac
done
```

### Quick Actions Menu
```bash
# uDOS quick actions
echo -e "🚀 Start uDOS\n📊 Generate Dashboard\n📝 Create Mission\n🔍 Check Setup\n🧹 Clean uDOS" | fzf | while read action; do
  case "$action" in
    *"Start uDOS"*) ./uCode/ucode.sh ;;
    *"Generate Dashboard"*) ./uCode/dash.sh ;;
    *"Create Mission"*) ./uCode/structure.sh build --input ;;
    *"Check Setup"*) ./uCode/check.sh all ;;
    *"Clean uDOS"*) ./uCode/destroy.sh ;;
  esac
done
```

## ⚙️ Configuration

### Environment Variables
```bash
# In ~/.zshrc or ~/.bashrc
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'

# uDOS-specific defaults
export FZF_DEFAULT_OPTS="
  --height=60%
  --layout=reverse
  --border=rounded
  --margin=1
  --padding=1
  --color='bg+:#293739,bg:#1B1D1E,border:#808080,spinner:#E6DB74,hl:#7E8E91'
"
```

### Custom Functions
```bash
# In ~/.zshrc
udos_mission_edit() {
  local mission=$(fd 'mission-.*\.md$' ./uMemory/missions/ | fzf --preview 'glow {}')
  [ -n "$mission" ] && code "$mission"
}

udos_template_use() {
  local template=$(fd 'template.*\.md$' ./uTemplate/ | fzf --preview 'bat {}')
  [ -n "$template" ] && ./uCode/ucode.sh CREATE FROM "$template"
}

udos_log_view() {
  local log=$(fd '\.log$' ./uMemory/logs/ | fzf --preview 'tail -20 {}')
  [ -n "$log" ] && bat "$log"
}
```

## 🔧 uDOS Integration Features

- **Interactive File Selection**: Enhanced file browsing and selection
- **Mission Navigation**: Quick mission file access and editing
- **Template Browser**: Interactive template selection and usage
- **Log Analysis**: Easy log file discovery and viewing
- **Command Integration**: Seamless integration with other uDOS tools
- **Dashboard Navigation**: Interactive dashboard component browsing
- **Git Integration**: Enhanced version control workflows

---

*Interactive fuzzy finding for enhanced uDOS workflow navigation.*
