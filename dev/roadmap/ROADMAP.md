# 🗺️ uDOS Development Roadmap

**Current Version:** v1.1.13 ✅ **STABLE** (Project Structure Reorganization)
**Status:** Production ready, 111/111 tests passing
**Last Updated:** December 2, 2025

> **Philosophy:** Development measured in STEPS and MOVES, not time. Work proceeds through organic pacing and cron patterns.

---

## 📍 Current Release: v1.1.13 (December 2025)

**Status:** ✅ **STABLE** - Production ready
**Test Coverage:** 111/111 tests passing (100%)

### What's New

- **Project Structure:** Clean separation between `/dev/` (tracked) and `/memory/` (unified user workspace)
- **Development Workspace:** Organized tools, roadmaps, and session logs in `/dev/`
- **User Workspace:** Consolidated `/sandbox/` → `/memory/` for simpler mental model
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
│   ├── missions/           # Mission definitions and state
│   ├── workflows/          # Workflow templates and active runs
│   ├── checklists/         # Checklist progress and state
│   ├── archived/           # Completed/archived work
│   ├── user/               # User profiles and persistent settings
│   └── logs/               # Session and runtime logs
│
├── core/                   # Core system (required, stable)
├── extensions/             # Extension system
├── knowledge/              # Public knowledge bank (read-only)
└── wiki/                   # GitHub wiki (documentation)
```

**Note:** `/memory/` replaces old `/sandbox/` split for v1.1.13+ unified workspace.

---

## 🎯 Active Development: v1.1.14 - Unified Task Management System

**Target:** Q1 2026
**Status:** 🔄 Planning phase
**Complexity:** Medium (consolidation + new features)

### Vision

Unify isolated workflow/mission/checklist systems into a cohesive JSON-based task management architecture with real-time dashboard visualization and gameplay variable integration.

### Core Objectives

1. **Checklist System** - JSON-based interactive checklists with progress tracking
2. **Workflow Integration** - Migrate .uscript → .upy, expose WORKFLOW commands in main CLI
3. **Mission-Workflow Linking** - Bidirectional integration between missions and workflows
4. **Dashboard MVP** - Flask web server with NES-style retro UI
5. **Variable System Extension** - MISSION/CHECKLIST/WORKFLOW scopes for $VARIABLES
6. **Archive Command** - Proper archival system for completed work

### Design Decisions

**Dashboard Implementation:** ✅ **Flask Web Server**
- Real-time updates via polling/WebSocket
- Interactive controls (pause/resume missions)
- NES.css styling (8-bit Nintendo aesthetic)
- Multiple widget types (progress bars, meters, status panels)

**Checklist Progress Persistence:** ✅ **`memory/user/checklist_state.json`**
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

#### Phase 1: Infrastructure (Week 1-2)

**1. Checklist System Foundation**
- Create `core/data/schemas/checklist.schema.json`
- Implement `core/services/checklist_manager.py` (~200 lines)
- Create `core/commands/checklist_handler.py` (~300 lines)
- Add CHECKLIST command routing in `core/uDOS_commands.py`
- Convert 3 existing checklists to JSON:
  - `knowledge/checklists/emergency/72-hour-bug-out-bag.md`
  - `knowledge/checklists/emergency/first-aid-kit-inventory.md`
  - `knowledge/checklists/daily/water-storage-maintenance.md`

**2. Workflow Migration**
- Convert 8 `.uscript` files to `.upy` using `dev/tools/migrate_upy.py`:
  - `memory/workflows/examples/nano_banana_*.uscript` (4 files)
  - `memory/workflows/batch_svg_generation.uscript`
  - `memory/workflows/templates/workflow_template.uscript`
  - `memory/workflows/knowledge_generation.uscript`
- Update workflow templates to `.upy` format
- Expose WORKFLOW commands in main CLI (currently hidden in handler)

**3. Archive Handler**
- Create `core/commands/archive_handler.py`
- Commands: `ARCHIVE mission|workflow|checklist <id>`
- Storage: `memory/archived/` with timestamps
- Metadata: JSON files with completion stats
- Integration with existing cleanup commands (CLEAN, TIDY)

#### Phase 2: Integration (Week 3-4)

**4. Variable System Extension**
- Extend `core/commands/variable_handler.py` with new scopes:
  - `MISSION.*` - Access mission state from `mission_manager.py`
  - `CHECKLIST.*` - Access checklist progress from `checklist_manager.py`
  - `WORKFLOW.*` - Access workflow state from checkpoints
- Examples:
  - `GET MISSION.PROGRESS` → "45/55 (81.8%)"
  - `GET CHECKLIST.COMPLETED_ITEMS` → "127/156"
  - `GET WORKFLOW.PHASE` → "monitoring"

**5. System Linking**
- Add `workflow_script` field to `memory/workflows/templates/mission_template.json`
- Add `related_guides`, `related_checklists` to checklist schema
- Update `core/commands/guide_handler.py` to display related checklists
- Sync mission metrics from workflow checkpoints automatically

**6. Dashboard MVP**
- Create `extensions/web/dashboard/` structure:
  ```
  dashboard/
  ├── extension.json         # Extension metadata
  ├── server.py              # Flask application
  ├── static/
  │   ├── nes.css           # Nintendo 8-bit styling
  │   ├── dashboard.js      # Real-time updates
  │   └── icons/            # Retro icons
  └── templates/
      ├── index.html        # Main dashboard
      └── widgets/          # Widget templates
  ```
- Core widgets:
  - Mission progress bars (current mission, all missions)
  - Checklist completion meters (active checklists)
  - Workflow phase indicators (current phase, iterations)
  - Resource usage graphs (retro-styled)
- Real-time polling (5-second refresh)
- Port: 5050 (configurable)

#### Phase 3: Content & Polish (Week 5-6)

**7. Checklist Library Expansion**
- Auto-generate 7+ checklists from existing guides
- Target categories:
  - Emergency: Bug-out bag, First aid, Evacuation
  - Daily: Water check, Fire management, Security patrol
  - Projects: Shelter construction, Tool making
- Validate all against schema
- Add to `knowledge/checklists/`

**8. Documentation**
- Consolidate workflow docs (INDEX.md, OVERVIEW.md → wiki)
- Create `wiki/Systems-Integration.md` (mission ↔ workflow ↔ checklist)
- Update `wiki/Command-Reference.md` with new commands:
  - CHECKLIST (CREATE, LIST, LOAD, COMPLETE, STATUS, PROGRESS)
  - ARCHIVE (mission, workflow, checklist)
  - WORKFLOW (expose in main CLI)
- Create `wiki/Dashboard-Guide.md` (setup, usage, widgets)

### Success Metrics

**Checklists:**
- ✅ 10+ checklists in JSON format
- ✅ Full CRUD operations
- ✅ Progress tracking with persistence
- ✅ Guide integration

**Workflows:**
- ✅ Zero .uscript files (all migrated to .upy)
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
- ✅ ARCHIVE command functional
- ✅ Timestamps and metadata preserved
- ✅ Easy restore capability

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
