# Theme ↔ Layer Mapping

The Core theme service (`core/services/theme_service.py`) seeds a handful of voice templates from `core/framework/seed/bank/system/themes/` into `memory/system/themes/` on first boot. Each JSON file contains a `companions` array that links the template to layer categories, and the service now applies a **simplified TUI message vocabulary** just before text hits the terminal.

Scope boundary:
- This mapping is for **Core TUI message IO only**.
- It is not a GUI/CSS/WebView styling system.
- Wizard webview theme/styling is a separate future round.

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
| `scientist` | `galaxy_layers`, `stellar_layers` | Systems/lab voice for orbital and stellar operations (`Lab Tip`, `Research Ops`). |

Virtual layers reuse these galaxy/outer-space themes today (Foundation and Hitchhiker’s tones double as the “virtual themes”) but you can introduce additional templates by extending the seed folder and adding `virtual_layers` to the `companions` list.

## Working with the seeds
- Add or update a theme JSON in `core/framework/seed/bank/system/themes/` with a `name`, `description`, `companions`, and `replacements`.
- Keep replacements narrowly scoped (message labels such as `Tip:`, `Health:`, `Wizard`) so you’re only shifting operator-facing wording.
- The theme service copies these seeds into `memory/system/themes/`; edit the copy there for live tweaks, then commit them back into the seed folder if you want the changes to ship.
- Switch the active base theme by setting `UDOS_THEME=<theme-name>` when launching uCODE or by calling `core/services/theme_service.ThemeService.load_theme`.
- For TUI message routing, optionally set:
  - `UDOS_TUI_MESSAGE_THEME=dungeon|foundation|galaxy`
  - `UDOS_TUI_MESSAGE_THEME=fantasy|role-play|explorer|scientist|stranger-things|lonely-planet|doomsday|hitchhikers|dungeon|foundation|galaxy`
  - `UDOS_TUI_MAP_LEVEL=dungeon|foundation|galaxy|...`
  - `UDOS_TUI_LEGACY_REPLACEMENTS=1` to temporarily restore broad legacy text replacement behavior.

Dreamed themes are companions to layers, not requirements—if you render an Earth layer but the current theme is `hitchhikers`, the service still applies the replacements but the map data itself stays unchanged. Use the table above as the single-source reference when aligning future Wizard rounds, Hotkey Center briefs, or docs with the theme/layer pairings.
