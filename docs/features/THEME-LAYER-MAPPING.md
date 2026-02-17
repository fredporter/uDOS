# Theme ↔ Layer Mapping

The Core theme service (`core/services/theme_service.py`) seeds a handful of voice templates from `core/framework/seed/bank/system/themes/` into `memory/system/themes/` on first boot. Each JSON file contains a `companions` array that links the template to layer categories, and the service now applies a **simplified TUI message vocabulary** just before text hits the terminal.

Scope boundary:
- This mapping is for **Core TUI message IO only**.
- It is not a GUI/CSS/WebView styling system.
- Wizard webview theme/styling is a separate future round.
- Legacy broad replacement seeds are archived at:
  - `core/framework/seed/bank/system/themes/.archive/2026-02-15-legacy-broad-replacements/`

| Theme | Target Layer(s) | Notes |
| --- | --- | --- |
| `dungeon` | `earth_layers_subterranean` | Rune-worn voice for sub-terrain dungeons. Keeps strings simple (Hotkey → Rune Key, Wizard → Golem) and limits replacements to the surface-facing copy so the underground map dialogue feels different without touching logs. |
| `fantasy` | `earth_layers_subterranean`, `earth_layers` | Quest-style voice for dungeon/overworld messaging (`Quest Tip`, `Arcane Ops`). |
| `role-play` | `earth_layers_subterranean`, `earth_layers` | Tabletop role-play voice for party/narrative messaging (`Role Tip`, `Narrator Ops`). |
| `stranger-things` | `earth_layers_subterranean` | UpsideDown flavor for sub-terrain messaging (`Upside Tip`, `Signal Ops`) without changing command/log contracts. |
| `explorer` | `earth_layers`, `regional_layers` | Expedition voice for route/surface traversal messaging (`Expedition Tip`, `Survey Ops`). |
| `lonely-planet` | `earth_layers` | Explorer guidance voice for surface messaging (`Trail Tip`, `Guide Ops`). |
| `doomsday` | `earth_layers` | Survival voice for critical messaging (`Survival Tip`, `Fallback Ops`). |
| `hitchhikers` | `galaxy_layers` | Immediate space voice for near-Earth orbit and expedition messaging (`42 Tip`, `Guide Console`). |
| `foundation` | `galaxy_layers` | Outer-space settlement voice aligned with deep galaxy layers. Ideal for extraplanetary builds, with replacements that stay in the orbital/survival spectrum. |
| `galaxy` | `galaxy_layers` | Explicit alias-friendly galaxy messaging profile used for orbital/stellar map levels in TUI copy. |
| `pilot` | `galaxy_layers`, `orbital_layers` | Cockpit/navigation voice for flight-path operations (`Cockpit Tip`, `Flight Ops`). |
| `captain-sailor` | `galaxy_layers`, `regional_layers` | Bridge-and-crew command voice (`Bridge Tip`, `Deck Ops`). |
| `pirate` | `galaxy_layers`, `earth_layers_subterranean` | Raider voice for risky traversal/combat messaging (`Raid Tip`, `Corsair Ops`). |
| `adventure` | `earth_layers`, `regional_layers` | General exploration voice (`Adventure Tip`, `Expedition Ops`). |
| `scavenge-hunt` | `earth_layers`, `earth_layers_subterranean` | Resource-recovery voice (`Scavenge Tip`, `Scrap Ops`). |
| `traveller` | `earth_layers`, `galaxy_layers` | Route/transit voice (`Traveller Tip`, `Route Ops`). |
| `scientist` | `galaxy_layers`, `stellar_layers` | Systems/lab voice for orbital and stellar operations (`Lab Tip`, `Research Ops`). |

Virtual layers reuse these galaxy/outer-space themes today (Foundation and Hitchhiker’s tones double as the “virtual themes”) but you can introduce additional templates by extending the seed folder and adding `virtual_layers` to the `companions` list.

## Working with the seeds
- Add or update a theme JSON in `core/framework/seed/bank/system/themes/` with a `name`, `description`, `companions`, and `replacements`.
- Keep replacements narrowly scoped (message labels such as `Tip:`, `Health:`, `Wizard`) so you’re only shifting operator-facing wording.
- The theme service copies these seeds into `memory/system/themes/`; edit the copy there for live tweaks, then commit them back into the seed folder if you want the changes to ship.
- Switch the active base theme by setting `UDOS_THEME=<theme-name>` when launching uCODE or by calling `core/services/theme_service.ThemeService.load_theme`.
- For TUI message routing, optionally set:
  - `UDOS_TUI_MESSAGE_THEME=dungeon|foundation|galaxy`
  - `UDOS_TUI_MESSAGE_THEME=fantasy|role-play|explorer|scientist|pilot|captain-sailor|pirate|adventure|scavenge-hunt|traveller|stranger-things|lonely-planet|doomsday|hitchhikers|dungeon|foundation|galaxy`
  - `UDOS_TUI_MAP_LEVEL=dungeon|foundation|galaxy|...`
  - `UDOS_TUI_LEGACY_REPLACEMENTS=1` to temporarily restore broad legacy text replacement behavior.

Dreamed themes are companions to layers, not requirements—if you render an Earth layer but the current theme is `hitchhikers`, the service still applies the replacements but the map data itself stays unchanged. Use the table above as the single-source reference when aligning future Wizard rounds, Hotkey Center briefs, or docs with the theme/layer pairings.

## TUI Z-layer and Theme Switching

The TUI uses spatial z/elevation data for map semantics while message theming stays a separate, explicit switch.

- Spatial side:
  - `LocId` can carry `-Zz` (for example `L305-DA11-Z-2`).
  - Seed overlays can define `z`, `z_min`, `z_max`, `stairs`, `ramps`, and `portals`.
- Message side:
  - `UDOS_TUI_MAP_LEVEL` hints the message-level bucket (`dungeon`, `foundation`, `galaxy`).
  - `UDOS_TUI_MESSAGE_THEME` pins a specific vocabulary profile.

Recommended z-to-level convention for TUI map messaging:

| Spatial signal | Recommended `UDOS_TUI_MAP_LEVEL` | Typical theme picks |
| --- | --- | --- |
| `SUB` space, negative z, or underground traversal | `dungeon` | `dungeon`, `fantasy`, `role-play`, `pirate`, `scavenge-hunt` |
| Surface/regional traversal around baseline elevation | `foundation` | `explorer`, `adventure`, `traveller`, `lonely-planet`, `doomsday` |
| Orbital/stellar/celestial traversal and high-band maps | `galaxy` | `galaxy`, `foundation`, `pilot`, `captain-sailor`, `scientist`, `hitchhikers` |

The convention above is for consistent operator wording in terminal output. It does not mutate place records or renderer state.

## TOYBOX Lens Profile Switches

TOYBOX profile changes and TUI message theme switching are complementary:

```bash
# Dungeon lens
PLAY TOYBOX SET hethack
export UDOS_TUI_MAP_LEVEL=dungeon
export UDOS_TUI_MESSAGE_THEME=dungeon

# Galaxy lens
PLAY TOYBOX SET elite
export UDOS_TUI_MAP_LEVEL=galaxy
export UDOS_TUI_MESSAGE_THEME=pilot
```

If you only set `PLAY TOYBOX`, gameplay profile state changes but message wording does not automatically switch. Keep the theme switch explicit so operators can override tone per session.
