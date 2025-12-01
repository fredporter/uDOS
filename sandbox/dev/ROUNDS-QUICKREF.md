# uDOS Development Rounds - Quick Reference

## 🚀 Quick Start Commands

```bash
# Start a development round
./start_round.sh <1|2|3>

# Complete a round
./complete_round.sh <1|2|3>

# Check progress
cat sandbox/dev/round-<N>-progress.md

# Run tests
pytest sandbox/tests/ -v
```

---

## 📋 Round Overview

| # | Name | Duration | Files | Tests | Status |
|---|------|----------|-------|-------|--------|
| **1** | Variable Definition System | 3-5 days | 5 JSON + 1 Python | 30+ | 📋 Planned |
| **2** | Play Extension Alignment | 4-6 days | 10+ files | 25+ | 📋 Planned |
| **3** | uCODE → uPY Refactor | 5-7 days | 15+ files | 40+ | 📋 Planned |

**Total**: 12-18 days | 30+ files | 95+ tests | Version 1.1.9

---

## 🎯 Round 1: Variable Definition System

**Goal**: JSON-defined system, user, sprite, object, and story variables

### Key Deliverables
- `core/data/variables/system.json` - System vars (VERSION, DATE, paths)
- `core/data/variables/user.json` - User profile (USERNAME, ROLE)
- `core/data/variables/sprite.json` - Character stats (HP, XP, level)
- `core/data/variables/object.json` - Game objects (items, equipment)
- `core/data/variables/story.json` - Story state (flags, progress)

### Commands
```bash
./start_round.sh 1
# ... develop ...
pytest sandbox/tests/test_variable_system.py -v
./complete_round.sh 1
```

### Success Criteria
✅ All 5 schemas created
✅ VariableManager validates types
✅ SPRITE variables work (HP/XP)
✅ OBJECT variables work (inventory)
✅ 30+ tests passing

---

## 🎮 Round 2: Play Extension Alignment

**Goal**: STORY command + .upy adventures + SPRITE/OBJECT gameplay

### Key Deliverables
- `extensions/play/commands/story_handler.py` - Story management
- `sandbox/workflow/adventures/water_quest.upy` - Sample adventure
- `sandbox/workflow/adventures/shelter_building.upy` - Sample adventure
- `sandbox/workflow/adventures/fire_making.upy` - Sample adventure
- `sandbox/workflow/templates/adventure_template.upy` - Template

### Commands
```bash
./start_round.sh 2

# Test adventure
uDOS> STORY START water_quest
uDOS> SPRITE STATUS
uDOS> MAP SPRITES

./complete_round.sh 2
```

### Adventure Script Format
```python
#!/usr/bin/env python3
# adventure_name.upy

SET [$SPRITE-NAME = "Survivor"]
SET [$SPRITE-HP = 100]

PRINT [=== ADVENTURE TITLE ===]

CHOICE [What do you do?]
  OPTION [Choice A] → LABEL-A
  OPTION [Choice B] → LABEL-B

LABEL [LABEL-A]
PRINT [You chose A...]
IF [$SPRITE-HP < 50]
  DAMAGE [10]
ENDIF
```

### Success Criteria
✅ STORY command works
✅ 3+ adventures run
✅ SPRITE/OBJECT integration
✅ Map integration
✅ 25+ tests passing

---

## 🔧 Round 3: uCODE → uPY Refactor

**Goal**: Python-first architecture with hyphenated naming

### Key Deliverables
- `core/data/naming_rules.json` - Naming convention definitions
- `core/runtime/commands.py` - Central command registry
- `core/interpreters/upy_preprocessor.py` - .upy parser
- `bin/udos` - Shell launcher
- `uenv.sh` - Environment helper
- `COPILOT_BRIEF.md` - AI assistant guide

### Naming Conventions
```python
# Commands: UPPERCASE-HYPHEN
SYSTEM-STATUS  # ✅ New format
FILE-INFO      # ✅ New format
BANK-SEARCH    # ✅ New format

# Variables: $UPPERCASE-HYPHEN
$CURRENT-PATH  # ✅ New format
$USER-NAME     # ✅ New format
$SPRITE-HP     # ✅ New format

# Python internals: snake_case
def handle_system_status():  # ✅ Function name
    current_path = ...       # ✅ Variable name
```

### Commands
```bash
./start_round.sh 3

# Test .upy scripts
./bin/udos sandbox/ucode/system_status.upy

# Source environment
source uenv.sh
u  # Shorthand for udos

./complete_round.sh 3
```

### Success Criteria
✅ All commands hyphenated
✅ .upy preprocessor works
✅ Command registry complete
✅ 4+ sample .upy scripts (all valid Python 3)
✅ Shell integration
✅ Python 3 compatibility verified
✅ 40+ tests passing (including Python stdlib integration)

---

## 📊 Progress Tracking

### During Round
```bash
# Update tasks
vim sandbox/dev/round-<N>-progress.md

# Mark task complete
- [x] 1.1 Create Variable Schema Files  # ✅ Done

# Add session notes
### 2025-12-02
- Created system.json schema
- Implemented type validation
- Fixed edge case in array parsing
```

### After Round
```bash
# Archive progress
./complete_round.sh <N>
# → Creates: sandbox/dev/archive/round-<N>-progress-YYYYMMDD.md
```

---

## 🧪 Testing Strategy

### Unit Tests
```bash
# Round 1
pytest sandbox/tests/test_variable_system.py -v

# Round 2
pytest sandbox/tests/test_story_handler.py -v
pytest sandbox/tests/test_sprite_variables.py -v

# Round 3
pytest sandbox/tests/test_upy_preprocessor.py -v
pytest sandbox/tests/test_command_registry.py -v
```

### Integration Tests
```bash
# Full suite
pytest sandbox/tests/ -v --cov=core --cov=extensions

# Specific round
pytest sandbox/tests/ -v -k "round_1"
```

### Manual Tests
```bash
# Round 1: Variable validation
uDOS> SET [$SPRITE-HP = 100]
uDOS> GET [$SPRITE-HP]
# Output: 100

# Round 2: Adventure gameplay
uDOS> STORY START water_quest
uDOS> CHOICE 1
uDOS> SPRITE STATUS

# Round 3: .upy execution
./bin/udos sandbox/ucode/demo.upy
```

---

## 🐛 Troubleshooting

### Round Won't Start
```bash
# Uncommitted changes?
git status
git stash push -m "stash for round N"

# Wrong branch?
git checkout main
./start_round.sh <N>
```

### Tests Failing
```bash
# Verbose output
pytest sandbox/tests/ -vv --tb=long

# Single test
pytest sandbox/tests/test_file.py::test_function -v

# Debug mode
pytest sandbox/tests/ --pdb
```

### Round Won't Complete
```bash
# Check criteria
cat sandbox/dev/implementation-rounds-dec-2025.md

# Review progress
cat sandbox/dev/round-<N>-progress.md

# Fix issues, then retry
./complete_round.sh <N>
```

---

## 📚 Documentation Updates

### Per Round
1. Update wiki pages relevant to round
2. Add examples to `wiki/` directory
3. Update `CHANGELOG.md` (automated by complete script)
4. Update `README.md` if major features

### After All Rounds
1. Complete `wiki/Variable-System.md`
2. Complete `wiki/Adventure-Scripting.md`
3. Complete `wiki/uPY-Language.md`
4. Update `wiki/Command-Reference.md` with hyphenated names
5. Create `COPILOT_BRIEF.md` in project root

---

## 🎯 Dependencies Graph

```
Round 1 (Variables)
    ↓ (SPRITE/OBJECT schemas)
Round 2 (Play Extension)

Round 3 (uPY Refactor)
    ↑ (Variable system)
Round 1 (Variables)
```

**Parallel Option**: Run Round 1 + Round 3 simultaneously (different codebases)

---

## 🔗 Resources

- **Main Plan**: `sandbox/dev/implementation-rounds-dec-2025.md`
- **Roadmap**: `sandbox/dev/roadmap/ROADMAP.MD`
- **Progress**: `sandbox/dev/round-<N>-progress.md`
- **Archive**: `sandbox/dev/archive/`
- **Scripts**: `./start_round.sh`, `./complete_round.sh`

---

**Version**: 1.0
**Last Updated**: December 1, 2025
**Status**: Ready for Round 1
