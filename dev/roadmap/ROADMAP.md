# 🗺️ uDOS Development Roadmap

**Current Version:** v1.1.13 ✅ **STABLE** (Project Structure Reorganization)
**Status:** Production ready, 111/111 tests passing
**Last Updated:** December 2, 2025

> **Philosophy:** Development measured in STEPS and MOVES, not time. Work proceeds through organic pacing and cron patterns.

---

## 📍 Current Release: v1.1.13 (December 2025)

**Status:** ✅ **COMPLETE** - Production ready
**Test Coverage:** 111/111 tests passing (100%)
**Completion Date:** December 2, 2025

### What's New

- **Project Structure:** Clean separation between `/dev/` (tracked) and `/memory/` (unified user workspace)
- **Development Workspace:** Organized tools, roadmaps, and session logs in `/dev/`
- **User Workspace:** Consolidated `/sandbox/` → `/memory/` for simpler mental model
- **Memory Consolidation:** Merged 721 files, removed 5 directories, renamed 23 .uscript → .upy
- **Directory Cleanup:** `/data/` databases → `memory/user/`, flattened logs, merged shared+groups→community
- **Professional Organization:** Unix-style conventions, clear file lifecycle
- **Git Clarity:** Simple .gitignore rules, selective tracking (ucode/ only)

### Directory Structure

```
uDOS/
├── dev/                    # Development workspace (tracked in git)
│   ├── tools/              # Development utilities (migrate_upy.py)
│   ├── roadmap/            # This file - project planning
│   ├── sessions/           # Development session logs
│   └── scripts/            # Automation scripts
│
├── memory/                 # Unified user workspace (tracked selectively)
│   ├── ucode/              # Core distributable .upy scripts + tests
│   │   └── stdlib/         # Standard library (merged from modules/)
│   ├── missions/           # Mission definitions and state
│   ├── workflows/          # Workflow templates and active runs (.upy format)
│   ├── checklists/         # Checklist progress and state
│   ├── scenarios/          # Scenario definitions (JSON)
│   ├── sessions/           # Session management
│   ├── archived/           # Completed/archived work
│   ├── community/          # Community content (merged from shared/groups/)
│   ├── logs/               # Session and runtime logs (flattened)
│   ├── user/               # User profiles, settings, databases
│   ├── system_backup/      # System config backups (used by core)
│   ├── docs/               # Draft documentation
│   ├── drafts/             # Work in progress
│   ├── private/            # Private user content
│   ├── public/             # Public user content
│   ├── barter/             # Barter system data
│   └── themes/             # Custom themes
│
├── core/                   # Core system (required, stable)
├── extensions/             # Extension system
├── knowledge/              # Public knowledge bank (read-only)
└── wiki/                   # GitHub wiki (documentation)
```

**Changes in v1.1.13:**
- Removed `/sandbox/` (721 files merged into `/memory/`)
- Removed `/data/` (databases moved to `memory/user/`)
- Removed `inbox/`, `shared/`, `groups/`, `modules/` (consolidated)
- Flattened `logs/sessions/` → `logs/`
- Renamed all `.uscript` → `.upy` (23 files)

**Note:** `/memory/` replaces old `/sandbox/` split for v1.1.13+ unified workspace.

---

## 🎯 Active Development: v1.1.15 - Graphics Infrastructure Enhancement

**Target:** Q1 2026
**Status:** 🔄 Planning phase (Research)
**Complexity:** Medium-High (new capabilities + integration)
**Priority:** High - Blocks content quality improvements

### Strategic Rationale

**Why graphics first?** Before expanding knowledge bank content (136+ guides), improve visual tools to ensure consistent, high-quality diagrams across all content. Better tools → better content → then systematic upgrade pass.

**User-Referenced Standards:**
- [Typora Mermaid Support](https://support.typora.io/Draw-Diagrams-With-Markdown/) - Markdown-based diagrams
- [GitHub Diagram Formats](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams) - Mermaid, GeoJSON, ASCII STL
- [ASCII Diagrams](https://asciidiagrams.github.io/) - Refined, less chunky style

### Current Gaps Analysis

**Existing Graphics Infrastructure (v1.1.13):**
✅ `diagram_handler.py` - ASCII art library browser (13 types, 880 lines)
  - Commands: LIST, SEARCH, SHOW, RENDER, COPY, EXPORT, TYPES, GENERATE
  - Storage: `core/data/diagrams/`
  - **Limitation:** Pre-built library only, no dynamic generation

✅ `generate_handler.py` - Nano Banana SVG pipeline (580 lines)
  - Pipeline: Style Guide → Gemini 2.5 Flash (PNG) → Vectorize → SVG
  - Commands: GENERATE SVG/DIAGRAM/ASCII/TELETEXT
  - **Limitation:** No text-to-diagram (Mermaid), ASCII described as "chunky"

**Missing Capabilities:**
❌ Mermaid diagram support (sequence, flowchart, Gantt, class, state, pie, gitgraph, mindmap)
❌ GitHub diagram formats (GeoJSON/TopoJSON maps, ASCII STL 3D models)
❌ Refined ASCII graphics (asciidiagrams.github.io quality)
❌ Text-to-diagram conversion (markdown code blocks → rendered diagrams)
⚠️ Nano Banana needs finetuning for technical survival diagrams
⚠️ Workflow cycles need improvement for diagram generation iteration

### Phase 1: Mermaid Integration (Tasks 1-2)

**Goal:** Enable Mermaid diagram generation for decision trees, flowcharts, state machines

**Research (Task 1):**
- Server-side rendering: mermaid-cli + puppeteer (offline-compatible)
- Client-side rendering: Web dashboard integration (requires browser)
- Hybrid approach: Pre-render in workflow, display in dashboard
- **Decision criteria:** Offline-first design, minimal dependencies, integration with existing GENERATE system

**Implementation (Task 2):**
```python
# core/commands/mermaid_handler.py (new)
class MermaidHandler:
    """
    Mermaid diagram generation and management.

    Commands:
    - MERMAID RENDER <type> <code|file>  # Generate diagram
    - MERMAID EXPORT <format>            # Export to SVG/PNG
    - MERMAID LIST                       # List supported types
    - MERMAID VALIDATE <code>            # Syntax check

    Supported types (Typora-compatible):
    - sequence, flowchart, gantt, class, state, pie
    - gitgraph, mindmap, timeline, quadrant

    Output: sandbox/drafts/mermaid/
    """
```

**Integration Points:**
- Extend `generate_handler.py` to recognize markdown code blocks
- Add `GUIDE RENDER` command to process guides with embedded Mermaid
- Store templates in `core/data/diagrams/mermaid/`
- Dashboard preview support (if client-side rendering chosen)

### Phase 2: GitHub Diagram Formats (Task 3)

**Goal:** Support GeoJSON/TopoJSON maps and ASCII STL 3D models

**GeoJSON/TopoJSON Maps:**
- Use case: Navigation guides, territory mapping, resource locations
- Integration: Extend `generate_handler.py` with map rendering
- Libraries: geojson.io, leaflet.js (for web dashboard)
- Offline: Pre-render to static images/SVG

**ASCII STL 3D Models:**
- Use case: Tool designs, shelter structures, trap diagrams
- Parser: Read ASCII STL syntax from code blocks
- Renderer: Three.js (web dashboard) or raytracing (static images)
- Storage: `extensions/assets/data/models/`

**Example Use Cases:**
```markdown
# Navigation Guide: Finding Water Sources

```geojson
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "properties": {"name": "River", "type": "freshwater"},
    "geometry": {"type": "LineString", "coordinates": [...]}
  }]
}
```

# Shelter Design: A-Frame Structure

```stl
solid a_frame_shelter
  facet normal 0.0 1.0 0.0
    outer loop
      vertex 0.0 0.0 0.0
      vertex 3.0 2.0 0.0
      vertex 0.0 0.0 4.0
    endloop
  endfacet
endsolid
```
```

### Phase 3: ASCII Graphics Refinement (Task 4)

**Goal:** Improve ASCII art quality to match asciidiagrams.github.io standard

**Current Issues:**
- "Chunky" appearance (thick lines, excessive spacing)
- Limited box-drawing character support
- Poor flowchart/table generation

**Improvements:**
- Unicode box-drawing: ┌─┐ │ └─┘ ├─┤ ┬ ┴ ┼
- Better alignment algorithms (less whitespace)
- Cleaner line styles (single/double/dashed)
- Improved table formatting (compact, aligned)
- Enhanced flowchart generation (decision diamonds, rounded boxes)
- Two house styles: Plain ASCII (max compatibility) + Block shading (visual hierarchy)

**Reference Library:**
- `dev/roadmap/graphics1.md` - 25 panel-style diagrams with block shading (█▓▒░)
- `dev/roadmap/graphics2.md` - 25 plain ASCII diagrams (no block characters)
- Includes: system architecture, flows, pipelines, tables, progress bars, theatre layouts

**Update Targets:**
- `core/services/ascii_generator.py` (or create if missing)
- `core/data/diagrams/` library (add 50 refined examples from graphics1/2.md)
- `diagram_handler.py` GENERATE command (use new renderer)

**Test Cases:**
```
Before (chunky):          After (refined):
+-------+-------+         ┌───────┬───────┐
| Cell1 | Cell2 |         │ Cell1 │ Cell2 │
+-------+-------+         ├───────┼───────┤
| Cell3 | Cell4 |         │ Cell3 │ Cell4 │
+-------+-------+         └───────┴───────┘
```

### Phase 4: Nano Banana Finetuning (Task 5)

**Goal:** Optimize AI diagram generation for technical survival content

**Current Pipeline:**
Style Guide → Gemini 2.5 Flash (PNG) → Vectorize (potrace/vtracer) → Cleanup → SVG

**Optimization Areas:**

1. **Prompt Engineering:**
   - Technical diagram templates (water purification, fire selection, shelter types)
   - Consistent visual style (minimal, clear, educational)
   - Label placement optimization
   - Color palette for different guide categories

2. **Vectorization Quality:**
   - Tune potrace parameters (threshold, turnpolicy, alphamax)
   - Experiment with vtracer settings (color mode, hierarchical, mode)
- Centralized user-specific state
- Follows existing `user.json` pattern
- Survives system updates
- Easy backup/restore

**Archive Command:** ✅ **New handler** (`core/commands/archive_handler.py`)
- Clean separation of concerns
- Integrates with existing cleanup utilities
- Timestamps and metadata preservation
- Supports missions, workflows, checklists

### Tasks

#### Phase 1: Infrastructure ✅ COMPLETE (December 2, 2025)

**1. Checklist System Foundation** ✅
- ✅ Create `core/data/schemas/checklist.schema.json` (180 lines, complete validation)
- ✅ Implement `core/services/checklist_manager.py` (276 lines, CRUD + progress tracking)
- ✅ Create `core/commands/checklist_handler.py` (370 lines, 7 commands)
- ✅ Add CHECKLIST command routing in `core/uDOS_commands.py`
- ✅ Convert 3 existing checklists to JSON:
  - ✅ `knowledge/checklists/emergency/72-hour-bug-out-bag.json` (15 categories, 80+ items)
  - ✅ `knowledge/checklists/emergency/first-aid-kit-inventory.json` (42 items, medical focus)
  - ✅ `knowledge/checklists/daily/water-storage-maintenance.json` (25 items, frequency-based)

**2. Workflow Migration** ✅ COMPLETE
- ✅ Convert 23 `.uscript` files to `.upy` (COMPLETE v1.1.13)
- ✅ Update workflow templates to `.upy` format
- ✅ Re-engineer workflows folder (v2.0 flat structure, gameplay integration)
- 🔄 Expose WORKFLOW commands in main CLI (currently in handler)

**3. Archive Handler** ✅ COMPLETE (December 2, 2025)
- ✅ Create `core/commands/archive_handler.py` (430 lines)
- ✅ Commands: `ARCHIVE mission|workflow|checklist <id>`, LIST, restore
- ✅ Storage: `memory/system/archived/` with timestamps
- ✅ Metadata: JSON files with completion stats
- ✅ Integration with existing cleanup commands (CLEAN, TIDY)

#### Phase 2: Integration (Week 3-4)

**4. Variable System Extension** ✅ COMPLETE (December 2, 2025)
- ✅ Extend `core/commands/variable_handler.py` with new scopes:
  - ✅ `MISSION.*` - Access mission state from workflow state
  - ✅ `CHECKLIST.*` - Access checklist progress from state file
  - ✅ `WORKFLOW.*` - Access workflow state from checkpoints
- ✅ Examples working:
  - `GET MISSION.PROGRESS` → "0/0 (no active mission)"
  - `GET CHECKLIST.ACTIVE` → "3"
  - `GET WORKFLOW.PHASE` → "IDLE"

**5. System Linking** ✅ COMPLETE (December 2, 2025)
- ✅ Add `workflow_script` field to mission schema (mission.schema.json)
- ✅ Add `related_guides`, `related_checklists` to mission schema
- ✅ Update `core/commands/guide_handler.py` to display related checklists
- ✅ Created example mission: water-purification-setup.json (links guides + checklists)
- 🔄 Sync mission metrics from workflow checkpoints (future enhancement)

**6. Dashboard MVP** ✅ COMPLETE (December 2, 2025)
- ✅ Create `extensions/web/dashboard/` structure:
  ```
  dashboard/
  ├── extension.json         # Extension metadata
  ├── server.py              # Flask application (215 lines)
  ├── static/
  │   └── dashboard.js       # Real-time updates (5s refresh)
  └── templates/
      └── index.html         # Main dashboard (NES.css)
  ```
- ✅ Core widgets:
  - ✅ Mission progress bars (current mission, all missions)
  - ✅ Checklist completion meters (active checklists)
  - ✅ Workflow phase indicators (current phase, iterations)
  - ✅ XP and achievements display
- ✅ Real-time polling (5-second refresh)
- ✅ Port: 5050 (configurable)
- ✅ NES.css retro Nintendo 8-bit styling
- ✅ Complete README.md documentation

#### Phase 3: Content & Polish (Week 5-6)

**7. Checklist Library Expansion** ✅ COMPLETE (December 2, 2025)
- ✅ Created 7 new JSON checklists from existing guides
- ✅ Target categories achieved:
  - ✅ Emergency: Evacuation plan, Wound care (+ existing bug-out bag, first aid)
  - ✅ Daily: Fire management, Security patrol (+ existing water check)
  - ✅ Projects: Shelter construction, Tool making
  - ✅ Seasonal: Winter preparedness
- ✅ All validated against checklist.schema.json
- ✅ Added to `knowledge/checklists/` (10 total checklists, 126+ items)

**8. Documentation** ✅ COMPLETE (December 2, 2025)
- ✅ Consolidated workflow docs to wiki
- ✅ Created `wiki/Systems-Integration.md` - comprehensive guide to mission/workflow/checklist integration
  - ✅ 5 integration patterns documented
  - ✅ Complete example workflows
  - ✅ State file reference
  - ✅ Best practices section
- ✅ Updated `wiki/Command-Reference.md` with v1.1.14 commands:
  - ✅ GUIDE (LIST, SHOW, START)
  - ✅ CHECKLIST (CREATE, LIST, LOAD, COMPLETE, STATUS, PROGRESS, RESET)
  - ✅ MISSION (CREATE, START, STATUS, COMPLETE)
  - ✅ ARCHIVE (LIST, mission, checklist, workflow, restore)
  - ✅ GET (MISSION.*, CHECKLIST.*, WORKFLOW.*)
- ✅ Created `wiki/Dashboard-Guide.md` - complete dashboard documentation
  - ✅ Quick start guide
  - ✅ All 4 widgets documented
  - ✅ 5 API endpoints referenced
  - ✅ Troubleshooting section
  - ✅ Customization guide
  - ✅ Production deployment section

### Success Metrics

**Checklists:**
- ✅ 10+ checklists in JSON format
- ✅ Full CRUD operations
- ✅ Progress tracking with persistence
- ✅ Guide integration

**Workflows:**
- ✅ Zero .uscript files (all migrated to .upy) - COMPLETE v1.1.13
- ✅ WORKFLOW commands in main CLI
- ✅ Mission-workflow linking functional

**Dashboard:**
- ✅ Flask server running on port 5050
- ✅ 3+ widget types implemented
- ✅ NES.css styling applied
- ✅ Real-time updates working

**Integration:**
- ✅ MISSION/CHECKLIST/WORKFLOW variable scopes
- ✅ Cross-system navigation (guide → checklist → mission)
- ✅ Automatic metric syncing

**Archive:**
- ✅ ARCHIVE command functional - COMPLETE (December 2, 2025)
- ✅ Timestamps and metadata preserved - COMPLETE (December 2, 2025)
- ✅ Easy restore capability - COMPLETE (December 2, 2025)

---

## 🎨 Graphics System Development Rounds

### Vision

Build a comprehensive graphics generation system with three distinct modes, each optimized for specific content types and use cases.

---

### Round 1: ASCII Line Art System (v1.1.15)

**Target:** Q1 2026 (after v1.1.14)
**Purpose:** Technical diagrams, schematics, flowcharts, and documentation illustrations

#### Objectives

1. **True ASCII Art Generator**
   - Line-drawing algorithm for technical precision
   - Box-drawing characters (─│┌┐└┘├┤┬┴┼)
   - Flowchart symbols (◆▶●□○)
   - Connection lines with proper intersections
   - Text label support

2. **Markdown Integration**
   - Code fence rendering (```ascii art```)
   - Export to .md files with preserved formatting
   - GitHub-compatible display
   - Monospace font optimization

3. **Technical Drawing Templates**
   - Circuit diagrams
   - System architecture
   - Network topology
   - Process flows
   - Tree structures

#### Implementation

- **Handler:** `core/commands/ascii_handler.py`
- **Service:** `core/services/ascii_generator.py`
- **Templates:** `core/data/templates/ascii/`
- **Command:** `ASCII DIAGRAM <type> <description>`
- **Output:** Pure ASCII text (no images)

#### Use Cases

- Documentation diagrams in wiki
- System architecture visualization
- Code structure maps
- Process flow documentation
- Quick technical sketches

---

### Round 2: Teletext Block Graphics System (v1.1.16)

**Target:** Q2 2026
**Purpose:** Photo/video conversion to retro teletext aesthetic, mosaic art, vintage UI

#### Objectives

1. **Teletext Mosaic Converter**
   - Photo → teletext block conversion
   - Video → teletext animation (frame-by-frame)
   - Color palette: 8 teletext colors
   - Block resolution: 2×3 pixel blocks
   - Dithering algorithms for smooth gradients

2. **Teletext Rendering Engine**
   - Real-time preview in terminal
   - HTML/CSS teletext renderer
   - Export to PNG/GIF
   - Animation support (frame sequences)

3. **Creative Tools**
   - Portrait mode (high detail)
   - Landscape mode (wide scenes)
   - Animation mode (video clips)
   - Mosaic art mode (abstract)

#### Implementation

- **Extension:** `extensions/web/teletext/`
- **Handler:** `core/commands/teletext_handler.py`
- **Converter:** `core/services/teletext_converter.py`
- **Renderer:** `extensions/web/teletext/renderer.py`
- **Command:** `TELETEXT CONVERT <image|video> [mode]`
- **Output:** Teletext markup + rendered image/animation

#### Technical Specs

**Block System:**
- Character set: Teletext mosaic characters (░▒▓█▀▄▌▐)
- Resolution: 40×25 characters (80×75 blocks)
- Colors: 8 (black, red, green, yellow, blue, magenta, cyan, white)
- Refresh: 50Hz for animations

**Conversion Pipeline:**
1. Load image/video frame
2. Resize to 80×75 pixel grid
3. Quantize to 8-color palette
4. Map to 2×3 block patterns
5. Apply dithering
6. Generate teletext markup
7. Render to output format

#### Use Cases

- Retro photo filters
- Vintage video aesthetics
- ASCII art alternative
- Creative mosaic art
- Nostalgic UI elements

---

### Round 3: SVG Nano Banana Enhancement (v1.1.17)

**Target:** Q2-Q3 2026
**Purpose:** Natural subjects, organic forms, intricate line art - creative/artistic content only

#### Scope Refinement

**✅ Appropriate for Nano Banana:**
- Natural landscapes (mountains, forests, rivers)
- Organic subjects (plants, animals, people)
- Creative illustrations (characters, scenes)
- Artistic line art (portraits, nature studies)
- Complex organic shapes

**❌ NOT for Nano Banana (use ASCII instead):**
- Technical diagrams
- System architecture
- Flowcharts
- Circuit diagrams
- Box-and-line schematics

#### Objectives

1. **Enhanced Natural Subject Processing**
   - Improved edge detection for organic shapes
   - Better curve handling (bezier optimization)
   - Texture preservation (bark, fur, water)
   - Depth perception (foreground/background)
   - Natural detail retention

2. **Style Guide Expansion**
   - Nature styles (botanical, landscape, wildlife)
   - Artistic styles (sketch, woodcut, engraving)
   - Cultural styles (Celtic, Japanese, Art Nouveau)
   - Material studies (water, fire, clouds, terrain)

3. **Quality Enhancements**
   - Multi-pass vectorization
   - Intelligent simplification
   - Organic curve fitting
   - Natural proportions
   - Artistic composition

#### Implementation

- **Existing:** `core/commands/generate_handler.py` (already complete)
- **Enhancement:** Better prompt engineering for natural subjects
- **Styles:** Expand `extensions/assets/styles/` with nature/organic presets
- **Templates:** `core/data/templates/svg/natural/`
- **Command:** `GENERATE SVG <natural_subject> [category] [style]`

#### Creative Brief Integration

**Natural Subject Categories:**
- **Botanical:** Plants, flowers, trees, fungi
- **Wildlife:** Animals, birds, insects, marine life
- **Landscape:** Mountains, valleys, coastlines, skies
- **Human:** Portraits, figures, expressions
- **Elements:** Fire, water, wind, earth, weather
- **Organic Patterns:** Fractals, growth patterns, natural textures

**Style Presets:**
- `botanical-study` - Scientific illustration style
- `landscape-sketch` - Loose, artistic landscapes
- `wildlife-portrait` - Detailed animal studies
- `nature-woodcut` - Traditional woodcut aesthetic
- `organic-flow` - Flowing, natural lines

#### Use Cases

- Nature guide illustrations
- Plant identification diagrams
- Wildlife reference art
- Landscape documentation
- Creative storytelling visuals

---

### Graphics System Integration

**Workflow Decision Tree:**

```
Need a graphic?
│
├─ Technical/Schematic? → Use ASCII Line Art
│   └─ Examples: flowcharts, architecture, circuits
│
├─ Photo/Video conversion? → Use Teletext Blocks
│   └─ Examples: portraits, scenes, retro filters
│
└─ Natural/Organic subject? → Use SVG Nano Banana
    └─ Examples: plants, animals, landscapes, art
```

**Command Summary:**

```bash
# ASCII for technical diagrams
ASCII DIAGRAM flowchart "User login process"
ASCII DIAGRAM circuit "Arduino LED controller"
ASCII DIAGRAM network "Home network topology"

# Teletext for photo/video conversion
TELETEXT CONVERT photo.jpg portrait
TELETEXT CONVERT video.mp4 animation
TELETEXT CONVERT landscape.png wide

# SVG for natural subjects
GENERATE SVG "oak tree in summer" botanical
GENERATE SVG "mountain landscape" nature sketch
GENERATE SVG "wolf portrait" wildlife detailed
```

---

## 🔮 Future Releases (v1.1.18+)

### v1.1.18+ - Variable System (Deferred from v1.1.9)
- JSON-defined variables (`core/data/variables/*.json`)
- SPRITE variables (HP, XP, level, stats)
- OBJECT variables (items, equipment, inventory)
- Scope management (global, session, script, local)

### v1.1.19+ - Play Extension (Deferred from v1.1.9)
- STORY command migration (old .uscript → .upy)
- Integration with new variable system
- Gameplay mechanics refinement

---

## 📊 Development Metrics

**Completed Versions:** 13 (v1.1.0 - v1.1.13)
**Test Coverage:** 111/111 passing (100%)
**Total Lines of Code:** ~50,000 (core + extensions)
**Knowledge Articles:** 136 guides across 6 categories
**Wiki Pages:** 30+ comprehensive documentation pages
**Extensions:** 12 bundled, unlimited cloneable

**v1.1.13 Consolidation Stats:**
- Files merged: 721 (sandbox → memory)
- Directories removed: 5 (inbox, shared, groups, modules, data)
- Scripts migrated: 23 (.uscript → .upy)
- Git commits: 5 (roadmap, memory structure, sandbox removal, data cleanup, consolidation)
- Lines removed: 2,709 (cleanup + consolidation)

**Quality Metrics:**
- ✅ Zero breaking bugs in production
- ✅ Backwards compatibility maintained (v1.1.0+)
- ✅ All tests passing every release
- ✅ Complete documentation coverage
- ✅ Active development (weekly updates)

---

## 🤝 Contributing

**Development Process:**
1. Work in `/dev/` for tracked development files
2. Test in `/memory/` (user workspace) for experiments
3. Update wiki for documentation
4. Run full test suite before commit
5. Follow coding standards (see `.github/copilot-instructions.md`)

**Current Priorities:**
1. v1.1.14 planning and task breakdown
2. Checklist system implementation
3. Dashboard MVP development
4. Graphics system design

**How to Help:**
- Report bugs via GitHub Issues
- Suggest features in Discussions
- Contribute checklists to knowledge bank
- Test new features in beta
- Improve documentation

---

**Last Updated:** December 2, 2025
**Next Review:** Weekly (Mondays)
**Maintainer:** @fredporter
**License:** MIT
