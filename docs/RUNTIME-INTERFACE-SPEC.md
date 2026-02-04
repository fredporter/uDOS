# Runtime Interface Spec (TUI + App)

**Goal:** Shared contract so TUI and App behave consistently.

---

## Core Runtime Contract
- Markdown input → deterministic HTML output.
- Shared state model (frontmatter + blocks).

## Required Capabilities
- `state` get/set
- `form` rendering
- `nav` handling
- `panel` rendering
- `map` blocks

## Execution Interface
- `load(markdown)`
- `execute(sectionId)` → `ExecutorResult`

---

## Output Contract
- Output must be deterministic for identical input.
- Map/teletext/canvas outputs must respect fixed dimensions when required.

---

## Shared Errors
- Invalid section
- Script disabled
- Malformed blocks

