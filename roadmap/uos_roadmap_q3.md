# 📘 uOS Development Roadmap – 2025 Q3

> **Summary:** This roadmap defines the markdown structure and character limit policies for `uOS` documentation, to ensure maximum compatibility across human and AI editing environments.\
> **Author:** Fred Porter (@hello)\
> **Last Edited:** 2025-06-22

---

## Section 1: Markdown Formatting Policy

### 📀 Purpose

To standardise all `uOS` documentation as plain Markdown that is:

- Easily parsed by AI agents (like GPT)
- Cleanly rendered in TTY-style or terminal-based readers
- Maintainable across screen tiers and ASCII-based interfaces (e.g. uMaps)

### 🧱 Structure Rules

- **Headings:** Use `#` to `###` only (`H1–H3`)
- **Code Blocks:** Triple backticks (\`\`\`), with language where applicable
- **Metadata Blocks:** Use `yaml` style at the end of each document
- **Line Length:** Prefer lines ≤ 100 chars; break where logical
- **Frontmatter:** Avoid unless exporting to external static site generators

### 📄 Section Order Template

````markdown
# Title
> Summary: short one-liner
> Author: [name], Last Edited: [YYYY-MM-DD]

---

## Section 1: Purpose

## Section 2: Details

### Subsection A

### Subsection B

## Section 3: Metadata

```yaml
id: uos.roadmap.2025q3
type: system-doc
category: roadmap
keywords: [markdown, limits, structure]
````

```

---

## Section 2: Character Limits and Text Boundaries

### 🔠 Why It Matters

To ensure:
- Clean AI ingestion
- Predictable rendering on uOS terminal interfaces
- Limits that work for voice command summaries and logging

### 🦮 Limit Policy Table

| **Element**           | **Soft Limit** | **Hard Limit** | **Notes** |
|-----------------------|----------------|----------------|-----------|
| File Title            | 60 chars       | 80 chars       | Use kebab-case |
| Headings              | 80 chars       | 100 chars      | `##` or `###` only |
| Summary / Voice Logs  | 280 chars      | 500 chars      | Ideal for AI agent response |
| Paragraphs            | 500 chars      | 750 chars      | Split into blocks if longer |
| Config/Manifest Block | 1000 chars     | 2000 chars     | YAML preferred |
| File Total Size       | 8K chars       | 12K chars      | Beyond that: paginate |

> 🤠 Note: AI agents will flag hard limits when generating or editing content.

---

## Section 3: File Naming Standards (Imported)

As per `filenames_and_structure.md`, standard naming follows this format:

```

\<project/system>.\<component/context>.\<tier/phase>[-optional]..md

````

### ✅ Examples for this Doc

- `uos.roadmap.2025q3-system-doc.md`
- `uos.kernel.memory-vm.v1-spec.md`
- `umaps.australia.tier-2-region-index.md`

---

## Appendix

### 🎤 ASCII Compatibility Reminder

Keep ASCII box-drawing and diagram sections isolated in fenced `txt` code blocks:

```txt
+-------------------+
|    CPU Stack      |
+-------------------+
|  Threads: 8       |
|  Load: 35%        |
+-------------------+
````

---

```yaml
id: uos.roadmap.2025q3
type: system-doc
category: roadmap
stage: draft
status: active
```

