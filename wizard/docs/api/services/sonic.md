# Sonic Service

Sonic Screwdriver integration endpoints for lifecycle, device DB, and build artifacts.

## Lifecycle and Platform

- `GET /api/platform/sonic/status`
- `POST /api/platform/sonic/build`
- `GET /api/platform/sonic/builds`
- `GET /api/platform/sonic/builds/{id}`
- `GET /api/platform/sonic/builds/{id}/artifacts`

## Library Integration

- `GET /api/library/integration/sonic`
- `POST /api/library/integration/sonic/install`
- `POST /api/library/integration/sonic/enable`
- `POST /api/library/integration/sonic/disable`
- `DELETE /api/library/integration/sonic`

## Device Database

Canonical:
- `GET /api/sonic/health`
- `GET /api/sonic/schema`
- `GET /api/sonic/devices`
- `GET /api/sonic/devices/{device_id}`
- `GET /api/sonic/stats`

DB sync routes:
- `GET /api/sonic/sync/status`
- `POST /api/sonic/sync/rebuild`
- `POST /api/sonic/sync/export`
- `POST /api/sonic/bootstrap/current`

DB aliases:
- `GET /api/sonic/db/status`
- `POST /api/sonic/db/rebuild`
- `GET /api/sonic/db/export`
- `POST /api/sonic/sync`
- `POST /api/sonic/rescan`
- `POST /api/sonic/rebuild`
- `GET /api/sonic/export`

## Device Query Filters

- `vendor`
- `reflash_potential`: `high|medium|low|unknown`
- `usb_boot`: `native|uefi_only|legacy_only|mixed|none`
- `uefi_native`: `works|issues|unknown`
- `windows10_boot`: `none|install|wtg|unknown`
- `media_mode`: `none|htpc|retro|unknown`
- `udos_launcher`: `none|basic|advanced|unknown`
- `year_min`, `year_max`, `limit`, `offset`

## Runtime Split

- Seed catalog DB: `memory/sonic/seed/sonic-devices.seed.db`
- User overlay DB: `memory/sonic/user/sonic-devices.user.db`
- Compatibility mirror: `memory/sonic/sonic-devices.db`

`GET /api/sonic/sync/status` reports the split runtime paths and whether the
current machine has been registered into the local user catalog.
