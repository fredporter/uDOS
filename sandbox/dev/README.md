# Sandbox Development Directory

**Primary development workspace for uDOS v2.0.0+**

## Purpose

This directory (`sandbox/dev/`) is where all active development work, session notes, and planning should happen. It's the primary workspace for contributors working on uDOS.

## Directory Structure

```
sandbox/
├── dev/                    # ← YOU ARE HERE
│   ├── sessions/           # Daily development sessions
│   ├── planning/           # Feature planning, roadmaps
│   ├── notes/              # Technical notes, investigations
│   └── archive/            # Completed work (optional)
├── docs/                   # Draft documentation (before wiki)
├── drafts/                 # Work-in-progress content
├── logs/                   # Runtime logs (auto-generated)
├── scripts/                # Utility scripts, generators
├── tests/                  # Pytest test suite
├── ucode/                  # Test .uscript files
├── trash/                  # Temporary files (auto-cleaned)
└── workflow/               # Automation scripts
```

## Usage Guidelines

### 📝 Session Notes

Create dated session files:

```
sandbox/dev/sessions/
├── 2025-11-26-grid-standardization.md
├── 2025-11-27-extension-refactor.md
└── 2025-11-28-wiki-consolidation.md
```

**Session Template:**
```markdown
# Session: [Feature Name]
**Date:** YYYY-MM-DD
**Status:** In Progress | Complete | Blocked
**Related:** Issue #123, PR #456

## Context
Brief background on what you're working on.

## Objectives
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Progress
- ✅ Completed items
- 🔄 In progress
- ⏳ Pending

## Technical Notes
- Key decisions
- Challenges
- Solutions

## Next Steps
1. Next action
2. Following action
```

### 🗺️ Planning

Feature planning and roadmaps:

```
sandbox/dev/planning/
├── v2.1.0-plan.md          # Version planning
├── extension-system.md     # Feature designs
└── mobile-pwa-spec.md      # Technical specs
```

### 🔬 Technical Notes

Investigations, research, architecture decisions:

```
sandbox/dev/notes/
├── grid-system-research.md
├── tile-code-format.md
└── api-architecture.md
```

### 📦 Archive (Optional)

Move completed work to archive:

```
sandbox/dev/archive/
├── v2.0.0-data-consolidation.md
└── grid-migration-complete.md
```

## Best Practices

### ✅ Do

- **Date your files**: `2025-11-26-feature-name.md`
- **Use clear names**: `grid-standardization.md` not `work.md`
- **Update regularly**: Document as you work
- **Link to commits**: Include git commit hashes
- **Track progress**: Use checkboxes and status indicators

### ❌ Don't

- **Don't commit sensitive data**: API keys, passwords, etc.
- **Don't create permanent files here**: Move to wiki when complete
- **Don't duplicate**: Check if note already exists
- **Don't leave stale files**: Archive or delete when done

## Integration with Git

**✅ Committed to Git:**
- Planning documents (roadmaps, designs)
- Technical notes (architecture, decisions)
- Session summaries (high-level only)

**❌ Not Committed (.gitignore):**
- Personal notes with sensitive info
- Temporary scratch files
- Experimental code (use `sandbox/drafts/`)
- Session logs with API keys or secrets

## Workflow

1. **Start Session** → Create `sandbox/dev/sessions/YYYY-MM-DD-topic.md`
2. **Work & Document** → Update session file as you progress
3. **Commit Code** → Reference session file in commit message
4. **Complete Feature** → Move key docs to wiki
5. **Archive Session** → Move to `archive/` or delete

## VS Code Tasks

Use these tasks for common operations:

- **Update Wiki: Current Dev Round** - Reminder to update docs
- **Copilot: Stamp Summary Line** - Generate dev summary
- **Logs: Tail Dev** - Monitor development logs
- **TIDY Sandbox** - Organize sandbox files

## Copilot Integration

GitHub Copilot is configured to use:
- `.github/copilot-instructions.md` - Project guidelines
- This README - Development workspace rules

Copilot will:
- Suggest placing dev files in `/sandbox/dev/`
- Use proper path conventions
- Follow uDOS coding standards
- Reference wiki for documentation

## Relationship to Other Directories

- **`/core`** - Production code (stable, tracked)
- **`/knowledge`** - Knowledge bank (curated, tracked)
- **`/extensions`** - Extensions (tracked)
- **`/sandbox`** - Development workspace (mostly gitignored)
  - **`/sandbox/dev`** - Active development (you are here)
  - **`/sandbox/tests`** - Test suite (tracked)
  - **`/sandbox/scripts`** - Utilities (tracked)
  - **`/sandbox/docs`** - Draft docs (temporary)
- **`/wiki`** - Public documentation (tracked separately)

## Questions?

See:
- **Copilot Instructions**: `.github/copilot-instructions.md`
- **Developers Guide**: `wiki/Developers-Guide.md`
- **Contributing**: `CONTRIBUTING.md`

---

**Remember:** This is your workspace. Keep it organized, but don't overthink it. The goal is to capture your thinking and progress, not create perfect documentation.
