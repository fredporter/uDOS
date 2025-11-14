# Changelog

All notable changes to uDOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
