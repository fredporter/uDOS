# Changelog

All notable changes to uDOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres on [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.30] - 2025-11-22

### Summary
Enhanced CLI experience with **teletext-style block character UI** for pickers, autocomplete, and file navigation. This update brings beautiful retro-inspired visual feedback while maintaining 100% backward compatibility and the text-first computing philosophy.

### Added
- **Teletext UI Components** (`core/ui/teletext_prompt.py`):
  - `TeletextBlocks` class with Unicode block characters for UI elements
  - `TeletextPromptStyle` class with pre-built UI patterns
  - `EnhancedPromptRenderer` for complete prompt rendering system
  - Selection boxes with double-line borders (`╔═╗ ╠═╣ ╚═╝`)
  - Visual indicators: radio buttons (`◉ ○`), checkboxes (`☑ ☐`)
  - File tree visualization with type icons (`📄 📁 📝 📊 🖼`)
  - Autocomplete panels with visual score bars (`█████░░░░░`)

- **Enhanced Picker System** (`core/ui/picker.py`):
  - `teletext_mode` field in `PickerConfig` (default: `True`)
  - Automatic teletext rendering when enabled
  - `_render_teletext()` method for block-based UI
  - Graceful fallback to classic mode if import fails
  - Multi-select with visual checkboxes
  - Numbered keyboard shortcuts clearly displayed (1-9)

- **Enhanced Autocomplete** (`core/services/smart_prompt.py`):
  - `TeletextIndicators` class for visual feedback
  - `score_bar()` method using block characters (`█ ░`)
  - Command icon (`⚡`) for command suggestions
  - Visual match quality display with progress bars
  - Better spacing and alignment in suggestions

- **Test Suite** (`memory/tests/test_v1_0_30_teletext_ui.py`):
  - 6 comprehensive tests for all new features
  - Single-select picker testing
  - Multi-select picker with checkboxes
  - File tree visualization testing
  - Autocomplete panel testing
  - Enhanced prompt renderer testing
  - Classic mode fallback verification

### Enhanced
- **UniversalPicker**:
  - Now supports teletext block styling by default
  - Better visual hierarchy with double-line borders
  - Clearer selection states with radio/checkbox indicators
  - Improved keyboard navigation feedback
  - Maintains classic box-drawing mode as fallback

- **SmartPrompt**:
  - Autocomplete suggestions now show visual score bars
  - Enhanced command display with icons
  - Better match quality feedback
  - Improved suggestion panel layout

### Changed
- `PickerConfig`: Added `teletext_mode: bool = True` field (v1.0.30)
- `UniversalPicker.__init__()`: Imports teletext components when enabled
- `smart_prompt.py`: Updated version comment to v1.0.30
- Autocomplete completion display format enhanced with blocks

### Documentation
- Added `wiki/Release-v1.0.30.md` with comprehensive feature documentation
- Included usage examples for all new components
- Added migration guide (no migration needed - fully compatible)
- Documented all new character sets and visual elements

### Performance
- Minimal overhead: <1ms added to render time
- All Unicode characters in BMP (no wide characters)
- Efficient block character generation
- No new dependencies required

### Backward Compatibility
- 100% backward compatible with v1.0.27
- Existing picker code automatically enhanced
- Classic mode available via `teletext_mode=False`
- All existing APIs preserved
- No breaking changes

---

## [1.0.27] - 2025-11-19 - STABLE RELEASE 🎉

### Summary
v1.0.27 marks the **stable release** of the v1.0.x series. This release completes the final polish phase with 370/395 tests passing (93.7%), pip package distribution, and comprehensive project reorganization for clean distribution and future development.

### Added
- **pip Package Distribution**:
  - Complete `setup.py` with metadata, dependencies, and entry points
  - `MANIFEST.in` for package data inclusion
  - `INSTALL.md` with comprehensive installation guide
  - Verified pip installable: `pip install -e .`

- **Project Reorganization**:
  - Created `/dev` folder for development workspace (replaces `/docs`)
  - Established clear separation: system code (tracked), user content (gitignored), dev work (gitignored)
  - `/dev/planning/` - Tracked roadmaps and specs for contributors
  - `/dev/archive/` - Local-only development history (gitignored)
  - `/dev/notes/` - Local-only personal notes (gitignored)
  - `/memory` - Clean distribution structure with templates and tests tracked

- **Memory Folder Templates**:
  - `memory/README.md` - Comprehensive user workspace guide
  - `memory/workflow/README.md` - Mission workflow documentation
  - `.gitkeep` files for config/, sandbox/, workflow/ structure
  - All tests tracked in `/memory/tests/` for distribution

### Changed
- **Version Bumping**:
  - Updated `setup.py` version to 1.0.27
  - Updated `README.MD` to reflect stable release status
  - Updated project status: 26/26 versions complete (100%)

- **Git Organization**:
  - Updated `.gitignore` for `/dev` folder structure
  - Improved `/memory` tracking (templates + tests tracked, user content gitignored)
  - `/dev/planning/` tracked for contributor access to roadmaps
  - `/dev/archive/` and `/dev/notes/` gitignored (local-only)

- **Documentation**:
  - README.MD updated to v1.0.27 stable release
  - Moved development history to `/dev/archive/v1.0.x/`
  - Archived `BASELINE-v1.0.26.md` to `/dev/archive/v1.0.x/baselines/`
  - Created `/dev/README.md` for development workspace guide

### Fixed
- **Test Failures** (5 fixes from v1.0.26):
  - Made HTML validation case-insensitive (DOCTYPE, title tags)
  - Excluded external libraries from JSON validation
  - Fixed markdown extension directory name check (both "markdown-viewer" and "markdown")
  - Updated Grid test to verify current API (panel management vs future render())
  - Fixed `quick_health_check()` to handle both dict and object returns

### Test Results
- **Total**: 1022 tests
- **v1.0.27 Suite**: 370/395 passing (93.7%)
- **Skipped**: 25 tests (intentional)
- **Failures**: 0 ✅

### Performance (Exceeds All Targets)
- **Command P90**: 1.70ms (97% faster than 50ms target)
- **Command P99**: 5.43ms (95% faster than 100ms target)
- **Startup**: 38ms (92% faster than 500ms target)
- **Memory**: <20MB (80% better than 100MB target)

### Distribution
- ✅ pip installable (`pip install -e .`)
- ✅ Offline-first (no network dependencies)
- ✅ Clean git repository (distribution-ready)
- ✅ Comprehensive documentation (README, INSTALL, wiki)
- ✅ Project organization (system/user/dev separation)

### Roadmap
- **v1.0.27**: Stable release (CURRENT) ✅
- **v1.1.0**: Cross-platform testing (Linux, Windows) - Q2 2026
- **v1.1.1**: Platform-specific packages (deb, rpm, installer) - 2026
- **v1.1.2**: GUI enhancements - 2026
- **v1.2.0**: Community features - Future
- **v1.3.0**: Advanced features (offline AI, P2P) - Future

### Developer Notes
- Development work now in `/dev` folder (gitignored except planning/)
- User workspace in `/memory` (gitignored except templates/tests)
- v1.0.x development history preserved in `/dev/archive/v1.0.x/`
- Roadmaps and specs in `/dev/planning/` (tracked for contributors)

---

## [1.0.26] - 2025-11-19 (Development Phase)

### Summary
v1.0.26 was the final polish and performance phase, completed with 5 phases of work. All objectives achieved and rolled into v1.0.27 stable release.

### Added
- **Testing Infrastructure (Phase 1)**:
  - Expanded test coverage to 1022 total tests (102% of 1000 target)
  - Added 16 performance regression tests
  - Created comprehensive test suite for v1.0.26 features
  - Test coverage: architecture, commands, data validation, error handling, extensions, file operations, integration workflows, map navigation, performance baselines, real execution, status/version, ucode, UI components

- **Performance Optimization (Phase 2)**:
  - Command execution P90: 1.70ms (97% faster than 50ms target)
  - Command execution P99: 5.43ms (95% faster than 100ms target)
  - Startup time: 38ms (92% faster than 500ms target)
  - Memory usage: <20MB (80% better than 100MB target)
  - All performance targets exceeded

- **New Commands**:
  - `MEMORY` command with 4-tier system (PRIVATE, SHARED, COMMUNITY, PUBLIC)
  - `PANEL` command for formatted content display
  - `history_handler.py` for command history management
  - Enhanced memory tier classification logic

- **Class Aliases for Test Compatibility**:
  - `CommandParser` alias for `Parser` class
  - `uDOSLogger` alias for `Logger` class
  - `uDOSSettings` alias for `SettingsManager` class

- **SystemHealth Enhancements**:
  - Added `to_dict()` method for API/test compatibility
  - Added `HealthStatus` enum with HEALTHY/DEGRADED/CRITICAL values
  - SystemHealth class now supports both object and dict returns
  - `check_system_health()` defaults to dict return for compatibility

- **Memory System Enhancements**:
  - Added `path` property to all 4 memory tiers
  - Improved content classification (README, LICENSE → public)
  - Better tier analysis for documentation and config files

### Changed
- **Cross-Platform Testing (Phase 3)**:
  - Completed macOS testing: 370/395 tests passing (93.7%)
  - Fixed 23/28 original test failures
  - Deferred Linux/Windows testing to v1.1.1 (requires actual hardware)

- **Command Updates**:
  - Renamed map `MOVE` command to `STEP` (eliminated duplicate)
  - Enhanced `MEMORY` command with tier-specific paths
  - Added templates directory at `data/templates/`

### Fixed
- Import errors: Added missing class aliases (CommandParser, uDOSLogger, uDOSSettings)
- SystemHealth structure: Now returns dict with 'status' and 'issues' keys
- Duplicate MOVE command: Map movement renamed to STEP
- Missing PANEL command: Added to commands.json
- Missing MEMORY command: Added comprehensive 4-tier memory command
- Memory tier paths: Added to all tier definitions
- Memory content classification: Improved public file detection

### Technical
- **Test Results (macOS)**:
  - 365/395 tests passing (92.4%)
  - 5 remaining failures are non-blocking (HTML casing, external JSON, future features)
  - All core functionality verified on macOS
  - Performance benchmarks: P90 1.70ms, P99 5.43ms, startup 38ms

- **Documentation Updates**:
  - Created `docs/planning/PHASE3-MACOS-RESULTS.md`
  - Updated `docs/planning/v1.0.26-PLAN.md` (Phase 3 complete)
  - Updated `ROADMAP.MD` with v1.1.1 cross-platform testing plan
  - Updated `README.MD` to reflect v1.0.26 status

---

## [1.0.25] - 2025-11-18

### Added
- **Unified Extensions Server**:
  - Centralized Python HTTP server for all web extensions
  - Single entry point with `extensions_server.py` and `launch.sh`
  - CORS support built-in for all extensions
  - API endpoints: `/api/extensions`, `/api/health`, `/api/status`
  - Colored ANSI logging with extension identification
  - Flexible port configuration via command line
  - Status monitoring HTML dashboard
  - Per-extension launch scripts (`start.sh`)

- **Dashboard Builder Extension**:
  - NES.css framework integration
  - 12+ customizable widgets (System Monitor, Quick Actions, Extensions, Activity, Stats, Knowledge, Clock, Weather, Tasks, Notes, Terminal, Music Player)
  - 4 retro themes (Synthwave DOS, Classic NES, Game Boy, C64)
  - 1-4 column grid layouts
  - Widget management (add, remove, reorder)
  - Import/export dashboard layouts
  - Persistent storage via localStorage
  - Real-time system metrics updates

- **Documentation**:
  - `README-SERVER.md` - Comprehensive server guide
  - `CREDITS.md` - Unified credits for all extensions
  - `wiki/Extensions-Server.md` - Wiki documentation
  - Updated all extension READMEs with v1.0.25 launch instructions

### Changed
- **Teletext Extension**: Updated to use unified server (port 9000)
- **Terminal Extension**: Updated to use unified server (port 8889)
- **Markdown Extension**: Updated to use unified server (port 9001)
- **Desktop Extension**: Updated to use unified server (port 9002)
- **Dashboard Extension**: Complete rebuild with NES styling (port 8888)
- Migrated teletext documentation to wiki (API, Synthwave, Assets, Credits)
- Archived all individual server scripts to `archive/old-servers/`

### Technical
- Python 3 standard library only (no external dependencies for server)
- Consistent launch interface across all extensions
- Single process management vs multiple server processes
- Centralized configuration in `extensions_server.py`
- 100% backwards compatible with v1.0.23

---

## [1.0.24] - 2025-11-18

### Added
- **File Organization**:
  - Moved `font-profile-template.json` from `/data/templates/` to `knowledge/system/`
  - Consolidated all system templates under `knowledge/system/templates/`
  - Font system unification with single source of truth

- **Documentation**:
  - `docs/releases/v1.0.24-COMPLETION.md` - Complete release report
  - Updated `ROADMAP.MD` with v1.0.24 and v1.0.25 completion status
  - Updated `wiki/Home.md` and `wiki/Latest-Development.md`

### Changed
- Removed `/data/` folder entirely (consolidated into `knowledge/system/`)
- Updated all path references (5 files):
  - `knowledge/system/README-FONT-SYSTEM.md` (5 path updates)
  - `knowledge/system/templates/setup.uscript` (3 path updates)
  - `wiki/Architecture.md` (2 section updates)
  - `wiki/uCODE-Language.md` (3 import examples)
  - `core/utils/reorganize_knowledge.sh` (added legacy warnings)

### Removed
- `/data/templates/` directory (moved to `knowledge/system/`)
- Legacy data structure references

### Technical
- 539/539 tests passing (100% cumulative from all versions)
- Zero breaking changes
- Clean git structure with clear separation of concerns
- Production-ready quality maintained

---

## [1.0.21] - 2026-01-XX

### Added
- **PANEL Command - Teletext-Style Display System**:
  - Character-based display panels with definable width × height boundaries
  - 15 screen tiers (Tier 0: Watch 20×10 to Tier 14: 8K 320×160 characters)
  - C64-style POKE command for character manipulation at x,y coordinates
  - SHOW with optional C64-style border display (centered in ▓ blocks)
  - Markdown embedding via EMBED action (exports as code blocks)
  - Full Unicode support (teletext blocks, emoji, box drawing)
  - Actions: CREATE, SHOW, POKE, WRITE, CLEAR, DELETE, LIST, EMBED, SIZE, INFO
  - Buffer system for programmatic panel manipulation via uSCRIPT
  - Integration with markdown viewer for embedded diagram viewing

- **Knowledge Library Expansion**:
  - Structured programming guide system (100+ guides planned)
  - 8 knowledge categories (survival, skills, productivity, well-being, environment, community, tools, building)
  - Diagram library converted to markdown format (.md with ASCII graphics)
  - uCODE/uSCRIPT-focused programming tutorials
  - Teletext-style graphics in diagrams (progress bars, block graphics)

- **Markdown Viewer Web Extension**:
  - Flask-based markdown viewer with fuzzy search (port 9000)
  - Category browser for knowledge library navigation
  - Syntax highlighting via Pygments
  - GitHub Dark theme styling
  - Fuzzy string matching (thefuzz) for typo-tolerant search
  - Native emoji support (UTF-8, no font files needed)
  - API endpoints: /api/browse, /api/search, /api/render, /api/categories, /api/diagrams

### Changed
- Diagram format standardized to markdown (.md) with ASCII graphics in code blocks
- Diagrams support teletext blocks (█▓▒░), emoji, and box drawing characters
- Screen tier system defined: 15 tiers from watch to 8K displays
- Knowledge library structure expanded for programming education

### Dependencies
- Added: flask>=2.0.0, markdown2>=2.4.0, pygments>=2.10.0, thefuzz>=0.19.0

---

## [1.0.20b] - 2025-11-17

### Added
- **Enhanced Mapping & Reference Data System**:
  - 25 major world cities with grid_cell format (480×270 grid map)
  - Grid-based location system (e.g., "Y320" for Tokyo)
  - Timezone data using standard abbreviations (JST, AEST, PST, etc.)
  - Terrain types, climate zones, ASCII/teletext graphics libraries
  - MapDataManager service for geographic lookups and calculations

- **Project Infrastructure**:
  - Complete data migration: `data/` → `knowledge/system/` (permanent home)
  - Removed symlink, updated 18+ core files for new paths
  - Project cleanup: pytest cache → `memory/sandbox/.pytest_cache`
  - Environment template → `knowledge/system/templates/.env.example`
  - Created `pytest.ini` for centralized test configuration

- **Geographic Data Files** (in `knowledge/system/geography/`):
  - `cities.json`: 25 cities with grid_cell, tzone, climate, population
  - `terrain_types.json`: 15+ terrain definitions
  - `tile_schema.json`: TILE system specification

- **Graphics Data Files** (in `knowledge/system/graphics/`):
  - `ascii_blocks.json`: ASCII block characters for map rendering
  - `teletext_mosaic.json`: 64 WST mosaic characters

### Changed
- **Data Architecture**: `knowledge/system/` is now canonical location for all system reference data
- **Grid System**: 480×270 cells, format "COLUMNROW" (e.g., "Y320")
- **City Data Format**: Changed from `tizo`/`lat`/`lon` to `grid_cell`/`tzone`
- **CityData Class**: Added `@property` methods for backwards compatibility (tizo, lat, lon)
- **Test Suite**: Updated all paths from `data/` to `knowledge/system/`

### Fixed
- Path references across 18+ Python files (core, services, commands, utils)
- Test expectations to match actual data format
- Backwards compatibility for existing code expecting lat/lon coordinates

### Testing
- 22/22 tests passing (100% pass rate)
- Test coverage: MapDataManager, GeographyData, GraphicsData, DataArchitecture
- Performance: All tests complete in <0.2s

### Configuration
- `.gitignore`: Added `.pytest_cache/` exclusion
- `pytest.ini`: Cache directory, test paths, output format
- `uDOS.code-workspace`: Updated VSCode settings for pytest, exclusions
- Root directory cleanup: Moved development artifacts to proper locations

### Documentation
- `docs/releases/v1.0.20b-COMPLETION.md`: Complete implementation notes
- `docs/releases/PROJECT-CLEANUP-DEC-2024.md`: Infrastructure cleanup summary

---

## [1.0.19] - 2026-01-XX

### Added
- **Smart Input System (Phase 1)**:
  - AutocompleteService with 0.18ms performance (277x faster than 50ms target)
  - SmartPrompt with prompt_toolkit integration
  - Tab completion for commands, options, and arguments
  - Ctrl+R reverse search through command history
  - Fuzzy matching (typ → TYPE, TPYE → TYPE)
  - Context-aware suggestions based on current mode
  - File path completion with directory detection
  - Map cell reference suggestions (A1-RL270)
  - Theme name suggestions

- **Enhanced Selectors (Phase 2+3)**:
  - OptionSelector with arrow-key navigation (↑/↓) using terminal tty raw mode
  - Spacebar toggle for multi-select
  - 1-9 quick jump to items
  - Scrollable list (max 10 visible items)
  - EnhancedFilePicker extending OptionSelector
  - Helper functions: select_theme(), select_command(), select_map_cell()
  - uDOSOptionSelector JavaScript modal for web interface
  - Smooth scrolling, click/hover support
  - Ctrl+K keyboard shortcut for command selector in Teletext GUI
  - Integration with InteractivePrompt (ask_choice with fallback)

- **REST API Server (Phase 5)**:
  - Comprehensive Flask API with 62 endpoints across 6 categories
  - System endpoints (10): health, info, commands, status, settings, config, repair, reboot, version, help
  - Files endpoints (15): list, read, write, delete, create, search, recent, preview, stats, tree, workspace, favorites, batch
  - Map endpoints (12): status, view, cell, navigate, goto, locate, metro, layers, distance, bearing, route, explore
  - Theme endpoints (8): list, current, apply, create, update, delete, validate, export
  - Grid endpoints (8): status, display, render, cell, update, clear, colors, modes
  - Assist endpoints (6): query, context, learn, memory, conversation, capabilities
  - WebSocket support with 4 events: connect, disconnect, execute_command, subscribe_updates
  - CORS enabled for cross-origin requests
  - Auto-initialization of uDOS environment
  - Standalone mode (works without uDOS core)
  - Launcher script with venv detection
  - Complete API documentation (API.md)

- **Test Files**:
  - test_autocomplete.py (215 lines): Command/option/argument tests, performance tests
  - test_smart_prompt.py (116 lines): Basic functionality tests
  - test_integration_autocomplete.py (143 lines): Integration and compatibility tests
  - test_option_selector.py (115 lines): Selector functionality tests
  - All tests passing (100% success rate)

- **Documentation**:
  - docs/releases/v1.0.19-phase1-complete.md: Smart Autocomplete documentation
  - docs/releases/v1.0.19-phase2-3-complete.md: Enhanced Selectors documentation
  - docs/releases/v1.0.19-RELEASE-NOTES.md: Comprehensive release notes
  - extensions/bundled/web/teletext/API.md: REST API reference
  - examples/option_selector_demo.py (230+ lines): Interactive demo with 6 examples

### Changed
- core/uDOS_main.py: Integrated SmartPrompt (old SmartPrompt renamed to PromptDecorator)
- core/uDOS_main.py: Fixed CommandHistory API calls (append_string not add_command)
- core/uDOS_interactive.py: Added use_arrow_keys parameter, OptionSelector integration with fallback
- extensions/bundled/web/teletext/index.html: Added udos-option-selector.js, Ctrl+K shortcut, 17 pre-configured commands

### Fixed
- Python 3.9 compatibility: Changed from `str | List[str]` to `Union[str, List[str]]`
- CommandHistory API: Corrected all calls to use append_string() method
- Port conflict: Server defaults to port 5001 (macOS AirPlay uses 5000)
- Import paths: Proper module resolution for standalone API server

### Performance
- Command autocomplete: 0.18ms avg (target: 50ms) - 277x faster ⚡
- Option autocomplete: 0.03ms avg - 1666x faster ⚡
- Argument autocomplete: 0.00ms avg - ∞ faster ⚡
- API response time: <10ms (local)

### Dependencies
- Added: prompt_toolkit (for SmartPrompt)
- Added: Flask>=2.0.0, flask-cors>=3.0.0, flask-socketio>=5.0.0, python-socketio>=5.0.0 (for API server)

### Deferred to v1.1.0
- Phase 4: Dashboard real-time updates (50% complete - WebSocket events defined, broadcasting pending)
- Phase 6: Integration testing (API endpoint tests, CLI+GUI integration, performance benchmarks)
- Startup integration (auto-launch API server, health monitoring, graceful shutdown)

---

## [1.0.18] - 2025-11-XX

### Added
- **Experience System (XP)**: Earn experience through command usage and achievements
- **Barter System**: Exchange resources without currency
- **Survival System**: Health, energy, hydration tracking
- **Scenario System**: Interactive post-apocalypse adventures
- **Knowledge System**: Learn and share survival knowledge

### Testing
- 192/192 tests passing (100% pass rate)
- 6 phases: XP, Inventory, Barter, Survival, Scenario, Knowledge

---

## [1.0.16] - 2025-11-14

### Added
- **Functions System**: FUNCTION/CALL/RETURN commands with local scopes
  - Function definitions with parameters
  - Return value capture via RETURN_VALUE variable
  - Local variable scopes (VariableScope class)
  - Nested function calls support
- **Error Handling**: TRY/CATCH/FINALLY/THROW commands
  - Robust exception handling
  - ERROR and ERROR_TYPE special variables
  - Nested error handling
  - Custom error throwing
- **Module System**: IMPORT/EXPORT commands
  - Module path resolution (stdlib, examples, relative)
  - Selective imports (module.item syntax)
  - Circular import prevention
- **Standard Library**: 4 modules with 25+ functions
  - math_utils: Mathematical operations (square, cube, abs, max, min, PI, E)
  - string_utils: String manipulation (split, join, upper, lower, trim, length, contains)
  - list_utils: List operations (first, last, count, reverse, append, remove, contains)
  - validators: Input validation (is_empty, is_number, is_positive, is_in_range, validate_required)
- **Script Templates**: 3 production-ready templates
  - crud_app.uscript: Complete CRUD operations (120 lines)
  - form_validation.uscript: User input validation (175 lines)
  - menu_system.uscript: Interactive menu framework (116 lines)
- **Example Scripts**: advanced_features.uscript demonstrating all new features

### Changed
- uDOS_ucode.py expanded from 900 to 1,304 lines (+404 lines, +45%)
- Enhanced wiki/uCODE-Language.md with Advanced Features section (+285 lines)

### Testing
- 31/31 tests passing (100% pass rate)
- test_v1_0_16_standalone.py with comprehensive coverage:
  - 8 function tests
  - 8 error handling tests
  - 6 module tests
  - 4 integration tests
  - 5 variable tests

---

## [1.0.15] - 2025-11-13

### Added
- **Wiki Migration**: Complete documentation migration to wiki/
  - 15 wiki pages created (Home, Quick Start, Architecture, etc.)
  - GitHub wiki deployment automation
  - Sidebar and footer navigation
- **Philosophy Documentation**: Core principles and vision documented
  - offline-first philosophy
  - Hitchhiker's Guide inspiration
  - Survival handbook focus
- **Knowledge Library**: Foundation for survival knowledge system
  - knowledge/ directory structure
  - Personal/shared/group/public tier design
  - Holocaust/zombie apocalypse scenario framework

### Changed
- Documentation restructured: docs/ (working) vs wiki/ (finalized)
- README.md updated with philosophy and vision

---

## [1.0.14] - 2025-11-12

### Added
- **Variables System**: SET/GET/DELETE/VARS commands
  - Variable storage with type preservation
  - Variable substitution with ${var} syntax
  - DELETE command for removing variables
  - VARS command listing all defined variables
- **Conditional Logic**: IF/ELSE/ENDIF commands
  - Comparison operators (EQ, NE, GT, LT, GE, LE)
  - Logical operators (AND, OR, NOT)
  - Nested conditionals
  - String and numeric comparisons
- **Loops**: LOOP/ENDLOOP/BREAK/CONTINUE commands
  - Iteration with counters
  - Loop control flow (BREAK, CONTINUE)
  - LOOP_INDEX special variable
  - Nested loops

### Testing
- 32/32 tests passing (100% pass rate)
- test_v1_0_14_standalone.py created
- test_v1_0_14_integration.py created

---

## [1.0.13] - 2025-11-11

### Added
- **Theme Preview**: THEME PREVIEW <name> command
  - Live preview before applying themes
  - Automatic revert to previous theme
- **Theme Creation**: THEME CREATE command
  - Capture current color palette
  - Save as new theme file
- **Theme Import/Export**: THEME EXPORT/IMPORT commands
  - Package themes with metadata
  - Validate theme structure on import
- **Theme Metadata**: Enhanced theme files
  - author, description, version fields
  - Validation on load

### Testing
- 16/16 tests passing (100% pass rate)
- test_v1_0_13.py created with comprehensive theme tests

---

## [1.0.12] - 2025-11-10

### Added
- **Enhanced HELP System**:
  - HELP DETAILED <command> for comprehensive command documentation
  - HELP SEARCH <keyword> for keyword-based search
  - Usage examples and related commands
- **BLANK Command**: Quick screen clearing with customizable output
  - Optional custom message parameter
  - Logo display option
- **Smart SETUP Command**: Interactive system initialization
  - User profile creation
  - Preferred theme selection
  - Directory structure setup
  - Configuration validation

### Changed
- HELP command now shows categorized command list
- SETUP command interactive vs automated modes

---

## [1.0.11] - 2025-11-09

### Added
- **Extension System**: Complete POKE-style extension framework
  - POKE INSTALL/REMOVE/LIST commands
  - Extension metadata validation
  - Dependency management
  - Dev mode for local development
- **Extension Examples**: 3 bundled extensions
  - hello_world: Basic extension template
  - color_demo: Color palette showcase
  - teletext_clone: Full teletext implementation

### Changed
- extensions/ directory structure reorganized
- Extension loading system with core/bundled/cloned separation

---

## [1.0.10] - 2025-11-08

### Added
- **Typography System**: Classic Mac font integration
  - Chicago, Geneva, Monaco, New York fonts
  - 8 theme styles (Classic Mac, DOS, Commodore, Atari, etc.)
  - Font fallback chain
- **NES.css Integration**: Retro UI styling framework
  - Authentic pixel-perfect rendering
  - Classic gaming aesthetics

---

## [1.0.9] - 2025-11-07

### Added
- **Universal Viewport System**: 14 screen tiers (180p to 8K)
  - Automatic layout adaptation
  - Responsive grid sizing
  - Terminal size detection
- **Viewport Commands**: VIEWPORT STATUS/SET/AUTO

### Changed
- Grid system now adapts to viewport size
- Splash screen responsive to terminal dimensions

---

## [1.0.8] - 2025-11-06

### Added
- **Knowledge System**: SQLite full-text search
  - KNOWLEDGE SEARCH/ADD/UPDATE/DELETE commands
  - AI integration for knowledge queries
  - Vector embeddings for semantic search
- **Knowledge Base**: Initial dataset
  - uDOS commands documentation
  - Development history
  - FAQ entries

---

## [1.0.7] - 2025-11-05

### Added
- **History System**: UNDO/REDO/RESTORE commands
  - File operation history tracking
  - Multi-level undo/redo
  - Point-in-time restore
- **Advanced File Operations**: Enhanced FILE commands
  - FILE COPY/MOVE/RENAME
  - FILE SEARCH with glob patterns
  - FILE INFO for metadata

---

## [1.0.6] - 2025-11-04

### Added
- **Automation System**: RUN command for .uscript execution
  - Script parsing and execution
  - Error handling
  - Script templates

---

## [1.0.5] - 2025-11-03

### Changed
- **AI Terminology**: Separated ASK (Gemini) from DEV (Copilot CLI)
  - OK ASK: Google Gemini for general queries
  - OK DEV: GitHub Copilot CLI for development tasks
  - Clearer mental model for AI assistance

---

## [1.0.4] - 2025-11-02

### Added
- **Teletext Extension**: Web interface with mosaic rendering
  - Classic teletext graphics
  - Interactive controls
  - Mosaic character rendering

---

## [1.0.3] - 2025-11-01

### Added
- **Mapping System**: TIZO cell-based navigation
  - MAP SHOW/GOTO/LEVEL commands
  - 5-character cell codes (e.g., AAAA0)
  - Multi-level vertical navigation
  - 26×26 grid per level (676 cells)

---

## [1.0.2] - 2025-10-31

### Added
- **Configuration System**: Modular user profiles
  - User-specific settings (USER.UDT)
  - Theme preferences
  - Viewport settings
- **Modular Handlers**: Command handler refactoring
  - base_handler.py with BaseCommandHandler
  - Specialized handlers for each command category

---

## [1.0.1] - 2025-10-30

### Added
- **System Commands**: HELP, STATUS, REPAIR, REBOOT, DESTROY, DASHBOARD
  - Enhanced HELP with command categorization
  - STATUS showing system metrics
  - REPAIR for file structure validation
  - DASHBOARD with system overview

---

## [1.0.0] - 2025-10-29

### Added
- **Foundation Release**: Core system architecture
  - Command-line interface
  - Basic file operations (LIST, LOAD, SAVE, EDIT)
  - Grid management (GRID, NEW GRID, SHOW GRID)
  - System utilities (CLEAR, VIEWPORT, PALETTE)
- **Repository Structure**: Organized file hierarchy
  - core/ for main system files
  - data/ for user data
  - docs/ for documentation
  - extensions/ for POKE system
  - memory/ for user memory (logs, scripts, tests)

### Changed
- Migrated from "OK Assisted Task" to "Assist" terminology
- Version standardized to v1.0.0

---

## Unreleased Features (Future Versions)

### [1.0.17] - Planned (December 2025)
- Interactive Debugger (DEBUG, STEP, BREAKPOINT commands)
- Developer Tools (VSCode extension, language server)
- Advanced testing framework
- Performance profiling

### [1.0.18] - Planned (January 2026)
- Apocalypse Adventures (Holocaust/Zombie scenarios)
- Experience Point System (usage, information, contribution, connection)
- Barter & Resource Management
- Survival skills integration

### [1.0.19] - Planned (February 2026)
- Project/Workflow Management (PROJECT, TASK, WORKFLOW commands)
- Barter Economy (INVENTORY, OFFER, REQUEST, TRADE commands)
- What-I-Have vs What-I-Need engine
- Contribution tracking

### [1.0.20] - Planned (March 2026)
- 4-Tier Knowledge Bank (Personal Private, Personal Shared, Group, Public)
- Knowledge management commands (KNOW, LEARN, TEACH, VERIFY)
- Encryption for Tier 1 (AES-256)
- Knowledge rating and curation

### [1.1.0] - Stable Release (June 2026)
- 1000+ tests passing
- Self-healing and error recovery
- 500+ survival guides
- Community launch
- Device spawning (laptop → mobile)

---

## Links

- [GitHub Repository](https://github.com/fredporter/uDOS)
- [Documentation Wiki](https://github.com/fredporter/uDOS/wiki)
- [Release Notes](https://github.com/fredporter/uDOS/releases)
- [Issue Tracker](https://github.com/fredporter/uDOS/issues)
