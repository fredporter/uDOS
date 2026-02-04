# Web Admin (SvelteKit Control Plane)

This folder hosts the optional SvelteKit admin UI described in `docs/uDOS-v1-3.md`. It showcases:

- Theme picker + mission queue components that consume the contracts defined in `docs/Theme-Pack-Contract.md` and `docs/Mission-Job-Schema.md`.
- Spatial metadata panel powered by `/api/renderer/spatial/*` so anchors, places, and file tags appear alongside theme telemetry.
- CSS tokens via `web-admin/src/lib/styles/global.css` so the admin UI matches the exported theme palette.
- Simple `dev`/`build` scripts for local iteration.

Environment:

- Copy `.env.example` → `.env` and adjust `VITE_WIZARD_API_URL` (defaults to `http://localhost:8765`) so the control plane can reach the renderer/Wizard server.

Run with:

```bash
cd web-admin
npm install
npm run dev -- --host
```
