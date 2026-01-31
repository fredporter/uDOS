# Core Cleanup — File Manifest

**Purpose:** Quick lookup of all files involved in cleanup  
**Status:** Audit complete, cleanup not started  
**Date:** 2026-01-31

---

## 🔴 TIER 1: CRITICAL FILES

### 1.1 Graphics System Duplication

**DELETE:**
- `core/services/diagram_compositor.py` — **CONFIRMED DUPLICATE** of graphics_compositor.py

**REMOVE (Deprecated):**
- `core/output/graphics.py` — 534 LOC, Phase 1 deprecation complete

**VERIFY/AUDIT:**
- `core/services/graphics_compositor.py` — Primary ASCII compositor (keep)
- `core/services/diagram_generator.py` — Verify doesn't duplicate compositor
- `core/commands/draw_handler.py` — Verify is command handler, not utility
- `core/ui/block_graphics.py` — Check relationship to compositor
- `core/services/feed/feed_renderer.py` — Check if isolated or duplicate

---

### 1.2 OK Handler Family

**MERGE:**
- `core/commands/okfix_handler.py` (521 LOC) → `core/commands/ok_handler.py` (as OK FIX subcommand)

**CONSOLIDATE:**
- `core/services/ok_context_builder.py` (241 LOC) → `core/services/ok_context_manager.py` (merge context building into manager)

**KEEP:**
- `core/commands/ok_handler.py` (898 LOC) — Will become full OK command hub
- `core/services/ok_config.py` (226 LOC) — Configuration is separate concern
- `core/services/ok_context_manager.py` (303 LOC) — Will absorb builder

**UPDATE:**
- `core/tui/dispatcher.py` — Update command registrations for OK handler
- `core/commands/__init__.py` — Update lazy imports

---

### 1.3 Deprecation Cleanup

**DELETE:**
- `core/output/graphics.py` — 534 LOC, completely deprecated since Phase 1

**CHECK FOR IMPORTS:**
- Verify no files import from `core/output/graphics`
- Update any references

**KEEP (Already Deprecated but Don't Delete Yet):**
- `wizard/services/plugin_factory.py::TCZBuilder` class (line 667+) — Marked deprecated, keep for backward compat

---

## 🟠 TIER 2: IMPORTANT FILES

### 2.1 Error Handling System (AUDIT FIRST)

**Files to audit (no deletions yet):**
- `core/services/error_handler.py` (50 LOC) — Too small, likely incomplete
- `core/services/error_intelligence.py` (582 LOC) — Error analysis/suggestions
- `core/services/error_interceptor.py` (407 LOC) — Catch & reroute errors
- `core/services/intelligent_error_handler.py` (430 LOC) — Smart error handling
- `core/services/debug_engine.py` (499 LOC) — Debug mode (overlaps with errors?)
- `core/services/debug_panel_service.py` (640 LOC) — Debug UI (KEEP - clear purpose)

**Action:** 
Document current architecture before making changes. Likely consolidate to 2-3 files.

---

### 2.2 Manager/Service Renaming (15+ files)

**RENAME (in core/services/):**

| Current Name | New Name |
|---|---|
| `asset_manager.py` | `asset_service.py` |
| `checkpoint_manager.py` | `checkpoint_service.py` |
| `citation_manager.py` | `citation_service.py` |
| `connection_manager.py` | `connection_service.py` |
| `device_manager.py` | `device_service.py` |
| `editor_manager.py` | `editor_service.py` |
| `help_manager.py` | `help_service.py` |
| `history_manager.py` | `history_service.py` |
| `menu_manager.py` | `menu_service.py` |
| `mission_manager.py` | `mission_service.py` |
| `memory_manager.py` | `memory_service.py` |
| `resource_manager.py` | `resource_service.py` |
| `role_manager.py` | `role_service.py` |
| `state_manager.py` | `state_service.py` |
| `user_manager.py` | `user_service.py` |

**ALSO UPDATE:**
- `core/commands/__init__.py` — Lazy import references
- Any handler files importing these services
- Test files

---

### 2.3 Monitoring Services Consolidation (4 → 1)

**CONSOLIDATE INTO SINGLE FILE:**
- `core/services/device_monitor.py`
- `core/services/disk_monitor.py`
- `core/services/server_monitor.py`
- `core/services/api_monitor.py`

**RESULT:** `core/services/monitoring_service.py` with pluggable monitor classes

**RENAME:** All `*_monitor.py` → internal class in `monitoring_service.py`

---

### 2.4 Theme/Display System

**MERGE:**
- `core/services/dashboard_data_service.py` (340 LOC) → internal module of `dashboard_service.py`

**CLARIFY (AUDIT FIRST):**
- `core/services/display_mode_manager.py` (326 LOC) — Purpose unclear, possibly rename
- `core/services/theme_messenger.py` (249 LOC) — Purpose unclear, possibly consolidate

**KEEP:**
- `core/services/dashboard_service.py` (780 LOC) — Clear purpose, main dashboard service

---

## 🟡 TIER 3: ARCHITECTURE FILES

### 3.1 Logging System Monolith (AUDIT FIRST)

**CRITICAL ISSUE:** 40K+ LOC in logging system

**MISPLACED FILE:**
- `core/services/biological_factors.py` (15,500 LOC) — ❓ **Why is this in logging?** Should be moved to game/mood system or equivalent

**SPLIT:**
- `core/services/logging_manager.py` (17,800 LOC) **MONOLITH** — Split into:
  - `core/services/log_formatter.py` — Formatting logic
  - `core/services/log_rotation.py` — Rotation/cleanup
  - `core/services/log_aggregator.py` — Aggregation logic
  - `core/services/logging_manager.py` — Keep as coordinator

**CLARIFY (AUDIT FIRST):**
- `core/services/logger_compat.py` (4,900 LOC) — Compatibility with what? Keep or deprecate?
- `core/services/loglang_logger.py` (8,100 LOC) — Custom logging language? Experimental? Status?
- `core/services/log_compression.py` (12,700 LOC) — Keep as-is or integrate into log_rotation?

**ACTION:**
Research and document current usage before splitting. High risk of breaking changes.

---

### 3.2 Extension System (REVIEW ARCHITECTURE)

**FILES:**
- `core/services/extension_lifecycle.py` (458 LOC)
- `core/services/extension_loader.py` (257 LOC)
- `core/services/extension_manager.py` (673 LOC)
- `core/services/extension_monitor.py` (284 LOC)
- `core/services/extension_registry.py` (481 LOC)

**ISSUE:** Unclear tier structure. Is this Registry→Loader→Manager→Lifecycle? Or fragmented?

**ACTION:** Architecture review to clarify and possibly consolidate to 3-4 files.

---

### 3.3 Handler Misplacement (MOVE 3 FILES)

**MOVE TO `core/ui/`:**
- `core/commands/keypad_demo_handler.py` → `core/ui/keypad_demo.py` (This is UI, not command)
- `core/commands/selector_handler.py` → `core/ui/selector_framework.py` (This is UI, not command)
- `core/commands/tui_handler.py` → `core/ui/tui_controller.py` (This is UI, not command)

**UPDATE IMPORTS:**
- `core/tui/dispatcher.py`
- `core/commands/__init__.py`
- Test files

---

## 🟢 TIER 4: POLISH

### 4.1 Archive Directories

**REVIEW CONTENTS:**
- `core/.archive/`
- `core/.archive/data/`
- `core/.archive/data/.archive/`
- `core/.archive/data/geography/.archive/`

**ACTION:**
Review old code, keep useful patterns, delete obsolete files.

---

### 4.2 TODOs & FIXMEs

**FOUND:**
- `core/tui/ucode.py` — TODO: Real packaging logic
- `core/commands/talk_handler.py` — TODO: Get from game state (5+ instances)

**ACTION:**
Create tickets for each TODO, add to sprint backlog.

---

## 📊 File Statistics

### By Type

**Graphics Files:** 9 files, 2.1K LOC
```
graphics_service.py ✅
graphics_library.py ⚠️
graphics_compositor.py ⚠️
diagram_compositor.py 🔴 DELETE
diagram_generator.py ⚠️
draw_handler.py ⚠️
output/graphics.py 🔴 DELETE (deprecated)
ui/block_graphics.py ❓
feed/feed_renderer.py ❓
```

**Error Handling Files:** 6 files, 2.6K LOC
```
error_handler.py 🔴
error_intelligence.py ⚠️
error_interceptor.py ⚠️
intelligent_error_handler.py 🔴 DUPLICATE
debug_engine.py ⚠️
debug_panel_service.py ✅ KEEP
```

**Manager Files:** 15+ files (all to be renamed `_service.py`)

**Monitoring Files:** 4 files (to consolidate)

**Logging Files:** 5 files, 40K+ LOC
```
logging_manager.py 🔴 MONOLITH
logger_compat.py ⚠️
loglang_logger.py ⚠️
log_compression.py ✅
biological_factors.py ❓ WRONG PLACE
```

**Extension Files:** 5 files, 2.7K LOC (review architecture)

**Handler Misplacements:** 3 files (move to ui/)

---

## ✅ Clean Systems (NO ACTION)

```
✅ core/version.py — Version management (3 files, clean)
✅ core/binder/ — Config system (well-organized)
✅ core/commands/base.py — Base handler pattern (excellent)
✅ core/services/identity_encryption.py — Transport/security (clear)
✅ knowledge/ — Knowledge bank (modular)
✅ core/services/graphics_service.py — Graphics bridge (focused)
```

---

## 🎯 Next Steps

1. **Confirm** file manifest with team
2. **Start** TIER 1 files (graphics, OK handler, deprecation)
3. **Create** GitHub issues for each file change
4. **Track** progress in project board
5. **Review** TIER 2 findings before proceeding

---

**Manifest Created:** 2026-01-31  
**Audit Source:** Full core/ directory analysis  
**Related:** [CORE-CLEANUP-PRIORITY-LIST.md](CORE-CLEANUP-PRIORITY-LIST.md)

