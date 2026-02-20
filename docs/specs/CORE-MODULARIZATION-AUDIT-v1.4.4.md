# Core Modularization Audit — v1.4.4

**Status:** Phase 1 Discovery Complete (2026-02-20)
**Target Completion:** 2026-03-31
**Current Phase:** Phase 2 Remediation Planning
**Scope:** Comprehensive audit and hardening of Core module boundaries, dependency integrity, and code organization.

---

## Phase 1 Discovery Results (2026-02-20)

### Key Findings

**✅ Strengths:**
- Handler modules well-organized (43 files, largest ~850 LOC)
- Parser modules properly separated (<250 LOC each)
- Clear service-layer structure (54 modules)

**⚠️ CRITICAL ISSUES:**
1. **Core/Wizard Boundary Violation:** 7+ direct wizard imports in Core
   - `core/tui/ucode.py` — 6 wizard imports
   - `core/commands/wizard_handler.py` — port_manager
   - `core/commands/repair_handler.py` — library_manager + plugin_repository
   - `core/commands/library_handler.py` — library_manager
   - `core/services/rate_limit_helpers.py` — rate_limiter, provider_load_logger
   - `core/services/system_script_runner.py` — MonitoringManager

2. **Large Service Modules:** Several services exceed 700 LOC
   - `gameplay_service.py` (1188 LOC) — PTY lifecycle + state replay + game logic
   - `location_migration_service.py` (943 LOC) — Schema migration + indexing + validation
   - `self_healer.py` (729 LOC) — Multiple recovery strategies bundled

3. **Error Handling:** No unified contract; inconsistent patterns across handlers

### Phase 1 Status: ✅ COMPLETE
- [x] Boundary violations identified
- [x] Large modules cataloged
- [x] Error patterns reviewed
- [x] Test scaffolds located
- [ ] Ready for Phase 2 remediation planning

---

## Overview

v1.4.4 focuses on internal Core stability via systematic modularization review. The goal is to verify that Core maintains strict boundaries, follows single-responsibility principle, and remains stdlib-only and venv-independent. This document defines the audit checklist and remediation strategy.

---

## Audit Dimensions

### 1. Function-Level Modularization

**Objective:** Verify handlers, services, and parsers maintain reasonable function sizes and responsibilities.

#### Commands (`core/commands/`)

- [ ] **`help_handler.py`** — Review for nested sub-handlers; extract if >150 lines.
- [ ] **`health_handler.py`** — Review dependency checks; extract provider-specific probes.
- [ ] **`verify_handler.py`** — Review schema validators; extract contract checks.
- [ ] **`place_handler.py`** — Review workspace switching logic; extract navigator.
- [ ] **`binder_handler.py`** — Review binder operations; extract CRUD helpers.
- [ ] **`draw_handler.py`** — Review renderer dispatch; extract by widget type.
- [ ] **`run_handler.py`** — Review command dispatch; extract by execution strategy.
- [ ] **`play_handler.py`** — Review game state management; extract by game phase.
- [ ] **`rule_handler.py`** — Review automation logic; extract evaluator/actions.
- [ ] **`library_handler.py`** — Review library operations; extract by operation type.

**Remediation:** Extract nested functions >150 lines into separate helper modules (`*_helpers.py`).

#### Services (`core/services/`)

- [ ] **`command_parser.py`** — Verify tokenizer/parser/dispatcher separation.
- [ ] **`markdown_compiler.py`** — Verify tokenizer/AST/renderer separation.
- [ ] **`cache_manager.py`** — Verify coherency/TTL/eviction logic separation.
- [ ] **`workspace_manager.py`** — Verify mounting/switching/validation separation.
- [ ] **`gameplay_service.py`** — Verify state/event/tick logic separation.
- [ ] **`grid_runtime.py`** — Verify spatial/viewport/query logic separation.
- [ ] **`binder_manager.py`** — Verify catalog/index/search logic separation.
- [ ] **`logging_manager.py`** — Verify level/format/persistence logic separation.

**Remediation:** Extract cohesive sub-tasks into focused helper modules or subpackages.

#### Parsers (`core/parsers/`)

- [ ] **`markdown_parser.py`** — Verify tokenizer/grammar/frontmatter separate.
- [ ] **`location_parser.py`** — Verify LocId validation/expansion/linking separate.
- [ ] **`command_line_parser.py`** — Verify tokenization/validation/dispatch separate.
- [ ] **`yaml_parser.py`** — Verify parsing/validation/schema separate.
- [ ] **`place_ref_parser.py`** — Verify parsing/resolution/validation separate.

**Remediation:** Consolidate related parser logic; extract schema validators into dedicated module.

#### Runtime (`core/runtime/`)

- [ ] **`server.py`** — Verify startup/shutdown/request-routing phases distinct.
- [ ] **`repl.py`** — Verify input/parsing/execution phases distinct.
- [ ] **`compiler.py`** — Verify parse/validate/generate phases distinct.
- [ ] **`adapters/`** — Verify each adapter has clear interface contract.

**Remediation:** Extract phase-specific logic; enforce immutable interfaces between phases.

---

### 2. Dependency Integrity

**Objective:** Verify Core remains stdlib-only, has no circular dependencies, and respects module boundaries.

#### Stdlib-Only Verification

```bash
# Check for non-stdlib imports in core/
grep -r "^import " core/ | grep -v "^core/" | grep -v __pycache__ | wc -l
# Should be 0 (all imports either stdlib or core.*)

# Check for wizard dependencies
grep -r "from wizard" core/ | grep -v __pycache__ | wc -l
# Should be 0

# Check for venv-required packages
grep -r "import numpy\|import pandas\|import requests\|import fastapi" core/ | grep -v __pycache__ | wc -l
# Should be 0
```

#### Circular Dependency Check

```python
# Use dependency-resolver tool or manual audit
# DAG should be acyclic:
# core/commands/ -> core/services/ -> core/parsers/ -> (stdlib)
# No back-edges allowed
```

#### Public/Private Boundary

- [ ] Document public API surface for each module (docstrings + `__all__`).
- [ ] Verify private functions prefixed with `_`.
- [ ] Verify no private imports from public modules.
- [ ] Enforce via linter rules in CI.

---

### 3. Error Handling Consistency

**Objective:** Verify all error paths conform to contract schema and include recovery guidance.

#### Error Contract Schema

```python
# All command handlers should raise errors structured as:
class CommandError(Exception):
    def __init__(self, code: str, message: str, recovery_hint: str = ""):
        self.code = code  # e.g., "ERR_INVALID_WORKSPACE"
        self.message = message
        self.recovery_hint = recovery_hint

# All errors logged via get_logger() at consistent levels
# Errors mapped to HTTP status codes in Wizard routes
```

#### Error Coverage Checklist

- [ ] All error codes documented in `ERROR-CODES-v1.4.4.md`.
- [ ] All command handlers have `try/except` with proper logging.
- [ ] No unhandled exceptions escape command layer.
- [ ] Recovery hints provided for 100% of user-facing errors.
- [ ] Sensitive data (paths, credentials) never logged at ERROR level.

---

### 4. Test Coverage & Boundary Tests

**Objective:** Verify Core/Wizard separation via isolated test suite.

#### Core-Only Tests

```bash
# Tests that run with system Python, no venv
pytest core/tests/ -v --co -q  # List all tests

# Should include:
# - stdlib-only imports
# - no network calls
# - no file access outside vault/
```

#### Boundary Tests

```bash
# Explicit tests that verify isolation
core/tests/v1_4_4_boundary_test.py:
  - test_no_wizard_imports()
  - test_no_venv_dependencies()
  - test_no_network_imports()
  - test_no_file_system_escapes()
```

#### Coverage Targets

- [ ] Command handlers: 90%+ coverage.
- [ ] Services: 85%+ coverage.
- [ ] Parsers: 95%+ coverage (critical for correctness).
- [ ] Runtime: 80%+ coverage.

---

## Audit Phases

### Phase 1: Discovery (2026-03-01 to 2026-03-08)

- [ ] Generate dependency graph (`pipdeptree`-style output for imports).
- [ ] List all functions >150 lines.
- [ ] Extract error codes and recovery hints.
- [ ] Count test coverage per module.
- [ ] Document current state in draft report.

### Phase 2: Remediation (2026-03-09 to 2026-03-24)

- [ ] Apply function-level extractions based on Phase 1 findings.
- [ ] Add missing error handling + recovery hints.
- [ ] Consolidate parser logic per recommendations.
- [ ] Add boundary tests for Core/Wizard separation.
- [ ] Increase coverage to targets.

### Phase 3: Verification (2026-03-25 to 2026-03-31)

- [ ] Re-run discovery checklist; compare before/after.
- [ ] Execute full test suite (90%+ pass rate).
- [ ] Run dependency cycle detector (0 cycles).
- [ ] Re-verify stdlib-only imports.
- [ ] Sign off on remediation report.

---

## Deliverables

1. **CORE-MODULARIZATION-AUDIT-v1.4.4.md** (this file updates with findings)
2. **ERROR-CODES-v1.4.4.md** — All error codes + recovery hints
3. **CORE-BOUNDARY-TESTS-v1.4.4.md** — New test suite reference
4. **core/tests/v1_4_4_boundary_test.py** — Executable boundary tests
5. **Dependency graph diagram** (text or Mermaid format)
6. **Remediation checklist with before/after metrics**

---

## Success Criteria

- [ ] 0 circular dependencies detected
- [ ] 0 non-stdlib imports in `core/`
- [ ] 0 wizard imports in `core/`
- [ ] All functions sized <150 lines (or justified)
- [ ] 90%+ coverage on critical paths
- [ ] 100% of user-facing errors have recovery hints
- [ ] All tests pass (green CI)

---

## References

- [u_dos_python_environments_dev_brief.md](u_dos_python_environments_dev_brief.md) — Core/Wizard boundary policy
- [docs/roadmap.md#v1.4.4](../roadmap.md#v144--core-hardening-demo-scripts--educational-distribution) — v1.4.4 roadmap
- [core/README.md](../../core/README.md) — Core module overview
