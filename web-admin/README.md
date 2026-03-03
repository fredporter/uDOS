# Web Admin (SvelteKit Control Plane)

This folder hosts the managed Wizard operator UI. It showcases:

- Theme picker + mission queue components that consume the contracts defined in `docs/Theme-Pack-Contract.md` and `docs/Mission-Job-Schema.md`.
- Spatial metadata panel powered by `/api/renderer/spatial/*` so anchors, places, and file tags appear alongside theme telemetry.
- CSS tokens via `web-admin/src/lib/styles/global.css` so the admin UI matches the exported theme palette.
- Simple `dev`/`build` scripts for local iteration.
- Session-based operator access through v1.5 ops surfaces: `/api/ops/session`, `/api/ops/switchboard`, `/api/ops/planning/*`, `/api/ops/automation/*`, `/api/ops/alerts*`, `/api/ops/config/*`, `/api/ops/releases/*`, and `/api/ops/logs/*`.

Environment:

- Copy `.env.example` → `.env` and adjust `VITE_WIZARD_API_URL` when developing against a separate Wizard origin.
- In managed deployments the UI is served by Wizard at `/admin` and should rely on server-managed session cookies instead of copied bearer tokens.
- `/admin` is role-aware: the switchboard payload controls whether the current session sees planning-only controls or the broader admin/system surface.

Run with:

```bash
cd web-admin
npm install
npm run dev -- --host
```

Generated dependency and build-work directories under `web-admin/node_modules/` and `web-admin/.svelte-kit/` are local-only and should not be committed. The deployable static output remains `web-admin/build/`.
