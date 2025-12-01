# Round 3: uCODE → uPY Refactor - Progress Tracker

**Started:** December 2, 2025
**Target Completion:** December 9, 2025 (7 days)
**Status:** 🚧 IN PROGRESS

## Overview

Python-first architecture with UPPERCASE-HYPHEN naming conventions throughout the entire system.

## Phase 1: Foundation (Day 1-2) ✅ COMPLETE

### Command Registry System
- [x] Create `core/runtime/` directory
- [x] Create `core/runtime/commands.py` - Central command registry (370 lines)
- [x] Create `core/runtime/registry.py` - Registration decorators (included in commands.py)
- [x] Define command metadata structure (CommandMetadata dataclass)
- [x] Implement command discovery system (list, search, filter)
- [x] Add validation for UPPERCASE-HYPHEN naming (strict regex validation)

### .upy Preprocessor
- [x] Create `core/runtime/upy_preprocessor.py` (276 lines)
- [x] Python 3 AST parsing for .upy files
- [x] Variable expansion ($SPRITE-HP → runtime value)
- [x] Command translation layer (validate UPPERCASE-HYPHEN)
- [x] Validation that .upy files are valid Python 3
- [x] Error reporting with line numbers (UPYSyntaxError)

### Shell Integration
- [x] Create `bin/udos` - Shell launcher script (170 lines)
- [x] Create `bin/uenv.sh` - Environment setup (140 lines)
- [x] Add PATH integration
- [x] Support for `udos script.upy` execution
- [x] Support for `udos --interactive` mode
- [x] Environment variable management (UDOS_HOME, UDOS_CONFIG, UDOS_THEME)

**Success Criteria:**
- [x] Command registry can discover and validate commands
- [x] .upy files parse as valid Python 3
- [x] Shell launcher works from any directory
- [x] 35+ tests passing for foundation (15 registry + 20 preprocessor)

**Phase 1 Results:**
- ✅ 35/35 tests passing (0.05s)
- ✅ Command registry fully functional
- ✅ .upy preprocessor with variable expansion
- ✅ Shell integration complete
- ✅ All validation working
- ✅ Files created: 7 (3 core + 2 tests + 2 shell scripts)

## Phase 2: Command Migration (Day 3-4)

### Core Commands → UPPERCASE-HYPHEN
- [ ] `STATUS` → `SYSTEM-STATUS`
- [ ] `HELP` → `SYSTEM-HELP`
- [ ] `CLEAR` → `DISPLAY-CLEAR`
- [ ] `EXIT` → `SYSTEM-EXIT`
- [ ] `VERSION` → `SYSTEM-VERSION`
- [ ] `CONFIG` → `SYSTEM-CONFIG`
- [ ] `THEME` → `DISPLAY-THEME`
- [ ] `LOG` → `SYSTEM-LOG`
- [ ] `SAVE` → `FILE-SAVE`
- [ ] `LOAD` → `FILE-LOAD`
- [ ] `LIST` → `FILE-LIST`
- [ ] `INFO` → `FILE-INFO`
- [ ] `SEARCH` → `KNOWLEDGE-SEARCH`
- [ ] `READ` → `KNOWLEDGE-READ`
- [ ] `GUIDE` → `KNOWLEDGE-GUIDE`

### Extension Commands
- [ ] `EXTENSION` → `EXTENSION-MANAGER`
- [ ] `GENERATE` → `CONTENT-GENERATE`
- [ ] `SVG` → `GRAPHICS-SVG`
- [ ] `TELETEXT` → `GRAPHICS-TELETEXT`
- [ ] `MAP` → `NAVIGATION-MAP`
- [ ] `GRID` → `NAVIGATION-GRID`
- [ ] `LOCATION` → `NAVIGATION-LOCATION`
- [ ] `STORY` → `ADVENTURE-STORY`
- [ ] `SCENARIO` → `ADVENTURE-SCENARIO`
- [ ] `XP` → `GAME-XP`
- [ ] `INVENTORY` → `GAME-INVENTORY`

### Legacy Cleanup
- [ ] Remove old .uscript parser
- [ ] Remove legacy command handlers
- [ ] Clean up sandbox/scripts/ (if any old .uscript files)
- [ ] Remove deprecated variable syntax handling
- [ ] Clean up old test files referencing legacy syntax

**Success Criteria:**
- [ ] All commands use UPPERCASE-HYPHEN
- [ ] No legacy command handlers remain
- [ ] Command aliases work (e.g., STATUS still maps to SYSTEM-STATUS)
- [ ] 20+ tests passing for commands

## Phase 3: Variable System Migration (Day 5)

### Variable Naming → $UPPERCASE-HYPHEN
- [ ] `$HP` → `$SPRITE-HP`
- [ ] `$HP_MAX` → `$SPRITE-HP-MAX`
- [ ] `$XP` → `$SPRITE-XP`
- [ ] `$LEVEL` → `$SPRITE-LEVEL`
- [ ] `$NAME` → `$SPRITE-NAME`
- [ ] `$GOLD` → `$SPRITE-GOLD`
- [ ] `$INVENTORY` → `$SPRITE-INVENTORY`
- [ ] `$LOCATION` → `$SPRITE-LOCATION`
- [ ] All STORY-* variables
- [ ] All SYSTEM-* variables
- [ ] All SESSION-* variables

### Variable Manager Updates
- [ ] Update `core/utils/variables.py` for HYPHEN naming
- [ ] Update JSON schemas in `core/data/variables/`
- [ ] Add validation for UPPERCASE-HYPHEN variable names
- [ ] Update template files with new variable syntax
- [ ] Migrate adventure.template.upy to new syntax

**Success Criteria:**
- [ ] All variables use UPPERCASE-HYPHEN
- [ ] Variable validation rejects underscores
- [ ] Templates updated
- [ ] 10+ tests passing for variables

## Phase 4: .upy Examples & Documentation (Day 6)

### Sample .upy Scripts (Valid Python 3)
- [ ] `memory/ucode/examples/water-quest.upy` - Water survival adventure
- [ ] `memory/ucode/examples/shelter-quest.upy` - Shelter building adventure
- [ ] `memory/ucode/examples/fire-quest.upy` - Fire making adventure
- [ ] `memory/ucode/examples/navigation-quest.upy` - Navigation training
- [ ] All scripts must be valid Python 3 (can run with `python3 script.upy`)

### Documentation
- [ ] `wiki/uPY-Language-Reference.md` - Complete .upy language guide
- [ ] `wiki/Command-Registry.md` - Command system documentation
- [ ] `wiki/Migration-Guide-v2.0.0.md` - Migration from v1.x
- [ ] `COPILOT_BRIEF.md` - AI assistant integration guide
- [ ] Update `wiki/Command-Reference.md` with HYPHEN names

### Legacy Cleanup
- [ ] Remove old .uscript documentation
- [ ] Update all wiki references to new command names
- [ ] Clean up old example scripts
- [ ] Remove deprecated syntax from guides

**Success Criteria:**
- [ ] 4+ .upy examples work as Python 3 scripts
- [ ] 3+ wiki pages created/updated
- [ ] COPILOT_BRIEF.md complete
- [ ] Migration guide comprehensive

## Phase 5: Testing & Polish (Day 7)

### Test Suite
- [ ] 40+ tests total across all systems
- [ ] Command registry tests (10+)
- [ ] .upy preprocessor tests (10+)
- [ ] Shell integration tests (5+)
- [ ] Variable system tests (10+)
- [ ] End-to-end integration tests (5+)
- [ ] All tests passing < 1s execution time

### Production Readiness
- [ ] Full regression test
- [ ] Performance benchmarks
- [ ] Error handling comprehensive
- [ ] Documentation complete
- [ ] CHANGELOG.md updated
- [ ] Git tag v2.0.0

**Success Criteria:**
- [ ] 40+ tests passing
- [ ] < 1s test execution
- [ ] Zero known bugs
- [ ] All documentation complete
- [ ] Production ready

## Cleanup Checklist

### Files to Remove
- [ ] `core/interpreters/ucode_interpreter.py` (if legacy)
- [ ] Old .uscript parser code
- [ ] `sandbox/scripts/*.uscript` (if any exist)
- [ ] Legacy command handler files
- [ ] Old test files for deprecated syntax

### Code to Clean
- [ ] Remove underscore variable support
- [ ] Remove old command name mappings
- [ ] Clean up backward compatibility shims
- [ ] Remove deprecated configuration keys
- [ ] Clean up old import statements

## Daily Progress Log

### Day 1 (December 2, 2025)
**Focus:** Foundation setup ✅ COMPLETE
- Created progress tracker ✅
- Implemented command registry system (370 lines) ✅
- Implemented .upy preprocessor (276 lines) ✅
- Created shell integration (bin/udos, bin/uenv.sh) ✅
- Created comprehensive tests (35 tests) ✅
- **Tests:** 35/35 passing in 0.05s ✅
- **Time:** ~2 hours (faster than 2-day estimate!)
- **Next:** Phase 2 - Command Migration

### Day 2
**Focus:**

### Day 3
**Focus:**

### Day 4
**Focus:**

### Day 5
**Focus:**

### Day 6
**Focus:**

### Day 7
**Focus:**

## Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Tests Created** | 40+ | 35 | ✅ 88% |
| **Commands Migrated** | 25+ | 0 | ⏳ Next |
| **Variables Migrated** | 20+ | 0 | ⏳ Next |
| **Wiki Pages** | 3+ | 0 | ⏳ Later |
| **Sample Scripts** | 4+ | 1 | ⏳ Later |
| **Legacy Files Removed** | 10+ | 0 | ⏳ Next |

## Notes

**Breaking Changes:**
- Old .uscript format no longer supported
- All commands require UPPERCASE-HYPHEN naming
- All variables require $UPPERCASE-HYPHEN syntax
- Shell launcher required for .upy execution

**Migration Path:**
- Users must convert scripts manually using migration guide
- Command aliases provided for common commands (temporary)
- Clear error messages for old syntax usage

## Blockers

None currently.

## Next Actions

1. Create `core/runtime/` directory structure
2. Implement command registry system
3. Create .upy preprocessor
4. Build shell integration
