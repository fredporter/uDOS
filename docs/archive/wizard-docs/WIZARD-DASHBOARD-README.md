# Wizard Dashboard (Svelte + Tailwind)

A modern dashboard interface for the uDOS Wizard Server, built with Svelte and Tailwind CSS v4.

## Development

### Setup

```bash
cd public/wizard/dashboard
npm install
```

### Run dev server

```bash
npm run dev
```

Opens at http://localhost:5173

### Build for production

```bash
npm run build
```

Compiled assets go to `dist/` folder. The Wizard server automatically serves these static files from `/`.

## Architecture

- **src/app.css** — Tailwind v4 + Design tokens (CSS variables)
- **src/+layout.svelte** — Root layout with global styles
- **src/+page.svelte** — Dashboard page (fetches `/api/v1/index`)
- **src/lib/components/** — Reusable Svelte components
  - `FeatureCard.svelte` — Feature listing
  - `APIStatus.svelte` — API configuration status
  - `ServiceStatus.svelte` — Service health indicators

## Design System

Follows the uDOS Global Tailwind Style Guide:

- **Spacing rhythm** — 4-based utilities (p-4, gap-4, etc.)
- **Typography** — Two modes: UI text (utilities) + Rich content (prose)
- **Color tokens** — CSS variables (--bg, --fg, --primary, etc.)
- **Dark mode** — Built-in via `prefers-color-scheme`

See `src/app.css` for token definitions.

## API Integration

Fetches dashboard data from:

```
GET /api/v1/index
```

Returns JSON with features, API status, services, and configuration.

## Styling Notes

- All Tailwind classes are utility-first
- Custom CSS kept minimal (token definitions only)
- Component styles use `@reference "tailwindcss"` for proper compilation
- No inline `<style>` tags for component logic—classes preferred

## Deployment

1. Build locally: `npm run build`
2. Wizard server mounts `/dist` at root path (`/`)
3. TUI opens http://localhost:8765/ to display dashboard
4. All API endpoints remain at `/api/v1/*`
