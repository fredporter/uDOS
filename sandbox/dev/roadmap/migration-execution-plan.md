# Migration Execution Plan - Old → New uPY Format

**Created:** 2024-12-02
**Status:** In Progress

## Phase 1: Integration ✅ COMPLETE
- ✅ Command registry (core/runtime/commands.py)
- ✅ UPY preprocessor (core/runtime/upy_preprocessor.py)
- ✅ UPY parser (core/runtime/upy_parser.py)
- ✅ Shell integration (bin/udos, bin/uenv.sh)

## Phase 2: Main System Integration (NOW)

### 2.1 Update uDOS_main.py
- [ ] Import new UPYParser
- [ ] Route .upy files to UPYParser instead of old interpreter
- [ ] Keep backward compatibility for .uscript (deprecated)

### 2.2 Update Command Handler
- [ ] Integrate command registry
- [ ] Support new COMMAND(args) format
- [ ] Deprecate [MODULE|COMMAND*ARGS] format

### 2.3 File Migration
- [ ] Convert sandbox/ucode/*.upy to new format
- [ ] Create converted/ directory for migrated files
- [ ] Archive old format files in sandbox/backup/

## Phase 3: Clean Old Code

### 3.1 Remove Old Scripts (sandbox/)
Files using old format:
- `sandbox/ucode/rpg_demo_v1.1.9.upy` (197 lines) - OLD FORMAT
- `sandbox/ucode/demo_adventure.upy` (137 lines) - OLD FORMAT
- `sandbox/ucode/shakedown.upy` (733 lines) - OLD FORMAT
- `sandbox/ucode/simple_demo.upy` - OLD FORMAT
- `sandbox/ucode/test-story.upy` - OLD FORMAT

Action: Migrate → sandbox/ucode/migrated/ or delete if obsolete

### 3.2 Remove Old Interpreters
- [ ] Review core/interpreters/ucode.py (old .uscript interpreter)
- [ ] Mark as deprecated
- [ ] Keep for backward compatibility until v3.0.0

### 3.3 Update Templates
- `core/data/templates/*.uscript` - Convert to .upy with new format
- `core/data/templates/adventure.template.upy` - Update to new syntax

## Phase 4: Testing

### 4.1 Create New Examples
- [ ] water-quest.upy (NEW FORMAT) ✅ DONE
- [ ] rpg-demo-new.upy (NEW FORMAT)
- [ ] shakedown-new.upy (NEW FORMAT)

### 4.2 Integration Tests
- [ ] Test .upy loading in main system
- [ ] Test command execution
- [ ] Test backward compatibility (.uscript)

### 4.3 End-to-End Tests
- [ ] Run full shakedown test
- [ ] Verify all commands work
- [ ] Check error handling

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
- Phase 2: Main system integration (1-2 hours)
- Phase 3: Clean old code (30 min)
- Phase 4: Testing (30 min)

**Total:** ~3 hours

## Success Criteria

✅ New .upy files load with UPYParser
✅ COMMAND(args) syntax works in main system
✅ Old .uscript files still work (deprecated)
✅ All tests passing
✅ Old format files archived
✅ Documentation updated

---

**Current Focus:** Phase 2.1 - Update uDOS_main.py
