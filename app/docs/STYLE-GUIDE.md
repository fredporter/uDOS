# uMarkdown Style Guide (Typo-derived)

**App Name:** uMarkdown  
**Internal Running Name:** Markdown  
**Base:** Typo (https://typo.robino.dev/) — SvelteKit + Tailwind CSS  
**Version:** 1.0.0  
**Last Updated:** 2026-01-15

---

## Goals

- Keep Typo's UI and layout as-is, but make extensions modular and consistent.
- Standardise class names for:
  - App shell + chrome
  - Editor + preview
  - Preferences panel
  - File operations UI
  - Font toggles (Heading / Body / Code)
- Use Tailwind utilities wherever possible; use a small set of semantic "app classes" as stable hooks.

---

## 1) Naming Conventions

### 1.1 Semantic "app classes"

Use a `mdk-` prefix (for internal "Markdown" app naming) for stable classes that represent components, regions, or behaviours.

**Examples:**

- `mdk-app`
- `mdk-shell`
- `mdk-toolbar`
- `mdk-bottom-bar`
- `mdk-editor`
- `mdk-preview`
- `mdk-preferences`
- `mdk-dialog`

These classes should be used alongside Tailwind utilities.

### 1.2 State classes

Use `is-` for state and `has-` for feature flags.

**Examples:**

- `is-active`
- `is-disabled`
- `is-dragging`
- `has-file`
- `has-folder`
- `has-split-view`

### 1.3 Data attributes for logic hooks

Prefer data attributes for JS behaviour hooks (e.g. menu actions), so class names stay styling-focused.

**Examples:**

- `data-action="open-file"`
- `data-action="open-folder"`
- `data-font-target="heading|body|code"`

---

## 2) Tailwind Structure

### 2.1 Where to put global styles

Create a global stylesheet (if not already present):

**Location:** `src/app.css` (or wherever Typo stores global CSS)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* App-layer semantic hooks + CSS vars live here */
@layer base {
}
@layer components {
}
@layer utilities {
}
```

### 2.2 "Component classes" in Tailwind layer

Define reusable semantic classes in `@layer components`, then apply them in Svelte.

**Example pattern:**

- `.mdk-btn`
- `.mdk-btn--primary`
- `.mdk-panel`
- `.mdk-field`
- `.mdk-toggle`

---

## 3) Global CSS Variables (fonts + sizing)

You want 3 independent font controls: **Heading / Body / Code**.

Define variables on `:root`, then switch them via:

- preferences (persisted)
- bottom-bar toggles (quick switch)
- OS-installed fonts (selected from system list)

### 3.1 Variables

In `@layer base`:

```css
@layer base {
  :root {
    /* Font families (set by Preferences) */
    --mdk-font-heading: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    --mdk-font-body: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    --mdk-font-code: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
      "Liberation Mono", monospace;

    /* Optional: font scale stays controlled by Typo's existing sizing toggles */
    --mdk-prose-scale: 1;
  }
}
```

### 3.2 Mapping variables to Tailwind-friendly classes

Add component hooks:

```css
@layer components {
  .mdk-font-heading {
    font-family: var(--mdk-font-heading);
  }
  .mdk-font-body {
    font-family: var(--mdk-font-body);
  }
  .mdk-font-code {
    font-family: var(--mdk-font-code);
  }

  /* Use this on code blocks too */
  .mdk-code {
    font-family: var(--mdk-font-code);
  }
}
```

---

## 4) Prose Rendering: Separate Heading vs Body Fonts

Typo likely uses Tailwind Typography (`prose`) for rendered markdown. You want:

- headings use `--mdk-font-heading`
- body text uses `--mdk-font-body`
- code uses `--mdk-font-code`
- keep Typo's existing font size toggle behaviour intact

### 4.1 Recommended structure

Wrap the preview in a container that declares "body font", then override headings and code.

Use these classes in the preview root element:

- `mdk-preview`
- `mdk-font-body`
- `prose` (and any Typo-provided prose variants)

**Example class stack:**

```html
<div class="mdk-preview mdk-font-body prose prose-zinc max-w-none">
  <!-- rendered markdown -->
</div>
```

### 4.2 Heading / code overrides (global CSS)

```css
@layer components {
  .mdk-preview :is(h1, h2, h3, h4, h5, h6) {
    font-family: var(--mdk-font-heading);
  }

  .mdk-preview :is(code, pre, kbd, samp) {
    font-family: var(--mdk-font-code);
  }
}
```

This keeps body text as body font because the preview container uses `mdk-font-body`.

---

## 5) Core Component Class Map (uMarkdown)

Use this as the canonical "where do classes go" reference.

### 5.1 App shell

- **Root:** `mdk-app`
- **Window shell:** `mdk-shell`
- **Title bar region:** `mdk-titlebar`
- **Main split layout:** `mdk-main`
- **Left column (editor):** `mdk-pane mdk-pane--editor`
- **Right column (preview):** `mdk-pane mdk-pane--preview`

**Suggested Tailwind pairings:**

- `flex h-screen w-screen overflow-hidden`
- `bg-background text-foreground` (if you have tokens)
- otherwise `bg-zinc-950 text-zinc-50` etc (match Typo)

### 5.2 Toolbars

**Top row:**

- `mdk-toolbar`
- `mdk-toolbar__group`
- `mdk-toolbar__button`

**Bottom bar:**

- `mdk-bottom-bar`
- `mdk-bottom-bar__group`
- `mdk-toggle`
- `mdk-toggle--heading`
- `mdk-toggle--body`
- `mdk-toggle--code`

### 5.3 Editor

- `mdk-editor`
- `mdk-editor__header` (if exists)
- `mdk-editor__surface` (textarea / Monaco / CodeMirror container)
- `mdk-editor__status`

### 5.4 Preview

- `mdk-preview`
- `mdk-preview__surface` (scroll container)
- `mdk-preview__content` (prose root; this is where prose goes)

### 5.5 Preferences panel

- `mdk-preferences`
- `mdk-preferences__nav`
- `mdk-preferences__content`
- `mdk-preferences__section`
- `mdk-field`
- `mdk-field__label`
- `mdk-field__control`
- `mdk-select`
- `mdk-input`
- `mdk-shortcut-hint`

---

## 6) Reusable UI Classes (recommended set)

Define a small library of consistent components.

```css
@layer components {
  .mdk-btn {
    @apply inline-flex items-center justify-center rounded-md px-2.5 py-1.5 text-sm
           transition focus:outline-none focus:ring-2 focus:ring-offset-2;
  }
  .mdk-btn.is-disabled {
    @apply opacity-50 pointer-events-none;
  }

  .mdk-btn--ghost {
    @apply hover:bg-zinc-800/60;
  }
  .mdk-btn--primary {
    @apply bg-zinc-100 text-zinc-900 hover:bg-white;
  }

  .mdk-icon-btn {
    @apply mdk-btn mdk-btn--ghost p-2;
  }

  .mdk-panel {
    @apply rounded-lg border border-zinc-800 bg-zinc-900/40;
  }
  .mdk-panel__header {
    @apply px-4 py-3 border-b border-zinc-800;
  }
  .mdk-panel__body {
    @apply px-4 py-4;
  }

  .mdk-field {
    @apply grid gap-1.5;
  }
  .mdk-field__label {
    @apply text-sm text-zinc-300;
  }
  .mdk-select,
  .mdk-input {
    @apply rounded-md border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm
           focus:outline-none focus:ring-2 focus:ring-offset-2;
  }

  .mdk-divider {
    @apply h-px bg-zinc-800;
  }
}
```

**Note:** Match colours to Typo's current theme tokens if it has them — the pattern matters more than the palette.

---

## 7) Font Toggles (Heading / Body / Code)

### 7.1 Class hooks

Bottom-bar toggle buttons:

- `mdk-toggle mdk-toggle--heading`
- `mdk-toggle mdk-toggle--body`
- `mdk-toggle mdk-toggle--code`
- plus state: `is-active`

### 7.2 Behaviour expectations

- **Preferences** pick a font family → sets:
  - `--mdk-font-heading`
  - `--mdk-font-body`
  - `--mdk-font-code`
- **Bottom-bar toggles** can:
  - enable/disable applying the custom font family (fallback to Typo defaults)
  - OR cycle through "saved sets" (if you add presets later)

### 7.3 Persistence keys (suggested)

- `prefs.font.heading`
- `prefs.font.body`
- `prefs.font.code`
- `prefs.font.enabled.heading`
- `prefs.font.enabled.body`
- `prefs.font.enabled.code`

---

## 8) File Operations (top-row buttons)

Add to the editor's top row buttons:

**Buttons (use `data-action`):**

- `mdk-toolbar__button mdk-icon-btn` + `data-action="open-file"`
- `mdk-toolbar__button mdk-icon-btn` + `data-action="open-folder"`
- `mdk-toolbar__button mdk-icon-btn` + `data-action="reveal-in-finder"` (optional)
- `mdk-toolbar__button mdk-icon-btn` + `data-action="save"` (if applicable)

**State flags on root:**

- `has-file` when file selected
- `has-folder` when folder selected

**Folder open behaviour:**

- default open `README.md`
- else open first `.md`
- else open first supported text/code file

---

## 9) Supported File Types

Use a class on the root when the current document is non-markdown:

- `is-plain-text` for `.txt`
- `is-code` for `.sh`, `.py`, etc.
- `data-file-ext="md|txt|sh|py|..."`

This lets you:

- adjust preview visibility
- adjust syntax highlighting mode
- swap button sets

---

## 10) Suggested File Layout for Styles

- `src/app.css` — global; tailwind layers + variables + semantic classes
- `src/lib/styles/components.css` — optional split if you prefer
- `docs/STYLE-GUIDE.md` — this doc

---

## 11) Quick Class Cheat Sheet

### App

- `mdk-app mdk-shell`
- `mdk-main has-file has-split-view`

### Top bar

- `mdk-toolbar`
- `mdk-toolbar__group`
- `mdk-icon-btn`

### Bottom bar

- `mdk-bottom-bar`
- `mdk-toggle mdk-toggle--heading is-active`
- `mdk-toggle mdk-toggle--body is-active`
- `mdk-toggle mdk-toggle--code is-active`

### Editor

- `mdk-pane mdk-pane--editor`
- `mdk-editor mdk-font-body`

### Preview

- `mdk-pane mdk-pane--preview`
- `mdk-preview mdk-font-body`
- `mdk-preview__content prose ...`

### Preferences

- `mdk-preferences mdk-panel`
- `mdk-field`
- `mdk-select`

---

## 12) Implementation Checklist

- [ ] Replace `src/styles.css` with proper Tailwind layers
- [ ] Add CSS variables for 3 font families
- [ ] Add Tailwind Typography plugin (`@tailwindcss/typography`)
- [ ] Create component classes for reusable UI elements
- [ ] Build Preferences panel component
- [ ] Add 3 font toggle buttons to bottom bar
- [ ] Add file operation buttons to top toolbar
- [ ] Implement Mac Finder integration (Tauri)
- [ ] Add support for `.txt`, `.sh`, `.py` file types
- [ ] Test font switching across all components
- [ ] Test file/folder selection behaviour

---

_This guide is living documentation. Update as patterns evolve._
