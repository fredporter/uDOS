# Terminal Font Fix & PETSCII Character Map

**Date**: 26 November 2025
**Issue**: PetMe64 font not loading in terminal
**Solution**: Local font copy + cache busting + PETSCII char map

## Changes Made

### 1. Font Path Fix
**Problem**: Font path `../../../assets/fonts/PetMe64.ttf` broken due to server routing

**Solution**:
- Created `/extensions/core/terminal/fonts/` directory
- Copied `PetMe64.ttf` locally
- Updated CSS path to `fonts/PetMe64.ttf?v=2`
- Added `font-display: block` for immediate rendering

**Files Modified**:
- `terminal.css` - Updated `@font-face` src path
- `index.html` - Added `?v=2` cache buster to CSS link

### 2. PETSCII Character Map (F8)
**Feature**: Functional character reference display

**Implementation**:
```javascript
function showCharacterMap() {
    // Standard ASCII (32-126)
    // Block graphics: ▀▄█▌▐░▒▓■□▪▫
    // Box drawing: ─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬
    // PETSCII symbols: ♠♥♦♣●○◆◇★☆▲▼◄►
}
```

**Character Sets Included**:
1. **Standard Characters** (32-126): All printable ASCII
2. **Block Graphics**: Unicode block drawing approximations
3. **Box Drawing**: Single/double line boxes
4. **PETSCII Symbols**: Card suits, circles, arrows, stars

### 3. Cache Busting
- CSS: `terminal.css?v=2`
- Font: `fonts/PetMe64.ttf?v=2`

## Testing

### Verify Font Loading
```bash
# Check font file accessibility
curl -I http://localhost:8889/fonts/PetMe64.ttf

# Should return: HTTP/1.0 200 OK, Content-type: font/ttf
```

### Test Character Map
1. Open terminal: `http://localhost:8889`
2. Press `F8` or click F8 button
3. Should display full PETSCII character map

## Font Details

**Font**: PetMe64.ttf
**Size**: 389,392 bytes
**Type**: TrueType
**Source**: `/extensions/assets/fonts/petme/PetMe64.ttf`
**Purpose**: C64/PETSCII character rendering

## Next Steps

Potential enhancements:
1. **Interactive Character Picker**: Click to copy characters
2. **Character Code Display**: Show hex/dec values
3. **Extended PETSCII**: Add high-bit characters (128-255)
4. **Search/Filter**: Find characters by name/category
5. **Copy to Clipboard**: One-click character copy

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Requires: Unicode character support, @font-face

## Troubleshooting

**Font not showing?**
1. Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)
2. Clear browser cache
3. Check console for 404 errors
4. Verify font file exists: `ls extensions/core/terminal/fonts/`

**Characters not displaying?**
- Some Unicode characters require font support
- Fallback to system font if glyph missing
- PetMe64 has full PETSCII coverage

## Related Files

- `extensions/core/terminal/terminal.css` - Font declaration
- `extensions/core/terminal/index.html` - CSS link
- `extensions/core/terminal/static/terminal.js` - Character map function
- `extensions/core/terminal/fonts/PetMe64.ttf` - Font file (local copy)
- `extensions/assets/fonts/petme/PetMe64.ttf` - Original font source
