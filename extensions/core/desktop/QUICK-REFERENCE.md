# Desktop Extension - Quick Reference

## New Features (v1.0.24)

### 1. Background Pattern Selector

**How to Access:**
- Double-click the **Patterns** icon (7th icon, Apple logo)
- Select a pattern from the numbered list (1-10)
- Pattern choice is saved automatically

**Available Patterns:**
1. **Checkerboard** - Classic Mac grid (default)
2. **Fine Dots** - Small dot pattern
3. **Grid Small** - 10px grid lines
4. **Grid Medium** - 20px grid lines
5. **Diagonal Lines** - 45° striped pattern
6. **Crosshatch** - Perpendicular line pattern
7. **Dense Dots** - Tight dot spacing
8. **Sparse Dots** - Wide dot spacing
9. **Solid Light** - Light gray (#c0c0c0)
10. **Solid Black** - Black background

### 2. Auto-Fullscreen Windows

**Behavior:**
- All windows now open in **fullscreen mode** automatically
- Desktop is **completely hidden** when a window is open:
  - Menu bar hidden
  - About window hidden
  - Desktop icons hidden
- Click **Close** button to return to desktop

**Affected Windows:**
- Character Editor
- File Picker (Memory Browser)
- Knowledge Library
- System Information
- Command Palette
- Extensions Finder
- Design System Test

**Benefits:**
- Clean, distraction-free workspace
- Maximum screen real estate
- Focused single-task interface
- True Mac System 6 feel

### 3. Local Icon Management

**All Icons Now Local:**
- System UI icons (buttons, scrollbars) → `icons/`
- Application icons (terminal, etc.) → `icons/cil-*.svg`
- No external dependencies

**Desktop Icons:**
1. Terminal → `icons/cil-terminal.svg`
2. Knowledge → `icons/cil-book.svg`
3. Teletext → `icons/cil-tv.svg`
4. Character → `icons/cil-text.svg`
5. Dashboard → `icons/cil-apps.svg`
6. Files → `icons/cil-folder.svg`
7. **Patterns** → `icons/apple.svg` ⬅ NEW!

### 4. Shared Assets Integration

**Pattern Library:**
- Linked: `../../assets/css/classic-patterns.css`
- Provides: 10+ classic Mac patterns
- Variables: `--pattern-1` through `--pattern-4`
- Desktop-specific: `--desktop-pattern-light/medium/dark`

## User Guide

### Changing Background Pattern

1. Double-click **Patterns** icon (bottom left, Apple logo)
2. Dialog shows numbered pattern list with checkmark (✓) on current
3. Enter number (1-10) in prompt
4. Pattern applies immediately
5. Choice saved to browser LocalStorage
6. Persists across sessions

### Working with Fullscreen Windows

**Opening:**
- Double-click any desktop icon
- Window opens fullscreen automatically
- Desktop completely hidden

**Closing:**
- Click **Close** button (⊗) in title bar
- Returns to desktop view
- Icons and menu bar reappear

**No Minimize/Restore:**
- Windows cannot be minimized
- No window management needed
- Clean, simple workflow

### Pattern Persistence

**How It Works:**
```javascript
// Saved automatically when pattern selected
localStorage.setItem('desktop-pattern-index', 0-9);

// Loaded automatically on page load
loadPatternPreference();
```

**Clearing Saved Pattern:**
- Browser DevTools → Application → LocalStorage
- Delete `desktop-pattern-index` key
- Refresh page to reset to default

## Technical Details

### Pattern Application

```javascript
// Pattern structure
const desktopPatterns = [
    {
        name: 'Checkerboard (Default)',
        value: 'linear-gradient(...)',
        size: '22px 22px'
    },
    // ... 9 more patterns
];

// Applied to body element
document.body.style.background = pattern.value;
document.body.style.backgroundSize = pattern.size;
```

### Fullscreen Logic

```javascript
// Auto-fullscreen on window open
function autoFullscreenWindow(win) {
    // Hide desktop elements
    menuBar.style.display = 'none';
    aboutWindow.style.display = 'none';
    desktopIcons.style.display = 'none';

    // Expand window
    win.style.width = '100vw';
    win.style.height = '100vh';
    win.dataset.fullscreened = 'true';
}

// Restore desktop on close
function restoreDesktop() {
    menuBar.style.display = 'flex';
    aboutWindow.style.display = 'block';
    desktopIcons.style.display = 'block';
}
```

## Keyboard Shortcuts

- **Cmd/Ctrl + K** - Open Command Palette (fullscreen)

## Files Modified

- `static/desktop.js` - Added pattern selector + auto-fullscreen
- `desktop.css` - Added fullscreen window styles
- `index.html` - Added classic-patterns.css link
- `icons/` - Added 6 CoreUI application icons
- `STRUCTURE.md` - Updated documentation

## Browser Compatibility

- **Chrome/Edge**: Full support ✓
- **Firefox**: Full support ✓
- **Safari**: Full support ✓
- **LocalStorage**: Required for pattern persistence

## Troubleshooting

**Pattern not saving:**
- Check browser allows LocalStorage
- Verify not in private/incognito mode

**Icons not showing:**
- Check `icons/` directory has all files
- Verify relative paths in `desktop.js`

**Fullscreen not working:**
- Check browser console for errors
- Verify CSS loaded correctly

**Desktop won't restore:**
- Click close button on window
- Refresh page if stuck

---

**Version**: 1.0.24
**Last Updated**: 2025-11-26
**Port**: 8887
