# Renderer + Task Indexer Runbook

Operational checklist for the static renderer, task indexer, and Wizard renderer API lane.

---

## 1. Build Core

```bash
cd core
npm run build
```

---

## 2. Renderer CLI

```bash
node dist/renderer/cli.js --theme prose --vault /path/to/vault --themes /path/to/themes --output /path/to/vault/_site --mission nightly-prose
```

Defaults:
- `VAULT_ROOT` → `../vault`
- `THEMES_ROOT` → `../themes`
- `OUTPUT_ROOT` → `../vault/_site`
- `MISSION_ID` → `renderer-<theme>`
- `RUNS_ROOT` → `<vault>/06_RUNS`

Expected outputs:
- Static site: `<vault>/_site/<theme>/...`
- Run report: `<vault>/06_RUNS/<mission>/job-*.json`

---

## 3. Task Indexer CLI

```bash
node dist/tasks/cli.js --vault /path/to/vault --db /path/to/vault/.udos/state.db
```

Expected outputs:
- SQLite tables `files` + `tasks` created in the DB.
- Tasks indexed with FK integrity against `files`.

---

## 4. Renderer + Indexer Tests

```bash
cd core
npm run test:renderer
npm run test:renderer-cli
npm run test:tasks
```

---

## 5. Wizard Renderer Endpoints

Assumes Wizard running at `http://localhost:8765`.

```bash
curl http://localhost:8765/api/renderer/themes
curl http://localhost:8765/api/renderer/site
curl http://localhost:8765/api/renderer/missions
curl -X POST http://localhost:8765/api/renderer/render \
  -H "Content-Type: application/json" \
  -d '{"theme":"prose","mission_id":"manual-prose"}'
```

Notes:
- `/api/renderer/render` accepts `theme` in JSON or as a query param.
- Spatial endpoints (`/api/renderer/spatial/*`) auto-bootstrap the SQLite schema if missing.

---

## 6. Renderer Auth Toggle

By default, renderer routes are public for local use. To require admin auth:

```bash
export WIZARD_RENDERER_PUBLIC=0
```

Then call endpoints with:

```bash
Authorization: Bearer $WIZARD_ADMIN_TOKEN
```

---
