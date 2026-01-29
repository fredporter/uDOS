---
uid: udos-wiki-stream1-action-plan-20260130180000-UTC-L300AB57
title: Stream 1 Action Plan - TypeScript Markdown Runtime
tags: [wiki, roadmap, stream1, implementation]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
---

# Stream 1 Action Plan: TypeScript Markdown Runtime Implementation

**Phase:** Post-Wiki Standardization → Core Runtime Development  
**Estimated Duration:** 2-3 weeks  
**Priority:** HIGH (enables all downstream features)

---

## Current Status

✅ **Stream 1 Sub-Components Complete:**
- Spatial Filesystem v1.0.7.1 (core/services/spatial_filesystem.py, 850 lines)
- Wiki Standardization (247 files, all standardized)
- Documentation complete (specs, guides, examples)

⏳ **Stream 1 Remaining:**
- TypeScript Markdown Runtime implementation
- Grid Runtime + Spatial Computing visualization
- File Parsing System integration
- Complete TUI output toolkit

---

## Next Priority: TypeScript Markdown Runtime

### Why This Matters

The TypeScript Markdown Runtime is the **core execution engine** that enables:
- Dynamic document state management (`$variables`)
- Interactive forms and navigation
- Conditional rendering (if/else blocks)
- Database connectivity (read-only SQLite)
- Scripting capabilities (uPY integration)

### Implementation Checklist

#### Phase 1A: State Management System (3 days)
**Goal:** Variable declaration, interpolation, and mutation

**Tasks:**
- [ ] Create `core/runtime/state_manager.py` (200 lines)
  - Variable registry (store/retrieve)
  - Type validation (string, number, boolean, array, object)
  - Scope management (global, session, document)
  - Mutation tracking (dirty flag for UI updates)

- [ ] Implement variable interpolation in Markdown text (150 lines)
  - Pattern: `${variable_name}` in body text
  - Support nested properties: `${user.profile.name}`
  - Handle undefined gracefully (empty string or default)
  - Track dependencies for reactive updates

- [ ] Add `$set` runtime block handler (100 lines)
  - Syntax: `$set variable_name = value`
  - Support expressions: `$set count = count + 1`
  - Type coercion rules
  - Validation before mutation

**Files to Create/Modify:**
- `core/runtime/state_manager.py` (NEW)
- `core/parsers/markdown_runtime_parser.py` (MODIFY - add variable extraction)
- `core/commands/runtime_handler.py` (NEW - expose state commands to TUI)

**Testing:**
- Unit tests: `core/tests/test_state_manager.py`
- Integration tests: `core/tests/test_markdown_execution.py`

---

#### Phase 1B: Runtime Blocks (4 days)
**Goal:** Parse and execute core runtime block types

**Block Types to Implement:**

1. **`state` block** (track state changes)
   ```markdown
   ```state
   {
     "user": { "name": "Alice", "age": 30 },
     "count": 0,
     "items": []
   }
   ```
   ```

2. **`set` block** (mutate state)
   ```markdown
   ```set
   count = count + 1
   user.age = 25
   items.push("new item")
   ```
   ```

3. **`form` block** (collect input)
   ```markdown
   ```form
   {
     "fields": [
       { "name": "username", "type": "text", "required": true },
       { "name": "email", "type": "email" }
     ]
   }
   ```
   ```

4. **`if/else` block** (conditional rendering)
   ```markdown
   ```if
   condition: count > 0
   ---
   Show this if true
   ```
   ```

5. **`nav` block** (document navigation)
   ```markdown
   ```nav
   {
     "links": [
       { "label": "Home", "target": "README.md" },
       { "label": "Settings", "target": "config.md" }
     ]
   }
   ```
   ```

6. **`panel` block** (UI container)
   ```markdown
   ```panel
   {
     "title": "Summary",
     "type": "info|warning|success|error"
   }
   Content goes here
   ```
   ```

7. **`map` block** (spatial visualization)
   ```markdown
   ```map
   {
     "source": "@sandbox/dataset.table.md",
     "layer": "SUR",
     "viewport": "80x30"
   }
   ```
   ```

**Tasks:**
- [ ] Create `core/runtime/block_parser.py` (300 lines)
  - Identify block type from fence language
  - Extract block parameters (JSON headers)
  - Separate block content from parameters
  - Validate block structure

- [ ] Create `core/runtime/block_executor.py` (400 lines)
  - Implement executor for each block type
  - Call state_manager for mutations
  - Form handler with validation
  - Conditional evaluation engine
  - Navigation resolver

- [ ] Create `core/runtime/form_handler.py` (200 lines)
  - Field type validation (text, email, number, select, checkbox, date)
  - Required field enforcement
  - Pattern matching (regex for email, phone, etc.)
  - Return structured form submission data

**Files to Create/Modify:**
- `core/runtime/block_parser.py` (NEW)
- `core/runtime/block_executor.py` (NEW)
- `core/runtime/form_handler.py` (NEW)
- `core/runtime/state_manager.py` (MODIFY - expand for block state)

**Testing:**
- Unit tests: `core/tests/test_block_parser.py`
- Unit tests: `core/tests/test_block_executor.py`
- Integration: `core/tests/test_markdown_execution.py`

---

#### Phase 1C: Variable Interpolation & Expression Evaluation (3 days)
**Goal:** Dynamic text with variable substitution and expressions

**Tasks:**
- [ ] Create `core/runtime/expression_evaluator.py` (250 lines)
  - Parse JavaScript-like expressions
  - Evaluate arithmetic: `count + 1`, `price * tax`
  - Evaluate string concatenation: `"Hello, " + user.name`
  - Support ternary: `count > 0 ? "items" : "no items"`
  - Short-circuit evaluation for conditionals

- [ ] Implement template interpolation (100 lines)
  - Replace `${expr}` in text
  - Lazy evaluation (parse templates once, evaluate on demand)
  - Cache compiled expressions
  - Safe evaluation (no arbitrary code execution)

- [ ] Add null/undefined handling (50 lines)
  - Default values: `${user.name || "Anonymous"}`
  - Optional chaining: `${user?.profile?.name}`
  - Array indexing: `${items[0]}`

**Files to Create/Modify:**
- `core/runtime/expression_evaluator.py` (NEW)
- `core/runtime/state_manager.py` (MODIFY - add expression context)

**Testing:**
- Unit tests: `core/tests/test_expression_evaluator.py`
- Parametrized tests for edge cases

---

#### Phase 1D: SQLite Database Binding (2 days)
**Goal:** Read-only database access from Markdown

**Tasks:**
- [ ] Create `core/runtime/db_binder.py` (200 lines)
  - Connect to SQLite database (read-only)
  - Query execution with parameter binding
  - Result set to JSON conversion
  - Error handling (database errors, query syntax)
  - Caching for repeated queries

- [ ] Implement `$query` block handler (100 lines)
  ```markdown
  ```$query
  source: @knowledge/survival.db
  sql: SELECT * FROM techniques WHERE category = ?
  params: ["fire"]
  ```
  ```

- [ ] Add result variable binding (100 lines)
  - Results → `$query_results` variable
  - Row iteration: `$for row in $query_results`
  - Single row access: `$query_results[0].name`

**Files to Create/Modify:**
- `core/runtime/db_binder.py` (NEW)
- `core/runtime/block_executor.py` (MODIFY - add query block)
- `core/commands/runtime_handler.py` (MODIFY - expose query commands)

**Testing:**
- Unit tests with SQLite fixture database
- Integration tests with knowledge databases

---

#### Phase 1E: Core Node Runner (2 days)
**Goal:** Parse, validate, and execute Markdown documents

**Tasks:**
- [ ] Create `core/runtime/markdown_executor.py` (300 lines)
  - Load Markdown file + frontmatter
  - Parse frontmatter location (spatial context)
  - Extract and validate all blocks
  - Execute in sequence (state → blocks)
  - Track execution state and errors
  - Return final state + output

- [ ] Implement error handling and recovery (150 lines)
  - Validation errors (missing required fields)
  - Execution errors (block failures)
  - Graceful degradation (skip failed blocks, log)
  - Error reporting with line numbers

- [ ] Add execution hooks (100 lines)
  - Before/after execution callbacks
  - Logging integration (canonical logger)
  - Performance monitoring

**Files to Create/Modify:**
- `core/runtime/markdown_executor.py` (NEW)
- `core/commands/runtime_handler.py` (MODIFY - add execute command)
- `core/services/logging_manager.py` (MODIFY - add runtime logging)

**Testing:**
- End-to-end tests with complete Markdown documents
- Performance benchmarks (execution time)

---

### Reference Specification

**Doc:** `docs/specs/typescript-markdown-runtime.md` (Already complete)

**Key Sections:**
- Variable system (naming, scoping, types)
- Block types and syntax (7 core blocks)
- Expression evaluation (arithmetic, string, conditional)
- Error handling (validation, execution)
- Database binding (read-only SQLite)
- Integration with spatial filesystem

---

## Estimated Effort

| Phase | Component | Duration | LOC | Status |
|-------|-----------|----------|-----|--------|
| 1A | State Management | 3 days | 450 | 🔲 TODO |
| 1B | Runtime Blocks | 4 days | 900 | 🔲 TODO |
| 1C | Expression Evaluation | 3 days | 400 | 🔲 TODO |
| 1D | Database Binding | 2 days | 400 | 🔲 TODO |
| 1E | Core Node Runner | 2 days | 550 | 🔲 TODO |
| **TOTAL** | **Runtime Core** | **14 days** | **2,700** | **🔲 TODO** |

---

## Success Criteria

✅ All phases complete when:
1. All 5 core runtime modules implemented (2,700+ LOC)
2. Unit test coverage ≥ 85% (core modules)
3. Integration tests with sample Markdown documents pass
4. TUI handler integrates runtime (EXECUTE command)
5. Documentation with examples added to `/docs/examples/`
6. Performance meets baseline (< 100ms for typical document)

---

## Next Steps

1. **Start Phase 1A** — State management implementation
   - [ ] Create state_manager.py with Variable class
   - [ ] Add unit tests for state operations
   - [ ] Test variable interpolation patterns

2. **Build incrementally** — Phase 1A → 1B → ... → 1E
   - Test each phase before starting next
   - Create example documents as regression tests
   - Document edge cases as they arise

3. **Integration checkpoint** — After Phase 1E
   - Expose runtime via TUI EXECUTE command
   - Run end-to-end test with real Markdown file
   - Performance profiling and optimization

---

## Implementation Resources

**Reference Docs:**
- [TypeScript Markdown Runtime Spec](../docs/specs/typescript-markdown-runtime.md)
- [Core Runtime Status](../docs/specs/core-runtime-status.md) — Gap analysis
- [Example Scripts](../docs/examples/example-script.md) — All TS Markdown features
- [SQLite Example](../docs/examples/example-sqlite-db.md) — Database schema patterns

**Related Code:**
- `core/parsers/markdown_parser.py` — Basic Markdown parsing
- `core/services/logging_manager.py` — Canonical logger
- `knowledge/` — Sample databases and content
- `core/commands/` — Handler pattern examples

**Similar Implementations to Reference:**
- `core/commands/shakedown_handler.py` — System validation (error handling patterns)
- `core/services/spatial_filesystem.py` — State management patterns
- `wizard/services/` — Database connection patterns

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Expression evaluator too slow | Implement expression caching + benchmarking early |
| Database access blocking | Use read-only mode + connection pooling |
| Complex state mutations | Start with simple assignments, add operators incrementally |
| Block parsing ambiguity | Test edge cases (nested blocks, escaped backticks) |
| Memory leaks in state tracking | Profile with large state objects, implement cleanup |

---

## Questions for Review

1. Should expression evaluator support JavaScript-like syntax or simpler subset?
2. Should `$for` loops be part of Phase 1B or deferred to Phase 2?
3. Should we support async operations (API calls) in runtime blocks?
4. Should form submission trigger state mutations automatically or require explicit `$set`?

---

**Action:** Ready to begin Phase 1A implementation.  
**Estimated Start:** 2026-01-30 (immediate)  
**Expected Completion:** 2026-02-13

---

**Status:** DRAFT (review and confirm before implementing)  
**Maintained by:** uDOS Engineering
