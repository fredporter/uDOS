# Renderer + UI Module Standards (Wizard)

This doc ties the new MD→HTML pipeline and the Svelte UI module expectations together so the Wizard server stays aligned with `docs/uDOS-v1-3.md`’s deliverables.

## 1. MD → HTML Renderer

1. **Inputs**
   - Vault Markdown + assets (`vault/` or its synced mirror).
   - Theme metadata (`themes/<name>/theme.json`) describing slots, typography tokens, and required assets.

2. **Process**
   - Parse Markdown into HTML fragments + metadata (title, nav, footer, frontmatter) using the deterministic TS core (`core/` renderer or `node/renderer`).
   - Inject the HTML fragment into the theme’s `shell.html` slots (`{{content}}`, `{{title}}`, `{{nav}}`, `{{meta}}`, `{{footer}}`).
   - Copy required assets into `_site/<theme>/` (theme CSS, fonts, JS). Respect offline-first rules: no third-party CDN references.
   - Emit run reports + artifact metadata (`vault/06_RUNS/<mission>` and the SQLite state from `docs/Mission-Job-Schema.md`).

3. **Outputs**
   - Static site under `vault/_site/<theme>/...` that wizard/portal-static can serve.
   - Theme metadata exposed via API so the portal UI can render previews and the SvelteKit control plane (`web-admin/`) can build theme pickers.
   - Logs and mission records appended to the vault SQLite/`06_RUNS/` directories along with slot token metadata (see `docs/CSS-Tokens.md`).

## 2. Svelte UI Module Guidelines

1. **Shared Contracts**
   - Every module should consume slot metadata from `docs/Theme-Pack-Contract.md` and the universal component guidance in `docs/Universal-Components-Contract.md`.
   - Reuse CSS tokens (`docs/CSS-Tokens.md`) so the admin UI and exported themes share typography/spacing/color definitions.
   - Mission/job schemas (`docs/Mission-Job-Schema.md`) and contribution bundles (`docs/Contributions-Contract.md`) provide the JSON shapes for mission queues and contribution lists.

2. **Module Responsibilities**
   - `ThemePicker`: lists `themes/` packs, displays metadata, and selects typography tokens for preview components.
   - `MissionQueue`: surfaces mission/job schemas from `docs/Mission-Job-Schema.md`, shows runs, and triggers renderer executions.
   - `ContributionReview`: fetches contributions per `docs/Contributions-Contract.md`, displays diffs, and allows reviewers to stage patch bundles.
   - `PortalPreview`: renders slot-level HTML (via API) inside a Svelte iframe or container so the portal UI matches the exported static view.

3. **Packaging**
   - Place modules under `wizard/web/modules/` so they can be imported individually by the portal, the SvelteKit admin (`web-admin/`), or future control-plane surfaces.
   - Keep components decoupled from Svelte-specific globals; they should operate on raw HTML strings + metadata to stay compatible with other frameworks if needed later.

4. **Documentation**
   - Document every new module’s props, slots, and data dependencies in this file so both static and interactive lanes consume the same contracts.
   - Link mission, contribution, and theme metadata to the renderer outputs so the portal UI can react to updates without tight coupling.

## 3. Operational Notes

- Host the static `_site/` outputs via `wizard/portal-static/` or another static file server within Wizard; keep them under private transports or authenticated portals only.
- Provide API endpoints under `/api/renderer/*` to list themes, export jobs, missions, and contributions so both CLI agents (Vibe, Core) and the Svelte UI modules can work with the same data.
- Maintain the `.env` + `wizard-key-store` handshake (per `docs/TUI-Vibe-Integration.md`) so the renderer or UI modules can assert identity/permissions before running operations.
- Renderer routes are public for local testing by default; set `WIZARD_RENDERER_PUBLIC=0` to require admin auth for `/api/renderer/*`.

## 4. Renderer API Endpoints

- `GET /api/renderer/themes` → list theme metadata (slots, required assets, `_site` stats).
- `GET /api/renderer/themes/{theme}` → single theme metadata plus `_site` site stats.
- `GET /api/renderer/site` → summary of exported theme folders under `vault/_site/`.
- `GET /api/renderer/site/{theme}/files` → enumerate rendered HTML files for a given theme.
- `GET /api/renderer/missions` → mission/job reports read from `vault/06_RUNS/`.
- `GET /api/renderer/missions/{mission_id}` → mission/job detail by mission or job ID.
- `GET /api/renderer/contributions` → queued contribution bundles stored under `vault/contributions/`.
- `POST /api/renderer/render` → trigger or simulate a render job for a theme and return an id for tracking.
- `GET /api/renderer/places` → frontmatter-normalised place refs extracted from vault Markdown (`vault/notes/*`).
- `GET /api/renderer/spatial/anchors` → anchors table rows from the v1.3 spatial SQLite schema.
- `GET /api/renderer/spatial/places` → places table rows to drive front-end spatial filters.
- `GET /api/renderer/spatial/file-tags` → file_place_tags joined with files/places for tagged markdown files.
