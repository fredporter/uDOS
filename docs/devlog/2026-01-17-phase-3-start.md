# Phase 3 Launch: Binder System Integration

**Date:** 2026-01-17  
**Status:** 🚀 LAUNCHED  
**Theme:** Offline-first document isolation + local database + content syndication

---

## 📋 Context

**What Completed:**

- Phase 2: Full file parsing system (CSV/TSV, JSON/JSONL, YAML/TOML, SQL, Export)
- 183+ test cases, 95%+ coverage across all parsers
- Markdown table import/export with metadata preservation

**What's Next:**

- Binder folder isolation (MyBinder/ with local database)
- Database context system for relative file access
- RSS feed generation from markdown content
- uDOS language registration in VS Code
- Release prep for v1.0.6.0

---

## 🎯 Phase 3 Architecture

### Binder Model

**Folder Structure:**

```
MyBinder/
  binder.md              # Optional binder home/metadata
  uDOS-table.db          # Local SQLite database
  imports/               # CSV, JSON, YAML sources
    contacts.csv
    config.yaml
  tables/                # Exported .table.md files
    contacts.table.md
  scripts/               # .script.md executables
    analysis.script.md
  data/                  # User data, logs, cache
  .binder-config         # Metadata (name, version, created_at)
```

### Database Context

**Scope Rules:**

- Each binder has isolated `uDOS-table.db` (local, encrypted optional)
- Relative references: `memory/binders/MyBinder/` is root context
- Can import from `imports/` folder (shared/external sources)
- Can export/read tables within binder scope
- Cross-binder access: requires explicit path (security boundary)

### RSS Generation

**Sources:**

- Scan all `.md` files in binder
- Extract frontmatter (title, author, date)
- Generate feed with latest 20 entries
- Include content preview (first 200 chars)
- Output: `MyBinder/feed.xml` (public feed)

### Language Registration

**uDOS Grammar:**

- Register with VS Code extension system
- Syntax highlighting for runtime blocks:
  - `state $var = ...` (blue)
  - `set $var to ...` (purple)
  - `form { fields }` (orange)
  - `if condition { ... }` (red)
- Snippet support for quick block insertion
- Inline variable interpolation highlighting

---

## 📊 Task Breakdown

### Task 7: Binder Structure (This Session)

**Deliverables:**

- `core/binder/` module (empty scaffold)
- `BinderConfig` dataclass (metadata)
- `BinderValidator` (folder structure checking)
- Documentation: binder design spec
- Tests: validation, config loading

**Files:**

- `core/binder/__init__.py` - Module exports
- `core/binder/config.py` - BinderConfig + loader
- `core/binder/validator.py` - Folder structure validation
- `core/tests/test_binder_config_v1_0_6.py` - 12+ tests

**Acceptance Criteria:**

- ✅ Create BinderConfig from folder
- ✅ Validate folder structure
- ✅ Load/save metadata
- ✅ Handle missing optional files
- ✅ Support nested binder discovery

---

### Task 8: Database Context (Next Session)

**Deliverables:**

- `BinderDatabase` class (context manager)
- Relative path resolution
- Cross-binder access control
- Query execution within scope
- Connection pooling

**Files:**

- `core/binder/database.py`
- `core/tests/test_binder_database_v1_0_6.py`

---

### Task 9: RSS Feed (Following Session)

**Deliverables:**

- `BinderFeed` class (generation + caching)
- Frontmatter extraction from markdown
- Feed entry sorting (by date, modified)
- XML generation (RSS 2.0 spec)
- FEED handler integration

**Files:**

- `core/binder/feed.py`
- `core/tests/test_binder_feed_v1_0_6.py`

---

### Task 10: Language Registration (Final Session)

**Deliverables:**

- VS Code extension grammar definition
- `syntaxes/udos.json` (TextMate grammar)
- `snippets/udos.json` (quick insert)
- Documentation for maintainers

**Files:**

- `extensions/vscode/syntaxes/udos.json`
- `extensions/vscode/snippets/udos.json`
- Update `extensions/vscode/package.json`

---

## 🏗️ Implementation Plan

**Today (Task 7):**

1. **Create binder module structure**

   - `core/binder/__init__.py` (exports)
   - `core/binder/config.py` (metadata dataclass)
   - `core/binder/validator.py` (validation logic)

2. **BinderConfig (25 lines)**

   ```python
   @dataclass
   class BinderConfig:
       name: str
       version: str
       created_at: datetime
       author: Optional[str] = None
       description: Optional[str] = None
       tags: List[str] = field(default_factory=list)
   ```

3. **BinderValidator (80 lines)**

   - Check folder structure
   - Validate required files
   - Handle optional files gracefully
   - Return validation report

4. **Test Suite (200+ lines)**

   - Valid folder structure
   - Missing folders
   - Missing metadata file
   - Nested binder discovery
   - Edge cases

5. **Documentation**
   - Binder design specification
   - API reference
   - Usage examples

---

## 🔗 Related Files

- Phase 2 Complete: `/docs/V1.0.6.0-PHASE-2-COMPLETE.md`
- Roadmap: `/docs/roadmap.md` (updated with Phase 3)
- Devlog Index: `/docs/devlog/` (this session)

---

## 📌 Key Decisions

1. **Database per Binder** - Not shared pools (isolation first)
2. **Folder-Based Structure** - Not virtual (portable, git-friendly)
3. **Optional Config File** - Infer from structure if missing
4. **RSS as Feed, Not API** - Static files for simplicity
5. **VS Code Grammar** - TextMate format (standard, maintainable)

---

## ✅ Acceptance Criteria (Phase 3 Complete)

- [ ] Binder folder structure validated
- [ ] Database context system operational
- [ ] RSS feeds generating correctly
- [ ] VS Code grammar registered
- [ ] 40+ new tests passing (binder-specific)
- [ ] Comprehensive documentation
- [ ] v1.0.6.0 released

---

**Next Update:** After Task 7 completion (Binder structure)  
**ETA:** 2-3 hours for full implementation
