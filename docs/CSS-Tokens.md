# CSS Tokens

Shared CSS tokens keep the static themes and SvelteKit admin UI visually aligned without importing a common framework.

## Typography
- `--font-body`: primary body stack (`Inter`, `system-ui`, etc.)
- `--font-heading`: heading stack (`Space Grotesk`, `Playfair Display`, etc.)
- `--font-code`: monospace stack (`JetBrains Mono`, `SF Mono`, etc.)

## Spacing
- `--space-unit`: base spacing (e.g., `0.5rem`) used for gaps/padding
- `--space-xl`, `--space-lg`, `--space-sm`: multiples of the base unit for larger and smaller gutters

## Colors
- `--color-bg`: default background
- `--color-fg`: default text
- `--color-muted`: muted text / metadata
- `--color-accent`: accent links/buttons

## Radius & Elevation
- `--radius-base`: border radius for cards/containers
- `--shadow-soft`: soft shadow for elevated surfaces

Apply these tokens inside `themes/<name>/theme.css` and the SvelteKit components in `web-admin/` so both lanes share the same design language without coupling to Tailwind or Svelte-specific utilities.
