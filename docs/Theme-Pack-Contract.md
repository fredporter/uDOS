# Theme Pack Contract

Reflecting `docs/uDOS-v1-3.md` sections 4 and 12, every theme pack must keep publishing framework-free and deterministic.

## Structure
```
themes/<name>/
  shell.html     # static HTML wrapper with slot placeholders
  theme.css      # minimal styles (Tailwind, retro, etc.)
  assets/        # fonts, sprites, JS, etc.
  theme.json     # metadata describing the pack
```

## shell.html
- Must define the slots `{{content}}`, `{{title}}`, `{{nav}}`, `{{meta}}`, and `{{footer}}`. Additional slots are permitted but optional.
- Should be a complete HTML document (DOCTYPE, `<html>`, `<head>`/`<body>`).
- Should reference local assets only (no external CDNs) to respect offline-first goals.

## theme.json
Example keys:
- `name`, `version`, `description`
- `mode`: `article`, `retro`, `slides`, or `forms`
- `requiredAssets`: list of files to copy into `_site/`
- `defaultTypography`: body/heading/code stack (applies to both the editor preview and exported HTML)
- `slots`: enumerated slot names consumed by the renderer

## Output
- Renderer (part of `core/`) expands Markdown into HTML, injects it into `shell.html`, and writes files to `vault/_site/<theme>/...`.
- themes should be referenceable by name so `wizard/` and the control plane can list them.
- Theme metadata drives preview panes and static export pipelines without requiring SvelteKit components.

## Universal component alignment
- SvelteKit components and portal previews should reuse the slots/data described here so HTML/headless lanes share contracts. See `docs/Universal-Components-Contract.md` for the combined HTML/data/CSS-token guidance.
- Tokens such as those defined in `docs/CSS-Tokens.md` ensure exported themes and the admin UI stay visually consistent without tying themselves to a specific styling library.
