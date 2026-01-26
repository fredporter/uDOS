# Wizard ↔ Core Storying Process

## Purpose

Capture the new responsibilities split between Core and Wizard so everyone knows where `-story.md` files are parsed, validated, and routed before any HTML/Svelte layer touches them.

## Process

1. **Core owns story parsing.** `core/services/story_service.py` now reads the YAML front matter (via `markdown_frontmatter`) and emits `sections`, `questions`, and a normalized `answers` object. Clients receive the same payload irrespective of whether the story is the setup wizard or a general workspace document.
2. **Wizard setup routes return the parsed state.** `/api/v1/setup/story/read` boots the template, passes it through the core story service, and enforces required keys (`title`, `type`, `submit_endpoint`). Errors are surfaced with HTTP 422 so the dashboard gets precise toast feedback instead of “invalid pattern” noise.
3. **Workspace files also reuse the service.** `/api/v1/workspace/story/parse` lets the dashboard request any `-story.md` from `/memory` and get the validated structure straight from Core—no client-side YAML parsing needed anymore.

## Responsibilities

- Core:
  - `story_service`: front matter validation, section extraction, question parsing.
  - `location_service`: grid/id lookup, timezone-aware defaults, location validations.
  - `markdown_frontmatter`: shared helpers for consistent YAML handling.
  - Keeps the text-only, TUI promise; no HTML/CSS logic lives here.
- Wizard:
  - Routes (setup/workspace) call the core helpers and return safe payloads.
  - The dashboard renders via `StoryRenderer`, `StorySection`, and `StoryField` using only the rendered content and progress helpers from `markdownRenderer.ts`.
  - Interactive console now exposes `reboot` to hot-reload config/console state and the launcher scripts honor `--rebuild` for dashboard builds.

## Notes

- Keystore usage (user vs. install profiles) should remain shared: `wizard/services/setup_profiles.py` is the current source of truth, but keep an eye on migrating parts of that API into Core so other subsystems can reuse the lock/unlock logic without duplicating secrets code.
- Document the process here whenever story-related handlers change—this page becomes the quick reference for new wizard flows.
- Core stays TUI-only for now; any HTML/CSS work belongs to Wizard’s dashboard until we explicitly expand the Core UI layer.

## Verification Checklist

- [x] `npm --prefix wizard/dashboard run build` rebuilds the dashboard successfully (✓ Verified 2026-01-26)
- [x] Core story parser migrated to `/core/src/story/` and exported from runtime (✓ Complete)
- [x] Python story service in Core at `core/services/story_service.py` (✓ Complete)
- [ ] `/api/v1/setup/story/read` response includes the `story` payload (requires server running)
- [ ] The dashboard no longer runs `parseStoryFile` locally; receives `story` directly from backend (requires testing with server)
- [ ] `Launch-Wizard-Server.command --rebuild` toggles the dashboard rebuild marker, and the console's `reboot` command reloads configuration/logging banners (requires server testing)

### Completed Since Last Review (2026-01-26)

1. **Dashboard Build**: ✅ Successfully builds in 2.91s with Vite
2. **Story Parser Migration**: ✅ Moved from Goblin to Core (`/core/src/story/`)
3. **Dual Implementation**: ✅ TypeScript (Core runtime) + Python (Wizard server)
4. **Import Structure**: ✅ Exported as `Story` from `@udos/runtime`
5. **Browser Compatibility**: ✅ Runtime checks for DOM APIs added

### Remaining Work

- Start Wizard Server to verify API endpoints
- Test dashboard integration with live server
- Verify `StoryRenderer` receives parsed story from backend (not client-side parsing)
