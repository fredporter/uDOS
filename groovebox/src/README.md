# Groovebox SvelteKit Application

Standalone Svelte + SvelteKit application for the Groovebox music production system.

## Directory Structure

```
src/
├── lib/
│   └── components/
│       ├── MixerPanel.svelte      - 8-channel mixer with faders
│       ├── PatternGrid.svelte     - Pattern editor grid
│       ├── SoundBrowser.svelte    - Sound/instrument browser
│       ├── TransportBar.svelte    - Playback transport controls
│       └── index.ts               - Component exports
├── routes/
│   ├── +page.svelte              - Main Groovebox page
│   └── api/
│       └── pattern/
│           └── +server.ts        - Pattern API endpoints
```

## Core Features

### MixerPanel

- 8-channel volume faders (0-100)
- Pan controls (-50 to 50)
- Mute/Solo buttons
- Master volume control
- Visual level meters

### PatternGrid

- 16-step pattern editor
- Multiple drum tracks
- Real-time visualization
- Pattern switching

### TransportBar

- Play/Pause/Stop controls
- BPM adjustment
- Pattern selection
- Recording controls

### SoundBrowser

- Instrument library navigation
- Sound preview
- Effect chains
- Preset management

## Development

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Server runs at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Output in `dist/` directory

## Integration

To use in Goblin dev server:

```
/dev/goblin/src/routes/groovebox → /groovebox/src/routes
/dev/goblin/src/lib/components/groovebox → /groovebox/src/lib/components
```

Components can be imported:

```typescript
import { MixerPanel, PatternGrid } from "$lib/components";
```

## Configuration

- **TypeScript:** tsconfig.json
- **Svelte:** svelte.config.js
- **Vite:** vite.config.ts
- **Build:** npm scripts in package.json

## API Endpoints

### POST /api/pattern

Create/update a pattern

**Request:**

```json
{
  "id": "pattern-1",
  "name": "Drum Pattern",
  "steps": [0, 1, 0, 1, ...],
  "tempo": 120
}
```

**Response:**

```json
{
  "success": true,
  "patternId": "pattern-1"
}
```

## Status

✅ Components migrated from Goblin
✅ Standalone SvelteKit app ready
✅ Configuration complete
⏳ Further development (recordings, effects, advanced synthesis)
