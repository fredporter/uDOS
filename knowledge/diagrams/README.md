# Technical Diagram Library

**Status:** 🔄 **IN PROGRESS** - Building SVG diagram collection
**Target:** 500+ Technical-Kinetic diagrams across 8 categories
**Current:** 80 diagrams (16.0%)

---

## 🎨 Diagram Design Philosophy

### Technical-Kinetic Style Guidelines
- **Line art:** Clean vector SVG format
- **Annotations:** Clear labels with leader lines
- **Sequential:** Step-by-step for processes
- **Cutaway views:** Internal mechanisms visible
- **Scale indicators:** Dimensions and measurements
- **Safety warnings:** Red highlights for hazards
- **Color coding:** Consistent palette (water=blue, fire=red, etc.)

### File Specifications
- **Format:** SVG (Scalable Vector Graphics)
- **Target size:** <50KB per file
- **Viewbox:** 800x600 or 1200x800 (16:10 aspect ratio)
- **Accessibility:** Text labels, not embedded images
- **Print-friendly:** High contrast, B&W compatible

---

## 📁 Diagram Categories

### Water Systems (Target: 80 diagrams, Current: 15, 18.8%)
**Location:** `knowledge/diagrams/water/`

**Completed:**
- Boiling water purification process
- Solar still construction
- Water filter cross-section
- Rainwater catchment system
- (11 more existing diagrams)

**Priority Needs:**
- Multi-barrier purification flowchart
- Ceramic filter assembly
- Well construction phases
- Stream crossing safety zones
- Water testing procedures

### Fire Structures (Target: 50 diagrams, Current: 10, 20.0%)
**Location:** `knowledge/diagrams/fire/`

**Completed:**
- Bow drill assembly
- Fire lay structures (teepee, log cabin, lean-to)
- Fire triangle diagram
- Friction fire hand positions
- (6 more existing diagrams)

**Priority Needs:**
- Tinder bundle construction
- Fire safety zones (distance markers)
- Char cloth preparation
- Coal bed preservation
- Smoke signal setup

### Shelter Designs (Target: 70 diagrams, Current: 12, 17.1%)
**Location:** `knowledge/diagrams/shelter/`

**Completed:**
- A-frame shelter construction
- Debris hut cross-section
- Tarp shelter configurations (6 types)
- Lashing techniques
- (8 more existing diagrams)

**Priority Needs:**
- Snow cave ventilation
- Shelter drainage system
- Knot diagrams (8 essential)
- Insulation layer cross-section
- Site selection decision tree

### Food Preparation (Target: 60 diagrams, Current: 10, 16.7%)
**Location:** `knowledge/diagrams/food/`

**Completed:**
- Smoking meat setup
- Food preservation methods
- Cooking fire structures
- (7 more existing diagrams)

**Priority Needs:**
- Universal Edibility Test flowchart
- Plant identification (toxic vs. edible)
- Fish trap construction
- Food storage methods
- Butchering diagrams (rabbit, fish)

### Navigation Tools (Target: 50 diagrams, Current: 8, 16.0%)
**Location:** `knowledge/diagrams/navigation/`

**Completed:**
- Compass parts and use
- Shadow stick method
- Star navigation (Northern/Southern hemisphere)
- (5 more existing diagrams)

**Priority Needs:**
- Dead reckoning process
- Topographic map reading
- Ground-to-air signal patterns
- Pace count calibration
- Route planning symbols

### Medical Procedures (Target: 80 diagrams, Current: 15, 18.8%)
**Location:** `knowledge/diagrams/medical/`

**Completed:**
- CPR hand placement
- Wound dressing layers
- Fracture splinting
- MARCH protocol flowchart
- (11 more existing diagrams)

**Priority Needs:**
- Burns assessment (1st/2nd/3rd degree)
- Tourniquet application steps
- Heimlich maneuver positions
- Shock treatment protocol
- Hypothermia progression stages

### Tool Usage (Target: 60 diagrams, Current: 6, 10.0%)
**Location:** `knowledge/diagrams/tools/`

**Completed:**
- Knife safety zones
- Axe cutting techniques
- Sharpening angles
- (3 more existing diagrams)

**Priority Needs:**
- Bow drill assembly exploded view
- Stone tool knapping process
- Rope making (reverse-wrap method)
- Basket weaving patterns
- Tool maintenance checklist flowchart

### Communication Systems (Target: 50 diagrams, Current: 4, 8.0%)
**Location:** `knowledge/diagrams/communication/`

**Completed:**
- Morse code chart
- Ground-to-air signals
- (2 more existing diagrams)

**Priority Needs:**
- Semaphore flag positions
- Mirror signal aiming technique
- Radio frequency bands
- Whistle code patterns
- Signal fire construction

---

## 🎯 Diagram Types & Templates

### Process Flowcharts
- Decision trees (if/then logic)
- Sequential steps (1→2→3→4)
- Troubleshooting guides (problem → solution)
- Safety protocols (checklists)

### Technical Illustrations
- Exploded views (assembly diagrams)
- Cross-sections (internal structure)
- Cutaway views (partial reveal)
- Scale comparisons (size reference)

### Instructional Diagrams
- Hand positions (grip, technique)
- Body positioning (stance, leverage)
- Tool usage (cutting angles, safety zones)
- Step-by-step assembly (numbered)

### Reference Charts
- Comparison tables (methods, effectiveness)
- Identification guides (plants, tracks, clouds)
- Measurement conversions (metric/imperial)
- Symbol libraries (map, signal, weather)

---

## 📊 Progress Tracking

### Overall Status: 80/500 diagrams (16.0%)

### By Complexity:
- Simple (icons, symbols): 20/100 (20%)
- Moderate (single-page instructional): 40/250 (16%)
- Complex (multi-step, exploded views): 15/100 (15%)
- Reference charts: 5/50 (10%)

### By Priority:
- **HIGH (Critical safety):** 25/100 (25%) ✅ Good
- **MEDIUM (Common tasks):** 35/250 (14%) ⚠️ Need more
- **LOW (Advanced skills):** 20/150 (13%) ⚠️ Future

---

## 🔗 Integration with Guides

### Diagram Embedding Syntax
```markdown
![Diagram Description](../diagrams/category/filename.svg)
*Figure 1: Caption describing the diagram*
```

### Cross-Referencing
- Guides link to diagrams
- Diagrams reference parent guide
- Checklists reference relevant diagrams
- Reference materials include diagram summaries

---

## 🤝 Contributing Diagrams

### Submission Guidelines
1. **SVG format only** (vector, scalable)
2. **Clean paths** (no raster images embedded)
3. **Labeled elements** (text, not cryptic symbols)
4. **Accessible** (screen reader compatible)
5. **Print-tested** (B&W legible)

### Required Elements
- [ ] Title/filename descriptive
- [ ] Scale indicator (if physical object)
- [ ] Safety warnings (if hazard present)
- [ ] Copyright/license info (CC-BY-SA 4.0)
- [ ] Source attribution (if adapted)

### Tools Recommended
- Inkscape (free, open-source SVG editor)
- Adobe Illustrator (professional)
- draw.io / diagrams.net (online, free)
- Hand-drawn → scan → vectorize (acceptable)

---

## 🎨 Color Palette Standard

### Semantic Colors
- **Water:** `#0066CC` (blue)
- **Fire:** `#CC3300` (red-orange)
- **Safety/Caution:** `#FFCC00` (yellow)
- **Danger/Stop:** `#CC0000` (red)
- **Vegetation/Food:** `#339933` (green)
- **Tools/Equipment:** `#666666` (gray)
- **Medical/First Aid:** `#CC0066` (magenta)
- **Navigation:** `#9933CC` (purple)

### Neutrals
- **Lines:** `#000000` (black, 2px)
- **Fill:** `#FFFFFF` (white) or none
- **Annotations:** `#333333` (dark gray)
- **Background:** Transparent or `#F5F5F5` (light gray)

---

## 📋 Priority Diagram Wishlist

### URGENT (Safety-Critical)
1. Tourniquet application (6 steps)
2. CPR hand placement (adult/child/infant)
3. Fire safety zones (distance markers)
4. Hypothermia progression stages
5. Water purification flowchart (decision tree)

### HIGH PRIORITY (Common Tasks)
6. Bow drill assembly (exploded view)
7. Debris hut cross-section (insulation layers)
8. Universal Edibility Test flowchart
9. Compass declination adjustment
10. Knot library (8 essential knots)

### MEDIUM PRIORITY (Skill Development)
11. Stone tool knapping sequence
12. Basket weaving patterns (4 types)
13. Fish trap construction
14. Snow cave ventilation system
15. Signal mirror aiming technique

---

## Related Resources

**Style Guides:**
- [[dev/THEME_GUIDE]] - UI design principles
- [[wiki/CSS-FRAMEWORKS-GUIDE]] - Visual consistency

**Content Integration:**
- [[knowledge/README]] - Master knowledge index
- [[knowledge/checklists/README]] - Checklist library
- [[knowledge/reference/]] - Quick reference materials

---

*Last updated: v1.4.0 Week 2 | 80 diagrams | 16.0% complete | Target: 500*
