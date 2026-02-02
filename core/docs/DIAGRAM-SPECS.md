# Diagram Specs (Core)

**Status:** Draft (Core standard)
**Purpose:** Define the minimal, Mermaid-compatible diagram syntax supported by Core renderers without bundling Mermaid.

Core supports a **lightweight Mermaid-style subset** for Gantt grids. The goal is compatibility with basic Mermaid commands while keeping parsing simple for CLI/TUI and dashboard rendering.

---

## ✅ Mermaid-Compatible Gantt Subset

Core accepts a subset of the Mermaid `gantt` grammar. Unsupported tokens are ignored (best-effort).

### Required Header

```
gantt
```

### Optional Directives (Supported)

```
title <text>
dateFormat <format>
axisFormat <format>
```

- `dateFormat` defaults to `YYYY-MM-DD` if omitted.
- `axisFormat` is display-only and does not affect parsing.

### Sections

```
section <name>
```

### Tasks (Supported)

```
Task name : <id?>, <flags?>, <start>, <end|duration>
```

**Supported fields:**
- `id` (optional): token string (no spaces)
- `flags` (optional): `milestone`, `crit`, `done`, `active`
- `start`: ISO date (`YYYY-MM-DD`) or datetime
- `end`: ISO date (`YYYY-MM-DD`) or datetime
- `duration`: `Nd`, `Nw`, `Nh` (days/weeks/hours)

**Allowed forms:**
- `Task : 2026-02-01, 2026-02-05`
- `Task : task-1, 2026-02-01, 3d`
- `Task : task-2, done, 2026-02-03, 2d`
- `Task : milestone, 2026-02-04, 0d`

### Dependencies (Supported)

```
Task : after <id>, <duration>
```

Example:
```
Build : build-1, 2026-02-01, 3d
Review : after build-1, 2d
```

### Minimal Example

```
gantt
  title Release Sprint
  dateFormat YYYY-MM-DD

  section Core
  Parser refactor : core-1, 2026-02-01, 3d
  Tests           : after core-1, 2d

  section Wizard
  OCR pass        : wiz-1, 2026-02-03, 2d
  Launch          : milestone, 2026-02-05, 0d
```

---

## ✅ Gantt Grid Output Contract

Core renderers map the parsed tasks into a fixed grid for ASCII/CLI output:

- **Window**: `window_days` (default 30)
- **Width**: 80 columns
- **Height**: `CALENDAR_HEIGHT`
- **Bars**: `#` for active span, `=` for completed span
- **Labels**: 16-char left column

Use `GanttGridRenderer.render_gantt()` for CLI views and the `/api/tasks/gantt` endpoint for UI consumers.

---

## Unsupported (Ignored)

Core ignores the following (for now):
- `todayMarker`, `excludes`, `tickInterval`, `linkStyle`, `classDef`
- `click`, `callback`, `axisFormat` styling
- advanced `dateFormat` tokens beyond ISO basics

---

## Compatibility Notes

- The subset is **compatible with basic Mermaid-style Gantt blocks**.
- Parsers should be tolerant: unknown directives do not fail the render.
- The format is **text-first** and does not require Mermaid runtime.

---

## Next

- Define formal grammar (EBNF) if needed
- Add JSON export format for dashboards
- Expand to basic flowchart subset if required
