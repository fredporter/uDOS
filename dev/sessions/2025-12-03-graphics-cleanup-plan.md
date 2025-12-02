# Graphics System Cleanup Plan
**Date**: December 3, 2025
**Status**: Planning
**Goal**: Consolidate and clean up old ASCII/teletext code after v1.1.15 improvements

---

## Current State Analysis

### Redundant Systems Found

**1. Dual GENERATE Commands**
- ❌ **OLD**: `diagram_handler.py._generate()` - Lines 355-550 (195 lines)
  - Calls Gemini for text, SVG, ASCII, teletext generation
  - Overlaps with new `generate_handler.py` functionality
  - Used syntax: `DIAGRAM GENERATE <file> [--crawl] [--style]`

- ✅ **NEW**: `generate_handler.py` (871 lines, enhanced in v1.1.15)
  - Unified GENERATE command with --survival flag
  - Optimized Nano Banana pipeline
  - Better organized, tested, documented
  - Used syntax: `GENERATE SVG --survival <category>/<prompt>`

**Decision**: Remove GENERATE from `diagram_handler.py`, keep it focused on library browsing (LIST, SEARCH, SHOW, RENDER, COPY, EXPORT, TYPES).

---

**2. Duplicate Graphics Directories**

```
OLD Structure (core/data/graphics/):
├── blocks/
│   ├── teletext.json          # Old teletext blocks
│   ├── borders.json           # Old border definitions
│   ├── patterns.json          # Old patterns
│   ├── box_drawing.json       # Old box drawing
│   └── maps.json              # Old map tiles
├── templates/                 # Old diagram templates
├── compositions/              # Pre-rendered examples
└── README.md                  # Old system documentation

NEW Structure (core/data/diagrams/):
├── blocks/                    # 25 block-shaded diagrams (v1.1.15)
├── plain/                     # 26 plain ASCII diagrams (v1.1.15)
├── mermaid/                   # Mermaid templates (v1.1.15)
└── templates/                 # Survival prompt templates (v1.1.15)
    ├── survival_prompts.json
    ├── style_technical_kinetic.json
    ├── style_hand_illustrative.json
    └── style_hybrid.json
```

**Observations**:
- `core/data/graphics/` is old content generation system
- `core/data/diagrams/` is new refined structure
- Some overlap in block definitions
- Old README explains outdated GraphicsCompositor approach

**Decision**:
- Keep `core/data/graphics/blocks/` for now (used by map rendering)
- Archive old `graphics/templates/` and `graphics/compositions/`
- Update `graphics/README.md` to reference new system
- Eventually consolidate all blocks into unified library

---

**3. Teletext Systems**

**Active & Needed:**
- ✅ `core/output/teletext_renderer.py` (512 lines)
  - Used by `extensions/play/commands/map_handler.py`
  - TeletextMapIntegration class for map rendering
  - HTML/CSS generation for web display
  - **Keep** - Still actively used

- ✅ `core/ui/teletext_prompt.py`
  - Used by file pickers and UI components
  - TeletextPromptStyle, TeletextBlocks classes
  - **Keep** - UI dependency

- ✅ `extensions/core/teletext/` (Web extension)
  - HTML editor, web server, font files
  - Standalone teletext editor
  - **Keep** - Separate web tool

**Deprecated/Questionable:**
- ❌ `diagram_handler.py` teletext generation methods
  - Lines 490-500: `gen.generate_teletext()`
  - Duplicates web extension functionality
  - **Remove** from diagram_handler

---

**4. ASCII Systems**

**Active & Needed:**
- ✅ `core/services/ascii_generator.py` (450 lines, v1.1.15)
  - Unicode box-drawing, refined style
  - 9 generation methods
  - Integrated with generate_handler
  - **Keep** - New refined system

**Questionable:**
- ⚠️ `diagram_handler.py` ASCII generation
  - Lines 486-490: `gen.generate_ascii()`
  - May overlap with ascii_generator.py
  - Need to verify if gemini_generator.generate_ascii() is different

---

## Cleanup Actions

### Phase 1: Remove Redundant GENERATE Command ✅ READY

**Files to modify:**
1. `core/commands/diagram_handler.py`
   - Remove `_generate()` method (lines ~355-550)
   - Remove `_generate_single()` method
   - Remove `_generate_batch()` method
   - Remove `_generate_help()` method
   - Update handle() to remove 'GENERATE' routing
   - **Result**: ~200 lines removed, focus on library browsing

2. Update command help text
   - Remove GENERATE from help output
   - Update examples to reference new GENERATE SVG command

**Testing:**
```bash
# Verify old command removed
DIAGRAM GENERATE test.md  # Should fail with helpful error

# Verify new command works
GENERATE SVG --survival water/purification_flow --pro  # Should work

# Verify library commands still work
DIAGRAM LIST
DIAGRAM SHOW water_purification
DIAGRAM TYPES
```

---

### Phase 2: Archive Old Graphics System ✅ READY

**Actions:**
1. Create archive directory
   ```bash
   mkdir -p core/data/graphics/.archive
   ```

2. Move deprecated files
   ```bash
   mv core/data/graphics/templates/ core/data/graphics/.archive/
   mv core/data/graphics/compositions/ core/data/graphics/.archive/
   ```

3. Update README.md
   - Note transition to new `core/data/diagrams/` system
   - Reference v1.1.15 improvements
   - Keep blocks/ directory (still used by maps)

4. Create migration note
   ```markdown
   # DEPRECATED - See core/data/diagrams/

   This graphics system (v1.1.1) has been superseded by the refined
   diagram system in v1.1.15.

   - Old: GraphicsCompositor → JSON templates → compositions
   - New: ascii_generator.py → Unicode box-drawing → direct generation

   The blocks/ directory remains active for map rendering.
   For new diagrams, use:
   - GENERATE ASCII (for programmatic generation)
   - GENERATE SVG --survival (for AI-generated diagrams)
   ```

---

### Phase 3: Update Documentation ✅ READY

**Files to update:**

1. **wiki/Graphics-System.md**
   - Add v1.1.15 updates section
   - Document new ascii_generator.py
   - Document survival diagram templates
   - Note deprecated GraphicsCompositor

2. **wiki/Command-Reference.md**
   - Remove DIAGRAM GENERATE
   - Emphasize GENERATE SVG with --survival flag
   - Update ASCII generation examples

3. **dev/roadmap/teletext.md**
   - Check if still relevant
   - Merge useful content into main ROADMAP
   - Archive if obsolete

---

### Phase 4: Code Quality Improvements 🔜 FUTURE

**Potential refactoring (not urgent):**

1. **Consolidate block libraries**
   - Merge `core/data/graphics/blocks/*.json` into single unified library
   - Used by both map rendering and ASCII generation
   - Eliminate duplication

2. **Unified ASCII rendering**
   - Check if `gemini_generator.generate_ascii()` duplicates `ascii_generator.py`
   - Standardize on one approach
   - Ensure consistency

3. **Teletext unification**
   - Web extension vs renderer vs prompt styles
   - Clarify boundaries and responsibilities
   - Document integration points

---

## Migration Impact Assessment

### Low Risk (Do Now)
- ✅ Remove DIAGRAM GENERATE (covered by new GENERATE)
- ✅ Archive old templates/compositions (not actively used)
- ✅ Update documentation (helps users)

### Medium Risk (Test First)
- ⚠️ Consolidate block libraries (map rendering dependency)
- ⚠️ Update graphics README (may break references)

### High Risk (Future)
- ⚠️ Refactor teletext systems (multiple integrations)
- ⚠️ Consolidate ASCII generation (verify no regressions)

---

## Testing Checklist

After cleanup:

### Functionality Tests
- [ ] DIAGRAM LIST still works
- [ ] DIAGRAM SEARCH <query> finds diagrams
- [ ] DIAGRAM SHOW <name> displays content
- [ ] DIAGRAM RENDER works
- [ ] DIAGRAM COPY to panels
- [ ] DIAGRAM EXPORT to files
- [ ] DIAGRAM TYPES lists categories

### Removed Features
- [ ] DIAGRAM GENERATE fails gracefully with helpful message
- [ ] Users directed to new GENERATE SVG command

### New Features Unchanged
- [ ] GENERATE SVG --survival still works
- [ ] GENERATE ASCII works
- [ ] Test suite passes (23/23 tests)

### Integration Tests
- [ ] Map rendering still uses teletext_renderer
- [ ] UI components still use teletext_prompt
- [ ] File pickers work
- [ ] Web teletext extension independent

---

## Implementation Steps

### Step 1: Remove DIAGRAM GENERATE
```python
# In diagram_handler.py

# Remove these methods:
# - _generate()
# - _generate_single()
# - _generate_batch()
# - _generate_help()

# Update handle() method:
def handle(self, command: str, params: str = "") -> str:
    """Handle DIAGRAM commands"""
    args = params.strip().split() if params.strip() else []

    if not args:
        return self._help()

    action = args[0].upper()

    if action == 'LIST':
        return self._list(args[1:])
    elif action == 'SEARCH':
        return self._search(args[1:])
    # ... other commands ...
    # REMOVE: elif action == 'GENERATE':
    #     return self._generate(args[1:])
    else:
        return f"❌ Unknown DIAGRAM command: {action}\n\n" + self._help()
```

### Step 2: Add Deprecation Notice
```python
# In diagram_handler.py, add to handle():

if action == 'GENERATE':
    return """❌ DIAGRAM GENERATE has been deprecated in v1.1.15

Use the improved GENERATE command instead:

  GENERATE SVG --survival <category>/<prompt> [--pro|--strict]
  GENERATE ASCII <type> <content>

Examples:
  GENERATE SVG --survival water/purification_flow --pro
  GENERATE ASCII box "Water Sources" 40 5

See: GENERATE --help
"""
```

### Step 3: Archive Old Files
```bash
#!/bin/bash
# Script: cleanup_old_graphics.sh

echo "📦 Archiving old graphics system..."

# Create archive directory
mkdir -p core/data/graphics/.archive

# Move old templates and compositions
mv core/data/graphics/templates/ core/data/graphics/.archive/
mv core/data/graphics/compositions/ core/data/graphics/.archive/

# Create deprecation notice
cat > core/data/graphics/.archive/README.md << 'EOF'
# Graphics System Archive (v1.1.1)

**Deprecated**: December 3, 2025
**Replaced by**: core/data/diagrams/ (v1.1.15)

This directory contains the old graphics generation system based on
GraphicsCompositor and JSON templates. It has been superseded by:

- `core/services/ascii_generator.py` - Unicode box-drawing
- `core/data/diagrams/` - Refined diagram library
- `GENERATE SVG --survival` - AI-generated survival diagrams

The `blocks/` directory in the parent folder remains active for
map rendering via teletext_renderer.py.

## Migration Path

Old:
```python
from core.services.graphics_compositor import GraphicsCompositor
gc = GraphicsCompositor()
flow = gc.create_flow(['Step 1', 'Step 2'])
```

New:
```bash
GENERATE ASCII flow "Step 1,Step 2,Step 3"
```

Or for AI-generated diagrams:
```bash
GENERATE SVG --survival water/purification_flow --pro
```
EOF

echo "✅ Archive complete"
```

### Step 4: Update Documentation
- Update wiki/Graphics-System.md with v1.1.15 changes
- Update wiki/Command-Reference.md to remove DIAGRAM GENERATE
- Add migration notes to dev/CHANGELOG.md

---

## Success Criteria

- ✅ No functionality lost (all features available via new commands)
- ✅ Code reduced by ~200 lines (diagram_handler cleanup)
- ✅ Clear migration path documented
- ✅ All tests passing
- ✅ No breaking changes to active systems (maps, UI, teletext extension)

---

## Timeline

**Immediate (Today):**
- Remove DIAGRAM GENERATE from diagram_handler.py
- Add deprecation notice with helpful migration message
- Update command help text

**Short-term (This week):**
- Archive old templates/compositions
- Update documentation
- Create migration guide

**Long-term (v1.1.16+):**
- Consolidate block libraries
- Unify ASCII rendering approaches
- Refactor teletext systems

---

## Related Work

- v1.1.15 Task 4: ASCII Graphics Refinement (completed)
- v1.1.15 Task 5: Nano Banana Optimization (completed)
- core/services/ascii_generator.py (new refined system)
- Test suite: memory/ucode/test_ascii_generator.py

---

**Next Session**: Execute Phase 1 (Remove DIAGRAM GENERATE)
