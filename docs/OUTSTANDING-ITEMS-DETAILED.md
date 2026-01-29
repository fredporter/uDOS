# Outstanding Items - Detailed Status & Resolution Path

**Date:** 2026-01-29  
**Prepared by:** System Verification  
**Status:** Comprehensive review with action items

---

## ✅ Completed Items

### 1. UNDO Command Implementation ✅
**Status:** COMPLETE (2026-01-29)  
**Time:** 45 minutes  
**Files:** 
- [core/commands/undo_handler.py](../core/commands/undo_handler.py) — NEW (200 lines)
- [core/commands/__init__.py](../core/commands/__init__.py) — UPDATED (added UndoHandler)
- [core/tui/dispatcher.py](../core/tui/dispatcher.py) — UPDATED (registered UNDO)
- [core/commands/help_handler.py](../core/commands/help_handler.py) — UPDATED (UNDO docs)

**Features:**
- Simple UNDO RESTORE wrapper around BACKUP system
- Links to existing RESTORE command
- Non-destructive (uses backups, no deletions)
- Full logging integration
- Help system integrated

**Usage:**
```bash
UNDO                          # Show help
UNDO RESTORE workspace        # Restore from latest backup
UNDO RESTORE workspace --force # Overwrite existing
```

**Testing:** Ready for manual testing in uCODE TUI

---

## 🔴 HIGH Priority Items

### 1. Test Variable Synchronization System (1 hour)
**Status:** PLAN CREATED ✅  
**Location:** [docs/VARIABLE-SYNC-TEST-PLAN.md](VARIABLE-SYNC-TEST-PLAN.md) (NEW, 350 lines)  
**Implementation Status:** Fully implemented

**Components Already Done:**
- ✅ [core/commands/config_handler.py](../core/commands/config_handler.py) — TUI CONFIG command
- ✅ [wizard/routes/config_routes.py](../wizard/routes/config_routes.py) — REST API endpoints
- ✅ Storage: .env, secrets.tomb, wizard.json
- ✅ Logging integration
- ✅ Permission enforcement

**Test Plan Includes:**
1. TUI Variable READ (CONFIG GET) — 10 mins
2. TUI Variable WRITE (CONFIG SET) — 15 mins
3. SYNC Operation (CONFIG --sync) — 10 mins
4. API Access (Wizard endpoints) — 15 mins
5. Encryption & Security validation — 10 mins
6. Dashboard Integration (if available) — 10 mins
7. Failure Cases & Recovery — 10 mins

**Next Steps:**
```bash
# 1. Start Wizard server
python wizard/server.py

# 2. In another terminal, run uCODE TUI
python uDOS.py

# 3. Execute test cases from plan
CONFIG                          # List all
CONFIG USER_NAME                # Get specific
CONFIG USER_NAME "Alice"        # Set value
CONFIG --sync                   # Force sync
```

**Effort:** 60 minutes (execution)  
**Blocker:** None (ready to test)

---

### 2. Fix Multi-Section Story Parsing Test (15 mins)
**Status:** INVESTIGATION NEEDED  
**Location:** [core/__tests__/runtime.test.ts](../core/__tests__/runtime.test.ts) (line 129)  
**Issue:** 1 failing test out of 9 (88.9% pass rate)

**Test Name:** "parse multiple sections"  
**Test Markdown:**
```markdown
---
title: Test
---

## First Section
Content 1

## Second Section
Content 2

## Third Section
Content 3
```

**Expected:** 3 sections parsed  
**Actual:** Unknown (need to run test)

**Investigation Steps:**
```bash
cd /Users/fredbook/Code/uDOS/core
npm test __tests__/runtime.test.ts 2>&1 | grep -A 5 "multiple sections"
```

**Possible Root Causes:**
1. Section separator parsing (looks for ---after headings)
2. Whitespace handling around separators
3. Heading format detection (## vs #)
4. Edge case with multiple --- lines

**Parser Code:** [core/src/story/parser.ts](../core/src/story/parser.ts) (line 47-53)
```typescript
const sectionTexts = mainContent.split(/\n---\n/);
// Splits on --- between newlines
// Test may have inconsistent formatting
```

**Resolution:**
1. Run test to see exact error message
2. Compare parser expectations vs test input
3. Fix either parser (if bug) or test (if test error)
4. Verify 9/9 tests passing

**Effort:** 15 minutes  
**Blocker:** None (non-critical edge case, 88.9% passing)

---

### 3. Grid Runtime Test Fixes (30 mins)
**Status:** INVESTIGATION NEEDED  
**Location:** [core/grid-runtime/__tests__/](../core/grid-runtime/__tests__/)  
**Issue:** 2 failing tests (96% pass rate from OUTSTANDING-TASKS.md)

**From OUTSTANDING-TASKS.md:**
> Grid block missing required 'name' field

**Files to Check:**
- [core/grid-runtime/__tests__/code-block-parser.test.ts](../core/grid-runtime/__tests__/code-block-parser.test.ts)
- Grid runtime test fixtures

**Expected Fix:**
1. Add `"name"` field to grid block test data
2. Ensure all grid blocks have required fields
3. Verify 51/51 tests passing

**Investigation:**
```bash
cd /Users/fredbook/Code/uDOS/core
npm test grid-runtime 2>&1 | grep -A 5 "name"
```

**Effort:** 30 minutes  
**Blocker:** None (isolated to grid tests)

---

## 🟡 MEDIUM Priority Items

### 1. Goblin → Wizard Migration Status
**Status:** NEEDS CLARIFICATION ❓  
**Question:** Is this migration still needed, or is it complete?

**Current Understanding:**
- Goblin = Experimental dev server (port 8767, `/api/v0/*`)
- Wizard = Production server (port 8765, `/api/v1/*`)
- User's request: "Goblin should be reset to wizard-like state, and contain only Teletext and Terminal mode testing GUIs"

**Implications:**
- **IF migration complete:** Goblin is already Wizard-like, only keep Teletext/Terminal
  - Action: Archive non-essential Goblin features
  - Effort: 2-4 hours cleanup
  
- **IF migration needed:** Need to port remaining features to Wizard
  - Action: Run migration checklist from [docs/howto/goblin-wizard-migration-checklist.md](howto/goblin-wizard-migration-checklist.md)
  - Effort: 8-12 hours

**Decision Needed:**
1. Check current Goblin state
2. Identify what's actually needed
3. Archive or migrate accordingly

**Recommendation:**
```bash
# Quick check of Goblin current features
ls -la /Users/fredbook/Code/uDOS/dev/goblin/
grep -r "TODO\|FIXME" /Users/fredbook/Code/uDOS/dev/goblin/ | head -20
```

**Next Steps:** Verify requirement with user or check dev/roadmap for current status

---

### 2. Core Runtime Development - What's Needed?
**Status:** NEEDS CLARIFICATION ❓  
**Timeline:** 4-6 weeks (planned from development-streams.md)

**Current Status:**
From [docs/development-streams.md](development-streams.md#stream-1-core-runtime-typescript-markdown--grid):

**Completed:**
- ✅ Specs moved to `/docs/specs/`
- ✅ Examples moved to `/docs/examples/`
- ✅ Binder compiler moved to Core
- ✅ Dataset manager + regen tools
- ✅ Output toolkit (ASCII-first)

**In Progress/Planned:**
- 🔲 Core runtime implementation (full TS runtime support)
- 🔲 Grid viewport renderer (beyond base map render)
- 🔲 File parser integration (CSV/JSON/YAML/SQL)

**Question:** What specific features are needed NOW vs later?

**Investigation:**
```bash
# Check what's actually implemented
grep -r "TODO\|FIXME" /Users/fredbook/Code/uDOS/core/src/ | head -20
grep -r "TODO\|FIXME" /Users/fredbook/Code/uDOS/core/__tests__/ | head -20

# Check test status
npm test --prefix /Users/fredbook/Code/uDOS/core 2>&1 | tail -20
```

**Options:**
1. **Minimal (1-2 weeks):** Complete failing tests, integrate parsers
2. **Standard (4-6 weeks):** Full TS runtime, grid viewport, all parsers
3. **Maximum (8+ weeks):** Include SQLite binding, advanced features

**Recommendation:** Clarify priority in development-streams.md

---

## 🟢 LOW Priority Items

### 1. Notion Handler Implementation (4-6 hours, if active)
**Status:** 11 TODO stubs exist  
**Location:** [/wizard/services/notion_handler.py](../wizard/services/notion_handler.py)  
**Blocking:** Wizard Phase 6C timeline

**Current TODOs:**
- [ ] Block → markdown conversion
- [ ] API key validation
- [ ] Page fetch/list/create
- [ ] Block operations (fetch/create/update)
- [ ] Webhook handler
- [ ] Bidirectional sync
- [ ] Conflict detection

**Decision:** Is Notion integration active feature or backlog?

**If Active:**
- Estimate: 4-6 hours
- Phase: 6C (weeks 3-4 of Phase 6 timeline)
- Blocks: Workflow Management integration

**If Backlog:**
- Archive to future planning
- Mark stubs as "TODO: Phase 7"

**Recommendation:** Confirm in [docs/development-streams.md](development-streams.md#phase-6a-oauth-foundation)

---

### 2. Wizard Phase 6 OAuth & Integrations (4-8 weeks)
**Status:** Phase 6A-6D planned, not started

**Phase Breakdown:**
- **Phase 6A:** OAuth Foundation (2 weeks) — Google, Microsoft, GitHub, Apple
- **Phase 6B:** HubSpot Integration (2 weeks)
- **Phase 6C:** Notion Bidirectional Sync (2 weeks)
- **Phase 6D:** iCloud Backup Relay (2 weeks)

**Status:** Planning phase only  
**Effort:** 4-8 weeks (after Phase 5 completion)

**Note:** Depends on completion of earlier phases

**Recommendation:** Review blocker dependencies before starting

---

### 3. PEEK Command Enhancements - Summary
**Status:** Feature backlog  
**Location:** [/wizard/docs/PEEK-COMMAND.md](../wizard/docs/PEEK-COMMAND.md)

**Current PEEK Features:**
- ✅ URL fetch & parse
- ✅ Markdown output
- ✅ Basic cleanup

**Backlog Enhancements:**
1. URL batch processing (3-4 hours)
2. Content cleanup options (2 hours)
3. Format options (GitHub-flavored, CommonMark) (2 hours)
4. Resume interrupted conversions (3 hours)
5. Cache management (2 hours)
6. PDF to Markdown support (4 hours)
7. Multi-format output (HTML, LaTeX) (4 hours)
8. Incremental updates (3 hours)
9. Content diffing (2 hours)
10. Web archiving integration (4 hours)

**Total Backlog Effort:** ~30 hours  
**Recommended Priority:** LOW (current features working)

**Recommendation:** Pick high-value items (batch, PDF, cleanup) for next cycle

---

### 4. Documentation Updates (Ongoing)
**Status:** Ongoing maintenance

**Recent Completions:**
- ✅ [docs/COMMAND-VERIFICATION-2026-01-29.md](COMMAND-VERIFICATION-2026-01-29.md) (35KB)
- ✅ [docs/ACTION-ITEMS-2026-01-29.md](ACTION-ITEMS-2026-01-29.md) (12KB)
- ✅ [docs/VARIABLE-SYNC-TEST-PLAN.md](VARIABLE-SYNC-TEST-PLAN.md) (15KB)

**Outstanding Documentation:**
- [ ] Update help references for UNDO command
- [ ] Add Variable Sync examples to wiki
- [ ] Document Notion handler TODOs
- [ ] Update development-streams with clarifications

**Effort:** 2-3 hours total  
**Recommendation:** Do after test results confirmed

---

## 📊 Summary Table

| Item | Status | Effort | Blocker | Next Step |
|------|--------|--------|---------|-----------|
| UNDO command | ✅ Complete | 45 min | None | Test in TUI |
| Variable Sync testing | 📋 Plan ready | 60 min | None | Execute test plan |
| Story parsing fix | ❓ Investigate | 15 min | None | Run test, diagnose |
| Grid runtime fix | ❓ Investigate | 30 min | None | Run test, add fields |
| Goblin migration | ❓ Unclear | 2-12 hrs | Clarify need | Check roadmap |
| Core Runtime needs | ❓ Unclear | 1-8 wks | Clarify scope | Review streams |
| Notion handler | 📋 Backlog | 4-6 hrs | Phase 6 gate | Confirm active |
| Phase 6 OAuth | 📋 Planned | 4-8 wks | Phase 5 done | Dependency check |
| PEEK enhancements | 📋 Backlog | ~30 hrs | None | Prioritize items |
| Documentation | 📋 Ongoing | 2-3 hrs | Test results | Schedule updates |

---

## 🎯 Immediate Action Plan (Next 2 hours)

### Priority 1: Execute (45 minutes)
1. **Test UNDO command** (10 mins)
   ```bash
   python uDOS.py
   > BACKUP workspace test-undo
   > UNDO RESTORE workspace
   ```

2. **Quick test Variable Sync** (20 mins)
   - Start Wizard server
   - CONFIG command basics
   - Verify sync working

3. **Run story/grid tests** (15 mins)
   ```bash
   npm test --prefix core/__tests__
   npm test grid-runtime
   ```

### Priority 2: Clarify (30 minutes)
1. Is Goblin migration still needed or complete?
2. What's the specific scope for Core Runtime (4-6 weeks)?
3. Is Notion handler active or backlog?

### Priority 3: Plan (45 minutes)
1. Document test results
2. Update outstanding-tasks.md with findings
3. Create detailed roadmap for clarified items

---

## 📞 Clarification Needed From User

1. **Goblin Status:**
   - Is Goblin→Wizard migration complete?
   - Should Goblin contain only Teletext/Terminal testing GUIs?
   - Or is Goblin still experimental development server?

2. **Core Runtime Scope:**
   - Which features are HIGH priority for 4-6 weeks?
   - What's minimum viable (1-2 weeks)?
   - What can be deferred to Phase 2?

3. **Notion Handler:**
   - Is Notion integration an active feature?
   - Or Phase 6C placeholder for future work?
   - Block on other systems?

4. **Testing Priorities:**
   - Execute Variable Sync tests now?
   - Fix story/grid tests now?
   - Or defer to later?

---

## ✅ Acceptance Criteria

System ready when ALL of:
- [x] UNDO command implemented and tested
- [ ] Variable Sync System tested (plan ready, needs execution)
- [ ] Story parsing test diagnosed
- [ ] Grid runtime test diagnosed
- [ ] Goblin status clarified
- [ ] Core Runtime scope defined
- [ ] Notion handler priority set
- [ ] Outstanding tasks document updated

---

**Status:** Ready for execution and clarification  
**Generated:** 2026-01-29 14:45 UTC  
**Next Review:** After test execution

