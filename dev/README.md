# Development Workspace (`/dev/`)

**Version:** 2.0.1
**Purpose:** Tracked development files (roadmap, session logs, tools)

---

## Overview

`/dev/` contains **all tracked development files** for uDOS. Unlike `/sandbox/` (which is gitignored), everything in `/dev/` is committed to version control.

### ⚠️ Key Difference: `/dev/` vs `/sandbox/`

| Directory | Purpose | Git Status | Contents |
|-----------|---------|------------|----------|
| `/dev/` | Development tracking | **Tracked** | Roadmap, session logs, tools |
| `/sandbox/` | Runtime workspace | **Gitignored** | User files, logs, drafts |

---

## Directory Structure

```
dev/
├── roadmap/      # Project roadmap and planning docs
├── sessions/     # Development session logs
├── tools/        # Development utilities (migrate_upy.py, etc.)
└── scripts/      # Development automation scripts
```

---

## Usage Guidelines

### `/dev/roadmap/` - Project Planning

**Purpose:** High-level roadmap, version planning, and architecture decisions

**Files:**
- `ROADMAP.MD` - Master roadmap document
- Version planning docs
- Architecture proposals
- Feature specifications

**Examples:**
```
dev/roadmap/ROADMAP.MD
dev/roadmap/v1.2.0-planning.md
dev/roadmap/architecture-proposal.md
```

### `/dev/sessions/` - Development Logs

**Purpose:** Session-by-session development logs tracking progress

**Files:**
- Daily development session logs
- Feature implementation logs
- Refactoring session logs
- Completion reports

**Naming Convention:**
```
session-YYYY-MM-DD-description.md
session-2025-12-02-consolidation.md
session-2025-12-02-phase3-migration.md
```

**Examples:**
```
dev/sessions/session-2025-12-02-consolidation.md
dev/sessions/system-handler-refactor-plan.md
dev/sessions/v1.1.5.2-consolidation-analysis.md
```

### `/dev/tools/` - Development Utilities

**Purpose:** Scripts and tools for development tasks

**Files:**
- Migration scripts
- Code generators
- Analysis tools
- Build utilities

**Examples:**
```
dev/tools/migrate_upy.py          # .uscript → .upy migration
dev/tools/analyze_handlers.py     # Handler analysis tool
dev/tools/generate_diagrams.sh    # SVG diagram generator
```

### `/dev/scripts/` - Automation Scripts

**Purpose:** Development automation and CI/CD scripts

**Files:**
- Build scripts
- Test runners
- Deployment scripts
- Git hooks

**Examples:**
```
dev/scripts/run_tests.sh
dev/scripts/build_release.sh
dev/scripts/check_style.sh
```

---

## File Placement Rules

### ✅ Use `/dev/` For:

1. **Session Logs** - `dev/sessions/session-*.md`
2. **Roadmap Updates** - `dev/roadmap/ROADMAP.MD`
3. **Development Tools** - `dev/tools/migrate_upy.py`
4. **Planning Docs** - `dev/roadmap/v1.2.0-plan.md`

### ❌ Don't Use `/dev/` For:

1. **User scripts** → Use `sandbox/ucode/`
2. **Runtime logs** → Use `sandbox/logs/`
3. **Draft documentation** → Use `sandbox/docs/` then promote to `wiki/`
4. **Temporary files** → Use `sandbox/trash/`

---

## Development Workflow

### Starting a New Session

1. Create session log: `dev/sessions/session-YYYY-MM-DD-feature.md`
2. Document objectives and approach
3. Track progress in session log
4. Update roadmap when completing milestones

### Typical Session Log Structure

```markdown
# Session: Feature Implementation

**Date:** 2025-12-02
**Version:** 1.1.12
**Objective:** Implement water filter guide

## Objectives

- [ ] Create water filter guide
- [ ] Add to knowledge bank
- [ ] Write tests

## Progress

### Phase 1: Research (Completed)
- [x] Reviewed existing water guides
- [x] Identified key concepts

### Phase 2: Implementation (In Progress)
- [x] Created guide structure
- [ ] Add diagrams
- [ ] Write tests

## Files Changed

- `knowledge/water/filter-guide.md` (new)
- `memory/ucode/test_water_filter.upy` (new)

## Next Steps

- Complete diagrams
- Run tests
- Update roadmap
```

### Completing a Session

1. Mark tasks as completed
2. Update `dev/roadmap/ROADMAP.MD` with progress
3. Commit changes: `git commit -m "feat: water filter guide (v1.1.12)"`
4. Archive if needed: Move old sessions to subdirectories

---

## Git Best Practices

### Commit Messages

Use conventional commit format:

```
feat: Add water filter guide
fix: Correct boiling temperatures in fire guide
docs: Update roadmap with v1.2.0 plan
refactor: Split configuration_handler.py
```

### When to Commit

- After completing a logical unit of work
- Before switching tasks
- After updating roadmap/session logs

### What to Track

✅ **Always commit:**
- Session logs
- Roadmap updates
- Development tools
- Planning documents

❌ **Never commit:**
- Temporary files
- User data
- Runtime logs
- Draft content (use `sandbox/docs/` first)

---

## Organization Tips

### Archive Old Sessions

Create subdirectories for completed versions:

```
dev/sessions/
├── v1.1.12/          # Archived v1.1.12 sessions
├── v1.1.11/          # Archived v1.1.11 sessions
└── session-*.md      # Current sessions
```

### Keep Roadmap Updated

Update `dev/roadmap/ROADMAP.MD` regularly:
- Mark completed milestones ✅
- Update version progress
- Add new planning sections

### Use Descriptive Names

Good:
- `session-2025-12-02-core-consolidation.md`
- `v1.1.5.2-consolidation-analysis.md`

Bad:
- `session1.md`
- `notes.md`

---

## See Also

- `/sandbox/` - Runtime workspace (gitignored)
- `wiki/Developers-Guide.md` - Complete development guide
- `CONTRIBUTING.md` - Contribution guidelines
- `.gitignore` - Git ignore rules
