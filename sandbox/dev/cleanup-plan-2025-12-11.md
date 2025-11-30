# uDOS Cleanup & uCODE Conversion Plan

**Date**: December 11, 2025
**Status**: In Progress

## 📋 Scripts for uCODE Conversion

### High Priority - Simple Command Runners

These scripts primarily execute uDOS commands and would be better as .uscript:

1. **`sandbox/scripts/health_check.py`** → `sandbox/tests/health_check.uscript`
   - Runs: HELP, STATUS, VERSION
   - Simple command sequence, perfect for uCODE

2. **`sandbox/scripts/quick_startup_test.py`** → `sandbox/tests/quick_startup_test.uscript`
   - Runs: --version, STATUS --brief, HELP
   - Fast validation tests

3. **`sandbox/tests/shakedown.uscript`** - Already exists but is bash, should be pure uCODE

### Medium Priority - Update Utilities

4. **`sandbox/update_paths.py`** - Could be uCODE with FILE operations
5. **`sandbox/update_logging_paths.py`** - Could be uCODE with SEARCH/REPLACE
6. **`sandbox/update_all_docs.py`** - Could be uCODE with file batch operations

### Complex Scripts - Keep as Python

These require complex logic and should remain Python:
- `sandbox/scripts/comprehensive_shakedown.py` - Complex test framework
- `sandbox/scripts/generate_svg_diagram.py` - Gemini AI integration
- `sandbox/scripts/enhance_*_with_gemini.py` - AI processing
- All test files that validate Python imports/modules

## 🗑️ Files/Folders for Cleanup

### Redundant/Old Test Files

**Version-Specific Tests (Outdated)**:
- [ ] `sandbox/tests/test_v1_0_12_utilities.py` - v1.0.12 specific
- [ ] `sandbox/tests/test_v1_0_13_theming.py` - v1.0.13 specific
- [ ] `sandbox/tests/test_v1_0_16_standalone.py` - v1.0.16 specific
- [ ] `sandbox/tests/test_v1_0_17_*.py` (7 files) - v1.0.17 specific
- [ ] `sandbox/tests/test_v1_0_18_*.py` (6 files) - v1.0.18 specific
- [ ] `sandbox/tests/test_v1_0_2*.py` (13 files) - v1.0.2x specific
- [ ] `sandbox/tests/test_v1_0_30_*.py` (2 files) - v1.0.30 specific
- [ ] `sandbox/tests/test_v1_0_33_barter.py` - v1.0.33 specific

**Future Version Tests (Premature)**:
- [ ] `sandbox/tests/test_v1_1_*.py` (12 files) - Future versions
- [ ] `sandbox/tests/test_v1_2_*.py` (3 files) - v1.2.x tests
- [ ] `sandbox/tests/test_v1_3_*.py` (3 files) - v1.3.x tests
- [ ] `sandbox/tests/test_v1_6_0_infrastructure.py` - Far future

**Old Benchmarking/Profiling**:
- [ ] `sandbox/tests/analyze_coverage_v1_0_26.py`
- [ ] `sandbox/tests/baseline_report_v1_0_26.py`
- [ ] `sandbox/tests/baseline_v1_0_26.json`
- [ ] `sandbox/tests/benchmark_v1_0_26.py`
- [ ] `sandbox/tests/performance_v1_0_26.py`
- [ ] `sandbox/tests/quick_benchmark_v1_0_26.py`
- [ ] `sandbox/tests/startup_profiler_v1_0_26.py`

### Duplicate/Debug Files

**Test Debris**:
- [ ] `sandbox/tests/debug_test.uscript`
- [ ] `sandbox/tests/test_interactive.txt`
- [ ] `sandbox/tests/test_restored_commands.txt`
- [ ] `sandbox/tests/usage_tracker.json`

**One-Off Debug Scripts**:
- [ ] `sandbox/tests/test_bracket_debug.py`
- [ ] `sandbox/tests/test_oneline_debug.py`
- [ ] `sandbox/tests/test_print_script.py`
- [ ] `sandbox/tests/test_print_standalone.py`
- [ ] `sandbox/tests/test_set_debug.py`

### Empty/Minimal Directories

**Check for cleanup**:
- [ ] `sandbox/tests/e2e/` - If empty or unused
- [ ] `sandbox/tests/integration/` - Consolidate if minimal
- [ ] `sandbox/tests/manual/` - If outdated
- [ ] `sandbox/tests/memory/` - If redundant with sandbox/user/
- [ ] `sandbox/tests/scripts/` - If unused
- [ ] `sandbox/tests/unit/` - If minimal

### Sandbox Script Cleanup

**Old Development Scripts**:
- [ ] `sandbox/scripts/demo_v1_0_30.py` - Version-specific demo
- [ ] `sandbox/scripts/quick_test.py` - Replaced by comprehensive tests
- [ ] `sandbox/scripts/test_*.py` files in scripts/ (should be in tests/)

## ✅ Action Plan

### Phase 1: uCODE Conversions (This Session)
1. Convert `health_check.py` to `health_check.uscript`
2. Convert `quick_startup_test.py` to `quick_startup_test.uscript`
3. Rewrite `shakedown.uscript` to pure uCODE

### Phase 2: File Cleanup (This Session)
1. Remove all version-specific test files (test_v1_0_*.py)
2. Remove old benchmarking files
3. Remove debug/temporary files
4. Clean empty directories

### Phase 3: Directory Reorganization
1. Consolidate remaining tests into logical groups
2. Update VSCode tasks to reference new .uscript files
3. Update documentation

## 🎯 Expected Results

**Before**: 150+ test files, many version-specific and outdated
**After**: ~50-75 current, relevant test files + new .uscript automation

**Storage Savings**: ~2-3MB of old test files
**Maintenance**: Easier to maintain current tests vs legacy versions

---

**Priority**: Medium (cleanup debt, but not blocking development)
**Effort**: 1-2 hours total
**Risk**: Low (all files are in sandbox/, non-production)
