# Development Round: v1.1.1 - uCODE Modernization

**Started:** 27 November 2025
**Status:** 🚀 ACTIVE
**Progress:** 4/38 steps (10.5%)

---

## Mission Overview

**Objective:** Modernize uCODE syntax with minimal, clean commands while maintaining backward compatibility.

**Key Changes:**
- `ECHO` → `PRINT` (with deprecation warnings)
- `ENDIF/ENDFOR/ENDWHILE/ENDFUNCTION` → curly braces `{}`
- Enable one-line command syntax
- Both old and new syntax work simultaneously

**Complexity:** Medium (38 steps across 4 moves)
**Dependencies:** None
**Location:** `core/interpreters/ucode.py` (primary), templates, docs

---

## Move 1: Core Syntax (12 steps) - IN PROGRESS

### Steps

- [x] 1. Add `PRINT` command handler to `core/interpreters/ucode.py`
- [x] 2. Implement template string support: `PRINT "Value: ${var}"`
- [x] 3. Add deprecation warnings for `ECHO` usage
- [x] 4. Create curly brace parser for blocks: `IF (condition) { }`
- [ ] 5. Extend `_handle_if_block()` for both syntaxes
- [ ] 6. Extend `_handle_for_loop()` for both syntaxes
- [ ] 7. Extend `_handle_while_loop()` for both syntaxes
- [ ] 8. Extend `_handle_function_definition()` for both syntaxes
- [ ] 9. Extend `_handle_try_block()` for both syntaxes
- [ ] 10. Add one-line command support
- [ ] 11. Test backward compatibility (old syntax still works)
- [ ] 12. Update error messages for new syntax

**Status:** 🔨 Step 4/12 complete
**Estimated Complexity:** Mix of simple and medium steps---

## Move 2: Migration Tools (8 steps) - NOT STARTED

### Steps

- [ ] 13. Create `ucode-migrate` command
- [ ] 14. Build AST analyzer for old syntax detection
- [ ] 15. Implement auto-conversion: `ECHO` → `PRINT`
- [ ] 16. Implement auto-conversion: `ENDIF` → `}`
- [ ] 17. Implement auto-conversion: `IF/THEN` → `IF (condition)`
- [ ] 18. Add dry-run mode for migration preview
- [ ] 19. Add backup creation before migration
- [ ] 20. Test migration on template files

**Status:** ⏸️ Blocked by Move 1
**Estimated Complexity:** Medium steps (requires AST knowledge)

---

## Move 3: Templates & Docs (10 steps) - NOT STARTED

### Steps

- [ ] 21. Update `core/data/templates/menu_system.uscript`
- [ ] 22. Update `core/data/templates/*.uscript` (all templates)
- [ ] 23. Update `sandbox/workflow/templates/*.uscript`
- [ ] 24. Update example scripts in `sandbox/ucode/`
- [ ] 25. Update wiki page: `uCODE-Language.md`
- [ ] 26. Create migration guide document
- [ ] 27. Add syntax comparison examples
- [ ] 28. Document both syntaxes (modern + traditional)
- [ ] 29. Update inline code comments
- [ ] 30. Create syntax quick reference card

**Status:** ⏸️ Blocked by Move 1 & 2
**Estimated Complexity:** Simple steps (file editing)

---

## Move 4: Testing & Polish (8 steps) - NOT STARTED

### Steps

- [ ] 31. Write unit tests for PRINT command
- [ ] 32. Write unit tests for curly brace parsing
- [ ] 33. Write unit tests for one-line syntax
- [ ] 34. Write integration tests (mixed syntax files)
- [ ] 35. Test backward compatibility suite
- [ ] 36. Test migration tool on real scripts
- [ ] 37. Performance testing (parsing speed)
- [ ] 38. Documentation review and finalization

**Status:** ⏸️ Blocked by all previous moves
**Estimated Complexity:** Simple to medium (test writing)

---

## Current Work Session

### Today's Goal
Start Move 1 by implementing the PRINT command and template string support.

### Next Steps
1. Read `core/interpreters/ucode.py` to understand current command structure
2. Implement PRINT command handler (Steps 1-2)
3. Add deprecation warning system (Step 3)
4. Commit progress: "v1.1.1 Move 1: Steps 1-3 complete"

### Files to Modify
- `core/interpreters/ucode.py` - Add PRINT command, curly brace parsing
- `core/interpreters/ucode.py` - Extend control flow handlers
- Tests to create in `sandbox/tests/test_ucode_modern_syntax.py`

---

## Notes & Decisions

### Design Decisions
- **Backward Compatibility:** Critical - old syntax must continue to work
- **Deprecation Strategy:** Soft deprecation with warnings, hard removal in v2.0
- **Migration Tool:** Optional but recommended for users
- **Documentation:** Maintain docs for both syntaxes during v1.x

### Questions to Resolve
- [ ] Should curly braces be optional or required for new code?
  - **Decision:** Optional - both work, modern is recommended
- [ ] How verbose should deprecation warnings be?
  - **Decision:** Show once per session per deprecated feature
- [ ] Should migration tool be automatic or manual?
  - **Decision:** Manual with dry-run preview for safety

### Blockers
None currently.

---

## Progress Log

### 2025-11-27 - Session 1
- Created current-round.md
- Reviewed roadmap for v1.1.1
- **Step 1 COMPLETE**: Added PRINT command handler to core/interpreters/ucode.py
  - Handles quoted strings (double and single quotes)
  - Handles variable names (unquoted)
  - Returns output as string
- **Step 2 COMPLETE**: Implemented template string support
  - Pattern: `PRINT "Text with ${variable_name}"`
  - Uses regex to find ${var} patterns
  - Substitutes with actual variable values
  - Keeps original ${var} if variable not found
  - Works with numbers, strings, all types
- Created test suite: `sandbox/tests/test_print_standalone.py` (7/7 tests pass)
- Created test script: `sandbox/ucode/test_print.uscript` (works perfectly)
- **Step 3 COMPLETE**: Added ECHO deprecation warnings
  - ECHO now shows deprecation warning on first use
  - Warning only shown once per session
  - ECHO still works (executes as PRINT)
  - Created test: `sandbox/tests/test_echo_deprecation.py` (all tests pass)
- **Step 4 COMPLETE**: Curly brace syntax for IF blocks
  - New syntax: `IF (condition) { }` and `} ELSE {`
  - Old syntax still works: `IF condition ... ENDIF`
  - Both syntaxes fully functional and tested
  - Handles nested blocks and brace depth tracking
  - Test script: `sandbox/ucode/test_square_brackets.uscript` (all 4 tests pass)
- **Next:** Step 5 - Extend FOR/WHILE/FUNCTION/TRY for curly braces

---

## Quick Reference

**Roadmap:** `sandbox/dev/roadmap/ROADMAP-V1.1.x-COMPLETE.md`
**Tests:** `sandbox/tests/`
**Core Interpreter:** `core/interpreters/ucode.py`
**Templates:** `core/data/templates/`, `sandbox/workflow/templates/`
**Commit Format:** `v1.1.1 Move X: Step Y - Description`

**Next Session:** Pick up at Step 1 - Implement PRINT command
