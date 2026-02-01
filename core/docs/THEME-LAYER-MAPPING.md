# Theme ↔ Layer Mapping

The Core theme service (`core/services/theme_service.py`) seeds a handful of voice templates from `core/framework/seed/bank/system/themes/` into `/memory/bank/system/themes/` on first boot. Each JSON file contains a `companions` array that links the template to the layer categories it was designed to colorize, and the service applies the replacements just before the text hits the terminal so log files and health reports stay verbatim.

| Theme | Target Layer(s) | Notes |
| --- | --- | --- |
| `dungeon` | `earth_layers_subterranean` | Rune-worn voice for sub-terrain dungeons. Keeps strings simple (Hotkey → Rune Key, Wizard → Golem) and limits replacements to the surface-facing copy so the underground map dialogue feels different without touching logs. |
| `stranger-things` | `earth_layers_subterranean` | UpsideDown flavor for the immediate sub-terrain beneath real-world locations. Use alongside Torn `earth_layers` seeds when the story leans horror or experimental science. |
| `lonely-planet` | `earth_layers` | Soft, Lonely Planet guidance tuned for Earth layers, trails, and friendly adventure—our “fantasy/adventure” voice for surface layers. |
| `doomsday` | `earth_layers` | Apocalypse / survival tone for scorched-Earth stories that still live on the same Earth layer seeds. |
| `hitchhikers` | `galaxy_layers` | Immediate space voice for near-Earth orbit and expedition layers. Keeps the textual load light (“Hotkey” → “42 Button”) so the narrative stays whimsical. |
| `foundation` | `galaxy_layers` | Outer-space settlement voice aligned with deep galaxy layers. Ideal for extraplanetary builds, with replacements that stay in the orbital/survival spectrum. |

Virtual layers reuse these galaxy/outer-space themes today (Foundation and Hitchhiker’s tones double as the “virtual themes”) but you can introduce additional templates by extending the seed folder and adding `virtual_layers` to the `companions` list.

## Working with the seeds
- Add or update a theme JSON in `core/framework/seed/bank/system/themes/` with a `name`, `description`, `companions`, and `replacements`.
- Keep replacements narrowly scoped (core strings such as `uDOS`, `Wizard`, `Hotkey`, `Self-Heal`) so you’re only shifting jargon, not altering diagnostic output.
- The theme service copies these seeds into `memory/bank/system/themes/`; edit the copy there for live tweaks, then commit them back into the seed folder if you want the changes to ship.
- Switch the active theme by setting `UDOS_THEME=<theme-name>` when launching uCODE or by calling `core/services/theme_service.ThemeService.load_theme`.

Dreamed themes are companions to layers, not requirements—if you render an Earth layer but the current theme is `hitchhikers`, the service still applies the replacements but the map data itself stays unchanged. Use the table above as the single-source reference when aligning future Wizard rounds, Hotkey Center briefs, or docs with the theme/layer pairings.
