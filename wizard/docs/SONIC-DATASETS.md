# Sonic Screwdriver Device Database

Wizard Server integration for the Sonic Screwdriver device catalog.

## Overview

The `/sonic/datasets` folder in the public `sonic` submodule contains:

- `sonic-devices.table.md` - Primary Markdown table (human-editable)
- `sonic-devices.schema.json` - JSON Schema for validation
- `sonic-devices.sql` - SQLite schema + seed data
- `version.json` - Dataset component version metadata

Runtime database location:
- `memory/sonic/sonic-devices.db`

## API Endpoints

Core endpoints:

- `GET /api/sonic/health`
- `GET /api/sonic/schema`
- `GET /api/sonic/devices`
- `GET /api/sonic/devices/{device_id}`
- `GET /api/sonic/stats`

Device DB endpoints:

- `GET /api/sonic/sync/status`
- `POST /api/sonic/sync/rebuild`
- `POST /api/sonic/sync/export`
- `GET /api/sonic/db/status` (alias)
- `POST /api/sonic/db/rebuild` (alias)
- `GET /api/sonic/db/export` (alias)
- `POST /api/sonic/sync` (alias)
- `POST /api/sonic/rescan` (alias)
- `POST /api/sonic/rebuild` (alias)
- `GET /api/sonic/export` (alias)

## Query Filters (`GET /api/sonic/devices`)

- `vendor` - Vendor name filter
- `reflash_potential` - `high`, `medium`, `low`, `unknown`
- `usb_boot` - `native`, `uefi_only`, `legacy_only`, `mixed`, `none`
- `uefi_native` - `works`, `issues`, `unknown`
- `windows10_boot` - `none`, `install`, `wtg`, `unknown`
- `media_mode` - `none`, `htpc`, `retro`, `unknown`
- `udos_launcher` - `none`, `basic`, `advanced`, `unknown`
- `year_min`
- `year_max`
- `limit` - results per page (1-1000)
- `offset` - pagination offset

## Building the Database

```bash
mkdir -p memory/sonic
sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql
```

Or rebuild via API:

```bash
curl -X POST -H "Authorization: Bearer $DEVICE_TOKEN" \
  http://localhost:8765/api/sonic/db/rebuild
```

## References

- `sonic/datasets/README.md`
- `wizard/routes/sonic_plugin_routes.py`
- `library/sonic/api/__init__.py`
- `library/sonic/sync/__init__.py`
