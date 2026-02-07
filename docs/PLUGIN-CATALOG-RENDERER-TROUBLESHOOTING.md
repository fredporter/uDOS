# Plugin Catalog & Renderer Control Plane Troubleshooting Guide

**Status:** Common v1.3 issues documented  
**Date:** 2026-02-05

---

## Overview

When Wizard server starts, two subsystems load:

1. **Plugin Catalog** (`/api/plugins/catalog`) - Scans library for available plugins
2. **Renderer Control Plane** (`/api/render/...`) - Manages theme exports and missions

Both can fail silently if:
- Required directories don't exist
- File permissions are wrong
- Dependencies are missing
- Configuration paths are incorrect

---

## Diagnosing the Issue

### Step 1: Check Wizard Logs

```bash
# Follow real-time Wizard logs
tail -f memory/logs/unified-wizard-*.log | grep -i "plugin\|catalog\|renderer"

# Or check for recent errors
grep -i "error\|exception" memory/logs/unified-wizard-2026-02-05.log | head -20
```

### Step 2: Test Endpoints Directly

```bash
# Plugin Catalog
curl -v http://localhost:8765/api/plugins/catalog

# Renderer Status
curl -v http://localhost:8765/api/render/status

# Should return 200 with JSON. If 500, the error message shows the problem.
```

### Step 3: Check Required Directories

```bash
# Ensure all required paths exist
ls -la library/            # Plugin definitions
ls -la vault-md/bank/      # Vault bank
ls -la wizard/config/      # Configuration
ls -la themes/             # Theme definitions (if rendering enabled)
ls -la vault/              # Content vault (if missions enabled)
```

---

## Common Issues & Solutions

### Issue 1: Plugin Catalog Error 500

**Symptom:** `GET /api/plugins/catalog` returns 500

**Root cause:** Discovery service can't scan library directory

**Solution:**

```bash
# Check if library directory exists
test -d library && echo "✓ Exists" || echo "✗ Missing"

# Check permissions
ls -ld library/
# Should be: drwxr-xr-x

# Fix permissions if needed
chmod 755 library/
```

---

### Issue 2: "Theme Site Not Found"

**Symptom:** Renderer returns 404 for theme operations

**Root cause:** `themes/` directory missing or wrong path

**Solution:**

```bash
# Create themes directory if missing
mkdir -p themes

# Verify path is correct
ls -la themes/
# Should contain: manifest.json, theme-packs/

# Set environment variable (if custom location)
export THEMES_ROOT="/path/to/themes"
```

---

### Issue 3: "Spatial Database Not Found"

**Symptom:** Mission/mission operations fail

**Root cause:** Vault spatial store not initialized

**Solution:**

```bash
# Initialize spatial database
python -m core.commands.file_handler --init-spatial

# Or via Wizard API
curl -X POST http://localhost:8765/api/render/spatial/init

# Verify it exists
ls -la vault/spatial_database.db
```

---

### Issue 4: Plugin Discovery Hangs or Times Out

**Symptom:** Catalog endpoint takes 30+ seconds or times out

**Root cause:** Large library or slow disk I/O

**Solution:**

```bash
# Check library size
du -sh library/

# If > 500MB, optimize:
# 1. Move unused plugins to archive
mkdir -p .archive/plugins
mv library/unused-plugin .archive/plugins/

# 2. Disable auto-discovery for large trees
export PLUGIN_DISCOVERY_RECURSIVE_LIMIT=2

# 3. Restart Wizard
./bin/Launch-uCODE.command wizard
```

---

### Issue 5: Renderer Subprocess Failed

**Symptom:** `POST /api/render/render` returns 500 with "Renderer failed"

**Root cause:** Renderer command (usually TS runtime or markdown parser) crashed

**Solution:**

```bash
# Check if renderer executable exists
which pandoc || echo "pandoc not installed"

# Or if using custom renderer
ls -la wizard/renderers/

# Install missing dependency
npm install -g pandoc  # or pip install pandoc

# Verify renderer works standalone
echo "# Test" | pandoc -f markdown -t html

# Then restart Wizard
./bin/Launch-uCODE.command wizard
```

---

## Prevention Checklist

Before starting Wizard, ensure:

```bash
# ✅ Required directories exist
mkdir -p library wizard/config themes vault-md vault-md/bank memory/system

# ✅ File permissions are correct (rwxr-xr-x)
chmod 755 library wizard themes vault

# ✅ No stale lock files
rm -f wizard/.lock wizard/discovery.lock

# ✅ Python dependencies installed
pip install -r requirements.txt

# ✅ Node dependencies installed (if using TS renderer)
cd wizard/dashboard && npm install

# ✅ Environment variables set (optional)
export UDOS_ENV=production
export UDOS_LOG_LEVEL=INFO

# ✅ Then start Wizard
./bin/Launch-uCODE.command wizard
```

---

## Debugging with Verbose Logging

### Enable Debug Mode

```bash
# Set in environment
export UDOS_LOG_LEVEL=DEBUG
export PLUGIN_DEBUG=1
export RENDERER_DEBUG=1

# Restart Wizard
./bin/Launch-uCODE.command wizard

# Now check logs with more detail
tail -f memory/logs/unified-wizard-*.log
```

### Check Individual Service Logs

```bash
# Plugin discovery logs
grep "plugin-discovery\|discovery" memory/logs/unified-wizard-*.log | tail -50

# Renderer logs
grep "renderer\|render" memory/logs/unified-wizard-*.log | tail -50

# Full stack traces
grep -A5 "Traceback" memory/logs/unified-wizard-*.log
```

---

## Recovery Steps

If both systems are broken:

### 1. Soft Reset (keeps data)

```bash
# Stop Wizard
killall python

# Clear caches but keep data
rm -f wizard/.cache wizard/discovery.lock
rm -rf wizard/__pycache__ .pytest_cache

# Restart
./bin/Launch-uCODE.command wizard

# Check status
curl http://localhost:8765/api/system/health
```

### 2. Hard Reset (clear temporary files)

```bash
# Stop Wizard
killall python

# Clear all temporary data
rm -rf wizard/.cache wizard/__pycache__ .pytest_cache
rm -f memory/logs/wizard-* memory/logs/unified-*

# Recreate directories
mkdir -p library wizard/config themes vault-md vault-md/bank memory/system
chmod 755 library wizard themes vault

# Reinstall dependencies
pip install -r requirements.txt

# Restart
./bin/Launch-uCODE.command wizard
```

### 3. Full Rebuild (if still broken)

```bash
# Stop all services
pkill -f "python.*wizard"

# Clean build artifacts
rm -rf build dist *.egg-info
rm -rf wizard/dist wizard/build

# Reinstall from scratch
pip install --force-reinstall -r requirements.txt

# Initialize fresh
python -m wizard.server --init

# Restart
./bin/Launch-uCODE.command wizard
```

---

## Testing Checklist

After fixing, verify both systems work:

```bash
# 1. Plugin Catalog
curl -s http://localhost:8765/api/plugins/catalog | jq '.total'
# Should print: number > 0

# 2. Renderer Status
curl -s http://localhost:8765/api/render/status | jq '.healthy'
# Should print: true

# 3. Dashboard loads
open http://localhost:8765/#plugins
# Should show plugin grid

# 4. Config visible
open http://localhost:8765/#config
# Should show configuration page

# 5. Webhooks registered
curl -s http://localhost:8765/api/webhooks/status | jq '.webhooks'
# Should show github
```

---

## Known Limitations (v1.3)

| Feature | Status | Workaround |
|---------|--------|-----------|
| Plugin auto-reload | ⚠️ Experimental | Restart Wizard after changes |
| Theme hot-swap | ⚠️ Slow for 100+ themes | Use `THEMES_RECURSIVE_LIMIT=2` |
| Large vault rendering | ⚠️ >1GB missions timeout | Split into smaller missions |
| Spatial indexing | ✅ Stable | None needed |
| Nested plugin discovery | ⚠️ 4-level max | Flatten directory structure |

---

## Reference

- **Plugin Routes:** `wizard/routes/enhanced_plugin_routes.py`
- **Renderer Routes:** `wizard/routes/renderer_routes.py`
- **Discovery Service:** `wizard/services/plugin_discovery.py`
- **Contribution Service:** `wizard/services/contribution_service.py`

---

## Getting Help

If issues persist:

1. Check the main [GITHUB-WEBHOOKS-HUBSPOT-SETUP.md](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md) for related configs
2. Review [AGENTS.md](AGENTS.md) for architecture overview
3. Check `memory/logs/` for the specific error stack trace
4. Search `wizard/routes/` for the failing endpoint

---

**Last Updated:** 2026-02-05  
**Maintainer:** uDOS Team
