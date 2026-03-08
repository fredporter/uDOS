# Sonic Datasets

Wizard integrates with the Sonic device catalog from the external
`uDOS-sonic` repository.

Canonical companion repo:

- `../uDOS-sonic`

Optional override:

- `UDOS_SONIC_ROOT`

## Dataset files

Wizard expects these files under the external Sonic repo:

- `datasets/sonic-devices.schema.json`
- `datasets/sonic-devices.sql`
- `datasets/version.json`

## Runtime database layout

The external Sonic runtime owns the local database artifacts:

- `memory/sonic/seed/sonic-devices.seed.db`
- `memory/sonic/user/sonic-devices.user.db`
- `memory/sonic/sonic-devices.db`

## Wizard API

- `GET /api/sonic/health`
- `GET /api/sonic/schema`
- `GET /api/sonic/schema/contract`
- `GET /api/sonic/devices`
- `GET /api/sonic/devices/{device_id}`
- `GET /api/sonic/stats`
- `GET /api/sonic/sync/status`
- `POST /api/sonic/sync/rebuild`
- `POST /api/sonic/sync/export`
- `POST /api/sonic/bootstrap/current`

## Platform API

- `GET /api/platform/sonic/status`
- `GET /api/platform/sonic/verify`
- `GET /api/platform/sonic/dataset-contract`
- `GET /api/platform/sonic/gui/summary`

## Rebuild flow

Use the external dataset SQL through Wizard:

```bash
curl -X POST -H "Authorization: Bearer $DEVICE_TOKEN" \
  "${WIZARD_BASE_URL}/api/sonic/sync/rebuild"
```

## Related docs

- `docs/howto/SONIC-UHOME-EXTERNAL-INTEGRATION.md`
- `wizard/routes/sonic_plugin_routes.py`
- `wizard/routes/platform_routes.py`
