# Formatting Spec v1.4

Updated: 2026-03-03
Status: active formatting contract
Scope: markdown formatting, slide formatting, table/grid normalization, and `.compost` archival rules

## Purpose

This spec defines the stable formatting rules for uDOS content pipelines that rewrite or enhance markdown.

It covers:
- archival of replaced source files into `.compost`
- standard markdown normalization
- Marp slide formatting
- table and grid conversion rules
- output placement for derived artifacts

## Design Rules

1. Human-readable markdown remains the primary output.
2. Derived formats must be reproducible from readable source files.
3. Rewrites must preserve the previous version in `.compost` before replacing active content.
4. Slide formatting and grid conversion are derived outputs, not the canonical authoring source.
5. Formatting tools must prefer deterministic local transforms where possible.

## `.compost` Archive Contract

When a formatter or converter replaces an existing file, it must archive the previous version first.

Archive rules:
- archive root: `vault/.compost/`
- filename pattern: `YYYYMMDD_HHMMSS_original-filename.ext`
- preserve original extension
- keep the newest versions by default
- retention policy may be configurable by tool/runtime

Minimum behavior:
- create `.compost` if missing
- copy the prior file before writing the new one
- avoid silent destructive rewrites

## Standard Markdown Formatting

Standard markdown formatting must:
- normalize heading spacing
- preserve fenced code blocks
- normalize list indentation
- repair broken code fences where possible
- keep links and Obsidian-style references intact
- retain frontmatter when present

Standard markdown output is the canonical editable artifact.

## Marp Slide Formatting

Marp output is an optional derived format for presentation workflows.

Marp rules:
- add Marp frontmatter when generating slide output
- split slides at major section boundaries or explicit slide markers
- preserve headings, lists, code blocks, images, and tables
- allow slide-class annotations for layout tuning
- keep generated slide files distinct from the source markdown

Recommended output path:
- `vault/@binders/<binder>/slides/<name>.marp.md`

## Table and Grid Conversion

Formatting tools may convert:
- HTML tables to markdown tables
- markdown tables to normalized markdown
- markdown or HTML tables to structured JSON for downstream use

Conversion rules:
- preserve header names
- preserve row order
- avoid inventing columns
- emit compact markdown tables when possible
- allow slide-specific compact formatting for Marp outputs

Recommended structured output path:
- `vault/@binders/<binder>/data/<name>.json`

## Integrated Formatting Pipeline

The expected pipeline is:

1. Read source markdown or HTML.
2. Archive the current version to `.compost` when replacing an existing file.
3. Parse headings, tables, lists, links, code blocks, and metadata.
4. Produce normalized markdown.
5. Optionally produce Marp markdown and structured table JSON.
6. Save derived artifacts into binder-local output folders.

## Output Placement

Preferred output layout:

```text
vault/
├── .compost/
├── @binders/<binder>/
│   ├── notes.md
│   ├── slides/<name>.marp.md
│   └── data/<name>.json
```

Projects may extend this layout, but must keep:
- canonical markdown readable and editable
- derived outputs clearly separated
- archived versions recoverable from `.compost`

## Acceptance Criteria

This spec is satisfied when:
- formatting tools archive replaced files into `.compost`
- markdown formatting preserves readable source structure
- slide generation produces valid Marp markdown
- table conversion preserves headers and rows
- derived outputs are stored separately from canonical source markdown

