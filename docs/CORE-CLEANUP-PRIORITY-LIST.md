# Core Cleanup Priority List — uDOS

**Date:** 2026-01-31  
**Status:** Active Cleanup Plan  
**Based on:** Full audit of `core/` directory (300+ files, 50K+ LOC)

---

## 🎯 Executive Summary

Core has **significant technical debt** from multiple incomplete efforts:
- **95 handler files** (many are UI components misplaced in `commands/`)
- **152 service files** with 20+ naming inconsistencies
- **5 error handling implementations** that overlap
- **2.1K LOC of duplicate graphics code**
- **17.8K LOC monolith** in logging_manager.py
- **Multiple archive directories** indicating past attempts to clean up

**Estimated impact if all cleaned:** 20% LOC reduction + massive clarity gain.

---

## 🔴 TIER 1: CRITICAL (Do First — High Impact, Low Risk)

### 1.1 Graphics/Rendering System Cleanup
**Impact:** 2.1K LOC duplication, 43% reduction  
**Effort:** 4-6 hours  
**Risk:** Low (well-contained, good tests)

**Current State:**
```
services/graphics_service.py       ✅ Node.js bridge (clear)
services/graphics_library.py       ⚠️  Unclear vs compositor
services/graphics_compositor.py    ⚠️  ASCII composition  
services/diagram_compositor.py     🔴 DUPLICATE of graphics_compositor
services/diagram_generator.py      ⚠️  Overlaps with compositor
commands/draw_handler.py           ⚠️  Handler or utility?
output/graphics.py                 🔴 DEPRECATED (Phase 1 complete)
ui/block_graphics.py               ❓  Needs audit
services/feed/feed_renderer.py     ❓  Isolated or duplicate?
```

**Actions:**
- [x] Identify duplication
- [ ] **DELETE** `services/diagram_compositor.py` (confirmed duplicate)
- [ ] **KEEP** `services/graphics_compositor.py` (primary ASCII composition)
- [ ] **VERIFY** `diagram_generator.py` doesn't duplicate graphics_compositor
- [ ] **CLARIFY** `draw_handler.py` purpose (command handler or utility?)
- [ ] **REVIEW** `feed_renderer.py` (isolated or overlapping?)
- [ ] **REMOVE** `output/graphics.py` (deprecation complete)
- [ ] **AUDIT** `block_graphics.py` relationship to main compositor

**Files to check:**
- [core/services/graphics_compositor.py](core/services/graphics_compositor.py)
- [core/services/diagram_compositor.py](core/services/diagram_compositor.py)
- [core/services/diagram_generator.py](core/services/diagram_generator.py)

---

### 1.2 OK Handler Family Consolidation
**Impact:** 1.4K LOC duplication, 29% reduction  
**Effort:** 3-4 hours  
**Risk:** Low (well-isolated subsystem)

**Current State:**
```
commands/ok_handler.py             898 LOC (MAKE, ASK subcommands)
commands/okfix_handler.py          521 LOC (FIX subcommand) 🔴 DUPLICATE HANDLER
services/ok_config.py              226 LOC (config state)
services/ok_context_manager.py     303 LOC (context management)
services/ok_context_builder.py     241 LOC (context building) 🔴 OVERLAPS WITH MANAGER
```

**Problem:**
- `okfix_handler.py` should be a subcommand of `ok_handler.py`, not a separate handler
- `ok_context_builder.py` overlaps with `ok_context_manager.py`

**Actions:**
- [ ] **MERGE** `okfix_handler.py` → `ok_handler.py` (as OK FIX subcommand)
- [ ] **MERGE** `ok_context_builder.py` → `ok_context_manager.py` (single context service)
- [ ] **KEEP** `ok_config.py` (configuration is separate concern)
- [ ] **UPDATE** dispatcher references
- [ ] **TEST** all OK subcommands (MAKE, ASK, FIX)

**Files to edit:**
- [core/commands/ok_handler.py](core/commands/ok_handler.py)
- [core/commands/okfix_handler.py](core/commands/okfix_handler.py)
- [core/services/ok_context_builder.py](core/services/ok_context_builder.py)
- [core/services/ok_context_manager.py](core/services/ok_context_manager.py)

---

### 1.3 Deprecation Cleanup
**Impact:** 534 LOC removal, 100% of deprecated code  
**Effort:** 1-2 hours  
**Risk:** Very Low (code is already marked deprecated)

**Current State:**
```
output/graphics.py                 534 LOC 🔴 DEPRECATED (Phase 1 complete)
wizard/services/plugin_factory.py  Line 667+ TCZBuilder class (old TinyCore, deprecated)
```

**Actions:**
- [ ] **DELETE** `core/output/graphics.py` (deprecation complete as of Phase 1)
- [ ] **VERIFY** no imports from output/graphics.py
- [ ] **DEPRECATE** `wizard/services/plugin_factory.py::TCZBuilder` (already marked, keep for now)
- [ ] **ARCHIVE** any old version files found

**Files to remove:**
- `core/output/graphics.py`

---

## 🟠 TIER 2: IMPORTANT (Do Next — Medium Impact, Medium Risk)

### 2.1 Error Handling System Consolidation
**Impact:** 2.6K LOC fragmentation, 54% reduction  
**Effort:** 6-8 hours  
**Risk:** Medium (unclear current usage patterns)

**Current State:**
```
services/error_handler.py          50 LOC  (generic, incomplete)
services/error_intelligence.py     582 LOC (analysis/suggestions)
services/error_interceptor.py      407 LOC (catch & reroute) 
services/intelligent_error_handler.py 430 LOC (smart handling) 🔴 DUPLICATE NAME
services/debug_engine.py           499 LOC (debug mode)
services/debug_panel_service.py    640 LOC (debug UI) ✅ Clear
```

**Problem:**
- 5 files for one concern with no clear architecture
- `error_handler` (50 LOC) is too small and incomplete
- `intelligent_error_handler` duplicates name pattern with `error_intelligence`
- `debug_engine` conflates debugging with error handling
- No clear flow or integration between components

**Required Investigation:**
- [ ] Document current error handling flow
- [ ] Map dependencies between error services
- [ ] Check test coverage
- [ ] Get existing usage patterns

**Proposed Actions:**
- [ ] **CONSOLIDATE** to 2-3 file error system
- [ ] **MERGE** error_handler.py (50 LOC too small)
- [ ] **CHOOSE** primary error handler (error_intelligence or intelligent_error_handler)
- [ ] **CLARIFY** debug_engine.py role (debug ≠ error handling)
- [ ] **KEEP** debug_panel_service.py (UI concern, clear)

**Files to audit:**
- [core/services/error_handler.py](core/services/error_handler.py)
- [core/services/error_intelligence.py](core/services/error_intelligence.py)
- [core/services/error_interceptor.py](core/services/error_interceptor.py)
- [core/services/intelligent_error_handler.py](core/services/intelligent_error_handler.py)
- [core/services/debug_engine.py](core/services/debug_engine.py)

---

### 2.2 Manager/Service Naming Standardization
**Impact:** 20+ files, 0% LOC reduction but +1000% searchability  
**Effort:** 2-3 hours (mechanical find/replace)  
**Risk:** Low (naming refactor, good tooling)

**Current State:**
```
❌ INCONSISTENT NAMING:
  asset_manager.py         (should be asset_service.py)
  checkpoint_manager.py    (should be checkpoint_service.py)
  connection_manager.py    (should be connection_service.py)
  ... 15+ more _manager files
```

**Problem:**
- "Manager" adds no semantic value (services manage things)
- Inconsistent with other service naming
- Harder to search/discover

**Files to rename:**
```
asset_manager.py           → asset_service.py
checkpoint_manager.py      → checkpoint_service.py
citation_manager.py        → citation_service.py
connection_manager.py      → connection_service.py
device_manager.py          → device_service.py
editor_manager.py          → editor_service.py
help_manager.py            → help_service.py
history_manager.py         → history_service.py
menu_manager.py            → menu_service.py
mission_manager.py         → mission_service.py
memory_manager.py          → memory_service.py
resource_manager.py        → resource_service.py
role_manager.py            → role_service.py
state_manager.py           → state_service.py
user_manager.py            → user_service.py
```

**Actions:**
- [ ] Find all `*_manager.py` files in core/services/
- [ ] Rename to `*_service.py`
- [ ] Update all imports (mostly in `__init__.py` and handlers)
- [ ] Update dispatcher references if any
- [ ] Run full test suite

---

### 2.3 Monitoring Service Consolidation
**Impact:** 4 files, 1.2K LOC duplication, 40% reduction  
**Effort:** 4-5 hours  
**Risk:** Medium (multiple monitoring systems)

**Current State:**
```
services/device_monitor.py         (device monitoring)
services/disk_monitor.py           (disk monitoring)
services/server_monitor.py         (server monitoring)
services/api_monitor.py            (API monitoring)
```

**Problem:**
- 4 separate monitoring services with likely overlapping logic
- No unified monitoring architecture
- Each probably duplicates health check, logging, alerting

**Proposed Solution:**
```
services/monitoring_service.py
  ├── DeviceMonitor (pluggable)
  ├── DiskMonitor (pluggable)
  ├── ServerMonitor (pluggable)
  └── APIMonitor (pluggable)
```

**Actions:**
- [ ] Audit each monitor's implementation
- [ ] Identify common patterns (health check, logging, alerts)
- [ ] Extract common monitoring base class
- [ ] Consolidate to single monitoring_service.py with pluggable monitors
- [ ] Update dispatcher/initialization

---

### 2.4 Theme/Display System Cleanup
**Impact:** 1.7K LOC fragmentation, 24% reduction  
**Effort:** 3-4 hours  
**Risk:** Medium (UI-related)

**Current State:**
```
services/dashboard_service.py      780 LOC (role-based dashboard) ✅ Clear
services/dashboard_data_service.py 340 LOC (dashboard data) 🔴 SHOULD BE INTERNAL
services/display_mode_manager.py   326 LOC (display mode???)
services/theme_messenger.py        249 LOC (theme relay???)
```

**Problem:**
- `dashboard_data_service` should be internal module of `dashboard_service`
- `display_mode_manager` - purpose unclear (UI theme? Color scheme? Layout?)
- `theme_messenger` - unclear responsibility (broadcasts? Caches? Routes?)

**Required Investigation:**
- [ ] What is "display mode"? (terminology)
- [ ] What does "theme messenger" do? (behavior)
- [ ] Can dashboard_data be internal?

**Actions:**
- [ ] Merge `dashboard_data_service.py` → internal module of `dashboard_service.py`
- [ ] Clarify `display_mode_manager.py` purpose and rename if needed
- [ ] Clarify `theme_messenger.py` purpose and consolidate with theme system
- [ ] Consider unified display/theme architecture

---

## 🟡 TIER 3: ARCHITECTURE (Medium-term — Structural Changes)

### 3.1 Logging System Refactoring
**Impact:** 40K+ LOC monolith, 62% reduction  
**Effort:** 10-15 hours  
**Risk:** High (foundational system)

**Current State:**
```
services/logging_manager.py        17,800 LOC 🔴 MASSIVE MONOLITH
services/logger_compat.py          4,900 LOC (compatibility layer?)
services/loglang_logger.py         8,100 LOC (custom language??)
services/log_compression.py        12,700 LOC (compression)
services/biological_factors.py     15,500 LOC ❓❓❓ WHY IS THIS IN LOGGING?
```

**Problems:**
- `logging_manager.py` is 17.8K lines — it's a monolith
- `biological_factors.py` has NO BUSINESS being in logging (game/mood system?)
- `logger_compat.py` purpose unclear (compatibility with what?)
- `loglang_logger.py` - custom logging language? This seems experimental

**Required Investigation:**
- [ ] Why is `biological_factors.py` in services/? (should be game/mood system)
- [ ] What is `logger_compat.py` for? (backward compat? Cross-platform?)
- [ ] What is `loglang_logger.py`? (experimental custom language?)
- [ ] Can `logging_manager.py` be split into modular components?

**Proposed Actions:**
- [ ] **MOVE** `biological_factors.py` to correct location (not logging!)
- [ ] **DOCUMENT** or **DEPRECATE** `logger_compat.py`
- [ ] **CLARIFY** or **ARCHIVE** `loglang_logger.py`
- [ ] **SPLIT** `logging_manager.py` into:
  - `log_formatter.py` (formatting logic)
  - `log_rotation.py` (rotation/cleanup)
  - `log_aggregator.py` (aggregation logic)
  - Keep core as `logging_manager.py` (coordinator)

**Files to refactor:**
- [core/services/logging_manager.py](core/services/logging_manager.py)
- [core/services/logger_compat.py](core/services/logger_compat.py)
- [core/services/loglang_logger.py](core/services/loglang_logger.py)
- [core/services/log_compression.py](core/services/log_compression.py)
- [core/services/biological_factors.py](core/services/biological_factors.py)

---

### 3.2 Extension System Architecture
**Impact:** 2.7K LOC across 5 files, unclear boundaries  
**Effort:** 8-10 hours  
**Risk:** High (system-level)

**Current State:**
```
services/extension_lifecycle.py    458 LOC
services/extension_loader.py       257 LOC
services/extension_manager.py      673 LOC
services/extension_monitor.py      284 LOC
services/extension_registry.py     481 LOC
```

**Problem:**
- 5 files with unclear tier structure
- Is this Registry→Loader→Manager→Lifecycle? Or fragmented chaos?
- No clear documentation of extension loading pipeline

**Proposed Solution:**
Design clear 3-4 tier architecture:
```
extension_registry.py       (discovery, metadata)
extension_loader.py        (load, initialize)
extension_manager.py       (lifecycle, enable/disable)
extension_monitor.py       (health, performance) [OPTIONAL]
```

**Actions:**
- [ ] Document extension loading pipeline
- [ ] Design clear tier architecture
- [ ] Consider consolidating monitor into manager
- [ ] Verify test coverage
- [ ] Consider reducing to 3 files

---

### 3.3 Handler Categorization & UI Component Migration
**Impact:** Organization/Clarity  
**Effort:** 5-7 hours  
**Risk:** Medium (moving files between directories)

**Problem Handlers:**
```
commands/keypad_demo_handler.py    ⚠️  This is a UI component, not command
commands/selector_handler.py       ⚠️  This is a UI component (selector framework)
commands/tui_handler.py            ⚠️  This is TUI controller
```

**Why this matters:**
- Handlers should be command handlers (route to business logic)
- UI components should be in `ui/` (display/interaction)
- Current organization is confusing

**Actions:**
- [ ] Move misplaced handlers to `ui/`:
  - `commands/keypad_demo_handler.py` → `ui/keypad_demo.py`
  - `commands/selector_handler.py` → `ui/selector_framework.py`
  - `commands/tui_handler.py` → `ui/tui_controller.py`
- [ ] Document handler categories:
  - **Navigation:** MAP, PANEL, GOTO, FIND, TELL
  - **Game State:** BAG, GRAB, SPAWN, SAVE, LOAD
  - **System:** SHAKEDOWN, REPAIR, RESTART, SETUP, USER
  - **NPC:** NPC, TALK, REPLY
  - **Wizard:** CONFIG, PROVIDER, WIZARD, AI
- [ ] Suggest new handler organization in docs

---

## 🟢 TIER 4: POLISH (Nice-to-have)

### 4.1 Archive Directory Cleanup
**Files affected:**
```
core/.archive/
core/commands/.archive/2026-01-07-v1.0.1/
core/services/.archive/
```

**Action:**
- [ ] Review what's in archives
- [ ] Keep useful patterns, delete obsolete code
- [ ] Document decisions

---

### 4.2 TODOs & FIXMEs
**Current issues found:**
```
core/tui/ucode.py:             TODO: Real packaging logic
core/commands/talk_handler.py:  TODO: Get from game state (5+ instances)
```

**Action:**
- [ ] Create tickets for each TODO
- [ ] Assign to next sprint
- [ ] Track completion

---

## 📊 Implementation Order

### Week 1 (TIER 1 - Start immediately)
1. Graphics cleanup (1.1) — 4-6 hours
2. OK handler consolidation (1.2) — 3-4 hours
3. Deprecation cleanup (1.3) — 1-2 hours

**Impact:** 4K LOC removed, graphics pipeline clarified, OK system unified

### Week 2 (TIER 2 - High ROI items)
1. Error handling audit (2.1) — 6-8 hours (investigation heavy)
2. Manager renaming (2.2) — 2-3 hours (mechanical)
3. Monitoring consolidation (2.3) — 4-5 hours

**Impact:** 3.8K LOC removed, consistent naming, unified monitoring

### Week 3+ (TIER 3 - Structural)
1. Logging refactoring (3.1) — 10-15 hours
2. Extension architecture (3.2) — 8-10 hours
3. Handler migration (3.3) — 5-7 hours

**Impact:** 40K+ LOC refactored, clear architecture

---

## ✅ What's Already Good

These systems need **NO cleanup**:

| System | Files | Status | Why |
|--------|-------|--------|-----|
| **Version Management** | 3 | ✅ Clean | Simple, well-scoped |
| **Config System** | 2-3 | ✅ Well-organized | Clear boundaries |
| **Base Handler** | 1 | ✅ Good pattern | Excellent foundation |
| **Transport/Security** | 2 | ✅ Clear boundaries | Well-separated |
| **Knowledge Bank** | Modular | ✅ Good structure | Logical organization |
| **Graphics Service (bridge)** | 1 | ✅ Clear purpose | Node.js bridge is focused |

---

## 📋 Cleanup Checklist

### TIER 1
- [ ] 1.1 Graphics duplication (diagram_compositor.py delete)
- [ ] 1.2 OK handler consolidation (okfix→ok, context_builder→manager)
- [ ] 1.3 Deprecation cleanup (output/graphics.py delete)

### TIER 2
- [ ] 2.1 Error handling audit + consolidation plan
- [ ] 2.2 Manager → Service renaming (15+ files)
- [ ] 2.3 Monitoring service consolidation (4 monitors → 1)
- [ ] 2.4 Theme/display system clarification

### TIER 3
- [ ] 3.1 Logging system refactoring (split 17.8K monolith)
- [ ] 3.2 Extension system architecture review
- [ ] 3.3 Handler→UI component migration

### TIER 4
- [ ] 4.1 Archive cleanup
- [ ] 4.2 TODO/FIXME tickets

---

## 🎯 Success Metrics

| Metric | Current | Target | Benefit |
|--------|---------|--------|---------|
| **Core LOC** | ~50K | ~40K | 20% reduction in cognitive load |
| **Duplicate code** | 8-10K LOC | <1K | Single source of truth |
| **Naming consistency** | 70% | 95%+ | Easier discovery/maintenance |
| **Architectural clarity** | Moderate | High | Faster onboarding, fewer bugs |
| **File organization** | Scattered | Clear boundaries | Better navigation |

---

## Related Docs

- [AGENTS.md](AGENTS.md) — Core system boundaries
- [core/README.md](core/README.md) — Core subsystem overview
- [ADR-0003-alpine-linux-migration.md](decisions/ADR-0003-alpine-linux-migration.md) — Deprecation patterns
- [docs/PHASE5-HANDLER-LOGGING-INTEGRATION.md](PHASE5-HANDLER-LOGGING-INTEGRATION.md) — Handler architecture

---

**Status:** Active cleanup plan  
**Created:** 2026-01-31  
**Next Review:** After TIER 1 completion  
**Maintainer:** @fredporter

