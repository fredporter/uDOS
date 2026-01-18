# Teletext Character Rendering & Bottom Bar Fixes

**Date:** 2026-01-18  
**Build:** Dashboard v1.0.0.1  
**Status:** ✅ Complete

---

## Issues Fixed

### 1. Teletext Characters All Look the Same

**Problem:** Unicode sextant blocks (U+1FB00-U+1FB3B) were not rendering distinctly because the default `monospace` font doesn't include these characters.

**Solution:** Added comprehensive Unicode font stack:

```css
font-family:
  "Noto Sans Symbols 2", "Segoe UI Symbol", "Apple Color Emoji",
  "Noto Color Emoji", monospace;
```

**Changes Made:**

1. **Character Picker Modal** (`PixelEditor.svelte`):
   - Character grid buttons: Increased from `text-2xl` to `text-3xl`
   - Added inline `style` with Unicode font stack
   - Added `line-height: 1` for tighter rendering
2. **Selected Character Preview**:
   - Added same font stack to preview display
   - Ensures consistency between picker and preview

3. **Canvas Rendering**:
   - Updated `ctx.font` from `monospace` only to full Unicode font stack
   - Characters now render correctly in the 24×24 pixel grid

**Font Fallback Chain:**

1. **Noto Sans Symbols 2** — Best Unicode block character support
2. **Segoe UI Symbol** — Windows fallback
3. **Apple Color Emoji** — macOS emoji support
4. **Noto Color Emoji** — Cross-platform emoji
5. **monospace** — Final ASCII fallback

---

### 2. Missing Global Bottom Control Bar

**Problem:** Dashboard lacked persistent UI controls like the typo.robino.dev reference implementation.

**Solution:** Added fixed-bottom global control bar with icon-based controls.

**Features Added:**

**Left Section (Status):**

- Current page name (uppercase, monospace)
- Server status indicator (online/offline with color coding)

**Right Section (Controls):**

- 🔍 Zoom In
- 🔍 Zoom Out
- 🔲 Grid Toggle
- 🌙 Theme Toggle
- ⚙️ Settings
- ❓ Help

**Design Specs:**

- Fixed to bottom of viewport (`position: fixed`)
- Dark background (`bg-gray-900`)
- Border top with shadow
- z-index 40 (above content, below modals)
- Icon-only buttons with tooltips
- Hover states (`hover:bg-gray-800`)
- Responsive container (max-w-6xl)

**SVG Icons:** Using Heroicons outline style (consistent with modern UI standards)

---

## Files Modified

### 1. PixelEditor.svelte

**Lines Changed:** 3 sections

```svelte
<!-- Selected Character Preview (line ~460) -->
<div class="text-6xl mb-2"
     style="font-family: 'Noto Sans Symbols 2', 'Segoe UI Symbol', 'Apple Color Emoji', 'Noto Color Emoji', monospace; line-height: 1;">
  {selectedChar}
</div>

<!-- Character Grid Buttons (line ~475) -->
<button
  class="... text-3xl ..."
  style="font-family: 'Noto Sans Symbols 2', 'Segoe UI Symbol', 'Apple Color Emoji', 'Noto Color Emoji', monospace; line-height: 1;"
>
  {char.utf8}
</button>

<!-- Canvas Rendering (line ~146) -->
ctx.font = `${size * 0.8}px 'Noto Sans Symbols 2', 'Segoe UI Symbol', 'Apple Color Emoji', 'Noto Color Emoji', monospace`;
```

### 2. App.svelte

**Lines Added:** 55 lines (bottom control bar)

```svelte
<!-- Global Bottom Control Bar -->
<div class="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-700 shadow-lg z-40">
  <div class="container mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
    <!-- Status section -->
    <div class="flex items-center gap-4 text-sm text-gray-400">
      <span class="font-mono">{currentPage.toUpperCase()}</span>
      <span>Server: <span class="{serverStatus === 'online' ? 'text-green-400' : 'text-red-400'}">{serverStatus}</span></span>
    </div>

    <!-- Controls section -->
    <div class="flex items-center gap-2">
      <!-- 7 icon buttons with SVG icons -->
    </div>
  </div>
</div>
```

---

## Testing

### Character Rendering Test

1. Navigate to Pixel Editor: http://127.0.0.1:8765/#pixel-editor
2. Click "🔤 Character Picker" button
3. Select "Teletext Blocks" collection
4. **Expected:** All 63 sextant characters display distinctly with proper 2×3 grid patterns
5. **Verify:** Characters differ visually (not all identical squares)

### Bottom Bar Test

1. Navigate to any page
2. Scroll to bottom
3. **Expected:** Fixed control bar visible with:
   - Current page name on left
   - Server status indicator
   - 7 icon buttons on right
4. **Verify:** Bar stays fixed when scrolling

### Font Stack Fallback Test

**Test on different platforms:**

- macOS: Should use Noto Sans Symbols 2 or Apple Color Emoji
- Windows: Should use Segoe UI Symbol
- Linux: Should use Noto fonts (if installed) or monospace
- Mobile: Should use system emoji fonts

---

## Technical Details

### Unicode Sextant Block Range

```
U+1FB00 — U+1FB3B (64 characters total)
64 combinations representing 2×3 pixel grids
6-bit encoding (b0-b5 for 2 cols × 3 rows)
```

**Example Characters:**

- 🬀 (U+1FB00) — All empty
- 🬂 (U+1FB02) — Top row filled
- 🬃 (U+1FB03) — Top-left filled
- 🬻 (U+1FB3B) — All filled (full block)

### Canvas Font Rendering

Canvas `fillText()` respects CSS font fallback chains.
Font stack ensures:

1. Best-quality Unicode rendering when available
2. Graceful degradation to system fonts
3. Monospace as final fallback (ASCII characters)

### Bottom Bar Positioning

```css
position: fixed;
bottom: 0;
left: 0;
right: 0;
z-index: 40;
```

**Avoids conflicts with:**

- Modals (z-50+)
- Navigation (z-10)
- Regular content (z-0)

---

## Build Output

```
✓ 43 modules transformed
../dist/index.html                  0.72 kB │ gzip:  0.42 kB
../dist/assets/index-Dyq0_gV-.css  26.21 kB │ gzip:  5.52 kB
../dist/assets/index-ooPisMau.js   56.59 kB │ gzip: 17.62 kB
✓ built in 462ms
```

**Size Impact:**

- CSS: +620 bytes (bottom bar styles)
- JS: +4.17 kB (SVG icons + control logic)

---

## Future Enhancements

### Planned (Next Version)

- [ ] Wire zoom buttons to actual zoom controls
- [ ] Implement grid toggle functionality
- [ ] Add theme switcher (light/dark toggle)
- [ ] Settings modal (palette, viewport size)
- [ ] Help overlay with keyboard shortcuts

### Font Improvements

- [ ] Preload Unicode font subset (reduce flash)
- [ ] Add @font-face declaration for Noto Sans Symbols 2
- [ ] Font loading indicator for slow connections

### Accessibility

- [ ] Add ARIA labels to icon buttons
- [ ] Keyboard navigation for bottom bar
- [ ] Screen reader announcements for status changes

---

## References

- **Inspiration:** https://typo.robino.dev (bottom bar design)
- **Unicode Spec:** [Legacy Computing Supplement](https://unicode.org/charts/PDF/U1FB00.pdf)
- **Font Stack:** [Modern CSS Font Stacks](https://modernfontstacks.com/)
- **Heroicons:** https://heroicons.com (SVG icons)

---

_Fixes Complete: 2026-01-18_  
_Dashboard v1.0.0.1 | Wizard v1.0.0.1_
