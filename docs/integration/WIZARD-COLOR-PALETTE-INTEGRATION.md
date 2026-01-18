# Wizard Color Palette Integration

**Date:** 2026-01-18
**Version:** Wizard v1.1.0.0
**Status:** ✅ Complete

---

## Overview

Integrated the official uDOS 32-color palette v2.0.0 into the Wizard dashboard and configured all wizard pages for Tailwind dark mode as default with light mode provision.

---

## Changes Made

### 1. Pixel Editor Color Palette

**File:** [public/wizard/dashboard/src/lib/pages/PixelEditor.svelte](dashboard/src/lib/pages/PixelEditor.svelte)

**Updates:**

- ✅ Replaced 8-color palette with full 32-color uDOS palette v2.0.0
- ✅ Organized colors into 4 categories:
  - **Terrain** (0-7): Forest, Grass, Deep Water, Water, Earth, Sand, Mountain, Snow
  - **Markers** (8-15): Danger, Alert, Waypoint, Safe, Objective, Purple, Pink, Magenta
  - **Greyscale** (16-23): Black → White (8-step ramp)
  - **Special** (24-31): Skin tones, Lava, Ice, Toxic, Deep Sea
- ✅ Enhanced color picker with organized `<optgroup>` categories
- ✅ Added color previews in dropdown (colored backgrounds + proper text contrast)

**Color Count:** 32 colors (up from 8)
**Format:** Organized categories with semantic naming

---

### 2. Dark Mode Configuration

#### HTML Templates

**File:** [public/wizard/dashboard/src/index.html](dashboard/src/index.html)

**Updates:**

- ✅ Added `class="dark"` to `<html>` element
- ✅ Added dark mode initialization script with localStorage provision
- ✅ Configured Tailwind to use class strategy (`darkMode: 'class'`)

**Strategy:**

```javascript
// Dark mode by default
if (localStorage.theme === "light") {
  document.documentElement.classList.remove("dark");
} else {
  document.documentElement.classList.add("dark");
}
```

#### Jinja2 Base Template

**File:** [public/wizard/web/templates/base.html](web/templates/base.html)

**Updates:**

- ✅ Added `class="dark"` to `<html>` element
- ✅ Added dark mode initialization script
- ✅ Configured Tailwind with `darkMode: 'class'` config
- ✅ Added uDOS color palette as CSS custom properties (`--udos-*`)
- ✅ Updated all UI elements with proper `dark:` classes:
  - Navigation: `bg-gray-100 dark:bg-gray-800`
  - Text: `text-gray-900 dark:text-white`
  - Borders: `border-gray-200 dark:border-gray-700`
  - Links: `text-blue-600 dark:text-blue-400`
  - Status indicator: `text-green-600 dark:text-green-400`

**CSS Variables Added:**

```css
:root {
  /* Tailwind Standard Colors */
  --color-primary: #3b82f6;
  --color-secondary: #8b5cf6;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;

  /* uDOS Terrain Colors */
  --udos-forest: #2d5016;
  --udos-grass: #4c9a2a;
  --udos-deep-water: #1b4965;
  --udos-water: #3377dd;
  --udos-earth: #6b4423;
  --udos-sand: #e0b984;
  --udos-mountain: #4f646f;
  --udos-snow: #f2f6f9;

  /* uDOS Marker Colors */
  --udos-danger: #dc2626;
  --udos-alert: #ff7a1a;
  --udos-waypoint: #ffd23f;
  --udos-safe: #00e89a;
  --udos-objective: #00bfe6;

  /* uDOS Special Colors */
  --udos-lava: #ff4500;
  --udos-ice: #a7c7e7;
  --udos-toxic: #2ee312;
  --udos-deep-sea: #003366;
}
```

#### Global CSS

**File:** [public/wizard/dashboard/src/app.css](dashboard/src/app.css)

**Updates:**

- ✅ Changed default theme to dark mode
- ✅ Replaced `@media (prefers-color-scheme: dark)` with explicit class strategy
- ✅ Added smooth transitions for theme switching
- ✅ Enhanced typography defaults with dark mode support

**Before:**

```css
html {
  background: white;
  color: #1f2937;
}

@media (prefers-color-scheme: dark) {
  html {
    background: #111827;
    color: #f3f4f6;
  }
}
```

**After:**

```css
/* Dark mode by default */
html {
  background: #111827;
  color: #f3f4f6;
}

/* Light mode when class removed */
html:not(.dark) {
  background: white;
  color: #1f2937;
}

/* Smooth transitions */
* {
  @apply transition-colors duration-200;
}
```

---

### 3. Verified Dark Mode Compliance

**Audited Pages:**

- ✅ [Dashboard.svelte](dashboard/src/lib/pages/Dashboard.svelte) — All dark classes present
- ✅ [FontManager.svelte](dashboard/src/lib/pages/FontManager.svelte) — Full dark mode support
- ✅ [PixelEditor.svelte](dashboard/src/lib/pages/PixelEditor.svelte) — Updated with new palette + dark mode
- ✅ [FeatureCard.svelte](dashboard/src/lib/components/FeatureCard.svelte) — Dark mode ready
- ✅ [APIStatus.svelte](dashboard/src/lib/components/APIStatus.svelte) — Dark mode ready
- ✅ [ServiceStatus.svelte](dashboard/src/lib/components/ServiceStatus.svelte) — Dark mode ready

**Pattern Used:**

```svelte
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-gray-200 dark:border-gray-700">
```

---

## Future: Light Mode Toggle

**Provision Added:**

1. **localStorage detection** — Script checks `localStorage.theme` on page load
2. **Class strategy** — Tailwind configured to use `class="dark"` on `<html>`
3. **Toggle implementation** (coming soon):

```javascript
// Add this to any page for theme toggle
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.classList.contains("dark");

  if (isDark) {
    html.classList.remove("dark");
    localStorage.theme = "light";
  } else {
    html.classList.add("dark");
    localStorage.theme = "dark";
  }
}
```

**UI Suggestion:**

```html
<button
  onclick="toggleTheme()"
  class="px-3 py-2 rounded-lg bg-gray-200 dark:bg-gray-700"
>
  <span class="dark:hidden">🌙</span>
  <span class="hidden dark:inline">☀️</span>
</button>
```

---

## Reference

**Palette Specification:** [dev/roadmap/u_dos_colour_palette_specification.md](../../dev/roadmap/u_dos_colour_palette_specification.md)
**Tailwind Dark Mode Docs:** https://tailwindcss.com/docs/dark-mode

---

## Checklist

- [x] Wire 32-color palette into Pixel Editor
- [x] Organize colors into semantic categories
- [x] Add `dark` class to all HTML templates
- [x] Configure Tailwind `darkMode: 'class'` strategy
- [x] Add uDOS color CSS variables to base template
- [x] Update navigation, footer, status with dark mode classes
- [x] Update global CSS to default dark mode
- [x] Verify all Svelte pages/components have dark mode
- [x] Add localStorage provision for light mode toggle
- [x] Document future light mode toggle implementation

---

**Status:** ✅ Complete — All wizard pages configured for dark mode with uDOS color palette v2.0.0
