# uDOS Logging API Spec (v1.3)

Status: Draft
Audience: uDOS Core + Wizard + script authors
Language: Australian English

Primary goal: Keep logging in code forever, but make it switchable, structured, cheap when off, and centralised to `<repo>/memory/logs/udos`.

---

## Principles

1. One logging API everywhere
   - Scripts, Core, and Wizard all call the same logging surface (`log.info()`, `log.error()`, etc).
   - Dev logging is not a separate system; it is a configuration preset.

2. Logs are structured first
   - JSON Lines (one JSON object per line) as the canonical format.
   - Pretty console output is optional (dev UX), derived from the same events.

3. Logging must be cheap when disabled
   - Debug/trace must not allocate heavy objects or build strings unless enabled.
   - Provide `log.isDebug()` and/or lazy log builders.

4. Privacy and redaction by default
   - Never write secrets or sensitive payloads to disk.
   - Provide explicit opt-in for payload dumps in dev mode, and even then: sanitised.

5. Centralise by contract
   - Default sink writes to `~/memory/logs/`.
   - Component-specific subfolders and stable filenames support grepping, rotation, and support bundles.

---

## Directory Layout

Canonical log root:

- `<repo>/memory/logs/udos`

Recommended structure:

- `<repo>/memory/logs/udos/`
  - `core/`
  - `wizard/`
  - `scripts/`
  - `audit/`
  - `crash/`
  - `metrics/` (optional; derived later)

Examples:

- `<repo>/memory/logs/udos/core/core.jsonl`
- `<repo>/memory/logs/udos/wizard/wizard.jsonl`
- `<repo>/memory/logs/udos/scripts/<script_name>.jsonl`
- `<repo>/memory/logs/udos/audit/audit.jsonl`
- `<repo>/memory/logs/udos/crash/<timestamp>-<session_id>.jsonl`

---

## Event Schema (JSON)

All logs are emitted as JSON objects with these stable fields.

### Required fields

- `ts` (ISO8601 with timezone, e.g. `2026-02-07T13:02:11+10:00`)
- `level` (`trace|debug|info|warn|error|fatal`)
- `msg` (short human-readable message)
- `component` (`core|wizard|script`)
- `category` (e.g. `db|fs|sync|net|ui|exec|security`)
- `event` (stable machine name, e.g. `script.start`, `db.migrate`, `wizard.connect`)
- `session_id` (stable for the runtime session)
- `corr_id` (correlation id for a request/job/command)
- `ctx` (object; contextual fields — sanitised)

### Optional fields

- `op_id` (operation id, if different from corr_id)
- `script` (script id/name for script runtime)
- `binder` (binder id/path alias; avoid raw user paths unless necessary)
- `loc_id` (uDOS location anchor id, if relevant)
- `duration_ms` (for completed operations)
- `result` (`ok|fail|partial`)
- `err` (object; error details: `{ name, message, code, stack? }`)
- `meta` (object; build/version: `{ version, commit, build }`)
- `schema` (log schema id, e.g. `udos-log-v1.3`)
- `ts_mono_ms` (monotonic timestamp for duration calculations)

### Error object rules

- `err.stack` allowed only for `error` and `fatal` by default.
- `err.stack` must be stripped/redacted if it contains secrets or sensitive paths.

---

## Logging Levels

- `trace`: extremely noisy, for deep diagnostics; off by default
- `debug`: dev instrumentation; off by default in prod
- `info`: lifecycle milestones; on by default
- `warn`: unexpected but recoverable; on by default
- `error`: failures; on by default
- `fatal`: unrecoverable; always captured and triggers crash handling

---

## Configuration

Configuration can be sourced from env vars, a future config file, or Wizard runtime settings.

### Minimum configuration keys

- `UDOS_LOG_LEVEL` = `info|warn|error|debug|trace`
- `UDOS_LOG_FORMAT` = `json|pretty` (default `json`)
- `UDOS_LOG_DEST` = `file|stdout|both` (default `file`)
- `UDOS_LOG_ROOT` = `<repo>/memory/logs/udos` (default)
- `UDOS_LOG_REDACT` = `on|off` (default `on`)
- `UDOS_LOG_CATEGORIES` = allow-list (optional)
- `UDOS_LOG_SAMPLING` = float `0..1` (optional; applies to debug/trace)
- `UDOS_LOG_PAYLOADS` = `off|dev-only|on` (default `dev-only`, and only if redact is on)

### Mode presets

Dev (loud):
- level: `debug`
- format: `pretty` (console) + `json` (file)
- dest: `both`
- payloads: `dev-only` (explicit opt-in per category)

Prod (quiet):
- level: `info`
- format: `json`
- dest: `file`
- redact: `on`
- sampling: enabled for any debug categories (if temporarily elevated)

---

## API Surface

All uDOS code uses the same interface:

### Core functions

- `log.trace(msg, ctx?)`
- `log.debug(msg, ctx?)`
- `log.info(msg, ctx?)`
- `log.warn(msg, ctx?)`
- `log.error(msg, ctx?, err?)`
- `log.fatal(msg, ctx?, err?)`

### Machine-stable event helper

- `log.event(level, event, msg, ctx?, err?)`

### Lazy logging (must exist)

- `log.debug(msg, () => ctx)`
- or `if (log.isDebug()) log.debug(msg, ctx)`

Provide:
- `log.isTrace()`
- `log.isDebug()`

### Context binding

Create a child logger with baked-in fields:

- `log.child({ component, category, corr_id, session_id, script, binder, loc_id })`

Example usage:
- Core creates `coreLog = log.child({ component: "core" })`
- Script runtime creates `scriptLog = log.child({ component: "script", script: "my-script" })`

---

## Sinks (Destinations)

### File sink (default)

- Writes JSONL to:
  - `~/memory/logs/udos/<component>/<name>.jsonl`
- One event per line.
- Buffered writes to reduce IO overhead.

### Console sink (optional)

- Pretty formatting for dev UX.
- Mirrors the same events (no extra detail unless configured).

### Ring buffer (recommended)

- Keep last N events in memory (e.g. N=500–2000).
- On fatal/crash, dump ring buffer to:
  - `~/memory/logs/udos/crash/<timestamp>-<session_id>.jsonl`

---

## Rotation & Retention

Minimum viable rotation:
- by size (e.g. 10–50 MB), and/or
- daily files (e.g. `core-2026-02-07.jsonl`)

Retention defaults:
- keep 7–30 days of standard logs
- keep 30–90 days of audit logs
- keep crash logs until manually pruned or 30 days

Pruning:
- a core command can prune by age and max total size

---

## Redaction Rules

Default redact keys (case-insensitive):
- `password`, `pass`, `secret`, `token`, `api_key`, `authorization`, `cookie`, `set-cookie`, `session`, `jwt`, `private_key`

Redaction behaviours:
- replace values with `"[REDACTED]"`
- for long strings: keep prefix/suffix (optional) e.g. `abcd...wxyz` (only if safe)

Hard rule:
- never write raw request bodies, DB rows, or file contents unless:
  - `UDOS_LOG_PAYLOADS` explicitly enabled
  - category allow-listed
  - redact is on

---

## What We Keep In Normal Operations

Always-on (info/warn/error):
- start/stop events for Core/Wizard/Script runtime
- command/script invoked (sanitised args)
- binder mount/open/close
- DB migrate/open/close
- wizard connect/disconnect
- sync start/end + counts + duration
- permission/share/relay decisions (audit)
- errors with: type/code, correlation id, minimal reproduction context

Avoid in prod (debug/trace only):
- tight-loop logs
- full payload dumps
- verbose internal state snapshots

---

## Correlation and IDs

### `session_id`
- generated at process start
- stable for the lifetime of the process

### `corr_id`
- generated per command/request/job
- propagated across components (core ↔ wizard ↔ script)

Recommended format:
- short, URL-safe id (base32/base64url) or existing uDOS UID strategy

---

## Example Events

Script start:

```json
{"ts":"2026-02-07T13:02:11+10:00","level":"info","msg":"Script started","component":"script","category":"exec","event":"script.start","session_id":"S-8F3K","corr_id":"C-K2P9","ctx":{"script":"backup-binder","binder":"music-fest-2026"}}
```
