# Teletext Extension - Asset Organization Analysis
**Version:** 1.0.24
**Date:** 18 November 2025

## Current Status

### ✅ Already Using Shared Assets
- **Fonts:** `/extensions/assets/fonts/mallard/` (via symlink `assets`)
- **Colors:** `/extensions/assets/css/synthwave-dos-colors.css` (loaded in HTML)

### 📦 Files That SHOULD Stay Local
These files are teletext-specific and should remain in `/extensions/core/teletext/`:

#### **HTML Files**
- `index.html` - Main teletext interface (specific to this extension)

#### **CSS Files**
- `teletext-synthwave.css` - Teletext-specific Synthwave styling (uses shared color vars)
- `teletext-udos.css` - Teletext uDOS integration styles
- `teletext-web.css` - Teletext web-specific styles

#### **JavaScript Files** (in `static/`)
- `teletext-core.js` - Core teletext terminal logic with uDOS integration ✅
- `teletext-terminal.js` - Legacy terminal logic (can be removed?)
- `teletext-commands.js` - Teletext-specific command handlers (can be removed?)
- `block-graphics.js` - Block graphics support (teletext-specific)

#### **Data Files**
- `mosaic_codepoints_E200-E3FF.csv` - Teletext mosaic character mappings

#### **Python Files**
- `api_server.py` - Teletext API server (should stay, it's teletext-specific Flask app)
- `requirements.txt` - Python dependencies for api_server.py

#### **Shell Scripts**
- `start.sh` - Teletext server startup script
- `start_api.sh` - API server startup script

#### **Documentation**
- `README.md` - Teletext extension documentation
- `README-SYNTHWAVE.md` - Synthwave palette documentation
- `CREDITS.md` - Credits
- `API.md` - API documentation

### 🔧 Files That COULD Be Moved to Shared Assets

#### **Generic JavaScript** (if used by multiple extensions)
None currently - all JS is teletext-specific

#### **Generic CSS** (if used by multiple extensions)
- `teletext-enhanced.css` - **OBSOLETE** (replaced by teletext-synthwave.css, can be deleted)
- `teletext-api.js` - **CHECK IF USED** (might be generic API client)
- `teletext-shell.js` - **CHECK IF USED** (might be generic shell)

### 🗑️ Files That Can Be REMOVED
- `teletext-enhanced.css` - Replaced by `teletext-synthwave.css`
- `teletext-enhanced.js` - Not referenced in current `index.html`
- Possibly `teletext-terminal.js` and `teletext-commands.js` if superseded by `teletext-core.js`

## Python API Server Analysis

### Should `api_server.py` be moved?
**NO** - It should stay in `/extensions/core/teletext/` because:

1. **Teletext-Specific:** It's a Flask server specifically for the teletext web interface
2. **Local Dependencies:** Imports from relative paths to teletext static files
3. **Extension Isolation:** Each extension should manage its own backend services
4. **Different from uDOS Core:** This is NOT the main uDOS core API (which is at `localhost:8890`)

### Shared vs Extension APIs
```
localhost:8890  → uDOS Core API (in /core/)
localhost:9002  → Teletext HTTP Server (serves static files)
localhost:5001  → Teletext API Server (api_server.py) - optional enhanced features
```

## Recommendations

### Immediate Actions
1. ✅ **Keep using shared Synthwave colors** - Already implemented
2. ✅ **Keep using shared fonts via symlink** - Already implemented
3. 🔄 **Remove obsolete files:**
   ```bash
   cd /Users/fredbook/Code/uDOS/extensions/core/teletext
   rm teletext-enhanced.css teletext-enhanced.js
   ```

### Future Considerations
1. **If Terminal and Teletext share command logic:** Extract to `/extensions/assets/js/udos-terminal-commands.js`
2. **If block graphics used elsewhere:** Extract to `/extensions/assets/js/udos-block-graphics.js`
3. **For common API client code:** Create `/extensions/assets/js/udos-api-client.js`

## Current File Structure ✅

```
/extensions/core/teletext/
├── index.html              # Main interface
├── teletext-synthwave.css  # Synthwave styling ✅
├── teletext-udos.css       # uDOS integration
├── teletext-web.css        # Web-specific
├── api_server.py           # Flask API (stays here)
├── requirements.txt        # Python deps
├── start.sh                # Server startup
├── start_api.sh            # API startup
├── mosaic_codepoints_E200-E3FF.csv
├── static/
│   ├── teletext-core.js    # Main terminal logic ✅
│   ├── block-graphics.js   # Block graphics
│   ├── teletext-terminal.js  # (check if needed)
│   └── teletext-commands.js  # (check if needed)
└── assets → ../../assets   # Symlink to shared ✅
```

## Shared Assets Being Used ✅

```
/extensions/assets/
├── css/
│   └── synthwave-dos-colors.css  # Used by teletext ✅
└── fonts/
    └── mallard/
        └── mallard-blockier.otf   # Used by teletext ✅
```

## Conclusion

**Current setup is GOOD:**
- ✅ Using shared Synthwave DOS color palette
- ✅ Using shared Mallard font via symlink
- ✅ Teletext-specific files properly isolated
- ✅ Python API server correctly located in extension folder
- ✅ Clean separation of concerns

**Minor cleanup needed:**
- Remove obsolete `teletext-enhanced.css` and `teletext-enhanced.js`
- Verify if `teletext-terminal.js` and `teletext-commands.js` are still used (likely superseded by `teletext-core.js`)
