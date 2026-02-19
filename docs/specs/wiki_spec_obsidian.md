# uDOS Wiki Specification
_Obsidian-compatible Markdown profile_

Version: 1.1
Status: Stable
Scope: Plain Markdown wiki authoring for uDOS binders, Wizard, CLI, and App
Release baseline validated: v1.4.3

---

## 1. Goals

This specification defines a **wiki-style Markdown format** for uDOS that is:

- File-based and offline-first
- Compatible with Obsidian-style Markdown
- Human-readable and Git-friendly
- Machine-parseable for indexing, search, and sqlite ingestion
- Stable under refactors (renames, moves, merges)

This spec intentionally avoids proprietary or UI-only features.

---

## 2. Baseline Markdown

- **CommonMark** is the baseline Markdown grammar.
- All extensions defined here are additive and optional.
- A document MUST remain valid Markdown even if wiki features are ignored.

---

## 3. YAML Frontmatter (Required for Wiki Pages)

Wiki documents MUST include YAML frontmatter.

### 3.1 Required fields

```yaml
---
uid: udos-wiki-{component}-YYYYMMDDHHMMSSSAEST-L301AB33
title: Human-readable Page Title
tags: [wiki]
status: living
updated: 2026-01-30
---
```

| Field | Type | Purpose |
|------|------|---------|
| `uid` | string | Stable identifier: `udos-wiki-{component}-{YYYYMMDDHHMMSS}-{timezone}-{L###-AB##}` |
| `title` | string | Display title |
| `tags` | array | Wiki categorisation |
| `status` | enum | `living`, `draft`, `frozen`, `deprecated` |
| `updated` | date | Last semantic update |

### 3.2 Optional fields

```yaml
supersedes: udos-wiki-YYYYMMDDHHMMSSSAEST-L301AB33
aliases: [Old Name, Legacy Title]
```

---

## 4. Wiki Links

uDOS supports **Obsidian-style wiki links**.

### 4.1 Basic links

```md
[[Wizard Relay Pairing]]
```

### 4.2 Aliased links

```md
[[Wizard Relay Pairing|Pairing Flow]]
```

### 4.3 Section links

```md
[[Wizard Relay Pairing#Proximity handshake]]
```

### 4.4 Resolution rules (in order)

1. Match by `uid`
2. Match by `title`
3. Match by filename
4. Fallback: unresolved link warning

Links MUST NOT rely on folder paths.

---

## 5. Tags

Tags MAY appear in frontmatter or inline.

### 5.1 Inline tags

```md
#wizard #networking #offline-first
```

### 5.2 Hierarchical tags

```md
#spec/wiki
#core/grammar
```

Rules:
- Lowercase
- Kebab-case
- `/` indicates hierarchy
- Tags are not links, but MAY be indexed into pages

---

## 6. Headings and Anchors

Standard Markdown headings apply.

### 6.1 Stable heading anchors (recommended)

```md
## Proximity handshake {#proximity-handshake}
```

This ensures stable deep links even if heading text changes.

---

## 7. Block Identifiers (Optional but Supported)

Block IDs allow fine-grained linking and transclusion.

```md
This paragraph defines the handshake protocol. ^handshake-v1
```

Linked as:

```md
[[Wizard Relay Pairing#^handshake-v1]]
```

---

## 8. Transclusion (Include Syntax)

uDOS supports logical includes.

```md
!include ./_snippets/proximity-handshake.md
```

Rules:
- Includes are resolved at render/build time
- Includes MUST reference `.md` files
- Circular includes are invalid

---

## 9. Change Logs (Recommended)

Living documents SHOULD include a human-readable change log.

```md
### Change log
- 2026-01-30: Added opt-in verification flow
- 2026-01-18: Initial relay architecture
```

This does not replace Git history.

---

## 10. Index Generation (Non-authoring Behaviour)

Tooling MAY generate:
- `WIKI_INDEX.md` (by uid + title)
- `TAGS.md` and `/tags/*.md`
- Backlink maps
- sqlite mirrors

These files are derived artefacts, not source-of-truth.

---

## 11. Non-goals

This spec does NOT include:
- Obsidian Canvas
- Plugin-specific syntax
- Rich embeds or UI widgets
- Database-backed authoring

---

## 12. Compatibility Statement

Any document conforming to this spec MUST:
- Render cleanly in standard Markdown viewers
- Open natively in Obsidian
- Be parseable by uDOS Core, Wizard, and CLI tools

---

_End of specification_

---

## Frontmatter Brief (Required in Wiki Pages)

```yaml
---
uid: udos-wiki-000XXX
title: <Page Title>
tags: [wiki]
status: living
updated: YYYY-MM-DD

udostype: wiki
spec: uDOS-WIKI-SPEC.md
authoring-rules:
  - Obsidian-compatible Markdown
  - File-based, offline-first
  - Stable uid, title may change
  - Wiki links over paths
  - Tags for categorisation, not navigation
---
```
