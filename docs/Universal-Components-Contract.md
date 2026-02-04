# Universal Component Contracts

This contract codifies the “universal components” promise from `docs/uDOS-v1-3.md` sections 4, 5, and 12: publishing uses framework-agnostic HTML/data contracts while the control plane (SvelteKit admin) follows the same shared definitions.

## HTML + slot contracts
- Theme packs (`themes/<name>/shell.html`) must define the slots `{{content}}`, `{{title}}`, `{{nav}}`, `{{meta}}`, and `{{footer}}`. Additional optional slots (e.g., `{{aside}}`, `{{cta}}`) are allowed if documented in `theme.json`.
- Control-plane components (SvelteKit) must render any exported HTML through the same slots when reusing the theme shell for previews or export pipelines.
- Slot contents must remain pure HTML snippets with no framework-specific bindings so they can be rendered both in static exports and inside the admin UI WebView.

## Data contracts
- Theme metadata (`theme.json`) describes available slots, required assets, typography defaults, and mode (`article`, `retro`, `slides`, `forms`). SvelteKit components read this metadata to configure previews, theme pickers, and export jobs.
- Mission/job schemas (`docs/Mission-Job-Schema.md`) and contribution bundles (`docs/Contributions-Contract.md`) provide JSON shapes that both the renderer (`core/`) and admin UI (`web-admin/`, `wizard/`) consume without inferring framework-specific logic.
- CSS tokens (gap/spacing/typography) are defined once (e.g., `docs/CSS-Tokens.md` or inline in `theme.json`) and reused by both exported themes and SvelteKit styling so the visual language stays consistent without coupling to Svelte or Tailwind internals.

## CSS tokens & styling
- Define global tokens for typography scale, spacing, colors, and radius (see `docs/CSS-Tokens.md`). Publish these tokens as design tokens (`bodyFont`, `headingFont`, `codeFont`, `spacingUnit`).
- Both theme packs and SvelteKit components must map to the same token names when compiling CSS, ensuring static exports and the admin UI share the same look/feel without sharing a CSS framework.
- When new tokens are added, update both the theme metadata (`theme.json`) and the SvelteKit theme picker so the runtime knows how to apply them.

## Shared tooling
- The renderer (`core/` or `node/renderer`) should treat exported slots/data as simple objects (HTML strings + metadata) so it can target both filesystem exports and the portal static server (`wizard/portal-static`).
- The SvelteKit control plane (`web-admin/`) should expose a theme picker and preview component that consumes the same HTML/data contracts, preventing duplication of slot logic.
- Document any additional slots, data fields, or tokens in this file whenever they are introduced so every lane can stay aligned.
