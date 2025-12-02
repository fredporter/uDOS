# Graphics System Archive (v1.1.1-v1.1.14)

**Status:** ARCHIVED (replaced in v1.1.15)
**Date Archived:** December 2025

## Contents

This directory contains the old graphics generation system that was active from v1.1.1 through v1.1.14. These files are preserved for reference but are no longer used by the active system.

### Archived Files

- **templates/** - Old diagram templates (flow, tree, grid, hierarchy)
- **compositions/** - Pre-rendered example diagrams
- **components.json** - Old component definitions

### Why Archived?

In v1.1.15, the graphics system was significantly improved:

1. **Replaced GraphicsCompositor** with refined diagram generation
2. **New directory structure** - `core/data/diagrams/` (blocks/, plain/, mermaid/)
3. **Better organization** - Separated survival diagrams from general graphics
4. **Improved templates** - `survival_prompts.json` with 13 optimized prompts
5. **Style guides** - Professional, Strict, Refined modes
6. **Better testing** - 23 comprehensive tests

### Migration Path

Old functionality is now available via:

```bash
# Old way (deprecated)
DIAGRAM GENERATE source.md --style technical

# New way (v1.1.15+)
GENERATE SVG --survival water/purification_flow --pro
GENERATE ASCII box "Water Sources" 40 5
```

### What's Still Active?

- **blocks/** directory - Still contains block libraries for map rendering
- **teletext_renderer.py** - Still used by map_handler.py for map visualization
- **teletext_prompt.py** - Still used by UI components

### Reference Documentation

See these for the current system:

- `core/data/diagrams/README.md` - New diagram system
- `wiki/Graphics-System.md` - Updated documentation
- `dev/sessions/2025-12-03-graphics-cleanup-plan.md` - Cleanup rationale

---

**Note**: These files are kept for historical reference only. Do not use in new development.
