# Development Workshop (`/dev/`)

**Version:** Alpha v1.0.2.0  
**Purpose:** Engineering workshop for tools, scripts, and working concepts  
**Last Updated:** 2026-01-13

---

## Overview

`/dev/` is the **engineering workshop** — a space for development tools, scripts, and working concepts that support the build/test/release workflow.

**This folder is not the source of truth.** Canonical documentation and roadmap live in `/docs/`.

### Key Difference: `/dev/` vs `/.dev/` vs `/docs/`

| Directory | Purpose | Git Status | Contents |
|-----------|---------|------------|----------|
| `/docs/` | **Canonical truth** | **Tracked** | Roadmap, decisions, specs, devlogs |
| `/dev/` | Engineering workshop | **Tracked** | Drafts, tools, experiments, research |
| `/.dev/` (or `**/.dev/`) | Local dev notes | **Gitignored** | Session notes, WIP, debug |
| `/.archive/` (or `**/.archive/`) | Version history | **Gitignored** | Backups, old versions |

---

## Promotion Pattern (Critical)

After **~2 weeks**, drafts in `/dev/` must be:

**Promoted** to canonical locations:

| Type | Destination |
|------|-------------|
| Current work | `docs/devlog/YYYY-MM.md` |
| Architecture decision | `docs/decisions/ADR-####-*.md` |
| Repeatable procedure | `docs/howto/*.md` |
| Technical spec | `docs/specs/*.md` |
| Long-term plan | `docs/roadmap.md` |

**OR Archived** to cold storage:
- Move to `**/.archive/YYYY-MM-DD/` (local-only, gitignored)

**Do not** let drafts accumulate indefinitely.

---

## Directory Structure

```
dev/
├── README.md           # This file (governance)
├── roadmap/            # ✅ Versioned concepts & planning (governance: roadmap/README.md)
├── scripts/            # ✅ Development automation
├── tools/              # ✅ Development utilities
├── examples/           # ✅ Reference code & demos (linked from docs/howto/)
├── tests/              # ✅ Dev-specific tests
├── build/              # ✅ Build configuration
├── architecture/       # Optional: Diagrams/sketches
├── progress/           # ⚠️ Audit needed (promote or delete)
├── .dev/               # ✅ Local experiments (gitignored)
└── .archive/           # ✅ Cold storage (gitignored)
    └── 2026-01-13/
        └── docs/       ← Old /dev/docs/ archived here
```

---

## Key Rule

**`/dev` is for development workflow.**  
**`/docs` is for project truth.**

- If something **explains how the system works** → goes to `/docs`
- If something **runs, tests, or builds** → goes to `/dev`
- If something is a **finished concept** → gets promoted to `/docs` after 2 weeks

---

## Promotion Pattern

After **~2 weeks**, content in `/dev/` must be either:

**Promoted** to `/docs`:

| Type | Destination |
|------|-------------|
| Working concepts | `docs/specs/` |
| How-to guides | `docs/howto/` |
| Architecture decisions | `docs/decisions/ADR-*.md` |
| Progress/milestones | `docs/devlog/YYYY-MM.md` |
| Long-term plan | `docs/roadmap.md` |

**OR Archived** to cold storage:
- Move to `dev/.archive/YYYY-MM-DD/` (gitignored)

**Files:**
- `ROADMAP.md` - Master roadmap document
- Version planning docs
- Architecture proposals
---

## Subdirectory Reference

### `/dev/roadmap/` ✅ Active
**Purpose:** Versioned working concepts  
**Governance:** See `roadmap/README.md`  
**Promotion:** Concepts → `/docs/specs/`, completed features → `/docs/devlog/`  

### `/dev/scripts/` ✅ Active
**Purpose:** Development automation scripts  
**Examples:** Build, test, setup, deployment scripts

### `/dev/tools/` ✅ Active
**Purpose:** Development utilities  
**Examples:** Code generators, analysis tools, build utilities

### `/dev/examples/` ✅ Active
**Purpose:** Reference code and examples (linked from `/docs/howto/`)  
**Usage:** Standalone reference implementations, not test fixtures

### `/dev/tests/` ✅ Active
**Purpose:** Development-specific tests (not in subsystem test suites)  

### `/dev/build/` ✅ Active
**Purpose:** Build configuration and packaging scripts  

### `/dev/architecture/` ⚠️ Optional
**Purpose:** Diagrams, sketches, visual architecture notes  
**Note:** Link images from `/docs/specs/` if referencing them

### `/dev/progress/` ⚠️ Audit Needed
**Status:** Historical progress tracking  
**Recommendation:** Consolidate into `docs/devlog/` or delete

### `/dev/.dev/` ✅ Local Only
**Status:** Gitignored, local-only experiments  
**Usage:** Session notes, WIP, temporary files

### `/dev/.archive/` ✅ Cold Storage
**Status:** Gitignored, historical  
**Contains:** Old versions, deprecated code, historical docs

---

## Do NOT Create

❌ `/dev/docs/` — Documentation lives in `/docs/`, not `/dev/`  
❌ `/dev/wiki/` — Wiki output, not source; use `/docs` instead  
❌ Project roadmap in `/dev/` — Use `/docs/roadmap.md`  
❌ Architecture specs in `/dev/` — Use `/docs/specs/`
