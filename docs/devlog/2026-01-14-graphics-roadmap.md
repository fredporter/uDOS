# Graphics Architecture & Hardcoding Roadmap Update

**Date:** 2026-01-14  
**Status:** Documentation Complete, Implementation Ready  
**Session:** TUI Audit + Graphics Architecture Clarification

---

## 🎯 Key Decisions Made

### Graphics: Three-Tier Strategy Clarified

**Principle:** Markdown-native is single source of truth

```
Markdown (flowchart.js | Mermaid | Marp)
    ↓
    ├→ TUI: ASCII-Teletext (Graphics Service or fallback)
    ├→ App: SVG (Graphics Service + Tauri)
    └→ Export: HTML/PDF (Marp CLI)
```

**Critical Insight:**
- **TUI cannot render SVG** (no graphics capability)
- **TUI gets ASCII fallback always**
- **ASCII-Teletext blocks MUST map semantically to SVG**
  - Colors encode same meaning
  - Shapes mean same thing
  - Layout communicates same flow

**Example:**
```
Flowchart source: Decision with Yes/No paths

TUI (ASCII):
┌─────────┐
│ Start   │
└────┬────┘
   ◊─┬─◊
   │ │
Green│Red    (Colors matter in TUI)
   │ │
┌──┴─┴──┐
│Action │Error
└───────┘

App (SVG):
Same layout, but with:
- Rounded corners
- Shadows
- Better spacing
- Same green/red arrows
- Same semantic meaning
```

### API: Graphics Service is the Bridge

- **Port 5555** (central graphics processor)
- Handles all format conversion
- 5 rendering formats: ascii, teletext, svg, sequence, flow
- Offline-capable (templates cached locally)
- Python client: `core/services/graphics_service.py`

### Box Drawing: Will Consolidate

Current state: **3 implementations** (panel_templates.py, graphics.py, block_graphics.py)

Plan: Consolidate to single source in `panel_templates.py`, archive duplicates

---

## 📋 Updated Roadmap

### Now (This Week)

✅ **Complete:**
- Graphics Architecture spec created
- Hardcoded values audit completed
- TUI consolidation plan created
- VS Code settings enhanced for tracking

📋 **This Week (Next Actions):**
1. **Phase 1: Box Drawing** (2-3 hours)
   - Consolidate 3 implementations → 1 source
   - Update 19 files using box drawing
   - Archive duplicates

2. **Phase 2: Progress Bars** (2 hours)
   - Keep progress_indicators.py as primary
   - Remove 3 duplicates from graphics.py, output_pacer.py

3. **Phase 3: Viewport Detection** (3-4 hours)
   - Create viewport_utils.py
   - Replace 20+ hardcoded dimensions

4. **Graphics Service Integration** (2 hours)
   - Verify port 5555 registration
   - Test all 5 rendering formats
   - Document API endpoints

5. **Teletext Mapping Docs** (2 hours)
   - Create mapping spec for ASCII→Block→SVG alignment
   - Document color semantics

### Next (This Month)

**Total:** ~20 hours over 2 weeks

- Box drawing consolidation (Phase 1)
- Progress bar consolidation (Phase 2)
- Viewport utilities (Phase 3)
- Graphics Service verification
- DIAGRAM command integration in TUI
- DiagramRenderer.svelte in App
- TUI-App consistency testing

**Success Metrics:**
- ✅ Zero hardcoded dimensions in TUI
- ✅ Single box drawing module
- ✅ Graphics tiers working (Markdown → ASCII → SVG)
- ✅ ASCII-Teletext aligned with SVG output
- ✅ DIAGRAM command functional
- ✅ DiagramRenderer component working

---

## 📚 New Documentation Created

1. **[docs/specs/graphics-architecture.md](../specs/graphics-architecture.md)**
   - Complete three-tier system explanation
   - Tier 1: Markdown source (flowchart.js, Mermaid, Marp)
   - Tier 2: ASCII-Teletext for TUI
   - Tier 3: SVG for App/Desktop/Web
   - Semantic alignment requirements
   - Color semantics mapping

2. **[docs/specs/graphics-service-integration.md](../specs/graphics-service-integration.md)**
   - Data flow diagrams
   - API endpoints documentation
   - Python client examples
   - Svelte component usage
   - Error handling patterns
   - Testing strategies

3. **[TUI-CONSOLIDATION-TODO.md](../../TUI-CONSOLIDATION-TODO.md)**
   - Phase-by-phase implementation plan
   - Risk assessment and mitigation
   - Timeline and deliverables

4. **[HARDCODED-VALUES-AUDIT.md](../../HARDCODED-VALUES-AUDIT.md)**
   - Complete audit of 20+ hardcoded values
   - Files and line numbers
   - Replacement strategy

---

## 🔑 Key Insights

### 1. Graphics Realm Clarity
- **TUI = ASCII only** (no SVG capability)
- **App = SVG primary** (Tauri webview)
- **Fallback path = Always ASCII** (graphics service unavailable)
- **Escalation path = SVG** (when service available)

### 2. Markdown as Source
- All diagrams derive from markdown
- Single version-controlled source
- Can generate multiple formats
- Portable and editable

### 3. Semantic Equivalency
- ASCII version ≈ SVG version (same meaning)
- Colors encode semantics (green=success, red=error)
- Block characters map to shapes
- Layout communicates same flow/structure

### 4. API as Bridge
- Graphics Service on port 5555
- Central rendering authority
- Handles format conversion
- Fallback for offline use

### 5. No Hardcoding
- Terminal dimensions: Use `shutil.get_terminal_size()`
- Box drawing: Use consolidated module
- Progress bars: Use unified renderer
- Viewport heights: Calculate dynamically

---

## 🚀 Next Steps (For User)

1. **Review** the three new spec documents
2. **Approve** the three-tier graphics strategy
3. **Begin** Phase 1 (box drawing consolidation) when ready
4. **Test** each phase before moving to next

**Recommended Sequence:**
1. Phase 1: Box Drawing (impacts 19 files)
2. Phase 2: Progress Bars (impacts 4 files)
3. Phase 3: Viewport Utils (impacts 20+ files)
4. Then: Graphics integration
5. Finally: TUI-App consistency

---

## 📊 Metrics Before → After

| Metric | Before | Target | Status |
|--------|--------|--------|--------|
| Box drawing implementations | 3 | 1 | 📋 Planned |
| Progress bar implementations | 4 | 1 | 📋 Planned |
| Hardcoded dimensions | 20+ | <5 | 📋 Planned |
| Files needing consolidation | 25+ | 0 | 📋 Planned |
| Graphics tiers documented | 0 | 3 | ✅ Done |
| Port registry updated | Partial | Complete | 📋 Planned |

---

## 🎨 Graphics Architecture Visualization

```
Knowledge Base (Version-Controlled)
├── Markdown diagrams (source of truth)
│   ├── flowchart.js
│   ├── Mermaid
│   └── Marp presentations
│
├── Exported outputs
│   ├── ASCII (TUI rendering)
│   ├── SVG (App rendering)
│   └── HTML5/PDF (export)
│
└── Catalog
    └── Templates + examples
    
Rendering Paths:
1. TUI: Markdown → Graphics Service → ASCII → Terminal
2. App: Markdown → Graphics Service → SVG → Tauri webview
3. Export: Markdown → Marp CLI → HTML5/PDF → File
4. Offline: Markdown → Fallback generator → ASCII → Cache

API/Service:
- Graphics Service (port 5555)
  - render/ascii, render/teletext, render/svg
  - render/sequence, render/flow
  - templates/catalog endpoints
```

---

## 📝 Documentation Notes

### For Core Team
- Check [docs/specs/graphics-architecture.md](../specs/graphics-architecture.md) for TUI rendering strategy
- Use `core.services.graphics_service.GraphicsService` for all diagram rendering
- Handle service unavailability gracefully (fallback to ASCII)

### For App Team
- Check [docs/specs/graphics-service-integration.md](../specs/graphics-service-integration.md) for data flow
- Use `DiagramRenderer.svelte` for embedding diagrams
- Verify SVG semantic alignment with TUI ASCII version

### For API Team
- Ensure Graphics Service (port 5555) is properly documented
- Verify all 5 rendering formats are functional
- Test offline fallback scenario

---

## 🔗 Related Issues Tracked

Via VS Code TODO Tree (integrated in settings):

**HARDCODED Tags:**
- `file_browser.py:392` - `viewport_height = 15`
- 19 other files with hardcoded dimensions

**DUPLICATE Tags:**
- `graphics.py` - BoxChars class (will archive)
- `output_pacer.py` - progress_bar method (will archive)

**MODULARIZE Tags:**
- Box drawing (consolidate to panel_templates)
- Progress bars (consolidate to progress_indicators)
- Terminal detection (create viewport_utils)

---

## ✅ Session Summary

**Accomplishments:**
1. ✅ Completed hardcoded values audit (20+ issues found)
2. ✅ Documented three-tier graphics architecture
3. ✅ Created Graphics Service integration guide
4. ✅ Updated roadmap with phases
5. ✅ Enhanced VS Code workspace settings
6. ✅ Created implementation plan with timelines

**Deliverables:**
- 4 new specification documents
- Updated roadmap
- Enhanced workspace settings
- Comprehensive implementation roadmap
- Audit reports with specific actions

**Quality Tracked:**
- TODO tags visible in VS Code
- Phase-by-phase implementation guidance
- Risk assessment and mitigation
- Success metrics defined

---

**Status:** Ready for implementation  
**Confidence:** High (clear architecture, low-risk phased approach)  
**Owner:** Core + App + API teams  
**Version:** Alpha v1.0.2.0

---

*Last Updated: 2026-01-14*  
*Session: Hardcoding Audit + Graphics Architecture Clarification*  
*Next: Begin Phase 1 (Box Drawing Consolidation)*
