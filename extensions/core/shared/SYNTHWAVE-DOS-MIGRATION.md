# Synthwave DOS Color Palette Migration Guide

## Overview

This document tracks the migration from the Polaroid C64 palette to the standardized **Synthwave DOS 16-color palette** across all uDOS extensions.

## Color Mapping Reference

### Old Polaroid → New Synthwave DOS

| Old Variable | New Variable | Hex Value | Notes |
|--------------|--------------|-----------|-------|
| `--c64-black` | `--color-black` | #000000 | Unchanged |
| `--c64-white` | `--color-white-bright` | #FFFFFF | Unchanged |
| `--c64-red` | `--color-red-bright` | #FB5607 | **Changed** - Blaze Orange |
| `--c64-cyan` | `--color-cyan-bright` | #8ECAE6 | **Changed** - Sky Blue Light |
| `--c64-purple` | `--color-magenta-bright` | #FF006E | **Changed** - Neon Pink |
| `--c64-green` | `--color-green-bright` | #06D6A0 | **Changed** - Emerald |
| `--c64-blue` | `--color-blue-bright` | #3A86FF | **Changed** - Azure Blue |
| `--c64-yellow` | `--color-yellow-bright` | #FFFF00 | Unchanged |
| `--c64-orange` | `--color-orange-bright` | #FFD166 | **Changed** - Golden Pollen |
| `--c64-light-blue` | `--color-cyan-bright` | #8ECAE6 | Merged with cyan |
| `--c64-light-green` | `--color-green-bright` | #06D6A0 | Merged with green |
| `--c64-dark-gray` | `--color-gray-dark` | #AAAAAA | **Changed** |
| `--c64-gray` | `--color-gray-light` | #CCCCCC | **Changed** |
| `--c64-light-gray` | `--color-gray-light` | #CCCCCC | Merged |
| `--polaroid-blue-full` | `--color-blue-dark` | #023047 | **Changed** - Deep Space Blue |

### Block Graphics Palette (8 Colors)

| Block Purpose | Variable | Hex Value |
|---------------|----------|-----------|
| Background | `--block-bg` | #000000 |
| Text/Lines | `--block-text` | #FFFFFF |
| Frame/Border | `--block-frame` | #3A86FF (Azure Blue) |
| Accent/Active | `--block-accent` | #FFD166 (Golden Pollen) |
| Info | `--block-info` | #8ECAE6 (Sky Blue Light) |
| Success/Good | `--block-good` | #06D6A0 (Emerald) |
| Error/Bad | `--block-bad` | #FB5607 (Blaze Orange) |
| Focus/Highlight | `--block-focus` | #FF006E (Neon Pink) |

## Files Requiring Updates

### ✅ Completed
- [x] `/extensions/core/shared/synthwave-dos-colors.css` - **NEW FILE CREATED**

### 🔄 In Progress
- [ ] `/extensions/core/c64-terminal/c64-terminal.css`
- [ ] `/extensions/core/teletext/teletext-polaroid.css`
- [ ] `/extensions/core/font-tools/font-manager.css`

### 📋 Documentation Updates Needed
- [ ] `/extensions/core/c64-terminal/README.md`
- [ ] `/extensions/core/teletext/README-POLAROID.md`
- [ ] `/extensions/core/font-tools/README-FONT-MANAGER.md`

## Migration Strategy

### Phase 1: Core Palette Definition ✅
1. Create `/extensions/core/shared/synthwave-dos-colors.css`
2. Define all 16 colors with proper naming
3. Define 8-color block graphics subset
4. Add monochrome mode support
5. Create utility classes

### Phase 2: Extension Updates (Current)
1. **C64 Terminal**: Import shared colors, map terminal-specific variables
2. **Teletext**: Replace Polaroid variables, update color scheme
3. **Font Manager**: Update all UI colors to Synthwave DOS

### Phase 3: Testing & Documentation
1. Visual regression testing (screenshots)
2. Update all README files with new color references
3. Create migration notes for any custom extensions

## Terminal-Specific Mappings

### C64 Terminal
```css
--term-bg: var(--color-black);
--term-fg: var(--color-cyan-bright);
--term-border: var(--color-blue-bright);
--term-cursor: var(--color-cyan-bright);
--term-header: var(--color-blue-bright);
--term-status: var(--color-orange-bright);
```

### Teletext
```css
--teletext-bg: var(--color-black);
--teletext-fg: var(--color-cyan-bright);
--teletext-border: var(--color-blue-bright);
--teletext-header: var(--color-orange-bright);
--teletext-status: var(--color-cyan-bright);
```

### Font Manager
```css
--manager-bg: var(--color-blue-dark);
--manager-fg: var(--color-cyan-bright);
--manager-accent: var(--color-cyan-bright);
--manager-border: var(--color-blue-bright);
--manager-panel-bg: var(--color-black);
--manager-header-bg: var(--color-blue-bright);
--manager-header-fg: var(--color-orange-bright);
```

## Contrast Ratings (on #000000 Background)

### AAA (7:1+) - Highest Readability
- White Bright, Red Bright, Orange Bright, Yellow Bright
- Green Bright, Cyan Bright, Blue Bright, Magenta Bright

### AA (4.5:1+) - Good Readability
- Gray Light, Gray Dark, all `-dark` variants

## Breaking Changes

### CSS Variable Renames
All extensions using the old `--c64-*` or `--polaroid-*` prefixes must be updated to use the new `--color-*` prefix.

### Removed Colors
- `--c64-brown` - No direct equivalent (use `--color-orange-dark`)
- `--c64-light-red` - No direct equivalent (use `--color-red-bright`)
- `--polaroid-blue-full` - Replaced with `--color-blue-dark`

### New Colors
- `--color-magenta-dark` (#8338EC) - Blue Violet
- `--color-blue-dark` (#023047) - Deep Space Blue
- `--color-cyan-dark` (#118AB2) - Ocean Blue

## Implementation Checklist

- [x] Define global color system in shared CSS
- [x] Create 8-color block graphics subset
- [x] Add monochrome mode support
- [ ] Update C64 Terminal CSS
- [ ] Update Teletext CSS
- [ ] Update Font Manager CSS
- [ ] Test visual consistency
- [ ] Update all documentation
- [ ] Create before/after screenshots
- [ ] Commit with comprehensive message

## Future Enhancements

1. **JavaScript Color API**: Create `window.uDOS.colors` object for programmatic access
2. **Theme Switcher**: Allow runtime color scheme switching
3. **Custom Palettes**: User-defined color sets (saved to localStorage)
4. **Accessibility Mode**: Higher contrast variants for vision impairment

---

**Status**: Migration in progress (Phase 2)
**Last Updated**: 2025-11-17
**Version**: 1.0.24
