# 🎯 QUICK REFERENCE - Path Updates Needed

**Last Updated:** 2026-01-18  
**Status:** Ready to execute  
**Effort:** ~45 minutes total

---

## 📋 The 3 Key Files to Update

### 1️⃣ AGENTS.md (Most Important)

**Location:** `/Users/fredbook/Code/uDOS/AGENTS.md`  
**References:** 12 instances  
**Update pattern:**

```
/wizard/                    →  /public/wizard/
/wizard/extensions/         →  /public/extensions/
```

**Specific lines:**

- Line 160: `/wizard/config/wizard.json`
- Line 202: `/dev/goblin/config/goblin.json` (NO CHANGE)
- Line 235: `/wizard/extensions/`
- Line 240: Already correct
- Line 247: Note about plugins/extensions

### 2️⃣ docs/roadmap.md (Comprehensive)

**Location:** `/Users/fredbook/Code/uDOS/docs/roadmap.md`  
**References:** 25+ instances  
**Update pattern:** Same as above

**Key sections:**

- Line 462: Configuration paths
- Line 791-792: Service paths
- Line 1012: Relative doc paths
- Various other `/wizard/` references throughout

### 3️⃣ .vibe/CONTEXT.md (Supporting)

**Location:** `/Users/fredbook/Code/uDOS/.vibe/CONTEXT.md`  
**References:** 6 instances  
**Updates needed:**

- Line 21: `[core/README.md]` ✅ OK (keep as-is)
- Line 36: `[wizard/README.md]` → `[public/wizard/README.md]`
- Line 43: `[extensions/README.md]` → `[public/extensions/README.md]`

---

## 📊 Secondary Files (If Needed)

| File                                              | Lines   | Pattern          | Priority |
| ------------------------------------------------- | ------- | ---------------- | -------- |
| `.github/instructions/wizard.instructions.md`     | 217     | Verify paths     | Low      |
| `.github/instructions/extensions.instructions.md` | Various | Verify paths     | Low      |
| `docs/howto/wizard-dev-mode.md`                   | 264-267 | `/wizard/` paths | Low      |
| `docs/howto/OFFLINE-AI-SETUP.md`                  | 692     | `/wizard/`       | Low      |
| `docs/howto/SVG-GRAPHICS-GENERATION.md`           | 553-554 | `/wizard/`       | Low      |

---

## ⚡ Quick Execute (If Doing Now)

### Option A: Manual (15-30 min)

1. Open AGENTS.md
2. Find & Replace: `/wizard/` → `/public/wizard/`
3. Find & Replace: `/extensions/` → `/public/extensions/`
4. Open roadmap.md
5. Repeat steps 2-3
6. Open .vibe/CONTEXT.md
7. Manual edits (only 6 references)
8. Spot check a few links
9. Done!

### Option B: Batch with Tool (5 min)

Use `multi_replace_string_in_file` to update all in one call:

- Provide oldString/newString pairs
- All replacements happen together
- Much faster for large files

---

## ✅ Verification Checklist

After updates, verify with:

```bash
# 1. Check no broken links (VS Code will warn)
# Look in VS Code problems panel

# 2. Quick Python import test
python -c "from core import __version__"
# Should show no errors

# 3. Build test
cd app && npm run build
# Should complete successfully

# 4. Optional: Run shakedown
./start_udos.sh
# Type: SHAKEDOWN
```

---

## 🎯 Expected Results After Update

```
✅ AGENTS.md will reference /public/wizard/ and /public/extensions/
✅ roadmap.md will have consistent paths
✅ .vibe/CONTEXT.md will point to correct locations
✅ All links will be valid and work
✅ No broken references in documentation
✅ Code paths don't change (already correct)
```

---

## 🚀 Git Commit When Done

```bash
git add -A
git commit -m "docs: update paths after restructure (wizard→public/wizard)"
git log --oneline | head -3
```

---

## 💡 Pro Tips

1. **Use Find & Replace with Whole Word matching:**
   - Prevents accidental replacements
   - e.g., find `/wizard/` (with slashes) not `wizard` alone

2. **Test each major file after update:**
   - VS Code will show red squiggles on broken links
   - Click through a few links to verify they resolve

3. **Keep old analysis documents:**
   - RESTRUCTURE-ANALYSIS.md
   - RESTRUCTURE-VALIDATION.md
   - Good reference for what was moved where

4. **Consider doing in phases:**
   - Phase 1: AGENTS.md + roadmap.md (high impact)
   - Phase 2: Supporting docs (.vibe, howto, decisions)
   - Phase 3: Run full test suite

---

## 📞 Need Help?

- **Got stuck on a path?** → Check RESTRUCTURE-ANALYSIS.md
- **Want to understand structure?** → Check RESTRUCTURE-VALIDATION.md
- **Need context?** → This file (quick ref)

---

## ⏱️ Timeline

- **Phase 1 (AGENTS.md + roadmap.md):** 30 min
- **Phase 2 (Supporting docs):** 15 min
- **Phase 3 (Testing):** 10 min
- **Total:** ~55 min

**Could be faster:** If using multi_replace_string_in_file tool = ~15 min total

---

**Status:** Ready to proceed whenever! This is a clean, straightforward task. ✅
