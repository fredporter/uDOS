# Migration Execution Plan - Old → New uPY Format

**Created:** 2024-12-02
**Status:** In Progress

## Phase 1: Integration ✅ COMPLETE
- ✅ Command registry (core/runtime/commands.py)
- ✅ UPY preprocessor (core/runtime/upy_preprocessor.py)
- ✅ UPY parser (core/runtime/upy_parser.py)
- ✅ Shell integration (bin/udos, bin/uenv.sh)

## Phase 2: Main System Integration ✅ COMPLETE

### 2.1 Update uDOS_main.py ✅
- ✅ Import new UPYParser
- ✅ Route .upy files to UPYParser instead of old interpreter
- ✅ Keep backward compatibility for .uscript (deprecated)
- ✅ Added execute() method to UPYParser

### 2.2 Update Command Handler (DEFERRED)
- ⏸️  Integrate command registry (Phase 4)
- ⏸️  Support new COMMAND(args) format (Phase 4)
- ⏸️  Deprecate [MODULE|COMMAND*ARGS] format (Phase 4)

### 2.3 File Migration ✅
- ✅ Convert sandbox/ucode/*.upy to new format
- ✅ Create bin/migrate_upy.py (246 lines)
- ✅ Archive old format files in sandbox/backup/old-upy-format-20241202/

## Phase 3: Clean Old Code ✅ COMPLETE

### 3.1 Remove Old Scripts (sandbox/) ✅
Files using old format:
- ✅ `sandbox/ucode/rpg_demo_v1.1.9.upy` → ARCHIVED
- ✅ `sandbox/ucode/demo_adventure.upy` → ARCHIVED
- ✅ `sandbox/ucode/shakedown.upy` → ARCHIVED
- ✅ `sandbox/ucode/simple_demo.upy` → ARCHIVED
- ✅ `sandbox/ucode/test-story.upy` → ARCHIVED

### 3.2 Remove Old Interpreters ✅
- ✅ Deprecated core/interpreters/ucode.py (old .uscript interpreter)
- ✅ Renamed core/interpreters/upy_preprocessor.py → .deprecated.py
- ✅ Added deprecation warnings
- ✅ Keep for backward compatibility until v3.0.0

### 3.3 Update Templates (NEXT)
- [ ] `core/data/templates/*.uscript` - Convert to .upy with new format
- [ ] `core/data/templates/adventure.template.upy` - Update to new syntax

## Phase 4: Testing ✅ COMPLETE

### 4.1 Create New Examples ✅
- ✅ water-quest.upy (NEW FORMAT) - Round 3
- ✅ hello-world.upy (NEW FORMAT) - Simple intro
- ✅ rpg-combat.upy (NEW FORMAT) - Combat mechanics
- ✅ shakedown.upy (NEW FORMAT) - System validation

### 4.2 Integration Tests ✅
- ✅ Test .upy loading in main system
- ✅ Test command execution
- ✅ Test backward compatibility (.uscript)
- ✅ 64/64 tests passing (0.06s)

### 4.3 End-to-End Tests (DEFERRED)
- ⏸️  Run full shakedown test (needs command integration)
- ⏸️  Verify all commands work (needs command integration)
- ⏸️  Check error handling (needs command integration)

## Phase 5: Documentation

### 5.1 Update Wiki
- [ ] Command-Reference.md (new syntax)
- [ ] uCODE-Language.md (deprecate old format)
- [ ] Migration-Guide-v2.0.0.md (create)

### 5.2 Update Core Docs
- [ ] core/docs/ (if any uPY references)
- [ ] README.md (update examples)

## Execution Timeline

**Today (Dec 2):**
- ✅ Phase 2: Main system integration (1 hour)
- ✅ Phase 3: Clean old code (30 min)
- ✅ Phase 4: Testing (30 min)
- ✅ New examples created (30 min)

**Total:** ~2.5 hours

**Deferred to Phase 5 (Command Integration):**
- Command registry integration into main loop
- Full end-to-end testing with commands
- Documentation updates

## Success Criteria

✅ New .upy files load with UPYParser  
✅ COMMAND(args) syntax works in parser  
✅ Old .uscript files still work (deprecated)  
✅ All tests passing (64/64)  
✅ Old format files archived  
✅ New example files created  
⏸️  Documentation updated (Phase 5)  

---

**Current Status:** Migration Phase 2-4 COMPLETE

**Commits:** 2
1. Migration: Integrate new uPY parser and clean old code (e477c3d6)
2. [Pending] Migration: New example files

**Files Created:**
- bin/migrate_upy.py (246 lines)
- memory/ucode/examples/hello-world.upy (28 lines)
- memory/ucode/examples/rpg-combat.upy (137 lines)
- memory/ucode/examples/shakedown.upy (141 lines)

**Files Archived:**
- sandbox/backup/old-upy-format-20241202/ (5 files, 1,067+ lines)

**Files Deprecated:**
- core/interpreters/ucode.py (2,230 lines - backward compat)
- core/interpreters/upy_preprocessor.deprecated.py (937 lines - old format)

**Next:** Commit new examples, then Phase 5 (Documentation)
