# Dev vs Sandbox: Development Workspace Guide

As of **v1.1.13**, uDOS uses a clean separation between **tracked development files** (`/dev/`) and **gitignored runtime files** (`/sandbox/`).

## Quick Reference

| Directory | Status | Purpose | Examples |
|-----------|--------|---------|----------|
| `/dev/` | **Tracked in git** | Development files shared across contributors | Roadmap, tools, session logs |
| `/sandbox/` | **Gitignored** | User-specific runtime files, experiments | Local scripts, drafts, logs |
| `/core/` | **Tracked in git** | Production-ready core system | Commands, services, data |
| `/extensions/` | **Tracked in git** | Extensions and optional features | Play mechanics, web UI |
| `/knowledge/` | **Tracked in git** | Curated knowledge guides | Water, fire, shelter guides |
| `/memory/` | **Tracked in git** | Distributable scripts and tests | uCODE scripts, test suite |

## `/dev/` Directory (Tracked)

Development workspace for **project-level files** that should be shared across all contributors.

### Structure
```
dev/
├── roadmap/                  # Project roadmap and planning
│   ├── ROADMAP.MD            # Complete project roadmap
│   ├── PLAN-v1.1.5.3.md      # Version-specific plans
│   └── COMPLETED.md          # Archived completion notes
├── sessions/                 # Development session logs
│   ├── session-2025-12-02-v1.1.13-complete.md
│   └── reorganization-v1.1.13-complete.md
├── tools/                    # Development utilities
│   ├── migrate_upy.py        # .uscript → .upy migration
│   └── validate_tiles.py     # TILE code validation
└── scripts/                  # Development automation
    └── cleanup_structure.sh  # Project cleanup scripts
```

### What Goes in `/dev/`

✅ **DO commit to `/dev/`:**
- Project roadmap and version planning
- Development session logs (what was done, decisions made)
- Migration tools (shared across team)
- Project-wide automation scripts
- Architecture documentation drafts (before wiki promotion)

❌ **DON'T commit to `/dev/`:**
- Personal notes or experiments
- API keys or secrets (use `.env`)
- User-specific configurations
- Temporary test files
- Work-in-progress code (use `/sandbox/drafts/`)

### Example: Session Log
```markdown
# dev/sessions/session-2025-12-02-v1.1.13-complete.md

## v1.1.13 Project Structure Reorganization - Complete ✅

**Date**: December 2, 2025
**Version**: v1.1.13
**Status**: Complete (4/4 phases)

### Phase 1: /dev/ vs /sandbox/ Separation
- Created `/dev/` for tracked development files
- Moved 40 files from `sandbox/dev/` → `dev/`
- Updated `.gitignore` to exclude entire `sandbox/` directory

### Phase 2: Core Root Cleanup
...
```

## `/sandbox/` Directory (Gitignored)

Personal workspace for **user-specific files** that should NOT be shared.

### Structure
```
sandbox/
├── ucode/                    # Local .upy scripts (not synced)
│   ├── test_automation.upy   # Personal workflow scripts
│   └── experimental.upy      # Prototyping new commands
├── user/                     # User data files
│   ├── planets.json          # User's planet database
│   └── USER.UDT              # User profile
├── logs/                     # Runtime logs
│   ├── dev.log               # Development log
│   └── error.log             # Error log
├── drafts/                   # Work-in-progress content
│   ├── new_guide_draft.md    # Content before knowledge/ promotion
│   └── feature_ideas.md      # Personal brainstorming
├── docs/                     # Draft documentation
│   ├── api_notes.md          # Documentation before wiki promotion
│   └── tutorial_draft.md     # Tutorial drafts
├── workflow/                 # Workflow automation
│   ├── daily_backup.upy      # Personal automation
│   └── test_suite.upy        # Local testing workflows
└── trash/                    # Temporary files (auto-cleaned by CLEAN)
    └── old_test_output.txt
```

### What Goes in `/sandbox/`

✅ **DO use `/sandbox/` for:**
- Local .upy scripts for personal automation
- Draft content before promoting to `knowledge/` or `wiki/`
- Experimental code and prototypes
- User-specific data files (planets.json, USER.UDT)
- Runtime logs
- Temporary test outputs

❌ **DON'T use `/sandbox/` for:**
- Core system files (use `core/`)
- Production-ready extensions (use `extensions/`)
- Curated knowledge guides (use `knowledge/`)
- Distributable scripts (use `memory/ucode/`)
- Final documentation (use `wiki/`)

### Example: Workflow Script
```python
# sandbox/workflow/daily_backup.upy
"""
Personal workflow: Daily backup of user data.
Not synced to git (stays in sandbox/).
"""

# Backup user data
COPY sandbox/user/planets.json → sandbox/user/backups/planets-{date}.json
COPY sandbox/user/USER.UDT → sandbox/user/backups/USER-{date}.UDT

# Clean old backups (keep last 7 days)
WORKFLOW CLEAN_OLD --days=7 --path=sandbox/user/backups/

ECHO "✅ Daily backup complete"
```

## File Placement Decision Tree

```
┌─────────────────────────────────────┐
│ Where should this file go?         │
└─────────────────────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │ Is it production-   │  YES  ┌────────────────────┐
    │ ready & stable?     │──────▶│ Core/Extensions/   │
    └─────────────────────┘       │ Knowledge/Memory   │
              │ NO                 └────────────────────┘
              ▼
    ┌─────────────────────┐
    │ Is it project-level │  YES  ┌────────────────────┐
    │ development?        │──────▶│ /dev/              │
    │ (shared with team)  │       │ (tracked in git)   │
    └─────────────────────┘       └────────────────────┘
              │ NO
              ▼
    ┌─────────────────────┐
    │ Is it user-specific │  YES  ┌────────────────────┐
    │ or experimental?    │──────▶│ /sandbox/          │
    └─────────────────────┘       │ (gitignored)       │
                                   └────────────────────┘
```

## Development Workflows

### Workflow 1: Creating a New Guide

1. **Draft in sandbox**:
   ```bash
   # Create draft
   NEW sandbox/docs/water_filtration_advanced.md

   # Iterate on content (not tracked)
   EDIT sandbox/docs/water_filtration_advanced.md
   ```

2. **Review and promote**:
   ```bash
   # Once ready, move to knowledge bank
   MOVE sandbox/docs/water_filtration_advanced.md → knowledge/water/filtration_advanced.md

   # Now tracked in git
   git add knowledge/water/filtration_advanced.md
   git commit -m "Add advanced water filtration guide"
   ```

### Workflow 2: Development Session

1. **Create session log** (tracked):
   ```bash
   NEW dev/sessions/session-2025-12-XX-feature-name.md

   # Document what you're doing
   EDIT dev/sessions/session-2025-12-XX-feature-name.md
   ```

2. **Prototype in sandbox** (not tracked):
   ```bash
   # Experiment with code
   NEW sandbox/drafts/new_feature_prototype.py

   # Test locally
   RUN sandbox/drafts/new_feature_prototype.py
   ```

3. **Finalize in core** (tracked):
   ```bash
   # Once working, move to core
   COPY sandbox/drafts/new_feature_prototype.py → core/services/new_feature.py

   # Commit to git
   git add core/services/new_feature.py dev/sessions/...
   git commit -m "Add new feature service"
   ```

### Workflow 3: Testing Changes

1. **Local test script** (sandbox):
   ```python
   # sandbox/ucode/test_my_changes.upy
   """Quick test of recent changes (local only)"""

   # Test new feature
   OK ASK "Test query for new feature"

   # Check output
   GET LAST_RESPONSE
   ```

2. **Distributable test** (memory):
   ```python
   # memory/ucode/test_new_feature.py
   """Pytest test for new feature (shared with team)"""

   import pytest
   from core.services.new_feature import NewFeature

   def test_new_feature():
       feature = NewFeature()
       assert feature.works() == True
   ```

## Common Scenarios

### Scenario: "I want to create a personal workflow"
✅ Use `/sandbox/workflow/my_workflow.upy`

**Why?** Personal workflows are user-specific and should not be shared.

### Scenario: "I'm writing a development tool that others will use"
✅ Use `/dev/tools/my_tool.py`

**Why?** Development tools should be tracked and shared across the team.

### Scenario: "I'm documenting what I did today"
✅ Use `/dev/sessions/session-2025-12-XX.md`

**Why?** Session logs capture project history and should be tracked.

### Scenario: "I'm prototyping a new knowledge guide"
✅ Use `/sandbox/docs/guide_draft.md` → promote to `knowledge/category/guide.md` when ready

**Why?** Drafts are user-specific until reviewed and promoted to knowledge bank.

### Scenario: "I have user data (planets, character stats)"
✅ Use `/sandbox/user/planets.json`

**Why?** User data is personal and should never be committed to git.

### Scenario: "I'm creating a distributable .upy script"
✅ Use `memory/ucode/my_script.upy`

**Why?** Memory tier is for production-ready, distributable scripts shared with all users.

## Migration from Old Structure

### Before v1.1.13 (Old)
```
sandbox/
├── dev/                      # ❌ DEPRECATED
│   ├── roadmap/              # Should be in /dev/
│   ├── sessions/             # Should be in /dev/
│   └── tools/                # Should be in /dev/
└── ucode/                    # ✅ Correct
```

### After v1.1.13 (New)
```
dev/                          # ✅ Tracked development files
├── roadmap/
├── sessions/
└── tools/

sandbox/                      # ✅ Gitignored runtime files
├── ucode/
├── user/
└── logs/
```

### Migration Command
```bash
# Automated migration (already done in v1.1.13)
# This is for reference only

# Move dev files to /dev/
mv sandbox/dev/roadmap dev/
mv sandbox/dev/sessions dev/
mv sandbox/dev/tools dev/

# Update git tracking
git add dev/
git rm -r sandbox/dev/
git commit -m "Move dev files to /dev/ (v1.1.13 reorganization)"
```

## Best Practices

### 1. Keep Sandbox Clean
```bash
# Regular cleanup (removes files in trash/)
CLEAN

# Organize files into correct directories
TIDY --report
```

### 2. Document as You Go
```bash
# Create session log at start of work
NEW dev/sessions/session-$(date +%Y-%m-%d)-feature-name.md

# Update throughout session
EDIT dev/sessions/session-$(date +%Y-%m-%d)-feature-name.md
```

### 3. Graduate Drafts to Production
```bash
# Draft phase (sandbox)
NEW sandbox/docs/new_api_feature.md

# Review phase (still sandbox)
EDIT sandbox/docs/new_api_feature.md

# Production phase (promote to wiki)
MOVE sandbox/docs/new_api_feature.md → wiki/New-API-Feature.md
git add wiki/New-API-Feature.md
git commit -m "Add new API feature documentation"
```

### 4. Never Commit Secrets
```bash
# ✅ Good: Use .env file (gitignored)
echo "GEMINI_API_KEY=abc123" >> .env

# ❌ Bad: Hardcode in tracked files
# Never do this in /dev/ or /core/!
```

## CLEAN Command Behavior

The `CLEAN` command (from `environment_handler.py`) operates on `/sandbox/` only:

```bash
CLEAN              # Interactive cleanup of sandbox/
CLEAN --trash      # Delete sandbox/trash/ only
CLEAN --logs       # Delete sandbox/logs/ only
CLEAN --all        # Delete all cleanable directories
```

**What CLEAN removes:**
- `sandbox/trash/` (temporary files)
- `sandbox/logs/*.log` (runtime logs)
- `sandbox/peek/` (temporary file previews)

**What CLEAN preserves:**
- `sandbox/ucode/` (user scripts)
- `sandbox/user/` (user data)
- `sandbox/docs/` (draft documentation)
- `sandbox/workflow/` (workflow automation)

## See Also

- [Architecture](Architecture.md) - Overall system architecture
- [Layer Architecture](Layer-Architecture.md) - Grid and layer system
- [Developers Guide](Developers-Guide.md) - Complete development reference
- [Configuration](Configuration.md) - System configuration
- `.gitignore` - Complete list of gitignored files/directories
