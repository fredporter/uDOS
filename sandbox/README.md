# Sandbox - Runtime User Workspace

**Version:** 2.0.1  
**Purpose:** Gitignored runtime workspace for user files, logs, and temporary content

---

## Overview

`/sandbox/` is the **runtime-only** workspace for uDOS. All files here are **gitignored** (not tracked in version control). This is where user-generated content, logs, and temporary files live.

### ⚠️ Important: Development vs Runtime

- **Development work** (tracked in git): Use `/dev/` directory
  - Session logs → `/dev/sessions/`
  - Roadmap & planning → `/dev/roadmap/`
  - Development tools → `/dev/tools/`

- **Runtime files** (gitignored): Use `/sandbox/` directory (this folder)
  - User scripts → `sandbox/ucode/`
  - User data → `sandbox/user/`
  - Logs → `sandbox/logs/`
  - Drafts → `sandbox/drafts/`

---

## Directory Structure

```
sandbox/
├── ucode/        # User .upy scripts (gitignored)
├── user/         # User data files (planets.json, USER.UDT)
├── logs/         # Runtime logs (dev, error, session)
├── drafts/       # Work-in-progress content
├── docs/         # Draft documentation (before promoting to wiki)
├── workflow/     # uCODE workflow automation scripts
└── trash/        # Temporary files (auto-cleaned by CLEAN command)
```

---

## Usage Guidelines

### ✅ Use Sandbox For:

1. **Testing Scripts** - `sandbox/ucode/test_*.upy`
2. **User Data** - `sandbox/user/planets.json`
3. **Draft Docs** - `sandbox/docs/new-feature.md`
4. **Temporary Files** - `sandbox/trash/temp.txt`
5. **Runtime Logs** - `sandbox/logs/dev.log`

### ❌ Don't Use Sandbox For:

1. **Development session logs** → Use `/dev/sessions/`
2. **Project planning** → Use `/dev/roadmap/`
3. **Migration tools** → Use `/dev/tools/`
4. **Core documentation** → Use `wiki/` or `core/docs/`

---

## See Also

- `/dev/` - Development workspace (tracked in git)
- `CLEAN` command - Cleanup sandbox files
- `TIDY` command - Organize sandbox structure
- `.gitignore` - Gitignore rules
