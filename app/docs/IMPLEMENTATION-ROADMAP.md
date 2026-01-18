# uMarkdown Implementation Roadmap

**Based on:** STYLE-GUIDE.md + Typo source analysis  
**Date:** 2026-01-15  
**Target:** Complete Typo integration with font management extensions

---

## 🎯 Phase 1: Style System Foundation (2-3 hours)

### Task 1.1: Install Tailwind Typography

```bash
cd /Users/fredbook/Code/uDOS/app
npm install -D @tailwindcss/typography
```

**Update `tailwind.config.js`:**

```javascript
export default {
  content: ["./index.html", "./src/**/*.{js,ts,svelte}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        humanist: [
          "Seravek",
          "Gill Sans Nova",
          "Ubuntu",
          "Calibri",
          "sans-serif",
        ],
        serif: ["ui-serif", "Georgia", "Cambria", "serif"],
        "old-style": ["Iowan Old Style", "Palatino Linotype", "serif"],
        mono: ["JetBrains Mono", "Courier New", "monospace"],
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
```

### Task 1.2: Overhaul styles.css

**Replace `/app/src/styles.css` with:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ============================================
   uMarkdown Style System
   Based on: docs/STYLE-GUIDE.md
   ============================================ */

@layer base {
  /* Text wrapping (from Typo) */
  h1 {
    text-wrap: balance;
  }

  p,
  li {
    text-wrap: pretty;
  }

  /* Font CSS Variables */
  :root {
    /* Three independent font controls */
    --mdk-font-heading: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    --mdk-font-body: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    --mdk-font-code: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
      "Liberation Mono", monospace;

    /* Font scale (controlled by Typo-style toggles) */
    --mdk-prose-scale: 1;

    /* Syntax highlighting (from Typo) */
    --shiki-foreground: rgb(229 231 235); /* gray-200 */
    --shiki-background: rgb(17 24 39); /* gray-900 */
    --shiki-token-constant: rgb(249 250 251); /* gray-50 */
    --shiki-token-string: rgb(186 230 253); /* sky-200 */
    --shiki-token-comment: rgb(156 163 175); /* gray-400 */
    --shiki-token-keyword: rgb(153 246 228); /* teal-300 */
    --shiki-token-parameter: rgb(209 213 219); /* gray-300 */
    --shiki-token-function: rgb(165 180 252); /* indigo-300 */
    --shiki-token-string-expression: rgb(186 230 253); /* sky-200 */
    --shiki-token-punctuation: rgb(209 213 219); /* gray-300 */
    --shiki-token-link: rgb(209 213 219); /* gray-300 */
  }
}

@layer components {
  /* ============================================
     Font Application Classes
     ============================================ */
  .mdk-font-heading {
    font-family: var(--mdk-font-heading);
  }
  .mdk-font-body {
    font-family: var(--mdk-font-body);
  }
  .mdk-font-code {
    font-family: var(--mdk-font-code);
  }

  /* Preview-specific overrides */
  .mdk-preview :is(h1, h2, h3, h4, h5, h6) {
    font-family: var(--mdk-font-heading);
  }

  .mdk-preview :is(code, pre, kbd, samp) {
    font-family: var(--mdk-font-code);
  }

  /* ============================================
     Reusable Button Styles
     ============================================ */
  .mdk-btn {
    @apply inline-flex items-center justify-center rounded-md px-2.5 py-1.5 text-sm
           transition focus:outline-none focus:ring-2 focus:ring-offset-2;
  }

  .mdk-btn.is-disabled {
    @apply opacity-50 pointer-events-none;
  }

  .mdk-btn--ghost {
    @apply hover:bg-gray-200 dark:hover:bg-gray-800/60;
  }

  .mdk-btn--primary {
    @apply bg-brand-600 text-white hover:bg-brand-700;
  }

  .mdk-icon-btn {
    @apply mdk-btn mdk-btn--ghost p-2;
  }

  /* ============================================
     Panel & Form Components
     ============================================ */
  .mdk-panel {
    @apply rounded-lg border border-gray-300 dark:border-gray-800 bg-white dark:bg-gray-900/40;
  }

  .mdk-panel__header {
    @apply px-4 py-3 border-b border-gray-300 dark:border-gray-800;
  }

  .mdk-panel__body {
    @apply px-4 py-4;
  }

  .mdk-field {
    @apply grid gap-1.5;
  }

  .mdk-field__label {
    @apply text-sm text-gray-700 dark:text-gray-300 font-medium;
  }

  .mdk-select,
  .mdk-input {
    @apply rounded-md border border-gray-300 dark:border-gray-800
           bg-white dark:bg-gray-950 px-3 py-2 text-sm
           focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2;
  }

  .mdk-divider {
    @apply h-px bg-gray-300 dark:bg-gray-800;
  }

  /* ============================================
     Toggle Buttons (Bottom Bar)
     ============================================ */
  .mdk-toggle {
    @apply px-3 py-1.5 rounded-md text-sm transition
           hover:bg-gray-200 dark:hover:bg-gray-800;
  }

  .mdk-toggle.is-active {
    @apply bg-brand-600 text-white hover:bg-brand-700;
  }

  /* ============================================
     Layout Components
     ============================================ */
  .mdk-toolbar {
    @apply flex items-center gap-2 px-4 py-2 border-b border-gray-300 dark:border-gray-800;
  }

  .mdk-toolbar__group {
    @apply flex items-center gap-1;
  }

  .mdk-bottom-bar {
    @apply flex items-center justify-between px-4 py-2 border-t border-gray-300 dark:border-gray-800;
  }

  .mdk-bottom-bar__group {
    @apply flex items-center gap-2;
  }
}
```

---

## 🎯 Phase 2: Core Components (3-4 hours)

### Task 2.1: Create Bottom Bar Component

**File:** `src/components/BottomBar.svelte`

```svelte
<script lang="ts">
  import { writable } from 'svelte/store';

  // Font toggle states
  let headingEnabled = writable(true);
  let bodyEnabled = writable(true);
  let codeEnabled = writable(true);

  // Font size options (from Typo)
  const fontSizes = ['prose-sm', 'prose-base', 'prose-lg', 'prose-xl', 'prose-2xl'];
  let currentSize = writable(1); // index into fontSizes

  function toggleFont(target: 'heading' | 'body' | 'code') {
    if (target === 'heading') headingEnabled.update(v => !v);
    if (target === 'body') bodyEnabled.update(v => !v);
    if (target === 'code') codeEnabled.update(v => !v);
  }

  function cycleSize() {
    currentSize.update(v => (v + 1) % fontSizes.length);
  }
</script>

<div class="mdk-bottom-bar">
  <div class="mdk-bottom-bar__group">
    <button
      class="mdk-toggle mdk-toggle--heading"
      class:is-active={$headingEnabled}
      on:click={() => toggleFont('heading')}
      data-font-target="heading"
    >
      Heading Font
    </button>

    <button
      class="mdk-toggle mdk-toggle--body"
      class:is-active={$bodyEnabled}
      on:click={() => toggleFont('body')}
      data-font-target="body"
    >
      Body Font
    </button>

    <button
      class="mdk-toggle mdk-toggle--code"
      class:is-active={$codeEnabled}
      on:click={() => toggleFont('code')}
      data-font-target="code"
    >
      Code Font
    </button>
  </div>

  <div class="mdk-bottom-bar__group">
    <button class="mdk-icon-btn" on:click={cycleSize}>
      {fontSizes[$currentSize]}
    </button>
  </div>
</div>
```

### Task 2.2: Create Toolbar Component

**File:** `src/components/Toolbar.svelte`

```svelte
<script lang="ts">
  import { open } from '@tauri-apps/plugin-opener';

  async function openFile() {
    // TODO: Implement Tauri file picker
    console.log('Open file');
  }

  async function openFolder() {
    // TODO: Implement Tauri folder picker
    console.log('Open folder');
  }

  async function saveFile() {
    // TODO: Implement save logic
    console.log('Save file');
  }

  async function revealInFinder() {
    // TODO: Implement Finder reveal
    console.log('Reveal in Finder');
  }
</script>

<div class="mdk-toolbar">
  <div class="mdk-toolbar__group">
    <button
      class="mdk-icon-btn"
      on:click={openFile}
      data-action="open-file"
      title="Open File (⌘O)"
    >
      📄
    </button>

    <button
      class="mdk-icon-btn"
      on:click={openFolder}
      data-action="open-folder"
      title="Open Folder"
    >
      📁
    </button>

    <button
      class="mdk-icon-btn"
      on:click={saveFile}
      data-action="save"
      title="Save (⌘S)"
    >
      💾
    </button>

    <button
      class="mdk-icon-btn"
      on:click={revealInFinder}
      data-action="reveal-in-finder"
      title="Reveal in Finder"
    >
      🔍
    </button>
  </div>
</div>
```

### Task 2.3: Create Preferences Component

**File:** `src/components/Preferences.svelte`

```svelte
<script lang="ts">
  import { onMount } from 'svelte';

  // System fonts will be loaded from macOS
  let systemFonts: string[] = [];

  // Current selections
  let headingFont = 'Inter';
  let bodyFont = 'Inter';
  let codeFont = 'JetBrains Mono';

  onMount(async () => {
    // TODO: Query macOS system fonts via Tauri
    systemFonts = [
      'Inter',
      'San Francisco',
      'Helvetica Neue',
      'Georgia',
      'Palatino',
      'Courier New',
      'Monaco',
      'JetBrains Mono',
    ];

    // Load from localStorage
    const saved = localStorage.getItem('mdk-font-preferences');
    if (saved) {
      const prefs = JSON.parse(saved);
      headingFont = prefs.heading || headingFont;
      bodyFont = prefs.body || bodyFont;
      codeFont = prefs.code || codeFont;
    }

    applyFonts();
  });

  function applyFonts() {
    document.documentElement.style.setProperty('--mdk-font-heading', headingFont);
    document.documentElement.style.setProperty('--mdk-font-body', bodyFont);
    document.documentElement.style.setProperty('--mdk-font-code', codeFont);

    // Persist
    localStorage.setItem('mdk-font-preferences', JSON.stringify({
      heading: headingFont,
      body: bodyFont,
      code: codeFont,
    }));
  }

  $: {
    headingFont;
    bodyFont;
    codeFont;
    applyFonts();
  }
</script>

<div class="mdk-preferences mdk-panel">
  <div class="mdk-panel__header">
    <h3 class="text-lg font-semibold">Preferences</h3>
  </div>

  <div class="mdk-panel__body space-y-4">
    <div class="mdk-field">
      <label class="mdk-field__label" for="heading-font">Heading Font</label>
      <select class="mdk-select" id="heading-font" bind:value={headingFont}>
        {#each systemFonts as font}
          <option value={font}>{font}</option>
        {/each}
      </select>
    </div>

    <div class="mdk-field">
      <label class="mdk-field__label" for="body-font">Body Font</label>
      <select class="mdk-select" id="body-font" bind:value={bodyFont}>
        {#each systemFonts as font}
          <option value={font}>{font}</option>
        {/each}
      </select>
    </div>

    <div class="mdk-field">
      <label class="mdk-field__label" for="code-font">Code Font</label>
      <select class="mdk-select" id="code-font" bind:value={codeFont}>
        {#each systemFonts as font}
          <option value={font}>{font}</option>
        {/each}
      </select>
    </div>
  </div>
</div>
```

---

## 🎯 Phase 3: Integration & Testing (2 hours)

### Task 3.1: Update App.svelte

Integrate new components:

- Import Toolbar, BottomBar, Preferences
- Add proper class names (mdk-app, mdk-shell, etc)
- Apply mdk-font-body to editor/preview

### Task 3.2: Test Font Switching

- [ ] Verify heading font changes independently
- [ ] Verify body font changes independently
- [ ] Verify code font changes independently
- [ ] Test persistence (reload page)
- [ ] Test with different font combinations

### Task 3.3: Test File Operations

- [ ] Open .md file
- [ ] Open .txt file
- [ ] Open .py file
- [ ] Open folder (auto-select README.md)
- [ ] Save file
- [ ] Reveal in Finder

---

## 📋 Checklist Summary

### Phase 1: Foundation

- [ ] Install @tailwindcss/typography
- [ ] Update tailwind.config.js with font families
- [ ] Replace styles.css with full @layer structure
- [ ] Add CSS variables for fonts
- [ ] Add component classes (.mdk-\*)

### Phase 2: Components

- [ ] Create BottomBar.svelte
- [ ] Create Toolbar.svelte
- [ ] Create Preferences.svelte
- [ ] Wire up font toggles
- [ ] Wire up file operations

### Phase 3: Integration

- [ ] Refactor App.svelte
- [ ] Test all font switching
- [ ] Test file operations
- [ ] Add keyboard shortcuts
- [ ] Polish UI

---

## 🔗 Key Files to Modify

| File                                   | Action                        | Complexity |
| -------------------------------------- | ----------------------------- | ---------- |
| `tailwind.config.js`                   | Add typography plugin + fonts | Low        |
| `src/styles.css`                       | Complete overhaul             | Medium     |
| `src/components/BottomBar.svelte`      | Create new                    | Medium     |
| `src/components/Toolbar.svelte`        | Create new                    | Medium     |
| `src/components/Preferences.svelte`    | Create new                    | High       |
| `src/App.svelte`                       | Refactor layout               | Medium     |
| `src/components/Preview.svelte`        | Add mdk- classes              | Low        |
| `src/components/MarkdownEditor.svelte` | Add mdk- classes              | Low        |

---

## 🎓 Typo Patterns to Port

From studying `/library/ucode/typo/src/`:

1. **Font size cycling:** Use `prose-sm`, `prose-base`, `prose-lg`, `prose-xl`, `prose-2xl`
2. **Font family options:** Support sans, humanist, serif, old-style, mono
3. **View mode toggle:** Expand preview to full width
4. **Text wrapping:** Use `text-wrap: balance` for headings, `text-wrap: pretty` for body
5. **Syntax highlighting:** Use Shiki CSS variables (already included in styles.css)

---

## 🚀 Launch Commands

```bash
# Development
cd /Users/fredbook/Code/uDOS/app
npm run tauri:dev

# Build
npm run tauri:build
```

---

_Next: Start with Phase 1, Task 1.1_
