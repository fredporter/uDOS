# Classicy Desktop - Deferred to v1.1.x

**Status**: 🔒 Preserved for Future Development
**Target Version**: v1.1.x
**Integration**: Tauri Desktop Application

---

## Overview

Classicy Desktop is an exceptional Mac OS 8 Platinum interface recreation built with React. This extension is being **preserved** as the foundation for uDOS's future desktop application in v1.1.x.

**Original Repository**: https://github.com/robbiebyrd/classicy
**Author**: Robbie Byrd
**License**: [Verify License]

---

## Why Deferred to v1.1.x?

### Current Status (v1.0.24)
uDOS v1.0.24 focuses on **web-based extensions** that integrate directly with the browser environment. Classicy Desktop requires:
- Node.js build process
- React framework
- Complex bundling
- Desktop window management

### Future Integration (v1.1.x)
In v1.1.x, uDOS will introduce **Tauri-based desktop applications**, making Classicy Desktop the perfect foundation:

1. **Tauri Integration**
   - Native desktop app wrapper
   - System-level integration
   - Native window management
   - File system access

2. **React Foundation**
   - Classicy Desktop's React architecture aligns perfectly with Tauri
   - Component-based UI design
   - State management
   - Professional polish

3. **Desktop Features**
   - Full System 7/8 desktop environment
   - Multi-window management
   - Drag-and-drop file operations
   - Native menu bar
   - System tray integration

4. **uDOS Integration**
   - Deep integration with uDOS core commands
   - File picker dialogs
   - Font manager integration
   - Markdown editor
   - Terminal emulator
   - Extension hosting

---

## Current Alternative (v1.0.24)

For v1.0.24, users can access **System Desktop** (`extensions/core/desktop/`):
- Web-based System 7 environment
- Pure CSS + JavaScript (no build process)
- Immediate browser access
- uDOS core integration
- Classic Mac aesthetic

System Desktop provides a polished System 7 experience **today**, while Classicy Desktop is preserved for the **native desktop app** in v1.1.x.

---

## Roadmap

### v1.0.24 (Current)
- ✅ Preserve Classicy Desktop in `/extensions/cloned/`
- ✅ Document deferral to v1.1.x
- ✅ Build System Desktop as web alternative

### v1.1.x (Future)
- [ ] Tauri desktop application architecture
- [ ] Integrate Classicy Desktop as primary UI
- [ ] Native window management
- [ ] System-level file operations
- [ ] Multi-platform builds (macOS, Linux, Windows)
- [ ] App store distribution

---

## Preservation

This directory contains the **complete Classicy Desktop codebase** for future reference and integration:

```
classicy-desktop/
├── dist/              # Built application
├── src/               # React source code
├── public/            # Static assets
├── package.json       # Dependencies
└── README.md          # Original documentation
```

**DO NOT DELETE**: This code will be the foundation for v1.1.x desktop app.

---

## Credits

**Original Work**: Classicy Desktop by Robbie Byrd
**Repository**: https://github.com/robbiebyrd/classicy
**Purpose**: Mac OS 8 Platinum interface recreation
**Quality**: Professional-grade, pixel-perfect System 8 recreation

**uDOS Integration Plans**:
- Tauri wrapper (v1.1.x)
- uDOS core command integration
- Extension hosting
- File system integration
- Multi-platform builds

---

## References

- **v1.0.24 Alternative**: `extensions/core/desktop/` (System Desktop)
- **v1.1.x Roadmap**: See `ROADMAP.MD` for Tauri integration plans
- **Tauri Framework**: https://tauri.app/
- **Design Philosophy**: Classic Mac System 7/8 aesthetic

---

**Status**: Preserved and ready for v1.1.x integration
**Current Focus**: System Desktop (web-based alternative)
**Future Focus**: Tauri + Classicy = Native Desktop App
