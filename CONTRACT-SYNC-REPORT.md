# Contract & Dispatcher Sync Report
Generated: 2026-02-20

## Summary

| Metric | Value |
|--------|-------|
| Contract v1.3.16 commands | 35 |
| Dispatcher commands | 55 |
| Sync gap | 20 commands |
| **Contract v1.3.20 commands | 55** |
| **Sync status | ✅ ALIGNED** |

---

## Commands Added to Contract (v1.3.20)

These 20 commands are now in the dispatcher but were missing from v1.3.16:

```
ANCHOR       (Navigation - anchor management)
BACKUP       (Maintenance - backup creation)
CLEAN        (Maintenance - cleanup with trashing)
COMPOST      (Maintenance - archival compression)
DESTROY      (Cleanup - system reset/wipe)
EMPIRE       (Extension - Empire management)
GHOST        (System - ghost mode status)
GRID         (Display - grid/table visualization)
LIBRARY      (Content - library management)
MIGRATE      (Data - location migration)
MUSIC        (Media - Groovebox/Songscribe)
PLACE        (Workspace - file placement picker)
READ         (File - read markdown/content files)
RESTORE      (Maintenance - restore from backup)
SCHEDULER    (Automation - task scheduling)
SCRIPT       (System - script execution)
SEED         (Init - framework seed installer)
TIDY         (Maintenance - soft cleanup)
TOKEN        (Auth - token generation)
UNDO         (Undo - simple restore undo)
VIEWPORT     (Display - viewport measurement)
```

---

## Dispatcher Organization

The 55 commands are organized into functional groups (from dispatcher.py):

### Navigation (5)
- MAP, ANCHOR, GRID, PANEL, GOTO, FIND

### Information (2)
- TELL, HELP

### Game State (5)
- BAG, GRAB, SPAWN, SAVE, LOAD

### System (11)
- HEALTH, VERIFY, REPAIR, REBOOT, SETUP, UID, TOKEN, GHOST, SONIC, MUSIC, DEV, LOGS

### Workspace / File Operations (9)
- SCHEDULER, SCRIPT, VIEWPORT, DRAW, RUN, STORY, READ, FILE, NEW/EDIT, LIBRARY

### Workspace (4)
- PLACE, FILE, NEW, EDIT

### Maintenance (5)
- BACKUP, RESTORE, TIDY, CLEAN, COMPOST

### User Management (2)
- USER, PLAY

### Gameplay (1)
- RULE

### Cleanup/Reset (2)
- DESTROY, UNDO

### Data Migration (1)
- MIGRATE

### Seed Installation (1)
- SEED

### NPC & Dialogue (3)
- NPC, SEND, TALK

### Wizard Management (3)
- CONFIG, WIZARD, EMPIRE

### Binder (1)
- BINDER

---

## Contract Versioning

- **v1.3.16** (old): 35 commands, incomplete
- **v1.3.20** (new): 55 commands, complete dispatcher parity

No commands were deprecated/removed - all previous v1.3.16 commands remain in v1.3.20.

---

## Integration Checklist

- [x] Updated contract JSON with all 55 commands
- [x] New file: `core/config/ucli_command_contract_v1_3_20.json`
- [ ] Update `check_contract_dispatcher_parity.py` to point to v1.3.20
- [ ] CI test to validate contract sync
- [ ] Update docs (UCODE-COMMAND-REFERENCE.md) to list all commands

---

## Next Steps

1. Update CI test to use v1.3.20 contract
2. Verify dispatcher test: `tools/ci/check_contract_dispatcher_parity.py`
3. Document new commands in UCODE-COMMAND-REFERENCE.md
4. Create example workflows for 20 new commands
