---
title: Documentation & Dev Structure Consolidated (2026-01-13)
status: complete
version: 1.0.0
---

# Documentation & Dev Folder Consolidation

## ✅ Changes Completed

### 1. Deleted `/dev/docs/` Folder
- **Archived to:** `dev/.archive/2026-01-13/docs/`
- **Files archived:**
  - `EXTENSION-SYSTEM-GUIDE.md` (Phase 2 planning)
  - `TINYCORE-REFACTOR-COMPLETE.md` (v1.0.0.0 historical)
  - `v1.0.0.2-POLICY-INFRASTRUCTURE.md` (transport policy draft)

**Reason:** `/dev/docs/` violates the single-source-of-truth principle. Documentation belongs in `/docs/`.

---

### 2. Clarified `/dev` Folder Purpose
Updated `/dev/README.md` to clarify what belongs in `/dev`:

**✅ KEEPS:**
- `roadmap/` — Versioned working concepts (not source of truth)
- `scripts/` — Development automation
- `tools/` — Development utilities
- `examples/` — Reference code
- `tests/` — Dev-specific tests
- `build/` — Build configuration
- `.dev/` — Local experiments (gitignored)
- `.archive/` — Cold storage (gitignored)

**❌ DELETES:**
- `/dev/docs/` — Use `/docs` instead
- `/dev/wiki/` — Wiki is output, not source
- Project roadmap in `/dev/` — Use `/docs/roadmap.md`
- Architecture specs in `/dev/` — Use `/docs/specs/`

---

## 📊 Final Structure

```
PROJECT ROOT
├── /docs                        ← SOURCE OF TRUTH (GitHub)
│   ├── _index.md               (entry point)
│   ├── roadmap.md              (NOW/NEXT/LATER - primary)
│   ├── devlog/                 (monthly development notes)
│   │   ├── 2026-01.md
│   │   └── 2026-01-13-activation.md
│   ├── decisions/              (ADRs - immutable)
│   ├── howto/                  (procedures & guides)
│   ├── specs/                  (finalized specs)
│   │   ├── vibe-setup.md       ✨ PROMOTED
│   │   └── workspace-architecture.md ✨ PROMOTED
│   └── (subsystem-specific docs below)
│
├── core/
│   ├── docs/                   (Core technical authority)
│   ├── README.md
│   └── ...
│
├── app/
│   ├── docs/                   (App technical authority)
│   ├── README.md
│   └── ...
│
├── wizard/
│   ├── README.md               (link to docs/specs/)
│   └── docs/                   (Wizard technical authority - TBD)
│
├── /dev                        ← DEVELOPMENT WORKSHOP (tools, scripts, concepts)
│   ├── README.md               (governance - updated)
│   ├── roadmap/                (✅ Active concept folder)
│   │   ├── README.md           (versioning rules)
│   │   ├── ROADMAP.md          (detailed history)
│   │   └── sync-vscode.md      (active concept)
│   ├── scripts/                (automation scripts)
│   ├── tools/                  (development utilities)
│   ├── examples/               (reference code)
│   ├── tests/                  (dev-specific tests)
│   ├── build/                  (build config)
│   ├── .dev/                   (local experiments, gitignored)
│   └── .archive/               (cold storage, gitignored)
│       └── 2026-01-13/
│           └── docs/           ← Old /dev/docs/ archived here
│
└── (other subsystems)
```

---

## 🎯 Key Principles (Now Clear)

### 1. Single Source of Truth
- **All project documentation** lives in `/docs/`
- Subsystems have **technical reference** in their own `/docs/` folders
- `/dev/` is **supporting infrastructure**, not documentation

### 2. Clear `/dev` Purpose
- `/dev/` is the **engineering workshop**
- Contains tools, scripts, automation, examples
- **Working concepts** in `roadmap/` with versioning
- **Not** the primary documentation spine

### 3. Example Files
**Where examples live:**
```
examples/                       ← Standalone reference code
├── vibe/                       (linked from docs/howto/setup-devstral.md)
├── extensions/                 (linked from docs/howto/extensions.md)
├── handlers/                   (linked from docs/howto/handlers.md)
└── services/                   (linked from docs/howto/services.md)
```

**How they're used:**
- In `/docs/howto/*.md`, include: `See examples in examples/vibe/`
- Readers can browse working examples to understand patterns
- Not committed as part of docs, but linked from docs

---

## 🚀 Do You Need `/dev` Folder?

### YES, you should keep it for:
✅ Development automation (`scripts/`, `tools/`)  
✅ Build configuration (`build/`)  
✅ Reference examples (`examples/`)  
✅ Working concepts that evolve (`roadmap/`)  

### NO, don't use it for:
❌ Documentation (use `/docs`)  
❌ Project roadmap (use `/docs/roadmap.md`)  
❌ Long-term specs (use `/docs/specs/`)  
❌ Architecture decisions (use `/docs/decisions/`)  

---

## 📖 Example: How Documentation Flows

```
Working Concept (2 weeks active in /dev/roadmap/)
        ↓
    Matures into specs/decisions/procedures
        ↓
Promoted to /docs (roadmap.md, specs/, howto/, decisions/)
        ↓
    Can be archived if superseded
        ↓
Archived to dev/.archive/YYYY-MM-DD/
```

---

## 🔗 Updated Files

- ✅ `docs/_index.md` — Links to promoted specs
- ✅ `docs/devlog/2026-01-13-activation.md` — Activation summary
- ✅ `/dev/README.md` — Governance clarified
- ✅ `/dev/roadmap/README.md` — Versioning rules
- ✅ `.vibe/CONTEXT.md` — References canonical docs
- ✅ `dev/.archive/2026-01-13/docs/` — Old `/dev/docs/` archived

---

## ✨ Result

You now have:

1. **One source of truth** (`/docs`)
2. **Clear dev workshop** (`/dev` for tools/scripts only)
3. **Transparent promotion** (concepts → /docs after validation)
4. **No doc sprawl** (no more /dev/docs/ confusion)
5. **Scalable structure** (new contributors understand the pattern)

---

*Consolidation Date: 2026-01-13*  
*Status: Complete ✅*
