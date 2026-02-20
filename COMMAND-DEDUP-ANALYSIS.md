# Command Deduplication Analysis
Generated: 2026-02-20

## Overview

Analyzed 55 core commands for overlapping functionality. Result: **Few true duplicates, mostly intentional aliases**.

---

## Potential Consolidation Candidates

### 1. Maintenance Commands (5 commands → Could merge to 3-4)

| Commands | Overlap | Assessment | Risk |
|----------|---------|-----------|------|
| BACKUP, RESTORE, UNDO | Backup/versioning | **HIGH** - Could reduce to BACKUP + variants | Medium |
| TIDY, CLEAN, COMPOST, DESTROY | Data cleanup | **HIGH** - Overlapping scopes | High |

**Details:**
- BACKUP: Create backup snapshots
- RESTORE: Restore from backup
- UNDO: Simple undo via last backup
- **Overlap**: RESTORE and UNDO both read backups; scopes differ
- **Issue**: UNDO is just "latest RESTORE"

**Recommendation:**
- Keep BACKUP (primary)
- Keep RESTORE (primary)
- Consider UNDO as alias to "RESTORE --latest"
- Merge TIDY + CLEAN into single command with flags (--soft vs --hard)
- COMPOST = archive old backups (specialized, keep)
- DESTROY = wipe+reset (dangerous, keep isolated)

---

### 2. File Operations Commands (9 commands → Could merge to 5-6)

| Commands | Overlap | Assessment | Risk |
|----------|---------|-----------|------|
| FILE, NEW, EDIT | File ops | **MEDIUM** - Different entry points | Low |
| READ, STORY | Content reading | **MEDIUM** - STORY is markdown-specific | Low |
| PLACE, LIBRARY | Content selection | **MEDIUM** - PLACE for workspaces; LIBRARY for shared | Low |
| RUN, SCRIPT | Script execution | **MEDIUM** - RUN is general; SCRIPT is system-specific | Low |

**Details:**
- FILE: File picker/manager
- NEW: Create new file (shortcut via file_editor)
- EDIT: Edit existing file (shortcut via file_editor)
- **Issue**: NEW/EDIT both wrap FileEditorHandler; could be FILE NEW/FILE EDIT
- READ: Read file content
- STORY: Read story/markdown files
- **Issue**: STORY is subset of READ for markdown files
- PLACE: Workspace-aware file picker
- LIBRARY: Shared content browser
- RUN: General script runner
- SCRIPT: System script specific runner
- **Issue**: RUN is general; SCRIPT for system scripts (minor overlap)

**Recommendation:**
- Consolidate: FILE NEW/FILE EDIT instead of NEW/EDIT separate commands
- Consolidate: STORY could be variant of READ (READ --story)
- Keep PLACE and LIBRARY separate (different contexts)
- Keep RUN and SCRIPT separate (RUN is more general, SCRIPT is system-specific)
- **Estimated reduction**: 9 → 6-7 commands

---

### 3. System Status Commands (3 commands → Could merge to 2)

| Commands | Overlap | Assessment | Risk |
|----------|---------|-----------|------|
| HEALTH, VERIFY, REPAIR  | System checks | **MEDIUM** - All check system health | Low |

**Details:**
- HEALTH: Basic health check
- VERIFY: Deeper verification
- REPAIR: Attempt to fix issues
- **Issue**: Linear progression - HEALTH → VERIFY → REPAIR

**Recommendation:**
- Keep separate (user mental model: diagnose → verify → fix)
- Could reduce to: HEALTH [--deep] vs REPAIR [--dry-run]
- Current separate commands is better for clarity
- **Estimated reduction**: Keep as-is (3 commands)

---

### 4. Navigation Commands (6 commands → Keep as-is)

| Commands | Overlap | Assessment | Risk |
|----------|---------|-----------|------|
| MAP, GRID, PANEL, ANCHOR, GOTO, FIND | Different purposes | **LOW** - Specialized | None |

**Details:**
- MAP: Show world map
- GRID: Show grid (calendar/table/schedule/dashboard/workflow)
- PANEL: Show map panel
- ANCHOR: Manage anchors (place markers)
- GOTO: Navigate to location
- FIND: Search locations
- **Assessment**: All have distinct functions
- **Recommendation**: Keep all 6

---

### 5. NPC & Dialogue Commands (3 commands → Keep as-is)

| Commands | Overlap | Assessment | Risk |
|----------|---------|-----------|------|
| NPC, SEND, TALK/TELL | NPC interaction | **LOW** - NPC state vs dialogue | None |

**Details:**
- NPC: Manage NPCs (list, spawn, edit)
- SEND: Send message to NPC (dialogue execution)
- TELL: Describe NPC (information)
- **Assessment**: Different purposes
- **Recommendation**: Keep all 3

---

### 6. Game State Commands (5 commands → Keep as-is)

| Commands | Overlap | Assessment | Risk |
|----------|---------|-----------|------|
| BAG, GRAB, SPAWN, SAVE, LOAD | Game state | **LOW** - Distinct state aspects | None |

**Assessment**: All have clear, distinct functions. No overlap.

---

### 7. Extension/Integration Commands (3 commands → Keep as-is)

| Commands | Overlap | Assessment | Risk |
|----------|---------|-----------|------|
| SONIC, MUSIC, EMPIRE | Extensions | **LOW** - Different extensions | None |

**Assessment**: Each manages different extension/provider.

---

## Summary: Consolidation Opportunities

### High Priority (Significant reduction)

| Current | Proposed | Reduction | Risk |
|---------|----------|-----------|------|
| BACKUP/RESTORE/UNDO (3) | BACKUP + variants (1-2) | 1-2 cmds | Medium |
| TIDY/CLEAN/COMPOST/DESTROY (4) | CLEANUP + DESTROY (2) | 2 cmds | High |
| NEW/EDIT (2) | FILE subcommands (0 separate) | 2 cmds | Low |

**Total potential reduction**: 5-7 commands → 55 to 48-50

### Medium Priority (Minor consolidation)

| Current | Proposed | Reduction | Risk |
|---------|----------|-----------|------|
| READ/STORY (2) | READ variants (0 separate) | 1 cmd | Low |
| RUN/SCRIPT (2) | RUN variants (0 separate) | 1 cmd | Medium |

**Total potential reduction**: 4 commands → fewer

### Recommendation

**Conservative approach (Low risk):**
- Consolidate NEW/EDIT into FILE subcommands (no API change, just UX)
- Consolidate STORY into READ flags (no API change)
- Keep maintenance commands separate (current mental model works)
- **Result**: 55 → 53 commands

**Aggressive approach (Medium risk):**
- Consolidate all of above PLUS
- Merge UNDO as "RESTORE --latest" alias
- Merge TIDY/CLEAN into "CLEANUP --soft" vs "DESTROY"
- **Result**: 55 → 48-50 commands

**Recommendation**: Start with **conservative approach** (2-command reduction). Aggressive consolidation can happen in v1.4 with more testing.

---

## Implementation Notes

### Commands to NOT consolidate (clear needs)

- MAP, GRID, PANEL: Different visualization contexts
- HEALTH, VERIFY, REPAIR: Users expect linear diagnostic flow
- SAVE, LOAD: Game state management (must stay separate)
- ANCHOR, GOTO, FIND: Different navigation primitives
- CONFIG, WIZARD, EMPIRE: Different system integrations
- BAG, GRAB, SPAWN: Core gameplay mechanics
- TOKEN, UID, GHOST, USER: User/auth management (all needed)

### Low-hanging fruit (safe to consolidate)

1. **FILE operations**: NEW/EDIT → FILE NEW/FILE EDIT
2. **Content reading**: STORY → READ --story or READ [--format story]
3. **Script execution**: SCRIPT → RUN --system or RUN [--scope system]
