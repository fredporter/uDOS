# SQL Blocks & Runner Results (STREAM1)

This note summarizes the new `sql` runtime block options plus the enriched document runner payload so **stories and TUI health checks** can exercise database lookups without leaving the Markdown runtime.

## `sql` block options

| Key | Description | Example |
| --- | --- | --- |
| `path` | Filesystem path to the SQLite database that will be opened in read-only mode. Supports relative paths in the repo or absolute locations. When omitted the block runs against an in-memory database (fresh every execution). | `path = memory/db/location.db` |
| `db` | Synonym for `path`; useful when you prefer semantic naming or reusing older docs. | `db = ${memory.db.path}` |
| `query` | **Required.** The SQL statement to execute. Only `SELECT` or `PRAGMA` statements are allowed to protect the core runtime from destructive SQL. Interpolation (`$var`) runs before execution. | `query = SELECT id, name FROM heroes WHERE power > $player.power` |
| `params` | Optional list/payload added to the prepared statement. You can pass a JSON array (e.g. `[10, "Nova"]`) or comma-separated list (`10, Nova`); all values are interpolated before binding. Booleans become `1/0`. | `params = [$player.level, "Explorer"]` |
| `as` | Alias to store the query rows inside runtime state (default: `__sqlResult`). The alias supports nested paths and dot notation. | `as = heroQuery` |

### Interpolation + safety

The block resolves `$` templates before parsing literals, so `"Hero $player.name"` becomes `"Hero Nova"`. Numeric and JSON-like literals convert automatically, string quotes are optional, and blank values become `null`. The executor enforces read-only usage via `regex /^(select|pragma)/i` and closes every database connection (neither `better-sqlite3` nor `sql.js` instances leak handles).

## DocumentRunner result payload

`DocumentRunner.run(...)` now returns a richer payload that stories can inspect after the Markdown graph runs:

| Field | Meaning |
| --- | --- |
| `success` | `true` when the runner finished without early aborts/errors; otherwise includes `error`. |
| `output` | The last executor output (panel/nav) or aggregated view if no section produced branded output. |
| `aggregatedOutput` | Full text from all executed sections, collated in execution order (new sections append output + `\n`). |
| `executedSections` | Array of section IDs that actually ran. Enables TUI watchers to verify specific mutation paths ran during self-heal/startup. |
| `history` | List of raw `ExecutorResult` objects (state/set/panel/etc.). Useful for integrations that need to inspect `rows`, `choices`, or `formFields`. |
| `finalState` | Snapshot of `RuntimeState` after the final section ran; use it to surface `$heroQuery` results or confirm mutations. |
| `rows` | When an `sql` block runs, the executor appends the row list to the result (also stored under `finalState[alias]`). |

## TUI story guidance

1. **Run SQL before panels.** Create a `state` block to anchor defaults, follow with an `sql` block to query the DB, and finish with a `panel`/`map` that references the alias. The runner ensures the alias is available for interpolation.
2. **Assert runner output** in story metadata: capture `history` or `finalState` after `run()` and log `executedSections` to `memory/logs/health-training.log` so the TUI startup banner can mention whether the mutation path executed.
3. **Automation scripts** can query `aggregatedOutput` + `executedSections` to guarantee `memory/tests/phase1/*` suites touched the expected sections and that no SQL block failed silently. Persistent logging resides under `memory/logs/memory-tests.log`, while `memory/tests/automation.py` is invoked by the TUI health-check scheduler to rerun the Jest phase‑1 suite whenever new files land under `memory/tests/`. This means every startup health banner now gates on the same DocumentRunner+SQL coverage you just defined.

## Example block

````markdown
```state
$player.level = 9000
```

```sql
path = memory/db/heroes.db
query = SELECT name, power FROM heroes WHERE level >= $player.level
as = heroStack
params = [1]
```

```panel
High level heroes:
$heroStack.0.name ($heroStack.0.power)
```
````

This story now has a documented path (`heroStack`) that can be validated inside the TUI banner or self-test scripts.
