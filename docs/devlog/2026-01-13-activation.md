---
title: Documentation Consolidation & Versioning Activation (2026-01-13)
status: complete
version: 1.0.0
activated: 2026-01-13
---

# Documentation Consolidation & Versioning Activation

## Summary

✅ **Completed:** Consolidated documentation structure and activated versioning for `dev/roadmap/` concepts.

---

## 🎯 What Was Activated

### 1. Promoted Concepts to `/docs/specs/`

Two mature concepts were promoted from `dev/roadmap/` to formal specifications:

| Concept | Source | Destination | Version |
|---------|--------|-------------|---------|
| **Vibe Setup** | `VibeCLI.md` | `docs/specs/vibe-setup.md` | v1.0.0 |
| **Three-Workspace Architecture** | `3-workspaces.md` | `docs/specs/workspace-architecture.md` | v1.0.0 |

**Why:** These concepts had stabilized into the actual project structure and needed to be part of the canonical documentation spine.

---

### 2. Versioning System for `dev/roadmap/`

Added frontmatter versioning to all files:

```yaml
---
title: Human-readable title
status: active | archived | deprecated
version: 1.0.0
date: 2026-01-13
note: Optional context
---
```

**Files Updated:**
- `VibeCLI.md` — Updated to archived with pointer to promoted spec
- `3-workspaces.md` — Updated to archived with pointer to promoted spec
- `sync-vscode.md` — Tagged as active (v1.0.0)
- `ROADMAP.md` — Inherently active (detailed historical reference)

---

### 3. Updated Navigation

#### `/docs/_index.md`
Added new "Architecture & Setup" section linking to promoted specs:
```markdown
### Architecture & Setup
- [Three-Workspace Architecture](specs/workspace-architecture.md)
- [Vibe Setup (Offline Agent)](specs/vibe-setup.md)
```

#### `.vibe/CONTEXT.md`
Updated architecture reference to point to formal spec:
```markdown
### Three Workspaces Model
- **Read formal spec:** [docs/specs/workspace-architecture.md](../docs/specs/workspace-architecture.md)
```

---

### 4. Created `dev/roadmap/README.md`

New governance file for the working scratchpad folder:
- Explains folder purpose (working concepts, not truth)
- Documents promotion pipeline
- Lists all files with status
- Provides audit checklist

---

## 📋 Current Documentation Structure

```
docs/                           ← Source of truth (GitHub)
├── _index.md                   ← Entry point (updated)
├── roadmap.md                  ← NOW/NEXT/LATER
├── devlog/                     ← Monthly development notes
├── decisions/                  ← Architecture Decision Records
├── howto/                      ← Repeatable procedures
└── specs/                      ← Finalized technical specs
    ├── vibe-setup.md           ← ✅ NEW (promoted)
    └── workspace-architecture.md ← ✅ NEW (promoted)

dev/roadmap/                    ← Working scratchpad (NOT source of truth)
├── README.md                   ← ✅ NEW (governance)
├── ROADMAP.md                  ← Active (detailed history)
├── sync-vscode.md              ← Active (device sync strategy)
├── agents-example.md           ← ⚠️ Audit needed
├── localai.md                  ← ⚠️ Audit needed
├── VibeCLI.md                  ← ➡️ Archived (see docs/specs/vibe-setup.md)
└── 3-workspaces.md             ← ➡️ Archived (see docs/specs/workspace-architecture.md)

core/docs/                      ← Technical authority (local)
app/docs/                       ← Technical authority (local)
wizard/docs/                    ← To be created (planned)
```

---

## 🚀 How Versioning Now Works

### File Status Lifecycle

1. **Draft** (`.dev/` or initial concept)
   - Status: `draft`
   - Location: Local-only, gitignored
   - Lifespan: Experimental

2. **Active Concept** (`dev/roadmap/`)
   - Status: `active`
   - Version: Semver (e.g., v1.0.0)
   - Lifespan: 2-4 weeks

3. **Promoted Spec** (`docs/specs/` or elsewhere)
   - Status: `active`
   - Version: Semver (immutable in `/docs`)
   - Original file: Archived with pointer
   - Lifespan: Long-term (part of project truth)

4. **Archived** (`.archive/YYYY-MM-DD/`)
   - Status: `archived`
   - Reason: No longer active
   - Lifespan: Historical reference

---

## ✅ Activation Checklist

### Completed
- [x] Promote VibeCLI.md → docs/specs/vibe-setup.md (v1.0.0)
- [x] Promote 3-workspaces.md → docs/specs/workspace-architecture.md (v1.0.0)
- [x] Update docs/_index.md with new specs links
- [x] Update .vibe/CONTEXT.md with new architecture reference
- [x] Add versioning headers to all dev/roadmap/ files
- [x] Create dev/roadmap/README.md (governance)
- [x] Archive pointers in original files (VibeCLI.md, 3-workspaces.md)

### To Do (Not Required Now)
- [ ] Audit agents-example.md (promote or archive?)
- [ ] Audit localai.md (promote or archive?)
- [ ] Create wizard/docs/ (planned for v1.0.2.0)
- [ ] Audit dev/docs/ folder (consolidate relevant files)

---

## 📊 Statistics

| Metric | Before | After |
|--------|--------|-------|
| Files in `docs/specs/` | 0 | 2 |
| Promoted specs | — | 2 |
| Files with versioning headers | ~2 | 8+ |
| Navigation hubs updated | 2 | 2 |
| New governance files | 0 | 1 |

---

## 🎯 Next Steps

### This Round (Done ✅)
1. ✅ Version the dev/roadmap files
2. ✅ Activate the sync-vscode setup (still in dev as active reference)
3. ✅ Promote the finalized specs

### Next Round (Soon)
1. **Audit remaining concepts**
   - Review `agents-example.md`, `localai.md`
   - Decide: promote to `/docs/howto/`, or archive?

2. **Establish Wizard documentation**
   - Create `wizard/docs/` folder
   - Document model routing, AI providers, webhooks
   - Link from `docs/_index.md`

3. **Create example promotion**
   - Document the promotion workflow with a real example
   - Add to `docs/howto/doc-maintenance.md`

---

## 🔗 Key Files to Review

- [docs/specs/vibe-setup.md](../../docs/specs/vibe-setup.md) — New promoted spec
- [docs/specs/workspace-architecture.md](../../docs/specs/workspace-architecture.md) — New promoted spec
- [docs/_index.md](../../docs/_index.md) — Updated navigation
- [dev/roadmap/README.md](./README.md) — New governance file
- [.vibe/CONTEXT.md](../../.vibe/CONTEXT.md) — Updated context reference

---

## 💾 Archive Info

Archived concept files (still in place but marked as deprecated):
- `dev/roadmap/VibeCLI.md` — Header updated 2026-01-13
- `dev/roadmap/3-workspaces.md` — Header updated 2026-01-13

These remain in the folder for historical reference but now point to their promoted versions.

---

## ✨ Why This Matters

1. **Single source of truth** — `/docs` is now the canonical project documentation
2. **Versioning discipline** — All concepts have lifecycle management
3. **Transparent promotion** — Clear pipeline from drafts to specs
4. **Device sync ready** — Vibe, VS Code, and Copilot share the same context
5. **Team scalability** — New contributors can follow the workflow

---

*Activation Date: 2026-01-13*  
*Promoted Files: 2*  
*Navigation Updates: 2*  
*Status: Complete ✅*
