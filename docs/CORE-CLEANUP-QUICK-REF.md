# Core Cleanup — Quick Reference

**Last Updated:** 2026-01-31

## 🔴 CRITICAL (Do First)

### 1️⃣ Graphics Duplication — 2.1K LOC
```
DELETE: core/services/diagram_compositor.py (duplicate)
KEEP:   core/services/graphics_compositor.py (primary)
FIX:    Verify diagram_generator.py doesn't overlap
AUDIT:  draw_handler.py, block_graphics.py, feed_renderer.py
REMOVE: core/output/graphics.py (deprecated)
```

### 2️⃣ OK Handler Split — 1.4K LOC
```
MERGE: core/commands/okfix_handler.py → ok_handler.py (OK FIX subcommand)
MERGE: core/services/ok_context_builder.py → ok_context_manager.py
KEEP:  core/services/ok_config.py (separate)
```

### 3️⃣ Dead Code — 534 LOC
```
DELETE: core/output/graphics.py (Phase 1 deprecation complete)
```

---

## 🟠 IMPORTANT (Do Next)

### 4️⃣ Error Handling — 2.6K LOC, 5 files
```
AUDIT FIRST: error_handler.py, error_intelligence.py, error_interceptor.py,
             intelligent_error_handler.py, debug_engine.py

CONSOLIDATE: Too many overlapping solutions, needs architecture review
RESULT:      Should be 2-3 files max
```

### 5️⃣ Naming Standardization — 15+ files
```
RENAME ALL: *_manager.py → *_service.py
  asset_manager.py → asset_service.py
  checkpoint_manager.py → checkpoint_service.py
  device_manager.py → device_service.py
  ... (15+ more)
```

### 6️⃣ Monitoring Services — 4 files
```
CONSOLIDATE:
  device_monitor.py
  disk_monitor.py
  server_monitor.py
  api_monitor.py
  
RESULT: single monitoring_service.py with pluggable monitors
```

### 7️⃣ Theme/Display — 1.7K LOC
```
MERGE:    dashboard_data_service.py → internal module of dashboard_service.py
CLARIFY:  display_mode_manager.py (what is "display mode"?)
CLARIFY:  theme_messenger.py (what does "messenger" do?)
```

---

## 🟡 ARCHITECTURE (Medium-term)

### 8️⃣ Logging Monolith — 40K+ LOC
```
PROBLEM: logging_manager.py is 17.8K lines!
ACTION:  
  - MOVE biological_factors.py (not logging system!)
  - SPLIT logging_manager.py into:
    • log_formatter.py
    • log_rotation.py  
    • log_aggregator.py
    • log_manager.py (coordinator)
  - CLARIFY/DEPRECATE logger_compat.py, loglang_logger.py
```

### 9️⃣ Extension System — 2.7K LOC, 5 files
```
REVIEW: extension_lifecycle, extension_loader, extension_manager,
        extension_monitor, extension_registry

DESIGN: Clear tier architecture (Registry→Loader→Manager→Monitor)
CONSOLIDATE: Maybe to 3 files
```

### 🔟 Handler Misplacement — Organization
```
MOVE TO ui/:
  commands/keypad_demo_handler.py → ui/keypad_demo.py
  commands/selector_handler.py → ui/selector_framework.py
  commands/tui_handler.py → ui/tui_controller.py

DOCUMENT: Handler categories (navigation, game_state, system, npc, wizard)
```

---

## ✅ NO CLEANUP NEEDED

```
✅ Version Management (core/version.py) — Clean, simple
✅ Config System — Well-organized
✅ Base Handler Pattern — Excellent foundation
✅ Transport/Security — Clear boundaries
✅ Knowledge Bank — Modular structure
✅ Graphics Service Bridge — Single focused purpose
```

---

## 📊 By The Numbers

| Category | Count | Status | Action |
|----------|-------|--------|--------|
| **Duplicate graphics files** | 2 | 🔴 Critical | DELETE diagram_compositor.py |
| **OK handler fragmentation** | 5 files | 🔴 Critical | MERGE okfix + context_builder |
| **Error handling implementations** | 5 | 🟠 Important | CONSOLIDATE to 2-3 |
| **Manager/Service inconsistency** | 15+ | 🟠 Important | RENAME to _service.py |
| **Monitoring services** | 4 | 🟠 Important | CONSOLIDATE to 1 |
| **Logging monolith LOC** | 17,800 | 🟡 Architecture | SPLIT into 4 files |
| **Handler misplacement** | 3 | 🟡 Architecture | MOVE to ui/ |
| **Extension system fragmentation** | 5 files | 🟡 Architecture | REVIEW tiers |

---

## 🎯 Implementation Timeline

```
WEEK 1 (Immediate)
├─ Graphics cleanup (4-6h)
├─ OK handler consolidation (3-4h)  
└─ Deprecation cleanup (1-2h)
    └─ Impact: 4K LOC removed, critical systems unified

WEEK 2 (Next)
├─ Error handling audit (6-8h)
├─ Manager renaming (2-3h)
├─ Monitoring consolidation (4-5h)
└─ Theme/display clarification (3-4h)
    └─ Impact: 3.8K LOC removed, naming consistency

WEEK 3+ (Longer-term)
├─ Logging refactoring (10-15h)
├─ Extension architecture (8-10h)
└─ Handler migration (5-7h)
    └─ Impact: 40K+ LOC refactored, clear boundaries
```

---

## 📋 Start Here

1. **READ:** [CORE-CLEANUP-PRIORITY-LIST.md](CORE-CLEANUP-PRIORITY-LIST.md) (full details)
2. **START:** Graphics duplication cleanup (1.1)
3. **THEN:** OK handler consolidation (1.2)
4. **FINALLY:** Deprecation cleanup (1.3)

---

*See [CORE-CLEANUP-PRIORITY-LIST.md](CORE-CLEANUP-PRIORITY-LIST.md) for detailed analysis, file paths, and implementation guidance.*

