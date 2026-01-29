---
uid: udos-wiki-20260130120100-L300AB01
title: Wiki Frontmatter Guide
tags: [wiki, spec, documentation]
status: living
updated: 2026-01-30
---

# Wiki Frontmatter Standard for uDOS

**Version:** 1.0  
**Status:** Reference  
**Scope:** All documentation pages using `wiki_spec_obsidian.md` standard

---

## Overview

All wiki documents in uDOS must include YAML frontmatter following the `wiki_spec_obsidian.md` specification. This guide provides:

1. Required field descriptions
2. UID generation rules
3. Status value definitions
4. Migration examples
5. Validation checklist

---

## Required Fields

### `uid` (String)

**Format:** `udos-wiki-{COMPONENT}-{TIMESTAMP}-{TIMEZONE}-{GRID_LOCATION}`

**Components:**
- `COMPONENT`: Descriptive name (alpine, beacon, sonic, wizard, knowledge, etc.)
- `TIMESTAMP`: `YYYYMMDDHHmmss` (UTC, staggered for unique creation times)
- `TIMEZONE`: UTC (or specific timezone if applicable)
- `GRID_LOCATION`: Grid coordinate `L###-AB##` (optional fallback: `L300-AB00`)

**Examples:**
```
uid: udos-wiki-alpine-20260125080000-UTC-L300AB01
uid: udos-wiki-beacon-20260125100000-UTC-L300AB02
uid: udos-wiki-sonic-20260125160000-UTC-L300AB05
uid: udos-wiki-wizard-20260128090000-UTC-L300AB06
uid: udos-wiki-knowledge-20260130120000-UTC-L300AB00
```

**Rules:**
- Generated at document creation
- NEVER modified (immutable identifier)
- Uniqueness guaranteed by component + timestamp + location
- Stagger timestamps across creation date for realistic variation
- Use original creation timestamp for backfilled docs

### `title` (String)

Human-readable page title.

**Rules:**
- Matches primary heading
- MAY change without affecting uid
- Use title case
- Keep under 80 characters

**Example:**
```yaml
title: uDOS Beacon Portal Protocol
```

### `tags` (Array)

Categorization tags for discovery and indexing.

**Format:** Lowercase, kebab-case, optional hierarchy with `/`

**Standard Tags:**
- `wiki` — All wiki documents must include
- `spec` — Specification documents
- `guide` — How-to or tutorial
- `reference` — Reference material
- `knowledge` — Knowledge bank content
- `protocol` — Network/system protocols
- `architecture` — Architecture decisions

**Hierarchical Examples:**
```yaml
tags: [wiki, spec, architecture]
tags: [wiki, guide, networking]
tags: [wiki, knowledge/fire/safety]
```

### `status` (Enum)

Document lifecycle status.

**Values:**

| Status | Meaning | Use Case |
|--------|---------|----------|
| `living` | Actively maintained | Current docs, active projects |
| `draft` | Early stage, incomplete | Work in progress, proposals |
| `frozen` | Complete, no changes | Finished specifications, archived |
| `deprecated` | Superseded or obsolete | Old docs, use `supersedes` field |

**Example:**
```yaml
status: living
```

### `updated` (ISO 8601 Date)

Last semantic update date.

**Format:** `YYYY-MM-DD`

**Rules:**
- Update when content changes
- Do NOT update for formatting only
- Reflects last meaningful edit
- Use current date for new docs

**Example:**
```yaml
updated: 2026-01-30
```

---

## Optional Fields

### `supersedes` (String)

UID of previous version.

**Use:** When document replaces another (status: deprecated)

**Example:**
```yaml
uid: udos-wiki-20260130120000-L300AB01
title: Beacon Portal v2
supersedes: udos-wiki-20260125000000-L300AB00
status: living
```

### `aliases` (Array)

Alternative names for discovery.

**Example:**
```yaml
aliases: [Beacon, Portal Protocol, Proximity Node]
```

### `spec` (String)

Reference to spec document.

**Example:**
```yaml
spec: wiki_spec_obsidian.md
```

### `authoring-rules` (Array)

Document-specific rules or conventions.

**Example:**
```yaml
authoring-rules:
  - Obsidian-compatible Markdown
  - File-based, offline-first
  - Wiki links over file paths
  - Hierarchical tags for navigation
```

---

## Complete Frontmatter Template

```yaml
---
uid: udos-wiki-{COMPONENT}-{YYYYMMDDHHMMSS}-{TIMEZONE}-{L###-AB##}
title: Document Title
tags: [wiki, category, subcategory]
status: living
updated: YYYY-MM-DD

# Optional fields
aliases: [Alt Name 1, Alt Name 2]
supersedes: udos-wiki-previous-component-uid
spec: wiki_spec_obsidian.md
authoring-rules:
  - Rule 1
  - Rule 2
---
```

---

## UID Generation Rules

### For New Documents

1. Choose descriptive component: alpine, beacon, sonic, wizard, knowledge, etc.
2. Use creation timestamp: `date +%Y%m%d%H%M%S` (staggered throughout the day)
3. Assign timezone: UTC (or regional if applicable)
4. Assign grid location (or use L300-AB00 default)
5. Format: `udos-wiki-{COMPONENT}-{TIMESTAMP}-{TIMEZONE}-{LOCATION}`

**Example - Created 2026-01-25 at 08:00:00 UTC, Alpine component, location L300-AB01:**
```
uid: udos-wiki-alpine-20260125080000-UTC-L300AB01
```

**Stagger throughout creation day:**
```
08:00 → 20260125080000
10:00 → 20260125100000
12:00 → 20260125120000
14:00 → 20260125140000
16:00 → 20260125160000
```

### For Backfilled Documents

Use original creation date + staggered time if available, else use earliest evidence:

```
# e.g., Alpine Core created 2026-01-25 08:00 UTC
uid: udos-wiki-alpine-20260125080000-UTC-L300AB01
```

### For Migrated Documents

Preserve UID from original source if it matches format, else generate new with descriptive component:

```
# Migrated from wiki.example.com, Alpine doc created 2025-11-20
uid: udos-wiki-alpine-20251120000000-UTC-L300AB00
```

---

## Migration Examples

### Example 1: Knowledge Doc

**Before:**
```yaml
---
title: "uDOS Knowledge Bank"
id: README
type: reference
category: knowledge
tags: [knowledge, knowledge]
difficulty: intermediate
last_updated: 2026-01-29
---
```

**After:**
```yaml
---
uid: udos-wiki-knowledge-20260130120000-UTC-L300AB00
title: uDOS Knowledge Bank
tags: [wiki, knowledge, reference]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
---
```

### Example 2: Protocol Spec

**Before:**
```markdown
# uDOS Alpine Core Protocol

**Version:** 1.0.0
**Status:** Specification
**Last Updated:** 2026-01-25
```

**After:**
```yaml
---
uid: udos-wiki-alpine-20260125080000-UTC-L300AB01
title: uDOS Alpine Core Protocol
tags: [wiki, spec, architecture]
status: frozen
updated: 2026-01-25
spec: wiki_spec_obsidian.md
authoring-rules:
  - Obsidian-compatible Markdown
  - Immutable specification
  - Link with [[reference]]
---
```

### Example 3: Living Guide

**Before:**
```markdown
# Wizard Relay Pairing

Status: In Development
Updated: 2026-01-28
```

**After:**
```yaml
---
uid: udos-wiki-wizard-20260128090000-UTC-L300AB06
title: Wizard Relay Pairing
tags: [wiki, guide, networking]
status: living
updated: 2026-01-28
aliases: [Pairing Flow, Relay Handshake]
spec: wiki_spec_obsidian.md
authoring-rules:
  - Include change log section
  - Update status after major changes
  - Use wiki links [[for references]]
---
```

---

## Validation Checklist

Before publishing a wiki document:

- ✅ `uid` matches format `udos-wiki-YYYYMMDDHHMMSS-L###-AB##`
- ✅ `title` is human-readable and matches main heading
- ✅ `tags` include at least `wiki` and one category
- ✅ `status` is one of: living, draft, frozen, deprecated
- ✅ `updated` is ISO 8601 format (YYYY-MM-DD)
- ✅ If `status: deprecated`, include `supersedes` field
- ✅ Document renders cleanly in Markdown viewer
- ✅ All wiki links `[[reference]]` are resolvable
- ✅ No hardcoded version numbers in text (use frontmatter)

---

## Integration Points

### Spatial Filesystem

Wiki documents MAY use location tagging:

```yaml
uid: udos-wiki-20260130120000-L301AB15
# ... other fields ...
tags: [wiki, knowledge, forest/survival]
```

Location tags are indexed by [Spatial Filesystem](../specs/SPATIAL-FILESYSTEM.md) for discovery.

### Binders

Multi-chapter documents use Binder structure in Spatial Filesystem:

```
@knowledge/my-binder/
  ch1-introduction.md
  ch2-techniques.md
  ch3-advanced.md
```

Each chapter includes frontmatter with shared `uid` prefix:

```yaml
uid: udos-wiki-20260130120000-L301AB00-ch1
```

### Obsidian Vault

All documents remain valid in Obsidian:

```
Obsidian Vault Root/
  knowledge/
    README.md (with frontmatter)
    water/
    fire/
    ...
  docs/
    wiki/
      ALPINE-CORE.md (with frontmatter)
      BEACON-PORTAL.md (with frontmatter)
      ...
```

---

## Tools & Automation

### Generate UID

```bash
python -c "import datetime; print(f'udos-wiki-{datetime.datetime.utcnow().strftime(\"%Y%m%d%H%M%S\")}-L300AB00')"
```

### Validate Frontmatter

```bash
# Check for uid format
grep -E "^uid: udos-wiki-[0-9]{14}-L[0-9]{3}AB[0-9]{2}$" file.md
```

### Migrate Batch

```bash
# Example: Update all knowledge docs
for file in knowledge/**/*.md; do
  # Extract timestamp, generate uid, prepend frontmatter
done
```

---

## Additional Resources

- [wiki_spec_obsidian.md](wiki_spec_obsidian.md) — Full specification
- [SPATIAL-FILESYSTEM.md](specs/SPATIAL-FILESYSTEM.md) — Location tagging reference
- [ROADMAP.md](ROADMAP.md) — Stream 1 documentation progress

---

**Last Updated:** 2026-01-30  
**Version:** 1.0  
**Status:** Living (updated as needed)
