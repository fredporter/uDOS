# uDOS VS Code Language Support

Syntax highlighting and snippets for uDOS runtime blocks inside Markdown.

## Features

- TextMate grammar for uDOS runtime blocks (`state`, `set`, `form`, `if`, `else`, `nav`, `panel`, `map`)
- Highlights variables (`$var`), keywords, directives, booleans, numbers, and strings
- Snippets for quickly inserting fenced blocks with common fields
- Works in fenced code blocks inside Markdown using the fence name (e.g. ```state)

## Usage

1. Open any uDOS markdown file (e.g. `.script.md`, `.ucode.md`, `.story.md`).
2. Add a fenced code block with one of the supported names:
   - `state / `set / `form / `if / `else / `nav / `panel / `map
3. Syntax highlighting is applied automatically.
4. Use snippets (prefix `udos-...`) to insert common block shapes.

## Snippet Prefixes

- `udos-state` – state initialization
- `udos-set` – mutations (`inc`, `dec`, `set`, `toggle`)
- `udos-if` – if/else with panel output
- `udos-form` – form fields
- `udos-nav` – navigation choices
- `udos-panel` – panel text with `$variables`
- `udos-map` – map viewport + sprites

## Project Layout

```
extensions/vscode/
├── package.json          # VS Code extension manifest
├── README.md             # This file
├── snippets/udos.json    # Snippets for markdown + udos blocks
└── syntaxes/udos.json    # TextMate grammar
```

## Notes

- No build step required (`npm run compile` is a no-op).
- The language id is `udos` with aliases matching fence names.
- Designed to stay lightweight for offline use.
