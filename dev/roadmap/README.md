---
title: Dev Roadmap & Concepts (Working Folder)
last_updated: 2026-01-13
---

# Dev Roadmap & Concepts

This folder is a **working scratchpad** for roadmap planning, architecture concepts, and implementation strategy.

---

## 📋 What's Here?

| File | Status | Purpose |
|------|--------|---------|
| `ROADMAP.md` | 🔄 Active | Detailed historical roadmap (working reference, not primary source) |
| `sync-vscode.md` | ✅ Active | VS Code settings & device sync strategy |
| `agents-example.md` | ⚠️ Check | Example Agent setup (needs audit) |
| `localai.md` | ⚠️ Check | LocalAI exploration (needs audit) |
| `VibeCLI.md` | ➡️ Promoted | **See:** [docs/specs/vibe-setup.md](../../docs/specs/vibe-setup.md) |
| `3-workspaces.md` | ➡️ Promoted | **See:** [docs/specs/workspace-architecture.md](../../docs/specs/workspace-architecture.md) |
| `wizard_model_routing_policy.md` | ➡️ Moved | **See:** [docs/decisions/wizard-model-routing-policy.md](../../docs/decisions/wizard-model-routing-policy.md) |
| `Nethack Sprites.md` | 🗄️ Archive | Historical artifact |

---

## 🎯 File Versioning Rules

### Every File Should Have a Header
```yaml
---
title: Human-readable title
status: active | archived | deprecated
version: 1.0.0
date: 2026-01-13
note: Optional context
---
```

### Status Meanings
- **active** — Currently used; maintained
- **archived** — Promoted to `/docs` with a pointer
- **deprecated** — No longer relevant; candidate for archive

---

## ✅ Promotion Pipeline

### Step 1: Active Concept
Work in `.dev/` or `dev/roadmap/` freely with status `active`.

### Step 2: Maturity Check (~2 weeks)
If still useful after 2 weeks, **promote** to `/docs`:

| Type | Destination |
|------|-------------|
| Release/milestone | `docs/devlog/YYYY-MM.md` |
| Architecture decision | `docs/decisions/ADR-####-*.md` |
| Procedure | `docs/howto/*.md` |
| Technical spec | `docs/specs/*.md` |

### Step 3: Update Original File
Replace content with a frontmatter pointer:
```yaml
---
title: [Original Title] (Archived)
status: archived
archived_to: docs/path/file.md
---

**This file has been promoted.**

👉 **Read instead:** [docs/path/file.md](../../docs/path/file.md)
```

### Step 4: Archive (Optional)
If a file is no longer active, move to:
```
.archive/YYYY-MM-DD/filename.md
```

---

## 📊 Current Promotion Status

### ✅ Recently Promoted (2026-01-13)
- `VibeCLI.md` → `docs/specs/vibe-setup.md` (v1.0.0)
- `3-workspaces.md` → `docs/specs/workspace-architecture.md` (v1.0.0)

### 🔄 Active & Maintained
- `sync-vscode.md` — Relates to vibe-setup.md section 2
- `ROADMAP.md` — Detailed historical reference

### ⚠️ Needs Audit
- `agents-example.md` — Is this still relevant? Promote or archive?
- `localai.md` — Active project or exploratory?

### 🗄️ Archive Candidates
- `Nethack Sprites.md` — Move to `.archive/` if not active
- `wizard_model_routing_policy.md` — Already moved to `docs/decisions/`

---

## 🚀 How to Use This Folder

### To Add a New Concept
1. Create a file with frontmatter header (see rules above)
2. Set `status: active` or `status: draft` (if in `.dev/`)
3. Work freely
4. After ~2 weeks: promote to `/docs` or archive

### To Reference a File Here
- If **active & stable**: Link to it directly
- If **promoted**: Point to `/docs` version with a note
- If **exploratory**: Keep in `.dev/` (local-only)

### To Maintain This Folder
- Monthly: Check for files due for promotion/archival
- Weekly: Update this README with new files

---

## 📌 Important Links

- **Project Truth:** [docs/_index.md](../../docs/_index.md)
- **Roadmap (Primary):** [docs/roadmap.md](../../docs/roadmap.md)
- **Dev Log (Monthly):** [docs/devlog/](../../docs/devlog/)
- **Architecture Specs:** [docs/specs/](../../docs/specs/)

---

## ❓ Questions?

- **Where should I put this idea?** → Depends on maturity. Drafts in `.dev/`, concepts here, truth in `/docs`.
- **How do I know when to promote?** → After ~2 weeks if still useful.
- **Can I edit promoted files?** → No. Create a new concept or ADR instead.
- **What if this roadmap conflicts with `/docs/roadmap.md`?** → `/docs` is authoritative. This folder is working notes.

---

*Last updated: 2026-01-13*  
*For project-wide roadmap, see: [docs/roadmap.md](../../docs/roadmap.md)*
