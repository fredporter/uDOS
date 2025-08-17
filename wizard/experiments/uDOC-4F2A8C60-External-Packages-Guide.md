# External Package Installation Guide

These packages are valuable but not bundled with uDOS. Install them manually for enhanced functionality.

## 🚀 Performance Tools (Recommended)

### ripgrep - Fast text search
```bash
# macOS with Homebrew
brew install ripgrep

# Ubuntu/Debian  
sudo apt install ripgrep

# Usage in uDOS
rg "search term" ./uMemory/
```

### bat - Syntax highlighted file viewer
```bash
# macOS with Homebrew
brew install bat

# Ubuntu/Debian
sudo apt install bat

# Usage in uDOS  
bat README.md
bat -n script.sh  # with line numbers
```

### fd - Fast file finder
```bash
# macOS with Homebrew
brew install fd

# Ubuntu/Debian
sudo apt install fd-find

# Usage in uDOS
fd ".md" ./docs/
fd "script" ./uCORE/
```

### fzf - Fuzzy finder
```bash
# macOS with Homebrew
brew install fzf

# Ubuntu/Debian
sudo apt install fzf

# Usage in uDOS
find . -name "*.sh" | fzf
```

## 💡 Enhancement Tools (Optional)

### glow - Terminal markdown renderer
```bash
# macOS with Homebrew  
brew install glow

# Usage in uDOS
glow README.md
glow docs/*.md
```

## 🔧 Installation Tips

1. **macOS**: Install Homebrew first - https://brew.sh
2. **Linux**: Use your distribution's package manager
3. **Windows**: Use Windows Subsystem for Linux (WSL)

## ✅ Verification

After installation, verify with:
```bash
which rg bat fd fzf glow
```

These tools integrate seamlessly with uDOS workflows once installed.
