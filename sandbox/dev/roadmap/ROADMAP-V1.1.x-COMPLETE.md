# 🗺️ uDOS Development Roadmap v1.1.x - v1.2.x

**Current Version:** v1.1.0 ✅ **COMPLETE**
**Status:** Production Ready (November 2025)
**Test Coverage:** 1,810 tests passing (100%)
**Next Round:** v1.1.1 - uCODE Modernization

> **Philosophy:** Development measured in STEPS and MOVES, not time. uDOS calculates work through cron patterns and organic pacing.

---

## 🎯 Current Status - v1.1.0 Stable Release

### What's in v1.1.0

✅ **Core System**
- 60+ commands with intuitive syntax
- Offline-first knowledge system
- Sandbox-based workspace architecture
- 5-tier knowledge system (PRIVATE → SHARED → GROUPS → COMMUNITY → KNOWLEDGE)

✅ **Knowledge Bank**
- 166+ comprehensive survival guides across 8 categories
- Multi-format diagram system (ASCII, Teletext, SVG)
- Quick reference materials and checklists
- Automated content generation workflows

✅ **Development Features**
- DEV MODE with master user authentication
- Unified configuration management (.env ↔ user.json sync)
- Asset management system (fonts, icons, patterns, CSS, JS)
- uCODE scripting language with markdown-compatible syntax

✅ **Infrastructure**
- Dual interface (Terminal CLI + Web GUI)
- Extension system with community marketplace ready
- 62 wiki pages of documentation (20,000+ lines)
- Complete test coverage (1,810 tests, 100% passing)

✅ **Web Extensions (Current)**
- Flask API Server (63 REST endpoints, port 5001)
- Terminal Extension (retro terminal with PetMe font)
- Teletext Extension (BBC teletext with WebSocket streaming)
- Dashboard Extension (NES Framework system dashboard)
- Desktop Extension (System 7 desktop environment)
- Markdown Viewer (GitHub-flavored with uCODE support)

---

## 🚀 v1.1.1 - uCODE Modernization

**Complexity:** Medium (38 steps across 4 moves)
**Dependencies:** None
**Status:** Planned

### Philosophy

Modern, minimal uCODE syntax with backward compatibility. Clean up verbosity, enable one-line commands, maintain human readability.

### Implementation Steps

**Move 1: Core Syntax (12 steps)**

1. Add `PRINT` command handler to `core/interpreters/ucode.py`
2. Implement template string support: `PRINT "Value: ${var}"`
3. Add deprecation warnings for `ECHO` usage
4. Create curly brace parser for blocks: `IF (condition) { }`
5. Extend `_handle_if_block()` for both syntaxes
6. Extend `_handle_for_loop()` for both syntaxes
7. Extend `_handle_while_loop()` for both syntaxes
8. Extend `_handle_function_definition()` for both syntaxes
9. Extend `_handle_try_block()` for both syntaxes
10. Add one-line command support
11. Test backward compatibility (old syntax still works)
12. Update error messages for new syntax

**Move 2: Migration Tools (8 steps)**

13. Create `ucode-migrate` command
14. Build AST analyzer for old syntax detection
15. Implement auto-conversion: `ECHO` → `PRINT`
16. Implement auto-conversion: `ENDIF` → `}`
17. Implement auto-conversion: `IF/THEN` → `IF (condition)`
18. Add dry-run mode for migration preview
19. Add backup creation before migration
20. Test migration on template files

**Move 3: Templates & Docs (10 steps)**

21. Update `core/data/templates/menu_system.uscript`
22. Update `core/data/templates/*.uscript` (all templates)
23. Update `sandbox/workflow/templates/*.uscript`
24. Update example scripts in `sandbox/ucode/`
25. Update wiki page: `uCODE-Language.md`
26. Create migration guide document
27. Add syntax comparison examples
28. Document both syntaxes (modern + traditional)
29. Update inline code comments
30. Create syntax quick reference card

**Move 4: Testing & Polish (8 steps)**

31. Write unit tests for PRINT command
32. Write unit tests for curly brace parsing
33. Write unit tests for one-line syntax
34. Write integration tests (mixed syntax files)
35. Test backward compatibility suite
36. Test migration tool on real scripts
37. Performance testing (parsing speed)
38. Documentation review and finalization

---

## ⚙️ v1.1.2 - Mission Control & Workflow Automation ⭐

**Complexity:** High (112 steps across 6 moves)
**Dependencies:** v1.1.1 (modern syntax recommended)
**Status:** Planned
**Location:** Core system with `extensions/core/mission-control/` UI

### Philosophy: "Always Know What's Next"

uDOS becomes a thoughtful assistant managing long-running projects through missions with milestones, cron-like scheduling, and visible progress. Not a race—steady, transparent progress.

### Core Concepts

**STEPS vs MOVES:**
- **STEP:** Single atomic operation (write file, call API, parse data)
- **MOVE:** Collection of steps forming a milestone (complete chapter, generate 10 guides)
- **MISSION:** Collection of moves toward a goal (write novel, build extension)

**Work Calculation:**
```
Mission: Write Novel
├─ Move 1: Outline (12 steps) → 12 STEPS
├─ Move 2: Chapter 1 (45 steps) → 45 STEPS
├─ Move 3: Chapter 2 (45 steps) → 45 STEPS
└─ Total: 102 STEPS across 3 MOVES

uDOS estimates: ~30-40 steps/hour (varies by complexity)
Not time-based, but work-based.
```

### Implementation Steps

**Move 1: Mission Core (25 steps)**

1. Create `core/services/mission_manager.py` skeleton
2. Define Mission data model (JSON schema)
3. Define Move data model (sub-goals)
4. Define Step data model (atomic operations)
5. Implement MISSION CREATE command
6. Implement MISSION START command
7. Implement MISSION PAUSE command
8. Implement MISSION RESUME command
9. Implement MISSION STATUS command
10. Implement MISSION PRIORITY command
11. Implement MISSION COMPLETE command
12. Create mission state persistence (JSON files)
13. Add mission workspace creation (sandbox/workflow/missions/)
14. Implement progress tracking (steps completed/total)
15. Add move completion detection
16. Add mission completion detection
17. Create mission templates system
18. Implement template variable substitution
19. Add mission validation (required fields)
20. Add dependency checking (missions requiring other missions)
21. Create mission lifecycle hooks (on_start, on_pause, on_complete)
22. Implement mission rollback (undo last move)
23. Add mission archival system
24. Add mission cloning (duplicate structure)
25. Unit tests for mission manager

**Move 2: Scheduler (Cron-like) (20 steps)**

26. Create `core/services/mission_scheduler.py` skeleton
27. Define Schedule data model
28. Implement SCHEDULE DAILY AT time syntax
29. Implement SCHEDULE EVERY interval syntax
30. Implement SCHEDULE WHEN condition syntax
31. Implement UNSCHEDULE task_id command
32. Add cron pattern parser (daily, hourly, every Xm)
33. Add datetime calculation engine
34. Implement background task queue
35. Add task priority system
36. Implement task execution loop
37. Add task timeout handling
38. Add task retry logic (3 attempts)
39. Implement task cancellation
40. Add task result logging
41. Create task state persistence
42. Add task dependencies (task B after task A)
43. Implement task condition evaluation (WHEN clauses)
44. Add scheduled task viewer (list all scheduled)
45. Unit tests for scheduler
46. Integration tests (schedule + execute)

**Move 3: Workflow Commands (28 steps)**

47. Implement LOG command (console + file)
48. Add log levels (info, warn, error, debug)
49. Implement LOAD_JSON command
50. Implement SAVE_JSON command
51. Implement CHECK_ENV command
52. Implement ENSURE_DIR command
53. Implement RUN_PYTHON command
54. Add --background flag for RUN_PYTHON
55. Implement PROCESS_RUNNING command
56. Implement SLEEP command
57. Implement TIMESTAMP command
58. Implement SAVE_CHECKPOINT command
59. Implement LOAD_CHECKPOINT command
60. Implement EXTRACT_METRIC command (regex extraction)
61. Implement COUNT_PATTERN command
62. Implement FIND_FILES command (glob patterns)
63. Implement COUNT_LINES command
64. Implement DISPLAY command (formatted output)
65. Implement CREATE_REPORT command (template-based)
66. Add template engine for reports
67. Implement MISSION_START (internal hook)
68. Implement MISSION_END (internal hook)
69. Add command error handling
70. Add command logging (all workflow commands logged)
71. Unit tests for each command
72. Integration tests (command chains)
73. Documentation for workflow commands
74. Example scripts showcasing commands

**Move 4: Resource Management (15 steps)**

75. Create `core/services/resource_manager.py` skeleton
76. Implement API quota tracking
77. Implement rate limiting (requests per minute)
78. Add quota reset timers
79. Implement disk space tracking
80. Add disk space warnings (90% full)
81. Implement CPU usage monitoring (low priority background)
82. Add memory usage tracking
83. Implement resource allocation per mission
84. Add resource conflict detection (2 missions want same API)
85. Implement resource priority system
86. Add resource dashboard view
87. Implement throttling (auto-slow when quota low)
88. Add resource usage logging
89. Unit tests for resource manager

**Move 5: Adaptive Output Pacing (12 steps)**

90. Create `core/services/output_pacer.py` skeleton
91. Implement character-by-character typing
92. Add configurable typing speed (chars/sec)
93. Implement speed ramping (slow → fast → slow)
94. Add viewport awareness (terminal size detection)
95. Implement fullness calculation (% of viewport used)
96. Add breathing pauses (200-500ms between sections)
97. Implement section detection (headers, paragraphs)
98. Add progress animation system (spinners, bars)
99. Implement organic pacing algorithm
100. Add user pause detection (wait for keypress when full)
101. Unit tests for output pacer
102. Integration tests (TUI rendering)

**Move 6: Dashboard Integration (10 steps)**

103. Create `extensions/core/mission-control/` web extension
104. Implement mission metrics dashboard
105. Create active missions panel (WebSocket real-time)
106. Create scheduled tasks panel
107. Create resource usage panel
108. Implement real-time progress bars
109. Add mission priority indicators (⚡ HIGH, 📊 MED, 🔧 LOW)
110. Add "Next up" suggestion display
111. Implement mission timeline view
112. Add completion celebration animations

---

## 🎨 v1.1.3 - Project Templates

**Complexity:** Medium (45 steps across 4 moves)
**Dependencies:** v1.1.2 (requires mission system)
**Status:** Planned
**Location:** `sandbox/workflow/templates/missions/`

### Objectives

Mission templates for common user projects: creative writing, research, learning, personal development.

### Template Categories

**Creative Writing (5 templates)**
- `novel` - Chapter-based fiction
- `play` - Script with scenes/acts
- `musical` - Script + lyrics + notes
- `screenplay` - Film/TV format
- `poetry-collection` - Curated anthology

**Research & Learning (4 templates)**
- `research-topic` - Academic research
- `explore-subject` - Deep-dive learning
- `learn-to-code` - Programming path (uCODE)
- `language-learning` - Foreign language

**Personal Development (4 templates)**
- `skill-building` - Structured acquisition
- `habit-tracking` - Daily habits
- `journal-project` - Reflective journaling
- `goal-achievement` - Milestone tracking

**Knowledge Creation (4 templates)**
- `knowledge-expansion` - Like survival guides
- `documentation-project` - Technical writing
- `tutorial-series` - Educational content
- `reference-library` - Curated resources

### Implementation Steps

**Move 1: Template Engine (12 steps)**

1. Create `sandbox/workflow/templates/missions/` directory structure
2. Define template metadata schema (config.json)
3. Create template variable system: `{{VAR_NAME}}`
4. Implement template loading system in mission_manager
5. Add variable substitution engine
6. Create template validation (required vars present)
7. Implement template inheritance (base → specific)
8. Add template listing command (MISSION TEMPLATES)
9. Add template preview (show structure before create)
10. Implement template customization during creation
11. Unit tests for template engine
12. Documentation for template creation

**Move 2: Creative Templates (15 steps)**

13. Create `novel` template (structure + prompts)
14. Create `play` template
15. Create `musical` template
16. Create `screenplay` template
17. Create `poetry-collection` template
18. Add genre-specific prompts for each
19. Create chapter/scene scaffolding
20. Add character template generators
21. Add worldbuilding templates
22. Create writing schedule generators
23. Add word count tracking
24. Add daily goal setting
25. Test each template with example project
26. Create template usage guides
27. User testing with creative writers

**Move 3: Research & Learning Templates (12 steps)**

28. Create `research-topic` template
29. Create `explore-subject` template
30. Create `learn-to-code` template (uCODE focus)
31. Create `language-learning` template
32. Add research methodology guides
33. Add citation tracking systems
34. Add progress milestone generators
35. Add quiz/assessment builders
36. Add resource library structures
37. Test templates with example projects
38. Create learning path visualizations
39. User testing with learners

**Move 4: Personal & Knowledge Templates (6 steps)**

40. Create remaining 8 templates (personal + knowledge)
41. Add habit tracking calendars
42. Add goal milestone systems
43. Add knowledge curation workflows
44. Test all templates
45. Final documentation and examples

---

## 🎨 v1.1.4 - ASCII/Teletext Graphics

**Complexity:** Medium (52 steps across 4 moves)
**Dependencies:** v1.1.2 (integrates with missions)
**Status:** Planned
**Location:** `core/services/graphics_compositor.py` + `core/data/graphics/`

### Objectives

Chunky teletext graphics integrated with mission workflows. Content generation becomes a mission with steps/moves.

### Implementation Steps

**Move 1: Graphics Library (15 steps)**

1. Create `core/data/graphics/blocks/` directory
2. Design teletext block character set
3. Create block component library (corners, edges, fills)
4. Define diagram types (flow, tree, grid, hierarchy)
5. Create diagram templates for each type
6. Implement color scheme system (terminal colors)
7. Add box-drawing character palette
8. Create arrow/connector components
9. Add text wrapping for diagram labels
10. Implement diagram scaling (fit to width)
11. Add diagram validation (proper connections)
12. Create diagram preview system
13. Unit tests for graphics library
14. Visual regression tests (snapshot testing)
15. Documentation for diagram creation

**Move 2: Diagram Compositor (12 steps)**

16. Create `core/services/graphics_compositor.py`
17. Implement layout engine (position elements)
18. Add automatic spacing calculation
19. Implement collision detection (overlapping elements)
20. Add alignment system (left, center, right)
21. Implement nesting (diagrams within diagrams)
22. Add layer system (foreground/background)
23. Implement rendering engine (to text)
24. Add export formats (plain text, markdown)
25. Create composition templates
26. Unit tests for compositor
27. Integration tests (complex diagrams)

**Move 3: Content Generation Mission (15 steps)**

28. Create `knowledge-expansion` mission template
29. Define guide generation as moves (1 guide = 1 move)
30. Break guide creation into steps (9 steps per guide):
    - Research topic (1 step)
    - Generate outline (1 step)
    - Write introduction (1 step)
    - Write materials section (1 step)
    - Write instructions (1 step)
    - Write safety section (1 step)
    - Create ASCII diagram (1 step)
    - Review and edit (1 step)
    - Save and index (1 step)
31. Implement AI generation with mission integration
32. Add throttling (respect API quotas via resource manager)
33. Add progress tracking (guides completed/total)
34. Implement checkpoint system (resume after pause)
35. Add quality validation step
36. Create batch processing workflow
37. Add manual review checkpoints
38. Implement diagram injection into guides
39. Add guide indexing step
40. Create completion report generation
41. Test full workflow (50 guides)
42. Optimize for efficiency

**Move 4: Mission Integration (10 steps)**

43. Add GENERATE GUIDE command
44. Implement guide type selection (simple/detailed/technical)
45. Add category filtering
46. Create diagram style selection
47. Add preview before save
48. Implement edit/refine workflow
49. Add bulk generation command
50. Create progress dashboard for content missions
51. Integration tests (full generation pipeline)
52. User acceptance testing

---

## 🎨 v1.1.5 - SVG Graphics Extension

**Complexity:** Low (22 steps across 3 moves)
**Dependencies:** v1.1.4 (optional enhancement)
**Status:** Planned
**Location:** `extensions/core/svg-generator/`

### Objectives

Optional SVG generation for advanced visualizations. Manual command only, not automated.

### Implementation Steps

**Move 1: Extension Setup (6 steps)**

1. Create `extensions/core/svg-generator/` structure
2. Define extension manifest (extension.json)
3. Create extension loader integration
4. Add extension activation command
5. Create extension documentation
6. Test extension loading

**Move 2: SVG Generation (10 steps)**

7. Implement GENERATE SVG command
8. Add style mode selection (lineart, blueprint, sketch, isometric)
9. Create AI prompt templates for each style
10. Implement Gemini API integration
11. Add SVG validation (well-formed XML)
12. Create post-processing pipeline
13. Add manual refinement workflow
14. Implement export to sandbox/drafts/
15. Add preview in terminal (ASCII conversion)
16. Create style customization options

**Move 3: Polish & Testing (6 steps)**

17. Add error handling (API failures)
18. Implement retry logic
19. Create usage examples
20. Write extension tests
21. Create user guide
22. User acceptance testing

---

## 🌐 v1.1.6 - uCODE Web Execution Extension

**Complexity:** Low (15 steps across 3 moves)
**Dependencies:** v1.1.2 (Mission Control)
**Status:** Planned
**Location:** `extensions/core/ucode-web/`

### Objectives

Execute .uscript files from web applications with real-time progress streaming.

### Implementation Steps

**Move 1: API Endpoints (5 steps)**

1. Create `extensions/core/ucode-web/` extension
2. Add `/api/script/execute` endpoint
3. Add `/api/script/status` endpoint
4. Add `/api/script/cancel` endpoint
5. Add `/api/script/list` endpoint (sandbox/workflow/missions)

**Move 2: Execution Engine (6 steps)**

6. Implement session-scoped script execution
7. Add WebSocket progress streaming
8. Create script execution queue (prevent conflicts)
9. Add script parameter passing from web
10. Implement execution time limits
11. Add execution logs (`sandbox/logs/web-scripts/`)

**Move 3: Web Interface (4 steps)**

12. Create web-based script editor
13. Add syntax highlighting for uCODE
14. Implement script templates (pre-loaded examples)
15. Add execution history viewer

---

## 🌍 v1.1.7 - POKE Online Extension (Sharing & Tunneling)

**Complexity:** High (35 steps across 4 moves)
**Dependencies:** v1.1.6 (needs script execution for shared missions)
**Status:** Planned
**Location:** `extensions/cloud/poke-online/`

### Philosophy

Local-first with optional peer-to-peer sharing. Minimal traffic, personal sharing only.

### Implementation Steps

**Move 1: Tunnel Infrastructure (10 steps)**

1. Create `extensions/cloud/poke-online/` extension
2. Integrate ngrok SDK or cloudflared
3. Create tunnel manager service
4. Implement POKE TUNNEL OPEN command
5. Implement POKE TUNNEL CLOSE command
6. Add tunnel status monitoring
7. Create tunnel URL generator
8. Add automatic reconnection
9. Implement tunnel analytics (visitors, bandwidth)
10. Add tunnel expiration (24h default)

**Move 2: User-to-User Sharing (12 steps)**

11. Create sharing manager service
12. Implement POKE SHARE command
13. Add permission system (read/write/execute)
14. Create share token generation
15. Implement share revocation
16. Add share expiration
17. Create share analytics (who accessed when)
18. Implement share notifications
19. Add share templates (common permission sets)
20. Create share history log
21. Implement collaborative editing (basic)
22. Test multi-user scenarios

**Move 3: Group Coordination (8 steps)**

23. Create group manager service
24. Implement POKE GROUP CREATE command
25. Add group member management
26. Create group workspace (shared sandbox)
27. Implement group permissions
28. Add group chat (via WebSocket)
29. Create group activity feed
30. Test group workflows

**Move 4: Security & Polish (5 steps)**

31. Implement rate limiting (prevent abuse)
32. Add content moderation hooks
33. Create privacy controls
34. Write security documentation
35. Penetration testing

---

## 🔒 v1.1.8 - Cloud Bridge Extension (Isolation Layer)

**Complexity:** Medium (25 steps across 3 moves)
**Dependencies:** None (standalone isolation)
**Status:** Planned
**Location:** `extensions/cloud/bridge/`

### Philosophy

**Local-first, cloud-optional.** ALL internet access requires explicit user permission.

### Implementation Steps

**Move 1: Permission System (8 steps)**

1. Create `extensions/cloud/bridge/` extension
2. Create permission manager service
3. Define permission schema (scope, expiry, quota)
4. Implement CLOUD ALLOW command
5. Implement CLOUD REVOKE command
6. Implement CLOUD STATUS command
7. Add permission UI (web dashboard)
8. Create permission audit log (`sandbox/logs/cloud.log`)

**Move 2: Provider Integration (10 steps)**

9. Create provider abstract base class
10. Implement GitHub provider (sync, backup)
11. Implement Gemini provider (AI, quota management)
12. Implement ngrok provider (tunneling)
13. Implement IPFS provider (decentralized storage)
14. Add provider health monitoring
15. Create provider fallback logic
16. Implement provider analytics
17. Add provider cost tracking (API quotas)
18. Test each provider

**Move 3: Sync Engine (7 steps)**

19. Create selective sync manager
20. Implement conflict resolution
21. Add sync scheduling (cron-like)
22. Create sync preview (show what will change)
23. Implement sync rollback
24. Add sync progress tracking
25. Test sync reliability

---

## 🖥️ v1.2.0 - Tauri Desktop App

**Complexity:** High (45 steps across 4 moves)
**Dependencies:** v1.1.6+ (all web features stable)
**Status:** Planned
**Location:** `uDOS-Desktop/` (separate Tauri project)

### Philosophy

Native desktop experience with full offline capability and deep OS integration.

### Why Tauri Over Electron

- **Size:** ~3MB vs ~100MB
- **Performance:** Uses system webview (not Chromium)
- **Integration:** Rust backend + HTML/JS frontend
- **Offline:** Native by design
- **Security:** Sandboxed by default

### Implementation Steps

**Move 1: Tauri Setup (10 steps)**

1. Initialize Tauri project (`uDOS-Desktop/`)
2. Configure Rust toolchain
3. Set up Python embedding (PyO3 or subprocess)
4. Create app configuration (`tauri.conf.json`)
5. Design app icon and branding
6. Set up native menus
7. Implement system tray
8. Add auto-updater
9. Configure build pipeline
10. Test basic app launch

**Move 2: uDOS Integration (15 steps)**

11. Create Rust ↔ Python bridge
12. Implement command execution from Rust
13. Add uCODE interpreter embedding
14. Create native file dialogs
15. Implement clipboard integration
16. Add native notifications
17. Create global keybindings
18. Implement window management
19. Add full screen mode
20. Create session persistence
21. Implement crash recovery
22. Add performance monitoring
23. Test integration reliability
24. Optimize startup time
25. Memory profiling

**Move 3: Frontend Integration (12 steps)**

26. Symlink web extensions (`extensions/core/*`)
27. Configure asset bundling
28. Implement theme system integration
29. Add native font rendering
30. Create offline asset caching
31. Implement service worker
32. Add PWA manifest
33. Create desktop-specific UI
34. Implement drag-and-drop
35. Add multi-window support
36. Test UI responsiveness
37. Accessibility audit

**Move 4: Distribution (8 steps)**

38. Configure platform builds (macOS, Windows, Linux)
39. Create installers (DMG, MSI, AppImage)
40. Set up code signing
41. Implement auto-updater backend
42. Create release pipeline
43. Write installation documentation
44. Beta testing program
45. Public release

---

## 📊 Total Work Summary

### v1.1.x Series (Core Enhancements)

```
v1.1.1:  38 steps (uCODE modernization)
v1.1.2: 112 steps (Mission Control) ⭐ FOUNDATION
v1.1.3:  45 steps (Project Templates)
v1.1.4:  52 steps (ASCII Graphics)
v1.1.5:  22 steps (SVG Extension)
────────────────────────────────────
Total:  269 steps across 5 releases
```

### Extension Ecosystem

```
v1.1.6:  15 steps (uCODE Web Extension)
v1.1.7:  35 steps (POKE Online Extension)
v1.1.8:  25 steps (Cloud Bridge Extension)
────────────────────────────────────
Total:   75 steps across 3 extensions
```

### Desktop Era

```
v1.2.0:  45 steps (Tauri Desktop App)
────────────────────────────────────
Total:   45 steps
```

### Grand Total

**389 steps** across 9 major releases

---

## 🏗️ Development Workflow

All development work happens in `/sandbox/dev/`:

```
sandbox/dev/
├── roadmap/
│   ├── ROADMAP-V1.1.x-COMPLETE.md  # This file
│   └── ROADMAP-ARCHIVE.MD          # Historical
├── current-round.md                # Active development tracking
├── testing-notes.md                # Test results and bugs
├── feature-specs/                  # Feature specifications
└── design-docs/                    # Design documents
```

### Round-Based Development (Measured in Steps)

Each development round follows this structure:

1. **Planning** - Break work into steps (atomic operations)
2. **Implementation** - Execute steps sequentially or parallel
3. **Testing** - Validate each step and overall moves
4. **Documentation** - Document completed moves
5. **Release** - Tag version when all moves complete

### Work Metrics

**Step Complexity:**
- **Trivial:** 5-15 minutes (create file, write function)
- **Simple:** 15-45 minutes (implement command, write tests)
- **Medium:** 45-120 minutes (build service, complex logic)
- **Complex:** 2-6 hours (system integration, architecture)

### Workflow Commands

```bash
# Start new development round
cd sandbox/dev
vim current-round.md

# Track steps completed
git add -A
git commit -m "v1.1.1 Step 12/38: Curly brace parsing complete"

# Run tests after each step
pytest sandbox/tests/

# Mark moves complete
echo "Move 1 complete: Core syntax (12/38 steps)" >> current-round.md

# Release when all steps done
git tag v1.1.1
git push origin main --tags
```

---

## 🎯 Core Principles

uDOS development follows these principles:

🌍 **Offline-First** - Full functionality without internet
🤝 **Barter Over Currency** - Exchange knowledge, not wealth
🧠 **5-Tier Knowledge** - PRIVATE → SHARED → GROUPS → COMMUNITY → KNOWLEDGE
🎯 **Practical Over Political** - Real survival skills that matter
🎮 **Learn by Creating** - Education through interactive experiences
👤 **User-Owned** - You control your data, not corporations
⚙️ **Work in Steps** - Measured progress, not arbitrary time
🔌 **Extensions First** - Advanced features as optional extensions
🔒 **Permission Gates** - Internet access requires explicit user consent

---

## 🔌 Extension Architecture

### Extension Locations

```
extensions/
├── core/                           # Core web extensions
│   ├── terminal/                   # Retro terminal UI
│   ├── teletext/                   # BBC teletext display
│   ├── dashboard/                  # System dashboard
│   ├── desktop/                    # System 7 desktop
│   ├── markdown/                   # Markdown viewer
│   ├── mission-control/            # Mission dashboard (v1.1.2)
│   ├── svg-generator/              # SVG graphics (v1.1.5)
│   └── ucode-web/                  # Web script execution (v1.1.6)
│
├── cloud/                          # Cloud features (opt-in only)
│   ├── poke-online/                # Sharing & tunneling (v1.1.7)
│   └── bridge/                     # Cloud isolation layer (v1.1.8)
│
├── play/                           # Game mechanics
│   ├── map-engine/
│   └── xp-system/
│
└── cloned/                         # External tools (git ignored)
```

### Extension Principles

1. **Optional by Default** - All extensions can be disabled
2. **Permission-Based** - Internet access requires explicit grant
3. **Isolated** - Extensions cannot break core
4. **Composable** - Extensions can depend on each other
5. **Documented** - Every extension has README.md
6. **Tested** - Extension test suite required

---

## 📞 Support

**Documentation:** 62 wiki pages covering everything
**Community:** GitHub Discussions for Q&A
**Issues:** GitHub Issues for bug reports
**Development:** sandbox/dev/ for current work

---

**Ready to contribute?** Check `sandbox/dev/current-round.md` for active work!
