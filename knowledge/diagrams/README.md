# Technical Diagram Library

**Status:** 🔄 **IN PROGRESS** - Building multi-format diagram collection
**Design Systems:**
- **SVG:** Mac OS System 1 (1984) bitmap patterns
- **ASCII:** C64 PetMe/PETSCII character set ✅ NEW
- **Teletext:** WST mosaic blocks (40×25) ✅ NEW
**Target:** 500+ diagrams across 8 categories + multi-format examples
**Current:** 68 total (51 SVG + 13 ASCII + 4 Teletext) - 13.6%

**Recent Update:** Nov 25, 2025 - Batch generated 15 new diagrams (shelter, food, fire, navigation)---

## 🎨 Multi-Format Design System (v1.4.0)

### NEW: Three Visual Formats

**1. ASCII Art (Terminal/CLI)**
- Character Set: C64 PetMe/PETSCII (UTF-8)
- Dimensions: 80×24 (standard terminal)
- Characters: ┌┐└┘├┤┬┴┼─│ (boxes), ░▒▓ (shading), ≈∙· (flow)
- Output: `.txt` files
- Use Cases: CLI help, terminal documentation, quick reference

**2. Teletext Graphics (Web)**
- Format: HTML with WST mosaic blocks
- Dimensions: 40×25 (Teletext standard)
- Colors: 8-color WST palette (RGBCMYW + Black)
- Blocks: █ (solid), ▄ (half)
- Output: `.html` files with inline CSS
- Use Cases: Retro web UI, chunky icons, nostalgic maps

**3. SVG Diagrams (Scalable)**
- **Technical-Kinetic:** Geometric precision, monochrome
- **Hand-Illustrative:** Organic sketchy style
- Output: `.svg` files (<50KB)
- Use Cases: Documentation, technical guides, educational content

### Example Files (Generated Nov 25, 2025)
- `water_filter_ascii.txt` (1.3 KB) - ASCII art water filter
- `heart_teletext.html` (4.3 KB) - Teletext heart icon
- `fire_triangle_technical.svg` (2.0 KB) - SVG fire safety triangle
- `tree_organic.svg` (2.1 KB) - SVG tree with roots

**See:** `/extensions/core/ok-assist/EXAMPLES.md` for complete visual gallery

---

## 🎨 Technical-Kinetic Design Style (SVG - Formal Specification)

### Style Name: Technical-Kinetic

**Rationale:** Merge structural clarity with detailed, expressive flow for standardized, objective reference documents

### Core Principles

**Structure:** Clean geometric forms (circles, rectangles, triangles)
- Consistent primary line weight: **1.5px**
- Design Reference: **Mid-Century Modern** graphic simplicity
- Sharp, precise edges with minimal decoration

**Flow & Connection:** Exaggerated curved tubes/conduits, gears, levers implying kinetic chain reactions
- Design Reference: **Rube Goldberg Machine** aesthetic
- Dynamic directional flow showing process movement
- Mechanical emphasis on cause-and-effect relationships

**Typography:** Clean geometric sans-serif (Arial/Helvetica), text treated as geometric shapes
- Design Reference: **Swiss Style / Bauhaus** typographic influence
- Text as editable SVG elements (NOT converted to paths)
- Consistent font sizing: Title 16-24px, Labels 10-14px, Annotations 8-10px

**General Aesthetic:** **MONOCHROME PALETTE** (black/white/grays), fully vector-based for infinite scalability
- Design Reference: **Mac OS System 1 (1984)** - bitmap patterns + clean Swiss typography + system UI
- **MONOCHROME ONLY** - Black `#000000`, White `#FFFFFF`, Solid grays `#1A1A1A-#E6E6E6`
- **BITMAP PATTERNS** - 17 Mac OS System 1 patterns for texture effects
- **UI COMPONENTS** - Windows, buttons, dialogs, menus from system.css (Apple HI Guidelines)
- **MIXED APPROACH** - Solid grays for gradients, patterns for texture, UI elements for structure

**Purpose:** Instructive/illustrative only, **NOT decorative**

---

## 📐 Mac OS System 1 Pattern Library

**Design System:** Classic Mac OS System 1 (1984) bitmap patterns
**Style:** Bold, geometric, pixel-perfect 8×8 patterns
**Font:** Generic monospace (no external dependencies)
**Strokes:** 2-3px bold lines (Mac OS aesthetic)

### Grayscale Patterns (7 patterns)

Bitmap density-based toning (NOT opacity or solid grays):

- **white** (0%): Pure backgrounds, empty areas, highlights
- **gray-12** (12.5%): Very light tint, subtle highlights - single pixel per 8×8
- **gray-25** (25%): Light backgrounds, soft shading - sparse checkerboard
- **gray-37** (37.5%): Light-medium tone, gentle gradients - diagonal sparse
- **gray-50** (50%): Balanced mid-tone, neutral areas - dense checkerboard
- **gray-62** (62.5%): Medium-dark shading - inverse diagonal
- **gray-75** (75%): Dark backgrounds, heavy shadows - inverse checkerboard
- **gray-87** (87.5%): Very dark, near-black areas - black with white dots
- **black** (100%): Solid black, high-contrast elements

**Implementation:** 8×8 pixel bitmap patterns using `<rect>` elements

### Texture Patterns (10 patterns)

Bold geometric 8×8 bitmap textures for material representation:

#### Structural Patterns
- **brick**: Offset rectangular blocks - masonry, stone walls, structural building
- **diagonal**: Bold diagonal lines - directional flow, structural elements, metal
- **cross-hatch**: Bold grid pattern - very dense materials, cast iron, metal grilles
- **horizontal**: Bold horizontal bars - layered materials, stratification, sediment
- **vertical**: Bold vertical bars - wood grain, columnar structures, vertical barriers

#### Organic/Decorative Patterns
- **dots**: Regular dot grid - soft materials, skin, clouds, atmospheric effects
- **scales**: Interlocking semicircle arcs - fish scales, roof tiles, armor, overlapping layers
- **grid**: Single-pixel grid lines - technical drawings, measurement grids, coordinates
- **waves**: Blocky wave pattern - water, organic flow, undulating surfaces
- **herringbone**: Zigzag weave pattern - decorative elements, fancy textiles, premium materials

**Total: 17 patterns** (7 grayscale + 10 textures)

### Design Philosophy

**Bold & Clear (Mac OS System 1 Aesthetic):**
- Thick stroke weights: 2-3px for primary lines, 1.5px secondary
- High contrast between elements
- Sharp pixel-perfect edges (no anti-aliasing)
- Geometric grid-based layout

**Pattern Usage Rules:**
- ✅ Use solid grays (#1A1A1A-#E6E6E6) for smooth gradients
- ✅ Use bitmap patterns for texture effects
- ✅ Generic monospace font for text
- ✅ Align to pixel boundaries when possible
- ✅ Combine solid fills and patterns for depth
- ❌ NO opacity or transparency effects

**Material Mapping Examples:**

*Layered Filter System:*
- Cloth filter → `cross-hatch` (fine mesh)
- Charcoal layer → `gray-75` (dense, dark carbon)
- Sand layer → `gray-37` (medium density particles)
- Gravel layer → `dots` (coarse particles)

*Structural Elements:*
- Metal/tools → `cross-hatch` or `diagonal`
- Stone/masonry → `brick` or `scales`
- Wood/timber → `vertical` or `horizontal`
- Glass/water → `gray-25` or `gray-37`

See [Mac OS Patterns Guide](../../dev/tools/MAC-OS-PATTERNS-GUIDE.md) for complete documentation.

---

## 📐 Legacy Pattern Documentation (v1.0)

<details>
<summary>Previous Woodcut/Engraving Pattern System (Click to expand)</summary>

### Core Pattern Categories

#### Grayscale Patterns (Pattern-Based Toning)
Grayscale tones achieved through **pattern density**, not opacity or hex colors:

- **solid-black:** Pure `#000` fill (for maximum contrast elements like warning boxes)
- **gray-90:** 90% black (near-black, reverse stipple - black bg + white dots)
- **gray-75:** 75% black (very dense cross-hatch)
- **gray-60:** 60% black (dense stipple with 4 dots per 4x4px)
- **gray-50:** 50% black (medium cross-hatch diagonal)
- **gray-40:** 40% black (medium stipple with 3 dots per 6x6px)
- **gray-25:** 25% black (light stipple with 2 dots per 8x8px)
- **gray-10:** 10% black (very light stipple, 1 dot per 10x10px)

**Usage:** Table headers, highlights, background shading, data visualization bars

#### 4 Mandatory Texture Patterns (CRITICAL - NO SOLID FILLS)

#### 1. Hatching/Cross-Hatching
- **Pattern:** Parallel or crossed lines at 45° angles
- **Line weight:** 0.3px (light)
- **Spacing:** 2-5px between lines (density controls tone)
- **Use Cases:** Metal/Mechanical components (gears, pipes, Rube Goldberg elements, tools)
- **SVG Implementation:** `<pattern id="hatch">` with rotated line elements

#### 2. Stipple/Dot Density
- **Pattern:** Uniform dots in grid or random distribution
- **Dot size:** 0.5-1px circles
- **Spacing:** 3-8px between dots (density controls tone)
- **Use Cases:** Soft shading/atmospheric fields (clouds, gas, subtle gradients, smoke)
- **SVG Implementation:** `<pattern id="stipple">` with circle elements

#### 3. Vector Wavy Lines
- **Pattern:** Repeating abstract, concentric or wavy lines
- **Line weight:** 0.3px
- **Spacing:** 2-4px between waves
- **Use Cases:** Organic/natural materials (woodgrain, stone, fabric, vegetation)
- **SVG Implementation:** `<pattern id="waves">` with curved path elements

#### 4. Circular/Undulating Lines (Topographic)
- **Pattern:** Smoothly flowing concentric or parallel curved lines
- **Line weight:** 0.3px
- **Spacing:** 2-5px between lines
- **Use Cases:** Environmental fields (water, terrain, data streams, topography, elevation)
- **SVG Implementation:** `<pattern id="topo">` with concentric circle/path elements

---

## 🎨 Creative Pattern Variations (Woodcut/Engraving Style)

**Purpose:** Enhance visual richness while maintaining monochrome Technical-Kinetic standards

### Artistic Patterns (9 Additional Types)

#### 5. Woodcut Texture
- **Pattern:** Irregular organic wavy lines mimicking wood grain
- **Line weight:** 0.25-0.3px varying
- **Use Cases:** Wood materials, natural textures, rustic elements, organic surfaces
- **Aesthetic:** Historical woodcut/block print style

#### 6. Engraving Texture
- **Pattern:** Fine parallel curved lines, delicate and flowing
- **Line weight:** 0.2px (finest)
- **Use Cases:** Fine detail work, elegant shading, historical technical illustrations
- **Aesthetic:** Copper plate engraving, banknote style

#### 7. Brick/Stone Pattern
- **Pattern:** Rectangular offset blocks with mortar gaps
- **Line weight:** 0.4px
- **Use Cases:** Masonry, stone walls, structural building, foundations
- **Aesthetic:** Architectural technical drawing

#### 8. Fabric Weave
- **Pattern:** Crossed thin lines creating textile appearance
- **Line weight:** 0.15px (ultra-fine)
- **Use Cases:** Cloth, fabric, woven materials, basketry, rope texture
- **Aesthetic:** Textile diagram, material science

#### 9. Radial Burst
- **Pattern:** Lines radiating from center point (sunburst)
- **Line weight:** 0.25-0.3px
- **Use Cases:** Energy, radiation, heat source, attention focus, explosive force
- **Aesthetic:** Vintage advertisement, emphasis marker

#### 10. Scales/Feathers
- **Pattern:** Overlapping arcs creating fish scale effect
- **Line weight:** 0.3px
- **Use Cases:** Fish/reptile scales, roof tiles, armor, protective layers, overlapping elements
- **Aesthetic:** Natural history illustration

#### 11. Rain/Motion Lines
- **Pattern:** Diagonal parallel lines suggesting movement
- **Line weight:** 0.25px
- **Use Cases:** Rain, wind direction, speed/movement, directional flow
- **Aesthetic:** Comic book style motion, manga effects

#### 12. Concentric Circles
- **Pattern:** Ripple circles from center (target/bullseye)
- **Line weight:** 0.3px
- **Use Cases:** Water ripples, sound waves, impact zones, targets, radar
- **Aesthetic:** Scientific diagram, physics illustration

#### 13. Whorl/Fingerprint
- **Pattern:** Organic spiral curves (fingerprint-like)
- **Line weight:** 0.25px
- **Use Cases:** Organic flow, identity markers, natural spirals, growth patterns
- **Aesthetic:** Forensic diagram, biometric illustration

---

## 🖌️ Creative Composition Techniques

### Woodcut/Engraving Aesthetic

**Line Weight Variation:**
- Fine detail: 0.2px (engraving texture, delicate features)
- Standard: 0.3px (most texture patterns)
- Medium: 1.0px (secondary outlines)
- Bold: 1.5px (primary subject outlines, emphasis)

**Pattern Layering:**
- ✅ **Allowed:** Combine 2 contrasting patterns (e.g., stipple background + hatch foreground)
- ❌ **Forbidden:** More than 2 layers (causes visual noise)
- **Rule:** Background pattern must be lighter density than foreground

**Dramatic Contrast:**
- Use solid black (#000) for maximum impact areas
- Surround dark elements with white space for breathing room
- Create chiaroscuro effect with dense cross-hatch adjacent to pure white

### Visual Hierarchy

**Three-Tier Depth System:**
1. **Foreground** (main subject): Bold 1.5px outlines + detailed pattern fills
2. **Midground** (context): 1.0px lines + medium pattern density
3. **Background** (environment): Light patterns (gray-10, gray-25) or pure white

**Focal Point Emphasis:**
- Radial or concentric patterns draw eye to center
- Solid black creates strongest contrast
- White space frames important elements

### Rube Goldberg Flow (Kinetic Emphasis)

**Directional Patterns:**
- Rain pattern (diagonal) for downward/wind motion
- Radial burst for energy emanation
- Arrows with pattern-filled heads for process flow

**Connection Techniques:**
- Flowing curved paths between components
- Dotted/dashed lines for implied connections
- Numbered sequence circles (solid black with white numerals)

### Historical Line-Art Style

**Embrace Organic Imperfection:**
- Woodcut texture adds hand-crafted authenticity
- Slightly irregular engraving lines suggest traditional technique
- Varied line weights create visual interest

**Cross-Hatching for Shadow:**
- Dense cross-hatch (0.3px) for deep shadows
- Medium cross-hatch for mid-tones
- Single hatch for light shadows
- No pattern for highlights (pure white)

---

## 📐 Enhanced Material-to-Pattern Guide

### Structural & Mechanical
- **Metal (polished):** Engraving or light hatch
- **Metal (cast iron):** Dense cross-hatch
- **Steel beams:** Bold hatch (0.4px weight)
- **Stone/masonry:** Brick pattern or dense stipple
- **Concrete:** Medium stipple
- **Glass:** Very light gray-10 or pure white with bold outline

### Organic & Natural
- **Human skin:** Light stipple (gray-25 to gray-40)
- **Animal fur:** Short hatch or stipple
- **Feathers:** Scales pattern
- **Wood (timber):** Woodcut or waves
- **Wood (bark):** Dense woodcut
- **Leaves/vegetation:** Waves or light stipple
- **Fabric/cloth:** Weave or fine stipple
- **Rope/cordage:** Waves or whorl
- **Leather:** Medium stipple with grain lines

### Environmental & Effects
- **Water (still/lake):** Topo or concentric
- **Water (flowing/river):** Waves or rain (directional)
- **Water (splash):** Radial burst + stipple drops
- **Terrain elevation:** Topo (classic topographic)
- **Mountains:** Engraving with elevation lines
- **Fire/flames:** Radial burst or organic whorl
- **Heat radiation:** Radial with decreasing density outward
- **Wind:** Rain pattern (diagonal direction)
- **Smoke/clouds:** Light stipple (scattered, irregular)
- **Fog/mist:** Very light gray-10 stipple

### Special Effects & Emphasis
- **Energy/power:** Radial burst
- **Explosion/impact:** Concentric circles + radial
- **Sound waves:** Concentric circles
- **Danger/warning:** Solid black or dense cross-hatch
- **Caution zone:** Medium cross-hatch with border
- **Focus/target:** Concentric circles or radial
- **Growth/organic flow:** Whorl or scales
- **Speed/motion:** Rain (diagonal direction)
- **Vibration:** Short parallel lines perpendicular to surface

### Texture Application Rules
- **Solid black `#000` allowed** for high-contrast elements (warning boxes, arrows, text)
- **Solid grays FORBIDDEN** (`fill="#808080"` or opacity manipulation is prohibited)
- **Tone control:** Adjust pattern density, NOT color/opacity
  - Light tone: Sparse pattern (gray-10, gray-25)
  - Medium tone: Medium pattern (gray-40, gray-50)
  - Dark tone: Dense pattern (gray-60, gray-75, gray-90)
- **Reusability:** Define once in `<defs>`, reference with `fill="url(#pattern-id)"`
- **White background:** Always use `#FFFFFF` or transparent for backgrounds

</details>

---

## 📋 SVG Technical Specifications

### Format Requirements
- **File Format:** SVG (Scalable Vector Graphics) only
- **Color Profile:** **MONOCHROME** - Black `#000000`, White `#FFFFFF`, pattern-based grays
- **Allowed:** Solid black `#000`, pattern-based grayscale (gray-10 through gray-90)
- **Forbidden:** Solid hex grays (#808080, etc.), opacity manipulation for toning
- **Structure:** Properly defined `width`, `height`, `viewBox` attributes
- **Viewbox Standards:** 800x600 (4:3) or 1200x800 (3:2) for diagrams
- **Optimization:** Minified (remove metadata, comments, editor data, unnecessary whitespace)
- **Target Size:** <50KB per file (post-optimization)

### Line Weight Standards
- **Primary structures:** 1.5px (main outlines, key shapes)
- **Secondary details:** 1.0px (internal divisions, minor elements)
- **Texture patterns:** 0.3px (hatching, stipple, waves, topographic)
- **Annotations/Leaders:** 0.5px (pointer lines, dimension arrows)

### Text Requirements
- **Format:** Editable `<text>` elements (NOT converted to paths)
- **Font Family:** **Mallard** (bundled in `extensions/assets/fonts/mallard/`)
  - Primary: `mallard-neueue.otf` (normal weight)
  - Bold: `mallard-blocky.otf` (bold weight)
  - Alternative: `mallard-smooth.otf` (smoother rendering)
  - Fallback: `Arial, sans-serif` for compatibility
- **Font Embedding:** Use `@font-face` in SVG `<defs><style>` section
- **Sizes:**
  - Title/Header: 16-24px
  - Section Labels: 12-14px
  - Annotations: 8-10px
- **Accessibility:** `<title>` and `<desc>` elements for screen readers

### Scope & Exclusions
- **Allowed:** Flowcharts, diagrams, technical renderings, schematics, cross-sections
- **FORBIDDEN:** Portraits, landscapes, photorealistic illustrations, decorative art

---

## 🎨 Color Palette (DEPRECATED - MONOCHROME ONLY)

**CRITICAL UPDATE:** Previous color-coded system is **RETIRED**.

### Current Standard: MONOCHROME ONLY
- **Black:** `#000000` - All lines, text, shapes
- **White:** `#FFFFFF` - Background, negative space
- **Grays:** **FORBIDDEN** - Use texture patterns instead

### Legacy Color Coding (Reference Only - DO NOT USE)
~~Water: `#0066CC` (blue)~~ → Use topographic/undulating line pattern
~~Fire: `#CC3300` (red-orange)~~ → Use hatching pattern with directional flow
~~Safety/Caution: `#FFCC00` (yellow)~~ → Use dense cross-hatching
~~Danger/Stop: `#CC0000` (red)~~ → Use very dense cross-hatching + warning text
~~Vegetation/Food: `#339933` (green)~~ → Use wavy line pattern
~~Tools/Equipment: `#666666` (gray)~~ → Use medium hatching
~~Medical/First Aid: `#CC0066` (magenta)~~ → Use stipple pattern
~~Navigation: `#9933CC` (purple)~~ → Use topographic pattern

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

### Fire Structures (Target: 50 diagrams, Current: 11, 22.0%)
**Location:** `knowledge/diagrams/fire/`

**Completed:**
- Bow drill assembly
- Fire lay structures (teepee, log cabin, lean-to)
- Fire triangle diagram ✨ **NEW** (Gemini generated)
- Simple fire triangle diagram ✨ **NEW** (Gemini generated)
- Friction fire hand positions
- (7 more existing diagrams)

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

## 🛠️ SVG Generation Tools

### Command-Line Generator (Gemini API)

**Location:** `dev/tools/generate_svg_diagram.py`
**Documentation:** `dev/tools/SVG-GENERATOR-GUIDE.md`

Generate Technical-Kinetic compliant SVG diagrams from text descriptions using Gemini AI.

#### Quick Usage

```bash
cd /Users/fredbook/Code/uDOS

# Generate diagram
.venv/bin/python dev/tools/generate_svg_diagram.py "DESCRIPTION" CATEGORY

# Examples
.venv/bin/python dev/tools/generate_svg_diagram.py "tourniquet application 6 steps" medical
.venv/bin/python dev/tools/generate_svg_diagram.py "bow drill assembly" fire --size 1200x800
.venv/bin/python dev/tools/generate_svg_diagram.py "water filter layers" water -o custom-name.svg
```

#### Features
- ✅ Automatic pattern library embedding (12 patterns)
- ✅ Mallard font with @font-face integration
- ✅ Material-to-pattern smart mapping
- ✅ Compliance validation (monochrome, accessibility, size)
- ✅ Auto-generated filenames and category organization
- ✅ Batch generation script for high-priority diagrams

#### Batch Generation

```bash
# Generate ~25 priority diagrams across all categories
dev/tools/scripts/generate_priority_diagrams.sh
```

---

## 🤖 Gemini API Image-to-Vector Processing

### Automated SVG Generation Pipeline

**Purpose:** Convert raster images (photos, sketches) to Technical-Kinetic compliant SVG diagrams

### Processing Requirements
1. **Input:** Raster images (PNG, JPG, sketch photos)
2. **Convert to SVG paths** with Technical-Kinetic constraints
3. **Enforce monochrome palette** - Reject any grays/colors, convert to black/white
4. **Apply standardized texture patterns** (4 types: hatch, stipple, waves, topo)
5. **Preserve semantic structure** - Group related elements logically
6. **Generate minified output** - Remove metadata, optimize paths
7. **Validate against style guide** - Automated compliance check

### Texture Pattern Assignment Logic
- **Detect material type** in source image:
  - Metal/mechanical → Hatching (45° lines)
  - Soft/atmospheric → Stipple (dots)
  - Organic/natural → Wavy lines
  - Environmental/terrain → Topographic (concentric)
- **Calculate tone density** from source brightness
- **Apply appropriate `<pattern>` fill** instead of solid grays

### API Workflow
```
1. Upload raster image to Gemini API
2. Request: "Convert to monochrome SVG with Technical-Kinetic style"
3. Specify: Line weights (1.5px primary, 0.3px texture)
4. Enforce: Black/white only, texture patterns for tone
5. Validate: Style compliance check
6. Output: Minified SVG with embedded <defs> patterns
```

### Validation Criteria
- [ ] **Monochrome check:** Only black `#000`, white `#FFF`, solid grays `#1A1A1A-#E6E6E6`
- [ ] **Color palette:** Solid grays and bitmap patterns supported
- [ ] **Line weights:** 1.5px primary, 0.3px texture, 0.5px annotations
- [ ] **Text format:** Editable `<text>` elements (not paths)
- [ ] **Structure:** Valid `viewBox`, optimized paths
- [ ] **Size:** <50KB file size
- [ ] **Accessibility:** `<title>` and `<desc>` present

### Integration with uDOS
- **DIAGRAM command:** Render SVG with viewport scaling in TUI
- **Export:** Save panel/grid as editable vector graphics (SVG/PDF)
- **Search:** Filter by topic, material type, texture pattern used
- **Metadata:** Category, skill level, tools required, complexity

---

## 📊 Progress Tracking

### Overall Status: 81/500 diagrams (16.2%)

### By Complexity:
- Simple (icons, symbols): 20/100 (20%)
- Moderate (single-page instructional): 40/250 (16%)
- Complex (multi-step, exploded views): 15/100 (15%)
- Reference charts: 6/50 (12%) ← Updated with multi-barrier diagram

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

### Submission Guidelines (STRICT TECHNICAL-KINETIC COMPLIANCE)

**CRITICAL:** All submissions must pass monochrome validation

#### Required Elements
- [ ] **SVG format only** - Vector, scalable, no raster images embedded
- [ ] **MONOCHROME PALETTE** - Black `#000000`, White `#FFFFFF`, solid grays `#1A1A1A-#E6E6E6`
- [ ] **BITMAP PATTERNS** - Use Mac OS System 1 patterns for texture effects
- [ ] **Line weights compliant:**
  - Primary structures: 1.5px
  - Texture patterns: 0.3px
  - Annotations: 0.5px
- [ ] **Editable text** - `<text>` elements (NOT paths)
- [ ] **Clean paths** - No editor metadata, optimized/minified
- [ ] **Accessible** - `<title>` and `<desc>` for screen readers
- [ ] **Print-tested** - B&W legible, patterns clear at 300dpi

#### Texture Pattern Requirements
- [ ] Define patterns in `<defs>` section (reusable)
- [ ] Apply patterns via `fill="url(#pattern-id)"`
- [ ] Use appropriate pattern for material:
  - Metal/mechanical: Hatching
  - Soft/atmospheric: Stipple
  - Organic/natural: Wavy lines
  - Environmental/terrain: Topographic
- [ ] Vary pattern density for tone (NOT opacity)

#### File Naming Convention
`category-topic-type.svg`
- Examples: `water-filter-cross-section.svg`, `fire-bow-drill-assembly.svg`
- Lowercase, hyphens between words
- Descriptive, searchable filenames

#### Validation Checklist
Run diagram through validator before submission:
```bash
# Check for forbidden colors (anything except #000000, #FFFFFF)
grep -E 'fill="#[0-9A-Fa-f]{6}"' diagram.svg | grep -v -E '#000000|#FFFFFF'
# Should return empty (no matches = valid)

# Check for forbidden opacity/gray usage
grep -E 'opacity|fill-opacity|stroke-opacity' diagram.svg
# Should return empty (no opacity manipulation)

# Check file size
ls -lh diagram.svg  # Should be <50KB
```

### Tools Recommended
- **Inkscape** (free, open-source) - Best for pattern creation
- **Adobe Illustrator** (professional) - Advanced vector editing
- **draw.io / diagrams.net** (online, free) - Quick flowcharts
- **Custom scripts** - Automated pattern application

### Creating Texture Patterns in Inkscape
1. Create pattern elements (lines, dots, waves)
2. Object → Pattern → Objects to Pattern
3. Edit → Clone → Create Tiled Clones (for density control)
4. Export as optimized SVG (File → Save As → Optimized SVG)
5. Validate monochrome compliance

---

## 📋 Priority Diagram Wishlist (Monochrome Compliant)

### URGENT (Safety-Critical)
1. **Tourniquet application** (6 steps) - Hatching for fabric, stipple for skin
2. **CPR hand placement** (adult/child/infant) - Anatomical cross-section
3. **Fire safety zones** (distance markers) - Topographic pattern for ground, hatching for structures
4. **Hypothermia progression stages** - Stipple gradient for temperature zones
5. **Water purification flowchart** (decision tree) ← **IN PROGRESS** (needs monochrome conversion)

### HIGH PRIORITY (Common Tasks)
6. **Bow drill assembly** (exploded view) - Hatching for wood, wavy for cordage
7. **Debris hut cross-section** (insulation layers) - Wavy for debris, topo for ground
8. **Universal Edibility Test flowchart** - Decision tree with pattern-coded risk levels
9. **Compass declination adjustment** - Mechanical hatching for compass body
10. **Knot library** (8 essential knots) - Clean line art, directional flow

### MEDIUM PRIORITY (Skill Development)
11. **Stone tool knapping sequence** - Cross-hatching for stone, directional flow for force
12. **Basket weaving patterns** (4 types) - Wavy organic lines for materials
13. **Fish trap construction** - Hatching for structure, topo for water flow
14. **Snow cave ventilation system** - Stipple for snow, directional airflow arrows
15. **Signal mirror aiming technique** - Hatching for mirror, stipple for reflection cone

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
