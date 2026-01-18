# Repository Restructure Analysis & Cleanup Report

**Date:** 2026-01-18  
**Status:** ✅ Pre-cleanup analysis complete  
**Scope:** Full path audit, documentation updates, old file cleanup

---

## Executive Summary

The repository has been successfully restructured with a cleaner organization:

### New Directory Layout

```
/Users/fredbook/Code/uDOS/
├── core/                    # TypeScript runtime (v1.1.0)
├── app/                     # Tauri/Svelte app (v1.0.3.0)
├── docs/                    # Engineering documentation
├── data/                    # Data/fixtures
├── dev/                     # Development tools
│   └── goblin/             # Goblin Dev Server (v0.1.0.0)
├── library/                # Library/assets (MOVED to public/)
├── memory/                 # User data, logs, tests
├── public/                 # 📦 NEW: Public-facing code
│   ├── wizard/            # Wizard Server v1.1.0.0 (MOVED from root)
│   ├── extensions/        # Public extensions (MOVED from root)
│   ├── knowledge/         # Knowledge base
│   ├── library/           # Assets/library
│   └── distribution/      # Release artifacts
├── private/               # Private data
├── wiki/                  # Wiki
└── bin/                   # Launch scripts
```

### Key Structural Changes

| Component         | Old Location   | New Location          | Status                   |
| ----------------- | -------------- | --------------------- | ------------------------ |
| **Wizard Server** | `/wizard/`     | `/public/wizard/`     | ✅ Moved                 |
| **Extensions**    | `/extensions/` | `/public/extensions/` | ✅ Moved                 |
| **Knowledge**     | `/knowledge/`  | `/public/knowledge/`  | ✅ Moved                 |
| **Library**       | `/library/`    | `/public/library/`    | ✅ Moved                 |
| **Core (TS)**     | `/core/`       | `/core/`              | ✅ Stable                |
| **App**           | `/app/`        | `/app/`               | ✅ Stable                |
| **Dev/Goblin**    | `/dev/goblin/` | `/dev/goblin/`        | ✅ Stable                |
| **.archive**      | N/A            | `/.archive/`          | ✅ Exists (mostly empty) |

---

## 🔍 Audit Findings

### ✅ Clean-Up (No Issues Found)

1. **No broken symlinks**
   - Scanned: No symlinks detected at all
   - Status: Clean

2. **No bad imports**
   - Scanned Python files for `core-beta`, `old_`, deprecated paths
   - Status: Clean (no references found)

3. **No .git remnants**
   - Only one `.git` directory at root (correct)
   - Removed old archives as intended
   - Status: Clean

4. **.archive directory**
   - Currently mostly empty
   - Safe to leave as-is (useful for future archived content)
   - Status: Clean

### ⚠️ Documentation Path Updates Required

**Files needing updates:**

1. **AGENTS.md** (12+ references)
   - Line 160: `/wizard/config/wizard.json` → `/public/wizard/config/wizard.json`
   - Line 202: `/dev/goblin/config/goblin.json` (correct)
   - Line 235: `/wizard/extensions/` → `/public/wizard/extensions/`
   - Line 240: `/dev/goblin/services/` (correct)
   - Lines 146, 247: `/plugins` → should reference `/public/extensions/`

2. **docs/roadmap.md** (25+ references)
   - Line 462, 791-792, etc.: `/wizard/` → `/public/wizard/`
   - Lines 536, 703: `/core-beta/` references (still valid but noted as deprecation context)
   - Line 1012: `../wizard/docs/` → `../public/wizard/docs/`
   - Line 1371: `/wizard/tools/bizintel/` → verify against actual location

3. **.github/instructions/wizard.instructions.md** (1 reference)
   - References correct path: `wizard/` prefix in applyTo OK (relative)

4. **.github/instructions/extensions.instructions.md** (2 references)
   - Line 154, 238-239: Path references need context validation

5. **docs/decisions/ADR-0002-typescript-runtime-for-mobile.md** (1 reference)
   - Line 162: `/dev/goblin/README.md` (correct path)

6. **.vibe/CONTEXT.md** (6 references)
   - Lines 21-22, 36-37, 43: References to `wizard/` and `extensions/`
   - Status: Need update to `/public/wizard/` and `/public/extensions/`

7. **docs/howto/** files (10+ references)
   - `OFFLINE-AI-SETUP.md` line 692
   - `SVG-GRAPHICS-GENERATION.md` lines 419, 553-554
   - `wizard-dev-mode.md` lines 264-267
   - `NOTIFICATION-HISTORY.md` lines 563, 684
   - All need `/wizard/` → `/public/wizard/` updates

8. **docs/V1.0.7.0-SPEC-COMPLETE.md** (3 references)
   - Lines 116, 251: `/core/` references (mostly OK for current structure)

---

## 🧹 Cleanup Tasks

### Phase 1: Critical Path Updates (HIGH PRIORITY)

These files reference moved directories and must be updated:

```bash
# Files to update
AGENTS.md                                          # 12 references to /wizard/
docs/roadmap.md                                    # 25 references to /wizard/
.vibe/CONTEXT.md                                   # 6 references to /wizard/ and /extensions/
.github/instructions/wizard.instructions.md        # Verify paths
.github/instructions/extensions.instructions.md    # Verify paths
```

**Pattern to apply:**

```
/wizard/  → /public/wizard/
/extensions/  → /public/extensions/
/knowledge/  → /public/knowledge/
/library/  → /public/library/ (if needed)
```

### Phase 2: Verify Build Scripts & Launchers

These files may reference old paths:

```bash
bin/Launch-*.command          # Check for hardcoded paths
bin/start_udos.sh             # Verify path references
setup.py                      # Check package paths
package.json                  # Verify workspace references
```

### Phase 3: Cross-Reference Validation

Check for any internal references:

```bash
# Check if any Python/TS imports reference old paths
grep -r "from.*wizard import\|from.*extensions import" --include="*.py" --include="*.ts"
```

---

## 📋 Detailed Path Replacement List

### AGENTS.md

| Line | Old                              | New                                            | Context                    |
| ---- | -------------------------------- | ---------------------------------------------- | -------------------------- |
| 146  | `/api/v1/plugins/*`              | `/api/v1/extensions/*`                         | Plugin repository endpoint |
| 160  | `/wizard/config/wizard.json`     | `/public/wizard/config/wizard.json`            | Wizard config path         |
| 202  | `/dev/goblin/config/goblin.json` | ✅ Correct                                     | Goblin config path         |
| 235  | `/wizard/extensions/`            | `/public/wizard/extensions/`                   | Wizard extensions location |
| 240  | `/dev/goblin/services/`          | ✅ Correct                                     | Goblin services location   |
| 247  | `/plugins` legacy note           | Update note to reference `/public/extensions/` | Archive note               |

### docs/roadmap.md

| Lines   | Old Pattern         | New Pattern                | Notes               |
| ------- | ------------------- | -------------------------- | ------------------- |
| 462     | `/wizard/config/`   | `/public/wizard/config/`   | Configuration paths |
| 791-792 | `/wizard/services/` | `/public/wizard/services/` | Service file paths  |
| 1012    | `../wizard/docs/`   | `../public/wizard/docs/`   | Relative doc path   |
| Various | `/wizard/` prefix   | `/public/wizard/` prefix   | All references      |

### .vibe/CONTEXT.md

Lines 21-22, 36-37, 43:

```
- [core/README.md]  ✅ OK (core is at root)
- [wizard/README.md]  → [public/wizard/README.md]
- [extensions/README.md]  → [public/extensions/README.md]
```

### docs/howto/\* files

Update pattern in:

- `OFFLINE-AI-SETUP.md`
- `SVG-GRAPHICS-GENERATION.md`
- `wizard-dev-mode.md`
- `NOTIFICATION-HISTORY.md`

---

## 🎯 Verification Checklist

After updates, verify:

- [ ] No broken markdown links (check VS Code link validation)
- [ ] All file references resolve correctly
- [ ] Launch scripts work without path errors
- [ ] Python imports resolve (test with: `python -c "from wizard import ..."`)
- [ ] TypeScript imports resolve (check app/tsconfig.json)
- [ ] All ADR and devlog links work
- [ ] Build/test tasks execute successfully
- [ ] No 404s when following docs

---

## 📝 Implementation Plan

### Step 1: Update Primary Documentation (AGENTS.md, roadmap.md)

```bash
# Use multi_replace_string_in_file to update all AGENTS.md paths at once
# Priority: AGENTS.md (foundational), roadmap.md (large file with many refs)
```

### Step 2: Update Supporting Docs

```bash
# .vibe/CONTEXT.md
# .github/instructions/*.md
# docs/howto/* files
# docs/*.md files
```

### Step 3: Verify Imports & Config

```bash
# Check bin/, setup.py, package.json
# Verify no hardcoded paths
# Test launcher scripts
```

### Step 4: Run Tests

```bash
# Verify markdown links don't break
# Run test suite to ensure paths are correct
# Check build process
```

---

## ✨ Benefits of New Structure

1. **Clear Public/Private Separation**
   - `/public/` contains distributable code (Wizard, Extensions, Knowledge)
   - `/private/` contains secrets and user data
   - Better for security and deployment

2. **Simplified Root Directory**
   - Easier to find core components (core, app, docs)
   - Dev tools in `/dev/`, builds in `/public/`
   - Cleaner workspace root

3. **Distribution-Ready**
   - `/public/distribution/` now contains release artifacts
   - Easy to identify what gets distributed vs. kept local

4. **Backward Compatible**
   - Core runtime structure unchanged
   - App structure unchanged
   - Just reorganized Wizard, Extensions, Knowledge locations

---

## 🔗 Related Documentation

- [AGENTS.md](./AGENTS.md) - Architecture reference
- [docs/roadmap.md](./docs/roadmap.md) - Implementation roadmap
- [.github/copilot-instructions.md](./.github/copilot-instructions.md) - Build instructions

---

## 📌 Next Steps

1. ✅ **This analysis complete** — Understand what moved where
2. 🔄 **Update documentation** — Use tools to batch-replace paths
3. ✔️ **Verify imports** — Test that code references still work
4. 🧪 **Run test suite** — Ensure nothing breaks
5. 📦 **Update launcher scripts** — Test bin/ command execution

---

**Status:** Ready for Path Update Phase  
**Estimated Time:** 30-45 minutes  
**Risk Level:** Low (documentation-only changes, clean imports, no symlinks)
