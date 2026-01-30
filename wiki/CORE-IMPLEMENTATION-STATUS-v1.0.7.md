# Core Implementation Status — v1.0.7.0

**Version:** 1.0.7.0
**Status Check Date:** 2026-01-30
**Validated Against:** [CORE-CAPABILITIES-v1.0.7.md](CORE-CAPABILITIES-v1.0.7.md)

This document tracks implementation status of all features documented in the v1.0.7 Core Capabilities Reference against actual code in the repository.

---

## Summary

| Feature Area | Status | Notes |
|-------------|---------|-------|
| Binder System | ⚠️ **Partial** | PDF/Brief still present (needs removal) |
| Markdown & Frontmatter | ✅ **Complete** | All features implemented |
| Database Operations | ✅ **Complete** | All parsers present |
| File Handling | ✅ **Complete** | CLEAN/TIDY/COMPOST implemented |
| **Publication Workflow** | ❌ **MISSING** | Not implemented |
| Map & Grid Rendering | ✅ **Complete** | MAP command functional |
| Teletext Graphics | ✅ **Complete** | Full fallback chain |
| Pattern Generation | ✅ **Complete** | 6 patterns available |
| **Diagram System** | ❌ **MISSING** | Not implemented |
| Seed-Bank Management | ✅ **Complete** | SEED command functional |
| Workspace System | ⚠️ **Partial** | Missing @public workspace & GHOST role |

**Overall Status:** 📊 **7/11 Complete, 2/11 Partial, 2/11 Missing**

---

## Detailed Implementation Status

### 1. Binder System ⚠️ **Partial**

**Module:** `core/binder/`

**Implemented:**
- ✅ Multi-format compilation
- ✅ SQLite database per binder
- ✅ Metadata management (.binder-config)
- ✅ Structure validation
- ✅ RSS/JSON feed generation
- ✅ F4 key integration
- ✅ TUI commands (BINDER, BINDER COMPILE, BINDER CHAPTERS)

**Issues:**
- ⚠️ **PDF compilation still present** (should be removed per spec)
- ⚠️ **Dev brief format still present** (should be removed per spec)
- ⚠️ **TXT format not explicitly supported** (spec requires MD/JSON/TXT only)

**Files:**
- `core/binder/compiler.py` — Lines 83-92 have PDF and brief compilation
- `core/commands/binder_handler.py` — Working correctly

**Required Changes:**
```python
# In compiler.py, remove these sections:
if "pdf" in formats:  # REMOVE
if "brief" in formats:  # REMOVE

# Add:
if "txt" in formats:  # ADD
    txt_output = await self._compile_txt(binder_id, chapters)
```

**Shakedown Test:** ❌ Not covered

---

### 2. Markdown & Frontmatter ✅ **Complete**

**Module:** `core/services/markdown_frontmatter.py`, `core/parsers/markdown_table_parser.py`

**Implemented:**
- ✅ YAML frontmatter parsing
- ✅ Validation with required keys
- ✅ Default fallbacks
- ✅ `.table.md` format with schema
- ✅ SQLite type mapping
- ✅ All standard fields (title, description, tags, grid_locations, binder_id, etc.)

**Files:**
- `core/services/markdown_frontmatter.py` — Complete implementation
- `core/parsers/markdown_table_parser.py` — Complete with frontmatter support

**Shakedown Test:** ✅ Indirectly tested via locations

---

### 3. Database Operations ✅ **Complete**

**Module:** `core/binder/database.py`, `core/parsers/`

**Implemented:**
- ✅ Context-managed connections
- ✅ Access modes (READ_ONLY, READ_WRITE, FULL)
- ✅ Query scoping
- ✅ CSV/TSV import with auto-detection
- ✅ Type inference
- ✅ Table export (multiple formats)
- ✅ SQL script execution with safety

**Files:**
- `core/binder/database.py` — Complete with context manager
- `core/parsers/csv_tsv_importer.py` — Full auto-detection
- `core/parsers/table_exporter.py` — Multiple format support
- `core/parsers/sql_executor.py` — Safety constraints implemented

**Issues:**
- ⚠️ **SQL execution location** — Spec says "execute in /memory/sandbox" but implementation doesn't enforce this

**Shakedown Test:** ❌ Not covered

---

### 4. File Handling & Maintenance ✅ **Complete**

**Module:** `core/services/maintenance_utils.py`

**Implemented:**
- ✅ `tidy()` — Move junk to .archive
- ✅ `clean()` — Reset to defaults
- ✅ `compost()` — Archive old archives
- ✅ Junk pattern detection
- ✅ TUI commands (REPAIR TIDY, REPAIR CLEAN, REPAIR COMPOST)

**Files:**
- `core/services/maintenance_utils.py` — Lines 157-278
- `core/commands/repair_handler.py` — Command integration

**Shakedown Test:** ❌ Not covered

---

### 5. Publication Workflow ❌ **MISSING — PRIORITY 1**

**Status:** NOT IMPLEMENTED

**Required Files:**
- ❌ `core/commands/publish_handler.py` — Does not exist
- ❌ `core/services/publication_service.py` — Does not exist
- ❌ `memory/public/.submissions/` — Directory does not exist

**Required Commands:**
- ❌ `PUBLISH <source> <dest> [--submit]`
- ❌ `PUBLISH BINDER <id> <dest> [--submit]`
- ❌ `PUBLISH STATUS <path>`
- ❌ `PUBLISH VALIDATE <path>`
- ❌ `PUBLISH LIST --pending`

**Required Features:**
- ❌ Document lifecycle management
- ❌ Validation rules (frontmatter, links, formatting)
- ❌ Wiki submission system
- ❌ Admin review workflow

**Shakedown Test:** ❌ Not covered (feature missing)

**Implementation Estimate:** 8-12 hours

---

### 6. Map & Grid Rendering ✅ **Complete**

**Module:** `core/services/map_renderer.py`, `core/commands/map_handler.py`

**Implemented:**
- ✅ 80×30 and 40×15 viewports
- ✅ Layer bands (SUR L300-305, UDN L294-299)
- ✅ Cell addressing (AA10-DC39)
- ✅ ASCII grid output
- ✅ Legend generation
- ✅ MAP and PANEL commands

**Files:**
- `core/services/map_renderer.py` — Complete implementation
- `core/commands/map_handler.py` — TUI integration
- `core/grid-runtime/src/map-panel-parser.ts` — Markdown block support

**Issues:**
- ⚠️ **Layer frontmatter** — `.layer.md` format not implemented (Priority 2)

**Shakedown Test:** ✅ Locations check validates map system

---

### 7. Teletext Block Graphics ✅ **Complete**

**Module:** `core/grid-runtime/src/teletext-renderer.ts` (renamed from sextant)

**Implemented:**
- ✅ TELETEXT (64 chars, 2×3 pixels)
- ✅ BLOCK (16 chars, 2×2 pixels)
- ✅ SHADE (5 chars, density)
- ✅ ASCII (5 chars, text-only)
- ✅ Fallback chain: TELETEXT → BLOCK → SHADE → ASCII
- ✅ Terminal detection
- ✅ Quality options in map blocks

**Files:**
- `core/grid-runtime/src/sextant-renderer.ts` — **NEEDS RENAME** to `teletext-renderer.ts`
- `core/grid-runtime/src/sextant-lookup.py` — **NEEDS RENAME** to `teletext-lookup.py`
- `core/grid-runtime/__tests__/sextant-renderer.test.ts` — Tests present

**Issues:**
- ⚠️ **Terminology outdated** — Files still use "sextant" naming (should be "teletext")
- ⚠️ **Quality enum** — Uses SEXTANT instead of TELETEXT

**Required Renames:**
```bash
# Rename files
mv sextant-renderer.ts teletext-renderer.ts
mv sextant-lookup.py teletext-lookup.py
mv __tests__/sextant-renderer.test.ts __tests__/teletext-renderer.test.ts

# Update enum in code
export enum RenderQuality {
  TELETEXT = 'teletext',   // Was: SEXTANT
  BLOCK = 'block',         // Was: QUADRANT
  SHADE = 'shade',
  ASCII = 'ascii',
}
```

**Shakedown Test:** ❌ Not covered

---

### 8. Pattern Generation ✅ **Complete**

**Module:** `core/services/pattern_generator.py`, `core/commands/pattern_handler.py`

**Implemented:**
- ✅ 6 pattern types (C64, chevrons, scanlines, raster, progress, mosaic)
- ✅ TUI commands (PATTERN, PATTERN <name>, PATTERN CYCLE, PATTERN TEXT)
- ✅ ASCII-only mode support
- ✅ 16-color ANSI palette
- ✅ Terminal width/height detection

**Files:**
- `core/services/pattern_generator.py` — 458 lines, complete
- `core/commands/pattern_handler.py` — TUI integration

**Shakedown Test:** ❌ Not covered

---

### 9. Diagram System ❌ **MISSING — PRIORITY 3**

**Status:** NOT IMPLEMENTED

**Required Files:**
- ❌ `core/parsers/diagram_parser.py` — Does not exist
- ❌ `core/services/diagram_renderer.py` — Does not exist
- ❌ `core/commands/diagram_handler.py` — Does not exist

**Required Features:**
- ❌ `.diagram.md` format parser
- ❌ ASCII flowchart renderer
- ❌ TELETEXT block renderer (32-color)
- ❌ Logic step parser
- ❌ TUI command: `DIAGRAM RENDER <file>`

**Specification:** See [Section 9: Diagram System](CORE-CAPABILITIES-v1.0.7.md#9-diagram-system)

**Shakedown Test:** ❌ Not covered (feature missing)

**Implementation Estimate:** 12-16 hours

---

### 10. Seed-Bank Management ✅ **Complete**

**Module:** `core/framework/seed_installer.py`, `core/commands/seed_handler.py`

**Implemented:**
- ✅ Framework seed data (locations, timezones, help, graphics, templates)
- ✅ Automatic bootstrap on first run
- ✅ TUI commands (SEED, SEED INSTALL, SEED STATUS)
- ✅ Directory structure creation
- ✅ 115 seed files

**Files:**
- `core/framework/seed_installer.py` — Complete implementation
- `core/commands/seed_handler.py` — TUI integration
- `core/framework/seed/` — Seed data present

**Shakedown Test:** ✅ Partial (checks directories, not full seed validation)

---

### 11. Workspace System ⚠️ **Partial**

**Module:** `core/services/spatial_filesystem.py`

**Implemented:**
- ✅ @sandbox, @bank, @shared workspaces
- ✅ Role-based access (ADMIN, USER)
- ✅ Grid location tagging
- ✅ Content discovery by tags
- ✅ Frontmatter management

**Issues:**
- ❌ **@public workspace missing** (spec requires @sandbox, @bank, @public, @shared)
- ❌ **GHOST role missing** (spec requires ADMIN, USER, GHOST — no GUEST)
- ⚠️ **WorkspaceType enum** has WIZARD, KNOWLEDGE, DEV (should be removed per spec)

**Current Workspaces in Code:**
```python
class WorkspaceType(Enum):
    SANDBOX = 'sandbox'    # ✅ Correct
    BANK = 'bank'          # ✅ Correct
    SHARED = 'shared'      # ✅ Correct
    WIZARD = 'wizard'      # ❌ Should be removed
    KNOWLEDGE = 'knowledge' # ❌ Should be removed
    DEV = 'dev'            # ❌ Should be removed
    # PUBLIC missing        # ❌ Should be added
```

**Required Changes:**
```python
class WorkspaceType(Enum):
    SANDBOX = 'sandbox'
    BANK = 'bank'
    PUBLIC = 'public'   # ADD
    SHARED = 'shared'
    # Remove: WIZARD, KNOWLEDGE, DEV

class UserRole(Enum):
    ADMIN = 'admin'
    USER = 'user'
    GHOST = 'ghost'     # ADD (replaces GUEST)
```

**Shakedown Test:** ✅ Partial (checks directories, not workspace types)

---

## Shakedown Test Coverage

**Current Shakedown Checks:** (from `core/commands/shakedown_handler.py`)

1. ✅ Framework initialization
2. ✅ Component registration
3. ✅ Locations database
4. ✅ Core command registration
5. ✅ Memory directories
6. ✅ TypeScript runtime
7. ✅ Handler modules
8. ✅ Services layer
9. ✅ User manager

**Additional Flags:**
- `--fresh` — Fresh install validation (9 checks)
- `--destroy-verify` — DESTROY command verification (8 checks)

**Missing Coverage:**
- ❌ Binder compilation (formats check)
- ❌ Database operations (import/export)
- ❌ File handling (TIDY/CLEAN/COMPOST)
- ❌ Publication workflow (not implemented)
- ❌ Map rendering quality
- ❌ Teletext graphics fallback
- ❌ Pattern generation
- ❌ Diagram rendering (not implemented)
- ❌ Seed validation (seed file integrity)
- ❌ Workspace type validation

---

## Required Shakedown Enhancements

Add these checks to `core/commands/shakedown_handler.py`:

### Check 10: Binder Formats
```python
def _check_binder_formats(self) -> Dict:
    """Verify binder supports MD/JSON/TXT only (not PDF/Brief)."""
    try:
        from core.binder.compiler import BinderCompiler
        compiler = BinderCompiler()

        # Check default formats
        formats = compiler.formats
        invalid = [f for f in formats if f in ['pdf', 'brief']]
        valid = [f for f in formats if f in ['markdown', 'json', 'txt']]

        if invalid:
            return {
                "status": "fail",
                "message": f"Invalid formats present: {invalid} (spec: MD/JSON/TXT only)"
            }

        return {
            "status": "pass",
            "message": f"Binder formats: {', '.join(valid)}",
            "count": len(valid)
        }
    except Exception as e:
        return {"status": "fail", "message": f"Binder format check failed: {e}"}
```

### Check 11: Workspace Types
```python
def _check_workspace_types(self) -> Dict:
    """Verify workspace types match spec (@sandbox, @bank, @public, @shared)."""
    try:
        from core.services.spatial_filesystem import WorkspaceType

        required = {'SANDBOX', 'BANK', 'PUBLIC', 'SHARED'}
        invalid = {'WIZARD', 'KNOWLEDGE', 'DEV'}

        actual = set(w.name for w in WorkspaceType)

        missing = required - actual
        extra = actual & invalid

        if missing or extra:
            issues = []
            if missing:
                issues.append(f"missing: {missing}")
            if extra:
                issues.append(f"invalid: {extra}")
            return {
                "status": "fail",
                "message": f"Workspace types mismatch: {', '.join(issues)}"
            }

        return {
            "status": "pass",
            "message": "Workspace types: @sandbox, @bank, @public, @shared",
            "count": 4
        }
    except Exception as e:
        return {"status": "fail", "message": f"Workspace check failed: {e}"}
```

### Check 12: User Roles
```python
def _check_user_roles(self) -> Dict:
    """Verify user roles match spec (ADMIN, USER, GHOST)."""
    try:
        from core.services.spatial_filesystem import UserRole

        required = {'ADMIN', 'USER', 'GHOST'}
        invalid = {'GUEST'}

        actual = set(r.name for r in UserRole)

        missing = required - actual
        extra = actual & invalid

        if missing or extra:
            issues = []
            if missing:
                issues.append(f"missing: {missing}")
            if extra:
                issues.append(f"invalid: {extra}")
            return {
                "status": "fail",
                "message": f"User roles mismatch: {', '.join(issues)}"
            }

        return {
            "status": "pass",
            "message": "User roles: ADMIN, USER, GHOST",
            "count": 3
        }
    except Exception as e:
        return {"status": "fail", "message": f"Role check failed: {e}"}
```

### Check 13: Teletext Graphics
```python
def _check_teletext_graphics(self) -> Dict:
    """Verify TELETEXT graphics (renamed from sextant) with fallback chain."""
    try:
        # Check if file exists (may need rename)
        renderer_path = PROJECT_ROOT / "core" / "grid-runtime" / "src" / "teletext-renderer.ts"
        old_path = PROJECT_ROOT / "core" / "grid-runtime" / "src" / "sextant-renderer.ts"

        if not renderer_path.exists() and old_path.exists():
            return {
                "status": "warning",
                "message": "Graphics renderer found but uses outdated 'sextant' naming (should be 'teletext')"
            }

        if renderer_path.exists():
            # TODO: Check for RenderQuality.TELETEXT enum
            return {
                "status": "pass",
                "message": "Teletext graphics: TELETEXT→BLOCK→SHADE→ASCII"
            }

        return {
            "status": "fail",
            "message": "Teletext graphics renderer not found"
        }
    except Exception as e:
        return {"status": "fail", "message": f"Graphics check failed: {e}"}
```

### Check 14: Publication System
```python
def _check_publication_system(self) -> Dict:
    """Verify PUBLISH command and publication workflow (Priority 1)."""
    try:
        publish_handler = PROJECT_ROOT / "core" / "commands" / "publish_handler.py"
        public_dir = PROJECT_ROOT / "memory" / "public"
        submissions_dir = public_dir / ".submissions"

        checks = {
            "handler": publish_handler.exists(),
            "public_dir": public_dir.exists(),
            "submissions": submissions_dir.exists()
        }

        if not any(checks.values()):
            return {
                "status": "fail",
                "message": "Publication system NOT IMPLEMENTED (Priority 1)"
            }

        missing = [k for k, v in checks.items() if not v]
        if missing:
            return {
                "status": "warning",
                "message": f"Publication system incomplete: missing {', '.join(missing)}"
            }

        return {
            "status": "pass",
            "message": "Publication system: PUBLISH command ready"
        }
    except Exception as e:
        return {"status": "fail", "message": f"Publication check failed: {e}"}
```

### Check 15: Diagram System
```python
def _check_diagram_system(self) -> Dict:
    """Verify diagram rendering system (Priority 3)."""
    try:
        diagram_parser = PROJECT_ROOT / "core" / "parsers" / "diagram_parser.py"
        diagram_renderer = PROJECT_ROOT / "core" / "services" / "diagram_renderer.py"
        diagram_handler = PROJECT_ROOT / "core" / "commands" / "diagram_handler.py"

        exists = [
            diagram_parser.exists(),
            diagram_renderer.exists(),
            diagram_handler.exists()
        ]

        if not any(exists):
            return {
                "status": "warning",
                "message": "Diagram system NOT IMPLEMENTED (Priority 3 — planned)"
            }

        count = sum(exists)
        if count < 3:
            return {
                "status": "warning",
                "message": f"Diagram system incomplete: {count}/3 modules present"
            }

        return {
            "status": "pass",
            "message": "Diagram system: .diagram.md flowcharts ready"
        }
    except Exception as e:
        return {"status": "fail", "message": f"Diagram check failed: {e}"}
```

---

## Action Items

### Immediate (Priority 1)

1. **Implement PUBLISH Command** ❌
   - Create `core/commands/publish_handler.py`
   - Create `core/services/publication_service.py`
   - Create `memory/public/` directory
   - Add validation logic
   - Add TUI commands

2. **Fix Binder Formats** ⚠️
   - Remove PDF compilation from `compiler.py`
   - Remove dev brief compilation
   - Add TXT format support
   - Update default formats list

3. **Fix Workspace Types** ⚠️
   - Add PUBLIC workspace to `spatial_filesystem.py`
   - Remove WIZARD, KNOWLEDGE, DEV workspaces
   - Add GHOST role
   - Remove GUEST role

### Short-term (Priority 2)

4. **Implement Layer Markdown Format** ❌
   - Create `.layer.md` parser
   - Add frontmatter support for layers
   - Update map rendering to use layer metadata

5. **Rename Teletext Graphics** ⚠️
   - Rename all "sextant" files to "teletext"
   - Update RenderQuality enum
   - Update documentation references
   - Update tests

6. **Enhance Shakedown Tests** ⚠️
   - Add Checks 10-15 above
   - Test binder formats
   - Test workspace types
   - Test publication system
   - Test diagram system

### Medium-term (Priority 3)

7. **Implement Diagram System** ❌
   - Create diagram parser
   - Create ASCII renderer
   - Create TELETEXT renderer
   - Add TUI commands
   - Add tests

8. **Enforce SQL Sandbox Execution** ⚠️
   - Update `sql_executor.py` to check execution path
   - Restrict to `/memory/sandbox` only
   - Add path validation

---

## Testing Strategy

### Unit Tests Needed

1. **Binder Compiler**
   - Test MD/JSON/TXT compilation
   - Verify PDF/Brief removed
   - Test single-format output

2. **Workspace System**
   - Test @public workspace
   - Test GHOST role permissions
   - Verify removed workspaces fail

3. **Publication System** (when implemented)
   - Test document validation
   - Test promotion workflow
   - Test submission queue

4. **Diagram System** (when implemented)
   - Test `.diagram.md` parsing
   - Test ASCII rendering
   - Test TELETEXT rendering

### Integration Tests Needed

1. **Publication Workflow**
   - Sandbox → Bank → Public pipeline
   - Validation failures
   - Admin review process

2. **Diagram Rendering**
   - Flowchart → ASCII conversion
   - TELETEXT color application
   - Fallback chain

### Shakedown Expansion

Add all checks listed in "Required Shakedown Enhancements" section.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.7.0 | 2026-01-30 | Initial implementation status tracking |

---

## See Also

- [CORE-CAPABILITIES-v1.0.7.md](CORE-CAPABILITIES-v1.0.7.md) — Feature specifications
- `core/commands/shakedown_handler.py` — Current shakedown implementation
- [AGENTS.md](../AGENTS.md) — Development guidelines

---

**End of Document**
