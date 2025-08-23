````markdown
# Development Experiments

This directory contains development and testing tools for uDOS experimentation.

## 📁 Directory Contents

### Development Tools
- `install-typo.sh` - Markdown editor installer for development
- `install-nethack.sh` - Classic roguelike game installer for testing
- `install-min-browser.sh` - Min Browser installer from GitHub
- `install-micro.sh` - Micro text editor installer from GitHub
- `install-type-game.sh` - Type terminal typing game installer from GitHub
- `ascii-generator/` - ASCII art generation tools for testing
- `urltomarkdown/` - URL to markdown conversion tools for testing

### Browser Testing
- **Min Browser** - https://minbrowser.org - Minimal, fast browser for testing web interfaces
  - GitHub: https://github.com/minbrowser/min
  - Install: `./install-min-browser.sh`
  - Launch: `./launch-min-browser.sh` (after installation)

### Text Editors
- **Micro Editor** - https://micro-editor.github.io/ - Modern terminal-based text editor
  - GitHub: https://github.com/zyedidia/micro
  - Install: `./install-micro.sh`
  - Launch: `./launch-micro.sh` (after installation)
  - Features: Syntax highlighting, mouse support, common keybindings

### Terminal Games & Tools
- **Type Game** - Terminal-based typing speed test and practice
  - GitHub: https://github.com/qurle/type
  - Install: `./install-type-game.sh`
  - Launch: `./launch-type-game.sh` (after installation)
  - Features: Real-time WPM tracking, accuracy measurement, typing practice

### Game/Entertainment Testing
- `nethack/` - NetHack game integration files for development

## 🎯 Purpose

These tools are:
- **Development**: Used for testing uDOS functionality
- **Experimental**: Under active development
- **Optional**: Testing tools that don't affect core system

## 🚀 Usage

Development installers can be run directly:
```bash
./install-typo.sh
./install-nethack.sh
```

## 📋 Notes

- These packages are kept for development and testing purposes
- Installation may require elevated privileges
- Test in development environment before production use
