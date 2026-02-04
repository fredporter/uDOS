# Binder + Sonic Endpoints (Wizard)

Short reference for the **Wizard** binder and Sonic (Screwdriver) APIs.
These replace the legacy Goblin dev endpoints.

## Base URL

- `http://localhost:8765`
- Requires admin auth (use `Authorization: Bearer $ADMIN_TOKEN` for protected routes).

## Binder API (`/api/binder/*`)

- `GET /api/binder/workspaces` — list binder workspaces
- `GET /api/binder?workspace=sandbox` — list binders
- `GET /api/binder/summary` — binder summaries from DB
- `POST /api/binder` — create binder
- `GET /api/binder/{binder_id}/chapters` — list chapters
- `POST /api/binder/{binder_id}/chapters` — create/update chapter
- `POST /api/binder/{binder_id}/compile` — compile binder

Example:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8765/api/binder/workspaces
```

## Sonic + Screwdriver API (`/api/sonic/*`)

- `GET /api/sonic/health` — dataset + DB status
- `GET /api/sonic/schema` — device schema
- `GET /api/sonic/devices` — list devices (filters via query params)
- `GET /api/sonic/devices/{device_id}` — device details
- `GET /api/sonic/stats` — catalog stats

### Screwdriver flash packs (`/api/sonic/screwdriver/*`)

- `GET /api/sonic/screwdriver/schema`
- `GET /api/sonic/screwdriver/flash-packs`
- `POST /api/sonic/screwdriver/flash-packs`
- `POST /api/sonic/screwdriver/flash-packs/{pack_id}/plan`
- `POST /api/sonic/screwdriver/flash-packs/{pack_id}/build`
- `POST /api/sonic/screwdriver/flash-packs/validate`

Example:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8765/api/sonic/health
```

## Legacy Note

- Goblin endpoints `/api/dev/binders/*` and `/api/dev/screwdriver/*` are removed.
- Use Wizard endpoints above going forward.
