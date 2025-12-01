# POKE & Dashboard Restructure - December 1, 2025

## Current State

### Commands
- **DASH** - Shows TUI text dashboard (should be deprecated)
- **DASH WEB** - Launches web dashboard on port 5555
- **STATUS** - Shows system status (should absorb DASH functionality)
- **POKE TUNNEL** - Tunnel management via poke_online extension

### File Structure
- `extensions/web/` - Empty directory (to be removed)
- `extensions/cloud/poke_online/` - POKE extension
- `extensions/core/dashboard/` - NES-themed web dashboard (port 5555)

## Proposed Changes

### 1. Command Consolidation

**DEPRECATE:**
- `DASH` (text mode) → Merge into `STATUS`

**KEEP:**
- `STATUS` - Enhanced text dashboard (absorbs DASH functionality)

**NEW POKE SHORTCUTS:**
- `POKE START <service>` - Start web service
- `POKE STOP <service>` - Stop web service
- `POKE DASHBOARD` - Shortcut for `POKE START dashboard`
- `POKE DESKTOP` - Shortcut for `POKE START desktop`
- `POKE TERMINAL` - Shortcut for `POKE START terminal`
- `POKE TELETEXT` - Shortcut for `POKE START teletext`
- `POKE WEB` - Shortcut for `POKE START web` (new web publishing tools)

**SERVICE COMMANDS:**
```bash
# Shortcuts (default action: start)
POKE DASHBOARD          # Start dashboard
POKE DASHBOARD --stop   # Stop dashboard

# Explicit
POKE START dashboard
POKE STOP dashboard

# List all services
POKE LIST
POKE STATUS
```

### 2. File Structure Changes

**BEFORE:**
```
extensions/
├── web/ (empty - DELETE)
├── cloud/
│   └── poke_online/
│       ├── server.py
│       ├── tunnel_manager.py
│       └── poke_commands.py
└── core/
    └── dashboard/
        ├── app.py
        ├── index.html
        └── start.sh
```

**AFTER:**
```
extensions/
├── cloud/
│   ├── poke_online/
│   │   ├── server.py
│   │   ├── tunnel_manager.py
│   │   ├── poke_commands.py (enhanced)
│   │   └── services/
│   │       ├── dashboard/ (moved from core/)
│   │       ├── desktop/
│   │       ├── terminal/
│   │       ├── teletext/
│   │       └── web/ (new - web publishing)
│   └── README.md (POKE cloud services doc)
└── core/
    └── (dashboard moved to cloud/poke_online/services/)
```

### 3. Implementation Steps

1. **Update STATUS command** (core/commands/dashboard_handler.py)
   - Absorb DASH text functionality
   - Remove DASH command handler
   - STATUS becomes the comprehensive TUI dashboard

2. **Enhance POKE commands** (extensions/cloud/poke_online/poke_commands.py)
   - Add START/STOP service management
   - Add service shortcuts (DASHBOARD, DESKTOP, etc.)
   - Add WEB publishing service
   - Update command routing

3. **Move dashboard to POKE services**
   ```bash
   mv extensions/core/dashboard extensions/cloud/poke_online/services/dashboard
   ```

4. **Create web publishing service**
   - New service in extensions/cloud/poke_online/services/web/
   - Web publishing tools (markdown, static sites, etc.)

5. **Update extension.json**
   - Update POKE extension manifest
   - Add new service definitions
   - Update command references

6. **Clean up**
   - Remove extensions/web/ directory
   - Update wiki documentation
   - Update copilot instructions

### 4. Service Registry

**POKE Services** (managed by poke_online extension):
```json
{
  "dashboard": {
    "port": 5555,
    "path": "services/dashboard",
    "description": "NES-themed system dashboard",
    "shortcuts": ["POKE DASHBOARD", "POKE START dashboard"]
  },
  "desktop": {
    "port": 8892,
    "path": "services/desktop",
    "description": "System desktop interface",
    "shortcuts": ["POKE DESKTOP", "POKE START desktop"]
  },
  "terminal": {
    "port": 8889,
    "path": "services/terminal",
    "description": "Web-based terminal",
    "shortcuts": ["POKE TERMINAL", "POKE START terminal"]
  },
  "teletext": {
    "port": 9002,
    "path": "services/teletext",
    "description": "Teletext interface",
    "shortcuts": ["POKE TELETEXT", "POKE START teletext"]
  },
  "web": {
    "port": 8080,
    "path": "services/web",
    "description": "Web publishing tools",
    "shortcuts": ["POKE WEB", "POKE START web"]
  }
}
```

### 5. Command Examples

**After Implementation:**
```bash
# Text dashboard (TUI)
STATUS

# Web services
POKE DASHBOARD              # Start dashboard at localhost:5555
POKE DASHBOARD --stop       # Stop dashboard
POKE START dashboard        # Explicit start

# Multiple services
POKE DESKTOP
POKE TERMINAL
POKE TELETEXT
POKE WEB

# Service management
POKE LIST                   # List all services and status
POKE STOP teletext         # Stop specific service
POKE RESTART dashboard     # Restart service

# Tunneling (existing)
POKE TUNNEL OPEN 5555      # Expose dashboard publicly
```

### 6. Benefits

✅ **Simpler Structure:**
- All web services in one place (cloud/poke_online)
- POKE becomes the unified web service manager
- STATUS is the unified TUI dashboard

✅ **Clearer Commands:**
- `STATUS` for text dashboard
- `POKE <SERVICE>` for web services
- Consistent start/stop pattern

✅ **Flatter Files:**
- Remove empty extensions/web/
- Consolidate dashboard under POKE
- All cloud services together

✅ **Better UX:**
- Shortcuts reduce typing (POKE DASHBOARD vs DASH WEB)
- Consistent service management
- Easy service discovery (POKE LIST)

## Migration Checklist

- [ ] Update STATUS command (absorb DASH text functionality)
- [ ] Remove DASH command handler
- [ ] Enhance POKE commands (START/STOP/shortcuts)
- [ ] Move dashboard: core → cloud/poke_online/services/
- [ ] Create web publishing service
- [ ] Update extension.json for POKE
- [ ] Remove extensions/web/ directory
- [ ] Update system_handler.py command routing
- [ ] Update wiki documentation
- [ ] Update copilot instructions
- [ ] Test all commands
- [ ] Commit and push changes
