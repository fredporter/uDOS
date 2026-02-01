# Round 4 Dataset Table + API Reference

Round 4 calls for the Wizard Browser to expose structured dataset tables (with sorting/filtering/pagination), chart views, and the SQLite binding that feeds those views. The canonical spec lives in `docs/specs/file-parsing-architecture.md`, which already outlines the Markdown/SQLite pipeline; this wiki page pulls the actionable pieces into one place for the week’s work.

## Key assets

- **`uDOS-table.db`** – the read-only SQLite database that backs the dataset tables. Exported tables live in `tables/*.table.md` alongside `scripts/*.script.md` helpers.  
- **Markdown table sources** – `.table.md` files contain frontmatter and pipe-delimited data; each file maps to an SQLite table (contacts, revenue summaries, top cities, etc.).
- **Parser pipeline** – `core/parsers/markdown_table_parser.py` reads `.table.md`, infers schema (column types, defaults), and writes into SQLite.

## Round 4 API surface

These endpoints need to exist (see `docs/specs/file-parsing-architecture.md:63-205` for the full workflow and helper components). Round 4 now ships `/api/data/tables/{table}?filter=column:value&order_by=<column>&desc=<bool>` so dashboards can page, sort, and filter real SQLite tables, and the teletext/NES canvas flows can consume `/api/teletext/canvas`/`/nes-buttons` (see Round 5) for retro previews as soon as the grids are rendered.

| Path | Method | Purpose |
| --- | --- | --- |
| `/api/parse/table` | `POST` | Accept Markdown/`@table` payload, parse it into SQLite (handles inference and schema validation). |
| `/api/parse/yaml` | `POST` | Ingest YAML/TOML config/data, split structured config vs. data tables, and populate SQLite tables accordingly. |
| `/api/parse/markdown` | `POST` (v0 path) | Auxiliary entry point that detects `.table.md` blocks and routes through the Markdown parser. |
| `/api/export/table` | `POST` | Export an existing SQLite table back into `.table.md` with pagination/truncation guardrails. |
| `/api/export/markdown` | `POST` (v0 path) | Legacy export that serializes table content plus frontmatter for manual editing. |

Round 4 also expects `/api/data/*` endpoints that expose table metadata (schema, row count), filtering helpers, and chart-ready aggregates; the spec suggests building them on top of the SQLite binding so the dashboard can paginate/sort without hitting raw files.

## Developer guidance

1. **API implementation** – Build FastAPI routes that call the Markdown parser/exporter components and wrap them with pagination/validation. Mimic the routes described above and reuse `core/parsers/markdown_table_parser.py` plus the exporter stub (`core/exporters/markdown_table_exporter.py`).  
2. **Wizard Browser** – In the dashboard, consume the `/api/data/*` endpoints to render tables and charts; provide quick filters (column sorting, schema toggles) and fallback to the `.table.md` editors in `tables/`.  
3. **SQLite binding** – Keep `uDOS-table.db` as the canonical data source; use binder helpers (`core/framework/seed/bank/grid` exposures) to open the DB, expose schema, and run queries when powering the dataset table view.
4. **Documentation** – Keep this wiki page synchronized with `docs/specs/file-parsing-architecture.md`. When new endpoints or UI behaviors land, update both the doc and this summary so other teams can reference whichever surface they prefer.

If you need the dataset table spec exported anywhere else (dashboard README, automation plan), let me know and I can mirror the relevant sections or add API samples to this wiki entry.
