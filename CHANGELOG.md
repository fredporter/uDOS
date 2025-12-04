# Changelog

All notable changes to uDOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres on [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### v1.2.3 - Knowledge & Map Layer Expansion (December 4, 2025)

**Multi-Layer Mapping:** Complete 4-layer map system with spatial data structures for Earth, solar system, and galaxy navigation.

#### Added

**Map Layer System (500 lines across 4 files)**
- `extensions/play/data/layers/surface.json` (150 lines) - Physical surface layer (Layer 100)
  - Elevation ranges (-11,034m deep ocean to 8,849m mountains)
  - 8 terrain types (water, plains, forest, desert, tundra, mountain, ice, swamp)
  - 9 biome classifications (Köppen climate zones)
  - Sample tiles for Sydney, London, Pacific Ocean
  - Survival-relevant terrain data
- `extensions/play/data/layers/cloud.json` (90 lines) - Atmospheric layer (Layer 600)
  - 5 cloud types (cirrus, cumulus, cumulonimbus, stratus, clear)
  - Precipitation types (drizzle, rain, heavy rain, snow, hail)
  - Wind speed and atmospheric pressure data
  - Weather patterns for major cities
- `extensions/play/data/layers/satellite.json` (120 lines) - Orbital layer (Layer 700)
  - 3 orbit types (LEO 400km, MEO 20,200km, GEO 35,786km)
  - 5 satellite types (communications, navigation, observation, weather, space station)
  - GPS/GNSS coverage data
  - Mesh networking integration notes for v1.2.9
- `extensions/play/data/layers/underground.json` (140 lines) - Subterranean layer (Layer 50)
  - 4 geological layers (soil, regolith, bedrock, deep crust)
  - 5 structure types (caves, aquifers, tunnels, bunkers, mines)
  - 3 aquifer types (unconfined, confined, artesian)
  - Survival applications (water sources, shelter, resources)

**Spatial Data Structures (720 lines across 3 files)**
- `core/data/spatial/locations.json` (200 lines) - Earth location database
  - 6 continents with TILE code ranges
  - 4 major cities (Sydney, London, Tokyo, New York) with:
    * TILE codes (AA340-100, JF57-100, LB110-100, QD95-100)
    * Survival resources (water, shelter, food, climate)
    * Population and elevation data
  - 3 survival landmarks (Great Barrier Reef, Amazon Rainforest, Sahara Desert)
  - Hazard assessments and resource availability
- `core/data/spatial/planets.json` (240 lines) - Solar system database
  - Sol (Sun) stellar data
  - 5 planets detailed (Mercury, Venus, Earth, Mars, Jupiter)
  - Orbital mechanics (semi-major axis, eccentricity, period)
  - Physical data (mass, radius, gravity, escape velocity)
  - Atmospheric composition and surface conditions
  - Mars colonization potential (survival rating 3/10, water ice present)
  - Celestial navigation applications
- `core/data/spatial/galaxies.json` (280 lines) - Galactic structures database
  - Milky Way structure (barred spiral, 400 billion stars)
  - Solar system location (Orion Arm, 26,000 ly from center)
  - Local Group (54 galaxies, Andromeda collision in 4.5B years)
  - 5 navigation stars (Sirius, Polaris, Betelgeuse, Rigel, Vega)
  - 7 key constellations (Ursa Major/Minor, Cassiopeia, Orion, Southern Cross, etc.)
  - Celestial navigation methods for survival scenarios

**GeoJSON Visualization (130 lines)**
- `extensions/play/data/geojson/grid_layer_100.geojson` - Sample TILE grid export
  - 5 representative tiles (Sydney, London, Tokyo, NYC, Pacific Ocean)
  - Polygon geometries with properties (elevation, terrain, biome, population)
  - CRS84 coordinate system (WGS84 lon/lat)
  - GitHub Maps compatible format
  - Integration with geojson.io and Mapshaper
  - Foundation for full 129,600-cell export in v1.2.4

**Integration Testing (300 lines)**
- `memory/ucode/test_v1_2_3_features.py` - Comprehensive feature validation
  - 14 tests covering all v1.2.3 deliverables
  - Map layer tests (structure, data types, sample tiles)
  - Spatial data tests (locations, planets, galaxies)
  - GeoJSON tests (format validation, feature integrity)
  - Map engine integration tests (layer loading compatibility)
  - Test results: 14/14 passing (100% success rate, 0.05s execution time)

**Documentation**
- `dev/sessions/2025-12-v1.2.3-implementation.md` (400 lines) - Complete session log
  - Implementation details for all 4 layers
  - Spatial data structure design decisions
  - GeoJSON export methodology
  - Integration points with existing map engine
  - Future expansion roadmap (v1.2.4 MAP commands, v1.2.5 mesh integration)

#### Changed

**Roadmap Updates**
- Renumbered v1.3.0 → v1.2.8 (Cross-Platform Distribution)
- Renumbered v1.4.0 → v1.2.9 (Device Management & Multi-Protocol Mesh)
- Removed all calendar timeframes (weeks, months, dates)
- Replaced with MOVES/STEPS measurement system
- Updated all internal references and dependencies
- Marked v1.2.3 as PRIORITY release

#### Metrics

**Code Delivered**
- Map layers: 500 lines (4 JSON files)
- Spatial data: 720 lines (3 JSON files)
- GeoJSON: 130 lines (1 file)
- Integration tests: 300 lines (14 tests)
- Documentation: 400 lines (session log)
- **Total: 2,050 lines delivered**

**Test Coverage**
- 14/14 integration tests passing (100%)
- All map layers validated
- All spatial data structures validated
- GeoJSON format validated
- Map engine compatibility confirmed

**System Impact**
- New directory: `core/data/spatial/` (3 files)
- New directory: `extensions/play/data/layers/` (4 files)
- New directory: `extensions/play/data/geojson/` (1 file)
- Map engine ready for multi-layer support
- Foundation for v1.2.4 MAP commands
- Foundation for v1.2.5 mesh location sharing

---

### v1.2.2 - DEV MODE Debugging System (December 3, 2025)

**Interactive Debugging:** Professional-grade debugging system for uPY scripts with breakpoints, step execution, variable inspection, and trace logging.

#### Added

**DEV MODE System (1,399 lines across 3 files)**
- `core/services/debug_engine.py` (462 lines) - Core debugging engine
  - Breakpoint management with conditional support
  - Step execution control (line-by-line)
  - Variable inspection with nested object access
  - Call stack tracking with frame navigation
  - Watch list for monitoring critical variables
  - Trace logging with detailed execution history
  - State persistence (save/load debug sessions)
- `core/commands/dev_mode_handler.py` (583 lines) - Command interface
  - 10 command groups: ENABLE, DISABLE, STATUS, BREAK, STEP, CONTINUE, INSPECT, STACK, TRACE, WATCH, HELP
  - Formatted status dashboard with breakpoints/call stack/watches
  - State persistence to `memory/system/debug_state.json`
  - Integration with unified logger for trace output
- `core/runtime/upy_executor.py` (354 lines) - Enhanced script executor
  - Line-by-line execution with debug integration
  - `#BREAK` directive support for embedded breakpoints
  - Breakpoint pause logic with callback support
  - Debug mode toggle for production/development

**Testing & Validation**
- `core/commands/shakedown_handler.py` - Replaced old DEV MODE security test with 10 new debugging tests
  - Test 1: DebugEngine import and initialization
  - Test 2: DevModeHandler import and routing
  - Test 3: UPYExecutor import with debug support
  - Test 4: Breakpoint management (set, remove, toggle, conditional)
  - Test 5: Variable inspection (simple and nested)
  - Test 6: Call stack tracking
  - Test 7: Watch list management
  - Test 8: State persistence (save/load)
  - Test 9: #BREAK directive support
  - Test 10: DEV MODE commands (ENABLE, STATUS, BREAK, DISABLE)
  - Test results: 10/10 passing (100% success rate)

**Documentation (936 lines)**
- `wiki/DEV-MODE-Guide.md` - Comprehensive debugging guide
  - 13 sections covering all aspects of DEV MODE
  - Command reference with syntax and examples
  - Breakpoints (simple and conditional)
  - Step execution workflows
  - Variable inspection (simple and nested objects)
  - Call stack analysis
  - Trace logging configuration
  - Watch variable management
  - 3 practical examples (loop debugging, conditional breakpoints, mission workflows)
  - Best practices and anti-patterns
  - Troubleshooting guide

**Knowledge Expansion Infrastructure**
- `core/data/knowledge_topics.json` - Already exists (100 planned topics)
  - 14 categories with gap analysis
  - Target: 236 total guides (currently 228)
  - Priority ratings and difficulty levels
  - Word count targets per guide
- `memory/workflows/missions/knowledge-expansion.upy` - Already exists (1,353 lines v1.1.19)
  - 6-phase workflow (gap analysis, generation, review, validation, commit, report)
  - Batch processing with GENERATE GUIDE integration
  - Quality review automation with 85% threshold
  - Smart git commit by category

#### Changed

**Command Routing**
- `core/uDOS_commands.py` - Added DEV module routing
  - Line ~227: Added `DevModeHandler` initialization
  - Line ~505: Added `DEV` module routing to `dev_mode_handler.handle()`

**Python 3.9 Compatibility**
- `core/services/debug_engine.py` - Fixed datetime deprecation
  - Changed `datetime.UTC` to `datetime.timezone.utc` (3 occurrences)
  - Timestamps now use `datetime.now(timezone.utc)`
- `core/services/unified_logger.py` - Fixed datetime deprecation
  - Changed `datetime.UTC` to `datetime.timezone.utc` (3 occurrences)
  - Log timestamps use timezone-aware UTC

**uPY Executor**
- `core/runtime/upy_executor.py` - Fixed result type handling
  - Added string conversion for non-string results before joining
  - Prevents "expected str instance, tuple found" error
  - Ensures `#BREAK` directive test passes in SHAKEDOWN

#### Fixed

**Import Errors**
- Resolved "cannot import name 'UTC' from 'datetime'" error
- All imports verified with `python3 -c` test commands
- Debug engine, DEV MODE handler, and uPY executor all import successfully

**SHAKEDOWN Tests**
- Replaced outdated `_test_dev_mode()` security test with new debugging tests
- All 10 new tests passing (previously 9/10 due to #BREAK string issue)
- Test coverage: 118 total tests, 115 passing (97.5% success rate)

#### Metrics

**Code Delivered**
- DEV MODE system: 1,399 lines (debug_engine + dev_mode_handler + upy_executor)
- Documentation: 936 lines (wiki/DEV-MODE-Guide.md)
- Tests: 10 comprehensive tests in shakedown_handler.py
- Total: 2,335+ lines

**Test Results**
- DEV MODE tests: 10/10 passing (100%)
- Overall SHAKEDOWN: 115/118 passing (97.5%)
- Failed tests unrelated to DEV MODE (Memory, API, Performance metrics)

**Production Readiness**
- ✅ All imports working (Python 3.9 compatible)
- ✅ Breakpoint system functional
- ✅ Step execution validated
- ✅ Variable inspection working (simple and nested)
- ✅ Call stack tracking operational
- ✅ State persistence tested
- ✅ #BREAK directive supported
- ✅ Complete documentation available

---


## Archive

For v1.1.x release notes and older versions, see:
- **[v1.1.x Changelog](wiki/.archive/CHANGELOG-v1.1.x.md)** - Complete v1.1.0 through v1.1.18 history
- **v1.0.x and earlier** - Historical development builds (see archived changelog)

---

## Links

- [GitHub Repository](https://github.com/fredporter/uDOS)
- [Documentation Wiki](https://github.com/fredporter/uDOS/wiki)
- [Release Notes](https://github.com/fredporter/uDOS/releases)
- [Issue Tracker](https://github.com/fredporter/uDOS/issues)
