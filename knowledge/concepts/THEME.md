---
uid: udos-knowledge-theme-20260201120000-UTC
title: Theme System
tags: [concepts, theme]
status: living
updated: 2026-02-01
---

# Theme System

The theme system keeps verbage simple: it maps a very small set of words
before the Core TUI sends text to the terminal so you can change the voice
without touching logs.

## Theme files

- Seed copies live in `core/framework/seed/bank/system/themes/`. Six variants ship
  with uDOS: `default`, `dungeon`, `doomsday`, `foundation`, `lonelyplant`,
  `hitchhikers`, and `stranger-things`.
- Run `core/services/theme_service.py` to copy seeds into `/memory/bank/system/themes`
  on first startup. Edit the copies under `/memory/bank/system/themes` to keep
  local changes.
- Each JSON file defines `"replacements"` (a simple key → value map). The Theme
  Service applies these substitutions in order for every text path that calls
  `theme.format(...)`.

## Switching themes

Set `UDOS_THEME` before starting uCODE (`UDOS_THEME=dungeon ./bin/Launch-uCODE.sh`)
to load another voice. Themes gracefully fall back to `default` if their file is
missing.

## Scope

- Only the Core TUI strings that run through `get_theme_service()` are touched
  (banner, hints, help, status, etc.).
- Glacier outputs such as logs, automation JSON, or automation scripts are never
  themed; replacements happen just before the string is printed to the user so
  Guardian messages remain clear for debugging.

## Extending

1. Drop a new `<name>.json` file into `/memory/bank/system/themes/` (or the
   seed directory for future resets).
2. List the tokens you want to change (e.g., `"uDOS": "NightVault"`).
3. Start uCODE with `UDOS_THEME=<name>`; the service auto-loads the themed map.

## Theme ↔ Layer Companions

- **Dungeon** pairs with the subterranean/teletext layers (`earth_layers`, `virtual_layers`) when running deep dives—think subsurface grids.
- **Stranger Things** is intended for “Upside-Down” sub-terrain layers that sit directly under real-world Earth tiles, keying off the same location IDs.
- **Fantasy/Adventure** (Earth) theme works with surface/earth layers such as `L100`/`L200` and any adventure-focused catalog entries.
- **Virtual** variations belong to the `virtual_layers` pieces that still map back to real-world coordinates (data centers, simulation nodes).
- **Lonely Planet** pairs with Earth layers like `L100`/`L200` for calming, travel-friendly output.
- **Hitchhikers Guide** fits the immediate space/low orbit layers (`L306`, orbital connections).
- **Foundation** accentuates the outer-space layers and station builds (distant orbitals, settlements beyond L306).

Themes are companions to map layers; they keep the same grid data but add flavor without altering georeference IDs.
