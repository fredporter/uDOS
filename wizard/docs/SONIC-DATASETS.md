# Sonic Screwdriver Device Database

Wizard Server integration for the Sonic Screwdriver device catalog.

## Overview

The `/sonic/datasets` folder in the public `sonic` submodule contains:

- **sonic-devices.table.md** — Primary Markdown table (human-editable)
- **sonic-devices.schema.json** — JSON Schema for validation
- **sonic-devices.sql** — SQLite schema + seed data
- **version.json** — Component versioning (v1.0.0)

## Distribution

- **Manifest:** `packages/sonic/udos-sonic-datasets.manifest.json`
- **Scope:** Wizard Server distribution (included in package index)
- **Integration:** Exposed via `/api/sonic/*` endpoints (auth required)

## Usage

### Get Device Catalog

```bash
curl -H "Authorization: Bearer $DEVICE_TOKEN" \
  http://localhost:8765/api/sonic/devices?vendor=Dell
```

### Query Devices

Supported filters:

- `vendor` — Vendor name filter
- `reflash_potential` — high, medium, low, unknown
- `usb_boot` — true/false
- `uefi_native` — works, issues, unknown
- `limit` — Results per page (1–1000)
- `offset` — Pagination offset

### Get Device Details

```bash
curl -H "Authorization: Bearer $DEVICE_TOKEN" \
  http://localhost:8765/api/sonic/devices/dell-optiplex-9020
```

### Schema and Raw Data

```bash
# JSON Schema
curl http://localhost:8765/api/sonic/schema

# Raw Markdown table
curl http://localhost:8765/api/sonic/table

# Catalog statistics
curl http://localhost:8765/api/sonic/stats
```

## Building the Database

If the SQLite database doesn't exist, compile it:

```bash
mkdir -p memory/sonic
sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql
```

Or via Wizard routes (triggers auto-compile):

```bash
# Health check will show next steps if DB missing
curl http://localhost:8765/api/sonic/health
```

## Adding Devices

1. Edit `sonic/datasets/sonic-devices.table.md`
2. Add row to table
3. Recompile database (or rebuild with Core file parsing tools)
4. Optionally bump `version.json` for new releases

## Format

Markdown table columns (required):

| Field             | Type    | Example                            |
| ----------------- | ------- | ---------------------------------- |
| id                | string  | `macbookpro-2012`                  |
| vendor            | string  | `Apple`                            |
| model             | string  | `MacBook Pro`                      |
| variant           | string  | `13" Mid 2012`                     |
| year              | integer | `2012`                             |
| cpu               | string  | `Intel i5-3210M`                   |
| gpu               | string  | `Intel HD 4000`                    |
| ram_gb            | integer | `8`                                |
| storage_gb        | integer | `256`                              |
| bios              | enum    | `UEFI`, `Legacy`, `UEFI+Legacy`    |
| secure_boot       | enum    | `yes`, `no`, `unknown`             |
| tpm               | enum    | `yes`, `no`, `unknown`             |
| usb_boot          | enum    | `yes`, `no`, `unknown`             |
| uefi_native       | enum    | `works`, `issues`, `unknown`       |
| reflash_potential | enum    | `high`, `medium`, `low`, `unknown` |
| methods           | json    | `["UEFI","dd","sonic_usb"]`        |
| notes             | string  | Device-specific guidance           |
| sources           | json    | `["https://..."]`                  |
| last_seen         | date    | `2026-01-25`                       |

## References

- [sonic/datasets/README.md](../../sonic/datasets/README.md) — Dataset guide
- [sonic/CHANGELOG.md](../../sonic/CHANGELOG.md) — Version history
- [packages/MANIFEST-INDEX.md](../MANIFEST-INDEX.md) — Package index
- [AGENTS.md](../../AGENTS.md) — Distribution system overview
