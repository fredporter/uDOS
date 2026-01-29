---
uid: udos-wiki-standardization-quick-ref-20260130170000-UTC-L300AB56
title: Wiki Standardization Quick Reference
tags: [wiki, documentation, quick-ref, completed]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
---

# Wiki Standardization — Quick Reference Card

**Status:** ✅ Complete (Jan 30, 2026)  
**Files Updated:** 247 total  
**Verification:** All UIDs unique, zero duplicates

---

## Overview

| Category | Files | Grid Range | Prefix |
|----------|-------|------------|--------|
| Wiki Docs | 7 | L300AB00-06 | `udos-wiki-` |
| Knowledge | 235 | L300AB26-53 | `udos-guide-` |
| Candidates | 5 | L300AB50-54 | `udos-wiki-candidate-` |
| **TOTAL** | **247** | **L300AB00-54** | — |

---

## UID Format

**Pattern:** `{prefix}-{component}-{YYYYMMDDHHMMSS}-UTC-{L###-AB##}`

### Examples by Type

**Wiki Architecture:**
```
udos-wiki-alpine-20260125080000-UTC-L300AB01
udos-wiki-beacon-20260125100000-UTC-L300AB02
udos-wiki-sonic-20260125160000-UTC-L300AB05
```

**Knowledge Guides:**
```
udos-guide-fire-20251204081800-UTC-L300AB44
udos-guide-water-20251204100000-UTC-L300AB13
udos-guide-shelter-20251204120000-UTC-L300AB14
```

**Wiki Candidates:**
```
udos-wiki-candidate-beacon-architecture-...-UTC-L300AB50
udos-wiki-candidate-self-healing-guide-...-UTC-L300AB53
```

---

## Knowledge Categories (14)

| Category | Files | Component | Grid Start | Example UID |
|----------|-------|-----------|-----------|-------------|
| fire | 20 | fire | L300AB44 | `udos-guide-fire-...` |
| water | 25 | water | L300AB45 | `udos-guide-water-...` |
| shelter | 20 | shelter | L300AB14 | `udos-guide-shelter-...` |
| food | 22 | food | L300AB15 | `udos-guide-food-...` |
| medical | 26 | medical | L300AB16 | `udos-guide-medical-...` |
| navigation | 20 | navigation | L300AB17 | `udos-guide-navigation-...` |
| tech | 8 | tech | L300AB18 | `udos-guide-tech-...` |
| tools | 15 | tools | L300AB19 | `udos-guide-tools-...` |
| survival | 26 | survival | L300AB20 | `udos-guide-survival-...` |
| making | 4 | making | L300AB21 | `udos-guide-making-...` |
| communication | 15 | communication | L300AB22 | `udos-guide-communication-...` |
| reference | 13 | reference | L300AB23 | `udos-guide-reference-...` |
| well-being | 5 | wellbeing | L300AB24 | `udos-guide-wellbeing-...` |
| community | — | community | L300AB25 | (parent README) |

---

## Frontmatter Template

### Wiki Format
```yaml
---
uid: udos-wiki-{component}-{YYYYMMDDHHMMSS}-UTC-{L###-AB##}
title: {Title}
tags: [wiki, category, subcategory]
status: living
updated: YYYY-MM-DD
spec: wiki_spec_obsidian.md
---
```

### Knowledge Format
```yaml
---
uid: udos-guide-{category}-{YYYYMMDDHHMMSS}-UTC-{L###-AB##}
title: {Title}
tags: [guide, knowledge, {category}]
status: living
updated: YYYY-MM-DD
spec: wiki_spec_obsidian.md
authoring-rules:
  - Knowledge guides use 'guide' tag
  - Content organized by technique/category
  - File-based, offline-first
---
```

---

## File Locations

### Wiki Architecture
- `/docs/wiki/ALPINE-CORE.md` → L300AB01
- `/docs/wiki/BEACON-PORTAL.md` → L300AB02
- `/docs/wiki/BEACON-QUICK-REFERENCE.md` → L300AB03
- `/docs/wiki/BEACON-VPN-TUNNEL.md` → L300AB04
- `/docs/wiki/SONIC-SCREWDRIVER.md` → L300AB05
- `/docs/wiki/WIZARD-CORE-STORY-INTEGRATION.md` → L300AB06
- `/knowledge/README.md` → L300AB00

### Knowledge Guides
- `/knowledge/{category}/{file}.md` → Each has unique UID
- 235 total content files
- 14 category READMEs + 2 core docs

### Wiki Candidates
- `/docs/wiki-candidates/BEACON-ARCHITECTURE-SUMMARY.md` → L300AB50
- `/docs/wiki-candidates/BEACON-PORTAL-DELIVERY.md` → L300AB51
- `/docs/wiki-candidates/HELP-COMMAND-QUICK-REF.md` → L300AB52
- `/docs/wiki-candidates/SELF-HEALING-GUIDE.md` → L300AB53
- `/docs/wiki-candidates/SELF-HEALING-SUMMARY.md` → L300AB54

---

## Verification Commands

### List all UIDs
```bash
# Knowledge files
find /Users/fredbook/Code/uDOS/knowledge -name '*.md' -type f | xargs grep -h '^uid:' | sort

# Wiki files
find /Users/fredbook/Code/uDOS/docs/wiki -name '*.md' -type f | xargs grep -h '^uid:' | sort

# Candidates
find /Users/fredbook/Code/uDOS/docs/wiki-candidates -name '*.md' -type f | xargs grep -h '^uid:' | sort
```

### Count total unique UIDs
```bash
find /Users/fredbook/Code/uDOS/{knowledge,docs/wiki,docs/wiki-candidates} -name '*.md' -type f 2>/dev/null | xargs grep -h '^uid:' 2>/dev/null | sort -u | wc -l
# Result: 247 ✅
```

### Find duplicates
```bash
find /Users/fredbook/Code/uDOS/{knowledge,docs/wiki,docs/wiki-candidates} -name '*.md' -type f 2>/dev/null | xargs grep -h '^uid:' 2>/dev/null | sort | uniq -d
# Result: (empty - no duplicates) ✅
```

---

## Documentation

| File | Purpose |
|------|---------|
| [FRONTMATTER-STANDARDIZATION-SUMMARY.md](FRONTMATTER-STANDARDIZATION-SUMMARY.md) | Comprehensive audit of all 247 files with details |
| [SESSION-WIKI-STANDARDIZATION-COMPLETE.md](SESSION-WIKI-STANDARDIZATION-COMPLETE.md) | Full session log with processing details |
| [WIKI-FRONTMATTER-GUIDE.md](WIKI-FRONTMATTER-GUIDE.md) | Migration guide and UID generation rules |
| [specs/wiki_spec_obsidian.md](specs/wiki_spec_obsidian.md) | Full specification reference |

---

## Next Steps

1. ✅ All files standardized with unique UIDs
2. ⏳ Import into Obsidian vault
3. ⏳ Validate cross-reference links
4. ⏳ Promote selected candidates to wiki/
5. ⏳ Build UID-based search index

---

**Quick Links:**
- See [FRONTMATTER-STANDARDIZATION-SUMMARY.md](FRONTMATTER-STANDARDIZATION-SUMMARY.md) for detailed audit
- See [SESSION-WIKI-STANDARDIZATION-COMPLETE.md](SESSION-WIKI-STANDARDIZATION-COMPLETE.md) for session details
- Check `/docs/WIKI-FRONTMATTER-GUIDE.md` for migration reference

**Status:** Ready for Obsidian import and integration  
**Completed:** 2026-01-30 16:00 UTC
