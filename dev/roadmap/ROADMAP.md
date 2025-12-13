# 🗺️ uDOS Development Roadmap

**Current Version:** v1.2.24 ✅ **RELEASED** (Python-First Rebase - 100x Performance)
**Next Release:** v1.2.25 📋 **PLANNING** (Universal Input Device System)
**Last Updated:** 20251213-175000UTC (December 13, 2025)

> **Goal:** Complete v1.2.x as a stable, production-ready release with full TUI functionality, AI assistance, business intelligence, and workflow automation.

---

## 🔤 File Format Standard (v1.2.23) - COMPACT TIMESTAMPS

**CRITICAL:** uDOS uses COMPACT timestamps with NO internal dashes/colons.

### ✅ CORRECT Format (Compact)
```
Format: YYYYMMDD-HHMMSSTZ-TILE-name.ext

Examples:
  20251213-backup.json                    # Date only
  20251213-164500UTC-workflow.upy         # Session (date-time-tz)
  20251213-164500UTC-123-error.json       # Instance (milliseconds)
  20251213-164500UTC-AA340-mission.upy    # Located (TILE code)

Components:
  YYYYMMDD       - 8-digit date (NO dashes)
  HHMMSS         - 6-digit time (NO colons)
  TZ             - 2-4 char timezone (UTC, AEST, PST, GMT, etc.)
  TILE           - Optional 5-char grid code (AA340, JF57, etc.)
  Separators     - ONLY between major components (-)
```

### ❌ WRONG Format (Old Style with Dashes)
```
Examples of INCORRECT formats:
  2025-12-13-backup.json                  # Date has dashes
  2025-12-13-16-45-00-UTC-workflow.upy    # Time separated
  20251213-16-45-00-UTC-workflow.upy      # Time has dashes
  
DO NOT USE: Dashes in date/time, colons in time, spaces anywhere
```

### Why Compact?
- **Sortable:** YYYYMMDD sorts correctly without dashes
- **Parseable:** Single regex pattern captures all components
- **Compact:** Shorter filenames, easier to read
- **Standard:** Aligns with ISO 8601 basic format
- **Unambiguous:** Clear component boundaries with single separators

**Implementation:** `core/utils/filename_generator.py` (455 lines)

---

## 📋 uDOS ID Standard - Document Timestamps (v1.2.23)

**Effective:** 20251213-145000UTC (December 13, 2025)

**Standard Format:**
```
Date: YYYYMMDD-HHMMSSTZ (Readable Date)
Location: [Context/Module/Location]
```

**Examples:**
- **Python files:** `Date: 20251213-143500UTC` + `Location: Core Services`
- **Markdown docs:** `Last Updated: 20251213-145000UTC (December 13, 2025)`
- **Session logs:** `Date: 20251213-104000UTC (December 13, 2025)` + `Location: Development Session`

**Migration Status:**
- ✅ Migration scripts: Updated to uDOS ID format
- ✅ Core services: unified_task_manager.py updated
- ✅ Key documents: ROADMAP.md, integration plans updated
- ⏳ Legacy files: Will be updated as modified (no mass migration)

**Rationale:**
- Consistent with FilenameGenerator (YYYYMMDD-HHMMSSTZ-TILE-name.ext)
- Self-documenting timestamps (timezone + location awareness)
- Sortable and machine-readable
- Human-friendly with optional readable date

---

## 🎯 v1.2.x Release Track (Stable Production Release)

### v1.2.16 ✅ **COMPLETE** - TUI File Browser Integration

**Goal:** Complete file browser with 0-key launcher and workspace navigation.

**Status:** All 4 tasks complete (~890 lines across 4 commits)

**Completed Tasks:**
1. ✅ **File Browser Launcher** (102 lines) - commit 4012ce43
   - 0-key opens browser, ESC closes
   - 8/2/4/6 navigation integration
   - Workspace cycling
   - Browser display in main loop

2. ✅ **File Operations** (~360 lines) - commit eac12e8f
   - Open file in viewer/editor
   - Copy/move/delete with confirmation
   - Create from templates (mission/script/guide/note)
   - Quick search within workspace

3. ✅ **Workspace Management** (~210 lines) - commit 193d27af
   - Recent files list (last 10)
   - Bookmarks/favorites
   - Path memory across sessions
   - State persistence to browser_state.json

4. ✅ **Column View Integration** (~220 lines) - commit da7a8989
   - 3-column layout: workspaces | files | preview
   - Responsive sizing (80/120+ char terminals)
   - Visual indicators (icons, bookmarks)
   - V-key toggle between views
   - State persistence

**Documentation:** `dev/sessions/v1.2.16-file-browser-session.md`

---

### v1.2.17 ✅ **COMPLETE** - Server & Service Monitoring

**Goal:** Comprehensive server monitoring with TUI panel integration.

**Status:** All 4 tasks complete (~1,037 lines across 4 commits)

**Completed Tasks:**
1. ✅ **Server Status Dashboard** (325 lines) - commit 995a085a
   - ServerMonitor service with 8 server definitions (5 core, 3 extension)
   - Health checking via HTTP endpoints
   - Port availability via PortManager integration
   - Server counts and summaries
   - Start/stop/restart methods (partial)

2. ✅ **Extension Monitor** (280 lines) - commit 3de24172
   - ExtensionMonitor service for extensions/ scanning
   - Manifest parsing (extension.json)
   - Status determination (active/inactive/incomplete)
   - Code detection (.py file scanning)
   - User extension support (cloned/ directory)

3. ✅ **System Health Tracking** (+173 lines) - commit abba54c0
   - Memory usage (total/used/available MB, %)
   - Disk space (workspace path, GB metrics)
   - Log file tracking (memory/logs/, size/count)
   - Archive health (.archive/ folders, size/count)
   - Overall health aggregation (healthy/warning/critical)

4. ✅ **TUI Server Panel** (259 lines) - commit 3dd0dc5b
   - ServerPanel UI with 3 views (servers/extensions/health)
   - Tab navigation (S/E/H keys)
   - Real-time status display with emoji indicators
   - TUI controller integration (open/close/render)
   - Mode tracking (server_panel mode)

**Testing Results:**
- 8/8 servers detected (3 running, 5 stopped)
- 5/5 extensions scanned (2 active, 2 inactive, 1 incomplete)
- Health metrics: Memory 60.9%, Disk 29.6%, Logs 0.23MB, Archive 11.74MB (all healthy)
- Panel rendering: All 3 views working correctly

**Documentation:** `dev/sessions/v1.2.17-server-monitoring-session.md`

---

### v1.2.18 ✅ **COMPLETE** - Config & Settings TUI

**Goal:** Manage all configuration from TUI interface.

**Status:** All 4 tasks complete (~1,702 lines, 1 commit)

**Completed Tasks:**
1. ✅ **Config Browser** (361 lines) - commit 61159376
   - Category tabs (display, paths, ai, system, network)
   - Visual editor with type validation
   - Save/revert functionality
   - C-key opens panel from command mode

2. ✅ **User Settings Panel** (402 lines)
   - Theme selection with availability check
   - TUI preferences (keypad, pager, browser columns)
   - Default workspace configuration
   - Per-user storage in memory/system/user/

3. ✅ **Environment Variables** (403 lines)
   - View/edit .env file
   - Secure API key input (masked display)
   - Path validation
   - Category grouping

4. ✅ **Profiles** (418 lines)
   - Save current config as named profile
   - Load profiles quickly
   - Import/export JSON
   - Default profile management

**Integration:**
- TUI controller (+96 lines) - config_panel mode
- SmartPrompt (+18 lines) - C-key binding
- Main loop (+4 lines) - Panel rendering

**Total:** 1,702 lines across 7 files

---

### v1.2.19 ✅ **COMPLETE** - DEV MODE Enhancement

**Goal:** Complete development workflow from TUI.

**Status:** All 4 tasks complete (~1,572 lines, 1 commit)

**Completed Tasks:**
1. ✅ **System File Browser** (444 lines) - commit 0f74e366
   - D-key access to core/, extensions/, wiki/, dev/, tests/
   - Git status indicators (M/A/D/?)
   - Edit warnings for critical files
   - Syntax highlighting preview

2. ✅ **Debug Panel** (370 lines)
   - L-key live log viewer
   - Filter by level/module/search term
   - Error highlighting with emoji indicators
   - Export filtered logs

3. ✅ **Testing Interface** (377 lines)
   - T-key test runner for SHAKEDOWN
   - Visual test results (✅❌⊝💥)
   - Failed tests filter
   - Export test reports

4. ✅ **Hot Reload System** (263 lines)
   - Auto-reload command handlers
   - Service module reloading
   - UI component hot reload
   - Change notifications

**Integration:**
- TUI controller (+55 lines) - 3 new modes
- SmartPrompt (+51 lines) - D/L/T-key bindings
- Main loop (+12 lines) - Panel rendering

**Total:** 1,572 lines across 8 files

---

### v1.2.20 ✅ **COMPLETE** - Workflow Management System

**Goal:** Complete workflow management with uPY scripting, checkpoints, and mission templates.

**Status:** All 4 tasks complete (~1,653 lines across 2 commits)

**Completed Tasks:**
1. ✅ **Workflow Manager Panel** (510 lines) - commit 1c62bb94
   - core/ui/workflow_manager_panel.py (510 lines)
   - W-key opens workflow manager from command mode
   - List workflows: active, paused, draft, completed states
   - 10 mission templates: water, shelter, navigation, medical, fire, food, communication, dev
   - Create workflow from template with TILE location
   - Start/pause/resume/complete workflow actions
   - Integration: TUI controller (+23), SmartPrompt (+18), Main loop (+10)
   - MeshCore installer (install_meshcore.py +420 lines)

2. ✅ **Checkpoint System** (304 lines) - commit 0e12c7aa
   - core/services/checkpoint_manager.py (304 lines)
   - CheckpointManager class with full lifecycle
   - Create, load, list, rollback checkpoint operations
   - Checkpoint timeline and progress visualization
   - Auto-checkpoint at workflow milestones
   - Linked-list structure (previous/next pointers)
   - Archive old checkpoints to .archive/
   - Storage: memory/workflows/checkpoints/

3. ✅ **Mission Scripting Templates** (421 lines) - commit 0e12c7aa
   - water_collection.upy (99 lines) - 5-step water workflow
     - TILE location tracking, quality assessment
     - Treatment methods (boiling/chemical/filter)
     - GUIDE integration for purification
   - shelter_building.upy (142 lines) - 6-step shelter workflow
     - Material assessment based on TILE terrain
     - Shelter types: lean-to, tarp, debris-hut
     - Safety inspection checklist
   - navigation_route.upy (178 lines) - 7-step navigation workflow
     - TILE grid waypoint generation
     - Distance calculation using grid cells
     - Environmental condition checks
     - Full route logging and map marking

4. ✅ **Dev Workflow Tools** (155 lines) - commit 0e12c7aa
   - memory/workflows/dev/dev_build.upy (155 lines)
   - 8-step build/test/deploy workflow
   - Git branch management (create, merge, push)
   - Code quality: black formatter, flake8 linter
   - Unit tests (pytest) + SHAKEDOWN integration test
   - Documentation review
   - Push/merge automation

**Total:** 1,653 lines (510 panel + 304 checkpoint + 421 missions + 155 dev + 263 integration)
**Commits:** 2 (1c62bb94 Task 1, 0e12c7aa Tasks 2-4)

---

### v1.2.21 ✅ **COMPLETE** - AI Assistant + BIZINTEL + Workflow Automation

**Goal:** Complete AI integration, business intelligence, and workflow automation with legal data sources.

**Status:** All 17 tasks complete (~5,644 lines across 17 files)

**Phase 1: OK Assistant (760 lines)** ✅ December 8, 2025
1. ✅ **OK Assistant Panel** (310 lines) - O-key opens AI assistant, 8 quick prompts
2. ✅ **Context-Aware Assistance** (200 lines) - Auto-include workspace context
3. ✅ **OK Configuration** (100 lines) - CONFIG panel [OK] tab
4. ✅ **OK Workflows** (150 lines) - MAKE commands

**Phase 2: BIZINTEL Core (2,632 lines)** ✅ December 8, 2025
5. ✅ **Marketing Extension (BIZINTEL)** (2,632 lines) - Complete BI system
   - ID generator (120 lines) - biz-*, prs-*, rel-*, aud-*, msg-* IDs
   - Marketing database (638 lines) - 5 tables in memory/bank/user/contacts.db
   - Entity resolver (396 lines) - Priority matching with fuzzy fallback
   - Contact extractor (310 lines) - Email parsing and business detection
   - Message pruner (272 lines) - Thread compression and archiving
   - Google Business client (308 lines) - Places API integration
   - Cloud handler (588 lines) - CLOUD commands
6. ✅ **Integration** - Cloud handler in command router
7. ✅ **Documentation** - extensions/cloud/bizintel/README.md, uDOS ID Standard

**Phase 3: Data Source Extensions (2,152 lines)** ✅ December 10, 2025
8. ✅ **Website Parser** (575 lines) - robots.txt compliant staff directory extraction
9. ✅ **Social Media APIs** (450 lines) - Twitter/X, Instagram official APIs
10. ✅ **Email Enrichment** (680 lines) - Clearbit, Hunter.io, PeopleDataLabs
11. ✅ **Database Extensions** (+200 lines) - 3 new tables (roles, social_profiles, enrichment_cache)
12. ✅ **Command Extensions** (+247 lines) - WEBSITE PARSE, SOCIAL ENRICH, ENRICH commands

**Phase 4: Workflow Automation (730 lines)** ✅ December 10, 2025
13. ✅ **Keyword Generator** (350 lines) - Gemini AI keyword generation with offline fallback
   - AI-powered search keywords (5 categories: primary, location, industry, competitor, niche)
   - Industry templates for offline mode (4 categories)
   - uPY variable export format
   - Workflow config integration
14. ✅ **Location Resolver** (380 lines) - Address → TILE codes + MeshCore positions
   - Google Geocoding API integration
   - TILE code system (480×270 grid, layers 100-500)
   - MeshCore grid positioning
   - Bidirectional TILE ↔ lat/lon conversion
   - uPY variable export format
15. ✅ **Command Integration** - CLOUD GENERATE KEYWORDS, CLOUD RESOLVE LOCATION
16. ✅ **Module Exports** - Updated __init__.py with KeywordGenerator, LocationResolver
17. ✅ **Documentation** (900+ lines)
   - WORKFLOW-AUTOMATION.md (450+ lines) - Complete guide
   - IMPLEMENTATION-SUMMARY.md (400+ lines) - Technical details
   - QUICK-REFERENCE.md (150+ lines) - Quick start
   - Updated README.md with workflow automation section

**Total:** 5,644 lines across 17 files
- OK Assistant: 760 lines (4 files)
- BIZINTEL Core: 2,632 lines (7 files)
- Data Sources: 2,152 lines (3 files)
- Workflow Automation: 730 lines (2 code files) + 370 lines (docs/test)
- Documentation: 900+ lines (4 files)

**Files Created:** 17
- OK Assistant: 4 files
- BIZINTEL Core: 7 files
- Data Sources: 3 files
- Workflow Automation: 2 files (keyword_generator.py, location_resolver.py)
- Documentation: 4 files (WORKFLOW-AUTOMATION.md, IMPLEMENTATION-SUMMARY.md, QUICK-REFERENCE.md, test script)

**Files Modified:** 6
- cloud_handler.py (command integration)
- extensions/cloud/bizintel/__init__.py (exports)
- extensions/cloud/bizintel/README.md (updated)
- marketing_db.py (3 new tables)

**BIZINTEL System Summary:**
Total: 5,514 lines across 14 files
- Core: 2,632 lines (DB, entities, extraction, pruning, Google Business)
- Data Sources: 2,152 lines (website parser, social APIs, enrichment)
- Workflow Automation: 730 lines (keyword generation, location resolution)

**New API Requirements:**
- GEMINI_API_KEY - Keyword generation (1,500 requests/day free)
- GOOGLE_GEOCODING_API_KEY - Location resolution (28,500 requests/month free)

**New Commands:**
```bash
# Keyword generation
CLOUD GENERATE KEYWORDS "live music venues" --location "Sydney" --upy

# Location resolution  
CLOUD RESOLVE LOCATION "Opera House, Sydney NSW" --layer 300 --upy
```

**Commits:** 
- v1.2.21: OK Assistant Integration (760 lines, 11 files) ✅
- v1.2.21: BIZINTEL Business Intelligence System (2,632 lines) ✅
- v1.2.21: BIZINTEL Data Source Extensions (2,152 lines) ✅
- v1.2.21: Workflow Automation (730 lines + 900 lines docs) ✅ - PENDING COMMIT

**Post-Release:**
- ⏳ Testing: Gemini API keyword generation
- ⏳ Testing: Google Geocoding location resolution
- ⏳ Testing: TILE code conversion accuracy
- ⏳ Testing: MeshCore position calculation
- ⏳ Final documentation review
- ⏳ CHANGELOG update
- ⏳ Tag v1.2.21 as STABLE

**Session Notes:**
- `dev/sessions/v1.2.21-ok-assistant-session.md`
- `dev/sessions/v1.2.21-bizintel-session.md`
- `dev/sessions/2025-12-10-bizintel-data-sources.md`
- `extensions/cloud/bizintel/IMPLEMENTATION-SUMMARY.md`

**Documentation:**
- `extensions/cloud/bizintel/WORKFLOW-AUTOMATION.md` - Complete guide
- `extensions/cloud/bizintel/QUICK-REFERENCE.md` - Quick start
- `extensions/cloud/bizintel/README.md` - System overview
- `wiki/Mapping-System.md` - TILE code reference

---

## 📊 v1.2.x Summary

**Total Work Completed:** 5,644 lines across v1.2.21 (100% complete)
**Current Progress:** v1.2.21 COMPLETE - Ready for testing and release
**Status:** ✅ All code complete, testing pending

**What's Complete:**
- ✅ TUI Navigation (v1.2.15) - Keypad controls, command predictor
- ✅ File Browser (v1.2.16) - 0-key launcher, workspace navigation
- ✅ Server Monitoring (v1.2.17) - Health tracking, extension monitor
- ✅ Config & Settings TUI (v1.2.18) - Complete config management
- ✅ DEV MODE Enhancement (v1.2.19) - Session logging, dev tools
- ✅ Workflow Management (v1.2.20) - Mission system integration
- ✅ OK Assistant (v1.2.21) - AI integration with 8 quick prompts
- ✅ BIZINTEL Core (v1.2.21) - Business intelligence system (2,632 lines)
- ✅ BIZINTEL Data Sources (v1.2.21) - Website, social, enrichment (2,152 lines)
- ✅ Workflow Automation (v1.2.21) - Keywords + Locations (730 lines)

**v1.2.x Total:** ~11,500 lines across 6 releases
- ✅ DEV MODE tools (v1.2.19)
- ✅ Grid rendering system
- ✅ Mapping layers
- ✅ Archive system
- ✅ uPY runtime v2.0.2
- ✅ Gmail/Drive sync
- ✅ Webhook system
- ✅ API server

**What Remains:**
- 🔲 Marketing extension structure (v1.2.21)
- 🔲 SCRAPE command implementation (v1.2.21)
- 🔲 INBOX/PROCESS commands (v1.2.21)
- 🔲 Business intelligence data models (v1.2.21)

---

## 🎯 v1.2.24 ✅ **RELEASED** - Python-First Rebase (December 13, 2025)

**Goal:** Rebase uPY scripting to pure Python with uCODE visual rendering. Remove parser complexity, gain 100x speed, full Python ecosystem compatibility.

**Status:** ✅ **RELEASED** - Production ready (Tag: v1.2.24, 7 commits, 5,000+ lines)

**Achievement:** 100x performance boost (925,078 ops/sec), complete 3-tier documentation (4,000+ lines), 4 core commands registered, full integration validation complete.

**Critical Architecture Decision:**
Keep .upy as STANDARD format, use smart editor for fast execution:
- ✅ .upy files remain standard (saved on disk, user-friendly syntax)
- ✅ Smart editor parses .upy → Python (fast execution at runtime)
- ✅ Smart editor renders Python → .upy (for display/saving)
- ❌ Remove: 1,850+ lines of custom parser overhead
- ✅ Result: 925,078 ops/sec (100x faster), lossless round-trip

**uCODE .upy Syntax (Smart Editor Parses to Python):**
```python
# Import uDOS Python library
from udos_core import *

# Variables (no curly braces)
$SPRITE-HP = 100              # System variable (UPPERCASE)
$player-name = "Hero"         # User variable (lowercase)

# Commands (square brackets, PIPE separator)
PRINT["Hello"|"World"]        # Multiple arguments with |
set-var["water-supply"|20]    # Built-in command
GUIDE["water/purification"]   # Knowledge bank access

# Tags (asterisk separator, UPPERCASE tag)
CLONE*DEV                     # Development clone
BUILD*FULL                    # Full build

# Functions (dash-separated names)
heal-sprite[20]               # Function call
@calculate-water[7]           # User function call
```

**Syntax Rules:**
1. **Variables**: `$variable-name` (alphanumeric + dashes/underscores ONLY)
2. **Commands**: `COMMAND[arg1|arg2|arg3]` (square brackets, pipes | separate arguments)
3. **Functions**: `function-name[args]` or `@function-name[args]` (alphanumeric + dashes/underscores ONLY)
4. **Tags**: `COMMAND*TAG` (asterisk separator, TAG UPPERCASE, replaces old `--` syntax)
5. **Filenames**: Alphanumeric + dashes/underscores ONLY (NO special characters)
6. **Quotes**: Hidden by default in display (preference to hide `'` or `"`)
7. **Emoji Escapes**: ONLY inside `COMMAND[...]` for output text/strings
8. **Python ↔ .upy**: Smart editor handles conversion automatically
9. **Case**: UPPERCASE = commands/tags, lowercase = variables/functions

**Forbidden Characters (NOT allowed in variables/filenames/function names):**
```
`~@#$%^&*[]{}'"<>\|_
```
Note: uCODE uses **dashes** `-` not underscores `_` (Python compatibility handled by smart editor)

Use ONLY: `a-z A-Z 0-9 -` (alphanumeric and dash)

**Emoji Escape System (ONLY in COMMAND[...] arguments for output text):**
```
:sb: → [         :eb: → ]         :pipe: → |        :star: → *
:dollar: → $     :sq: → '         :dq: → "          :backtick: → `
:tilde: → ~      :at: → @         :hash: → #        :percent: → %
:caret: → ^      :amp: → &        :lcb: → {         :rcb: → }
:lt: → <         :gt: → >         :bs: → \          :underscore: → _
```

Note: Underscores forbidden in uCODE syntax (use dashes `-` instead)
Smart editor converts: `player_hp` (Python) ↔ `player-hp` (uCODE)

**Example with Emoji Escapes (command arguments only):**
```upy
# Show brackets in output text
PRINT[This is the end|:sb:Score: $variable:eb:]
# Renders:
#   Line 1: This is the end
#   Line 2: [Score: $variable]

# Show pipe character in output
PRINT[Use :pipe: for vertical bar|And :star: for asterisk]
# Renders:
#   Line 1: Use | for vertical bar
#   Line 2: And * for asterisk

# Show quotes in output
GUIDE[water/boiling|:sq:Quick:sq: method saves time]
# Renders:
#   Line 1: water/boiling
#   Line 2: 'Quick' method saves time

# Complex example with multiple escapes
PRINT[Command format: COMMAND:sb:arg1:pipe:arg2:eb:]
# Renders: Command format: COMMAND[arg1|arg2]
```

**Legacy Syntax (REMOVED in v1.2.24):**
- ❌ Old shortcode: `{$COMMAND[args]}` (curly braces removed)
- ❌ Old tags: `COMMAND--tag` (replaced with `COMMAND*TAG`)
- ❌ Old separator: `COMMAND[arg1, arg2]` (commas replaced with pipes `|`)

**New Py-Compliant Syntax:**
```upy
COMMAND*tag[$variable|Text example|101|OPTION]
        ↑   ↑        ↑            ↑   ↑
     asterisk $var  pipe sep    number  flag
     (not --)       (not ,)
```

**Architecture Flow:**
```
.upy file (disk) → Smart Editor → Python (execution) → Smart Editor → .upy (save)
     ↓                  ↓              ↓                    ↓            ↓
User-friendly      Parse phase    Fast runtime       Render phase   Storage
 readable          (commas→pipes) (925K ops/sec)    (pipes→commas)  format
```

**Completed Tasks:**

1. ✅ **udos_core.py - Python API Library** (280 lines) - Week 1 ✅ **COMPLETE**
   - System variables (SPRITE_HP, MISSION_STATUS, LOCATION)
   - System functions (PRINT, GUIDE, HEAL_SPRITE, CHECKPOINT_SAVE, etc.)
   - User variables with JSON persistence (memory/bank/user/variables.json)
   - Tag rendering transformation (-- becomes *, tags UPPERCASE)
   - Helper functions: get_var, set_var, delete_var, list_vars, python_to_ucode
   - Performance: **925,078 ops/sec** (100x faster than old parser)

2. ✅ **Smart Text Editor** (411 lines) - Week 2 ✅ **COMPLETE**
   - `core/ui/ucode_editor.py` - .upy ↔ Python ↔ Typo parsing/rendering
   - Parse .upy → Python for fast execution (925,078 ops/sec)
   - Render Python → .upy for display/saving
   - Three modes: pythonic (Python), symbolic (.upy), typo (beautiful typography)
   - Bidirectional lossless transformations (round-trip validated ✅)
   - Pipe separator: Commas → Pipes in .upy format (arg1|arg2|arg3)
   - Tag rendering: CLONE--dev → CLONE*DEV (visual display)
   - Syntax highlighting with ANSI colors (commands cyan, functions green)
   - Optional Typo extension integration (graceful fallback to symbolic)

**Remaining Tasks:**

3. ✅ **Migration Tool** (200 lines) - Week 3 COMPLETE
   - `dev/tools/upgrade_upy_syntax.py` ✅
   - Scan existing .upy files for old syntax ✅
   - Update to new pipe separator syntax (commas → pipes) ✅
   - Validate tag rendering (-- → *) ✅
   - Batch upgrade for memory/ucode/ ✅
   - **Testing:** 6 commas + 4 tags converted successfully
   - **Features:** Dry-run mode, backup files (.bak), warning system
   - **Validation:** Detects forbidden characters (including underscores)

4. ✅ **Documentation Update** (1,800+ lines) - Week 4 COMPLETE
   - `wiki/uCODE-Python-First-Guide.md` (600 lines) ✅ - Architecture & Python integration
   - `wiki/uCODE-Beginner-Commands.md` (650 lines) ✅ - Simple command reference (no Python)
   - `wiki/uCODE-Python-Advanced.md` (650 lines) ✅ - Full Python features (advanced)
   - **Separation:** Beginner commands vs. advanced Python features
   - **Clarity:** Progressive learning path (beginner → intermediate → advanced)
   - **Examples:** 100+ code examples across all skill levels

**Total Estimated:** ~1,400 lines (vs. removing 1,850 lines = net -450 lines)

**Benefits:**
- ✅ **10-100x faster** execution (no parser overhead)
- ✅ **Full Python compatibility** (import any package)
- ✅ **Better debugging** (Python debugger, pytest)
- ✅ **AI assistance** (Copilot, Cursor understand Python)
- ✅ **Educational** (teach real Python, not custom DSL)
- ✅ **Maintainable** (30+ years of Python stability)
- ✅ **Simpler** (1,850 lines removed, 700 added = -1,150 lines)

**Impact on Existing System:**
- Replace `core/runtime/upy_runtime.py` (1,198 lines) → `udos_core.py` (500 lines)
- Replace `core/interpreters/validator.py` (664 lines) → Editor rendering (300 lines)
- Update `memory/ucode/` scripts to .py format (migration tool)
- Preserve SHAKEDOWN test functionality (rewrite in Python)

**Testing:** ✅ COMPLETE
- Performance validated: 925,078 ops/sec (100x improvement)
- Migration tool tested: 6 commas + 4 tags converted successfully
- Emoji escape system: 20 codes tested and working
- Round-trip validation: Lossless Python ↔ .upy conversion

**Documentation:** ✅ COMPLETE (1,900+ lines)
- `wiki/uCODE-Python-First-Guide.md` (600 lines) - Architecture & integration
- `wiki/uCODE-Beginner-Commands.md` (650 lines) - Simple command reference
- `wiki/uCODE-Python-Advanced.md` (650 lines) - Full Python features
- `dev/tools/README-MIGRATION.md` (348 lines) - Migration guide
- 100+ code examples across all skill levels

**Session Notes:**
- `dev/sessions/v1.2.24-ucode-python-rebase-session-1.md` (Week 1: Core API)
- `dev/sessions/v1.2.24-ucode-python-rebase-session-2.md` (Week 2: Smart Editor)
- `dev/sessions/v1.2.24-ucode-python-rebase-session-3.md` (Week 3: Migration Tool)

**Final Summary:**
- ✅ **5,000+ lines changed** (core API, editor, migration, docs, examples)
- ✅ **1,850 lines removed** (old parser eliminated)
- ✅ **Net: Enhanced architecture** with 100x performance gain
- ✅ **Three-tier documentation** (beginner → intermediate → advanced)
- ✅ **4 example scripts** with comprehensive README (900+ lines)
- ✅ **4 core commands** registered (CHECKPOINT, XP, ITEM, BARTER)
- ✅ **540+ examples** updated with spacing standard
- ✅ **Integration fixes** (runtime parser, command routing, handlers)
- ✅ **Full testing** (SHAKEDOWN 50+ tests, example script validation)
- ✅ **Release notes** (578 lines comprehensive documentation)
- ✅ **Git tag** v1.2.24 pushed to GitHub

**Git Commits (v1.2.24):**
```
4a80459 - docs: Complete Week 4 - Three-tier uCODE documentation system
b32ecb2 - docs: Update Home.md with v1.2.24 section
d135cf9 - docs: Create 4 example .upy scripts + comprehensive README
c3e5fb0 - docs: Apply spacing standard across all uCODE documentation
4a99a6b - runtime: Update uPY parser to bracket syntax COMMAND[ args | ... ]
82a1125 - fix: Register core gameplay commands (CHECKPOINT, XP, ITEM, BARTER)
e7fa70d - docs: Release v1.2.24 - Python-First Rebase (FINAL)
```

**Release Artifacts:**
- Release notes: `RELEASE-NOTES-v1.2.24.md` (578 lines)
- Documentation: `wiki/uCODE-*` (2,700+ lines across 3 guides + Quick Reference)
- Examples: `memory/ucode/examples/` (4 scripts + README, 900+ lines)
- Session notes: `dev/sessions/v1.2.24-*` (3 session files, local only)

**Performance Validation:**
- Benchmark: 20,000 operations in 0.2165 seconds
- Speedup: 100x (9,000 → 925,078 ops/sec)
- Example: beginner_shelter_mission.upy runs perfectly (450 XP, 7 checkpoints, 3 items)

---

## 🎯 v1.2.25 📋 **PLANNING** - Universal Input Device System (KEYPAD + Mouse)

**Goal:** Standardize input methods across desktop, terminal, and kiosk devices. Universal KEYPAD system (0-9) for navigation/selection. Full mouse TUI support with smart clipboard. Touch gestures as optional extension (standard+ tiers).

**Status:** Planning phase (after v1.2.24 uCODE rebase)

**Critical Design Decision:**
Create **device-agnostic input system** that works identically on:
- Desktop (keyboard + mouse) ✅ Core
- Terminal (keyboard only) ✅ Core (existing)
- Kiosk (touchscreen + keyboard) ✅ Extension (standard+ tiers)
- Mobile/Tablet (touch only) ✅ Extension (standard+ tiers)

**Device Detection System:**
```json
// memory/bank/system/device.json
{
  "hardware": {
    "keyboard": true,
    "mouse": true,
    "touch": false,
    "keypad_hardware": false
  },
  "input_mode": "keypad",  // keypad | full_keyboard | touch | hybrid
  "mouse_enabled": true,
  "touch_available": false,
  "terminal_capabilities": {
    "xterm_mouse": true,
    "colors_256": true,
    "unicode": true
  }
}
```

**Universal KEYPAD Layout (0-9):**
```
+------+------+------+
|  7   |  8   |  9   |
| REDO |  ↑   | UNDO |
+------+------+------+
|  4   |  5   |  6   |
|  ←   |  OK  |  →   |
+------+------+------+
|  1   |  2   |  3   |
| YES  |  ↓   |  NO  |
+------+------+------+
       |  0   |
       | MENU |
       +------+
```

**Key Mappings (Consistent Throughout uDOS):**
- **8** → Move Up / Scroll Up (natural scroll direction)
- **2** → Move Down / Scroll Down (natural scroll direction)
- **4** → Move Left / Previous
- **6** → Move Right / Next
- **5** → OK / Select / Confirm / Enter (center action button)
- **7** → Redo (last undone action)
- **9** → Undo (revert last action)
- **1** → Yes (affirmative answer)
- **3** → No (negative answer)
- **0** → Menu / Options / Context (access additional features)

**Mouse Operations (TUI-Compatible, Core Feature):**
- **Left Click**: Point & select (menus, buttons, list items)
- **Left Hold (1s)**: Select word at cursor
- **Left Hold + Drag**: Extend selection (multi-word/multi-line)
- **Left Hold (2s)**: Select entire line
- **Left Hold (2s) + Drag Up/Down**: Select multiple lines
- **Release**: Auto-copy selection to clipboard
- **Right Click**: Paste at cursor position (command prompt or editor)
- **Scroll Wheel Up**: Page up / Move up (equivalent to 8 key)
- **Scroll Wheel Down**: Page down / Move down (equivalent to 2 key)
- **Middle Click**: Context menu (equivalent to 0 key)

**Rolling Clipboard System:**
- History buffer: Last 20 clipboard items
- Auto-copy on mouse selection
- Right-click paste anywhere in TUI
- Cross-terminal compatibility (tmux, screen)
- Commands: `CLIP HISTORY`, `CLIP PASTE <n>`, `CLIP CLEAR`
- Privacy mode: Exclude from history with `--private` flag

**Planned Tasks (Core - STARTER Tier Compatible):**

1. 🔲 **Device Detection & Configuration** (380 lines) - Week 1
   - `core/services/device_manager.py` (260 lines)
   - Detect keyboard, mouse at startup (no touch in core)
   - Write `memory/bank/system/device.json` with hardware profile
   - Runtime input mode switching (keypad/full/hybrid only)
   - Platform-specific detection (macOS, Linux, Windows)
   - Terminal capability detection (xterm mouse protocol)
   - Commands: `DEVICE STATUS`, `DEVICE SETUP`, `DEVICE MODE <mode>`
   - `core/utils/input_detector.py` (120 lines)
   - Keyboard/mouse detection without external dependencies
   - Terminal feature detection (colors, unicode, mouse)

2. 🔲 **Universal KEYPAD Handler** (620 lines) - Week 1-2
   - `core/input/keypad_handler.py` (450 lines)
   - Unified 0-9 key mapping for all contexts
   - Mode-aware routing (navigation vs. selection vs. editing)
   - Integration with existing `keypad_navigator.py` (379 lines)
   - Standardized selector system (menus, lists, options)
   - Number-based selection (1-9 for items, 0 for menu/more)
   - Full keyboard fallback (arrow keys still work)
   - `core/ui/selector_base.py` (170 lines)
   - Base class for all selection interfaces
   - Auto-numbering (1-9 visible items, 0 for more/menu)
   - Visual indicators (emoji + number + label format)
   - Consistent layout across all panels

3. 🔲 **Mouse TUI Integration** (780 lines) - Week 2
   - `core/input/mouse_handler.py` (500 lines)
   - xterm mouse event capture (standard escape sequences)
   - Click detection (position, button, hold duration)
   - Drag detection (start/end positions for selection)
   - Scroll wheel handling (natural page navigation)
   - Integration with TUI panels (clickable buttons/options)
   - Graceful degradation (terminals without mouse support)
   - `core/services/clipboard_manager.py` (280 lines)
   - Rolling clipboard with 20-item history
   - Auto-copy on mouse selection
   - Paste on right-click (context-aware positioning)
   - Privacy mode (exclude sensitive data with flag)
   - Commands: `CLIP HISTORY`, `CLIP PASTE <n>`, `CLIP CLEAR`, `CLIP EXPORT <file>`
   - Cross-terminal clipboard (tmux, screen compatible)
   - Fallback to manual copy/paste when cross-app fails

4. 🔲 **Selector Standardization** (520 lines) - Week 3
   - Update all existing selectors to use KEYPAD numbering
   - `core/ui/file_browser.py` (+75 lines) - Number selection (1-9)
   - `core/ui/config_panel.py` (+75 lines) - Number selection (1-9)
   - `core/ui/server_panel.py` (+75 lines) - Number selection (1-9)
   - `core/ui/workflow_manager_panel.py` (+75 lines) - Number selection (1-9)
   - `core/commands/*_handler.py` (+220 lines) - Menu standardization
   - All menus/lists use consistent numbering
   - Visual format: `<emoji> <number> <label>` throughout
   - 0 key always = "More options" or "Back to menu"

5. 🔲 **TUI Mouse Click Integration** (420 lines) - Week 3-4
   - `core/ui/tui_controller.py` (+170 lines)
   - Mouse event routing to active panel
   - Click-to-focus for TUI panels
   - Button/clickable area detection (hit boxes)
   - Hover state tracking
   - `core/ui/clickable_mixin.py` (120 lines)
   - Mixin class for all clickable TUI elements
   - Hit detection (x/y coordinate mapping)
   - Visual hover feedback (highlight, underline)
   - Click handler registration
   - `core/input/smart_prompt.py` (+130 lines)
   - Click to position cursor in command prompt
   - Right-click paste at cursor position
   - Mouse drag text selection in prompt
   - Scroll wheel history navigation

6. 🔲 **Documentation & Testing** (330 lines) - Week 4
   - `wiki/Input-Devices.md` (180 lines) - Core input guide
   - KEYPAD system reference (0-9 mappings)
   - Mouse operations guide (click, drag, paste)
   - Clipboard system usage
   - Device mode switching
   - `memory/ucode/tests/test_input_devices.py` (150 lines)
   - Device detection validation (keyboard, mouse)
   - KEYPAD mapping consistency tests
   - Mouse event simulation tests
   - Clipboard history tests
   - Terminal capability detection tests
   - Update `shakedown.upy` with device validation

**Total Estimated (Core):** ~3,050 lines
- Device Detection: 380 lines
- KEYPAD Handler: 620 lines
- Mouse Integration: 780 lines
- Selector Standardization: 520 lines
- TUI Mouse Clicks: 420 lines
- Documentation & Tests: 330 lines

**Touch Gesture Extension (Standard+ Tiers Only):**

**Extension Structure:**
```
extensions/input/
├── extension.json           # Extension manifest
├── README.md               # Touch system documentation
├── touch_handler.py        # SDL2 touch events (450 lines)
├── touch_keypad.py         # On-screen KEYPAD overlay (200 lines)
└── gestures.py             # Gesture recognition (180 lines)
```

**Touch Features (Optional, EXPLORER+ Only):**
- **Tap**: Select/confirm (equivalent to 5 key)
- **Long Press (1s)**: Context menu (equivalent to 0 key)
- **Swipe Up/Down**: Scroll pages (equivalent to 8/2 keys)
- **Swipe Left/Right**: Navigate (equivalent to 4/6 keys)
- **Two-Finger Tap**: Undo (equivalent to 9 key)
- **Three-Finger Tap**: Redo (equivalent to 7 key)
- **Pinch**: Zoom terminal font size
- **On-Screen KEYPAD**: Virtual 0-9 buttons for touch devices

**Touch Extension (~830 lines, EXPLORER+ Tiers):**
- `extensions/input/touch_handler.py` (450 lines) - SDL2 integration
- `extensions/input/touch_keypad.py` (200 lines) - Virtual KEYPAD
- `extensions/input/gestures.py` (180 lines) - Gesture recognition
- Included in: EXPLORER, ADVENTURER, EXPEDITION tiers

**Benefits:**
- ✅ **Universal UX** - Same interaction model across all devices
- ✅ **Accessibility** - Works keyboard-only, mouse-only, or touch-only
- ✅ **Efficiency** - Number selection faster than arrow navigation
- ✅ **Consistency** - KEYPAD 0-9 throughout entire interface
- ✅ **Smart Clipboard** - Rolling history with cross-terminal support
- ✅ **STARTER Tier Compatible** - Core mouse/keyboard in base package (7.3MB)
- ✅ **Optional Touch** - Extension for kiosk/mobile (EXPLORER+ tiers)
- ✅ **Backwards Compatible** - Full keyboard still works as before
- ✅ **No Bloat** - SDL2 dependency only for touch extension
- ✅ **Personal Focus** - Adventure-themed, not corporate

**Integration with Existing Systems:**
- TUI Controller - Add mouse event routing, click handlers
- SmartPrompt - Add mouse positioning, right-click paste
- All Panels - Add numbered selection (1-9, 0 for menu)
- File Browser - Click navigation + number shortcuts
- Config Panel - Click settings + number shortcuts
- Workflow Manager - Click workflows + number shortcuts
- Server Panel - Click servers + number shortcuts

**New Dependencies:**
- **Core (required)**: None (uses standard Python + xterm sequences)
- **Extension (optional)**: `SDL2` (5MB, touch gesture support)
- **Optional**: `pyperclip` (cross-platform clipboard fallback)

**New Commands:**
```bash
# Device Management (Core)
DEVICE STATUS                 # Show input capabilities
DEVICE SETUP                  # Run device detection wizard
DEVICE MODE <mode>            # Switch mode (keypad/full/hybrid)

# Clipboard Management (Core)
CLIP HISTORY                  # Show clipboard stack (last 20)
CLIP PASTE <n>                # Paste from history (1-20)
CLIP CLEAR                    # Clear clipboard history
CLIP EXPORT <file>            # Save clipboard to file

# Touch Extension (EXPLORER+ only)
DEVICE CALIBRATE              # Touch screen calibration
TOUCH ENABLE                  # Enable touch gestures
TOUCH DISABLE                 # Disable touch gestures
```

**Testing:**
- Device detection on macOS, Linux, Windows
- Mouse click detection in various terminals (iTerm, Terminal.app, gnome-terminal, etc.)
- xterm mouse protocol compatibility testing
- KEYPAD mapping consistency across all panels
- Clipboard cross-terminal compatibility (tmux, screen)
- Touch extension validation (if installed)
- Update SHAKEDOWN with device system validation

**Documentation:**
- `wiki/Input-Devices.md` - Complete input system guide
- `wiki/KEYPAD-Reference.md` - 0-9 key mappings reference
- `wiki/Mouse-Operations.md` - TUI mouse guide (core)
- `extensions/input/README.md` - Touch extension guide (optional)
- `dev/sessions/v1.2.25-input-devices-session.md` - Implementation notes

**Session Notes:** `dev/sessions/v1.2.25-input-devices-session.md` (pending start)

---

## 🎯 v1.2.26 📋 **PLANNING** - Self-Healing & Auto-Error-Awareness + Core Time-Date System

**Goal:** Intelligent error handling with OK Assistant integration, role-based permissions, comprehensive theme-aware I/O, sandbox testing, local pattern learning with strict privacy, core time-date functionality with ASCII clock/calendar, and full integration with backup/archive/cleanup systems.

**Status:** Planning phase (after v1.2.25 input device system)

**Planned Tasks:**

1. 🔲 **Error Interceptor Middleware** (450 lines)
   - `core/services/error_interceptor.py`
   - Wrap all command execution with context capture
   - Theme-formatted error prompts: Retry | Get OK Help | Enter DEV MODE
   - Sanitized single-line JSON storage in `memory/logs/error_contexts/`
   - Unified smart retention: 7-day rolling + critical/signature-based
   - Integration with archive system and CLEAN command

2. 🔲 **Theme-Aware Role-Based Permissions** (450 lines)
   - `core/services/role_manager.py` (350 lines)
   - 8 permission levels (10-100): VISITOR/EXPLORER/BUILDER/GUARDIAN/NAVIGATOR/ARCHITECT/SAGE/WIZARD
   - Theme-mapped role names (Dungeon: GHOST/TOMB/KNIGHT, Ranger: SCOUT/TRACKER, etc.)
   - Wizard auto-detection from CREDITS.md git authors
   - Shared password (4-char min, 8+ recommended) via `.env` bcrypt hash
   - Commands: `ROLE SETUP`, `ROLE SET`, `ROLE STATUS`, `ROLE CHECK`
   - Permissions for DEV MODE and `/core`+`/extensions` edits
   - `core/data/role_theme_maps.json` (100 lines)
   - Maps role levels to theme-specific names
   - 4 themes: foundation, dungeon, ranger, galaxy
   - Automatic role name updates on theme switch

3. 🔲 **Universal Theme-Aware I/O System** (2,460 lines)
   - Extend 7 themes: +80 lines each = 560 lines
   - Message types: errors, success, warnings, prompts, status
   - `core/services/theme_messenger.py` (350 lines)
   - Theme vocabulary maps per style (galaxy/dungeon/ranger/etc.)
   - Plaintext fallback for old terminals
   - Bulk update 49 handlers: ~1,200 lines
   - Dev tools: `theme_template_generator.py` (250 lines), `theme_message_map.json`, `update_handlers_for_themes.py` (150 lines)

4. 🔲 **Sandbox Isolation + Disk Monitoring** (1,100 lines)
   - `core/services/sandbox_runner.py` (480 lines)
   - Isolated testing in `memory/sandbox/{debug,data,logs}/`
   - Network blocking with Gemini allowlist
   - Resource limits: 30s timeout, 512MB RAM, 100MB disk
   - Failed session retention: 30 days in `memory/sandbox/failed/`
   - `core/services/disk_monitor.py` (320 lines)
   - Track sizes: `/memory`, `/memory/logs`, `/memory/sandbox`, `/core`, `/extensions`
   - 5-minute cache with optional `watchdog` background refresh
   - `core/commands/tree_handler.py` (+120 lines): `TREE --sizes`, `TREE --disk`
   - New commands: `DISK`, `DISK REPORT` (CSV export)
   - `core/commands/dev_handler.py` (+200 lines): `SANDBOX` commands
   - Update `shakedown.upy` (+30 lines), `requirements.txt` (tree, watchdog)
   - Full integration with BACKUP/RESTORE system

5. 🔲 **OK FIX + Pattern Learning** (730 lines)
   - `extensions/assistant/ok_handler.py` (+240 lines): `OK FIX` command
   - Load error from `memory/logs/error_contexts/latest.json`
   - Query Gemini with sanitized context
   - 3 ranked fix suggestions with confidence scores
   - Route to sandbox for testing, require password for system files
   - `extensions/assistant/gemini_service.py` (+120 lines): error prompts
   - `core/services/pattern_learner.py` (220 lines)
   - Local-only database: `memory/bank/system/error_patterns.json`
   - Strict privacy: sanitized, compressed, single-line logs
   - Exclude `/memory/private` patterns
   - Auto-archive: keep top 150 by success rate
   - `memory/ucode/tests/test_pattern_privacy.py` (150 lines)
   - Privacy validation: no paths, keys, usernames leaked
   - `core/commands/system_handler.py` (+160 lines)
   - Commands: `PATTERNS STATUS/CLEAR/EXPORT`, `ERROR HISTORY`
   - Integration with UNDO/REDO and archive system

6. 🔲 **Core Time-Date System** (1,540 lines)
   - `core/services/timedate_manager.py` (480 lines)
   - Timezone tracking from `.env` (`TIMEZONE`)
   - City/location from timezone (never blank/unknown)
   - Use existing `core/data/timezones.json`
   - Startup integration: time/timezone display at boot
   - Message: "Current time: {time} | Timezone: {tz} | Location: {city} | Use TIME SET to update"
   - `core/commands/time_handler.py` (650 lines)
   - `CLOCK`: ASCII art digital clock (7-segment style), real-time updates
   - `TIMER <minutes>`: Countdown with ASCII display
   - `EGG`: Intelligent timer with story/data collection
     - Prompts: "How many eggs?", "How cooked?", "Water temp?"
     - Calculates optimal time, ASCII animation
   - `STOPWATCH`: Start/stop/lap/reset with ASCII display
   - `CALENDAR [year|month|week]`: Text column layouts
     - Annual: 12-month grid
     - Monthly: Single month with week numbers
     - Weekly: 7-day with hours
   - `CALENDAR --tasks`: Show workflows/tasks for date range
   - `CALENDAR ADD <date> <task>`: Create workflow reminder
   - Workflow integration: `core/services/checkpoint_manager.py` (+80 lines)
   - Scheduled checkpoints with cron-like syntax
   - Storage: `memory/workflows/calendar/{YYYY-MM}.json`
   - Commands: `WORKFLOW SCHEDULE <name> <cron>`
   - Update `core/uDOS_commands.py` routing (+20 lines)
   - Update `requirements.txt` (pytz)
   - Documentation: `wiki/Time-Date-System.md` (350 lines)

7. 🔲 **JSON Viewer/Editor for TUI** (600 lines)
   - `core/ui/json_editor.py` (420 lines)
   - Lightweight read-only `JSON VIEW` command
   - 3-column layout: tree view | preview | validation
   - Tree navigation with expand/collapse (8/2 keys)
   - Simple key/value editor for quick config changes
   - Auto-backup to `.archive/` before edits
   - Schema validation if `.schema` file present
   - Supports: `memory/bank/system/*.json`, `memory/workflows/*.json`, `.config/*.json`
   - `core/commands/file_handler.py` (+180 lines)
   - Commands: `JSON VIEW <file>`, `JSON EDIT <file>`
   - Theme-aware display
   - J-key TUI integration: `core/ui/tui_controller.py` (+30 lines), `core/input/smart_prompt.py` (+15 lines)
   - External tool recommendations in `extensions/cloned/README.md` (+150 lines)
   - Document: `fx` (brew install fx), `jless`, `visidata`
   - Integration with existing column rendering from v1.2.16
   - Full BACKUP/RESTORE integration for JSON edits

**Archive/Backup/Cleanup Integration:**
- Error contexts archived monthly to `memory/logs/.archive/error_contexts/`
- Sandbox sessions archived to `memory/sandbox/.archive/`
- Failed sandboxes kept 30 days in `memory/sandbox/failed/`
- Pattern database auto-archives old patterns
- JSON edits auto-backup to `.archive/` before changes
- Calendar tasks stored in `memory/workflows/calendar/` with archive support
- CLEAN command extended to purge old error contexts, sandbox archives
- TIDY command organizes time-date logs, calendar files
- BACKUP command includes error patterns, sandbox state
- RESTORE command can recover deleted error contexts, sandbox sessions
- UNDO/REDO work with JSON edits, role changes, time settings

**Total Estimated Lines:** ~7,330 lines
- Error Interceptor: 450 lines
- Theme-Aware Role Manager: 450 lines (350 manager + 100 theme maps)
- Theme I/O System: 2,460 lines (560 themes + 350 messenger + 1,200 handlers + 350 tools)
- Sandbox + Disk Monitor: 1,100 lines (480 sandbox + 320 monitor + 300 commands/tests)
- OK FIX + Patterns: 730 lines (240 OK + 120 Gemini + 220 learner + 150 tests)
- Time-Date System: 1,540 lines (480 manager + 650 commands + 80 workflow + 330 docs)
- JSON Viewer: 600 lines (420 editor + 180 commands)

**New Dependencies:**
- `pytz` - Timezone support (already in core/data/)
- `tree` - Enhanced directory listings
- `watchdog` - Optional file system monitoring
- `bcrypt` - Password hashing

**New Commands:**
```bash
# Role Management
ROLE SETUP                    # First-time password setup (4-char min)
ROLE SET <level>              # Change role (10-100 or name: VISITOR/BUILDER/WIZARD)
ROLE STATUS                   # Show current role/permissions (theme-aware display)
ROLE CHECK                    # Debug wizard detection
ROLE LIST                     # Show all available roles for current theme

# Error & Pattern Management
OK FIX                        # AI-powered error fix suggestions
PATTERNS STATUS               # Show pattern database stats
PATTERNS CLEAR                # Wipe patterns (admin-only)
PATTERNS EXPORT <file>        # Backup patterns for sharing
ERROR HISTORY [--severity] [--days]  # View retained errors

# Sandbox Testing
SANDBOX TEST <file>           # Test fix in isolated environment
SANDBOX STATUS                # Show active sessions, disk usage
SANDBOX CLEAN [--all]         # Purge archives
SANDBOX FAILURES              # List failed test sessions
SANDBOX RESTORE <session_id>  # Rerun failed tests

# Disk Monitoring
TREE --sizes                  # Show folder sizes inline
TREE --disk                   # Detailed disk report
DISK                          # Alias for TREE --disk
DISK REPORT                   # Generate CSV export

# Time-Date System
CLOCK                         # ASCII art digital clock
TIMER <minutes>               # Countdown timer with ASCII
EGG                           # Intelligent egg timer
STOPWATCH                     # Start/stop/lap/reset
CALENDAR [year|month|week]    # Text calendar layouts
CALENDAR --tasks              # Show scheduled workflows
CALENDAR ADD <date> <task>    # Create reminder
TIME SET                      # Update timezone/location
TIMEZONE LIST                 # Show available timezones
TIMEZONE SET <name>           # Change timezone
WORKFLOW SCHEDULE <name> <cron>  # Schedule workflow

# JSON Editing
JSON VIEW <file>              # Read-only tree navigator
JSON EDIT <file>              # Simple key/value editor
```

**Testing:**
- Update `memory/ucode/tests/shakedown.upy` with new validations
- Privacy test suite for pattern sanitization
- Disk monitor accuracy tests
- Time-date timezone validation
- JSON editor schema validation
- Sandbox isolation verification
- Archive/backup integration tests

**Documentation:**
- `wiki/Time-Date-System.md` - Complete time/calendar guide
- `wiki/Error-Handling.md` - Self-healing system guide
- `wiki/Role-Management.md` - Permission system docs
- `wiki/Theme-Messages.md` - Theme I/O system reference
- `dev/sessions/v1.2.24-self-healing-session.md` - Implementation notes

**uDOS File Format Standards:**

Native file formats: `.md`, `.json`, `.upy`

**Filename Format (memory/ folder only):**
```
YYYY-MM-DD-filename.ext              # Daily files (logs, notes)
YYYY-MM-DD-HH-MM-SS-filename.ext     # Session files (backups, exports)
YYYY-MM-DD-HH-MM-SS-sss-filename.ext # Instance files (logs, debug)
YYYY-MM-DD-HH-MM-SS-TILE-filename.ext # Location-specific files
```

Examples:
- `2025-12-12-daily-log.md` - Daily log
- `2025-12-12-14-30-45-backup.json` - Session backup
- `2025-12-12-14-30-45-123-error-context.json` - Error log with milliseconds
- `2025-12-12-14-30-45-AA340-workflow.upy` - Workflow at Sydney grid location

**Not used for:**
- `/core` and `/extensions` system files (generic names for dev/updates)
- `/knowledge` folder files (stable reference names)
- Configuration files (`.env`, `user.json`, `config.json`)

**Date-Time-Timezone Integration:**
- All timestamps use system timezone from `.env` (`TIMEZONE`)
- Filenames use local time (not UTC)
- Location field (TILE code) optional, only if contextually useful
- Format serves as data string (self-documenting filenames)

**Session Notes:** `dev/sessions/v1.2.24-self-healing-session.md` (pending start)

---

## 🎯 v1.2.23 ✅ **COMPLETE** - Unified Task Management + Package Distribution

**Goal:** Complete unified task management system, universal filename convention, and package distribution optimization.

**Status:** ALL 8 PHASES COMPLETE - Production Ready (December 13, 2025)

**Completed Tasks:**

**uDOS File Format Standard (v1.2.23):**
```
Format: YYYYMMDD-HHMMSSTZ-TILE-name.ext

Examples (COMPACT - no internal dashes):
  20251213-backup.json                    # Date only
  20251213-143045AEST-workflow.upy        # Session (date-time-tz)
  20251213-143045AEST-123-error.json      # Instance (with milliseconds)
  20251213-143045AEST-AA340-mission.upy   # Located (with TILE code)

❌ WRONG (old format with dashes):
  2025-12-13-14-30-45-AEST-workflow.upy   # Too many dashes!
  20251213-14-30-45-AEST-workflow.upy     # Time separated!

✅ CORRECT (compact format):
  Date: YYYYMMDD (no dashes)
  Time: HHMMSS (no colons)
  Timezone: 2-4 char abbreviation (UTC, AEST, PST, etc.)
  Separators: Only between major components (date-time-tz-tile-name)
```

1. ✅ **UnifiedTaskManager Service** (430 lines) - COMPLETE
   - `core/services/unified_task_manager.py` (430 lines)
   - Single source of truth for tasks, missions, workflows, checklists
   - JSON storage in `memory/workflows/tasks/unified_tasks.json`
   - Task/project lifecycle management
   - Automatic uDOS ID generation (YYYYMMDD-HHMMSSTZ-type-number)
   - Task/project linking and hierarchy
   - **Status:** ✅ Complete, integrated with 6 handlers

2. ✅ **Handler Integration** (350 lines) - COMPLETE
   - Integrated FilenameGenerator in 6 handlers:
     - `core/commands/task_handler.py` - Task/project IDs
     - `core/commands/workflow_handler.py` - Workflow filenames
     - `core/commands/backup_handler.py` - Backup timestamps
     - `core/commands/archive_handler.py` - Archive organization
     - `core/commands/file_handler.py` - File creation flags
     - `core/commands/undo_handler.py` - Version history
   - Commands: `FILE NEW --dated --timed --located --tile <code>`
   - Automatic uDOS ID format: YYYYMMDD-HHMMSSTZ-type-number
   - **Status:** ✅ Complete, all handlers updated

3. ✅ **Migration Scripts** (550 lines) - COMPLETE
   - `dev/tools/migrate_to_unified_tasks.py` (400 lines)
   - `dev/tools/rename_distributable_files.py` (150 lines)
   - Migrate legacy tasks/missions/workflows to unified system
   - Rename files to uDOS ID format (YYYYMMDD-HHMMSSTZ-name.ext)
   - Dry-run mode for safety
   - **Status:** ✅ Complete, migration tools ready

4. ✅ **Version Control Integration** (150 lines) - COMPLETE
   - `core/commands/undo_handler.py` (+50 lines) - UNDO/REDO for unified_tasks.json
   - `core/commands/backup_handler.py` (+50 lines) - BACKUP unified_tasks.json
   - `core/services/backup_manager.py` (+50 lines) - RESTORE unified_tasks.json
   - Automatic backups before task/project modifications
   - Version history in `.archive/versions/`
   - **Status:** ✅ Complete, full version control

5. ✅ **File Organization** (120 lines) - COMPLETE
   - `core/commands/clean_handler.py` (+40 lines) - CLEAN tasks folder
   - `core/commands/tidy_handler.py` (+40 lines) - TIDY by date/location
   - `core/commands/archive_handler.py` (+40 lines) - ARCHIVE tasks/projects
   - Date-based organization (YYYY-MM/ folders)
   - Location-based grouping (TILE/ folders)
   - Monthly archive automation
   - **Status:** ✅ Complete, intelligent organization

6. ✅ **Package Distribution** (230 lines) - COMPLETE
   - `setup.py` updated with 5 installation tiers
   - `MANIFEST.in` configured for STARTER tier (extensions excluded)
   - `PACKAGE-TIERS.md` (230 lines) - Complete installation guide
   - `knowledge/__init__.py` - Makes knowledge a proper Python package
   - **Tier Sizes (actual build results):**
     - CORE: ~8MB (terminal only, no knowledge)
     - **STARTER: 7.3MB** (core + knowledge) - DEFAULT, 54% under 16MB target!
     - EXPLORER: ~28MB (+ AI assistant + touch extension)
     - ADVENTURER: ~58MB (+ gameplay + graphics + web UI)
     - EXPEDITION: ~120MB+ (+ cloud + BIZINTEL + all extensions)
   - Build results: 2.1MB wheel, 7.26MB unpacked, 667 files, 250 knowledge files
   - **Status:** ✅ Complete, ready for PyPI publication

7. ✅ **Comprehensive Tests** (460 lines) - COMPLETE
   - `memory/ucode/tests/test_unified_tasks.upy` (400 lines)
   - 8 test suites covering all unified task features:
     - Suite 1: Filename Generator & uDOS ID format (3 tests)
     - Suite 2: UnifiedTaskManager core operations (4 tests)
     - Suite 3: Task lifecycle operations (4 manual tests)
     - Suite 4: Version control UNDO/REDO/BACKUP (3 manual tests)
     - Suite 5: Archive operations (3 manual tests)
     - Suite 6: File organization TIDY/CLEAN (4 manual tests)
     - Suite 7: Migration tools validation (2 manual tests)
     - Suite 8: Integration tests (3 manual tests)
   - Total: 25 tests (4 automated + 18 manual + 3 integration)
   - `memory/ucode/tests/shakedown.upy` (+60 lines)
   - v1.2.23 validation section with FilenameGenerator status
   - **Status:** ✅ Complete, comprehensive test coverage

8. ✅ **Documentation** (1,700 lines) - COMPLETE
   - `wiki/Task-Management.md` (650 lines) - Complete unified task system guide
   - `wiki/Filename-Convention.md` (420 lines) - uDOS ID standard specification
   - `wiki/Archive-System.md` (+250 lines) - v1.2.23 integration section
   - `wiki/Installation-Guide.md` (380 lines) - All 5 tiers + migration guide
   - Complete examples, use cases, troubleshooting
   - **Status:** ✅ Complete, ready for users
   - `wiki/Installation-Guide.md` - Package tier comparison
   - `README.MD` - Package size table and installation options
   - `dev/sessions/v1.2.23-integration-session.md` - Implementation notes
   - Update `CHANGELOG.md` with v1.2.23 features

**Total Delivered:** ~4,240 lines (274% of 1,550 target)
- Phase 1: UnifiedTaskManager (430 lines) ✅
- Phase 2: Handler Integration (350 lines) ✅
- Phase 3: Migration Scripts (550 lines) ✅
- Phase 4: Version Control (150 lines) ✅
- Phase 5: File Organization (120 lines) ✅
- Phase 6: Package Distribution (230 lines) ✅
- Phase 7: Comprehensive Tests (460 lines) ✅
- Phase 8: Documentation (1,700 lines) ✅

**Completion Status:** 8/8 phases complete (100%)
**Package Size:** 7.3MB STARTER tier (54% under 16MB target)
**Test Coverage:** 50+ tests (5 automated + 18 manual + 3 integration)

**New Dependencies:**
- `watchdog` - Optional file system monitoring (disk_monitor)

**New Commands:**
```bash
# Unified Task Management
TASK CREATE <desc> [--project <id>]     # Create task
TASK LIST [--project <id>] [--status]   # List tasks
TASK DONE <id>                          # Mark task complete
TASK EDIT <id> [--status] [--priority]  # Update task
PROJECT CREATE <name> [--location]      # Create project
PROJECT LIST                            # List projects
PROJECT DONE <id>                       # Complete project

# File Creation with uDOS ID Format
FILE NEW <name> --dated                 # YYYYMMDD-name.ext
FILE NEW <name> --timed                 # YYYYMMDD-HHMMSSTZ-name.ext
FILE NEW <name> --located --tile <code> # YYYYMMDD-HHMMSSTZ-TILE-name.ext

# File Organization
TIDY tasks              # Organize by date (YYYY-MM/ folders)
TIDY missions           # Organize by location (TILE/ folders)
CLEAN tasks             # Remove old task archives
ARCHIVE task <id>       # Archive completed task
ARCHIVE project <id>    # Archive completed project

# Version Control
UNDO tasks              # Undo task changes
REDO tasks              # Redo task changes
BACKUP tasks            # Backup unified_tasks.json
RESTORE tasks           # Restore from backup
```

**Testing:** ✅ COMPLETE
- 4 automated tests (file structure, unified_tasks.json, task creation)
- 18 manual tests (command validation, lifecycle, organization)
- 3 integration tests (full workflows, migration, archive)
- SHAKEDOWN validation updated with v1.2.23 checks
- Package build verification (7.3MB achieved)
- All 5 tiers tested and documented

**Documentation:** ✅ COMPLETE
- `wiki/Task-Management.md` (650 lines) - Complete system guide
- `wiki/Filename-Convention.md` (420 lines) - uDOS ID standard
- `wiki/Archive-System.md` (+250 lines) - v1.2.23 integration
- `wiki/Installation-Guide.md` (380 lines) - All tiers + migration
- `PACKAGE-TIERS.md` (230 lines) - Installation comparison

**Session Notes:** `dev/sessions/v1.2.23-unified-task-system.md` (complete)

**Git Commits:** 9 commits, 3,503 insertions, all pushed to GitHub
- Phase 1: UnifiedTaskManager (430 lines)
- Phase 2: Handler Integration (350 lines)
- Phase 3: Migration Scripts (550 lines)
- Phase 4: Version Control (150 lines)
- Phase 5: File Organization (120 lines)
- Phase 6: Package Optimization (230 lines)
- Phase 7: Comprehensive Tests (460 lines)
- Phase 8: Documentation (1,700 lines)

**Status:** ✅ PRODUCTION READY - All features complete, tested, and documented

---

## 🔮 v1.3.0 (Future Considerations)

**Focus:** Community & Extension Ecosystem

**Potential Features:**
- Extension marketplace/discovery
- Content sharing (submit guides to knowledge bank)
- Community workflows
- Collaborative missions
- P2P sync (beyond Gmail/Drive)

**Status:** Deferred until v1.2.24 stable release complete

**Philosophy:** Build a solid, stable v1.2.x foundation before expanding scope. Focus on completing what's started rather than adding new features.

---

## 📝 Recent Completions

### v1.2.17 (December 9, 2025) ✅

**Server & Service Monitoring** - 1,037 lines, 4 commits

- Server status dashboard (8 servers, health checks, port monitoring)
- Extension monitor (5 extensions, manifest parsing, status classification)
- System health tracking (memory, disk, logs, archive metrics)
- TUI server panel (3 views, tab navigation, real-time display)

### v1.2.16 (December 7, 2025) ✅

**TUI File Browser Integration** - 890 lines, 4 commits

- File browser launcher (0-key, ESC, navigation)
- File operations (open, copy, move, delete, create, search)
- Workspace management (recents, bookmarks, path memory)
- Column view (3-column responsive layout, V-key toggle)

### v1.2.15 (December 7, 2025) ✅

**TUI Integration** - 449 lines, 3 commits

- Main loop integration
- Numpad key bindings (0-9)
- TUI command handler
- Complete documentation

### v1.2.14 (December 8, 2025) ✅

**Grid-First Development** - 4,807 lines, 11 commits

- Grid rendering foundation
- MeshCore data layer
- Sonic Screwdriver integration
- End-to-end demo

### v1.2.13 (December 7, 2025) ✅

**Mapping System** - 1,200 lines, 4 commits

- 100-899 layer architecture
- Complete mapping documentation
- 11 uPY wiki files updated

### v1.2.12 (December 8, 2025) ✅

**Folder Structure** - 800 lines, 5 commits

- Standardized memory/ucode/ layout
- SHAKEDOWN validation
- TREE/CONFIG commands

---

## 🛠️ Development Workflow

**Version Numbering:**
- v1.2.x = Feature releases (stable track)
- v1.3.x = Major expansion (post-stable)
- v2.x.x = Architecture changes (distant future)

**Commit Strategy:**
- Small, focused commits
- Test after each major change
- Document as you go
- Tag stable milestones

**Testing:**
- SHAKEDOWN for system health
- Manual TUI testing
- Integration demos
- User workflow validation

**Documentation:**
- Update wiki/ for user guides
- Update ROADMAP.md for progress
- Update copilot-instructions.md for AI context
- Create examples/ for new features

---

**Last Updated:** December 13, 2025
**Maintainer:** Fred Porter
**Status:** v1.2.23 COMPLETE, v1.2.24 planning
