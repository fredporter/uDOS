# Wizard Plugin System — Quick Reference
**For Developers & Users**

---

## Start Wizard Server

```bash
cd ~/uDOS
source .venv/bin/activate
python -m wizard.server
# Access at http://localhost:8765
```

## Access Plugins Page

**Browser:**
```
http://localhost:8765/dashboard
→ Click "🧙 Plugins" in top navigation
```

**Or Direct:**
```
http://localhost:8765/dashboard#/plugins
```

---

## API Quick Commands

### Get All Plugins
```bash
ADMIN_TOKEN="your_token"

curl http://localhost:8765/api/plugins/catalog \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq .
```

### Search Plugins
```bash
curl "http://localhost:8765/api/plugins/search?q=home" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq .plugins
```

### Get Plugin Details
```bash
curl http://localhost:8765/api/plugins/home-assistant \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq .plugin
```

### Install Plugin
```bash
curl -X POST http://localhost:8765/api/plugins/meshcore/install \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq .
```

### Update Plugin
```bash
curl -X POST http://localhost:8765/api/plugins/meshcore/git/pull \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq .
```

---

## Dashboard Features

### Views
- **Grid** — 3-column cards, interactive
- **List** — Compact rows with details
- **Tiers** — Organized by tier (Core → Library → Extension)
- **Categories** — Organized by type

### Actions
- **Install** — Clone or install plugin
- **Update** — Pull latest from git
- **Details** — Full information modal
- **Search** — Real-time full-text search

### Information Shown
- Plugin name, version, description
- Tier & category badges
- Installation status
- Git repository info (URL, branch, commit)
- Dependencies list
- Links to homepage & docs

---

## Plugin Types

| Type | Example | Installation | Location |
|------|---------|--------------|----------|
| **Core** | meshcore | Git clone | distribution/plugins/ |
| **Library** | home-assistant | Container | library/ |
| **Transport** | meshcore-transport | Git (installed) | extensions/transport/ |
| **API** | server-modular | Git (installed) | extensions/api/ |

---

## Configuration

### .env Setup
```dotenv
# Path to uDOS root (for git operations)
UDOS_ROOT="/Users/fredbook/Code/uDOS"

# Wizard admin token (from .env)
WIZARD_ADMIN_TOKEN="your_admin_token_here"
```

### Get Admin Token
```bash
# From .env file
grep WIZARD_ADMIN_TOKEN .env

# Or set new one:
# WIZARD_ADMIN_TOKEN="$(openssl rand -base64 32)"
```

---

## Common Tasks

### Add New Plugin to Discovery

**If it's a git repo:**
1. Create `distribution/plugins/{plugin_id}/manifest.json`
2. Add entry to `distribution/plugins/index.json`
3. Restart Wizard or refresh page

**If it's a container:**
1. Add to `library/{plugin_id}/`
2. Ensure `container.json` exists
3. Refresh page

**If it's an extension:**
1. Add to `extensions/{type}/{plugin_id}/`
2. Create `version.json` (optional)
3. Restart Wizard

### Install a Plugin from UI
1. Open Plugins page
2. Search for plugin
3. Click "Install" button
4. Wait for completion (check console)
5. Plugin now appears as "Installed"

### Update a Plugin
1. Open Plugins page
2. Find installed plugin
3. Click "Update" button
4. Latest changes pulled from git

### Debug Plugin Discovery

```bash
python3 << 'EOF'
from wizard.services.enhanced_plugin_discovery import get_discovery_service
discovery = get_discovery_service()
plugins = discovery.discover_all()

# List all plugins
for plugin_id, plugin in plugins.items():
    print(f"{plugin_id}: {plugin.name} ({plugin.tier})")

# Search
results = discovery.search_plugins("home")
print(f"Found {len(results)} plugins")

# Get git status
plugin = discovery.get_plugin("meshcore")
if plugin.git:
    print(f"Git: {plugin.git.remote_url}")
EOF
```

---

## Troubleshooting

### Plugins Not Appearing
- [ ] Check `.env` UDOS_ROOT is correct
- [ ] Check plugin path exists
- [ ] Check manifest/config files exist
- [ ] Check Wizard logs: `memory/logs/wizard.log`

### Git Operations Failing
- [ ] Verify git is installed: `which git`
- [ ] Check remote is accessible: `git ls-remote <url>`
- [ ] Check permissions: `ls -la plugin_path`

### Installation Not Completing
- [ ] Check Wizard logs for errors
- [ ] Wait longer (large repos take time)
- [ ] Check disk space: `df -h`
- [ ] Try manual: `git clone <url> <path>`

### Plugin Showing as "Modified"
- [ ] Plugin has uncommitted changes
- [ ] Safe to update (git will warn if conflicts)
- [ ] View changes: `git status` in plugin dir

---

## API Reference

### Request Format
```bash
curl -X METHOD \
  http://localhost:8765/api/plugins/... \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"key": "value"}'
```

### Response Format
```json
{
  "success": true,
  "plugin": { ... },
  "message": "Operation completed"
}
```

### Error Handling
```json
{
  "detail": "Plugin not found"
}
// HTTP 404
```

---

## Performance Tips

1. **First load takes time** — Discovery scans filesystem + git repos
2. **Search is local** — Happens in browser, instant
3. **Git operations are async** — Don't block UI
4. **Results cached** — Refresh button manually recaches

---

## Integration Examples

### From uCODE TUI
```ucode
PLUGIN LIST              # Show all plugins
PLUGIN SEARCH home       # Search for plugins
PLUGIN INSTALL meshcore  # Install plugin
PLUGIN UPDATE meshcore   # Update plugin
PLUGIN REMOVE meshcore   # Uninstall plugin
```

### From Scripts
```python
from wizard.services.enhanced_plugin_discovery import get_discovery_service

discovery = get_discovery_service()
discovery.discover_all()

# Install
for plugin in discovery.get_plugins_by_tier("library"):
    print(f"Container: {plugin.name}")
```

### From CLI
```bash
# Get admin token
ADMIN_TOKEN=$(grep WIZARD_ADMIN_TOKEN .env | cut -d= -f2)

# List all
curl http://localhost:8765/api/plugins/catalog \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.plugins | keys'

# Install plugin
curl -X POST http://localhost:8765/api/plugins/meshcore/install \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `wizard/services/enhanced_plugin_discovery.py` | Discovery engine |
| `wizard/routes/enhanced_plugin_routes.py` | API endpoints |
| `wizard/dashboard/src/routes/Plugins.svelte` | Dashboard UI |
| `distribution/plugins/index.json` | Plugin index |
| `library/*/container.json` | Container metadata |
| `.env` | Configuration (UDOS_ROOT) |
| `docs/WIZARD-PLUGIN-SYSTEM.md` | Full documentation |

---

## Getting Help

1. **Check logs:** `tail -f memory/logs/wizard.log`
2. **Test API:** `curl http://localhost:8765/api/plugins/catalog`
3. **Debug discovery:** Run Python script above
4. **Read docs:** [WIZARD-PLUGIN-SYSTEM.md](../WIZARD-PLUGIN-SYSTEM.md)

---

**Last Updated:** 2026-02-01  
**Version:** 1.0.0  
**Status:** ✅ Ready
