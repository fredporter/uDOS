# Wizard Experiments

This directory contains experimental packages, external tool installers, and development prototypes that are not part of the core uDOS system.

## 📁 Directory Contents

### External Package Installers
- `install-bat-clean.sh` - Syntax-highlighted file viewer installer
- `install-typo.sh` - Markdown editor installer  
- `install-nethack.sh` - Classic roguelike game installer

### Package Documentation
- `uDOC-4F2A8C60-External-Packages-Guide.md` - Guide for external tools (ripgrep, bat, fd, fzf, glow)

### Game/Entertainment
- `nethack/` - NetHack game integration files

## 🎯 Purpose

These tools and packages are:
- **External Dependencies**: Require system package managers (brew, apt, etc.)
- **Experimental**: Under development or testing
- **Optional**: Enhance uDOS but not required for core functionality
- **Entertainment**: Games and non-essential tools

## 🚀 Usage

External package installers can be run directly:
```bash
./install-bat-clean.sh
./install-typo.sh
./install-nethack.sh
```

Refer to `uDOC-4F2A8C60-External-Packages-Guide.md` for manual installation instructions of performance tools.

## 📋 Notes

- These packages are kept separate from uCORE to maintain system integrity
- Installation may require elevated privileges
- Some packages may have additional system dependencies
- Test in development environment before production use
