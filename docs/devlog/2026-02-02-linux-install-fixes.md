# Linux/Ubuntu First Install Fixes - 2026-02-02

## Summary

Fixed 6 critical issues preventing successful first-time installation and startup on Linux/Ubuntu systems.

---

## Issues Fixed

### 1. TS Runtime Not Built on Install
**Problem:** Setup command failed with "TS runtime not built" error  
**Root Cause:** TypeScript grid-runtime wasn't being compiled during installation  
**Fix:**
- Added auto-build in `TSRuntimeService._check_runtime_entry(auto_build=True)`
- Added startup health check in `uCODE._check_and_build_ts_runtime()`
- Added build step to `bin/install.sh`
- Added self-healer check `_check_ts_runtime()` and repair `_repair_ts_runtime()`

**Files Changed:**
- `core/services/ts_runtime_service.py`
- `core/tui/ucode.py`
- `bin/install.sh`
- `core/services/self_healer.py`

---

### 2. ES Module Import Errors
**Problem:** `ERR_MODULE_NOT_FOUND: Cannot find module '.../geometry'`  
**Root Cause:** Node.js ES modules require `.js` extensions in import statements  
**Fix:**
- Added `.js` extensions to all relative imports in TypeScript source files
- Updated `tsconfig.json` to use `"moduleResolution": "bundler"`

**Files Changed:**
- `core/grid-runtime/src/*.ts` (all source files)
- `core/grid-runtime/tsconfig.json`

---

### 3. Timezone Detection Error
**Problem:** "Unknown command verb show-timezones" during SETUP  
**Root Cause:** Invalid `timedatectl` command syntax  
**Fix:**
- Changed from `timedatectl show-timezones` to `timedatectl show -p Timezone --value`

**Files Changed:**
- `core/tui/advanced_form_handler.py`

---

### 4. Arrow Key Escape Sequences in Forms
**Problem:** Arrow keys produced `^[[A^[[B` garbage in form inputs  
**Root Cause:** `input()` doesn't filter ANSI escape sequences  
**Fix:**
- Added `_clean_input()` method to filter escape sequences
- Applied to both select fields and text fields

**Files Changed:**
- `core/tui/advanced_form_handler.py`

---

### 5. Wizard Server Startup Failure
**Problem:** "source: not found" when starting Wizard server  
**Root Cause:** `source` is bash-specific, but subprocess used `/bin/sh`  
**Fix:**
- Wrapped venv activation in `bash -c 'source ... && ...'`

**Files Changed:**
- `core/tui/ucode.py`

---

### 6. Dashboard 404 Error
**Problem:** Accessing `/dashboard` returned 404  
**Root Cause:** Dashboard only served at `/`, not `/dashboard`  
**Fix:**
- Added `/dashboard` route as alias to `/`
- Applied to both built and fallback dashboards

**Files Changed:**
- `wizard/server.py`

---

## Installation Flow Improvements

### Before
1. Install dependencies
2. Copy files
3. **Missing:** Build TS runtime
4. Start uCODE
5. **Error:** Runtime not built

### After
1. Install dependencies
2. Copy files
3. **Build TS runtime** (if Node.js available)
4. Start uCODE
5. **Auto-build runtime** on first startup (fallback)
6. **Self-healer** detects and fixes on subsequent runs

---

## Self-Healing Additions

The self-healer now checks and repairs:
- Missing TS runtime (if Node.js available)
- Builds runtime automatically with progress spinner
- Non-blocking warnings if Node.js unavailable

---

## Testing Checklist

- [x] Fresh install on Ubuntu 22.04
- [x] TS runtime builds during install
- [x] TS runtime auto-builds on first startup if missing
- [x] Self-healer detects and repairs missing runtime
- [x] SETUP command works without timezone errors
- [x] Arrow keys don't break form input
- [x] Wizard server starts successfully
- [x] Dashboard accessible at `/` and `/dashboard`

---

## Commits

1. `d7f18a6` - Add automatic TS runtime build on first startup
2. `182935d` - Fix ES module imports in grid-runtime
3. `0e10386` - Fix timezone detection command
4. `7b48724` - Fix arrow key escape sequences in form input
5. `a5f9119` - Fix Wizard server startup on Ubuntu/Linux
6. `f287d25` - Add /dashboard route for compatibility
7. `7bf7566` - Add TS runtime build to install script and self-healer

---

## Documentation Updates Needed

- [ ] Update INSTALLATION.md with Node.js requirement
- [ ] Update QUICKSTART.md with troubleshooting section
- [ ] Add "First Install on Linux" guide

---

_Last Updated: 2026-02-02_
_All fixes tested and pushed to main branch_
