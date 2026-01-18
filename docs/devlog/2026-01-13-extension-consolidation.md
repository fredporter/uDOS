---
title: Extension Folders Consolidated to Library (2026-01-13)
status: complete
version: 1.0.0
---

# Extension Folders Consolidated to Library

## Summary

✅ **Moved 6 extension folders from root to `library/`** for cleaner workspace structure.

---

## What Changed

### Moved Folders

| Folder | Old Location | New Location |
|--------|--------------|--------------|
| gtx-form | `/gtx-form/` | `library/gtx-form/` |
| home-assistant | `/home-assistant/` | `library/home-assistant/` |
| markdown | `/markdown/` | `library/markdown/` |
| marp | `/marp/` | `library/marp/` |
| micro | `/micro/` | `library/micro/` |
| typo | `/typo/` | `library/typo/` |

### Updated Files

**`container.json` schema paths updated** in all 6 folders:
- Old: `$schema: "../container.schema.json"`
- New: `$schema: "../../container.schema.json"`

**Reason:** These files moved down one directory level, so schema reference needs one more `../`

### Verified References

Searched codebase for references to moved folders. Results:
- **Environment variables** (`.env.example`) — Just editor names, no path updates needed
- **Build scripts** (`start_udos.sh`) — References `extensions/cloned/micro` and `extensions/cloned/typo` (installed locations, not source)
- **Documentation** — File references to markdown/marp are feature names, not paths
- **Code** — No imports or hard-coded paths to these folders found

**Conclusion:** No breaking changes. All integration paths (`wrapper_path`, `handler_path`) remain unchanged.

---

## Project Structure (Updated)

```
PROJECT ROOT (cleaner)
├── AGENTS.md
├── MANIFEST.in
├── README.md
├── app/
├── bin/
├── core/
├── data/
├── dev/
├── distribution/
├── docs/
├── extensions/
├── knowledge/
├── library/                    ← ALL EXTENSIONS NOW HERE
│   ├── containers/
│   ├── fonts/
│   ├── gemini-cli/
│   ├── gtx-form/              ✨ MOVED
│   ├── handy/
│   ├── home-assistant/        ✨ MOVED
│   ├── icons/
│   ├── markdown/              ✨ MOVED
│   ├── markdown-to-pdf/
│   ├── marp/                  ✨ MOVED
│   ├── meshcore/
│   ├── micro/                 ✨ MOVED
│   ├── mistral-vibe/
│   ├── nethack/
│   ├── ollama/
│   ├── os-images/
│   ├── packages/
│   ├── piper/
│   ├── remark/
│   ├── songscribe/
│   ├── tinycore/
│   ├── typo/                  ✨ MOVED
│   └── url-to-markdown/
├── mapdata/
├── memory/
├── node_modules/
├── packages/
├── scripts/
├── setup.py
└── wizard/
```

---

## Benefits

1. **Cleaner root** — Root now only has essential folders and scripts
2. **Logical organization** — All third-party/vendor code in one place
3. **Easy to find extensions** — Know to look in `library/` for extension source
4. **Follows conventions** — Similar to how many projects organize dependencies

---

## Next Steps (Optional)

Consider also:
- Move `/data` and `/mapdata` to `memory/apps/` (user data consolidation)
- Hide `node_modules` from VS Code workspace view

---

## Verification

✅ All folders moved successfully  
✅ Container schema paths updated  
✅ No breaking code references found  
✅ Integration paths remain unchanged

---

*Consolidation Date: 2026-01-13*  
*Status: Complete*
