# Extensions Archive

This directory contains obsolete and superseded extensions archived during the v1.0.24 reorganization.

## 📦 **Directory Structure**

```
archive/
├── old-bundled-web/      # Original bundled/web extensions (pre-v1.0.24)
├── old-clones/           # External CSS frameworks (now integrated)
└── obsolete/             # Deprecated experiments and tests
```

## 🗄️ **old-bundled-web/**

**Archived**: November 17, 2024  
**Reason**: Superseded by integrated `/core` extensions

### Contents

Original first-generation web extensions from `bundled/web/`:

- **dashboard/**: Multi-theme system dashboard (superseded by `/core/dashboard` with NES.css)
- **font-editor/**: Web-based font editing tools (superseded by `/core/character-editor`)
- **markdown-viewer/**: Basic markdown renderer (superseded by `/core/markdown` with GitHub CSS)
- **system-desktop/**: Early System 7 desktop (superseded by `/core/desktop` with full System 7 CSS)
- **teletext/**: Basic teletext interface (superseded by `/core/teletext` with Mallard fonts)
- **system-style/**: Styling frameworks (consolidated into `/core/shared` Synthwave DOS)

### Launch Scripts (archived)

- `classicy-launcher.py`
- `deploy.py`
- `launch.sh`
- `launch_web.py`
- `launch_web.sh`
- `teletext_extension.py`

### Documentation (archived)

- `README.md`: Original bundled/web documentation
- `README_OLD.md`: Historical notes
- `version-manifest.json`: Version tracking metadata

### Why Archived

The v1.0.24 reorganization rebuilt all web extensions from scratch with:

1. **Unified Structure**: Consolidated into `/core` instead of separate `bundled/web`
2. **Better Frameworks**: NES.css, System 7 CSS, GitHub CSS instead of custom implementations
3. **Consistent Theming**: Synthwave DOS color system across all extensions
4. **Modern Typography**: Adobe Source Family fonts in markdown viewer
5. **Improved Features**: uCODE commands, PANEL callouts, Command Palette
6. **Cleaner Code**: Complete rewrites with better organization

These original files are preserved for:
- Git history reference
- Feature comparison
- Migration documentation
- Learning purposes

## 🎨 **old-clones/**

**Archived**: November 17, 2024  
**Reason**: External frameworks now integrated into `/core`

### Contents

External CSS/UI frameworks that have been absorbed:

#### **classicy-desktop/**
- **Source**: https://github.com/robbiebyrd/classicy
- **Description**: Mac OS 8 Platinum interface (React)
- **Integration**: System 7 CSS now in `/core/desktop/index-udos.html`
- **Status**: Fully integrated with uDOS-specific enhancements

#### **c64css3/**
- **Source**: https://github.com/RoelN/c64css3
- **Description**: Commodore 64 CSS framework
- **Integration**: C64 Terminal now in `/core/c64-terminal/` with PetMe font
- **Status**: Rebuilt with authentic Polaroid palette

#### **nes-style/**
- **Source**: https://github.com/nostalgic-css/NES.css
- **Description**: 8-bit Nintendo CSS framework
- **Integration**: NES Dashboard now in `/core/dashboard/index-nes.html`
- **Status**: CDN-based integration with custom widgets

### Why Archived

We cloned these repositories to study and adapt them, but the final implementations are now:

1. **Self-Contained**: Core extensions don't depend on external repos
2. **Customized**: Heavily modified to fit uDOS aesthetic and functionality
3. **Integrated**: Combined with Synthwave DOS colors and uDOS commands
4. **Maintained**: Part of uDOS codebase instead of external dependencies

Original repos preserved for:
- License compliance (attribution maintained in CREDITS.md)
- Update tracking (monitor upstream changes)
- Reference implementation
- Learning CSS framework patterns

## 🚮 **obsolete/**

**Purpose**: Future archival location for deprecated experiments

Currently empty. Will contain:
- Failed experiments
- Deprecated prototypes
- Replaced implementations
- Test files no longer needed

## 📊 **v1.0.24 Migration Summary**

### Before (Pre-v1.0.24)

```
extensions/
├── bundled/web/          # 7 separate extensions
├── cloned/               # 6 external repos
├── core/                 # Shared libraries only
└── fonts/                # Mixed font sources
```

### After (v1.0.24)

```
extensions/
├── core/                 # 7 unified extensions + shared
├── cloned/               # 2 tools (micro, typo)
├── fonts/                # Curated retro fonts
├── archive/              # Historical implementations
└── templates/            # Extension scaffolding
```

### What Was Consolidated

- ✅ All web extensions moved from `bundled/web/` → `/core`
- ✅ External frameworks integrated and archived
- ✅ Shared libraries unified in `/core/shared`
- ✅ Launch scripts replaced with uDOS CLI commands
- ✅ Documentation updated to reflect new structure

### What Was Improved

1. **Phase 1**: Consolidated structure
2. **Phase 2**: C64 Terminal rebuild (PetMe font, Polaroid palette)
3. **Phase 3**: Teletext rebuild (Mallard fonts, BBC standards)
4. **Phase 4**: Character Editor (multi-resolution, 8×8 to 128×128)
5. **Phase 4.5-4.7**: Synthwave DOS colors, migration tools
6. **Phase 5**: Markdown Viewer (GitHub CSS, uCODE, PANEL)
7. **Phase 5.1**: Typography stack (Adobe Source fonts)
8. **Phase 6**: Dashboard (NES.css framework)
9. **Phase 7**: System Desktop (System 7 CSS, Command Palette)

## 🔗 **Git History**

All archived files are preserved in git history:

```bash
# View bundled/web history
git log --follow -- extensions/bundled/web/

# View specific extension evolution
git log --follow -- extensions/bundled/web/dashboard/

# Compare old vs new implementations
git diff HEAD~11 HEAD -- extensions/core/dashboard/
```

## 📝 **Notes**

- **Do Not Modify**: Files in archive/ are read-only references
- **Do Not Deploy**: Archive contents are not for production use
- **Maintain History**: Keep git history intact for attribution
- **Reference Only**: Use for comparison and learning

---

**Last Updated**: November 17, 2024  
**Archive Version**: v1.0.24-cleanup  
**Total Files Archived**: ~30,000+ lines across 3 directories
