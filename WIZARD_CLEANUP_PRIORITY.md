# Wizard Cleanup Priority List

**Analysis Date:** January 31, 2026
**Scope:** `/wizard/` directory
**Status:** Identified code duplication, relics, and redundant implementations

---

## Executive Summary

The Wizard codebase has accumulated **technical debt** from parallel development efforts, scaffolding, and service evolution. Key issues:
- **Port management** has 4 files with overlapping functionality (936 LOC total)
- **OAuth** has conflicting implementations (919 LOC, v0.1.0 stub + full v1.0.0 manager)
- **GitHub integration** has 3 separate services (730 LOC) with potential overlap
- **Migration stubs** (143 LOC) from Goblin-to-Wizard transition are incomplete and unused
- **Dashboard backup** file (`app.css.bak`) and **secrets backup** from 2026-01-28
- **Routes location mismatch** - `migration_routes.py` in services/ instead of routes/
- **Notification history** - duplicated setup between routes and services

---

## HIGH PRIORITY (Block Other Work)

### 1. **Port Manager Consolidation** ⚠️ CRITICAL
**Files:**
- `/wizard/cli_port_manager.py` (231 LOC) - CLI wrapper
- `/wizard/launch_with_port_manager.py` - Entrypoint launcher
- `/wizard/services/port_manager.py` (467 LOC) - Core implementation
- `/wizard/services/port_manager_service.py` (240 LOC) - API endpoints

**Issue:** Three separate implementations of port management functionality
- `cli_port_manager.py` wraps `port_manager.py`
- `port_manager_service.py` re-wraps it for FastAPI
- `launch_with_port_manager.py` is an alternate entry point

**Recommended Action:**
1. Keep `services/port_manager.py` as canonical core
2. Merge `port_manager_service.py` into main (integrate FastAPI routes)
3. Convert `cli_port_manager.py` to thin wrapper using port_manager module
4. Remove `launch_with_port_manager.py` - use `server.py` instead

**Impact:** ~400 LOC reduction, clearer architecture
**Effort:** 2-3 hours

---

### 2. **OAuth Handler Stub vs Manager Clash** ⚠️ CRITICAL
**Files:**
- `/wizard/services/oauth_handler.py` (219 LOC) - v0.1.0 stub
- `/wizard/services/oauth_manager.py` (702 LOC) - v1.0.0 production

**Issue:**
- `oauth_handler.py` marked "Status: v0.1.0.0 (stub)" - **incomplete/abandoned**
- Duplicate enum definitions (`OAuthProvider`, `OAuthToken`)
- `oauth_manager.py` is the real implementation (702 LOC, full feature set)
- Code paths diverge; unclear which to use

**Recommended Action:**
1. Review all imports of both files
2. Remove `oauth_handler.py` entirely (it's a stub)
3. Ensure `oauth_manager.py` covers all use cases
4. Update docstrings to clarify v1.0.0 is canonical

**Impact:** 219 LOC removed, decision clarity
**Effort:** 1 hour

---

### 3. **Migration Routes Relic** ⚠️ ARCHIVE/DELETE
**File:** `/wizard/services/migration_routes.py` (144 LOC)

**Issue:**
- Labeled "Goblin-to-Wizard migration route stubs"
- "These are scaffolds only; wire into `wizard/server.py` when ready"
- **No references found** - not imported or used anywhere
- Created during Goblin→Wizard transition; likely obsolete

**Recommended Action:**
1. Archive to `.archive/migration_routes_deprecated.py`
2. Remove from `/wizard/services/`
3. Document decision in DEVLOG

**Impact:** 144 LOC removed, cleaner services/
**Effort:** 30 min

---

## MEDIUM PRIORITY (Clean Up Architecture)

### 4. **GitHub Services Overlap**
**Files:**
- `/wizard/services/github_integration.py` (146 LOC)
- `/wizard/services/github_monitor.py` (287 LOC)
- `/wizard/services/github_sync.py` (174 LOC)
- `/wizard/routes/github_routes.py` (123 LOC)

**Issue:**
- Three separate services + routes (730 LOC total)
- Overlapping concerns:
  - `github_integration.py` - issue/PR fetching, devlog access
  - `github_sync.py` - push/pull/webhook handling
  - `github_monitor.py` - CI/Actions monitoring
- All have `_get_repo_name()` and repo path handling
- Unclear service boundaries

**Recommended Action:**
1. Audit actual usage (which functions called from routes?)
2. Consolidate into `GithubService` with submodules if needed
3. Create clear interface: sync, monitor, integration = methods, not classes
4. Keep routes simple (call one service)

**Impact:** ~100-200 LOC reduction, clearer intent
**Effort:** 3-4 hours

---

### 5. **Backup File Cleanup**
**Files:**
- `/wizard/dashboard/src/app.css.bak` - 4 days old (2346 bytes)
- `/wizard/secrets.tomb.backup.20260128_203515` - 2 days old

**Issue:**
- `.bak` files should not be committed
- Secrets shouldn't be backed up in repo (security risk)
- Creates confusion about which is canonical

**Recommended Action:**
1. Remove `app.css.bak` (already have current `app.css`)
2. Move secrets backup to local `memory/` (gitignored)
3. Add `*.bak`, `*.backup*` to `.gitignore`
4. Document secrets rotation process

**Impact:** Cleaner repo, reduced security footprint
**Effort:** 30 min

---

## LOW PRIORITY (Technical Debt)

### 6. **Notification History Duplication**
**Files:**
- `/wizard/routes/notification_history_routes.py` (286 LOC)
- `/wizard/services/notification_history_service.py` (363 LOC)

**Issue:**
- Properly separated (routes/services pattern is correct)
- BUT: `clear_old_notifications()` exists in both
- Consider: if truly just request→service pass-through, consolidate

**Recommended Action:**
- ✓ Keep as-is if services layer adds value
- OR: Verify no duplicate logic exists
- Suggested: Audit if service does more than CRUD wrapper

**Impact:** ~0 LOC (proper design) or ~50 LOC (if refactoring)
**Effort:** 1 hour (audit only)

---

### 7. **Config Files Organization**
**Files:**
- `/wizard/config/oauth_providers.template.json`
- `/wizard/config/github_keys.example.json`
- `/wizard/config/check_config_status.py`
- `/wizard/config/init_dev_config.py`

**Issue:**
- Config initialization scattered
- No clear "config as code" pattern
- Templates mix with validation scripts

**Recommended Action:**
- Create `config/README.md` explaining setup
- Consider config builder pattern (BaseConfig + providers)
- Move templates to `config/templates/`

**Impact:** Better onboarding
**Effort:** 2 hours

---

### 8. **Tools Directory Audit**
**Files in `/wizard/tools/`:**
- `web_proxy.py` - HTTP proxy
- `web_scraper.py` - Web scraping (❓ Core violation?)
- `github_dev.py` - Dev utilities
- `package_builder.py` - APK/package building
- `library_cli.py` - Library management
- `secret_store_cli.py` - Secrets management
- `apk_keygen.py` - Key generation
- `image_teletext.py` - Teletext rendering
- `reset_secrets_tomb.py`, `check_secrets_tomb.py` - Tomb utilities

**Issue:**
- Mismatched purposes (web scraping violates core offline-first principle)
- Some duplicate with services (secret store utilities)
- Unclear which are dev-only vs. production

**Recommended Action:**
- Audit each tool for necessity
- Move dev-only to `dev/tools/`
- Mark web scraping as "cloud-only" with warnings
- Consolidate tomb utilities → single entry point

**Impact:** Clearer tool ecosystem
**Effort:** 3 hours (audit + organization)

---

## DEBT TRACKING

| ID | Issue | Type | LOC | Priority | Status |
|----|-------|------|-----|----------|--------|
| 1 | Port manager split | Duplication | 936 | HIGH | Not started |
| 2 | OAuth handler stub | Relic | 219 | HIGH | Not started |
| 3 | Migration routes | Relic | 144 | HIGH | Not started |
| 4 | GitHub services | Overlap | 730 | MEDIUM | Not started |
| 5 | Backup files | Hygiene | N/A | MEDIUM | Not started |
| 6 | Notification history | Possible dup | 649 | LOW | Not started |
| 7 | Config organization | Design | N/A | LOW | Not started |
| 8 | Tools audit | Clarity | Variable | LOW | Not started |

**Total Technical Debt:** ~2,500+ LOC (consolidation potential)

---

## Quick Wins (30 min - 1 hour)

1. Delete `oauth_handler.py` stub
2. Delete `migration_routes.py`
3. Delete backup files (`.bak`, `.backup`)
4. Update `.gitignore` to exclude backups
5. Document which port_manager is canonical

---

## Next Steps

1. **Week 1:** Complete HIGH priority items (port manager, oauth, migration)
2. **Week 2:** GitHub services consolidation
3. **Week 3:** Tools audit + config reorganization

---

*Generated by code analysis. Update as work progresses.*
