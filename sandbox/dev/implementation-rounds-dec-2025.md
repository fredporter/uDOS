# uDOS Development Rounds - December 2025

**Status**: Planning Phase
**Start Date**: December 1, 2025
**Target Completion**: January 2026

---

## Overview

Structured implementation of three major initiatives:
1. **uCODE → uPY → Python Refactor** (v1.1.9)
2. **Variable Definition System** (v1.1.9)
3. **Play Extension Alignment** (STORY + Gameplay)

Each round is independent, testable, and delivers production-ready features.

---

## 🎯 Round 1: Variable Definition System (3-5 days)

**Goal**: Define all system, user, and gameplay variables in JSON configuration files

### Tasks

#### 1.1 Create Variable Schema Files (Day 1)
- [ ] `core/data/variables/system.json` - System variables (VERSION, DATE, TIME, paths)
- [ ] `core/data/variables/user.json` - User profile variables (USERNAME, ROLE, PROJECT)
- [ ] `core/data/variables/sprite.json` - Character/sprite variables (HP, XP, level, stats)
- [ ] `core/data/variables/object.json` - Game object variables (items, equipment, resources)
- [ ] `core/data/variables/story.json` - Story/narrative variables (flags, state, progress)

**Schema Format**:
```json
{
  "version": "1.0.0",
  "category": "system|user|sprite|object|story",
  "variables": {
    "VARIABLE-NAME": {
      "type": "string|number|boolean|array|object",
      "format": "text|date|time|path|percentage|...",
      "default": "default value",
      "readonly": false,
      "description": "What this variable represents",
      "validation": {
        "min": 0,
        "max": 100,
        "pattern": "regex pattern",
        "required": true
      },
      "scope": "global|session|script|local",
      "callable": false
    }
  }
}
```

#### 1.2 Extend VariableManager (Day 2)
- [ ] Update `core/utils/variables.py` to load from JSON schemas
- [ ] Add validation based on schema definitions
- [ ] Support for SPRITE and OBJECT variable types
- [ ] Type coercion and format enforcement
- [ ] Scope management (global, session, script, local)

#### 1.3 SPRITE Variable System (Day 2-3)
- [ ] Character creation from schema
- [ ] HP/XP/Level calculations
- [ ] Stat modifiers (STR, DEX, CON, INT, WIS, CHA)
- [ ] Status effects tracking
- [ ] Equipment/inventory integration
- [ ] `$SPRITE-HP`, `$SPRITE-XP`, `$SPRITE-LEVEL` syntax

#### 1.4 OBJECT Variable System (Day 3)
- [ ] Item/object creation from schema
- [ ] Rarity/quality attributes
- [ ] Durability/condition tracking
- [ ] Stack/quantity support
- [ ] `$OBJECT-NAME`, `$OBJECT-QUANTITY` syntax

#### 1.5 Testing & Documentation (Day 4-5)
- [ ] Unit tests for VariableManager JSON loading
- [ ] Validation tests (type checking, constraints)
- [ ] SPRITE variable tests (HP/XP calculations)
- [ ] OBJECT variable tests (inventory operations)
- [ ] Update `wiki/uCODE-Language.md` with variable reference
- [ ] Create `wiki/Variable-System.md` comprehensive guide

**Success Criteria**:
- ✅ All 5 JSON schema files created
- ✅ VariableManager loads and validates from schemas
- ✅ SPRITE and OBJECT variables functional
- ✅ 95%+ test coverage
- ✅ Documentation complete

**Deliverables**:
- 5 JSON schema files in `core/data/variables/`
- Updated `core/utils/variables.py`
- Test suite in `sandbox/tests/test_variable_system.py`
- Wiki documentation

---

## 🎮 Round 2: Play Extension Alignment (4-6 days)

**Goal**: Integrate STORY command with .upy conditional adventures, sprite/object gameplay

### Tasks

#### 2.1 STORY Command Integration (Day 1)
- [ ] Create `extensions/play/commands/story_handler.py`
- [ ] Commands:
  - `STORY` - Show current story state
  - `STORY START <name>` - Begin adventure
  - `STORY SAVE <slot>` - Save game state
  - `STORY LOAD <slot>` - Load game state
  - `STORY RESET` - Clear story progress
- [ ] Story state management in `sandbox/user/story_state.json`
- [ ] Integration with existing scenario system

#### 2.2 .upy Adventure Scripts (Day 2-3)
- [ ] Create adventure template: `sandbox/workflow/templates/adventure_template.upy`
- [ ] Sample adventures:
  - `sandbox/workflow/adventures/water_quest.upy` - Find clean water
  - `sandbox/workflow/adventures/shelter_building.upy` - Construct shelter
  - `sandbox/workflow/adventures/fire_making.upy` - Start a fire
- [ ] IF/THEN/ELSE conditional logic in .upy format
- [ ] CHOICE mechanism for "choose your own adventure"
- [ ] Variable persistence across adventure steps

**Adventure Format**:
```python
#!/usr/bin/env python3
# water_quest.upy - Find Clean Water Adventure

# Initialize sprite
SET [$SPRITE-NAME = "Survivor"]
SET [$SPRITE-HP = 100]
SET [$SPRITE-WATER = 0]

# Story introduction
PRINT [=== WATER QUEST ===]
PRINT [You wake up in the wasteland. Your canteen is empty.]
PRINT [HP: $SPRITE-HP | Water: $SPRITE-WATER/5]

# First decision point
CHOICE [What do you do?]
  OPTION [Search nearby buildings] → BRANCH-BUILDINGS
  OPTION [Head to the river] → BRANCH-RIVER
  OPTION [Look for rainfall] → BRANCH-RAIN

# Branch: Buildings
LABEL [BRANCH-BUILDINGS]
PRINT [You search the abandoned buildings...]
ROLL [1d20] → $SEARCH-RESULT
IF [$SEARCH-RESULT > 15]
  PRINT [You find 2 bottles of water!]
  SET [$SPRITE-WATER = 2]
  XP [+50, reason="Found water supply"]
ELSE
  PRINT [Nothing but dust and debris.]
  DAMAGE [5, reason="Exhaustion"]
ENDIF

# Continue adventure...
```

#### 2.3 Sprite/Object Integration (Day 3-4)
- [ ] SPRITE creation command: `SPRITE CREATE <name> <class>`
- [ ] SPRITE status: `SPRITE STATUS` shows HP/XP/Level/Stats
- [ ] Damage/healing: `DAMAGE <amount>`, `HEAL <amount>`
- [ ] XP award integration: `XP [+amount, reason="action"]`
- [ ] OBJECT commands:
  - `OBJECT CREATE <name> <type>`
  - `OBJECT USE <name>` - Apply object effects
  - `OBJECT GIVE <name> <quantity>` - Add to inventory
  - `OBJECT TAKE <name> <quantity>` - Remove from inventory

#### 2.4 Map Layer Integration (Day 4-5)
- [ ] Update map_engine to use SPRITE position
- [ ] Map layers show OBJECT locations
- [ ] Movement affects SPRITE stats (exhaustion, etc.)
- [ ] Layer transitions (ASCEND/DESCEND) tied to story progress
- [ ] `MAP SPRITES` - Show all sprites on current layer
- [ ] `MAP OBJECTS` - Show all objects on current layer

#### 2.5 Testing & Examples (Day 5-6)
- [ ] Integration tests for STORY + SPRITE + OBJECT
- [ ] Adventure script validation
- [ ] CHOICE mechanism testing
- [ ] Create 3-5 complete adventure examples
- [ ] Update `extensions/play/README.md`
- [ ] Create `wiki/Adventure-Scripting.md` guide

**Success Criteria**:
- ✅ STORY command fully functional
- ✅ .upy adventures run with IF/THEN/CHOICE
- ✅ SPRITE variables track HP/XP correctly
- ✅ OBJECT variables work in inventory
- ✅ Map integration complete
- ✅ 3+ example adventures working

**Deliverables**:
- `extensions/play/commands/story_handler.py`
- 3-5 adventure scripts in `sandbox/workflow/adventures/`
- Adventure template
- Integration tests
- Wiki documentation

---

## 🔧 Round 3: uCODE → uPY → Python Refactor (5-7 days)

**Goal**: Python-first architecture with .upy user scripts, hyphenated command/variable naming

### Tasks

#### 3.1 Naming Convention Implementation (Day 1)
- [ ] Define naming rules in `core/data/naming_rules.json`:
  - Commands: `UPPERCASE-HYPHEN` (e.g., `SYSTEM-STATUS`, `FILE-INFO`)
  - Variables: `$UPPERCASE-HYPHEN` (e.g., `$CURRENT-PATH`, `$USER-NAME`)
  - Files/paths: unchanged (underscores OK)
  - Python internals: snake_case functions
- [ ] Update parser to handle hyphenated commands
- [ ] Variable substitution for hyphenated names

#### 3.2 Command Registry System (Day 1-2)
- [ ] Create `core/runtime/commands.py` - central registry
- [ ] Map all commands to handler functions
- [ ] Pure Python-compatible command dispatch
- [ ] No legacy format support (clean break)

**Registry Example**:
```python
COMMAND_REGISTRY = {
    "DASH": system.dash,
    "SYSTEM-STATUS": system.status,
    "FILE-INFO": files.file_info,
    "BANK-SEARCH": bank.bank_search,
    # ...
}
```

#### 3.3 .upy Preprocessor (Day 2-3)
- [ ] Create `core/interpreters/upy_preprocessor.py`
- [ ] Parse .upy files (Python + uCODE hybrid)
- [ ] Variable resolution: `$CURRENT-PATH` → `ctx["CURRENT-PATH"]`
- [ ] Command dispatch: `DASH` → `dispatch_command("DASH", args, ctx)`
- [ ] Pass-through for pure Python code
- [ ] Support for uCODE shorthand in .upy files

#### 3.4 Sample .upy Scripts (Day 3-4)
- [ ] `sandbox/ucode/system_status.upy` - System info demo
- [ ] `sandbox/ucode/file_ops_demo.upy` - File operations
- [ ] `sandbox/ucode/knowledge_demo.upy` - Knowledge/memory commands
- [ ] `sandbox/ucode/mixed_python_upy.upy` - Hybrid Python + uCODE
- [ ] Pure Python examples showing .upy as Python superset

#### 3.5 Command Handler Modules (Day 4-5)
- [ ] Restructure handlers under naming convention:
  - `core/commands/system.py` (not system_handler.py)
  - `core/commands/files.py` (not file_handler.py)
  - `core/commands/bank.py` (merged knowledge handlers)
- [ ] Update all function names to snake_case
- [ ] Command names remain UPPERCASE-HYPHEN in user-facing

#### 3.6 Shell Integration (Day 5-6)
- [ ] Create `bin/udos` launcher script
- [ ] Create `uenv.sh` environment helper
- [ ] Shell aliases: `udos`, `u` shorthand
- [ ] Python module entry: `python -m udos.cli`

#### 3.7 Testing & Python Compatibility (Day 6-7)
- [ ] Unit tests for upy_preprocessor
- [ ] Command registry tests
- [ ] .upy script execution tests
- [ ] Python compatibility tests (valid Python 3 syntax)
- [ ] Standard library integration tests (importable as module)
- [ ] Update all wiki documentation
- [ ] Create `COPILOT_BRIEF.md` in project root

**Success Criteria**:
- ✅ All commands use UPPERCASE-HYPHEN naming
- ✅ .upy scripts execute correctly
- ✅ Variable substitution works with hyphens
- ✅ Command registry functional
- ✅ Shell integration working
- ✅ Pure Python 3 compatibility (.upy files are valid Python)
- ✅ 95%+ test coverage

**Deliverables**:
- `core/runtime/commands.py`
- `core/interpreters/upy_preprocessor.py`
- 4+ sample .upy scripts (all valid Python)
- `bin/udos` and `uenv.sh`
- `COPILOT_BRIEF.md`
- Complete wiki updates
- Python module structure (`python -m udos`)

---

## 📅 Timeline Summary

| Round | Focus | Duration | Dependencies |
|-------|-------|----------|--------------|
| **Round 1** | Variable Definition System | 3-5 days | None (independent) |
| **Round 2** | Play Extension Alignment | 4-6 days | Round 1 (SPRITE/OBJECT vars) |
| **Round 3** | uCODE → uPY Refactor | 5-7 days | Round 1 (variable system) |

**Total Estimate**: 12-18 days
**Parallel Options**: Round 1 and Round 3 can run in parallel (different codebases)

---

## 🎯 Success Metrics

### Round 1 (Variables)
- [ ] 5 JSON schema files created
- [ ] VariableManager validates all types
- [ ] SPRITE HP/XP calculations working
- [ ] OBJECT inventory operations working
- [ ] 30+ unit tests passing

### Round 2 (Play Extension)
- [ ] STORY command functional
- [ ] 3+ adventure scripts working
- [ ] SPRITE/OBJECT integration complete
- [ ] Map layer integration done
- [ ] 25+ integration tests passing

### Round 3 (uPY Refactor)
- [ ] All commands use hyphenated names
- [ ] .upy preprocessor functional
- [ ] Command registry complete
- [ ] 4+ sample .upy scripts (all valid Python)
- [ ] Shell integration working
- [ ] Python 3 compatibility verified
- [ ] 40+ tests passing (includes Python stdlib integration)

---

## 🚀 Quick Start

### Option A: Sequential (Recommended)
```bash
# Week 1: Variable System
./start_round.sh 1

# Week 2: Play Extension
./start_round.sh 2

# Week 3: uPY Refactor
./start_round.sh 3
```

### Option B: Parallel (Advanced)
```bash
# Start Round 1 and Round 3 simultaneously
./start_round.sh 1 &
./start_round.sh 3 &
wait

# Then Round 2 (depends on Round 1)
./start_round.sh 2
```

---

## 📋 Pre-Round Checklist

Before starting each round:
- [ ] Create feature branch: `git checkout -b round-X-feature-name`
- [ ] Review round objectives and tasks
- [ ] Check dependencies (prior rounds complete?)
- [ ] Allocate time blocks (uninterrupted work)
- [ ] Prepare test environment
- [ ] Clear `sandbox/trash/` and `sandbox/logs/`

---

## 📝 Post-Round Checklist

After completing each round:
- [ ] All tasks marked complete
- [ ] Test suite passing (95%+ coverage)
- [ ] Documentation updated
- [ ] Examples/demos working
- [ ] Git commit with detailed message
- [ ] Merge to main: `git merge round-X-feature-name`
- [ ] Tag release: `git tag vX.X.X`
- [ ] Update `CHANGELOG.md`
- [ ] Update roadmap status
- [ ] Clear technical debt items

---

## 🐛 Known Risks & Mitigation

### Round 1 Risks
- **Risk**: Variable schema complexity grows out of control
  **Mitigation**: Start minimal, expand incrementally with real use cases

- **Risk**: Type validation too strict, breaks existing code
  **Mitigation**: Gradual migration, deprecation warnings, not hard errors

### Round 2 Risks
- **Risk**: Adventure script syntax becomes too complex
  **Mitigation**: Keep it Python-friendly, .upy is Python + shortcuts

- **Risk**: STORY state conflicts with scenario system
  **Mitigation**: Unified state management, single source of truth

### Round 3 Risks
- **Risk**: Breaking changes require user script updates
  **Mitigation**: Clear migration guide, example conversions in wiki

- **Risk**: .upy preprocessor performance issues
  **Mitigation**: Keep preprocessing minimal, leverage Python's ast module

- **Risk**: Python compatibility issues with uCODE syntax
  **Mitigation**: Design .upy as valid Python first, add shortcuts second

---

## 🔗 Related Documents

- [POKE WEB Roadmap](poke-web-roadmap-2025-12-01.md) - Cloud sharing (v2.1+)
- [Mission Control Styling](mission-control-nes-styling-2025-12-01.md) - Dashboard integration
- [Roadmap](roadmap/ROADMAP.MD) - Full version history and plans

---

**Status**: 📋 Planning Complete - Ready for Round 1
**Last Updated**: December 1, 2025
**Next Action**: Begin Round 1 - Variable Definition System
