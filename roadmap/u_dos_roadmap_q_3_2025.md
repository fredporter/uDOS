# 📘 uDOS Development Roadmap – 2025 Q3

> Summary: Defines markdown and character policies for uDOS Beta v1.6.1 Beta v1.6.1 Author: Fred Porter (@hello), Last Edited: 2025-06-22

---

## Section 1: Purpose

To standardise all `uDOS Beta v1.6.1` system documentation as plain Markdown that is:

- Easily parsed by AI agents (like Otter)
- Cleanly rendered in TTY-style or terminal-based readers
- Maintainable across screen tiers and ASCII-based interfaces (e.g. uMaps)

---

## Section 2: Details

### 🧱 Markdown Structure Rules

- **Headings:** Use `#` to `###` only (H1–H3)
- **Code Blocks:** Use triple backticks, language-annotated where needed
- **Metadata Blocks:** YAML-style fenced blocks at the end
- **Line Length:** Prefer ≤ 100 chars, wrap sensibly
- **Frontmatter:** Avoid unless targeting static site generators

### 📄 Standard Section Order Template

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

## Section 3: Character Limits and Text Boundaries

### 🔠 Why It Matters

To ensure:
- Clean AI ingestion
- Predictable rendering on uDOS Beta v1.6.1 terminal interfaces
- Suitable lengths for voice logs, summaries, and dashboards

### 🧮 Limit Policy Table

| **Element**           | **Soft Limit** | **Hard Limit** | **Notes**                  |
|-----------------------|----------------|----------------|----------------------------|
| File Title            | 60 chars       | 80 chars       | Use kebab-case             |
| Headings              | 80 chars       | 100 chars      | Use `##` or `###` only     |
| Summary / Voice Logs  | 280 chars      | 500 chars      | Ideal for AI responses     |
| Paragraphs            | 500 chars      | 750 chars      | Split into blocks if long  |
| Config/Manifest Block | 1000 chars     | 2000 chars     | YAML format recommended    |
| File Total Size       | 8K chars       | 12K chars      | Paginate beyond 12K        |

> ⚠️ Hard limits will be enforced by Otter’s AI editing interface.

---

## Section 4: File Naming Standards

As defined in `filenames_and_structure.md`:

```

\<project/system>.\<component/context>.\<tier/phase>[-optional].md

````

### ✅ Examples

- `uos.roadmap.2025q3-system-doc.md`
- `uos.kernel.memory-vm.v1-spec.md`
- `umaps.australia.tier-2-region-index.md`

---

## Appendix

### 🎤 ASCII Compatibility Reminder

Always fence ASCII layouts in `txt` code blocks to avoid render issues:

```txt
+-------------------+
|    CPU Stack      |
+-------------------+
|  Threads: 8       |
|  Load: 35%        |
+-------------------+
````

---

## Section 5: Metadata

```yaml
id: udos.roadmap.2025q3
type: system-doc
category: roadmap
stage: final
status: active
version: uDOS Beta v1.6.1 Beta v1.6.1
```

