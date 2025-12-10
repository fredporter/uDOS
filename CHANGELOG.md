# Changelog

All notable changes to uDOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres on [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Future Development

See [ROADMAP.md](dev/roadmap/ROADMAP.MD) for planned features and development priorities.

---

## Released

---

## [1.2.22] - 2025-12-09

### v1.2.22 - TUI Smart Input Navigation Fixes (v2 - FINAL)

**Bug Fix Release:** Fixed numpad navigation to work properly with completion menus and enhanced keyboard shortcuts.

#### Fixed

**TUI Smart Input System - Priority-Based Numpad Navigation**
- **Completion Menu Navigation** - Fixed critical issue where numpad keys inserted digits instead of navigating when completion menu was open
  - Changed priority order: Check completion menu state FIRST, then buffer state
  - **Priority 1:** Completion menu open → Numpad ALWAYS navigates (even if text present)
  - **Priority 2:** Buffer empty (no menu) → Numpad navigates history/pager
  - **Priority 3:** Text present (no menu) → Numpad inserts digits
  - Example: Type "R" → menu shows READ, REBOOT → Press 8 → Navigate up ✅ (previously inserted "8" ❌)

- **Three-State Navigation Logic** - Context-aware numpad behavior:
  - **State 1 (Empty + Menu):** Numpad 8/2 = History navigation, 5 = Submit
  - **State 2 (Text + Menu):** Numpad 8/2 = Menu navigation, 5 = Accept, Esc = Close
  - **State 3 (Text + No Menu):** Numpad 0-9 = Insert digits (e.g., "XP 100")

- **Enhanced Keyboard Shortcuts** - Added missing key bindings:
  - Tab key: Trigger/navigate completions (start menu or move to next item)
  - Esc key: Close completion menu (dismiss suggestions)
  - Arrow keys: Verified proper navigation in both menu and history modes
  - Right arrow/Tab: Accept selected completion

#### Enhanced

**Command Completion Display**
- Increased command suggestions from 10 to 25 maximum results
- Typing single letter now shows all matching commands (e.g., 'r' shows REBOOT, REPAIR, RUN, READ, REPORT, etc.)
- Empty input suggestions increased from 10 to 15 common commands
- Better visibility of available commands when typing

**Developer Tools**
- Added `dev/tools/demo_smart_input.py` - Interactive demo with visual guides
- Added `dev/tools/test_smart_input.py` - Automated test suite (5/5 passing)
- Updated `wiki/TUI-Smart-Input-Guide.md` - Complete keyboard reference

#### Technical Details
- Modified: `core/input/smart_prompt.py` (Lines 210-340)
  - Changed numpad 8/2/5/6 to priority-based logic
  - Added Tab and Esc key handlers
  - Enhanced completion menu state checking
- Zero performance impact, 100% backward compatible
- Graceful degradation when keypad disabled

#### Testing
- ✅ All 5 automated tests passing
- ✅ Completion menu navigation with numpad (8↑ 2↓)
- ✅ Tab/Esc keys for menu control
- ✅ Number insertion when no menu open
- ✅ History navigation when buffer empty

---

## [1.2.21] - 2025-12-08

### v1.2.21 - OK Assistant & AI Workflows (FINAL STABLE v1.2.x)

**Major Feature Release:** AI-assisted workflow generation with OK command panel, context-aware assistance, configuration management, and complete Gemini integration.

#### Added

**OK Assistant System** (760 lines across 11 files)
- **OK Command Panel** (`core/ui/ok_assistant_panel.py` - 263 lines)
  - O-key opens interactive TUI panel
  - 8 quick prompts (MAKE WORKFLOW/SVG/DOC/TEST/MISSION, explain, optimize, custom)
  - Conversation history (last 10 exchanges with timestamps)
  - Context display (workspace, TILE location, current file)
  - Two views: prompts list and history
  - Persistent history in `memory/system/user/ok_history.json`

- **Context-Aware Assistance** (200 lines)
  - `core/services/ok_context_manager.py` (261 lines) - Workspace tracking
  - `extensions/assistant/context_builder.py` (213 lines) - Prompt augmentation
  - Tracks workspace state, TILE location, recent commands, git status
  - Builds context-aware prompts for AI (general, code, debug, generate, explain)
  - Git status integration (modified/added/deleted/untracked files)
  - Error capture and context injection

- **OK Configuration** (100 lines)
  - `core/services/ok_config.py` (237 lines) - Settings management
  - `core/ui/config_browser.py` (+20 lines) - [OK] tab integration
  - Settings: model (4 options), temperature (0.0-2.0), max_tokens (100-100k)
  - Cost tracking enabled/disabled
  - Context length (1-20 commands)
  - Auto-save history and retention (1-365 days)
  - Persistent storage in `memory/system/user/ok_config.json`

- **OK Workflow Commands** (150 lines)
  - `core/commands/ok_handler.py` (563 lines) - Command handler
  - OK MAKE WORKFLOW - Generate uPY workflow scripts
  - OK MAKE SVG - Generate SVG graphics with AI
  - OK MAKE DOC - Generate documentation (markdown)
  - OK MAKE TEST - Generate unit tests (pytest)
  - OK MAKE MISSION - Generate mission scripts
  - OK ASK - Ask AI assistant questions
  - OK CLEAR - Clear conversation history
  - OK STATUS - Show usage statistics and config
  - Code extraction from AI responses
  - Output to appropriate directories (workflows/, drafts/svg/, docs/, tests/)
  - Usage tracking and statistics

**TUI Integration**
- O-key binding in `SmartPrompt` to open OK panel
- Panel rendering in main loop
- Commands: ESC (close), C (clear), P (prompts view), H (history view)
- Numpad navigation: 8/2 (navigate), 5 (select)

#### Changed

**Command Routing**
- Updated `core/uDOS_commands.py` (+11 lines) - OK handler integration
- OK commands now route to `ok_handler` before `assistant_handler`
- Updated `core/data/commands.json` - OK command definition v1.2.21

#### Fixed

**Import Errors**
- Fixed `core.utils.path_manager` → `core.utils.paths` (2 files)
- Fixed malformed import in `dashboard_handler.py`

**Command Parsing**
- OK commands now parse as `[OK|...]` instead of `[ASSISTANT|OK...]`

#### Notes

- **v1.2.21 is the FINAL STABLE release of the v1.2.x track**
- All 4 implementation tasks completed (760 lines delivered)
- 6 bug fixes applied during testing
- Requires `GEMINI_API_KEY` in `.env` for AI features
- Falls back gracefully when API not available
- Complete integration with existing TUI system (v1.2.15)

---

## [1.2.15] - 2025-12-08

### v1.2.15 - Unified Graphics System & Setup Modernization (December 8, 2025)

**Major Feature Release:** 5-format graphics system with unified MAKE command, Node.js rendering service, template library, and comprehensive path/config modernization.

#### Added

**Five-Format Graphics System**
- **ASCII Graphics** (25 templates): Flowcharts, systems, progress, funnels, timelines, decisions, org charts, networks, data views, UI mockups, process flows
- **Teletext Graphics** (4 palettes): Classic 8-color ANSI rendering with earth, terminal, amber themes
- **SVG Graphics** (3 styles): Technical (blueprint), simple (minimalist), detailed (comprehensive) with AI-assistant integration
- **Sequence Diagrams** (5 templates): Message flows, API requests, error handling, multi-system, async processes using js-sequence-diagrams
- **Flow Diagrams** (5 templates): Decision trees, login processes, data pipelines, business logic, error recovery using flowchart.js

**Template Library** (`core/data/diagrams/` - 44 files)
- `core/data/diagrams/ascii/` - 25 .txt template files with variable substitution
- `core/data/diagrams/teletext/` - 4 JSON palette definitions (8-color ANSI system)
- `core/data/diagrams/svg/` - 3 JSON style templates with gradient/color schemes
- `core/data/diagrams/sequence/` - 5 .seq template files (js-sequence syntax)
- `core/data/diagrams/flow/` - 5 .flow template files (flowchart.js syntax)
- `core/data/diagrams/README.md` (169 lines) - Complete template documentation
- `core/data/diagrams/catalog.json` (133 lines) - Programmatic template catalog

**Node.js Graphics Renderer** (`extensions/core/graphics-renderer/` - 10 files, 1,153 lines)
- `server.js` (177 lines) - Express server on port 5555 with 8 REST endpoints
- `renderers/ascii.js` (83 lines) - Template loading with variable substitution
- `renderers/teletext.js` (104 lines) - 8-color ANSI rendering with palette support
- `renderers/svg.js` (105 lines) - SVG generation with style templates
- `renderers/sequence.js` (67 lines) - js-sequence-diagrams integration
- `renderers/flow.js` (88 lines) - flowchart.js integration
- `package.json` (43 lines) - NPM dependencies (express, js-sequence-diagrams, flowchart.js, canvas, puppeteer)
- `extension.json` (61 lines) - Extension metadata for port 5555
- `README.md` (330 lines) - Complete API documentation

**Graphics Service Bridge** (`core/services/graphics_service.py` - 295 lines)
- Python HTTP client for Node.js renderer service
- 5 render methods: `render_ascii()`, `render_teletext()`, `render_svg()`, `render_sequence()`, `render_flow()`
- Health checking with service availability detection
- Error handling with graceful degradation
- Session statistics tracking
- Template listing and validation

**MAKE Command** (`core/commands/make_handler_v1_2_15.py` - 700 lines)
- **Unified --format syntax** replaces old GENERATE/DIAGRAM commands
- Common options: `--format <type>`, `--output <file>`, `--list`, `--status`, `--help`
- Format-specific options:
  - ASCII: `--template`, `--width`, `--border`
  - Teletext: `--palette`, `--source`
  - SVG: `--style`, `--ai-assisted`, `--source`
  - Sequence: `--template`, `--source`
  - Flow: `--template`, `--source`
- Automatic output to `memory/drafts/<format>/`
- Template browsing with `MAKE --list ascii|teletext|svg|sequence|flow`
- Session statistics with `MAKE --status`
- 6 help modes: general + 5 format-specific

**Path Management System** (`dev/tools/audit_hardcoded_paths.py` - 230 lines)
- Scans all .py files for hardcoded path strings
- Reports violations with file/line/context
- Validates PATHS constant usage
- Generates compliance report

**Config System Rebuild** (`core/services/config_initializer.py` - 335 lines)
- Schema v1.2.15 with comprehensive validation
- Auto-initialization of missing directories
- Backward compatibility with v1.2.12 configs
- Environment variable templating (${HOME}, ${UDOS_ROOT})
- Wizard mode for first-time setup
- Health check with repair options

#### Changed

**Breaking Changes**
- `GENERATE` command deprecated → Use `MAKE --format <type>`
- `DIAGRAM` command deprecated → Use `MAKE --format ascii|teletext|svg`
- Old `core/data/diagrams/` templates removed → New template library structure

**Migration Guide**
```bash
# Old syntax (deprecated)
GENERATE SVG water_filter water
DIAGRAM flowchart decision_tree

# New unified syntax (v1.2.15+)
MAKE --format svg --style technical --ai-assisted --source "water filter system"
MAKE --format ascii --template flowchart --border double "decision tree"
MAKE --format sequence --template api_request "user login flow"
MAKE --format flow --template decision_flow "error handling"
MAKE --format teletext --palette earth "welcome screen"
```

**Command Reference Updates**
- `MAKE` added to `core/data/commands.json` (119 lines)
- Complete format documentation with 13 usage examples
- Template catalog breakdown (25+4+3+5+5=42 templates)
- Format-specific option reference

**Port Registry**
- Port 5555 registered for graphics-renderer service
- Updated `extensions/PORT-REGISTRY.md`

#### Fixed
- Eliminated all hardcoded paths in favor of PATHS constants
- Config system handles missing directories gracefully
- Template loading errors provide helpful diagnostics

#### Testing

**Integration Tests** (`memory/ucode/tests/` - 312 lines)
- `test_config_v1_2_15.py` (158 lines) - 14 test methods for config system
- `test_path_integrity.py` (154 lines) - 19 test methods for path validation

**Demo Scripts** (`memory/ucode/examples/` - 326 lines)
- `demo_config_wizard.upy` (143 lines) - Interactive config setup walkthrough
- `demo_path_validation.upy` (183 lines) - Path compliance demonstration

#### Developer Notes

**Architecture**
- Clean separation: Templates (offline) → Node.js service (rendering) → Python bridge (command layer)
- Offline-first: Templates work without service, AI features optional
- Health checks: Python bridge detects service availability
- Port isolation: Graphics renderer on dedicated port 5555

**Dependencies**
- **Node.js**: v18+ for graphics-renderer service
- **NPM packages**: express, body-parser, cors, js-sequence-diagrams, flowchart.js, canvas, puppeteer
- **Python**: requests (HTTP client), PATHS constants (path management)

**File Organization**
- Development tools: `dev/tools/`, `dev/sessions/`
- Core templates: `core/data/diagrams/` (tracked in git)
- User output: `memory/drafts/<format>/` (gitignored)
- Renderer service: `extensions/core/graphics-renderer/`

**Credits**
- Built on v1.2.12 PATHS foundation
- Node.js renderer architecture inspired by offline-first design
- Template library structure follows v1.2.x standards

#### Files Added
- `dev/tools/audit_hardcoded_paths.py` (230 lines)
- `core/services/config_initializer.py` (335 lines)
- `core/services/graphics_service.py` (295 lines)
- `core/commands/make_handler_v1_2_15.py` (700 lines)
- `core/data/diagrams/README.md` (169 lines)
- `core/data/diagrams/catalog.json` (133 lines)
- `core/data/diagrams/ascii/` (25 template files)
- `core/data/diagrams/teletext/` (4 palette files)
- `core/data/diagrams/svg/` (3 style files)
- `core/data/diagrams/sequence/` (5 template files)
- `core/data/diagrams/flow/` (5 template files)
- `extensions/core/graphics-renderer/package.json` (43 lines)
- `extensions/core/graphics-renderer/server.js` (177 lines)
- `extensions/core/graphics-renderer/renderers/ascii.js` (83 lines)
- `extensions/core/graphics-renderer/renderers/teletext.js` (104 lines)
- `extensions/core/graphics-renderer/renderers/svg.js` (105 lines)
- `extensions/core/graphics-renderer/renderers/sequence.js` (67 lines)
- `extensions/core/graphics-renderer/renderers/flow.js` (88 lines)
- `extensions/core/graphics-renderer/extension.json` (61 lines)
- `extensions/core/graphics-renderer/README.md` (330 lines)
- `memory/ucode/tests/test_config_v1_2_15.py` (158 lines)
- `memory/ucode/tests/test_path_integrity.py` (154 lines)
- `memory/ucode/examples/demo_config_wizard.upy` (143 lines)
- `memory/ucode/examples/demo_path_validation.upy` (183 lines)

**Phase 1 Total:** 1,203 lines (path audit, config system, tests, demos)
**Phase 2 Total:** 2,986 lines across 57 files (templates, renderer, command handler)
**Grand Total:** 4,189 lines

---

## [1.2.13] - 2025-12-07

### v1.2.13 - Complete TUI Input & File Management Overhaul (December 7, 2025)

**Major Feature Release:** Revolutionary terminal user interface with keypad navigation, smart command prediction, enhanced paging, and workspace-aware file browsing.

#### Added

**Keypad Navigation System** (`core/ui/keypad_navigator.py`)
- Numpad-style 4-way movement: 8 (↑), 2 (↓), 4 (←), 6 (→)
- Action keys: 5 (select/confirm), 7 (undo), 9 (redo)
- History navigation: 1 (back), 3 (forward)
- Menu toggle: 0 (open/close)
- Mode-aware: command, menu, browser, pager
- Persistent state with undo/redo stacks
- Command history tracking (last 100 commands)

**Smart Command Predictor** (`core/ui/command_predictor.py`)
- Syntax-aware completions from `commands.json` schema
- Real-time COMMAND token highlighting (commands, args, paths, flags, values)
- Learning from command frequency (tracks usage patterns)
- Fuzzy matching for typo tolerance
- Ranked predictions with confidence scores (0.0-1.0)
- Source tracking: history, schema, fuzzy
- Argument prediction based on command schemas
- Color-coded tokens: green (valid cmd), yellow (unknown), cyan (flags), magenta (paths)

**Enhanced Pager** (`core/ui/pager.py`)
- Scroll-while-prompting: Navigate output while typing new commands
- Preserve scroll position across commands (configurable)
- Visual scroll indicators: ▲ (more above), ▼ (more below)
- Multi-key support: 8/2 (keypad), Space/k/j (vi-style), arrows, PgUp/PgDn
- Status line: "Lines X-Y of Z (N%)"
- Search functionality: Find text in output (forward/backward)
- Configurable viewport height
- Auto-scroll to bottom option

**Workspace-Aware File Browser** (`core/ui/file_browser.py`)
- 5 predefined workspaces:
  - `knowledge/` - Core distributable knowledge base (read-only)
  - `memory/docs/` - User documentation
  - `memory/drafts/` - Work in progress
  - `memory/ucode/sandbox/` - Experimental scripts
  - `memory/ucode/scripts/` - User scripts
- Filtered views: Show only .upy, .md, .json files
- Recursive subdirectory navigation
- Breadcrumb paths: "workspace > folder > subfolder"
- File statistics: Size, type icons (🐍 .upy, 📄 .md, 📊 .json, 📁 folders)
- Workspace cycling: Press 0 to switch between workspaces
- Search by filename
- Hidden file toggle

**TUI Integration** (`core/ui/tui_controller.py`)
- Master controller coordinating all TUI components
- Unified key handling across modes
- State persistence (keypad_state.json, predictor_state.json)
- Mode management: command, browser, pager
- Global TUI instance with `get_tui()` accessor

**TUI Configuration** (`core/ui/tui_config.py`)
- Centralized settings management
- Default config:
  - `keypad_enabled: false` (opt-in)
  - `preserve_scroll: true`
  - `show_scroll_indicators: true`
  - `prediction_max_results: 5`
  - `browser_filter: [.upy, .md, .json]`
  - `syntax_highlighting: true`
- Auto-save on change (configurable)
- Export/import config files
- Reset to defaults option

#### Changed

**Enhanced User Experience**
- Command line now supports real-time syntax highlighting
- Output can be scrolled without losing current prompt
- File selection integrated into workflow (no separate dialogs)
- Predictive text reduces typing for common commands
- Undo/redo for command editing

**Performance Optimizations**
- Prediction caching (top 50 commands)
- Index by first character for fast lookup
- Max 200ms response time for predictions
- Virtual scrolling in browser (20-item windows)
- Async subdirectory loading

#### Developer Notes

**Testing**
- Comprehensive test suite: `memory/ucode/tests/test_tui_system.py`
- 20+ test cases covering all TUI components
- Integration workflow tests
- Mocked terminal input sequences

**Configuration Files**
- `memory/system/user/tui_config.json` - User preferences
- `memory/system/user/keypad_state.json` - Navigation state
- `memory/system/user/predictor_state.json` - Learning data

**Migration**
- Fully backward compatible (keypad disabled by default)
- Legacy input mode still works
- Feature flags: `LEGACY_INPUT_MODE` in config
- Gradual opt-in adoption path

**Accessibility**
- Keypad can be toggled off for screen readers
- Standard arrow keys still work
- Verbose mode option for non-visual users

#### Files Added
- `core/ui/keypad_navigator.py` (417 lines)
- `core/ui/command_predictor.py` (337 lines)
- `core/ui/pager.py` (289 lines)
- `core/ui/file_browser.py` (410 lines)
- `core/ui/tui_controller.py` (168 lines)
- `core/ui/tui_config.py` (115 lines)
- `memory/ucode/tests/test_tui_system.py` (331 lines)

**Total:** 2,067 lines of new TUI infrastructure

---

## [1.2.12] - 2025-12-07

### v1.2.12 - Path Refactoring & Python 3.9+ Compatibility (December 7, 2025)

**Infrastructure Release:** Centralized path management, eliminated hardcoded paths, and ensured Python 3.9+ compatibility.

#### Changed

**Path Refactoring (101 changes across 58 files)**
- Migrated all hardcoded path strings to `core/utils/paths.py` PATHS constants
- 3 batches: commands (28 files), services (14 files), extensions/utils (11 files)
- Benefits: Single source of truth, easier path updates, better maintainability
- Scope: Replaced `"memory/"`, `"core/"`, `"knowledge/"` literals with PATHS.MEMORY, PATHS.CORE, etc.

**Python Compatibility Fixes**
- Replace `datetime.UTC` with `timezone.utc` (Python 3.11+ → 3.9+)
- Fix f-string syntax errors (escaped quotes, nested expressions)
- Move PATHS imports to module level (avoid default argument scope issues)
- Fix 10 files: handlers (mission, workflow, shakedown, make, object, backup), services (performance_monitor, sync_engine), webhooks (api_server, event_processor, event_router), extensions (scenario_service)

**Git Cleanup**
- Remove all `.archive/` folders from git tracking (36 files)
- Universal `.archive/` gitignore patterns now active
- Folders remain locally for version history/backups

#### Fixed
- SHAKEDOWN validation: 125/130 tests passing (96.2%)
- All import scope errors resolved
- System boots successfully on Python 3.9-3.12

#### Dependencies
- Added: `cryptography`, `jsonschema`, `google-auth-oauthlib` (optional features)

---

## [1.2.10] - 2025-12-04

### v1.2.10 - VS Code Extension & Developer Tools (December 4, 2025)

**Strategic Release:** Complete .uPY language support, script execution, sandbox testing, knowledge quality checking, and image format validation to accelerate all future development.

#### Added

**VS Code Extension Foundation (1,783 lines across 8 files)**
- `extensions/vscode-udos/package.json` (150 lines) - Extension manifest
  - 6 commands: runScript, runInSandbox, checkKnowledgeQuality, previewSVG, previewASCII, validateTeletext
  - Language configuration for .upy files
  - 4 configuration properties (apiUrl, autoRunOnSave, sandboxAutoCleanup, showExecutionTime)
  - Activation events for .upy language
- `extensions/vscode-udos/syntaxes/upy.tmLanguage.json` (200 lines) - TextMate grammar
  - Syntax highlighting for 60+ commands grouped by category
  - Variable highlighting with property support ($MISSION.ID, $WORKFLOW.PHASE)
  - Directives: #BREAK, #DEBUG, #TRACE, #REGION, #ENDREGION
  - Keywords, strings, numbers, operators
- `extensions/vscode-udos/language-configuration.json` (50 lines) - Language rules
  - Brackets, auto-closing pairs, indentation for IF/FOREACH/WHILE
- `extensions/vscode-udos/src/extension.ts` (50 lines) - Main entry point
- `extensions/vscode-udos/src/providers/completion.ts` (250 lines) - IntelliSense provider
  - 60+ command completions with documentation
  - Context-aware property completion for $MISSION., $WORKFLOW., $CHECKPOINT., $GUIDE.
  - Real-world usage examples
- `extensions/vscode-udos/src/providers/hover.ts` (350 lines) - Hover documentation
  - Comprehensive command documentation with syntax and examples
  - Covers GUIDE, MAP, MISSION, WORKFLOW, CHECKPOINT, GENERATE, control flow, system commands
- `extensions/vscode-udos/src/snippets/upy.json` (200 lines) - Code snippets
  - 18 patterns: mission, workflow, loops, conditionals, error handling, etc.
- `extensions/vscode-udos/README.md` (400 lines) - Extension documentation
- `extensions/vscode-udos/tsconfig.json` (20 lines) - TypeScript configuration

**Script Executor & Debugger (500 lines)**
- `extensions/vscode-udos/src/commands/executor.ts` - Execution and sandbox testing
  - API integration: POST to http://localhost:5001/api/workflows/run
  - Debug panel webview with execution results, variables, errors
  - Sandbox testing environment with isolated instances
  - ExecutionResult interface (success, output, errors, variables, execution_time)
  - SandboxInstance tracking (id, port, workspace, created)
  - Auto-cleanup on panel close (configurable)
  - Beautiful dark-themed HTML panels (200+ lines CSS)
  - Error handling for API unavailability

**Knowledge Quality Checker (450 lines)**
- `extensions/vscode-udos/src/commands/knowledge-checker.ts` - Quality analysis
  - Scans 6 knowledge categories (water, fire, shelter, food, navigation, medical)
  - 6 quality validation types:
    1. Missing frontmatter (error)
    2. Outdated content >365 days (warning)
    3. Too short <300 words (warning)
    4. Broken links in relative paths (error)
    5. Missing examples/code blocks (info)
    6. No tags defined (info)
  - REGEN flagging for critical issues
  - Comprehensive HTML report webview with quality metrics
  - Optional batch REGEN script generation (knowledge-regen-batch.upy)
  - QualityReport interface with category distribution and metrics

**Image Format Validators (400 lines)**
- `extensions/vscode-udos/src/commands/image-validator.ts` - Visual content validation
  - SVG inspector: Validates dimensions, viewBox, element count, font sizes
  - ASCII art tester: Checks width consistency, non-ASCII characters, tabs vs spaces
  - Teletext validator: Verifies 24×40 format, color code counting
  - Preview webviews with dark-themed HTML panels
  - SVGReport, ASCIIReport, TeletextReport interfaces

#### Features

- **Full .uPY Language Support**: Syntax highlighting, IntelliSense, hover docs, snippets in VS Code
- **Script Execution**: Run .upy scripts directly from editor with debug output
- **Sandbox Testing**: Test scripts in isolated environments with auto-cleanup
- **Knowledge Quality Analysis**: Scan 228+ guides across 6 categories for quality issues
- **Image Validation**: Preview and validate SVG diagrams, ASCII art, teletext pages
- **Developer Productivity**: 10x faster workflow development with visual tools

#### Technical Details

- TypeScript 5.0+ with strict mode
- VS Code Extension API 1.80.0+
- TextMate grammar system for syntax highlighting
- Webview API for debug panels and reports
- Node.js fetch for API integration
- File system APIs for knowledge scanning

#### Metrics

- **Total Lines Delivered**: 3,133 lines (87% of 3,600 target)
- **Files Created**: 11 new files
- **Commands**: 6 VS Code commands
- **Quality Checks**: 6 validation types
- **Code Snippets**: 18 patterns
- **Commits**: 2 (8da33e6c, 9107fee1)

---

## [1.2.4] - 2025-12-04

### v1.2.4 - Developer Experience & Hot Reload (December 4, 2025)

**Fast Iteration:** Extension hot reload system, GitHub-centric feedback workflow, and enhanced developer documentation for rapid development cycles.

#### Added

**Extension Hot Reload System (621 lines across 2 files)**
- `core/services/extension_lifecycle.py` (467 lines) - Hot reload engine
  - `ExtensionLifecycleManager` class with state preservation
  - `ExtensionState` dataclass (session_vars, servers, commands, config, timestamp)
  - `ReloadResult` dataclass (success, message, modules_reloaded, commands_registered, errors, warnings)
  - 13 methods: reload_extension, reload_all_extensions, validate_before_reload, preserve_state, restore_state, rollback_reload, etc.
  - Module cache management via `importlib.reload()`
  - Dependency-aware reload ordering
  - Automatic rollback on import errors
  - Health checks post-reload
  - Reload history audit trail
- `core/commands/system_handler.py` (+154 lines) - REBOOT command enhancement
  - Flag parsing for `--extension`, `--extensions`, `--validate`
  - `_handle_hot_reload()` router method
  - `_format_reload_result()` formatter with emoji symbols
  - 4 REBOOT variants:
    * `REBOOT` - Full system restart (unchanged)
    * `REBOOT --extension <id>` - Reload single extension
    * `REBOOT --extensions` - Reload all extensions in dependency order
    * `REBOOT --validate` - Dry-run validation (no actual reload)
  - Output format with state preservation (💾), modules reloaded (🔄), commands registered (⚡), success (🚀)
  - Error handling with first 3 errors/warnings shown

**SHAKEDOWN Hot Reload Tests (184 lines)**
- `core/commands/shakedown_handler.py` - `_test_hot_reload()` test suite
  - 8 comprehensive tests:
    1. ExtensionLifecycleManager import and method presence
    2. Extension validation (manifest, dependencies)
    3. Validation dry-run (validate_only=True)
    4. State preservation mechanism
    5. Error handling (invalid extension ID)
    6. Extension path detection
    7. REBOOT command integration
    8. Batch reload capability
  - All tests passing (8/8)

**GitHub Browser Integration (499 lines across 4 files)**
- `core/commands/feedback_handler.py` (+190 lines) - GitHub feedback methods
  - `handle_github_feedback()` - Main GitHub integration
  - `_collect_system_info()` - Returns {version, os, python, mode}
  - `_generate_issue_url()` - Pre-filled bug/feature Issue URLs
  - `_generate_discussion_url()` - Pre-filled Discussion URLs
  - Minimal data collection: version (from setup.py), OS (platform.system), Python (sys.version_info), mode (interactive)
  - Opens browser automatically with `webbrowser.open()`
  - Privacy-first: No sensitive data, no user info, no API tokens
- `core/commands/user_handler.py` (+135 lines) - FEEDBACK command enhancement
  - Enhanced `_handle_feedback()` with flag parsing
  - New `_handle_github_feedback()` - GitHub workflow router
  - New `_feedback_help()` - Comprehensive help text
  - Flags: `--github`, `--open`, `--bug`, `--feature`, `--question`, `--idea`, `--issue`, `--discussion`, `--general`
  - Local JSONL fallback preserved (feedback.jsonl, bug_reports.jsonl)
- `core/uDOS_commands.py` (+4 lines) - FEEDBACK top-level command
  - Added FEEDBACK module routing (shortcut to USER handler)
  - Usage: `FEEDBACK --github --bug` instead of `USER FEEDBACK --github --bug`
- `core/commands/shakedown_handler.py` - `_test_github_feedback()` test suite
  - 8 comprehensive tests:
    1. FeedbackHandler import with GitHub methods
    2. System info collection (version, OS, Python)
    3. Bug report URL generation
    4. Feature request URL generation
    5. Discussion URL generation
    6. UserCommandHandler integration
    7. FEEDBACK command routing
    8. URL encoding validation
  - All tests passing (8/8)

**Command Prompt Mode Indicators (270 lines across 2 files)**
- `core/input/prompt_decorator.py` (+95 lines) - Visual mode enhancements
  - New `Colors` class with ANSI escape codes (16 colors: standard + bright variants)
  - Enhanced themes with color/symbol configurations:
    * dungeon: regular (› default), dev (🔧 DEV› yellow), assist (🤖 OK› cyan)
    * science: regular (⚗️› default), dev (🔧 LAB› yellow), assist (🤖 AI› cyan)
    * cyberpunk: regular (🔮› default), dev (🔧 SYS› yellow), assist (🤖 NET› cyan)
  - `get_prompt()` with mode priority (dev_mode > is_assist > regular)
  - `get_mode_status()` for status display (e.g., "🔧 DEV MODE" in yellow)
  - Optional color disable (use_colors=False)
- `core/commands/shakedown_handler.py` - `_test_prompt_modes()` test suite
  - 8 comprehensive tests:
    1. PromptDecorator with Colors class import
    2. Regular mode prompt (› symbol)
    3. DEV mode prompt (🔧 symbol, yellow)
    4. ASSIST mode prompt (🤖 symbol, cyan)
    5. Mode priority (DEV > ASSIST > REGULAR)
    6. Color disable flag
    7. `get_mode_status()` method
    8. Theme variants (dungeon, science, cyberpunk)
  - All tests passing (8/8)

**Developer Documentation (1,015 lines across 3 files)**
- `CONTRIBUTING.md` (+185 lines) - Enhanced contribution guide
  - Updated project overview with v1.2.4 features
  - Hot Reload Workflow section (development examples, best practices, when to use full restart)
  - GitHub Feedback Integration section (quick feedback commands, data collection transparency)
  - Enhanced Testing Guide (SHAKEDOWN coverage breakdown: 15+ subsystems, 100+ tests)
  - Developer Experience section (visual mode indicators, hot reload workflow, GitHub integration commands)
  - Development tips (5 tips for fast iteration: hot reload, DEV MODE, FEEDBACK, SHAKEDOWN, extension manager)
  - Updated resources section (new wiki links)
- `wiki/Hot-Reload.md` (450 lines) - Complete hot reload documentation
  - Overview and quick start
  - 5 key features: targeted reload, state preservation, rollback, validation, health checks
  - Architecture deep-dive: ExtensionLifecycleManager, REBOOT integration, data structures
  - Best practices: design for reloadability, resource management, testing strategies
  - When to use full restart vs hot reload
  - Troubleshooting: import errors, state loss, hanging reloads
  - Performance metrics: reload times (<1s), memory/CPU impact (minimal)
  - Testing: SHAKEDOWN coverage, integration tests
  - Changelog
- `wiki/GitHub-Feedback.md` (380 lines) - Complete GitHub feedback documentation
  - Overview and quick start
  - 4 key features: browser workflow, pre-filled templates, minimal data collection, user confirmation
  - Command syntax: types (bug, feature, question, idea), categories, flags
  - Examples: bug reports, feature requests, questions, ideas
  - Architecture: FeedbackHandler methods, UserCommandHandler integration, command routing
  - System information collection: implementation details, privacy guarantees
  - URL encoding: safe characters, examples, GitHub form schema
  - Testing: SHAKEDOWN coverage, manual testing steps
  - Troubleshooting: browser issues, URL length limits, wrong category
  - Changelog

#### Changed

**Testing Infrastructure**
- SHAKEDOWN test suite expanded to 24 v1.2.4 tests (hot reload, GitHub feedback, prompt modes)
- All tests passing (24/24 = 100% success rate)

#### Performance

- **Hot Reload Speed:** <1 second extension reload vs 3-10 second full restart (70-90% time savings)
- **Memory Impact:** Minimal (<5MB additional for state cache)
- **Developer Iteration:** 10x faster development cycle with hot reload + DEV MODE

#### Migration Notes

- FEEDBACK command now available as top-level shortcut (no breaking changes, USER FEEDBACK still works)
- REBOOT command extended with new flags (original `REBOOT` behavior unchanged)
- Prompt decorator backward compatible (existing themes automatically enhanced)

#### Commits

- fcb85650 - Archive v1.1.x changelog, keep only v1.2.x in main CHANGELOG
- 9460052d - v1.2.4 Part 1: Extension Hot Reload System
- b84c19c1 - v1.2.4 Part 2: GitHub Browser Integration for Feedback
- 289ffe6c - v1.2.4 Part 3: Command Prompt Mode Indicators
- 3929894c - v1.2.4 Part 4: Developer Documentation Complete

#### Total Delivery

- **Code:** 2,573 lines (5 modified files, 3 new files)
- **Documentation:** 1,015 lines (3 files)
- **Tests:** 24 comprehensive tests (100% passing)
- **Grand Total:** 3,588 lines delivered

---

## [1.2.3] - 2025-12-04

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
- **[v1.1.x Changelog](dev/archive/CHANGELOG-v1.1.x.md)** - Complete v1.1.0 through v1.1.18 history
- **v1.0.x and earlier** - Historical development builds (see archived changelog)

---

## Links

- [GitHub Repository](https://github.com/fredporter/uDOS)
- [Documentation Wiki](https://github.com/fredporter/uDOS/wiki)
- [Release Notes](https://github.com/fredporter/uDOS/releases)
- [Issue Tracker](https://github.com/fredporter/uDOS/issues)
