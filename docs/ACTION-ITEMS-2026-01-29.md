# Action Items & Follow-ups

**Generated:** 2026-01-29  
**Based on:** Command & System Verification Report

---

## 🎯 Immediate Actions (< 1 hour)

### 1. ✅ Integration Testing
**Priority:** HIGH  
**Effort:** 30 minutes  
**Task:** Run command chains in uCODE TUI to verify end-to-end functionality

```bash
# Test sequence
BACKUP workspace pre-test         # Create recovery point
CLEAN workspace                   # Archive non-defaults  
REPAIR --check                    # Verify system health
REPAIR --upgrade                  # Install dependencies
RESTORE workspace                 # Recover from backup
DESTROY --help                    # Show options
```

### 2. ✅ Variable Sync Testing  
**Priority:** HIGH  
**Effort:** 45 minutes  
**Task:** Test newly completed Variable Synchronization System

```bash
# Test TUI ↔ Wizard API flow
CONFIG GET user_name              # Read from .env
CONFIG SET user_name "Alice"      # Write to .env + secrets
CONFIG SHOW                       # Verify in TUI

# Test from Wizard Dashboard
curl http://localhost:8765/api/v1/config/variables
curl -X POST http://localhost:8765/api/v1/config/set \
  -d '{"key":"user_name", "value":"Bob"}'
CONFIG GET user_name              # Should reflect change
```

### 3. ✅ Permission Enforcement
**Priority:** MEDIUM  
**Effort:** 20 minutes  
**Task:** Verify role-based access control works

```bash
# Test as admin
DESTROY --wipe-user               # Should succeed

# Test as regular user
USER create testuser player
# testuser runs:
DESTROY --wipe-user               # Should fail: "Permission denied"
```

---

## 🔨 Short-term Tasks (1-2 days)

### 1. Implement UNDO Command
**Priority:** MEDIUM  
**Effort:** 2-3 hours  
**Description:** UNDO not currently implemented

**Proposed Implementation:**
```python
# core/commands/undo_handler.py
class UndoHandler(BaseCommandHandler):
    def handle(self, command, params, grid, parser):
        # UNDO [--list|--count N|--to <timestamp>]
        # Track action history in unified logs
        # Provide rollback capability
```

**Options to implement:**
```bash
UNDO                              # Undo last action
UNDO --list                       # Show action history
UNDO --count 3                    # Undo last 3 actions
UNDO --to 2026-01-29T14:00       # Undo to specific time
```

**References:**
- [Keypad reference](../core/input/keypad_handler.py#L110) (KEY_UNDO = '9')
- [OUTSTANDING-TASKS.md](OUTSTANDING-TASKS.md) mentions UNDO capability

---

### 2. Enhanced Story Parser Testing
**Priority:** MEDIUM  
**Effort:** 15 minutes  
**Description:** 1 failing test in multi-section story parsing

**Test file:** `/core/src/story/parser.ts`  
**Status:** 8/9 passing (88.9%)  
**Blocked issue:** Multi-section parsing edge case

```bash
# Run story tests
cd core && npm test __tests__/runtime.test.ts
```

---

### 3. Documentation Sync
**Priority:** LOW  
**Effort:** 30 minutes  
**Description:** Update help references and quick reference guides

**Files to update:**
- [docs/wiki/HELP-COMMAND-QUICK-REF.md](wiki/HELP-COMMAND-QUICK-REF.md)
- [docs/uCODE-QUICK-REFERENCE.md](uCODE-QUICK-REFERENCE.md)
- [docs/uCODE.md](uCODE.md)

---

## 📋 Medium-term Tasks (1-2 weeks)

### 1. Goblin → Wizard Migration
**Priority:** HIGH  
**Effort:** 8-12 hours  
**Status:** Checklist exists at [docs/howto/goblin-wizard-migration-checklist.md](howto/goblin-wizard-migration-checklist.md)

**Priority 1 (Core user impact):**
- [ ] Setup wizard API port (`/api/v0/setup/wizard/*`)
- [ ] Story submission flow (Svelte component)
- [ ] Table save implementation

**Priority 2 (Stability):**
- [ ] Extension monitor enable/disable
- [ ] Map data conversion

**Priority 3 (Nice-to-have):**
- [ ] Voice handler
- [ ] Desktop open wizard URL update

---

### 2. Notion Handler Implementation
**Priority:** HIGH (if active)  
**Effort:** 4-6 hours  
**Status:** 11 TODO stubs need implementation

**File:** `/wizard/services/notion_handler.py`

**TODOs:**
- [ ] Block → markdown conversion
- [ ] API key validation
- [ ] Page fetch/list/create
- [ ] Block operations (fetch/create/update)
- [ ] Webhook handler
- [ ] Bidirectional sync
- [ ] Conflict detection

**Reference:** [development-streams.md](development-streams.md#phase-6-wizard-server)

---

### 3. Extension Monitor Enhancement
**Priority:** MEDIUM  
**Effort:** 3-4 hours

**Features to add:**
- [ ] Enable/disable endpoints
- [ ] Service health checks
- [ ] Dependency validation
- [ ] Auto-restart on failure

---

## 🚀 Long-term Development (4+ weeks)

### Stream 1: Core Runtime (TypeScript + Grid)
**Timeline:** 4-6 weeks  
**Owner:** Core (`/core/`)

**Key deliverables:**
- [ ] Full TS runtime support
- [ ] Grid viewport renderer (beyond base)
- [ ] File parser integration (CSV/JSON/YAML/SQL)
- [ ] SQLite DB binding

**Reference:** [development-streams.md](development-streams.md#stream-1-core-runtime)

---

### Stream 2: Wizard Server (Production Services)
**Timeline:** 4-8 weeks  
**Owner:** Wizard (`/wizard/`)

**Phase 6A-D:**
- [ ] OAuth Foundation (2 weeks)
- [ ] HubSpot Integration (2 weeks)
- [ ] Notion Bidirectional Sync (2 weeks)
- [ ] iCloud Backup Relay (2 weeks)

**Reference:** [development-streams.md](development-streams.md#stream-2-wizard-server)

---

### Stream 2.5: Beacon Portal (WiFi Infrastructure)
**Timeline:** 2-3 weeks  
**Status:** Specification complete, ready for integration

**Components:**
- [ ] Sonic Screwdriver Device Catalog
- [ ] Beacon Portal WiFi Setup
- [ ] VPN Tunnel (WireGuard)
- [ ] Device Quota Management

**Reference:** [development-streams.md](development-streams.md#stream-25-beacon-portal-wifi-infrastructure)

---

### Stream 3: Goblin Dev Server
**Timeline:** Ongoing  
**Status:** Experimental features graduating to Wizard/Core

**Features:**
- [ ] Binder Compiler (graduated to Core)
- [ ] Screwdriver Provisioner
- [ ] MeshCore Manager

---

### Stream 4: App Development
**Timeline:** 8-12 weeks  
**Status:** Typo editor foundation active

**Components:**
- [ ] Typo Editor Foundation
- [ ] File Converters (OCR, PDF→MD)
- [ ] Typography System (Monaspace)
- [ ] Emoji & Graphics
- [ ] Runtime Features (uCode, Marp, Forms)

**Reference:** [development-streams.md](development-streams.md#stream-4-app-development-tauri--future-native)

---

## 📊 Issue Triage

### Critical (Blocking)
- None identified

### High Priority
1. **Test Variable Sync System** — New feature validation (1 hour)
   - TUI CONFIG → Wizard API flow
   - Verify .env, secrets.tomb, wizard.json sync
   - Test encryption/decryption

2. **Multi-Section Story Parsing** — Minor edge case (15 mins)
   - 1 failing test in `/core/src/story/parser.ts`
   - Impact: Non-blocking (88.9% pass rate)

3. **Notion Handler** — 11 TODO stubs (4-6 hours if active)
   - Blocks Wizard Phase 6C
   - Conditional on feature priority

### Medium Priority
1. **Goblin Migration Priority 1** — Core user impact (8+ hours)
2. **Extension Monitor** — Reliability improvement (3-4 hours)
3. **UNDO Command** — Feature completeness (2-3 hours)

### Low Priority
1. **PEEK Enhancements** — Backlog items (various)
2. **Grid Runtime Tests** — Minor edge cases (30 mins)
3. **Documentation Updates** — Maintenance (ongoing)

---

## 🧪 Testing Strategy

### Unit Tests
```bash
cd /Users/fredbook/Code/uDOS

# Run all tests
pytest core/tests/ -v
npm test --prefix core

# Specific test suites
pytest core/commands/test_destroy_handler.py -v
pytest core/commands/test_restart_handler.py -v
```

### Integration Tests
```bash
# Test command sequences
./start_udos.sh
> BACKUP workspace pre-test
> CLEAN workspace
> REPAIR --check
> RESTORE workspace

# Test role enforcement
> USER create testuser player
> USER set testuser role player
# Switch user context and test permissions
```

### Smoke Tests
```bash
# Quick validation
./start_udos.sh
> HELP
> DESTROY --help
> REPAIR --check
> LOGS --last 20
> SYSTEM STATUS
```

---

## 📝 Document References

### Primary References
- [AGENTS.md](../AGENTS.md) — Project architecture
- [docs/README.md](README.md) — Engineering entry point
- [development-streams.md](development-streams.md) — Feature planning
- [OUTSTANDING-TASKS.md](OUTSTANDING-TASKS.md) — Comprehensive task list

### Command References
- [core/commands/help_handler.py](../core/commands/help_handler.py) — 531 lines of command docs
- [core/tui/dispatcher.py](../core/tui/dispatcher.py) — Handler registration (196 lines)
- [wiki/HELP-COMMAND-QUICK-REF.md](wiki/HELP-COMMAND-QUICK-REF.md) — Quick reference

### System References
- [wiki/CONFIGURATION.md](wiki/CONFIGURATION.md) — Variable reference
- [features/config-import-export.md](features/config-import-export.md) — Config management
- [PHASE4-USER-MANAGEMENT-COMPLETE.md](../PHASE4-USER-MANAGEMENT-COMPLETE.md) — User system

### Specialized Guides
- [howto/goblin-wizard-migration-checklist.md](howto/goblin-wizard-migration-checklist.md) — Migration planning
- [specs/typescript-markdown-runtime.md](specs/typescript-markdown-runtime.md) — Runtime architecture
- [decisions/ADR-0003-alpine-linux-migration.md](decisions/ADR-0003-alpine-linux-migration.md) — Alpine strategy

---

## ✅ Completion Status

| Item | Status | Evidence |
|------|--------|----------|
| DESTROY command | ✅ Complete | [destroy_handler.py](../core/commands/destroy_handler.py) |
| BACKUP/RESTORE | ✅ Complete | [maintenance_handler.py](../core/commands/maintenance_handler.py) |
| REPAIR command | ✅ Complete | [repair_handler.py](../core/commands/repair_handler.py) |
| RESTART/RELOAD/REBOOT | ✅ Complete | [restart_handler.py](../core/commands/restart_handler.py) |
| System variables | ✅ Complete | Variable sync system documented |
| Role/capability matrix | ✅ Complete | RBAC defined in user_manager.py |
| API exposure tiers | ✅ Complete | Documented in architecture |
| Transport policy | ✅ Complete | Documented in AGENTS.md |
| Help system | ✅ Complete | [help_handler.py](../core/commands/help_handler.py) |
| Command dispatcher | ✅ Complete | All handlers registered |

---

## 🎯 Success Criteria

All action items should meet these criteria:

1. **Documented** — PR description explains what changed
2. **Tested** — Unit or integration tests included
3. **Logged** — Changes captured in unified logging
4. **Reversible** — Can be rolled back or undone
5. **Reviewed** — Code passes linting and style checks
6. **Referenced** — Documentation updated with examples

---

**Generated by:** Comprehensive System Verification  
**Date:** 2026-01-29 14:30 UTC  
**Status:** Ready for execution

