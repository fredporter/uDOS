# Wizard Dashboard (Svelte + Vite + Tailwind)

Modern web dashboard for the uDOS Wizard Server.

## Building the Dashboard

```bash
# Navigate to dashboard directory
cd wizard/dashboard

# Install dependencies
npm install

# Build for production
npm run build

# Or run dev server
npm run dev
```

## Files Structure

- `src/` - Svelte components and styles
  - `App.svelte` - Main app component
  - `main.js` - Entry point
  - `routes/` - Page components
  - `components/` - Reusable components
  - `app.css` - Global styles
  - `styles.css` - Tailwind imports
- `dist/` - Built output (created by `npm run build`)
- `index.html` - HTML template
- `vite.config.js` - Vite configuration
- `tailwind.config.js` - Tailwind CSS configuration

## Features

- Real-time server status
- Device session management
- Rate limit monitoring
- AI model routing dashboard
- Cost tracking
- WebSocket updates
- Responsive design (mobile-first)

## Development

```bash
# Start dev server (hot reload)
npm run dev
# Dashboard available at http://localhost:5174

# Build for production
npm run build

# Preview production build
npm run preview
```

## Tech Stack

- **Framework:** Svelte 4
- **Build Tool:** Vite 5
- **Styling:** Tailwind CSS 3 + PostCSS
- **Template:** SvelteKit compatible

## Fallback Dashboard

When the built dashboard isn't available, the server provides a basic HTML fallback that shows all available API endpoints and status.
