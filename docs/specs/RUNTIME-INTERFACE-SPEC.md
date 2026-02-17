# Runtime Interface Spec (TUI + App)

**Goal:** Shared contract so TUI and App behave consistently.

---

## Core Runtime Contract
- Markdown input → deterministic HTML output.
- Shared state model (frontmatter + blocks).
- Shared text-grid model for terminal and markdown diagram outputs.

## Required Capabilities
- `state` get/set
- `form` rendering
- `nav` handling
- `panel` rendering
- `map` blocks
- `grid` rendering (`dashboard|calendar|schedule|table|map|workflow`)
- `diagram` export (`text|markdown|json`)

## Execution Interface
- `load(markdown)`
- `execute(sectionId)` → `ExecutorResult`
- `render(mode, payload, opts)` → `RenderResult`

---

## Output Contract
- Output must be deterministic for identical input.
- Map/teletext/canvas outputs must respect fixed dimensions when required.
- Canonical mode must support fixed `80x30` snapshots.
- Adaptive mode may use terminal viewport while preserving deterministic ordering.
- Markdown diagram output must use fenced `text` blocks.

---

## Advanced I/O Contract

- Input ownership: prompt/input handler owns stdin during entry phases.
- Output ownership: renderer owns stdout during draw phases.
- Background workers must not write directly to stdout outside renderer orchestration.
- Control-sequence safety:
  - no unsafe cursor-home restore behavior,
  - line clears must avoid residual artifacts,
  - ANSI styling must not break visible-width alignment.

---

## Shared Errors
- Invalid section
- Script disabled
- Malformed blocks
- Unsupported render mode
- Output writer collision / render contention
