author: Name
## App Instructions

**Scope:** `app/**` — Tauri + Svelte GUI client

## Critical Rules

1. UI only — no business logic; delegate to Core
2. Five formats: `-ucode.md`, `-story.md`, `-marp.md`, `-guide.md`, `-config.md`
3. Frontmatter required; keep type-safe via `$lib/types`
4. Do not duplicate types; import shared types
5. Version via `python -m core.version bump app ...` (never hardcode)

## Key Paths

- Svelte app: `app/src/`
- Shared types: `app/src/lib/types/`
- Rust backend: `app/src-tauri/`
- Version: `app/version.json`

## Quick Commands

- Install: `cd app && npm install`
- Dev: `npm run tauri:dev`
- Build: `npm run tauri:build`
- Type check: `npm run check`

## References

- [AGENTS.md](../../AGENTS.md)
- [app/README.md](../../app/README.md)
