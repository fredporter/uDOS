# uDOS Emoji Support (GitHub Shortcodes)

Offline-first, deterministic emoji shortcode support for uDOS, based on the canonical GitHub emoji list by rxaviers.

Source gist: [https://gist.github.com/rxaviers/7360908](https://gist.github.com/rxaviers/7360908)

---

## 1. Purpose

This module provides:

- Validation of `:emoji_shortcodes:` (GitHub-compatible)
- Fast lookup via indexed JSON
- Safe extraction from Markdown/text
- Pluggable rendering (terminal, HTML, Unicode, ASCII fallback)

Emoji are treated as **syntax**, not decoration.

---

## 2. Vendored Data

```
vendor/
└─ emoji/
   ├─ github-emoji-shortcodes.md
   └─ github-emoji-shortcodes.json
```

### JSON Shape

```json
{
  "source": {
    "name": "rxaviers/7360908",
    "raw": "https://gist.githubusercontent.com/rxaviers/7360908/raw/..."
  },
  "generatedAt": "2026-02-07",
  "shortcodes": [
    ":smile:",
    ":heart:",
    ":+1:"
  ]
}
```

---

## 3. TypeScript Types

```ts
// src/emoji/types.ts

export type EmojiShortcode = `:${string}:`;

export interface EmojiSourceMeta {
  name: string;
  raw: string;
}

export interface EmojiReference {
  source: EmojiSourceMeta;
  generatedAt: string; // YYYY-MM-DD
  shortcodes: EmojiShortcode[];
}
```

---

## 4. Lookup + Index (O(1))

```ts
// src/emoji/index.ts

import emojiData from "../../vendor/emoji/github-emoji-shortcodes.json";
import type { EmojiReference, EmojiShortcode } from "./types";

const reference = emojiData as EmojiReference;

const EMOJI_SET: ReadonlySet<EmojiShortcode> =
  new Set(reference.shortcodes);

export function isEmojiShortcode(
  token: string
): token is EmojiShortcode {
  return EMOJI_SET.has(token as EmojiShortcode);
}

export function getAllEmojiShortcodes(): EmojiShortcode[] {
  return reference.shortcodes;
}

export function getEmojiMeta() {
  return reference.source;
}
```

---

## 5. Extract Emoji from Text

```ts
// src/emoji/extract.ts

import { isEmojiShortcode } from "./index";
import type { EmojiShortcode } from "./types";

const EMOJI_REGEX = /:[a-z0-9_+\-]+:/gi;

export function extractEmojiShortcodes(
  text: string
): EmojiShortcode[] {
  const matches = text.match(EMOJI_REGEX) ?? [];
  return matches.filter(isEmojiShortcode);
}
```

---

## 6. Replace Emoji (Renderer Hook)

Rendering is **policy-based** and external.

```ts
// src/emoji/replace.ts

import { isEmojiShortcode } from "./index";

export type EmojiRenderer = (shortcode: string) => string;

export function replaceEmojiShortcodes(
  text: string,
  render: EmojiRenderer
): string {
  return text.replace(/:[a-z0-9_+\-]+:/gi, (match) =>
    isEmojiShortcode(match) ? render(match) : match
  );
}
```

---

## 7. Example Renderers

### Terminal-safe (no substitution)

```ts
replaceEmojiShortcodes(text, (s) => s);
```

### HTML hook

```ts
replaceEmojiShortcodes(text, (s) =>
  `<span class=\"emoji\" data-emoji=\"${s}\">${s}</span>`
);
```

### Partial Unicode map

```ts
const MAP: Record<string, string> = {
  ":heart:": "❤️",
  ":+1:": "👍"
};

replaceEmojiShortcodes(text, (s) => MAP[s] ?? s);
```

---

## 8. uDOS Integration Notes

- Emoji are **validated tokens**, not magic characters
- Works identically in:
  - Markdown
  - TUI
  - HTML
  - Logs
  - Scripts
- Enables:
  - Autocomplete
  - Linting
  - Theming
  - ASCII / Unicode fallback modes

Same architecture can later support:

- `@mentions`
- `/commands`
- `#tags`
- Icon glyph packs

---

## 9. Design Principles

- Offline-first
- Deterministic
- Renderer-agnostic
- Zero runtime dependencies
- Vendor once, diff forever

---

## End

