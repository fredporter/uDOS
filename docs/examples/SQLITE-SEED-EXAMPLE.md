# SQLite Seed Example

Updated: 2026-03-03
Status: active example

## Purpose

Example schema and seed data for a small SQLite-backed runtime demo.

## Included Tables

- `facts`
- `npc`
- `poi`
- `tile_edges`

## Minimal Seed Pattern

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS facts (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS npc (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  bio TEXT NOT NULL,
  tile TEXT NOT NULL,
  layer INTEGER NOT NULL
);
```

## Companion Example

- [Movement Demo Script Example](/Users/fredbook/Code/uDOS/docs/examples/MOVEMENT-DEMO-SCRIPT-EXAMPLE.md)

