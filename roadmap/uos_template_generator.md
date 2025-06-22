# 🛠 uOS Template Generator – v1

> **Summary:** Template definition system for standardising document generation across `uOS`. Designed to be human-readable, AI-operable, and markdown-native.  
> **Author:** Fred Porter (@hello)  
> **Last Edited:** 2025-06-22  

---

## Section 1: Purpose

This document establishes the default rules and syntax used by the `template.generator` module to scaffold consistent files across all `uOS` components.

It ensures:
- Consistency in headings, metadata, and file naming
- Quick scaffolding for new specs, logs, maps, or guides
- Easy integration with `uOS.render` and `uOS.agent.writer`

---

## Section 2: Template Structure Rules

### 📁 Supported Output Types

- `system-doc` — core documentation (roadmaps, proposals)
- `spec` — functional/technical specifications
- `log` — diagnostic or operational entries
- `map` — structured ASCII geography entries
- `config` — system blocks (yaml, ini, etc.)

### 📄 Template Format

```markdown
# {{ title }}
> Summary: {{ summary }}
> Author: {{ author }}, Last Edited: {{ date }}

---

## Section 1: Purpose
{{ purpose }}

## Section 2: Details
### Subsection A
{{ detail_a }}

### Subsection B
{{ detail_b }}

## Section 3: Metadata
```yaml
id: {{ file_id }}
type: {{ type }}
category: {{ category }}
keywords: {{ keywords }}
```
```

Placeholders (`{{ }}`) must be replaced before file is saved or rendered. Partial rendering is allowed in draft workflows.

---

## Section 3: Template Generator Behaviour

### 🧠 AI Usage

- Fields like `summary`, `purpose`, and `detail_*` may be auto-filled by `uOS.agent.writer`
- Section headers are locked unless explicitly overridden by system flags

### 📄 Output Pathing Convention

Generated files follow:

```
/uos/{category}/{component}/{file_name}.md
```

Example:

```
/uos/specs/kernel/uos.kernel.memory-vm.v2-spec.md
```

### 🔐 Constraints

- Title must not exceed 80 characters
- YAML fields must be valid; no trailing commas
- Only `.md` output is allowed by `generator.v1`  
  (Future versions may support `.json` for API docs)

---

## Appendix

### 🧪 Example Template Invocation

```bash
uos.template.generator \
  --type spec \
  --title "Memory Allocation Subsystem v2" \
  --category kernel \
  --component memory-vm
```

### 📌 Output Filename

```
uos.kernel.memory-vm.v2-spec.md
```

---

```yaml
id: uos.template.generator.v1
type: system-doc
category: generator
status: active
version: 1
keywords: [template, generation, markdown, uos]
```

