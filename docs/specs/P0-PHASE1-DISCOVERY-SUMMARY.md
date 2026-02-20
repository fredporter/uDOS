# P0 Phase 1 Discovery Summary — v1.4.4

**Date:** 2026-02-20
**Status:** ✅ COMPLETE
**Next Phase:** Phase 2 Remediation (2026-03-01 to 2026-03-24)

---

## What Was Completed

### 1. Core Module Audit ✅
- [x] Scanned all Python files in `core/` (150+ files)
- [x] Measured function sizes (handlers, services, parsers)
- [x] Identified boundary violations (Wizard imports)
- [x] Cataloged large modules (1100+ LOC candidates)
- [x] Assessed error handling patterns (inconsistent)

### 2. Specification Documents Created ✅
- [x] **CORE-MODULARIZATION-AUDIT-v1.4.4.md** — Complete audit findings + remediation plan
- [x] **ERROR-HANDLING-v1.4.4.md** — Contract schema + error registry + implementation guide
- [x] Test scaffolds verified: `v1_4_4_stdlib_command_integration_test.py`, `v1_4_4_display_render_test.py`

### 3. Critical Findings Documented ✅

**CRITICAL (Blocks v1.4.4):**
- Core imports from Wizard in 7+ locations (violates offline-first architecture)
  - `core/tui/ucode.py` — 6 wizard imports
  - `core/commands/wizard_handler.py`, `repair_handler.py`, `library_handler.py`
  - `core/services/rate_limit_helpers.py`, `system_script_runner.py`

**MEDIUM (Improves code quality):**
- Large service modules (1100+ LOC) could be split
  - `gameplay_service.py` (1188 LOC) → PTY lifecycle + state replay split
  - `location_migration_service.py` (943 LOC) → schema versioning + indexing split
  - `self_healer.py` (729 LOC) → recovery strategy plugins

**INFORMATIONAL (Document for future):**
- Error handling is inconsistent; needs unified CommandError contract
- Parser modules are well-structured (no changes needed)
- Handler files are appropriately sized (no immediate refactoring)

---

## P0 Execution Timeline

### Phase 1: Discovery ✅ (2026-02-20)
```
✅ Module structure surveyed
✅ Boundary violations identified
✅ Large modules cataloged
✅ Error patterns reviewed
✅ Spec documents created
✅ Audit findings documented
```
**Time:** 1.5 hours
**Deliverables:** This document + CORE-MODULARIZATION-AUDIT-v1.4.4.md + ERROR-HANDLING-v1.4.4.md

---

### Phase 2: Remediation Planning (Next)
```
📅 2026-03-01 to 2026-03-31 (4 weeks)
```

**Week 1 (03-01 to 03-08): Dependency Boundary Enforcement**
- [ ] Map all 7 wizard imports to understand feature dependency
- [ ] Design provider registration mechanism (callbacks instead of imports)
- [ ] Create adapter layer in Core for Wizard bridge (if approved)
- [ ] Implement boundary enforcement tests
- [ ] Remove wizard imports from Core

**Week 2-3 (03-09 to 03-24): Service Module Extraction**
- [ ] Split `gameplay_service.py` → PTY + state replay + adapter modules
- [ ] Split `location_migration_service.py` → schema + indexing modules
- [ ] Extract recovery strategies from `self_healer.py`
- [ ] Add tests for new modules
- [ ] Update imports and integration points

**Week 4 (03-25 to 03-31): Error Contract Implementation + Verification**
- [ ] Create `core/services/error_contract.py` with CommandError class
- [ ] Update all 43 handlers to use CommandError
- [ ] Add recovery hints to 100% of errors
- [ ] Create comprehensive error handling test suite (50+ tests)
- [ ] Verify zero sensitive data in logs
- [ ] Final audit report + gate approval

---

## P0 Success Criteria (Phase 3)

### Code Quality Gates
- [ ] ✅ 0 wizard imports in Core (boundary enforcement test passing)
- [ ] ✅ 0 circular dependencies detected
- [ ] ✅ All services <700 LOC (or split if larger)
- [ ] ✅ All handlers use CommandError contract
- [ ] ✅ Zero sensitive data in error logs

### Test Coverage
- [ ] ✅ 90%+ coverage on critical paths (commands + services)
- [ ] ✅ Boundary tests: stdlib-only, no wizard imports
- [ ] ✅ Error recovery path tests (all 40+ error codes)
- [ ] ✅ Module-level parity tests passing

### Documentation
- [ ] ✅ This audit complete and signed off
- [ ] ✅ Remediation checklist with before/after metrics
- [ ] ✅ Dependency graph visualization
- [ ] ✅ Error code registry complete

---

## Files Ready for Phase 2

### Specification Documents (Created This Phase)
1. **docs/specs/CORE-MODULARIZATION-AUDIT-v1.4.4.md**
   - Complete Phase 1 findings
   - Detailed remediation plan
   - Service extraction candidates listed

2. **docs/specs/ERROR-HANDLING-v1.4.4.md**
   - CommandError contract schema
   - Complete error code registry (40+ codes)
   - Implementation patterns + testing strategy
   - Recovery hint guidelines

### Test Scaffold Files (Existing)
1. **core/tests/v1_4_4_stdlib_command_integration_test.py**
   - Command lifecycle tests
   - Error handling validation
   - Display rendering parity

2. **core/tests/v1_4_4_display_render_test.py**
   - TUI consistency tests
   - Viewport rendering tests

### Implementation Templates (Needed Phase 2)
- [ ] `core/services/error_contract.py` (CommandError implementation)
- [ ] `core/tests/v1_4_4_boundary_test.py` (dependency enforcement)
- [ ] `core/tests/v1_4_4_error_handling_test.py` (error contract validation)
- [ ] Series of `*_helpers.py` files for service splits

---

## Key Decisions for Phase 2

### 1. Core/Wizard Bridge Strategy
**Decision Required:** How should Core access optional Wizard features?

**Options:**
- Option A: Create `core/services/wizard_bridge.py` adapter (explicit integration points)
- Option B: Use provider registry (callbacks registered at startup)
- Option C: Move features to Wizard, keep Core truly offline-only

**Recommendation:** Option B (provider registry) — keeps Core clean, allows optional Wizard features

### 2. Service Module Splits
**Decision Required:** Should we split large services now or defer?

**Recommendation:** Prioritize `gameplay_service.py` split (needed for game lens integration in P1)

### 3. Error Contract Rollout
**Decision Required:** Should we update all handlers at once or incrementally?

**Recommendation:** Create base contract first, then batch-update handlers per feature area

---

## Next Steps

### Immediate (Today)
1. ✅ Phase 1 discovery complete
2. ✅ Specifications created
3. ⏭️ Review findings with team
4. ⏭️ Approve remediation strategy (3 key decisions above)

### Week of 2026-03-01
1. Activate Phase 2 execution
2. Begin boundary enforcement work
3. Start provider registry design
4. Create error_contract.py implementation

### Track Progress
- Use `docs/roadmap.md` (v1.4.4 section) for ongoing updates
- Update this P0 summary weekly with progress
- Maintain checklist in CORE-MODULARIZATION-AUDIT-v1.4.4.md

---

## References

### Canonical Roadmap
- `docs/roadmap.md` — v1.4.4 Core Hardening section
- `docs/releases/2026-02-17-next-dev-round-prep.md` — Round prep context

### Specification Documents
- `docs/specs/CORE-MODULARIZATION-AUDIT-v1.4.4.md` — Detailed audit findings
- `docs/specs/ERROR-HANDLING-v1.4.4.md` — Error contract specification

### Implementation Guides
- `docs/howto/UCODE-COMMAND-REFERENCE.md` — Command semantics (needed for error mapping)
- Core module: `core/README.md` — Module overview

---

**Phase 1 Owner:** GitHub Copilot
**Phase 2 Owner:** [Assign to engineer]
**Status:** Ready for Phase 2 kickoff (2026-03-01)
**Last Updated:** 2026-02-20
